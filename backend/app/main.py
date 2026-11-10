"""
EcoPulse - Backend API (FastAPI + SQLAlchemy)
Projeto Integrado Multidisciplinar II (PIM II - UNIP)
Arquitetura Dual-Pipeline:
  - Hot Path: Estado em Memória RAM + Streaming SSE (< 15ms, Zero Disk I/O)
  - Cold Path: Agregação Temporal (5 min, WMO-No. 8 / INMET) + Deadband de Eventos no PostgreSQL
"""
import os
import re
import time
import json
import signal
import asyncio
import urllib.request
from collections import deque
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any, Set

from pathlib import Path
from fastapi import FastAPI, Header, HTTPException, Depends, Query, Request, status
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from dotenv import load_dotenv

from app.database import engine, Base, get_db, SessionLocal
from app.models import TelemetryAggregated5m, TelemetryEvent
from app.schemas import TelemetryPayload, TelemetryResponse, SensorDataSchema, DiagnosticsSchema

load_dotenv()

API_SECRET_KEY = os.getenv("API_SECRET_KEY", "chave-secreta-estacao-unip-2026")
COLD_PATH_WINDOW_SECONDS = int(os.getenv("COLD_PATH_WINDOW_SECONDS", "300"))  # 5 minutos (padrão WMO/Davis)
ESP32_MDNS_RAW_URL = os.getenv("ESP32_MDNS_RAW_URL", "http://esp32.local/raw")

# Cooldown de eventos de variação contínua (evita rajadas de gravação quando o sensor oscila no limiar)
EVENT_COOLDOWN_SECONDS = int(os.getenv("EVENT_COOLDOWN_SECONDS", "30"))
COOLDOWN_EVENT_TYPES = {"LUMINOSITY_SHIFT", "HUMIDITY_SHIFT", "THERMAL_SURGE"}


# =========================================================================
# 1. Barramento Pub/Sub em Memória para Streaming SSE (Hot Path)
# =========================================================================
class TelemetryBroadcaster:
    """Distribuidor assíncrono de leituras em tempo real para múltiplos clientes SSE."""
    def __init__(self):
        self._subscribers: Set[asyncio.Queue] = set()

    async def subscribe(self) -> asyncio.Queue:
        q = asyncio.Queue(maxsize=30)
        self._subscribers.add(q)
        return q

    def unsubscribe(self, q: asyncio.Queue):
        self._subscribers.discard(q)

    async def broadcast(self, data: dict):
        if not self._subscribers:
            return
        dead = []
        for q in list(self._subscribers):
            try:
                q.put_nowait(data)
            except asyncio.QueueFull:
                dead.append(q)
        for q in dead:
            self._subscribers.discard(q)


broadcaster = TelemetryBroadcaster()
shutdown_event = asyncio.Event()


