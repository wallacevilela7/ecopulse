# Firmware Embarcado ESP32 — Estação Meteorológica EcoPulse (v3.0)

Firmware em C++ para o microcontrolador **ESP32 DevKit V1**, responsável pela aquisição simultânea dos **5 sensores físicos** (no barramento I2C e no conversor ADC1), filtragem digital por *multisampling*, servidor web/Telnet de diagnóstico local e transmissão reativa de telemetria HTTP para a nuvem AWS EC2.

---

## 1. Especificações Técnicas Implementadas

* **Ambiente de Compilação:** Arduino IDE 2.x / `arduino-cli` (`fqbn esp32:esp32:esp32`) ou PlatformIO.
* **Temporização Não-Bloqueante:** Controle de ciclo por `millis()` (`intervaloLeitura = 2000ms`), mantendo o WebServer local (porta `80`), o servidor Telnet (porta `23`) e a pilha TCP/IP responsivos.
* **Filtragem Analógica no ADC1 (`lerAdcMedio`):** Leitura prévia de descarte para estabilização do capacitor *Sample-and-Hold* do multiplexador interno do ESP32 seguida da média aritmética de **16 amostras** por canal com atenuação `ADC_11db` (`0V` a `3.3V`).
* **Reconexão Automática Wi-Fi e I2C:** Reconexão automática ao roteador `2.4 GHz` a cada `10s` em caso de queda de sinal e reinicialização automática do barramento I2C (`D21`/`D22`) caso o BMP280 sofra ruído elétrico.
* **Gatilho Reativo de Baixa Latência:** Envia telemetria HTTP a cada `2,5 segundos` em regime nominal ou **imediatamente** se detectar início/fim de chuva, variação de gases $\ge 40\text{ ppm}$ ou mudança de luminosidade no LDR $\ge 15\%$.

---

## 2. Mapa de Pinos e Calibração dos 5 Sensores

| Sensor | Pino ESP32 | Alimentação | Calibração / Equacionamento no Firmware |
| :--- | :---: | :---: | :--- |
| **DHT22 (Temp/Umidade)** | `GPIO 4` | `3.3V` | Leitura digital One-Wire com descarte de `isnan()`. |
| **BMP280 (Pressão/Alt)** | `GPIO 21 / 22` | `3.3V` | Barramento I2C (`0x76` / `0x77`) a `100 kHz`; altitude barométrica ($P_0 = 1013,25\text{ hPa}$). |
| **MQ-135 (Gases/Ar)** | `GPIO 32` (ADC1) | `5.0V` (MB102) | Reconstituição do divisor 1kΩ/2kΩ ($V_{\text{sensor}} = 1,5 \times V_{\text{pino}}$) e curva de potência $\text{PPM} = 116,602 \cdot (R_s/R_0)^{-2,769}$. |
| **LDR 5mm (Luz)** | `GPIO 35` (ADC1) | `3.3V` | Escala percentual inversa calibrada: $\text{Luz}(\%) = (1 - \text{ADC}/4095) \times 100$. |
| **Chuva (LM393 + MH-RD)** | `GPIO 34` (ADC1) | `3.3V` | Limiar calibrado de circuito aberto (`CHUVA_LIMIAR_SECO = 500`): $\text{ADC} \ge 500 \Rightarrow 0\%$ (seco). |

---

## 3. Compilação e Upload via Linha de Comando (`arduino-cli`)

1. Copie `include/config.h.example` para `include/config.h` e configure o SSID `2.4 GHz`, a senha e a URL da API (`http://54.235.41.91/api/v1/telemetry`).
2. Conecte a ESP32 ao computador via cabo USB (`/dev/ttyACM0` ou `/dev/ttyUSB0`) mantendo a fonte MB102 ligada na protoboard para alimentar a linha de `5.0V` do MQ-135.
3. Compile e grave o firmware:
```bash
mkdir -p /tmp/ecopulse_sketch
cp src/main.cpp /tmp/ecopulse_sketch/ecopulse_sketch.ino
cp include/config.h /tmp/ecopulse_sketch/config.h
arduino-cli compile --fqbn esp32:esp32:esp32 /tmp/ecopulse_sketch
arduino-cli upload -p /dev/ttyACM0 --fqbn esp32:esp32:esp32 /tmp/ecopulse_sketch
```
