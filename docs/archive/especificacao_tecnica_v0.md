# ESPECIFICAÇÃO TÉCNICA E ARQUITETURA DO SISTEMA
## Estação Meteorológica Inteligente para Monitoramento Ambiental Urbano (Smart Cities)

**Instituição:** Universidade Paulista – UNIP  
**Curso:** Bacharelado em Ciência da Computação (2º Semestre)  
**Disciplina:** Projeto e Desenvolvimento II (PD-II / PIM II)  
**Tema:** Cidades Inteligentes, IoT, Sustentabilidade e Transparência de Dados Ambientais  

---

## 1. Visão Geral e Arquitetura do Sistema

O projeto consiste em uma solução integrada de **Internet das Coisas (IoT)** e **Computação em Nuvem** projetada para coletar, processar, armazenar e disponibilizar dados climáticos e de qualidade ambiental em tempo real para os cidadãos e gestores urbanos.

### Diagrama de Fluxo de Dados Ponta a Ponta

```
+-----------------------------------------------------------------------------------+
| CAMADA 1: DISPOSITIVO EMBARCADO (HARDWARE & FIRMWARE)                            |
|                                                                                   |
|  [ DHT22 ]   (Temp & Umidade)     --\                                             |
|  [ BMP280 ]  (Pressão & Altimetria)  \   GPIO / I2C / ADC                         |
|  [ MQ-135 ]  (Qualidade do Ar/Gases) --> [ MICROCONTROLADOR ESP32 ]               |
|  [ LDR ]     (Luminosidade/Sol)      /   * Leitura não-bloqueante                 |
|  [ Sensor ]  (Chuva/Pluviometria) --/    * Validação lógica e filtragem de ruído  |
|                                          * Formatação de Payload JSON             |
|                                          * Transmissão Wi-Fi (HTTP POST / MQTT)   |
+---------------------------------------------------+-------------------------------+
                                                    |
                                    Wi-Fi / HTTPS (JSON Payload)
                                                    v
+-----------------------------------------------------------------------------------+
| CAMADA 2: BACKEND & COMPUTAÇÃO EM NUVEM (AWS)                                    |
|                                                                                   |
|  [ NUVEM AWS (Instância EC2 / Lightsail) ]                                        |
|  +-----------------------------------------------------------------------------+  |
|  |  Servidor Web Python: FastAPI + Uvicorn + Pydantic                           |  |
|  |  - Endpoint de Ingestão: POST /api/v1/telemetria                            |  |
|  |  - Endpoint de Consulta: GET /api/v1/telemetria/atual & /historico          |  |
|  |  - Endpoint de Alertas:  GET /api/v1/alertas                                |  |
|  |  - Módulo Matemático:    Cálculo de Heat Index, AQI e Geometria Analítica   |  |
|  +-----------------------------------------------------------------------------+  |
+---------------------------------------------------+-------------------------------+
                                                    |
                                       SQLAlchemy ORM (Conexão SSL)
                                                    v
+-----------------------------------------------------------------------------------+
| CAMADA 3: BANCO DE DADOS EM NUVEM                                                 |
|                                                                                   |
|  [ PostgreSQL Cloud (Supabase / Neon / AWS RDS) ]                                 |
|  - Tabela: estacoes (identificação, latitude, longitude, altitude)               |
|  - Tabela: leituras_sensores (timestamp, temp, umidade, pressao, ar, luz, chuva)  |
|  - Tabela: alertas_emitidos (evento, severidade, data_hora, status)               |
+---------------------------------------------------+-------------------------------+
                                                    |
                                         REST API / JSON (HTTPS)
                                                    v
+-----------------------------------------------------------------------------------+
| CAMADA 4: DASHBOARD WEB PÚBLICO (FRONTEND ONLINE)                                 |
|                                                                                   |
|  [ Hospedagem Online: Vercel / Netlify / GitHub Pages ]                           |
|  - HTML5 Semântico + CSS3 Moderno (Responsivo & Dark/Light Mode)                  |
|  - JavaScript ES6+ assíncrono (fetch API)                                         |
|  - Gráficos Dinâmicos: Chart.js (Séries temporais das últimas 24h)                |
|  - Mapa Interativo: Leaflet.js / OpenStreetMap com cálculo geoanalítico de raios  |
|  - Painel de Alertas de Defesa Civil e Indicadores Socioambientais                |
+-----------------------------------------------------------------------------------+
```

---

## 2. Mapeamento Interdisciplinar das Disciplinas da UNIP

| Disciplina Curricular | Aplicação Direta no Projeto |
| :--- | :--- |
| **Circuitos Lógicos Digitais** | Dimensionamento dos circuitos de condicionamento de sinal (divisores resistivos do LDR e MQ-135), barramento I2C para BMP280, portas lógicas e lógica combinacional de acionamento de alarme local autônomo (LED/Buzzer). |
| **Lógica de Programação e Algoritmos** | Algoritmos de leitura de sensores sem travamento (temporização baseada em `millis()`), rotinas de cálculo de média móvel para estabilização de leitura e estruturas de repetição e seleção no firmware. |
| **Lógica Matemática / Fundamentos Lógicos** | Modelagem formal de regras de consistência de dados (descarte de leituras impossíveis) e tabelas-verdade para os estados de alerta climático (ex.: Chuva Intensa $\land$ Queda Barométrica $\implies$ Alerta de Tempestade). |
| **Programação Estruturada em Python** | Construção da API REST completa com FastAPI, classes Pydantic para validação estruturada dos dados, manipulação de coleções (listas, dicionários, tuplas) e análises estatísticas em Python. |
| **Geometria Analítica para Computação** | Georreferenciamento bidimensional e tridimensional da estação, aplicação de vetores para cálculo de dispersão de poluentes/gradiente térmico e equações da circunferência no plano para delimitar raios de cobertura e impacto de alertas. |
| **Educação Ambiental** | Apresentação transparente e acessível de métricas de qualidade do ar e conforto térmico para conscientização dos cidadãos, suporte a políticas públicas e mitigação de ilhas de calor urbanas. |

