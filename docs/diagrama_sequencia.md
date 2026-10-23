# Diagramas de Sequência do Sistema EcoPulse

Os diagramas de sequência abaixo representam o ciclo de vida temporal dos dados no sistema, detalhando a troca de mensagens síncronas e assíncronas entre os nós da arquitetura.

---

## 1. Ciclo Periódico de Aquisição e Telemetria (ESP32 → Backend)

```mermaid
sequenceDiagram
    autonumber
    participant HW as Sensores (DHT, BMP, LDR, MQ, Chuva)
    participant ESP as ESP32 (Firmware C++)
    participant NTP as Servidor NTP (pool.ntp.org)
    participant API as API Backend (FastAPI)
    participant DB as Banco de Dados (PostgreSQL)

    Note over ESP: Temporizador millis() atinge intervalo (ex: 30s)
    
    ESP->>HW: 1. Coleta grandezas físicas (GPIOs e Barramento I2C)
    HW-->>ESP: Retorna leituras elétricas (tensões, pulsos, dados digitais)
    
    Note over ESP: Aplica fórmulas dos divisores de tensão e valida NaN
    
    opt Primeira execução ou re-sincronização
        ESP->>NTP: Requisita horário Epoch Unix
        NTP-->>ESP: Retorna timestamp UTC preciso
    end
    
    ESP->>ESP: Serializa payload JSON estruturado
    
    ESP->>API: HTTP POST /api/v1/telemetry (Header: X-API-Key + Payload JSON)
    activate API
    
    API->>API: Valida cabeçalho de autenticação X-API-Key
    
    alt Autenticação Válida & Schema Correto
        API->>API: Executa cálculos derivados (Sensação Térmica, Orvalho, AQI)
        API->>DB: INSERT INTO tb_telemetry_records (telemetria e leituras brutas)
        DB-->>API: Confirmação de persistência (OK)
        API-->>ESP: HTTP 201 Created ({"status": "recorded", "id": 1234})
    else Chave Inválida
        API-->>ESP: HTTP 401 Unauthorized
    else Payload Malformado
        API-->>ESP: HTTP 422 Unprocessable Entity
    end
    
    deactivate API
    
    Note over ESP: ESP32 entra em modo de espera não-bloqueante até o próximo ciclo
```

---

## 2. Ciclo de Consulta e Atualização em Tempo Real (Dashboard Web)

```mermaid
sequenceDiagram
    autonumber
    participant User as Usuário / Operador
    participant Web as Dashboard Frontend
    participant API as API Backend (FastAPI)
    participant DB as Banco de Dados (PostgreSQL)

    User->>Web: Acessa URL da Estação Meteorológica
    Web->>API: GET /api/v1/telemetry/latest
    activate API
    API->>DB: SELECT * FROM tb_telemetry_records ORDER BY timestamp DESC LIMIT 1
    DB-->>API: Registro meteorológico mais recente
    API-->>Web: HTTP 200 OK (JSON com última leitura e métricas)
    deactivate API
    
    Web->>Web: Atualiza velocímetros e cards visuais (Temperatura, Umidade, etc.)

    Web->>API: GET /api/v1/telemetry/history?range=24h
    activate API
    API->>DB: SELECT agregado por hora das últimas 24 horas
    DB-->>API: Série temporal histórica
    API-->>Web: HTTP 200 OK (Array de leituras históricas)
    deactivate API
    
    Web->>Web: Renderiza gráficos de linha interativos (Canvas / SVG)
    
    opt Detecção de Condição Crítica (ex: Início de Chuva ou Alta Poluição)
        Web->>User: Exibe banner visual de alerta meteorológico em destaque
    end
```

---

## 3. Fluxo de Resiliência e Tolerância a Falhas de Rede

```mermaid
sequenceDiagram
    autonumber
    participant ESP as ESP32 (Firmware)
    participant WiFi as Roteador Wi-Fi
    participant API as Servidor Backend

    ESP->>API: HTTP POST /api/v1/telemetry
    Note over ESP,API: Queda de sinal ou roteador indisponível (Timeout / Error -1)
    ESP-->>ESP: Detecta status de conexão WiFi != WL_CONNECTED
    
    Note over ESP: Não bloqueia a execução do microcontrolador
    ESP->>WiFi: Dispara rotina de reconexão automática em segundo plano
    
    loop A cada tentativa com backoff exponencial
        ESP->>WiFi: WiFi.reconnect()
    end
    
    WiFi-->>ESP: Conexão reestabelecida (IP atribuído via DHCP)
    ESP->>API: Retoma envio normal da telemetria
```
