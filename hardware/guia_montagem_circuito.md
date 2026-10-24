# 📘 Manual Ilustrado de Montagem: Estação Meteorológica IoT com ESP32

Este documento apresenta o guia passo a passo da montagem física da estação **EcoPulse** em bancada, adotando a arquitetura de **Menor Caminho e Fiação Rente (Topologia Zero-Crossing)**. As protoboards estão acopladas horizontalmente pelas **travas plásticas laterais**, com a **Fonte MB102 na extremidade esquerda**, o **ESP32 na extremidade direita** e os sensores agrupados por **afinidade de borda** (sensores digitais/I2C no topo, sensores analógicos na base), permitindo que mais de **90% das conexões sejam feitas com jumpers rígidos em U rentes à matriz**, eliminando por completo o emaranhado de fios.

Documentos complementares de engenharia:
* [Tabela de Pinout Completa](file:///home/wvs/Documents/ccomp-unip/2sem/pim2/ecopulse/hardware/pinout_conexoes.md)
* [Cálculo Matemático dos Divisores de Tensão](file:///home/wvs/Documents/ccomp-unip/2sem/pim2/ecopulse/hardware/calculo_divisores_tensao.md)
* [Lista de Materiais (BOM)](file:///home/wvs/Documents/ccomp-unip/2sem/pim2/ecopulse/hardware/README.md)
* [Esquemático Ilustrado com Fonte MB102 (PNG)](file:///home/wvs/Documents/ccomp-unip/2sem/pim2/ecopulse/hardware/assets/protoboard_esquematico_mb102.png)
* [Esquemático Vetorial com Fonte MB102 (SVG)](file:///home/wvs/Documents/ccomp-unip/2sem/pim2/ecopulse/hardware/assets/protoboard_esquematico_mb102.svg)

---

## 🖼️ Visão Geral do Circuito (Layout de Menor Caminho)

![Esquemático de Menor Caminho com Fonte MB102](assets/protoboard_esquematico_mb102.png)

> [!IMPORTANT]
> **Vantagens da Arquitetura de Menor Caminho (Zero-Crossing):**
> 1. **Zero Cruzamentos Entre Placas:** Sensores digitais e I2C cujos pinos estão no topo do ESP32 (`D4`, `D21`, `D22`) ficam na **Protoboard Superior**. Sensores analógicos cujos pinos estão na base do ESP32 (`D34`, `D35`, `D32`) ficam na **Protoboard Inferior**.
> 2. **Distâncias Curtíssimas (2 a 7 furos):** Sensores colados ao microcontrolador usam jumpers rígidos em U retos, como trilhas de circuito impresso (PCB).
> 3. **Alimentação 100% Local (Jumpers 2 Furos):** Cada sensor puxa VCC e GND diretamente do trilho adjacente com os jumpers verdes de 2 furos.

---

## 🛠️ 1. Topografia das Coordenadas da Dupla Protoboard

```text
[FONTE MB102 - ESQUERDA]                                                    [ESP32 - DIREITA]
+-------------------------------------------------------------------------------------------+
| [-] Linha Azul: GND Comum                                                                 |
| [+] Linha Vermelha: BARRAMENTO 1 -> 5.0V EXCLUSIVO P/ MQ-135 (Jumper MB102 em 5V)         |
+-------------------------------------------------------------------------------------------+
|  Proto Sup (Fileiras 'j'-'f'): MQ-135 (Cols 16-19) + Divisor (Cols 20-22)                 |
|  ==================== Canal Central Divisório ====================                        |
|  Proto Sup (Fileiras 'e'-'a'): BMP280 (Cols 43-48) | DHT22 (Cols 54-56) | ESP32 (48-62)   |
+-------------------------------------------------------------------------------------------+
| [+] Linha Vermelha: BARRAMENTO 2 -> 3.3V SEGURO (Alimenta BMP280, DHT22 e ESP32)          |
| [-] Linha Azul: GND Comum                                                                 |
+===========================================================================================+
| [== SUPORTEZINHO PLÁSTICO / TRAVAS LATERAIS ACOPLADAS ENTRE AS PROTOBOARDS ==]            |
+===========================================================================================+
| [+] Linha Vermelha: BARRAMENTO 3 -> 3.3V (Alimenta Chuva e LDR)                           |
| [-] Linha Azul: GND Comum                                                                 |
+-------------------------------------------------------------------------------------------+
|  Proto Inf (Fileiras 'j'-'f'): Chuva (Cols 36-39) | LDR (Cols 44-47) | ESP32 Base (48-62) |
|  ==================== Canal Central Divisório ====================                        |
|  Proto Inf (Fileiras 'e'-'a'): ÁREA INFERIOR DESIMPEDIDA (Livre de fios e componentes!)   |
+-------------------------------------------------------------------------------------------+
| [+] Linha Vermelha: BARRAMENTO 4 -> 3.3V (Reserva p/ Expansão Futura)                    |
| [-] Linha Azul: GND Comum                                                                 |
+-------------------------------------------------------------------------------------------+
```

---

## ⚡ Passo 1: Fonte MB102 e Distribuição de Energia

A fonte MB102 fica na extremidade esquerda da Protoboard Superior (colunas 1 a 8):

1. **Seletores Amarelos:**
   - **Lado Superior:** Jumper em **`5V`** -> Energiza o Barramento 1 com 5.0V exclusivo para o MQ-135.
   - **Lado Inferior:** Jumper em **`3.3V`** -> Energiza o Barramento 2 com 3.3V seguro.
2. **Malha de GND Comum (Jumpers Pretos):**
   - Interligue o Barramento 1 (-) ao Barramento 2 (-).
   - Interligue o Barramento 2 (-) ao Barramento 3 (-).
   - Interligue o Barramento 3 (-) ao Barramento 4 (-).
3. **Distribuição de 3.3V (Jumpers Vermelhos):**
   - Interligue o Barramento 2 (+) ao Barramento 3 (+).
   - Interligue o Barramento 3 (+) ao Barramento 4 (+).
4. **Pontes da Coluna 30:** Insira jumpers rígidos em U (3 a 5 furos) unindo o lado esquerdo ao direito nas linhas vermelhas e azuis de todos os barramentos utilizados.

---

## 🧠 Passo 2: Microcontrolador ESP32 no Vão Direito

Espetado nas colunas `48` a `62`, com a porta Micro-USB voltada para a direita:
* **Pinos Superiores (Fileira `a` da Proto Sup):**
  - **Coluna 62 (`3V3`):** Jumper U de 2 furos (verde pequeno) direto no Barramento 2 (+ 3.3V).
  - **Coluna 61 (`GND`):** Jumper U de 2 furos (verde pequeno) direto no Barramento 2 (- GND).
  - **Coluna 58 (`D4`):** Entrada One-Wire do DHT22.
  - **Coluna 52 (`D21`):** Entrada I2C SDA do BMP280.
  - **Coluna 49 (`D22`):** Entrada I2C SCL do BMP280.
* **Pinos Inferiores (Fileira `j` da Proto Inf):**
  - **Coluna 61 (`GND`):** Jumper U de 2 furos (verde pequeno) direto no Barramento 3 (- GND).
  - **Coluna 53 (`D32`):** Entrada analógica atenuada do MQ-135 (ADC1).
  - **Coluna 52 (`D35`):** Entrada analógica do Sensor de Chuva (ADC1).
  - **Coluna 51 (`D34`):** Entrada analógica do Módulo LDR (ADC1).

---

## 🧭 Passo 3: Cluster Superior I2C & Digital (BMP280 e DHT22)

Instalados na **Protoboard Superior**, colados no ESP32:

### 1. Sensor DHT22 (Colunas 54 a 56, Fileira `e`):
* **Pino `+` (VCC - Col 54):** Jumper U de 2 furos (verde) no Barramento 2 (+ 3.3V).
* **Pino `OUT` (DAT - Col 55):** Jumper U de 3 furos (laranja) direto no **pino D4 (coluna 58, fileira `b`)**! Distância de apenas 3 furos!
* **Pino `-` (GND - Col 56):** Jumper U de 2 furos (verde) no Barramento 2 (- GND).

### 2. Sensor BMP280 (Colunas 43 a 48, Fileira `e`):
* **Pino `VCC` (Col 43):** Jumper U de 2 furos no Barramento 2 (+ 3.3V). *(Nunca em 5V!)*
* **Pino `GND` (Col 44):** Jumper U de 2 furos no Barramento 2 (- GND).
* **Pino `SCL` (Col 45):** Jumper U de 4 furos (vermelho/laranja) direto no **pino D22 (coluna 49, fileira `b`)**! Distância de apenas 4 furos!
* **Pino `SDA` (Col 46):** Jumper U de 6 furos (amarelo) direto no **pino D21 (coluna 52, fileira `b`)**! Distância de apenas 6 furos!
* **Pino `CSB` (Col 47):** Desconectado.
* **Pino `SDO` (Col 48):** Jumper U de 2 furos no Barramento 2 (- GND), fixando endereço I2C em `0x76`.

---

## ☀️ Passo 4: Cluster Inferior Analógico ADC1 (LDR e Chuva)

Instalados na **Protoboard Inferior**, colados no ESP32:

### 1. Módulo LDR Azul (Colunas 44 a 47, Fileira `f`):
* **Pino `AO` (Col 44):** Jumper U de 7 furos (amarelo) direto no **pino D34 (coluna 51, fileira `i`)**!
* **Pino `DO` (Col 45):** Desconectado.
* **Pino `GND` (Col 46):** Jumper U de 2 furos no Barramento 3 (- GND).
* **Pino `VCC` (Col 47):** Jumper U de 2 furos no Barramento 3 (+ 3.3V).

### 2. Sensor de Chuva LM393 (Colunas 36 a 39, Fileira `f`):
* **Pino `VCC` (Col 36):** Jumper U de 2 furos no Barramento 3 (+ 3.3V).
* **Pino `GND` (Col 37):** Jumper U de 2 furos no Barramento 3 (- GND).
* **Pino `DO` (Col 38):** Desconectado.
* **Pino `AO` (Col 39):** Jumper U de 13 furos (azul/marrom) direto no **pino D35 (coluna 52, fileira `i`)**!
* **Placa Coletora DSK MH-RD:** Ligada com 2 jumpers fêmea-fêmea nos 2 pinos frontais do comparador.

---

## 💨 Passo 5: Sensor MQ-135 e Divisor Resistivo (5V Exclusivo)

Instalado na **Protoboard Superior** (colunas 16 a 19, fileira `f`), logo ao lado da fonte MB102:
* **`VCC` (Col 16):** Jumper U de 2 furos direto na linha vermelha do **Barramento 1 (5.0V Exclusivo)**.
* **`GND` (Col 17):** Jumper U de 2 furos direto na linha azul do **Barramento 1 (- GND)**.
* **Divisor Resistivo (Colunas 20 a 22):**
  - Resistor de $1\text{ k}\Omega$ liga da coluna 19 (`AO`) à coluna 21 (junção central).
  - Resistor de $2\text{ k}\Omega$ liga da coluna 21 ao Barramento 1 (- GND).
* **Linha de Sinal:** 1 jumper flexível ou rígido longo parte da coluna 21 (saída atenuada a máx 3.33V) e corre limpo pelo canal central até o **pino D32 (coluna 53, fileira `i`)** no ESP32.

---

## 📏 6. Tabela Mestra de Jumpers Rígidos em U (Kit da Bancada)

Mapeamento exato de cada jumper do seu kit para cada ponto do circuito:

| Tamanho / Cor | Alcance | Aplicação Específica no Layout EcoPulse |
| :--- | :---: | :--- |
| **Verde Pequeno** | 2 furos | VCC e GND locais de todos os 5 módulos; alimentação 3V3 e GND do ESP32; aterramento SDO do BMP280. |
| **Laranja** | 3 furos | **OUT do DHT22** (coluna 55) ao **GPIO 4** (coluna 58). Fiação 100% rente! |
| **Vermelho** | 4 a 5 furos | **SCL do BMP280** (coluna 45) ao **GPIO 22** (coluna 49); pontes centrais da coluna 30. |
| **Amarelo** | 6 a 7 furos | **SDA do BMP280** (coluna 46) ao **GPIO 21** (coluna 52); **AO do LDR** (coluna 44) ao **GPIO 34** (coluna 51). |
| **Azul / Marrom** | 10 a 13 furos | **AO do Sensor de Chuva** (coluna 39) ao **GPIO 35** (coluna 52). Linha reta sem arcos aéreos. |
| **Jumpers Longos** | > 15 furos | Pontes verticais de GND Comum e distribuição de 3.3V entre os barramentos 2, 3 e 4. |
| **Jumper Único (Roxo)** | Flexível | Linha de sinal do divisor do MQ-135 (coluna 21) ao GPIO 32 (coluna 53). |
