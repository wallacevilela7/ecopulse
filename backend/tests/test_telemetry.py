"""
Testes automatizados da API de Telemetria e Banco de Dados (EcoPulse).
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app, API_SECRET_KEY
from app.database import Base, engine

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_database():
    """Garante que as tabelas estejam criadas para os testes."""
    Base.metadata.create_all(bind=engine)
    yield


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "service" in data


def test_telemetry_invalid_auth():
    payload = {
        "device_id": "esp32-meteo-01",
        "sensors": {
            "temperature_c": 23.3,
            "humidity_pct": 77.1
        }
    }
    response = client.post(
        "/api/v1/telemetry",
        json=payload,
        headers={"X-API-Key": "chave-incorreta"}
    )
    assert response.status_code == 401


def test_telemetry_db_persistence_and_query():
    # 1. Envia telemetria válida
    payload = {
        "device_id": "esp32-meteo-01",
        "sensors": {
            "temperature_c": 24.8,
            "humidity_pct": 72.5,
            "pressure_hpa": 926.1,
            "altitude_m": 755.0,
            "air_quality_ppm": 12.0,
            "luminosity_pct": 65.0,
            "rain_intensity_pct": 0.0,
            "is_raining": False
        },
        "diagnostics": {
            "uptime_seconds": 360,
            "wifi_rssi_dbm": -52
        }
    }
    response = client.post(
        "/api/v1/telemetry",
        json=payload,
        headers={"X-API-Key": API_SECRET_KEY}
    )
    assert response.status_code == 201
    assert response.json()["status"] == "success"

    # 2. Testa consulta do registro mais recente no banco
    latest_resp = client.get("/api/v1/telemetry/latest?device_id=esp32-meteo-01")
    assert latest_resp.status_code == 200
    latest = latest_resp.json()
    assert latest["device_id"] == "esp32-meteo-01"
    assert latest["sensors"]["temperature_c"] == 24.8
    assert latest["sensors"]["humidity_pct"] == 72.5
    assert latest["sensors"]["is_raining"] is False

    # 3. Testa consulta do histórico para gráficos
    history_resp = client.get("/api/v1/telemetry/history?limit=10&device_id=esp32-meteo-01")
    assert history_resp.status_code == 200
    history = history_resp.json()
    assert isinstance(history, list)
    assert len(history) >= 1
    assert history[-1]["sensors"]["temperature_c"] == 24.8
