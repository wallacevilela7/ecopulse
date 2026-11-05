# Modelo de Dados e Persistência (Cold Path PostgreSQL)

Este documento especifica a modelagem relacional do **EcoPulse** sob a arquitetura **Hot/Cold Path**, desenhada para evitar a saturação de escrita em disco (*Database as a Queue*) e alinhar o armazenamento histórico às diretrizes da **WMO-No. 8** e do **INMET**.

---

## 1. Diagrama Entidade-Relacionamento (ERD)

```mermaid
erDiagram
    TELEMETRY_AGGREGATED_5M {
        int id PK "Chave primária auto-incremento"
        string device_id "Identificador da estação (ex: esp32-meteo-01)"
        datetime window_start "Início UTC da janela de amostragem"
        datetime window_end "Fechamento UTC da janela (Indexado)"
        int samples_count "Quantidade de leituras integradas no bloco"
        
        float temp_avg "Temperatura média do período (°C)"
        float temp_min "Temperatura mínima registrada na janela (°C)"
        float temp_max "Temperatura máxima registrada na janela (°C)"
        
        float humidity_avg "Umidade relativa média (%)"
        float humidity_min "Umidade relativa mínima (%)"
        float humidity_max "Umidade relativa máxima (%)"
        
        float pressure_avg "Pressão barométrica média (hPa)"
        float pressure_min "Pressão barométrica mínima (hPa)"
        float pressure_max "Pressão barométrica máxima (hPa)"
        
        float altitude_avg "Altitude barométrica estimada (m)"
        float air_quality_avg "Concentração média de gases MQ-135 (PPM)"
        float air_quality_max "Pico máximo de gases na janela (PPM)"
        float luminosity_avg "Luminosidade média LDR (%)"
        float rain_intensity_avg "Intensidade média de precipitação (%)"
        boolean is_raining_period "Indica ocorrência de chuva durante a janela"
        
        int uptime_seconds "Tempo de atividade do ESP32 (s)"
        int wifi_rssi_dbm "Potência do sinal Wi-Fi (dBm)"
        int free_heap_bytes "Memória SRAM livre no fechamento (bytes)"
    }

    TELEMETRY_EVENTS {
        int id PK "Chave primária do evento"
        string device_id "Identificador da estação emissora"
        datetime recorded_at "Timestamp UTC exato da anomalia (Indexado)"
        string event_type "RAIN_STARTED | RAIN_STOPPED | PRESSURE_DROP_ALERT | GAS_SPIKE_ALERT"
        string severity "INFO | WARNING | CRITICAL"
        string title "Título resumido para o banner de alerta iOS"
        string description "Descrição detalhada da variação detectada pelo Deadband"
        string snapshot_json "Snapshot JSON das grandezas no instante do evento"
    }
```

---

## 2. Estratégia de Persistência e Indexação

1. **Consolidação Estatística (`tb_telemetry_aggregated_5m`):**
   * Enquanto o *Hot Path* distribui leituras em memória RAM a cada 2,5 segundos via SSE para o Dashboard, o *Cold Path* acumula as amostras e persiste **1 registro consolidado a cada 5 minutos** (contendo média, mínima e máxima), reduzindo o I/O de disco em **99,17%**.
2. **Gravação por Exceção / Deadband (`tb_telemetry_events`):**
   * Mudanças abruptas (início de chuva, queda barométrica $\ge 2.0\text{ hPa}$, salto de gases $\ge 50\text{ PPM}$ ou variação térmica $\ge 1.5^\circ\text{C}$) disparam gravação imediata na tabela de eventos e forçam o fechamento antecipado da janela estatística, garantindo zero perda de informação crítica.
3. **Índices Compostos B-Tree:**
   * `idx_agg5m_device_window (device_id, window_end)` e `idx_events_device_time (device_id, recorded_at)` garantem consultas históricas e de alertas em $O(\log N)$.
