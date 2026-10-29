# Memorial Técnico e Relatório de Engenharia: Integração de Sensores, Diagnóstico de Bancada e Arquitetura de Telemetria IoT

**Projeto Integrado Multidisciplinar II (PIM II)**  
**Curso:** Ciência da Computação — Universidade Paulista (UNIP)  
**Projeto:** EcoPulse — Estação Meteorológica e Monitoramento Ambiental Inteligente  
**Módulo:** Firmware Embarcado, Testes de Bancada e Camada de Ingestão HTTP/REST  
**Data de Consolidação:** Outubro de 2026  

---

## 1. Introdução e Contextualização do Sistema

O **EcoPulse** é um sistema computacional ciber-físico (Internet das Coisas - IoT) concebido para a coleta contínua, processamento, transmissão e exibição de variáveis micrometeorológicas e indicadores de qualidade ambiental em tempo real.

O projeto é estruturado em três macro-camadas interdependentes:
1. **Camada Física e Embarcada (Edge Computing):** Microcontrolador ESP32-WROOM-32 com cluster de 5 sensores de diferentes naturezas elétricas e físicas.
2. **Camada de Transporte e Ingestão (Middleware / Backend):** Barramento de comunicação TCP/IP sobre Wi-Fi (802.11 b/g/n), serialização em JSON, protocolo HTTP/1.1 RESTful e serviço de ingestão assíncrono em Python com FastAPI.
3. **Camada de Aplicação e Persistência:** Banco de dados relacional time-series e interface web responsiva em tempo real.

Este documento formaliza as decisões de projeto de engenharia de hardware e firmware, o histórico de resolução de problemas e testes empíricos de bancada, bem como a especificação formal do tráfego de telemetria entre o dispositivo microcontrolado e o servidor.

---

## 2. Topologia do Hardware e Cluster de Sensores

Para garantir integridade de sinal, isolamento de ruído e compatibilidade com o subsistema de rádio Wi-Fi do ESP32, as portas de Entrada e Saída (GPIO) foram distribuídas respeitando a arquitetura interna do chip (Silicon Labs / Espressif ESP32-D0WDQ6):

```
                                  +-------------------+
                                  |   ESP32 DevKit    |
                                  |                   |
[DHT22]  ────── Digital (GPIO 4) ─┤ D4                |
                                  |                   |
[BMP280] ────── I2C SDA (GPIO 21) ┤ D21               |
         ────── I2C SCL (GPIO 22) ┤ D22               |
                                  |                   |
[MQ-135] ── Divisor 1k/2k ───────┤ D32 (ADC1_CH4)    |
[LDR]    ────── Sinal Analógico ──┤ D35 (ADC1_CH7)    |
[Chuva]  ────── Sinal Analógico ──┤ D34 (ADC1_CH6)    |
                                  +---------┬---------+
                                            │ Wi-Fi 802.11 b/g/n
                                            ▼
                                  +-------------------+
                                  |   Backend FastAPI |
                                  |  HTTP POST :8000  |
                                  +-------------------+
```

### 2.1. Detalhamento dos Sensores Integrados

| Sensor | Grandeza Medida | Interface Física | Alimentação | Pino ESP32 | Tratamento de Sinal |
| :--- | :--- | :---: | :---: | :---: | :--- |
| **DHT22 (AM2302)** | Temperatura (°C) e Umidade Relativa (%) | Digital One-Wire proprietário | 3.3V | GPIO 4 | Protocolo temporizado com validação de checksum e rejeição de leituras `NaN`. |
| **BMP280** | Pressão Barométrica (hPa) e Altitude Estimada (m) | Barramento I2C síncrono (100 kHz) | 3.3V | D21 (SDA) / D22 (SCL) | Endereço `0x76` (SDO ao GND); rotina de auto-recuperação do barramento em caso de perda de ACK. |
| **MQ-135** | Qualidade do Ar, CO₂ e Gases Redutores (PPM) | Analógica (0 a 5V escalonada) | 5.0V (Aquecedor) | GPIO 32 (ADC1) | Divisor de tensão resistivo $1\text{ k}\Omega / 2\text{ k}\Omega$ (fator atenuador inverso $1.5\times$); curva analítica $PPM = A \cdot (R_s/R_0)^B$; rotina de pré-aquecimento de 180s. |
| **LDR 5mm** | Intensidade Luminosa Ambiente (%) | Analógica (0 a 3.3V) | 3.3V | GPIO 35 (ADC1) | Multisampling de 16 amostras com atenuação de 11 dB; mapeamento percentual calibrado para detecção de limiares dia/penumbra/noite. |
| **Sensor de Chuva (LM393 + MH-RD)** | Detecção e Intensidade Pluviométrica (%) | Analógica (0 a 3.3V) | 3.3V | GPIO 34 (ADC1) | Placa coletora condutiva com divisor pull-up; lógica inversa (ADC 4095 = seco; ADC decrescente com precipitação). |

