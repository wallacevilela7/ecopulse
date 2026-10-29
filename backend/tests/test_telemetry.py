"""
Testes automatizados da API de Telemetria do EcoPulse (PIM II).
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app, API_SECRET_KEY

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "service" in data


def test_telemetry_missing_auth():
    payload = {
        "device_id": "esp32-meteo-01",
        "sensors": {
            "temperature_c": 23.3,
            "humidity_pct": 77.1
        }
    }
    response = client.post("/api/v1/telemetry", json=payload)
    assert response.status_code == 422 or response.status_code == 401


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


def test_telemetry_success():
    payload = {
        "device_id": "esp32-meteo-01",
        "sensors": {
            "temperature_c": 23.30,
            "humidity_pct": 77.40,
            "pressure_hpa": 925.60,
            "altitude_m": 756.75,
            "air_quality_ppm": 15.0,
            "luminosity_pct": 35.8,
            "rain_intensity_pct": 0.0,
            "is_raining": False
        },
        "diagnostics": {
            "uptime_seconds": 180,
            "wifi_rssi_dbm": -55
        }
    }
    response = client.post(
        "/api/v1/telemetry",
        json=payload,
        headers={"X-API-Key": API_SECRET_KEY}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "success"
    assert data["device_id"] == "esp32-meteo-01"
    assert "recorded_at" in data

    # Testa se a última telemetria ficou salva em memória
    latest_resp = client.get("/api/v1/telemetry/latest")
    assert latest_resp.status_code == 200
    latest_data = latest_resp.json()
    assert latest_data["device_id"] == "esp32-meteo-01"
    assert latest_data["sensors"]["temperature_c"] == 23.30
    assert latest_data["sensors"]["is_raining"] is False
