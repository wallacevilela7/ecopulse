"""
Modelos relacionais ORM (SQLAlchemy) do EcoPulse.
Tabela tb_telemetry_records otimizada com índices para séries temporais.
"""
from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    Integer,
    Float,
    String,
    Boolean,
    DateTime,
    Index,
    func,
)
from app.database import Base


class TelemetryRecord(Base):
    __tablename__ = "tb_telemetry_records"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    device_id = Column(String(50), nullable=False, index=True)
    recorded_at = Column(DateTime(timezone=True), nullable=False, index=True)
    received_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # Medições Ambientais dos Sensores
    temperature_c = Column(Float, nullable=True)
    humidity_pct = Column(Float, nullable=True)
    pressure_hpa = Column(Float, nullable=True)
    altitude_m = Column(Float, nullable=True)
    air_quality_ppm = Column(Float, nullable=True)
    luminosity_pct = Column(Float, nullable=True)
    rain_intensity_pct = Column(Float, nullable=True)
    is_raining = Column(Boolean, default=False, nullable=False)

    # Metadados e Diagnósticos de Borda
    uptime_seconds = Column(Integer, nullable=True)
    wifi_rssi_dbm = Column(Integer, nullable=True)
    free_heap_bytes = Column(Integer, nullable=True)

    # Índice Composto para consultas temporais velozes em O(1)
    __table_args__ = (
        Index("idx_device_recorded", "device_id", "recorded_at"),
    )

    def to_dict(self):
        """Converte o modelo para dicionário compatível com o schema JSON da API."""
        return {
            "id": self.id,
            "device_id": self.device_id,
            "recorded_at": self.recorded_at.isoformat() if self.recorded_at else None,
            "received_at": self.received_at.isoformat() if self.received_at else None,
            "sensors": {
                "temperature_c": self.temperature_c,
                "humidity_pct": self.humidity_pct,
                "pressure_hpa": self.pressure_hpa,
                "altitude_m": self.altitude_m,
                "air_quality_ppm": self.air_quality_ppm,
                "luminosity_pct": self.luminosity_pct,
                "rain_intensity_pct": self.rain_intensity_pct,
                "is_raining": self.is_raining,
            },
            "diagnostics": {
                "uptime_seconds": self.uptime_seconds,
                "wifi_rssi_dbm": self.wifi_rssi_dbm,
                "free_heap_bytes": self.free_heap_bytes,
            },
        }