> **Nota Crítica de Engenharia (Restrição do ADC2):**  
> Os canais analógicos pertencentes ao bloco **ADC2** do ESP32 compartilham circuitos de amostragem com o sintetizador de radiofrequência do Wi-Fi. Quando o rádio Wi-Fi está ligado, qualquer chamada a pinos do ADC2 é bloqueada pelo driver do FreeRTOS ou retorna valores espúrios. Por essa razão, todos os sensores analógicos do projeto (**MQ-135, LDR e Chuva**) foram rigorosamente alocados no bloco **ADC1** (GPIOs 32, 34 e 35).

---

## 3. Estudo de Caso de Engenharia: Diagnóstico e Resolução de Falha de Bancada

Um dos pontos de maior relevância metodológica para apresentação acadêmica e documentação do PIM II foi o processo formal de isolamento de defeito ocorrido durante a integração do sensor de chuva.

### 3.1. Sintoma do Problema
O sensor pluviométrico apresentava leitura permanentemente saturada em **ADC: 4095 ($3.14\text{ V}$)**, correspondente a 0% de umidade (seco), mesmo após imersão completa da placa condutiva em recipiente com água.

### 3.2. Hipóteses Iniciais Formuladas
1. **Hipótese A:** Defeito de silício ou queima da porta conversora analógico-digital (GPIO 35) do microcontrolador.
2. **Hipótese B:** Erro lógico no firmware de cálculo de tensão ou amostragem do ADC.
3. **Hipótese C:** Inversão de serigrafia nos 4 pinos do módulo comparador LM393 (VCC ligado direto na entrada analógica do ESP32).
4. **Hipótese D:** Descontinuidade mecânica ou elétrica no caminho físico de condução (jumpers ou placa coletora).

### 3.3. Testes Experimentais e Resultados de Bancada

```
+------------------------------------------------------------------------------------+
|                      FLUXOGRAMA DE ELIMINAÇÃO CIENTÍFICA                           |
|                                                                                    |
| [1. Inversão Física D34 <-> D35]                                                  |
|      ├── D35 (recebendo LDR): Leu 823 ADC (0.81V)  --> Descarta Hipótese A (Pino OK)|
|      └── D34 (recebendo Chuva): Leu 4095 ADC       --> O defeito seguiu o sensor!   |
|                                                                                    |
| [2. Curto-Circuito direto nos 2 pinos do Módulo LM393]                             |
|      └── Saída do ESP32 caiu para ADC 0 (0.14V / 100% Água)                         |
|           --> Descarta Hipóteses B e C (Módulo LM393, Firmware e VCC/GND/AO OK)    |
|                                                                                    |
| [3. Teste de Continuidade com Cabos Jumpers em Curto]                             |
|      └── Saída manteve-se em ADC 0 (100%)          --> Jumpers íntegros            |
|                                                                                    |
| [4. Inspeção Mecânica nos Pinos da Placa Coletora MH-RD]                           |
|      └── Ao tensionar mecanicamente o terminal: sinal intermitente detectado        |
|           ===> CAUSA RAIZ: Solda fria / trinca mecânica nos pinos da placa coletora |
+------------------------------------------------------------------------------------+
```

* **Conclusão Técnica:** A metodologia de testes cruzados e isolamento por etapas demonstrou que tanto o microcontrolador quanto o código C++ e o módulo amplificador operacional LM393 operavam com 100% de conformidade. A falha residia exclusivamente em um defeito de fabricação do terminal do transdutor passivo, demonstrando a importância de validação de continuidade prévia em projetos de instrumentação.

---

## 4. Engenharia de Firmware (ESP32 / C++)

O código-fonte do firmware foi implementado no ecossistema Arduino/ESP32 com as seguintes características de robustez operacional:

