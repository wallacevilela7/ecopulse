# Firmware Embarcado ESP32 - Planejamento e Especificação

Este diretório conterá o firmware em C++ para o microcontrolador **ESP32 NodeMCU**, responsável pela aquisição de sinais dos sensores físicos, empacotamento em JSON e despacho seguro para a API REST via Wi-Fi.

---

## 1. Diretrizes Técnicas do Firmware

* **Ambiente de Desenvolvimento Recomendado:** PlatformIO (VS Code / CLI) ou Arduino IDE 2.x.
* **Framework:** Arduino Core para ESP32 (versão estável 2.x / 3.x).
* **Padrão de Execução:** Temporizador não-bloqueante baseado em `millis()`, evitando chamadas a `delay()` para manter o microcontrolador responsivo.
* **Bibliotecas Planejadas:**
  * `DHT sensor library` (Adafruit) + `Adafruit Unified Sensor` (leitura do DHT22)
  * `Adafruit BMP280 Library` (leitura digital via I2C)
  * `ArduinoJson` (v7.x - serialização eficiente e com alocação estática no heap)
  * `WiFi.h`, `HTTPClient.h` e `time.h` (nativas do ESP32 para conectividade e NTP)

---

## 2. Estrutura de Diretórios Planejada

```
firmware/
├── include/
│   └── config.h.example     # Modelo de credenciais Wi-Fi, URL da API e chave de autenticação
├── src/
│   └── main.cpp             # Ponto de entrada do firmware (setup e loop não-bloqueante)
├── platformio.ini.example   # Configuração do ambiente de compilação PlatformIO
└── README.md                # Este documento
```

---

## 3. Arquitetura Modular em C++

Conforme modelado no [**Diagrama de Classes UML**](file:///home/wvs/Documents/ccomp-unip/2sem/pim2/ecopulse/docs/diagrama_classes.md), o firmware será dividido em três responsabilidades:

1. **`SensorReader` (Hardware Abstraction Layer - HAL):** Encapsula as leituras analógicas (`analogRead`), aplica o fator de correção do divisor de tensão ($\times 1.5$) do MQ-135 e valida eventuais erros físicos (`isnan()`).
2. **`TelemetryHttpClient` (Camada de Rede):** Estabelece a conexão Wi-Fi, sincroniza a hora mundial via servidor NTP (`pool.ntp.org`), monta o payload JSON com `ArduinoJson` e dispara o `HTTP POST` com cabeçalho `X-API-Key`.
3. **`WeatherStationNode` (Orquestrador):** Gerencia o ciclo de amostragem (padrão: 30 segundos) e o tempo de pré-aquecimento do sensor de gases MQ-135 (3 minutos).

---

## 4. Próximos Passos (Construção Conjunta Passo a Passo)

1. [ ] Configuração do arquivo `platformio.ini` com pinos e parâmetros do microcontrolador.
2. [ ] Teste unitário e de bancada de cada sensor individualmente via Monitor Serial.
3. [ ] Implementação da classe `SensorReader` para unificar a leitura dos 5 sensores.
4. [ ] Implementação da rotina de transmissão Wi-Fi e sincronização de horário NTP.
