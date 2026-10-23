# Contrato e Especificação da API REST

A API do **EcoPulse** adota os padrões arquiteturais RESTful, com comunicação síncrona via HTTP/1.1 sobre TCP/IP e serialização em JSON (`application/json`).

---

## 1. Segurança e Autenticação

Todas as operações de escrita que originam do hardware exigem a passagem do cabeçalho de autenticação:

| Cabeçalho | Tipo | Descrição | Exemplo |
| :--- | :--- | :--- | :--- |
| `X-API-Key` | String | Chave de segurança pré-compartilhada da estação | `chave-secreta-estacao-unip-2026` |

Requisições que omitirem o cabeçalho ou fornecerem uma chave incorreta receberão imediatamente o código `HTTP 401 Unauthorized`.

---

## 2. Endpoints da API

### `POST /api/v1/telemetry`
Recebe o pacote de leitura periódica transmitido pelo microcontrolador ESP32.

* **Headers Obrigatórios:**
  * `Content-Type: application/json`
  * `X-API-Key: <CHAVE_SECRETA>`
* **Corpo da Requisição:** Consultar o arquivo [`docs/contratos/payload_exemplo.json`](file:///home/wvs/Documents/ccomp-unip/2sem/pim2/ecopulse/docs/contratos/payload_exemplo.json).
* **Respostas:**
  * `201 Created`: Telemetria processada e persistida com sucesso.
    ```json
    {
      "status": "success",
      "message": "Telemetry record saved successfully",
      "id": "e7b0c792-2a29-4b66-a364-51786522c0d1",
      "recorded_at": "2026-03-24T12:00:00Z"
    }
    ```
  * `400 Bad Request` / `422 Unprocessable Entity`: Validação de tipos ou campos ausentes falhou.
  * `401 Unauthorized`: Token ausente ou divergente.
  * `500 Internal Server Error`: Falha de conexão com o banco de dados.

---

### `GET /api/v1/telemetry/latest`
Retorna a medição mais recente enviada pela estação para atualização imediata dos medidores do Dashboard.

* **Parâmetros de Query:**
  * `device_id` (Opcional, string): Identificador da estação. Padrão: estação padrão do sistema.
* **Respostas:**
  * `200 OK`:
    ```json
    {
      "device_id": "esp32-meteo-01",
      "recorded_at": "2026-03-24T12:00:00Z",
      "temperature_c": 24.5,
      "humidity_pct": 68.2,
      "pressure_hpa": 1012.8,
      "luminosity_pct": 69.3,
      "air_quality_ppm": 412.5,
      "air_quality_status": "GOOD",
      "is_raining": false,
      "heat_index_c": 24.8,
      "dew_point_c": 18.2
    }
    ```

---

### `GET /api/v1/telemetry/history`
Retorna um vetor temporal com o histórico de leituras filtrado por janela de tempo, otimizado para gráficos.

* **Parâmetros de Query:**
  * `device_id` (Opcional, string)
  * `hours` (Opcional, integer): Quantidade de horas anteriores (Padrão: `24`, Máximo: `168`).
* **Respostas:**
  * `200 OK`: Array de objetos contendo timestamp e grandezas meteorológicas.

---

### `GET /api/v1/telemetry/summary`
Retorna dados estatísticos consolidados para os cards de resumo (mínimas, máximas, alertas ativos).

* **Respostas:**
  * `200 OK`:
    ```json
    {
      "period_hours": 24,
      "max_temperature_c": 31.2,
      "min_temperature_c": 18.4,
      "avg_humidity_pct": 65.0,
      "rain_accumulated_hours": 1.5,
      "active_alerts_count": 0
    }
    ```

---

### `GET /health`
Endpoint de liveness/readiness para balanceadores de carga e containers Docker.

* **Respostas:**
  * `200 OK`:
    ```json
    {
      "status": "healthy",
      "timestamp": "2026-03-24T12:00:05Z",
      "database_connected": true
    }
    ```