# =========================================================================
# 2. Motor Dual-Pipeline: Hot Path (RAM) & Cold Path (Agregador + Deadband)
# =========================================================================
class HotColdTelemetryEngine:
    """
    Gerencia o estado volátil de baixa latência (Hot Path) e decide quando
    consolidar e persistir no banco relacional (Cold Path).
    """
    def __init__(self):
        self.latest_by_device: Dict[str, dict] = {}
        self.live_ring_by_device: Dict[str, deque] = {}
        self.window_samples: Dict[str, List[dict]] = {}
        self.window_start_by_device: Dict[str, datetime] = {}
        self.daily_extremes: Dict[str, dict] = {}
        self.persisted_once_devices: Set[str] = set()
        self.total_hot_ticks: int = 0
        self.total_cold_writes: int = 0
        self.last_direct_push_ts: float = 0.0
        self.last_event_ts: Dict[tuple, float] = {}

    def reset_state(self):
        """Reinicia o estado em memória (útil para suíte de testes automatizados)."""
        self.latest_by_device.clear()
        self.live_ring_by_device.clear()
        self.window_samples.clear()
        self.window_start_by_device.clear()
        self.daily_extremes.clear()
        self.persisted_once_devices.clear()
        self.total_hot_ticks = 0
        self.total_cold_writes = 0
        self.last_direct_push_ts = 0.0
        self.last_event_ts.clear()

    def _update_extremes(self, device_id: str, s: dict):
        ext = self.daily_extremes.get(device_id)
        temp = s.get("temperature_c")
        hum = s.get("humidity_pct")
        press = s.get("pressure_hpa")
        aqi = s.get("air_quality_ppm")

        if not ext:
            self.daily_extremes[device_id] = {
                "temp_min": temp,
                "temp_max": temp,
                "humidity_min": hum,
                "humidity_max": hum,
                "pressure_min": press,
                "pressure_max": press,
                "air_quality_max": aqi,
            }
            return

        if temp is not None:
            ext["temp_min"] = min(ext["temp_min"], temp) if ext["temp_min"] is not None else temp
            ext["temp_max"] = max(ext["temp_max"], temp) if ext["temp_max"] is not None else temp
        if hum is not None:
            ext["humidity_min"] = min(ext["humidity_min"], hum) if ext["humidity_min"] is not None else hum
            ext["humidity_max"] = max(ext["humidity_max"], hum) if ext["humidity_max"] is not None else hum
        if press is not None:
            ext["pressure_min"] = min(ext["pressure_min"], press) if ext["pressure_min"] is not None else press
            ext["pressure_max"] = max(ext["pressure_max"], press) if ext["pressure_max"] is not None else press
        if aqi is not None:
            ext["air_quality_max"] = max(ext["air_quality_max"], aqi) if ext["air_quality_max"] is not None else aqi

    def detect_deadband_anomaly(self, prev: Optional[dict], curr_sensors: dict) -> Optional[dict]:
        """
        Avalia se ocorreu mudança abrupta nos sensores que justifique
        quebra imediata de janela e registro de alerta no Cold Path.
        """
        if not prev:
            if curr_sensors.get("is_raining"):
                return {
                    "event_type": "RAIN_STARTED",
                    "severity": "WARNING",
                    "title": "Precipitação em Andamento",
                    "description": (
                        f"Sensor pluviométrico detectou lâmina d'água ativa "
                        f"({curr_sensors.get('rain_intensity_pct', 0):.0f}% de intensidade)."
                    ),
                }
            return None

        prev_s = prev.get("sensors", {})

        # 1. Transição de Chuva (Início ou Fim)
        prev_rain = bool(prev_s.get("is_raining", False))
        curr_rain = bool(curr_sensors.get("is_raining", False))
        if curr_rain != prev_rain:
            if curr_rain:
                return {
                    "event_type": "RAIN_STARTED",
                    "severity": "WARNING",
                    "title": "Início de Chuva Detectado",
                    "description": (
                        f"Precipitação iniciada na estação com intensidade de "
                        f"{curr_sensors.get('rain_intensity_pct', 0):.0f}%."
                    ),
                }
            else:
                return {
                    "event_type": "RAIN_STOPPED",
                    "severity": "INFO",
                    "title": "Estiagem / Fim de Precipitação",
                    "description": "Superfície do sensor MH-RD retornou ao estado seco.",
                }

        # 2. Queda ou Variação Barométrica Brusca (>= 2.0 hPa)
        p_prev = prev_s.get("pressure_hpa")
        p_curr = curr_sensors.get("pressure_hpa")
        if p_prev is not None and p_curr is not None and abs(p_curr - p_prev) >= 2.0:
            direcao = "Queda" if p_curr < p_prev else "Elevação"
            return {
                "event_type": "PRESSURE_DROP_ALERT",
                "severity": "WARNING" if p_curr < p_prev else "INFO",
                "title": f"{direcao} Barométrica Acentuada",
                "description": (
                    f"Pressão atmosférica variou de {p_prev:.1f} hPa para {p_curr:.1f} hPa "
                    f"(Δ = {p_curr - p_prev:+.1f} hPa). Indicativo de instabilidade."
                ),
            }

        # 3. Salto de Poluentes / Gases no MQ-135 (Δ >= 50 PPM)
        aqi_prev = prev_s.get("air_quality_ppm")
        aqi_curr = curr_sensors.get("air_quality_ppm")
        if aqi_prev is not None and aqi_curr is not None and (aqi_curr - aqi_prev) >= 50.0:
            return {
                "event_type": "GAS_SPIKE_ALERT",
                "severity": "CRITICAL" if aqi_curr >= 600 else "WARNING",
                "title": "Pico de Gases / Fumaça Detectado",
                "description": (
                    f"Sensor MQ-135 registrou elevação abrupta de {aqi_prev:.0f} PPM "
                    f"para {aqi_curr:.0f} PPM."
                ),
            }

        # 4. Variação Térmica Abrupta (Δ >= 1.5 °C)
        t_prev = prev_s.get("temperature_c")
        t_curr = curr_sensors.get("temperature_c")
        if t_prev is not None and t_curr is not None and abs(t_curr - t_prev) >= 1.5:
            return {
                "event_type": "THERMAL_SURGE",
                "severity": "INFO",
                "title": "Oscilação Térmica Rápida",
                "description": f"Temperatura variou rapidamente de {t_prev:.1f}°C para {t_curr:.1f}°C.",
            }

        # 5. Variação Brusca de Luminosidade no LDR (Δ >= 15 %)
        # Mesmo limiar usado pelo firmware para disparo imediato (mudancaLuz em main.cpp)
        l_prev = prev_s.get("luminosity_pct")
        l_curr = curr_sensors.get("luminosity_pct")
        if l_prev is not None and l_curr is not None and abs(l_curr - l_prev) >= 15.0:
            direcao_luz = "Aumento" if l_curr > l_prev else "Queda"
            return {
                "event_type": "LUMINOSITY_SHIFT",
                "severity": "INFO",
                "title": f"{direcao_luz} Brusca de Luminosidade",
                "description": (
                    f"Sensor LDR variou de {l_prev:.0f}% para {l_curr:.0f}% "
                    f"(Δ = {l_curr - l_prev:+.0f}%)."
                ),
            }

        # 6. Variação Abrupta de Umidade Relativa (Δ >= 8 %)
        h_prev = prev_s.get("humidity_pct")
        h_curr = curr_sensors.get("humidity_pct")
        if h_prev is not None and h_curr is not None and abs(h_curr - h_prev) >= 8.0:
            return {
                "event_type": "HUMIDITY_SHIFT",
                "severity": "INFO",
                "title": "Oscilação Rápida de Umidade",
                "description": f"Umidade relativa variou de {h_prev:.0f}% para {h_curr:.0f}%.",
            }

        return None

    def flush_window_to_db(self, db: Session, device_id: str, now: datetime) -> TelemetryAggregated5m:
        """Calcula médias, mínimas e máximas do buffer e grava 1 linha consolidada no PostgreSQL."""
        samples = self.window_samples.get(device_id, [])
        w_start = self.window_start_by_device.get(device_id, now)

        def valid_vals(key: str) -> List[float]:
            return [
                float(x["sensors"][key])
                for x in samples
                if x["sensors"].get(key) is not None
            ]

        temps = valid_vals("temperature_c")
        hums = valid_vals("humidity_pct")
        press = valid_vals("pressure_hpa")
        alts = valid_vals("altitude_m")
        aqis = valid_vals("air_quality_ppm")
        lights = valid_vals("luminosity_pct")
        rains = valid_vals("rain_intensity_pct")
        any_rain = any(bool(x["sensors"].get("is_raining")) for x in samples)

        last_diag = samples[-1].get("diagnostics", {}) if samples else {}

        avg = lambda lst: round(sum(lst) / len(lst), 2) if lst else None

        registro = TelemetryAggregated5m(
            device_id=device_id,
            window_start=w_start,
            window_end=now,
            samples_count=len(samples) if samples else 1,
            temp_avg=avg(temps),
            temp_min=round(min(temps), 2) if temps else None,
            temp_max=round(max(temps), 2) if temps else None,
            humidity_avg=avg(hums),
            humidity_min=round(min(hums), 2) if hums else None,
            humidity_max=round(max(hums), 2) if hums else None,
            pressure_avg=avg(press),
            pressure_min=round(min(press), 2) if press else None,
            pressure_max=round(max(press), 2) if press else None,
            altitude_avg=avg(alts),
            air_quality_avg=avg(aqis),
            air_quality_max=round(max(aqis), 2) if aqis else None,
            luminosity_avg=avg(lights),
            rain_intensity_avg=avg(rains),
            is_raining_period=any_rain,
            uptime_seconds=last_diag.get("uptime_seconds"),
            wifi_rssi_dbm=last_diag.get("wifi_rssi_dbm"),
            free_heap_bytes=last_diag.get("free_heap_bytes"),
        )

        db.add(registro)
        db.commit()
        db.refresh(registro)

        # Reinicia o buffer da janela após persistir
        self.window_samples[device_id] = []
        self.window_start_by_device[device_id] = now
        self.persisted_once_devices.add(device_id)
        self.total_cold_writes += 1

        return registro


