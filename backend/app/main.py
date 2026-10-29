"""
EcoPulse - Backend API (FastAPI + SQLAlchemy)
Projeto Integrado Multidisciplinar II (PIM II - UNIP)
Receptor, Persistência e Consultas de Telemetria IoT
"""
import os
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any

from fastapi import FastAPI, Header, HTTPException, Depends, Query, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from dotenv import load_dotenv

from app.database import engine, Base, get_db
from app.models import TelemetryRecord
from app.schemas import TelemetryPayload, TelemetryResponse

load_dotenv()

API_SECRET_KEY = os.getenv("API_SECRET_KEY", "chave-secreta-estacao-unip-2026")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Cria automaticamente as tabelas do banco no boot da aplicação."""
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="EcoPulse IoT API",
    description="API de Ingestão e Telemetria Meteorológica da Estação EcoPulse (ESP32)",
    version="1.1.0",
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
    db: Session = Depends(get_db),
):
    """
    Ingestão de telemetria emitida pelo ESP32 via HTTP POST.
    Valida a chave, grava no banco de dados e registra log.
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

    # Log resumido no terminal do Backend
    chuva_str = "SIM" if s.is_raining else "NÃO"
    print(
        f"[DB PERSISTED #{registro.id}] {payload.device_id} | "
        f"T: {s.temperature_c}°C | U: {s.humidity_pct}% | "
        f"P: {s.pressure_hpa}hPa | Ar: {s.air_quality_ppm}ppm | "
        f"Luz: {s.luminosity_pct}% | Chuva: {chuva_str}"
    )

    return TelemetryResponse(
        status="success",
        message="Telemetria gravada com sucesso no banco de dados.",
        device_id=payload.device_id,
        recorded_at=agora.isoformat(),
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