---

## 3. Especificação da Camada 1: Hardware e Firmware (ESP32)

### 3.1. Lista de Componentes do Dispositivo

| Componente | Função | Tipo de Sinal / Interface | Faixa de Operação |
| :--- | :--- | :--- | :--- |
| **ESP32 NodeMCU (30 pinos)** | Processador central e módulo Wi-Fi 2.4 GHz | Microcontrolador Dual-Core 240 MHz | 3.3V DC |
| **DHT22 (AM2302)** | Temperatura e Umidade Relativa | Digital (Pino Único Proprietário) | -40 a +80 °C / 0 a 100% UR |
| **BMP280** | Pressão Atmosférica e Estimativa de Altitude | Digital (Barramento I2C - SDA/SCL) | 300 a 1100 hPa |
| **MQ-135** | Qualidade do ar (CO2, NH3, fumaça, benzeno) | Analógico (ADC) / Digital comparador | 10 a 1000 ppm |
| **LDR (Fotoresistor 5mm)** | Nível de luminosidade ambiente (radiação solar) | Analógico (Divisor de Tensão resistivo) | 0 a 4095 (ADC de 12 bits) |
| **Sensor de Chuva / Pluviômetro** | Detecção e intensidade de precipitação pluvial | Analógico (presença de lâmina de água) | 0 a 4095 (ADC) |
| **Resistores (10kΩ e 4.7kΩ)** | Pull-up para DHT22 e divisor para LDR | Passivo | N/A |
| **LED RGB + Buzzer 5V** | Indicador local de status e alarme autônomo | Digital (GPIOs com lógica de acionamento) | 3.3V / 5V |
| **Protoboard 830 pontos + Jumpers** | Conexão sem solda dos componentes | Prototipagem | N/A |

### 3.2. Mapeamento Completo de Conexões e Pinagem (ESP32 & Protoboard)

A estação utiliza uma arquitetura com **duas protoboards unidas em paralelo**, proporcionando espaço seguro e organizado para a disposição do ESP32 NodeMCU e dos módulos de sensoriamento, minimizando interferências eletromagnéticas e ruídos nas linhas analógicas.

| Sensor / Periférico | Pino no Sensor | Conectar em (ESP32 / Protoboard) | Observações Técnicas |
| :--- | :--- | :--- | :--- |
| **Alimentação Lógica** | Trilho Vermelho (Protoboard 1 - Superior) | **3V3 do ESP32** | Barramento regulado de 3.3V para sensores lógicos (BMP280, DHT22, LDR, Sensor de Chuva). |
| **GND Comum** | Trilho Azul/Preto (Ambas Protoboards) | **GND do ESP32** | Ponto de terra unificado interligando os trilhos superior e inferior para fechar o circuito. |
| **Alimentação de Potência** | Trilho Vermelho/Laranja (Protoboard 2 - Inferior) | **VIN / 5V do ESP32** | Barramento de 5V direto da porta USB, reservado exclusivamente para o aquecedor do MQ-135. |
| **BMP280** (Pressão e Temp.) | `VCC`<br>`GND`<br>`SCL`<br>`SDA` | Trilho 3.3V<br>Trilho GND<br>**GPIO 22** (SCL padrão)<br>**GPIO 21** (SDA padrão) | Barramento I2C digital. Pinos `CSB` e `SDO` mantidos desconectados (ou ligar `SDO` ao GND para fixar endereço I2C `0x76`). |
| **DHT22** (Umidade e Temp.) | `VCC` (Pino 1)<br>`DATA / OUT` (Pino 2)<br>`NC` (Pino 3)<br>`GND` (Pino 4) | Trilho 3.3V<br>**GPIO 4**<br>Não conectar<br>Trilho GND | Barramento proprietário One-Wire. Exige resistor de pull-up de 10kΩ entre o Pino 1 (`VCC`) e o Pino 2 (`DATA`) se for sensor avulso. Módulos com PCB integrada já possuem esse resistor embutido. |
| **LDR** (Luminosidade) | Perna A<br>Perna B | Trilho 3.3V<br>**GPIO 34** (ADC1) + Resistor 10kΩ ao GND | Configuração em divisor de tensão resistivo. Como o ESP32 opera com ADC de 12 bits no canal ADC1 (não sofre interferência do Wi-Fi), a leitura é estável. |
| **Sensor de Chuva** (Gotas) | `VCC`<br>`GND`<br>`AO` (Saída Analógica) | Trilho 3.3V<br>Trilho GND<br>**GPIO 35** (ADC1) | Alimentar o módulo comparador em 3.3V garante que a excursão de tensão em `AO` varie estritamente entre 0.0V e 3.3V, protegendo o pino ADC1 do ESP32. |
| **MQ-135** (Gases / Qualidade Ar) | `VCC`<br>`GND`<br>`AO` (Saída Analógica) | Trilho 5V (`VIN`)<br>Trilho GND<br>**GPIO 32** (via Divisor de Tensão) | O filamento de aquecimento exige 5.0V nominais. Para compatibilizar a saída analógica de até 5V com o ESP32 (máx. 3.3V), é obrigatório o divisor resistivo 1kΩ / 2kΩ. |
| **Indicadores Locais** | Anodo LED / Buzzer | **GPIO 25** (Alarme) / **GPIO 26** (Wi-Fi) | Acionamento digital local para resposta rápida em caso de alerta ou perda de sinal. |

