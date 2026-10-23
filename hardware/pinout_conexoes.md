# Tabela Completa de Pinout e Conexões

Esta tabela consolida todas as conexões físicas entre os periféricos sensores, fontes de alimentação e as portas de entrada/saída (GPIO) do microcontrolador ESP32.

---

## 1. Mapeamento Pino a Pino

| Sensor / Periférico | Pino no Módulo | Conectar em (ESP32 / Protoboard) | Tensão | Observações Elétricas e Funcionais |
| :--- | :--- | :--- | :---: | :--- |
| **Alimentação Geral** | Trilho MB102 A | Barramento Protoboard 1 | **3.3V** | Fornece 3.3V regulado para lógica do ESP32 e sensores. |
| | Trilho MB102 B | Barramento Protoboard 2 | **5.0V** | Fornece 5.0V regulado para o aquecedor do MQ-135. |
| | GND MB102 | Barramento Negativo Comum | **0V** | Referência comum obrigatória a todo o circuito. |
| **BMP280** | `VCC` | Trilho 3.3V | 3.3V | Não alimentar em 5V sob risco de queima do sensor Bosch. |
| *(Pressão / Altitude)* | `GND` | Trilho GND | 0V | Terra comum. |
| | `SCL` | **GPIO 22** | 3.3V | Linha de clock do barramento I2C padrão. |
| | `SDA` | **GPIO 21** | 3.3V | Linha de dados do barramento I2C padrão. |
| | `CSB` / `SDO` | Desconectados | — | Deixar desconectado fixa o endereço I2C em `0x76`. |
| **DHT22 (AM2302)** | `VCC` (Pino 1) | Trilho 3.3V | 3.3V | Alimentação positiva do transdutor capacitivo. |
| *(Temp / Umidade)* | `DATA` (Pino 2) | **GPIO 4** | 3.3V | Protocolo digital One-Wire. Exige pull-up de 10kΩ com VCC. |
| | `NC` (Pino 3) | Desconectado | — | Sem conexão (Not Connected). |
| | `GND` (Pino 4) | Trilho GND | 0V | Terra comum. |
| **LDR (Luz)** | Perna A | Trilho 3.3V | 3.3V | Terminal superior do fotoresistor. |
| *(Luminosidade)* | Perna B | **GPIO 34** + Resistor 10kΩ | Variável | A outra perna do resistor 10k vai ao GND (Divisor de tensão). |
| **Sensor de Chuva** | `VCC` | Trilho 3.3V | 3.3V | Alimentar em 3.3V garante saída $0-3.3V$ segura para o ADC. |
| *(Montimport)* | `GND` | Trilho GND | 0V | Terra comum. |
| | `AO` | **GPIO 35** | Variável | Saída analógica: seca = ~4095; encharcada = ~0. |
| | `DO` | Desconectado | — | Saída digital tipo limiar (não utilizada). |
| **MQ-135** | `VCC` | Trilho **5.0V** (MB102) | 5.0V | O filamento de aquecimento exige 5V para liberar elétrons. |
| *(Qualidade do Ar)* | `GND` | Trilho GND | 0V | Terra comum. |
| | `AO` | Resistor **1 kΩ** | $0-5.0V$ | O sinal analógico passa pelo divisor resistivo (1kΩ / 2kΩ). |
| | Ponto Central | **GPIO 32** | $0-3.3V$ | Junção entre resistor de 1kΩ e 2kΩ. Seguro para o ESP32! |
| | `DO` | Desconectado | — | Saída digital comparadora (não utilizada). |

---

## 2. Restrições Importantes de Hardware do ESP32

1. **Uso Exclusivo do ADC1 para Sensores Analógicos:**
   * No ESP32, o conversor **ADC2** compartilha hardware com o driver interno de Wi-Fi. Quando o rádio Wi-Fi é ativado, leituras nos pinos do ADC2 tornam-se ruidosas ou retornam erros.
   * Por isso, **todos os sensores analógicos do EcoPulse (LDR no GPIO 34, Chuva no GPIO 35 e MQ-135 no GPIO 32) foram mapeados exclusivamente nos canais do ADC1**, garantindo leituras analógicas confiáveis mesmo durante a transmissão de dados na rede.
2. **Pinos Somente Entrada (Input Only):**
   * Os GPIOs 34, 35, 36 e 39 não possuem transistores internos de pull-up ou pull-down e não podem ser configurados como saída digital. São ideais para sensores analógicos como o LDR e o sensor de chuva.
