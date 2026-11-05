# Contrato e Especificação da API REST & SSE (v2.0 — Hot/Cold Path)

A API do **EcoPulse** combina endpoints RESTful (`application/json`) e canal de streaming **Server-Sent Events (`text/event-stream`)** para atender simultaneamente ao *Hot Path* (tempo real em memória) e ao *Cold Path* (histórico consolidado no PostgreSQL).

---

## 1. Autenticação da Borda (ESP32)

| Cabeçalho | Tipo | Obrigatório em | Descrição |
| :--- | :--- | :---: | :--- |
| `X-API-Key` | String | `POST /api/v1/telemetry` | Chave pré-compartilhada da estação (`API_SECRET_KEY`). |

---

## 2. Endpoints Operacionais

### `POST /api/v1/telemetry`
Recebe a leitura periódica (2,5s) do ESP32, transmite imediatamente no **Hot Path** via SSE e avalia as regras do **Cold Path** (janela de 5 minutos ou disparo por *Deadband*).

* **Resposta `201 Created`:**
  ```json
  {
    "status": "success",
    "message": "Telemetria processada no Hot Path e avaliada pelo Cold Path.",
    "device_id": "esp32-meteo-01",
    "recorded_at": "2026-11-05T22:30:00Z",
    "hot_path_streamed": true,
    "cold_path_persisted": false,
    "persistence_reason": "HOT_PATH_MEMORY_ONLY"
  }
  ```
  *(Valores possíveis de `persistence_reason`: `HOT_PATH_MEMORY_ONLY`, `INITIAL_BOOT`, `WINDOW_5M`, `DEADBAND_EVENT`)*

---

### `GET /api/v1/telemetry/stream`
Canal contínuo **Server-Sent Events (SSE)**. Assim que o cliente abre a conexão, recebe o estado atual em memória RAM e passa a receber cada novo pacote do ESP32 em menos de 15ms.

---

### `GET /api/v1/telemetry/latest`
Retorna em $O(1)$ o estado atual mantido no **Hot Path (RAM)** — ou reconstrói a partir do último bloco consolidado no PostgreSQL caso o servidor tenha acabado de iniciar — incluindo os extremos diários (`temp_min`, `temp_max`).

---

### `GET /api/v1/telemetry/history?limit=48`
Retorna as janelas temporais consolidadas pelo **Cold Path** (`tb_telemetry_aggregated_5m`), contendo médias e extremos (`temp_min`, `temp_max`), utilizadas para renderizar as barras de amplitude térmica estilo iOS Weather e os gráficos do Chart.js.

---

### `GET /api/v1/telemetry/events?limit=10`
Retorna os alertas e anomalias climáticas detectadas pelo algoritmo de **Deadband** e gravadas em `tb_telemetry_events` (início/fim de chuva, queda barométrica $\ge 2\text{ hPa}$, pico de gases $\ge 50\text{ PPM}$).

---

### `GET /health`
Retorna o diagnóstico de saúde do container e as métricas de economia de I/O do pipeline (`hot_path_ticks_received`, `cold_path_db_writes`, `disk_io_reduction_pct`).