---

### 3.3. Detalhamento dos Circuitos Passivos na Protoboard

A integração mista de componentes analógicos de 3.3V e 5V com o microcontrolador ESP32 requer condicionamento passivo de sinal rigorosamente dimensionado conforme os preceitos de **Circuitos Lógicos Digitais**:

#### 1. Divisor de Tensão do LDR (Fotoresistor)
O LDR varia sua resistência ôhmica inversamente proporcional à irradiância luminosa incidente. Para transformar essa variação de resistência em um sinal de tensão legível pelo conversor analógico-digital (ADC):
* Conecta-se um terminal do LDR à linha regulada de **3.3V**.
* Conecta-se o outro terminal do LDR à entrada analógica **GPIO 34** (ADC1_CH6).
* No mesmo nó do GPIO 34, conecta-se um resistor pull-down fixo de **10kΩ**.
* O outro terminal do resistor de 10kΩ conecta-se à linha de **GND**.

Dessa forma, sob escuridão total ($R_{\text{LDR}} \gg 10\text{k}\Omega$), a tensão no GPIO 34 tende a 0V ($\text{raw\_adc} \approx 0$). Sob incidência solar plena ($R_{\text{LDR}} \ll 10\text{k}\Omega$), a tensão aproxima-se de 3.3V ($\text{raw\_adc} \approx 4095$).

#### 2. Circuito Atenuador / Divisor de Proteção do MQ-135 (5V $\rightarrow$ 3.3V)
O sensor eletroquímico MQ-135 exige 5V em seu filamento aquecedor interno (*heater*) para promover a adsorção de gases na camada semicondutora de dióxido de estanho ($\text{SnO}_2$). Por consequência, o pino de saída analógica `AO` pode fornecer até 5.0V, tensão destrutiva para as portas GPIO do ESP32 (cujo limite absoluto é 3.6V).

Para atenuar o sinal para uma faixa 100% segura sem perder a linearidade da leitura:
* Conecta-se a saída `AO` do MQ-135 a um resistor em série $R_1 = 1\text{ k}\Omega$.
* O terminal oposto de $R_1$ conecta-se simultaneamente ao **GPIO 32** (ADC1_CH4) e a um resistor $R_2 = 2\text{ k}\Omega$ (ou dois resistores de $1\text{ k}\Omega$ em série).
* O terminal inferior de $R_2$ é ligado ao **GND**.

A relação matemática de transferência do divisor de tensão é dada por:
$$V_{\text{ESP32}} = V_{\text{AO}} \cdot \left(\frac{R_2}{R_1 + R_2}\right) = V_{\text{AO}} \cdot \left(\frac{2000}{1000 + 2000}\right) = V_{\text{AO}} \cdot \frac{2}{3} \approx 0{,}667 \cdot V_{\text{AO}}$$

Para o pico máximo de emissão de $V_{\text{AO}} = 5{,}0\text{ V}$:
$$V_{\text{ESP32, máx}} = 5{,}0\text{ V} \cdot \frac{2}{3} \approx 3{,}33\text{ V}$$
O valor obtido enquadra-se com margem na faixa dinâmica nominal do ADC do ESP32 configurado com atenuação de 11 dB ($0\text{ a }3{,}3\text{ V}$).

---

### 3.4. Representação Visual e Montagem na Protoboard Dupla

A organização física das duas matrizes de contato (protoboards) garante que as trilhas de alimentação permaneçam independentes, evitando queda de tensão e ruídos induzidos pelo aquecedor do MQ-135 sobre as linhas sensíveis do I2C e do ADC:

![Esquema de Montagem e Interligação na Protoboard Dupla](assets/protoboard_esquematico.jpg)

**Diretrizes Críticas para a Montagem Prática:**
1. **Segregação de Barramentos:**
   * O **trilho vermelho superior** recebe a saída regulada de **3V3 do ESP32** e alimenta exclusivamente os sensores digitais e de baixa corrente (BMP280, DHT22, LDR e Sensor de Chuva).
   * O **trilho vermelho/laranja inferior** conecta-se diretamente ao pino **VIN / 5V** do ESP32 (fornecido pelo cabo USB), abastecendo exclusivamente o pino `VCC` do sensor MQ-135.
   * Os **trilhos azul/preto (GND)** superior e inferior são interligados por jumpers de derivação direta, assegurando equipotencialidade em todo o sistema.
2. **Estabilidade Mecânica e de Sinal:**
   * O módulo ESP32 fica centralizado na divisão da protoboard 1, permitindo acesso aos pinos de ambos os lados.
   * O BMP280 conecta-se via barramento I2C nos pinos nativos GPIO 21 (SDA) e GPIO 22 (SCL), operando com resistores pull-up internos ativados no microcontrolador.
   * O resistor de 10kΩ do DHT22 fica posicionado diretamente entre os pinos 1 e 2 do sensor para mitigar reflexões de onda na linha One-Wire.

---

