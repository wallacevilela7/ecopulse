"""
Schemas de validação Pydantic v2 para os contratos de telemetria do EcoPulse (Hot/Cold Path).
"""
from typing import Optional
from pydantic import BaseModel, Field


class SensorDataSchema(BaseModel):
    temperature_c: Optional[float] = Field(None, description="Temperatura em graus Celsius (DHT22/BMP280)")
    humidity_pct: Optional[float] = Field(None, description="Umidade relativa do ar em % (DHT22)")
    pressure_hpa: Optional[float] = Field(None, description="Pressão atmosférica em hPa (BMP280)")
    altitude_m: Optional[float] = Field(None, description="Altitude aproximada em metros (BMP280)")
    air_quality_ppm: Optional[float] = Field(None, description="Concentração estimada de gases em PPM (MQ-135)")
    luminosity_pct: Optional[float] = Field(None, description="Intensidade luminosa em % (LDR)")
    rain_intensity_pct: Optional[float] = Field(None, description="Intensidade de chuva em % (Pluviômetro)")
    is_raining: Optional[bool] = Field(False, description="Flag booleana indicando precipitação ativa")


class DiagnosticsSchema(BaseModel):
    uptime_seconds: Optional[int] = Field(None, description="Tempo de atividade do ESP32 em segundos")
    wifi_rssi_dbm: Optional[int] = Field(None, description="Potência do sinal Wi-Fi em dBm")
    free_heap_bytes: Optional[int] = Field(None, description="Memória RAM livre no ESP32 em bytes")


class TelemetryPayload(BaseModel):
    device_id: str = Field("esp32-meteo-01", description="Identificador único da estação emissora")
    sensors: SensorDataSchema = Field(..., description="Leituras dos 5 sensores físicos")
    diagnostics: Optional[DiagnosticsSchema] = Field(default_factory=DiagnosticsSchema, description="Metadados operacionais")


class TelemetryResponse(BaseModel):
    status: str = "success"
    message: str = "Telemetria processada com sucesso"
    device_id: str
    recorded_at: str
    hot_path_streamed: bool = True
    cold_path_persisted: bool = False
    persistence_reason: str = "HOT_PATH_MEMORY_ONLY"
