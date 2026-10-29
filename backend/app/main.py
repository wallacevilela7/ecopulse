"""
EcoPulse - Backend API (FastAPI)
Projeto Integrado Multidisciplinar II (PIM II - UNIP)
Receptor e Validador de Telemetria IoT
"""
import os
from datetime import datetime, timezone
from typing import Optional, Dict, Any

from fastapi import FastAPI, Header, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from app.schemas import TelemetryPayload, TelemetryResponse

# Carrega variáveis do arquivo .env
load_dotenv()

API_SECRET_KEY = os.getenv("API_SECRET_KEY", "chave-secreta-estacao-unip-2026")

app = FastAPI(
    title="EcoPulse IoT API",
    description="API de Ingestão e Telemetria Meteorológica da Estação EcoPulse (ESP32)",
    version="1.0.0",
)

# Habilita CORS para permitir conexões do futuro Dashboard Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Armazenamento em memória da última telemetria recebida (ponte imediata)
latest_telemetry: Dict[str, Any] = {}


def verificar_autenticacao(x_api_key: Optional[str] = Header(None)) -> str:
    """Valida o cabeçalho X-API-Key enviado pelo ESP32."""
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Cabeçalho 'X-API-Key' ausente na requisição.",
        )
    if x_api_key != API_SECRET_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Chave de autenticação 'X-API-Key' inválida.",
        )
    return x_api_key


@app.get("/health", tags=["Monitoramento"])
def health_check():
    """Endpoint de verificação de integridade da API."""
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "service": "EcoPulse Backend API",
    }


@app.post(
    "/api/v1/telemetry",
    status_code=status.HTTP_201_CREATED,
    response_model=TelemetryResponse,
    tags=["Telemetria"],
)
def receber_telemetria(
    payload: TelemetryPayload,
    _auth: str = Header(..., alias="X-API-Key"),
):
    """
    Endpoint principal de ingestão de telemetria emitido pelo ESP32 via HTTP POST.
    Valida a chave de autenticação, checa os tipos de dados e registra a leitura.
    """
    # Validação da chave
    if _auth != API_SECRET_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Chave de autenticação 'X-API-Key' inválida.",
        )

    agora = datetime.now(timezone.utc)
    s = payload.sensors
    d = payload.diagnostics

    # Atualiza o buffer da última leitura em memória
    latest_telemetry.clear()
    latest_telemetry.update({
        "device_id": payload.device_id,
        "recorded_at": agora.isoformat(),
        "sensors": s.model_dump(),
        "diagnostics": d.model_dump() if d else {},
    })

    # Log formatado e colorido no terminal do Backend
    print("\n" + "=" * 65)
    print(f"📡 [TELEMETRIA RECEBIDA] Estação: {payload.device_id} | {agora.strftime('%H:%M:%S')}")
    print("-" * 65)
    print(f"🌡️  Temperatura:  {s.temperature_c:.1f} °C" if s.temperature_c is not None else "🌡️  Temperatura:  N/D")
    print(f"💧 Umidade:      {s.humidity_pct:.1f} %" if s.humidity_pct is not None else "💧 Umidade:      N/D")
    print(f"🧭 Pressão:      {s.pressure_hpa:.1f} hPa" if s.pressure_hpa is not None else "🧭 Pressão:      N/D")
    print(f"⛰️  Altitude:     {s.altitude_m:.1f} m" if s.altitude_m is not None else "⛰️  Altitude:     N/D")
    print(f"💨 Ar / Gases:   {s.air_quality_ppm:.1f} PPM" if s.air_quality_ppm is not None else "💨 Ar / Gases:   N/D")
    print(f"☀️  Luz (LDR):    {s.luminosity_pct:.1f} %" if s.luminosity_pct is not None else "☀️  Luz (LDR):    N/D")
    chuva_str = "SIM (CHUVOSO)" if s.is_raining else "NÃO (Seco)"
    print(f"🌧️  Chuva:        {chuva_str} ({s.rain_intensity_pct:.1f} %)" if s.rain_intensity_pct is not None else f"🌧️  Chuva: {chuva_str}")
    if d and d.wifi_rssi_dbm is not None:
        print(f"📶 Wi-Fi RSSI:   {d.wifi_rssi_dbm} dBm | Uptime: {d.uptime_seconds or 0}s")
    print("=" * 65 + "\n")

    return TelemetryResponse(
        status="success",
        message="Telemetria validada e recebida com sucesso pelo Backend.",
        device_id=payload.device_id,
        recorded_at=agora.isoformat(),
    )


@app.get("/api/v1/telemetry/latest", tags=["Telemetria"])
def obter_ultima_telemetria():
    """Retorna a medição mais recente recebida da estação ESP32."""
    if not latest_telemetry:
        return {"status": "waiting", "message": "Nenhuma telemetria recebida até o momento."}
    return latest_telemetry
