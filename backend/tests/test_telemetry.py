"""
Testes unitários automatizados para a API EcoPulse — Arquitetura Hot/Cold Path.
Valida autenticação, retenção em RAM no Hot Path, agregação e disparo por Deadband no Cold Path.
Utiliza banco SQLite isolado em memória (StaticPool) para nunca poluir o banco real (ecopulse.db).
"""
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app, API_SECRET_KEY, telemetry_engine
from app.database import Base, get_db

# Banco SQLite em memória exclusivo para a suíte de testes
TEST_ENGINE = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=TEST_ENGINE)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def setup_function():
    """Limpa banco de teste isolado em memória antes de cada caso de teste."""
    Base.metadata.drop_all(bind=TEST_ENGINE)
    Base.metadata.create_all(bind=TEST_ENGINE)
    telemetry_engine.reset_state()


def test_health_check_dual_pipeline():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["architecture"] == "Hot/Cold Path Dual-Pipeline"
    assert "pipeline_metrics" in data


def test_telemetry_unauthorized():
    payload = {
        "device_id": "esp32-meteo-01",
        "sensors": {"temperature_c": 25.0, "humidity_pct": 60.0},
    }
    response = client.post(
        "/api/v1/telemetry",
        json=payload,
        headers={"X-API-Key": "chave-invalida"},
    )
    assert response.status_code == 401


def test_hot_cold_path_memory_retention_without_db_spam():
    headers = {"X-API-Key": API_SECRET_KEY}

    # 1º envio (Boot inicial): persiste no Cold Path para inicializar o histórico
    payload_1 = {
        "device_id": "esp32-meteo-01",
        "sensors": {
            "temperature_c": 22.0,
            "humidity_pct": 65.0,
            "pressure_hpa": 1013.0,
            "altitude_m": 760.0,
            "air_quality_ppm": 15.0,
            "luminosity_pct": 50.0,
            "rain_intensity_pct": 0.0,
            "is_raining": False,
        },
        "diagnostics": {"uptime_seconds": 10, "wifi_rssi_dbm": -50},
    }
    r1 = client.post("/api/v1/telemetry", json=payload_1, headers=headers)
    assert r1.status_code == 201
    d1 = r1.json()
    assert d1["hot_path_streamed"] is True
    assert d1["cold_path_persisted"] is True
    assert d1["persistence_reason"] == "INITIAL_BOOT"

    # 2º envio (2.5s depois, sem anomalia): deve ficar APENAS no Hot Path (RAM), sem gravar no BD!
    payload_2 = {
        "device_id": "esp32-meteo-01",
        "sensors": {
            "temperature_c": 22.3,
            "humidity_pct": 65.2,
            "pressure_hpa": 1013.1,
            "altitude_m": 760.0,
            "air_quality_ppm": 16.0,
            "luminosity_pct": 52.0,
            "rain_intensity_pct": 0.0,
            "is_raining": False,
        },
        "diagnostics": {"uptime_seconds": 13, "wifi_rssi_dbm": -49},
    }
    r2 = client.post("/api/v1/telemetry", json=payload_2, headers=headers)
    assert r2.status_code == 201
    d2 = r2.json()
    assert d2["hot_path_streamed"] is True
    assert d2["cold_path_persisted"] is False
    assert d2["persistence_reason"] == "HOT_PATH_MEMORY_ONLY"

    # Consulta /latest deve refletir imediatamente a leitura 2 (22.3°C) direto da RAM e calcular extremos (22.0 a 22.3)
    latest = client.get("/api/v1/telemetry/latest").json()
    assert latest["sensors"]["temperature_c"] == 22.3
    assert latest["extremes"]["temp_min"] == 22.0
    assert latest["extremes"]["temp_max"] == 22.3


def test_cold_path_deadband_anomaly_rain_and_events():
    headers = {"X-API-Key": API_SECRET_KEY}

    # Envio inicial seco
    client.post(
        "/api/v1/telemetry",
        json={
            "device_id": "esp32-meteo-01",
            "sensors": {
                "temperature_c": 22.0,
                "humidity_pct": 70.0,
                "pressure_hpa": 1012.0,
                "air_quality_ppm": 12.0,
                "luminosity_pct": 40.0,
                "rain_intensity_pct": 0.0,
                "is_raining": False,
            },
        },
        headers=headers,
    )

    # Envio com detecção súbita de chuva -> deve acionar DEADBAND_EVENT imediatamente
    r_rain = client.post(
        "/api/v1/telemetry",
        json={
            "device_id": "esp32-meteo-01",
            "sensors": {
                "temperature_c": 21.6,
                "humidity_pct": 82.0,
                "pressure_hpa": 1010.5,
                "air_quality_ppm": 12.0,
                "luminosity_pct": 25.0,
                "rain_intensity_pct": 45.0,
                "is_raining": True,
            },
        },
        headers=headers,
    )
    assert r_rain.status_code == 201
    d_rain = r_rain.json()
    assert d_rain["cold_path_persisted"] is True
    assert d_rain["persistence_reason"] == "DEADBAND_EVENT"

    # Verifica se o alerta foi gravado em /api/v1/telemetry/events
    events = client.get("/api/v1/telemetry/events").json()
    assert len(events) >= 1
    assert events[0]["event_type"] == "RAIN_STARTED"