telemetry_engine = HotColdTelemetryEngine()


async def _ingest_telemetry_payload(payload: TelemetryPayload, db: Session) -> TelemetryResponse:
    """Núcleo compartilhado de ingestão Dual-Pipeline (POST direto ou Bridge mDNS local)."""
    agora = datetime.now(timezone.utc)
    dev_id = payload.device_id
    s_dict = payload.sensors.model_dump()
    d_dict = payload.diagnostics.model_dump() if payload.diagnostics else {}

    prev_sample = telemetry_engine.latest_by_device.get(dev_id)

    # Atualiza extremos diários em RAM
    telemetry_engine._update_extremes(dev_id, s_dict)

    # Monta pacote enriquecido para o Hot Path
    hot_packet = {
        "device_id": dev_id,
        "recorded_at": agora.isoformat(),
        "sensors": s_dict,
        "diagnostics": d_dict,
        "extremes": telemetry_engine.daily_extremes.get(dev_id, {}),
    }

    # Registra no buffer da janela atual
    if dev_id not in telemetry_engine.window_samples:
        telemetry_engine.window_samples[dev_id] = []
        telemetry_engine.window_start_by_device[dev_id] = agora

    # Avalia regras do Cold Path (1: Boot inicial, 2: Deadband Anomaly, 3: Janela de 5 minutos)
    anomaly = telemetry_engine.detect_deadband_anomaly(prev_sample, s_dict)
    is_initial_boot = dev_id not in telemetry_engine.persisted_once_devices
    elapsed_sec = (agora - telemetry_engine.window_start_by_device[dev_id]).total_seconds()
    is_window_expired = elapsed_sec >= COLD_PATH_WINDOW_SECONDS

    # Se houve mudança brusca (Deadband), reinicia a janela com a leitura atual para não diluir o salto na média anterior
    if anomaly:
        telemetry_engine.window_samples[dev_id] = [hot_packet]
        telemetry_engine.window_start_by_device[dev_id] = agora
    else:
        telemetry_engine.window_samples[dev_id].append(hot_packet)

    telemetry_engine.latest_by_device[dev_id] = hot_packet
    telemetry_engine.total_hot_ticks += 1

    if dev_id not in telemetry_engine.live_ring_by_device:
        telemetry_engine.live_ring_by_device[dev_id] = deque(maxlen=30)
    telemetry_engine.live_ring_by_device[dev_id].append(hot_packet)

    cold_persisted = False
    reason = "HOT_PATH_MEMORY_ONLY"

    if anomaly:
        evento = TelemetryEvent(
            device_id=dev_id,
            recorded_at=agora,
            event_type=anomaly["event_type"],
            severity=anomaly["severity"],
            title=anomaly["title"],
            description=anomaly["description"],
            snapshot_json=json.dumps(s_dict),
        )
        db.add(evento)
        db.commit()
        hot_packet["latest_event"] = evento.to_dict()

    if is_initial_boot or anomaly or is_window_expired:
        reason = (
            "DEADBAND_EVENT"
            if anomaly
            else ("WINDOW_5M" if is_window_expired else "INITIAL_BOOT")
        )
        agg_rec = telemetry_engine.flush_window_to_db(db, dev_id, agora)
        cold_persisted = True
        hot_packet["id"] = agg_rec.id

    hot_packet["pipeline"] = {
        "hot_path_streamed": True,
        "cold_path_persisted": cold_persisted,
        "persistence_reason": reason,
        "hot_ticks_total": telemetry_engine.total_hot_ticks,
        "cold_writes_total": telemetry_engine.total_cold_writes,
        "buffer_samples": len(telemetry_engine.window_samples.get(dev_id, [])),
    }

    # Disparo imediato no Hot Path via SSE (< 15ms)
    await broadcaster.broadcast(hot_packet)

    status_tag = f"COLD DB [{reason}]" if cold_persisted else "HOT RAM [SSE ONLY]"
    print(
        f"[{status_tag}] {dev_id} | "
        f"T: {s_dict.get('temperature_c')}°C | U: {s_dict.get('humidity_pct')}% | "
        f"P: {s_dict.get('pressure_hpa')}hPa | Luz: {s_dict.get('luminosity_pct')}% | "
        f"Chuva: {s_dict.get('rain_intensity_pct')}%"
    )

    return TelemetryResponse(
        status="success",
        message="Telemetria processada no Hot Path e avaliada pelo Cold Path.",
        device_id=dev_id,
        recorded_at=agora.isoformat(),
        hot_path_streamed=True,
        cold_path_persisted=cold_persisted,
        persistence_reason=reason,
    )


