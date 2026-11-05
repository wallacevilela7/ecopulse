"""
Modelos relacionais ORM (SQLAlchemy) do EcoPulse — Arquitetura Cold Path (WMO-No. 8 / INMET).
- tb_telemetry_aggregated_5m: Consolidações estatísticas periódicas (médias, mínimas e máximas).
- tb_telemetry_events: Registros imediatos disparados por Deadband / Exceção Climática.
"""
import json
from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    Integer,
    Float,
    String,
    Boolean,
    DateTime,
    Index,
)
from app.database import Base


class TelemetryAggregated5m(Base):
    """Série temporal consolidada do Cold Path (janelas de 5 minutos ou snapshots de exceção)."""
    __tablename__ = "tb_telemetry_aggregated_5m"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    device_id = Column(String(50), nullable=False, index=True)
    window_start = Column(DateTime(timezone=True), nullable=False)
    window_end = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, index=True)
    samples_count = Column(Integer, default=1, nullable=False)

    # Estatísticas da Janela (Temperatura, Umidade, Pressão)
    temp_avg = Column(Float, nullable=True)
    temp_min = Column(Float, nullable=True)
    temp_max = Column(Float, nullable=True)

    humidity_avg = Column(Float, nullable=True)
    humidity_min = Column(Float, nullable=True)
    humidity_max = Column(Float, nullable=True)

    pressure_avg = Column(Float, nullable=True)
    pressure_min = Column(Float, nullable=True)
    pressure_max = Column(Float, nullable=True)

    altitude_avg = Column(Float, nullable=True)
    air_quality_avg = Column(Float, nullable=True)
    air_quality_max = Column(Float, nullable=True)
    luminosity_avg = Column(Float, nullable=True)
    rain_intensity_avg = Column(Float, nullable=True)
    is_raining_period = Column(Boolean, default=False, nullable=False)

    # Diagnósticos do nó no fechamento da janela
    uptime_seconds = Column(Integer, nullable=True)
    wifi_rssi_dbm = Column(Integer, nullable=True)
    free_heap_bytes = Column(Integer, nullable=True)

    __table_args__ = (
        Index("idx_agg5m_device_window", "device_id", "window_end"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "device_id": self.device_id,
            "window_start": self.window_start.isoformat() if self.window_start else None,
            "window_end": self.window_end.isoformat() if self.window_end else None,
            "recorded_at": self.window_end.isoformat() if self.window_end else None,
            "samples_count": self.samples_count,
            "extremes": {
                "temp_min": self.temp_min,
                "temp_max": self.temp_max,
                "humidity_min": self.humidity_min,
                "humidity_max": self.humidity_max,
                "pressure_min": self.pressure_min,
                "pressure_max": self.pressure_max,
                "air_quality_max": self.air_quality_max,
            },
            "sensors": {
                "temperature_c": self.temp_avg,
                "humidity_pct": self.humidity_avg,
                "pressure_hpa": self.pressure_avg,
                "altitude_m": self.altitude_avg,
                "air_quality_ppm": self.air_quality_avg,
                "luminosity_pct": self.luminosity_avg,
                "rain_intensity_pct": self.rain_intensity_avg,
                "is_raining": self.is_raining_period,
            },
            "diagnostics": {
                "uptime_seconds": self.uptime_seconds,
                "wifi_rssi_dbm": self.wifi_rssi_dbm,
                "free_heap_bytes": self.free_heap_bytes,
            },
        }


class TelemetryEvent(Base):
    """Eventos extraordinários persistidos imediatamente via Deadband no Cold Path."""
    __tablename__ = "tb_telemetry_events"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    device_id = Column(String(50), nullable=False, index=True)
    recorded_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, index=True)
    event_type = Column(String(40), nullable=False)
    severity = Column(String(20), nullable=False, default="WARNING")
    title = Column(String(120), nullable=False)
    description = Column(String(500), nullable=False)
    snapshot_json = Column(String(2000), nullable=True)

    __table_args__ = (
        Index("idx_events_device_time", "device_id", "recorded_at"),
    )

    def to_dict(self):
        snapshot = None
        if self.snapshot_json:
            try:
                snapshot = json.loads(self.snapshot_json)
            except Exception:
                snapshot = None
        return {
            "id": self.id,
            "device_id": self.device_id,
            "recorded_at": self.recorded_at.isoformat() if self.recorded_at else None,
            "event_type": self.event_type,
            "severity": self.severity,
            "title": self.title,
            "description": self.description,
            "snapshot": snapshot,
        }
