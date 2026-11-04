"""
EcoPulse - Backend API (FastAPI + SQLAlchemy)
Projeto Integrado Multidisciplinar II (PIM II - UNIP)
Receptor, Persistência, Consultas e Streaming SSE em Tempo Real
"""
import os
import json
import asyncio
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any, Set

from fastapi import FastAPI, Header, HTTPException, Depends, Query, Request, status
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from dotenv import load_dotenv

from app.database import engine, Base, get_db
from app.models import TelemetryRecord
from app.schemas import TelemetryPayload, TelemetryResponse

load_dotenv()

API_SECRET_KEY = os.getenv("API_SECRET_KEY", "chave-secreta-estacao-unip-2026")


# =========================================================================
# Barramento de Eventos em Tempo Real (Pub/Sub para Streaming SSE)
# =========================================================================
class TelemetryBroadcaster:
    """Distribuidor de leituras em tempo real para múltiplos clientes conectados."""
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


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Cria automaticamente as tabelas do banco no boot da aplicação."""
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="EcoPulse IoT API",
    description="API de Ingestão, Persistência e Streaming em Tempo Real (ESP32)",
    version="1.2.0",
    lifespan=lifespan,
)

# Habilita CORS para o Dashboard Web
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["Monitoramento"])
def health_check():
    """Endpoint de verificação de integridade da API."""
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "service": "EcoPulse Backend API",
        "subscribers_online": len(broadcaster._subscribers),
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
    Ingestão de telemetria emitida pelo ESP32 via HTTP POST.
    Valida a chave, grava no banco de dados e transmite instantaneamente (SSE).
    """
    if _auth != API_SECRET_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Chave de autenticação 'X-API-Key' inválida.",
        )

    agora = datetime.now(timezone.utc)
    s = payload.sensors
    d = payload.diagnostics

    # Criação da entidade relacional para persistência no banco
    registro = TelemetryRecord(
        device_id=payload.device_id,
        recorded_at=agora,
        temperature_c=s.temperature_c,
        humidity_pct=s.humidity_pct,
        pressure_hpa=s.pressure_hpa,
        altitude_m=s.altitude_m,
        air_quality_ppm=s.air_quality_ppm,
        luminosity_pct=s.luminosity_pct,
        rain_intensity_pct=s.rain_intensity_pct,
        is_raining=s.is_raining,
        uptime_seconds=d.uptime_seconds if d else None,
        wifi_rssi_dbm=d.wifi_rssi_dbm if d else None,
        free_heap_bytes=d.free_heap_bytes if d else None,
    )

    db.add(registro)
    db.commit()
    db.refresh(registro)

    # Disparo Imediato via SSE para todos os navegadores abertos (< 10ms)
    dict_payload = registro.to_dict()
    await broadcaster.broadcast(dict_payload)

    # Log resumido no terminal do Backend
    chuva_str = "SIM" if s.is_raining else "NÃO"
    print(
        f"[DB PERSISTED #{registro.id} + SSE BROADCAST] {payload.device_id} | "
        f"T: {s.temperature_c}°C | U: {s.humidity_pct}% | "
        f"P: {s.pressure_hpa}hPa | Ar: {s.air_quality_ppm}ppm | "
        f"Luz: {s.luminosity_pct}% | Chuva: {chuva_str}"
    )

    return TelemetryResponse(
        status="success",
        message="Telemetria gravada com sucesso e propagada em tempo real.",
        device_id=payload.device_id,
        recorded_at=agora.isoformat(),
    )


@app.get("/api/v1/telemetry/stream", tags=["Telemetria"])
async def stream_telemetria(request: Request, db: Session = Depends(get_db)):
    """
    Canal de Streaming Server-Sent Events (SSE).
    Mantém conexão persistente e envia novos dados imediatamente após cada leitura do ESP32.
    """
    queue = await broadcaster.subscribe()

    async def event_generator():
        try:
            # Envia a leitura mais recente imediatamente na conexão para sincronizar a tela
            ultimo = db.query(TelemetryRecord).order_by(TelemetryRecord.recorded_at.desc()).first()
            if ultimo:
                yield f"data: {json.dumps(ultimo.to_dict())}\n\n"

            while True:
                if await request.is_disconnected():
                    break
                try:
                    # Aguarda a próxima telemetria emitida pelo ESP32 (ou timeout de 15s para ping de keepalive)
                    data = await asyncio.wait_for(queue.get(), timeout=15.0)
                    yield f"data: {json.dumps(data)}\n\n"
                except asyncio.TimeoutError:
                    # Ping para manter ativa a conexão através de proxies Nginx / Cloudflare
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
    """Retorna a medição mais recente gravada no banco de dados."""
    query = db.query(TelemetryRecord)
    if device_id:
        query = query.filter(TelemetryRecord.device_id == device_id)

    registro = query.order_by(TelemetryRecord.recorded_at.desc()).first()
    if not registro:
        return {"status": "empty", "message": "Nenhum registro encontrado no banco de dados."}
    return registro.to_dict()


@app.get("/api/v1/telemetry/history", tags=["Telemetria"])
def obter_historico_telemetria(
    limit: int = Query(50, ge=1, le=500, description="Quantidade máxima de medições"),
    device_id: Optional[str] = Query(None, description="Filtra por estação"),
    db: Session = Depends(get_db),
):
    """
    Retorna a série temporal cronológica para plotagem dos gráficos no frontend.
    Ordenado do mais antigo para o mais recente dentro do limite selecionado.
    """
    query = db.query(TelemetryRecord)
    if device_id:
        query = query.filter(TelemetryRecord.device_id == device_id)

    # Pega os N mais recentes e reordena em ordem cronológica para plotagem linear
    ultimos = query.order_by(TelemetryRecord.recorded_at.desc()).limit(limit).all()
    cronologicos = list(reversed(ultimos))

    return [r.to_dict() for r in cronologicos]