def _parse_esp32_raw_block(raw_text: str) -> Optional[TelemetryPayload]:
    """
    Extrai a última leitura física real diretamente do buffer /raw da ESP32 via mDNS.
    Garante funcionamento imediato na rede local mesmo quando o roteador altera o IP DHCP do host.
    """
    blocks = [b.strip() for b in raw_text.split("==================================================") if "[DHT22]" in b or "[LDR]" in b]
    if not blocks:
        return None
    last_block = blocks[-1]

    dht_m = re.search(r"\[DHT22\]\s+Temp:\s*([\d.]+)\s*°C\s*\|\s*Umidade:\s*([\d.]+)\s*%", last_block)
    bmp_m = re.search(r"\[BMP280\]\s+Temp:\s*([\d.]+)\s*°C\s*\|\s*Pressao:\s*([\d.]+)\s*hPa\s*\|\s*Alt\.\s*Aprox:\s*([\d.]+)\s*m", last_block)
    mq_m = re.search(r"\[MQ-135\].*?PPM:\s*([\d.]+)", last_block)
    ldr_m = re.search(r"\[LDR\]\s+ADC:\s*(\d+)\s*\|.*?Luz:\s*([\d.]+)\s*%", last_block)
    rain_m = re.search(r"\[CHUVA\]\s+ADC:\s*(\d+)\s*\|.*?Agua:\s*([\d.]+)\s*%\s*\|\s*Chuva:\s*(SIM|NAO)", last_block)

    if not (dht_m or bmp_m or ldr_m):
        return None

    temp_c = float(dht_m.group(1)) if dht_m else (float(bmp_m.group(1)) if bmp_m else None)
    hum_pct = float(dht_m.group(2)) if dht_m else None
    press_hpa = float(bmp_m.group(2)) if bmp_m else None
    alt_m = float(bmp_m.group(3)) if bmp_m else None
    ppm = float(mq_m.group(1)) if mq_m else 10.0
    luz = float(ldr_m.group(2)) if ldr_m else 0.0

    # Calibração de baseline real e filtro de ruído ADC1 para o sensor de chuva (GPIO 34):
    # Em circuito aberto (placa seca), o pino GPIO 34 flutua entre ADC 650 e 2800 (~0.65V a 2.4V)
    # devido ao acoplamento com o canal adjacente (GPIO 35). Apenas quando há água fechando
    # contato físico na malha condutiva (ou DO ativo em nível baixo) o ADC cai abaixo de 500.
    agua = 0.0
    chovendo = False
    if rain_m:
        rain_adc = int(rain_m.group(1))
        if rain_adc < 500:
            agua = round(min(100.0, max(0.0, ((500.0 - rain_adc) / 450.0) * 100.0)), 1)
            chovendo = agua >= 5.0

    return TelemetryPayload(
        device_id="esp32-meteo-01",
        sensors=SensorDataSchema(
            temperature_c=temp_c,
            humidity_pct=hum_pct,
            pressure_hpa=press_hpa,
            altitude_m=alt_m,
            air_quality_ppm=ppm,
            luminosity_pct=luz,
            rain_intensity_pct=agua,
            is_raining=chovendo,
        ),
        diagnostics=DiagnosticsSchema(wifi_rssi_dbm=-52),
    )