### 3.5. Lógica Combinacional e Circuito Local de Segurança
Em conformidade com a disciplina de **Circuitos Lógicos Digitais**, o circuito local do ESP32 possui um estágio combinacional autônomo de alarme:
* Sejam as variáveis booleanas:
  * $C$: Chuva detectada em nível alto ($\text{intensity\_pct} > 15.0\%$)
  * $B$: Pressão barométrica em queda abrupta ($\Delta P < -2.0\text{ hPa/h}$)
  * $A$: Concentração de gases nocivos elevada ($\text{voltage\_v} > 2.5\text{ V}$)
* O sinal de emergência local $S$ para ativação do alarme autônomo (LED Vermelho / Buzzer no GPIO 25) é modelado pela expressão booleana:
  $$S = (C \land B) \lor A$$
Essa lógica garante acionamento instantâneo do alarme local mesmo diante de eventual perda ou latência da conexão Wi-Fi.

---

### 3.6. Contrato de Comunicação ESP32 & Servidor Backend (REST API)

A transmissão de telemetria entre o ESP32 (produtor) e a API em Nuvem (consumidor) adota o protocolo HTTP sobre TCP/IP nativo do stack Wi-Fi do ESP32 (`esp_http_client` / `HTTPClient.h`), dispensando brokers intermediários na camada inicial.

#### A. Parâmetros de Transporte e Rede

| Parâmetro | Especificação Técnica | Justificativa de Engenharia |
| :--- | :--- | :--- |
| **Protocolo de Aplicação** | HTTP/1.1 (ou HTTPS / TLS 1.3) | Integração direta com APIs REST padrão, minimizando overhead de infraestrutura. |
| **Método HTTP** | `POST` | Semântica idempotente de ingestão de novos registros de séries temporais. |
| **Endpoint Canônico** | `/api/v1/telemetry` | Padrão RESTful versionado para ingestão de telemetria ambiental. |
| **Porta (Desenvolvimento)** | `8080` | Porta padrão para servidores de teste local (`http://192.168.1.X:8080/api/v1/telemetry`). |
| **Porta (Produção em Nuvem)** | `80` (HTTP) / `443` (HTTPS) | Portas padrão de tráfego web seguro gerenciadas pelo proxy reverso Nginx na AWS. |
| **Content-Type** | `application/json` | Serialização estruturada leve, com baixo consumo de memória RAM via `ArduinoJson v6/v7`. |
| **Autenticação / Segurança** | `X-API-Key: <token_secreto>` | Validação de credencial estática no cabeçalho HTTP para mitigar requisições forjadas. |
| **Intervalo de Envio (Polling)** | A cada 30 a 60 segundos | Respeita a taxa física de acomodação do DHT22 ($\ge 2\text{ s}$) e economiza largura de banda. |

#### B. Estrutura Canônica do Payload JSON

Seguindo as melhores práticas de arquitetura IoT, o firmware transmite simultaneamente o **valor bruto digitalizado do ADC (`raw_adc`)** e o **valor de engenharia processado** (tensão, porcentagem ou unidade física). Isso permite que calibrações finas, compensações de offset ou alterações de limiares sejam ajustadas diretamente no backend sem necessidade de regravar o firmware do dispositivo em campo.

```json
{
  "device_id": "esp32-meteo-01",
  "timestamp": 1792508580,
  "wifi_rssi_dbm": -62,
  "sensors": {
    "dht22": {
      "temperature_c": 25.4,
      "humidity_pct": 68.2,
      "status": "OK"
    },
    "bmp280": {
      "temperature_c": 25.6,
      "pressure_hpa": 1013.25,
      "altitude_m": 760.5,
      "status": "OK"
    },
    "ldr": {
      "raw_adc": 2890,
      "luminosity_pct": 70.6
    },
    "mq135": {
      "raw_adc": 1150,
      "voltage_v": 1.39,
      "air_quality_ppm": 415.8,
      "is_warmed_up": true
    },
    "rain": {
      "raw_adc": 3850,
      "intensity_pct": 6.0,
      "is_raining": false
    }
  }
}
```

#### C. Dicionário de Dados do Hardware e Fórmulas de Conversão
O conversor Analógico-Digital (ADC) integrado do ESP32 opera com resolução de **12 bits**, mapeando tensões entre $0{,}0\text{ V}$ e $3{,}3\text{ V}$ em números inteiros discretos de **0 a 4095**:

1. **Metadados do Dispositivo:**
   * `device_id` *(String)*: Identificador unívoco da estação (ex.: ID cadastrado ou MAC Address).
   * `timestamp` *(Long / Unix Epoch)*: Horário exato da leitura em segundos, sincronizado via NTP (*Network Time Protocol*). Pode ser preenchido pela API caso o relógio local do ESP32 não esteja calibrado.
   * `wifi_rssi_dbm` *(Integer)*: Indicador de intensidade do sinal recebido em $\text{dBm}$ (ex.: $-50\text{ dBm}$ excelente, $-85\text{ dBm}$ crítico), para diagnóstico de conectividade de campo.
2. **Sensor DHT22 (GPIO 4 — One-Wire):**
   * `temperature_c` *(Float)*: Temperatura do ar em graus Celsius (faixa de $-40^\circ\text{C}$ a $+80^\circ\text{C}$, resolução $\pm 0{,}1^\circ\text{C}$).
   * `humidity_pct` *(Float)*: Umidade relativa do ar de $0{,}0\%$ a $100{,}0\%$.
   * `status` *(String)*: `"OK"` ou `"READ_ERROR"` (tratamento defensivo caso o sensor retorne `NaN`).
