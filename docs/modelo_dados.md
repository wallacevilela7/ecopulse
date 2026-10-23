# Modelo de Dados e Persistência

Este documento define a modelagem do banco de dados do sistema **EcoPulse**, projetada para oferecer alta vazão de escrita para séries temporais de sensores IoT e consultas analíticas velozes para o dashboard.

---

## 1. Diagrama Entidade-Relacionamento (ERD)

```mermaid
erDiagram
    STATION ||--o{ TELEMETRY_RECORD : "transmite"
    STATION ||--o{ ALERT_EVENT : "gera"
    TELEMETRY_RECORD ||--o{ ALERT_EVENT : "origina"

    STATION {
        string device_id PK "Identificador único da estação (ex: esp32-meteo-01)"
        string name "Nome descritivo amigável"
        float latitude "Latitude geográfica em graus decimais"
        float longitude "Longitude geográfica em graus decimais"
        float altitude_meters "Altitude em relação ao nível do mar"
        string firmware_version "Versão do firmware compilado"
        boolean is_active "Status operacional da estação"
        datetime registered_at "Data e hora de cadastramento"
    }

    TELEMETRY_RECORD {
        uuid id PK "Identificador único do registro (UUID v4)"
        string device_id FK "Chave estrangeira referenciando STATION"
        bigint epoch_timestamp "Epoch Unix timestamp em segundos enviado pelo ESP32"
        datetime recorded_at "Data e hora no fuso horário UTC"
        datetime received_at "Data e hora exata de chegada no servidor"
        
        float temp_dht_c "Temperatura aferida pelo DHT22"
        float humidity_pct "Umidade relativa do ar (0-100%)"
        string dht_status "Status operacional do DHT22 (OK, READ_ERROR)"
        
        float temp_bmp_c "Temperatura aferida pelo BMP280"
        float pressure_hpa "Pressão barométrica absoluta"
        float altitude_est_m "Altitude barométrica estimada"
        string bmp_status "Status operacional do BMP280 (OK, I2C_ERROR)"
        
        int ldr_raw "Leitura bruta analógica (0 a 4095)"
        float ldr_voltage_v "Tensão medida no pino ADC (0 a 3.3V)"
        float luminosity_pct "Porcentagem de luminosidade ambiente"
        
        int mq135_raw "Leitura bruta analógica com divisor (0 a 4095)"
        float mq135_sensor_voltage "Tensão real de saída do sensor (0 a 5.0V)"
        float air_quality_ppm "Estimativa de concentração de gases em PPM"
        boolean mq135_warmed_up "Flag indicando aquecimento prévio concluído"
        
        int rain_raw "Leitura bruta analógica da placa de chuva (0 a 4095)"
        float rain_intensity_pct "Porcentagem de presença de água na placa"
        boolean is_raining "Indicador booleano de detecção de chuva"
        
        float heat_index_c "Sensação térmica calculada no servidor"
        float dew_point_c "Ponto de orvalho calculado no servidor"
        string air_quality_class "Classificação categórica da qualidade do ar"
    }

    ALERT_EVENT {
        uuid id PK "Identificador do evento de alerta"
        string device_id FK "Estação emissora"
        uuid telemetry_id FK "Registro que causou o disparo do alerta"
        string alert_type "Tipo (HEAVY_RAIN, PRESSURE_DROP, POOR_AIR_QUALITY)"
        string severity "Gravidade (INFO, WARNING, CRITICAL)"
        string message "Mensagem detalhada do evento"
        boolean acknowledged "Se o alerta foi visto pelo operador"
        datetime created_at "Horário de disparo do alerta"
    }
```

---

## 2. Estratégia de Indexação e Desempenho

Para assegurar respostas na casa dos milissegundos mesmo com milhões de registros acumulados:
1. **Índice Composto (`device_id`, `recorded_at` DESC):**
   * Essencial para atender a consulta de leitura mais recente (`/telemetry/latest`) com custo $O(1)$.
   * Agiliza a busca de intervalos históricos específicos (`BETWEEN :start AND :end`).
2. **Índice B-Tree em `created_at` na tabela de alertas:**
   * Permite filtrar alertas não resolvidos recentes no topo da barra de notificações do frontend.
3. **Desnormalização Controlada (Flattened Table):**
   * Todas as métricas de um ciclo de leitura são mantidas na mesma linha da tabela `tb_telemetry_records`.
   * Essa escolha evita a necessidade de múltiplos `JOINs` para renderizar uma única tela ou gráfico, reduzindo consumo de memória do banco de dados relacional.
