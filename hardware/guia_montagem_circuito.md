# Guia Passo a Passo de Montagem do Circuito

Este manual detalha o procedimento prático de montagem em bancada do circuito da estação **EcoPulse**, utilizando protoboards, fonte MB102, ESP32 e os sensores especificados no projeto.

---

## 1. Princípios Básicos e Segurança Elétrica

> [!WARNING]
> O microcontrolador ESP32 opera com nível lógico de **3.3V**. Aplicar tensões superiores a 3.6V em seus pinos GPIO causará danos irreversíveis ao chip. Siga rigorosamente as instruções de divisor de tensão para o sensor MQ-135.

1. **Montagem sem Solda:** O circuito foi concebido para ser montado em protoboards através de jumpers, dispensando solda direta na placa de ensaio.
2. **GND Comum (Referência Elétrica Única):** Todos os terminais negativos (GND da fonte MB102, GND do ESP32 e GNDs dos módulos de sensores) **devem** estar interligados no mesmo barramento negativo.
3. **Desligamento Prévio:** Mantenha a fonte MB102 desligada da tomada e da porta USB durante todo o processo de inserção dos componentes e fios.

---

## 2. Passo a Passo da Montagem

### Etapa 1: Preparação e Acoplamento das Protoboards
1. Pegue as duas protoboards de 830 pontos e una-as lado a lado utilizando as travas plásticas macho-fêmea presentes nas laterais.
2. Essa união fornece espaço suficiente para acomodar o ESP32 de um lado e distribuir os 5 módulos de sensores no outro, mantendo a fiação limpa e desobstruída.

---

### Etapa 2: Instalação e Configuração da Fonte MB102
1. Encaixe a fonte MB102 na extremidade superior da protoboard, alinhando os pinos metálicos com os trilhos laterais de alimentação.
2. **Configuração dos Jumpers de Tensão da MB102:**
   * **Lado A (Trilho Superior):** Posicione o jumper seletor em **3.3V**. Este barramento alimentará o ESP32 e os sensores lógicos de 3.3V.
   * **Lado B (Trilho Inferior):** Posicione o jumper seletor em **5.0V**. Este barramento fornecerá corrente estável ao elemento de aquecimento interno do sensor MQ-135.
3. **Interligação de GND:** Use um jumper macho-macho para ligar o trilho azul/preto (GND) do Lado A ao trilho azul/preto (GND) do Lado B.

---

### Etapa 3: Posicionamento do Microcontrolador ESP32
1. Insira o ESP32 na Protoboard 1, montando-o transversalmente sobre a ranhura central divisória.
2. Conecte o pino **GND** do ESP32 ao trilho negativo (GND comum).
3. Se estiver alimentando o ESP32 pela fonte MB102 externa: conecte o trilho de **3.3V** ao pino `3V3` do ESP32 (ou o trilho de **5V** ao pino `VIN` do ESP32).

---

### Etapa 4: Montagem do Sensor BMP280 (Pressão e Altitude)
O BMP280 utiliza o barramento digital I2C:
1. Conecte o pino **VCC** do BMP280 ao trilho **3.3V**.
2. Conecte o pino **GND** do BMP280 ao trilho **GND**.
3. Conecte o pino **SCL** ao **GPIO 22** do ESP32.
4. Conecte o pino **SDA** ao **GPIO 21** do ESP32.
5. Os pinos *CSB* e *SDO* devem permanecer desconectados (o que fixa o endereço I2C em `0x76`).

---

### Etapa 5: Montagem do Sensor DHT22 (Temperatura e Umidade)
1. Conecte o pino **VCC** do DHT22 ao trilho **3.3V**.
2. Conecte o pino **GND** do DHT22 ao trilho **GND**.
3. Conecte o pino **DATA / OUT** ao **GPIO 4** do ESP32.
4. Se o DHT22 for o modelo avulso de 4 pinos (sem placa PCB embutida): insira um **resistor de 10 kΩ** entre o pino 1 (VCC) e o pino 2 (DATA) para atuar como *pull-up*. Caso seja o módulo em plaquinha azul de 3 pinos, o resistor já vem soldado internamente.

---

### Etapa 6: Montagem do Sensor de Luminosidade (LDR)
1. Insira o LDR e um **resistor de 10 kΩ** na protoboard:
   * Conecte um dos terminais do LDR ao trilho **3.3V**.
   * Conecte o segundo terminal do LDR à mesma linha de um dos terminais do resistor de 10 kΩ.
   * Conecte o outro terminal do resistor de 10 kΩ ao trilho **GND**.
2. Da junção intermediária entre o LDR e o resistor de 10 kΩ, puxe um jumper para o **GPIO 34** (ADC1) do ESP32.

---

### Etapa 7: Montagem do Sensor de Chuva Montimport
1. O sensor de chuva possui duas partes: a placa condutora de gotas e o módulo comparador LM393.
2. Interligue os 2 pinos da placa de gotas aos 2 pinos de entrada do módulo comparador usando jumpers macho-fêmea.
3. Conecte o pino **VCC** do módulo comparador ao trilho **3.3V**.
4. Conecte o pino **GND** ao trilho **GND**.
5. Conecte o pino **AO** (Saída Analógica) ao **GPIO 35** (ADC1) do ESP32. (O pino digital *DO* pode permanecer desconectado).

---

### Etapa 8: Montagem do Sensor MQ-135 e Divisor Resistivo de Proteção
O sensor MQ-135 necessita de 5V para o aquecedor cerâmico, gerando um sinal de 0 a 5V que precisa ser atenuado:
1. Conecte o pino **VCC** do MQ-135 ao trilho **5.0V** da fonte MB102.
2. Conecte o pino **GND** ao trilho **GND**.
3. Da saída **AO** do sensor, conecte a um resistor $R_1$ de **1 kΩ**.
4. Conecte a outra ponta do resistor $R_1$ a uma linha livre da protoboard.
5. Nessa mesma linha livre, conecte um resistor $R_2$ de **2 kΩ**, cuja outra extremidade vai para o **GND**.
6. Dessa mesma junção entre $R_1$ e $R_2$, puxe um jumper para o **GPIO 32** (ADC1) do ESP32.

---

## 3. Checklist de Validação Pré-Energização

Antes de plugar a fonte de energia ou o cabo USB:
* [ ] Os trilhos de 3.3V e 5.0V estão estritamente separados na fonte MB102?
* [ ] O GND de todos os sensores, fonte e ESP32 estão em comum?
* [ ] O pino de saída do MQ-135 está passando pelo divisor 1kΩ / 2kΩ antes de chegar ao pino 32?
* [ ] Nenhum jumper de alimentação está conectado em curto entre trilho positivo e negativo?
* [ ] Com um multímetro na escala de continuidade/diodo, verifique ausência de curto entre VCC e GND.