3. **Sensor BMP280 (GPIO 21/22 — Barramento I2C):**
   * `temperature_c` *(Float)*: Temperatura do silício para compensação de dilatação da cápsula piezorresistiva. Atua como redundância analítica para o DHT22.
   * `pressure_hpa` *(Float)*: Pressão barométrica absoluta em Hectopascais ($1\text{ hPa} = 1\text{ mbar}$).
   * `altitude_m` *(Float)*: Estimativa barométrica de elevação em metros em relação ao nível médio do mar.
   * `status` *(String)*: `"OK"` ou `"I2C_ERROR"`.
4. **Sensor LDR (GPIO 34 — ADC1):**
   * `raw_adc` *(Integer)*: Valor bruto quantizado de 0 a 4095. Como o LDR está ligado ao 3.3V com pull-down de 10kΩ ao GND, maior luminosidade acarreta maior tensão.
   * `luminosity_pct` *(Float)*: Conversão linear percentual ($0{,}0\%$ a $100{,}0\%$):
     $$\text{luminosity\_pct} = \left(\frac{\text{raw\_adc}}{4095.0}\right) \times 100$$
5. **Sensor MQ-135 (GPIO 32 — ADC1 com Divisor Resistivo):**
   * `raw_adc` *(Integer)*: Leitura digitalizada de 0 a 4095 correspondente à saída atenuada do divisor.
   * `voltage_v` *(Float)*: Reconstituição da tensão real gerada pelo sensor antes do divisor passivo ($2/3$). Multiplica-se o valor medido pelo inverso do fator de atenuação ($1{,}5$):
     $$\text{voltage\_v} = \left(\frac{\text{raw\_adc}}{4095.0}\right) \times 3.3 \times 1.5$$
   * `air_quality_ppm` *(Float)*: Estimativa de concentração de partículas redutoras em partes por milhão (PPM).
   * `is_warmed_up` *(Boolean)*: Flag de estabilização térmica. O sensor exige no mínimo 3 minutos de pré-aquecimento do filamento químico. Enquanto $\text{millis}() < 180000$, envia-se `false`, instruindo o backend a descartar leituras transitórias.
6. **Sensor de Chuva (GPIO 35 — ADC1):**
   * `raw_adc` *(Integer)*: Em estado seco, a resistência entre as trilhas é infinita ($\text{raw\_adc} \approx 4095$). Ao acumular gotas d'água condutivas, a resistência despenca, aproximando a tensão de 0V.
   * `intensity_pct` *(Float)*: Porcentagem de saturação hídrica calculada de forma complementar invertida:
     $$\text{intensity\_pct} = \left(1.0 - \frac{\text{raw\_adc}}{4095.0}\right) \times 100$$
   * `is_raining` *(Boolean)*: Flag binária ativada por limiar prático ($\text{is\_raining} = \text{true}$ se $\text{intensity\_pct} > 15.0\%$).

#### D. Tratamento de Códigos de Resposta HTTP no Firmware

O firmware do ESP32 deve avaliar o cabeçalho de status da resposta para gerenciar a rotina de retenção e retransmissão:

| Código HTTP | Significado | Comportamento Operacional do ESP32 |
| :--- | :--- | :--- |
| **`201 Created` / `200 OK`** | Ingestão bem-sucedida | Sucesso confirmado. Limpa buffers temporários e entra no modo de repouso até o próximo ciclo. |
| **`400 Bad Request` / `422 Unprocessable`** | Inconsistência nos dados | Erro de tipagem ou campo nulo. Imprime log de depuração na Serial e descarta o registro corrompido. |
| **`401 Unauthorized`** | Falha de autenticação | Token de chave de API (`X-API-Key`) inválido ou expirado. Registra alerta crítico na Serial. |
| **`500 Internal Error` / `-1 Timeout`** | Falha de nuvem ou rede | Servidor inacessível ou queda de Wi-Fi. O ESP32 armazena a telemetria em buffer circular e força reconexão de rede. |

---

## 4. Especificação da Camada 2: Backend em Nuvem (AWS & Python)

