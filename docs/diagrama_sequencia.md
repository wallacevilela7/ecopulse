# Diagramas de Sequência do Sistema EcoPulse (Hot/Cold Path)

Os diagramas abaixo ilustram a separação temporal entre o fluxo de baixa latência em memória (**Hot Path**) e a persistência inteligente em janelas e exceções no PostgreSQL (**Cold Path**).

---

## 1. Ingestão Dual-Pipeline (ESP32 $\rightarrow$ Hot Path SSE & Cold Path PostgreSQL)

```mermaid
sequenceDiagram
    autonumber
    participant HW as Cluster 5 Sensores
    participant ESP as ESP32 (Firmware)
    participant API as FastAPI (HotColdTelemetryEngine)
    participant SSE as Dashboard Web (Cliente SSE)
    participant DB as PostgreSQL (Cold Path)

    ESP->>HW: Amostragem física + Multisampling ADC1 (a cada 2.5s)
    HW-->>ESP: Sinais elétricos convertidos em grandezas
    ESP->>API: HTTP POST /api/v1/telemetry (JSON + X-API-Key)
    activate API

    API->>API: Valida X-API-Key e Schema Pydantic v2
    API->>API: Atualiza estado em RAM, extremos diários e buffer da janela
    
    par HOT PATH (Tempo Real < 15ms | Zero Disk I/O)
        API-->>SSE: Broadcast imediato via asyncio.Queue (SSE data frame)
        SSE->>SSE: Atualiza Hero 22°, Condições e flashes de oscilação
    and COLD PATH (Avaliação de Janela 5m ou Deadband)
        alt Anomalia Deadband detectada (Chuva, ΔP >= 2hPa, ΔGás >= 50ppm)
            API->>DB: INSERT INTO tb_telemetry_events (Alerta Imediato)
            API->>DB: INSERT INTO tb_telemetry_aggregated_5m (Snapshot Consolidado)
        else Janela de 5 minutos (300s) atingida ou 1º Boot
            API->>DB: INSERT INTO tb_telemetry_aggregated_5m (Média, Mín, Máx)
        else Condição Estável dentro da janela
            Note over API,DB: Nenhuma escrita em disco! Mantido apenas em RAM (Economia de 99,17% I/O)
        end
    end

    API-->>ESP: HTTP 201 Created (hot_path_streamed: true, cold_path_persisted: bool)
    deactivate API
```

---

## 2. Inicialização do Dashboard e Transição entre Dobras (iOS Weather UI)

```mermaid
sequenceDiagram
    autonumber
    participant User as Usuário
    participant Web as Frontend SPA (iOS Weather)
    participant API as FastAPI Backend
    participant DB as PostgreSQL

    User->>Web: Abre o aplicativo EcoPulse
    Web->>API: GET /api/v1/telemetry/history & /events
    API->>DB: SELECT janelas consolidadas (5m) e alertas recentes
    DB-->>API: Séries temporais com extremos (temp_min, temp_max) e eventos
    API-->>Web: JSON Histórico + Eventos
    Web->>Web: Renderiza 1ª Dobra (Hero, Alertas, Condições e Peek das Barras Laranjas)

    Web->>API: Abre conexão persistente GET /api/v1/telemetry/stream (SSE)
    API-->>Web: Frame inicial direto da RAM + Stream contínuo (< 15ms)

    User->>Web: Rola a tela para baixo (2ª Dobra)
    Web->>User: Revela Bento Grid dos 5 Sensores, Gráfico Chart.js e Mapa de Cobertura
```
