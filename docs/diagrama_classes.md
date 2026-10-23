# Diagrama de Classes UML (Firmware & Backend)

Este documento especifica a modelagem orientada a objetos do projeto **EcoPulse**, contemplando a camada de firmware embarcado (C++ no microcontrolador ESP32) e a arquitetura em camadas da API Backend (Python).

---

## 1. Diagrama de Classes Estrutural

```mermaid
classDiagram
    direction TB

    %% ==========================================
    %% CAMADA DE FIRMWARE (ESP32 - C++)
    %% ==========================================
    namespace Firmware_ESP32 {
        class WeatherStationNode {
            -String deviceId
            -unsigned long pollingIntervalMs
            -unsigned long bootTimeMs
            +setup() void
            +loop() void
            +collectAllSensors() TelemetryPayload
        }

        class SensorReader {
            -DHT dht
            -Adafruit_BMP280 bmp
            -bool bmpInitialized
            +begin() void
            +readDHT22(int pin) DHTData
            +readBMP280(uint8_t addr) BMPData
            +readLDR(int pin) LDRData
            +readMQ135(int pin, bool warmedUp) MQ135Data
            +readRain(int pin) RainData
        }

        class TelemetryHttpClient {
            -String apiUrl
            -String apiKey
            +connectWiFi(String ssid, String pass) bool
            +syncNTPTime() long
            +sendTelemetry(String jsonPayload) int
        }

        class DHTData {
            +float temperatureC
            +float humidityPct
            +String status
        }

        class BMPData {
            +float temperatureC
            +float pressureHpa
            +float altitudeM
            +String status
        }

        class LDRData {
            +int rawAdc
            +float luminosityPct
        }

        class MQ135Data {
            +int rawAdc
            +float voltageV
            +float airQualityPpm
            +bool isWarmedUp
        }

        class RainData {
            +int rawAdc
            +float intensityPct
            +bool isRaining
        }
    }

    %% ==========================================
    %% CAMADA DA API BACKEND (Python)
    %% ==========================================
    namespace Backend_API {
        class TelemetryController {
            -TelemetryService service
            +receiveTelemetry(apiKey: str, dto: TelemetryRequestDTO) Response
            +getLatestReading(deviceId: str) TelemetryResponseDTO
            +getHistoricalData(deviceId: str, fromTime: datetime, toTime: datetime) List
            +getDashboardSummary(deviceId: str) DashboardSummaryDTO
        }

        class ApiKeyAuthFilter {
            -String validApiKey
            +validateHeader(requestKey: str) bool
        }

        class TelemetryService {
            -TelemetryRepository repository
            +processAndSave(dto: TelemetryRequestDTO) TelemetryRecord
            +fetchLatest(deviceId: str) TelemetryResponseDTO
            +fetchHistory(deviceId: str, fromTime: datetime, toTime: datetime) List
            +calculateAverages(deviceId: str, hours: int) DashboardSummaryDTO
            +evaluateAlerts(record: TelemetryRecord) List
        }

        class TelemetryRepository {
            -DatabaseSession session
            +save(record: TelemetryRecord) bool
            +findLatestByDevice(deviceId: str) TelemetryRecord
            +findByTimeRange(deviceId: str, start: datetime, end: datetime) List
        }

        class TelemetryRecord {
            +UUID id
            +String deviceId
            +datetime recordedAt
            +datetime receivedAt
            +DHT22Reading dht22
            +BMP280Reading bmp280
            +LDRReading ldr
            +MQ135Reading mq135
            +RainReading rain
        }

        class DHT22Reading {
            +Float temperatureC
            +Float humidityPct
            +SensorStatus status
        }

        class BMP280Reading {
            +Float temperatureC
            +Float pressureHpa
            +Float altitudeM
            +SensorStatus status
        }

        class LDRReading {
            +Integer rawAdc
            +Float voltageV
            +Float luminosityPct
        }

        class MQ135Reading {
            +Integer rawAdc
            +Float pinVoltageV
            +Float sensorVoltageV
            +Float estimatedPpm
            +Boolean isWarmedUp
        }

        class RainReading {
            +Integer rawAdc
            +Float intensityPct
            +Boolean isRaining
        }

        class DashboardSummaryDTO {
            +Float avgTemperature24h
            +Float maxHumidity24h
            +Float minPressure24h
            +Boolean rainAlertActive
            +String airQualityClassification
        }
    }

    %% Relacionamentos Firmware
    WeatherStationNode *-- SensorReader : utiliza
    WeatherStationNode *-- TelemetryHttpClient : transmite via
    SensorReader ..> DHTData : produz
    SensorReader ..> BMPData : produz
    SensorReader ..> LDRData : produz
    SensorReader ..> MQ135Data : produz
    SensorReader ..> RainData : produz

    %% Relacionamento Firmware -> Backend
    TelemetryHttpClient ..> ApiKeyAuthFilter : HTTP POST JSON
    ApiKeyAuthFilter ..> TelemetryController : autoriza requisição

    %% Relacionamentos Internos do Backend
    TelemetryController --> TelemetryService : delega regras
    TelemetryService --> TelemetryRepository : persiste e consulta
    TelemetryService ..> DashboardSummaryDTO : gera agregados
    TelemetryRepository --> TelemetryRecord : gerencia entidade

    %% Composição do Domínio Backend
    TelemetryRecord *-- "1" DHT22Reading : contem
    TelemetryRecord *-- "1" BMP280Reading : contem
    TelemetryRecord *-- "1" LDRReading : contem
    TelemetryRecord *-- "1" MQ135Reading : contem
    TelemetryRecord *-- "1" RainReading : contem
```

---

## 2. Princípios de Design e Responsabilidades

### A. Camada de Firmware (ESP32)
* **`WeatherStationNode` (Orquestrador de Ciclo de Vida):** Controla o tempo de execução não-bloqueante via temporizador com `millis()`, evitando o uso de `delay()` para manter o microcontrolador responsivo a eventos de rede.
* **`SensorReader` (Hardware Abstraction Layer - HAL):** Isola os detalhes de baixo nível dos sensores (endereços I2C, leitura analógica `analogRead()`, canais ADC1). Aplica calibrações de divisores resistivos e normalização de grandezas.
* **`TelemetryHttpClient` (Cliente de Conectividade):** Responsável por estabelecer a conexão Wi-Fi com algoritmo de reconexão exponencial, sincronizar a hora via NTP e disparar requisições POST com tratamento de timeout.

### B. Camada de Backend (API Python)
* **`ApiKeyAuthFilter`:** Middleware de segurança que valida tokens em tempo constante no cabeçalho `X-API-Key`.
* **`TelemetryController`:** Ponto de entrada REST, realiza desserialização e validação de schema via Pydantic.
* **`TelemetryService`:** Contém o núcleo da lógica de negócios: detecção de anomalias, cálculo de médias móveis, classificação de qualidade do ar e disparo de regras de alerta.
* **`TelemetryRepository`:** Isola a camada de persistência em banco de dados através do padrão *Repository Pattern*.