### 4.1. Infraestrutura na Nuvem AWS
* **Ambiente de Computação:** Instância **AWS EC2** (tipo `t2.micro` ou `t3.micro`, elegível no nível gratuito *Free Tier* por 12 meses) executando Ubuntu Server 24.04 LTS.
* **Gerenciador de Processos:** `Gunicorn` com workers `Uvicorn` supervisionados por serviço `systemd`.
* **Segurança de Rede:** AWS Security Group configurado com:
  * Porta `22` (SSH restrito);
  * Porta `80` (HTTP) redirecionada para `443` (HTTPS com certificado SSL gratuito Let's Encrypt / Certbot);
  * Porta `8000` (FastAPI interna vinculada a proxy reverso Nginx).

### 4.2. Arquitetura de Software da API (FastAPI)
A aplicação em Python é estruturada de forma modular e tipada:
```
backend/
├── app/
│   ├── main.py              # Ponto de entrada FastAPI e middlewares CORS
│   ├── config.py            # Variáveis de ambiente (DB_URL, CHAVE_API)
│   ├── database.py          # Conexão SQLAlchemy e sessão do banco de dados
│   ├── models.py            # Modelos relacionais das tabelas ORM
│   ├── schemas.py           # Esquemas de validação Pydantic (Request/Response)
│   ├── services/
│   │   ├── weather_math.py  # Fórmulas matemáticas (Heat Index, AQI, Geometria)
│   │   ├── alert_engine.py  # Regras de inferência lógica para emissão de alertas
│   │   └── statistics.py    # Médias móveis, extremos e agregações
│   └── routers/
│       ├── telemetria.py    # Endpoints de recebimento e consulta de dados (/telemetry)
│       └── alertas.py       # Endpoints de consulta de alertas ativos
├── requirements.txt         # Dependências do projeto (fastapi, uvicorn, pydantic, sqlalchemy)
└── Dockerfile               # Conteinerização para deploy em nuvem
```

#### Esquema de Validação Pydantic (Python):
```python
from typing import Optional
from pydantic import BaseModel, Field

class DHT22Data(BaseModel):
    temperature_c: float = Field(..., ge=-40.0, le=80.0, description="Temperatura em Celsius")
    humidity_pct: float = Field(..., ge=0.0, le=100.0, description="Umidade relativa do ar (%)")
    status: str = Field(default="OK")

class BMP280Data(BaseModel):
    temperature_c: float
    pressure_hpa: float = Field(..., ge=300.0, le=1100.0, description="Pressão atmosférica em hPa")
    altitude_m: float
    status: str = Field(default="OK")

class LDRData(BaseModel):
    raw_adc: int = Field(..., ge=0, le=4095)
    luminosity_pct: float = Field(..., ge=0.0, le=100.0)

class MQ135Data(BaseModel):
    raw_adc: int = Field(..., ge=0, le=4095)
    voltage_v: float = Field(..., ge=0.0, le=5.0)
    air_quality_ppm: float
    is_warmed_up: bool = True

class RainData(BaseModel):
    raw_adc: int = Field(..., ge=0, le=4095)
    intensity_pct: float = Field(..., ge=0.0, le=100.0)
    is_raining: bool

class SensorsPayload(BaseModel):
    dht22: DHT22Data
    bmp280: BMP280Data
    ldr: LDRData
    mq135: MQ135Data
    rain: RainData

class TelemetryIngest(BaseModel):
    device_id: str = Field(..., min_length=3, max_length=50)
    timestamp: Optional[int] = Field(None, description="Unix timestamp UTC")
    wifi_rssi_dbm: Optional[int] = Field(None, ge=-120, le=0)
    sensors: SensorsPayload
```

### 4.3. Especificação dos Endpoints REST

| Método | Rota | Descrição | Cabeçalhos / Parâmetros / Corpo |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/telemetry`<br>*(alias: `/telemetria`)* | Ingestão primária da telemetria do ESP32. Valida payload Pydantic, calcula métricas derivadas e persiste no PostgreSQL. | Header: `X-API-Key: <token>`<br>Body: JSON `TelemetryIngest` |
| `GET` | `/api/v1/telemetry/latest` | Retorna o registro meteorológico mais recente para exibição no Dashboard. | Query: `device_id` (opcional) |
| `GET` | `/api/v1/telemetry/history` | Retorna o histórico de leituras das últimas 24h para montagem dos gráficos no Chart.js. | Query: `hours` (padrão: 24), `limit` (padrão: 100) |
| `GET` | `/api/v1/alerts/active` | Retorna os alertas climáticos e socioambientais vigentes no momento. | Resposta: Lista estruturada de alertas |
| `GET` | `/api/v1/analysis/geometry` | Retorna as coordenadas da estação, raio de cobertura analítico e cálculo de distância do usuário. | Query: `user_lat`, `user_lon` |
| `GET` | `/health` | Verificação de disponibilidade da API e conexão com o banco. | Resposta: Status `ok` com latência de BD |

### 4.4. Módulo Matemático e Lógica de Negócio em Python

#### A. Cálculo da Sensação Térmica (*Heat Index* de Rothfusz)
Para temperaturas $T \ge 27^\circ\text{C}$ e umidade $R \ge 40\%$, a sensação térmica em graus Celsius é obtida pela equação polinomial multivariável:
$$HI = c_1 + c_2 T + c_3 R + c_4 T R + c_5 T^2 + c_6 R^2 + c_7 T^2 R + c_8 T R^2 + c_9 T^2 R^2$$

#### B. Normalização do Índice de Qualidade do Ar (AQI Urbano)
O valor de resistência lido pelo sensor MQ-135 é convertido em uma escala normalizada de 0 a 500 conforme as faixas da OMS / CETESB:
* **0 a 50:** Boa (Verde)
* **51 a 100:** Moderada (Amarelo)
* **101 a 150:** Inadequada para grupos sensíveis (Laranja)
* **151 a 200:** Má / Insalubre (Vermelho)
* **> 200:** Crítica / Perigosa (Roxo)

---

## 5. Especificação da Camada 3: Banco de Dados em Nuvem (PostgreSQL)

O banco de dados escolhido é o **PostgreSQL** hospedado na nuvem (utilizando serviços com camada gratuita gerenciada como **Supabase**, **Neon** ou **AWS RDS Free Tier**), proporcionando facilidade de integração via string de conexão SSL padrão (`postgresql+psycopg2://...`), alta confiabilidade e suporte nativo a consultas espaciais e séries temporais.

### 5.1. Modelo Relacional e Esquema SQL

```sql
-- 1. Tabela de Cadastro das Estações Meteorológicas
CREATE TABLE estacoes (
    id VARCHAR(30) PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    cidade VARCHAR(80) NOT NULL,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    altitude DOUBLE PRECISION NOT NULL,
    raio_cobertura_km DOUBLE PRECISION DEFAULT 5.0,
    ativa BOOLEAN DEFAULT TRUE,
    criada_em TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 2. Tabela de Séries Temporais das Leituras dos Sensores
CREATE TABLE leituras_sensores (
    id BIGSERIAL PRIMARY KEY,
    estacao_id VARCHAR(30) REFERENCES estacoes(id),
    data_hora TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    -- Variáveis meteorológicas processadas
    temperatura NUMERIC(4, 1) NOT NULL,
    umidade NUMERIC(4, 1) NOT NULL,
    pressao NUMERIC(6, 1) NOT NULL,
    altitude_m NUMERIC(6, 1),
    qualidade_ar NUMERIC(6, 1) NOT NULL,
    luminosidade NUMERIC(5, 1) NOT NULL,
    chuva_intensidade NUMERIC(5, 1) NOT NULL,
    chuva_detectada BOOLEAN DEFAULT FALSE,
    sensacao_termica NUMERIC(4, 1),
    aqi_classificacao VARCHAR(30),
    -- Diagnóstico e valores brutos do conversor analógico-digital (ADC 12 bits)
    wifi_rssi_dbm INTEGER,
    ldr_raw_adc INTEGER,
    mq135_raw_adc INTEGER,
    mq135_voltage_v NUMERIC(4, 2),
    mq135_warmed_up BOOLEAN DEFAULT TRUE,
    rain_raw_adc INTEGER,
    dht22_status VARCHAR(15) DEFAULT 'OK',
    bmp280_status VARCHAR(15) DEFAULT 'OK'
);

-- Índice composto para consultas temporais ultra-rápidas no Dashboard
CREATE INDEX idx_leituras_estacao_data ON leituras_sensores (estacao_id, data_hora DESC);

-- 3. Tabela de Alertas e Notificações Emitidas
CREATE TABLE alertas_emitidos (
    id BIGSERIAL PRIMARY KEY,
    estacao_id VARCHAR(30) REFERENCES estacoes(id),
    tipo_evento VARCHAR(50) NOT NULL,      -- 'TEMPESTADE', 'AR_INSALUBRE', 'CALOR_EXTREMO'
    severidade VARCHAR(20) NOT NULL,       -- 'INFO', 'ATENCAO', 'PERIGO', 'EMERGENCIA'
    mensagem TEXT NOT NULL,
    recomendacao_cidadao TEXT NOT NULL,
    emitido_em TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    resolvido_em TIMESTAMP WITH TIME ZONE
);
```

---

## 6. Aplicação da Geometria Analítica na Computação

Em atendimento formal aos objetivos do projeto interdisciplinar, a Geometria Analítica é empregada em três componentes essenciais da solução:

### 6.1. Posicionamento e Projeção no Plano Cartesiano
Cada estação meteorológica $E_0$ possui coordenadas geodésicas de Latitude ($\phi_0$) e Longitude ($\lambda_0$). Para análises locais urbanas, realiza-se uma projeção equirretangular aproximando o plano tangente da cidade como um plano cartesiano $\mathbb{R}^2$:
$$x = R_{\text{terra}} \cdot (\lambda - \lambda_0) \cdot \cos\left(\frac{\phi + \phi_0}{2}\right)$$
$$y = R_{\text{terra}} \cdot (\phi - \phi_0)$$
Onde $R_{\text{terra}} \approx 6371\text{ km}$.

### 6.2. Equação do Raio de Cobertura e Abrangência de Alertas
A área urbana influenciada pelas medições da estação é modelada pela equação canônica da circunferência no plano cartesiano:
$$(x - x_0)^2 + (y - y_0)^2 \le r^2$$
Onde:
* $(x_0, y_0)$ é a origem coincidente com a localização da estação meteorológica;
* $r$ é o raio analítico de dispersão/validade dos dados microclimáticos (ex.: $r = 5\text{ km}$).

Quando o cidadão acessa o dashboard e concede acesso à geolocalização do navegador $(x_u, y_u)$, o backend calcula a **Distância Euclidiana**:
$$d = \sqrt{(x_u - x_0)^2 + (y_u - y_0)^2}$$
Se $d \le r$, o cidadão é notificado de que se encontra na zona de cobertura direta dos alertas meteorológicos vigentes.

### 6.3. Vetores de Tendência Barométrica e Dispersão
A taxa de variação barométrica em relação ao tempo é expressa como um vetor unidimensional de gradiente de pressão:
$$\vec{v}_{\Delta P} = \left(\frac{dP}{dt}\right) \hat{i}$$
Se $|\vec{v}_{\Delta P}| < -2.0\text{ hPa/hora}$, o algoritmo identifica uma frente fria/tempestade em rápida aproximação espacial.

---

## 7. Especificação da Camada 4: Dashboard Web Público Online

### 7.1. Características Técnicas e Hospedagem
* **Tecnologias:** HTML5 semântico, Vanilla CSS moderno (Grid, Flexbox, variáveis CSS, tipografia Google Fonts *Outfit* / *Inter*), JavaScript assíncrono modular.
* **Hospedagem Online:** **Vercel** ou **Netlify** (com integração contínua a partir de repositório Git, certificado SSL automático e custo zero).
* **Consumo de Dados:** Requisições via `fetch()` consumindo a API na nuvem AWS, com atualização automática a cada 30 segundos (polling inteligente).

### 7.2. Elementos e Módulos da Interface
1. **Header Informativo:**
   * Título do Sistema ("EcoPulse Urbano - Monitoramento Climático Inteligente");
   * Tag de Status da Estação em tempo real (`ONLINE - Conectado via Wi-Fi/AWS`);
   * Carimbo de data/hora da última leitura atualizada.
2. **Painel de Indicadores Principais (Cards de Telemetria):**
   * **Temperatura:** Valor atual em °C + Sensação Térmica calculada;
   * **Umidade Relativa:** Valor percentual + barra de conforto higrométrico;
   * **Pressão Atmosférica:** Valor em hPa + vetor de tendência (subindo, estável ou caindo);
   * **Qualidade do Ar:** Concentração estimada + Tag visual com cor indicativa (Boa / Moderada / Nociva);
   * **Luminosidade:** Intensidade solar (Dia Claro / Nublado / Noite);
   * **Chuva:** Presença e intensidade pluviométrica instantânea.
3. **Painel de Alertas de Defesa Civil:**
   * Mensagens dinâmicas baseadas nas regras de Lógica Matemática (ex.: Alerta amarelo de tempestade com instruções de segurança para os moradores).
4. **Gráficos Históricos Interativos (Chart.js):**
   * Gráfico 1: Variação de Temperatura e Sensação Térmica nas últimas 24 horas;
   * Gráfico 2: Pressão Atmosférica e Índice Pluviométrico;
   * Gráfico 3: Índice de Qualidade do Ar ao longo do dia.
5. **Mapa Interativo com Geometria Analítica (Leaflet.js):**
   * Marcador georreferenciado da estação na cidade;
   * Círculo representativo do raio analítico de cobertura ($r$ km);
   * Botão "Minha Localização" que projeta as coordenadas do usuário e informa a distância euclidiana exata até a estação.
6. **Rodapé de Sustentabilidade e Transparência:**
   * Dicas de educação ambiental baseadas no clima atual (ex.: economia de água, cuidados com ar seco, proteção solar).

---

## 8. Roteiro de Testes e Validação do Projeto

| ID | Cenário de Teste | Procedimento | Critério de Sucesso |
| :--- | :--- | :--- | :--- |
| **TC-01** | Coleta dos sensores | Iniciar ESP32 conectado aos sensores no protótipo físico ou Wokwi. | Leituras coerentes no monitor serial dentro das faixas nominais. |
| **TC-02** | Filtragem de anomalias | Simular desconexão de pino de dados do sensor. | O firmware detecta falha e não envia dados inconsistentes para a nuvem. |
| **TC-03** | Ingestão na Nuvem AWS | ESP32 envia payload JSON para o endpoint `/api/v1/telemetria`. | A API retorna status `HTTP 201 Created` e grava os registros no PostgreSQL. |
| **TC-04** | Disparo de Alertas Lógicos | Injetar via simulador pressão baixa (< 1005 hPa) e chuva alta. | O motor de regras gera registro na tabela `alertas_emitidos` com severidade `PERIGO`. |
| **TC-05** | Cálculo Geoanalítico | Enviar requisição com coordenadas distantes da estação. | A API calcula com precisão a distância em km e valida se está dentro do raio. |
| **TC-06** | Acessibilidade e Responsividade | Abrir dashboard em desktop (1920x1080) e smartphone (375x667). | Layout fluido sem quebra de elementos, tempo de carregamento < 1.5s. |

---

## 9. Estrutura Mapeada para o Relatório ABNT (15 a 20 Páginas de Desenvolvimento)

Para atender estritamente aos requisitos do manual da UNIP:

* **Elementos Pré-Textuais:** Capa institucional, Resumo com palavras-chave, Abstract com keywords, Sumário.
* **Seção 1: Introdução (aprox. 1,5 páginas):** Contextualização sobre Smart Cities, justificativa socioambiental e objetivos do PD-II.
* **Seção 2: Desenvolvimento (15 a 20 páginas divididas conforme as 6 etapas oficiais):**
  * *Capítulo 2.1 – Concepção e Planejamento:* Requisitos funcionais, diagrama de casos de uso e gestão ágil (Kanban).
  * *Capítulo 2.2 – Circuitos Eletrônicos e Hardware:* Esquemático na protoboard, dimensionamento dos componentes e circuitos lógicos de segurança.
  * *Capítulo 2.3 – Firmware do Microcontrolador ESP32:* Arquitetura do software embarcado, fluxo de leitura não-bloqueante e comunicação Wi-Fi.
  * *Capítulo 2.4 – Backend em Nuvem e Banco de Dados:* Configuração da AWS (EC2/PostgreSQL), arquitetura REST com FastAPI e modelagem de dados.
  * *Capítulo 2.5 – Fundamentos Teóricos Integrados:* Demonstração formal dos conceitos de Lógica Matemática (tabelas-verdade) e Geometria Analítica (vetores, projeções e equações da circunferência).
  * *Capítulo 2.6 – Dashboard Público e Análise de Dados:* Interfaces da aplicação web, gráficos, mapa interativo e responsividade.
  * *Capítulo 2.7 – Resultados, Testes e Discussão:* Evidências de funcionamento, logs de transmissão, validação de estabilidade e análise de impacto ambiental.
* **Seção 3: Conclusão (aprox. 1,5 páginas):** Síntese dos resultados alcançados, contribuições acadêmicas e perspectivas futuras.
* **Elementos Pós-Textuais:** Referências bibliográficas normatizadas segundo a ABNT NBR 6023.