def _fetch_esp32_raw_sync() -> Optional[str]:
    try:
        req = urllib.request.Request(ESP32_MDNS_RAW_URL, headers={"User-Agent": "EcoPulse-Backend/2.0"})
        with urllib.request.urlopen(req, timeout=1.5) as resp:
            if resp.status == 200:
                return resp.read().decode("utf-8", errors="ignore")
    except Exception:
        return None
    return None


async def _esp32_mdns_bridge_loop():
    """
    Loop resiliente de descoberta mDNS (esp32.local):
    Se a ESP32 estiver online na LAN mas tentando enviar POST para um IP DHCP antigo do computador,
    coleta automaticamente as leituras reais em http://esp32.local/raw a cada 2.5s.
    """
    while True:
        await asyncio.sleep(2.5)
        if "PYTEST_CURRENT_TEST" in os.environ:
            continue
        # Se a ESP32 já está entregando POST diretamente nos últimos 4s, não precisa fazer pull
        if (time.monotonic() - telemetry_engine.last_direct_push_ts) < 4.0:
            continue

        raw_text = await asyncio.to_thread(_fetch_esp32_raw_sync)
        if not raw_text:
            continue

        payload = _parse_esp32_raw_block(raw_text)
        if payload:
            db = SessionLocal()
            try:
                await _ingest_telemetry_payload(payload, db)
            except Exception:
                pass
            finally:
                db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Inicializa as tabelas do Cold Path e a ponte mDNS resiliente no boot da aplicação (apenas em ambiente local)."""
    shutdown_event.clear()

    # Evita deadlock no desligamento/reload: o Uvicorn espera as conexões abertas terminarem
    # antes de rodar o shutdown do lifespan, mas os streams SSE só terminam quando
    # shutdown_event é setado. Encadeamos ao handler original do Uvicorn para sinalizar
    # os streams assim que SIGINT/SIGTERM chegar.
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        original_handler = signal.getsignal(sig)

        def _on_shutdown_signal(signum, frame, _orig=original_handler):
            loop.call_soon_threadsafe(shutdown_event.set)
            if callable(_orig):
                _orig(signum, frame)

        try:
            signal.signal(sig, _on_shutdown_signal)
        except ValueError:
            pass  # Fora da thread principal (ex.: TestClient) — não se aplica

    Base.metadata.create_all(bind=engine)
    bridge_task = None
    if "PYTEST_CURRENT_TEST" not in os.environ and os.getenv("APP_ENV") != "production":
        bridge_task = asyncio.create_task(_esp32_mdns_bridge_loop())
    try:
        yield
    finally:
        shutdown_event.set()
        if bridge_task:
            bridge_task.cancel()


app = FastAPI(
    title="EcoPulse IoT API — Hot/Cold Path",
    description=(
        "API de Telemetria Meteorológica com Dual-Pipeline: "
        "Hot Path (RAM + SSE < 15ms) e Cold Path (Agregação 5m WMO-No. 8 + Deadband no PostgreSQL)."
    ),
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["Monitoramento"])
def health_check():
    """Diagnóstico operacional da API e métricas de economia de I/O do Hot/Cold Path."""
    hot = telemetry_engine.total_hot_ticks
    cold = telemetry_engine.total_cold_writes
    io_saved_pct = round((1 - (cold / hot)) * 100, 2) if hot > 0 and cold <= hot else 0.0
    return {
        "status": "healthy",
        "architecture": "Hot/Cold Path Dual-Pipeline",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "subscribers_online": len(broadcaster._subscribers),
        "pipeline_metrics": {
            "hot_path_ticks_received": hot,
            "cold_path_db_writes": cold,
            "disk_io_reduction_pct": io_saved_pct,
            "window_interval_seconds": COLD_PATH_WINDOW_SECONDS,
        },
    }


@app.post(
    "/api/v1/telemetry",
    status_code=status.HTTP_201_CREATED,
    response_model=TelemetryResponse,
    tags=["Telemetria"],
)
async def receber_telemetria(
    payload: TelemetryPayload,
    _auth: str = Header(..., alias="X-API-Key"),
    db: Session = Depends(get_db),
):
    """
    Ingestão Dual-Pipeline:
    1. Hot Path: Atualiza estado em RAM e transmite imediatamente via SSE (< 15ms).
    2. Cold Path: Agrega em janela de 5 minutos ou persiste imediatamente se detectar Deadband/Exceção.
    """
    if _auth != API_SECRET_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Chave de autenticação 'X-API-Key' inválida.",
        )

    telemetry_engine.last_direct_push_ts = time.monotonic()
    return await _ingest_telemetry_payload(payload, db)


@app.get("/api/v1/telemetry/stream", tags=["Telemetria"])
async def stream_telemetria(request: Request, db: Session = Depends(get_db)):
    """
    Canal Server-Sent Events (SSE) do Hot Path.
    Entrega a leitura atual imediatamente ao conectar e faz push contínuo em < 15ms.
    """
    queue = await broadcaster.subscribe()

    async def event_generator():
        try:
            # Sincronização imediata na abertura do stream (prioriza Hot Path em RAM)
            if telemetry_engine.latest_by_device:
                latest_mem = next(iter(telemetry_engine.latest_by_device.values()))
                yield f"data: {json.dumps(latest_mem)}\n\n"
            else:
                ultimo_db = (
                    db.query(TelemetryAggregated5m)
                    .order_by(TelemetryAggregated5m.window_end.desc())
                    .first()
                )
                if ultimo_db:
                    yield f"data: {json.dumps(ultimo_db.to_dict())}\n\n"

            while not shutdown_event.is_set():
                if await request.is_disconnected():
                    break
                try:
                    data = await asyncio.wait_for(queue.get(), timeout=2.0)
                    yield f"data: {json.dumps(data)}\n\n"
                except asyncio.TimeoutError:
                    if shutdown_event.is_set():
                        break
                    yield ": ping\n\n"
        finally:
            broadcaster.unsubscribe(queue)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@app.get("/api/v1/telemetry/latest", tags=["Telemetria"])
def obter_ultima_telemetria(
    device_id: Optional[str] = Query(None, description="Filtra por identificador de estação"),
    db: Session = Depends(get_db),
):
    """
    Retorna o estado mais recente da estação a partir do Hot Path em memória RAM (O(1)),
    ou faz fallback para a última janela consolidada no PostgreSQL caso o servidor tenha acabado de iniciar.
    """
    # 1. Tenta obter do Hot Path em memória RAM
    if device_id and device_id in telemetry_engine.latest_by_device:
        packet = dict(telemetry_engine.latest_by_device[device_id])
        return packet
    elif not device_id and telemetry_engine.latest_by_device:
        packet = dict(next(iter(telemetry_engine.latest_by_device.values())))
        return packet

    # 2. Fallback para o Cold Path persistido no banco
    query = db.query(TelemetryAggregated5m)
    if device_id:
        query = query.filter(TelemetryAggregated5m.device_id == device_id)

    registro = query.order_by(TelemetryAggregated5m.window_end.desc()).first()
    if not registro:
        return {"status": "empty", "message": "Nenhum registro encontrado."}
    return registro.to_dict()


@app.get("/api/v1/telemetry/history", tags=["Telemetria"])
def obter_historico_telemetria(
    limit: int = Query(48, ge=1, le=500, description="Quantidade máxima de janelas consolidadas"),
    device_id: Optional[str] = Query(None, description="Filtra por estação"),
    db: Session = Depends(get_db),
):
    """
    Retorna a série temporal consolidada pelo Cold Path (tb_telemetry_aggregated_5m).
    Quando há poucos blocos consolidados no banco após o boot, complementa com os pontos
    recentes do ring-buffer para visualização contínua imediata.
    """
    query = db.query(TelemetryAggregated5m)
    if device_id:
        query = query.filter(TelemetryAggregated5m.device_id == device_id)

    ultimos_db = query.order_by(TelemetryAggregated5m.window_end.desc()).limit(limit).all()
    cronologicos = [r.to_dict() for r in reversed(ultimos_db)]

    # Mescla sempre os ticks recentes do ring-buffer em RAM (Hot Path) posteriores à última janela do banco
    ring_target = None
    if device_id and device_id in telemetry_engine.live_ring_by_device:
        ring_target = list(telemetry_engine.live_ring_by_device[device_id])
    elif not device_id and telemetry_engine.live_ring_by_device:
        ring_target = list(next(iter(telemetry_engine.live_ring_by_device.values())))

    if ring_target:
        existing_ts = {item.get("recorded_at") for item in cronologicos}
        for sample in ring_target:
            if sample.get("recorded_at") not in existing_ts:
                cronologicos.append(sample)

    return cronologicos[-limit:]


@app.get("/api/v1/telemetry/events", tags=["Telemetria"])
def obter_eventos_climaticos(
    limit: int = Query(10, ge=1, le=100, description="Quantidade máxima de eventos/alertas"),
    device_id: Optional[str] = Query(None, description="Filtra por estação"),
    db: Session = Depends(get_db),
):
    """Retorna os alertas e eventos extraordinários registrados pelo detector de Deadband."""
    query = db.query(TelemetryEvent)
    if device_id:
        query = query.filter(TelemetryEvent.device_id == device_id)

    eventos = query.order_by(TelemetryEvent.recorded_at.desc()).limit(limit).all()
    return [e.to_dict() for e in eventos]


# Monta o Frontend estático na raiz se o diretório existir localmente (facilita acesso em http://localhost:8000)
FRONTEND_DIR = Path(__file__).resolve().parent.parent.parent / "frontend"
if FRONTEND_DIR.is_dir():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")
