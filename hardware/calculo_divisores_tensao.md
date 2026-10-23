# Cálculos e Engenharia dos Circuitos Passivos

Este documento formaliza as equações matemáticas, princípios de eletrônica e critérios de dimensionamento para os componentes passivos (resistores e divisores de tensão) implementados na estação **EcoPulse**.

---

## 1. Fundamentação Teórica: O Divisor Resistivo de Tensão

Um divisor de tensão é um circuito formado por dois resistores em série ($R_1$ e $R_2$) capaz de atenuar uma tensão de entrada ($V_{in}$) para um valor proporcionalmente menor ($V_{out}$), conforme a lei de Ohm:

$$V_{out} = V_{in} \times \frac{R_2}{R_1 + R_2}$$

---

## 2. Dimensionamento para o Sensor de Gases MQ-135

### O Problema da Incompatibilidade de Níveis Lógicos
* O sensor MQ-135 requer **5.0V** para aquecer a camada de óxido de estanho ($\text{SnO}_2$) até a temperatura em que o gás atmosférico reage quimicamente.
* Por conseguinte, a tensão na saída analógica (**AO**) pode alcançar até **5.0V** quando exposto a altas concentrações de fumaça ou gases combustíveis.
* Os conversores analógico-digitais (ADC) do microcontrolador ESP32 têm tensão de operação de **0 a 3.3V**. Aplicar 5.0V em um pino GPIO provocará a saturação do canal e a degradação física dos transistores internos.

### A Solução por Divisor Resistivo
Escolhemos valores comerciais e acessíveis com proporção de $1:2$:
* Resistor Superior ($R_1$): **$1.0\text{ k}\Omega$** (1000 ohms)
* Resistor Inferior ($R_2$): **$2.0\text{ k}\Omega$** (2000 ohms)

Substituindo na equação para o pior caso ($V_{in} = 5.0\text{ V}$):

$$V_{out} = 5.0\text{ V} \times \frac{2000}{1000 + 2000} = 5.0\text{ V} \times \frac{2}{3} \approx 3.33\text{ V}$$

Como a tensão máxima atenuada atinge exatamente a faixa de segurança do ESP32, o ADC fica protegido contra sobretensão.

### Reconstituição da Tensão Real no Software
Para que o software conheça a tensão original gerada pelo sensor antes da atenuação, aplicamos o inverso da razão do divisor:

$$\text{Razão do Divisor} = \frac{R_1 + R_2}{R_2} = \frac{1000 + 2000}{2000} = 1.5$$

$$V_{\text{sensor}} = V_{\text{medida\_pino}} \times 1.5$$

---

## 3. Circuito Divisor de Tensão do Fotoresistor (LDR)

O LDR (Light Dependent Resistor) varia sua resistência interna inversamente à luz incidente:
* **Escuridão Total:** Resistência extremamente alta ($R_{\text{LDR}} \approx 100\text{ k}\Omega \text{ a } 1\text{ M}\Omega$).
* **Luz Plena / Solar:** Resistência reduzida ($R_{\text{LDR}} \approx 1\text{ k}\Omega \text{ a } 5\text{ k}\Omega$).

Para converter essa variação de resistência em uma variação de tensão mensurável pelo ADC do ESP32, montamos um divisor de tensão com um resistor fixo de referência:
* Resistor de Carga ($R_{\text{fixo}}$): **$10\text{ k}\Omega$**
* Conexão: LDR ligado ao barramento de **3.3V**; Resistor de $10\text{ k}\Omega$ ligado ao **GND**; Junção intermediária ligada ao **GPIO 34**.

A tensão entregue ao pino GPIO 34 é expressa por:

$$V_{\text{GPIO34}} = 3.3\text{ V} \times \frac{10\text{ k}\Omega}{R_{\text{LDR}} + 10\text{ k}\Omega}$$

* Sob luz intensa ($R_{\text{LDR}} \to 1\text{ k}\Omega$), $V_{\text{GPIO34}} \approx 3.0\text{ V}$ (leitura ADC alta, indicando alta luminosidade).
* No escuro ($R_{\text{LDR}} \to 100\text{ k}\Omega$), $V_{\text{GPIO34}} \approx 0.3\text{ V}$ (leitura ADC baixa).

---

## 4. Resistor de Pull-Up do Barramento do DHT22

O sensor digital DHT22 adota um protocolo de comunicação proprietário assíncrono sobre um único condutor (*One-Wire / Single-Bus*):
* A linha de dados opera em modo coletor aberto (*open-drain*).
* Na ausência de transmissão, a linha deve ser mantida em nível lógico alto (**3.3V**).
* Para isso, utiliza-se um resistor de **$10\text{ k}\Omega$** conectado entre o pino **VCC (3.3V)** e o pino **DATA (GPIO 4)**.
* Esse resistor garante tempos de subida de sinal (*rise-time*) nítidos, evitando oscilações ou ruídos que corrompam os pulsos digitais enviados pelo sensor.