1. **Arquitetura Não-Bloqueante:** O laço principal (`loop()`) é inteiramente temporizado via `millis()`, eliminando o uso de chamadas bloqueantes `delay()`. Isso garante que a pilha de rede Wi-Fi, o servidor HTTP e o serviço Telnet mantenham taxa de resposta inferior a 5 ms.
2. **Filtragem de Ruído por Superamostragem (Multisampling):** Para contornar a não-linearidade característica do ADC de 12 bits do ESP32 em extremos de tensão e atenuar transientes eletromagnéticos de alta frequência, foi criada a rotina `lerAdcMedio(pino, amostras)` com média móvel aritmética de 16 amostras e atraso intercalado de $50\,\mu\text{s}$.
3. **Calibração Interna por Efuse (`analogReadMilliVolts`):** O cálculo de tensão real é derivado das curvas de calibração gravadas de fábrica na ROM do chip ESP32, garantindo precisão superior ao cálculo puramente linear.
4. **Triplo Canal de Telemetria Local:** As leituras dos sensores são transmitidas simultaneamente para:
   * **Porta Serial USB** (115200 bps);
   * **Terminal de Rede Telnet / Netcat** (porta TCP 23);
   * **Servidor Web Embutido** (porta HTTP 80 com buffer circular em memória e atualização assíncrona).

---

## 5. Arquitetura de Comunicação: Transporte e Ingestão (ESP32 $\rightarrow$ Backend)

Para conectar o mundo físico ao sistema de banco de dados e à interface visual, foi estabelecido um contrato de API RESTful que opera sobre a pilha TCP/IP da rede local.

### 5.1. Protocolo e Transporte
* **Método HTTP:** `POST`
* **Caminho (Endpoint):** `/api/v1/telemetry`
* **Biblioteca Embarcada:** `HTTPClient.h` (nativa do core ESP32)
* **Periodicidade de Envio:** A cada 10 segundos (ajustável).

### 5.2. Segurança e Autenticação
O ESP32 injeta no cabeçalho HTTP da requisição um token pré-compartilhado:
```http
POST /api/v1/telemetry HTTP/1.1
Host: 192.168.18.121:8000
Content-Type: application/json
X-API-Key: chave-secreta-estacao-unip-2026
```
O backend valida este cabeçalho antes de qualquer deserialização. Requisições sem chave ou com credencial incorreta são descartadas imediatamente com status `HTTP 401 Unauthorized`.

### 5.3. Estrutura do Payload JSON
O payload encapsula tanto os dados úteis dos sensores quanto metadados diagnósticos da estação:

```json
{
  "device_id": "esp32-meteo-01",
  "sensors": {
    "temperature_c": 23.3,
    "humidity_pct": 77.1,
    "pressure_hpa": 925.6,
    "altitude_m": 756.8,
    "air_quality_ppm": 15.0,
    "luminosity_pct": 35.8,
    "rain_intensity_pct": 0.0,
    "is_raining": false
  },
  "diagnostics": {
    "uptime_seconds": 120,
    "wifi_rssi_dbm": -55
  }
}
```

### 5.4. Camada de Ingestão do Backend (FastAPI / Pydantic)
No lado do servidor, o microframework **FastAPI** foi adotado por oferecer:
* **Validação de Schema em Tempo de Execução:** Classes baseadas em `Pydantic` rejeitam automaticamente dados corrompidos ou tipos incompatíveis com código `HTTP 422 Unprocessable Entity`.
* **Desempenho Assíncrono (`async/await`):** Suporte nativo a alta concorrência por meio do servidor ASGI **Uvicorn**, essencial para permitir a ingestão simultânea de múltiplos nós sensores.
* **Documentação Automática:** Geração instantânea de especificações interativas OpenAPI/Swagger em `/docs`.

---

## 6. Próximas Etapas no Ciclo de Vida do Projeto

Concluída a homologação do firmware e da ingestão HTTP, as etapas subsequentes do projeto acadêmico compreendem:
1. **Camada de Persistência:** Implementação de modelo de entidades ORM (SQLAlchemy) e repositório com banco de dados time-series/relacional (PostgreSQL).
2. **Processamento Derivado:** Cálculo de índices meteorológicos pelo backend (Sensação Térmica / Heat Index, Ponto de Orvalho / Dew Point e Índice de Qualidade do Ar / AQI).
3. **Frontend Dashboard:** Construção de painel web com gráficos temporais históricos, cards de valores instantâneos e alarmes meteorológicos automáticos.

---
*Relatório técnico consolidado para fins de documentação formal do PIM II — Universidade Paulista (UNIP).*
