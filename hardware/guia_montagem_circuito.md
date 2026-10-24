# 📘 Manual Ilustrado de Montagem: Estação Meteorológica IoT com ESP32

Este documento apresenta o guia passo a passo progressivo da montagem física da estação **EcoPulse** em **duas protoboards de 830 pontos acopladas em paralelo**. A metodologia adotada adiciona **um componente por vez**, utilizando diagramas esquemáticos em arte ASCII com coordenadas exatas de furos (colunas e fileiras) e padrão de cores de fiação para eliminar riscos de curtos-circuitos e garantir repetibilidade na bancada.

Documentos complementares de engenharia:
* [Tabela de Pinout Completa](file:///home/wvs/Documents/ccomp-unip/2sem/pim2/ecopulse/hardware/pinout_conexoes.md)
* [Cálculo Matemático dos Divisores de Tensão](file:///home/wvs/Documents/ccomp-unip/2sem/pim2/ecopulse/hardware/calculo_divisores_tensao.md)
* [Lista de Materiais (BOM)](file:///home/wvs/Documents/ccomp-unip/2sem/pim2/ecopulse/hardware/README.md)
* [Foto do Esquemático de Referência](file:///home/wvs/Documents/ccomp-unip/2sem/pim2/ecopulse/hardware/assets/protoboard_esquematico.jpg)

---

## 🛠️ 1. Visão Geral das Coordenadas da Dupla Protoboard

Para seguir as coordenadas com precisão milimétrica, considere as duas protoboards unidas horizontalmente na sua bancada pelas travas plásticas laterais:

```text
+-----------------------------------------------------------------------------------------+
| [+] Barramento 1 (Vermelho) - Configurar Jumper MB102 em 5V (Aquecedor MQ-135)          |
| [-] Barramento 1 (Azul)     - GND Comum                                                 |
+-----------------------------------------------------------------------------------------+
|  Protoboard Superior: Fileiras 'f' a 'j' | Colunas 1 a 63                               |
|  ==================== Canal Central (Divisória) ====================                    |
|  Protoboard Superior: Fileiras 'a' a 'e' | Colunas 1 a 63                               |
+-----------------------------------------------------------------------------------------+
| [+] Barramento 2 (Vermelho) - Configurar Jumper MB102 em 3.3V                           |
| [-] Barramento 2 (Azul)     - GND Comum                                                 |
+-----------------------------------------------------------------------------------------+
| [+] Barramento 3 (Vermelho) - Ponte de 3.3V (Vindo do Barramento 2)                     |
| [-] Barramento 3 (Azul)     - GND Comum                                                 |
+-----------------------------------------------------------------------------------------+
|  Protoboard Inferior: Fileiras 'f' a 'j' | Colunas 1 a 63                               |
|  ==================== Canal Central (Divisória) ====================                    |
|  Protoboard Inferior: Fileiras 'a' a 'e' | Colunas 1 a 63                               |
+-----------------------------------------------------------------------------------------+
| [+] Barramento 4 (Vermelho) - Ponte de 3.3V                                             |
| [-] Barramento 4 (Azul)     - GND Comum                                                 |
+-----------------------------------------------------------------------------------------+
```

> [!WARNING]
> **Atenção Crítica: Pontes da Coluna 30 nas Protoboards de 830 Pontos**  
> Na grande maioria das protoboards de 830 pontos, as trilhas de alimentação positiva (`+`) e negativa (`-`) possuem uma **interrupção física interna bem no centro** (entre as colunas 30 e 33).  
> **Ação obrigatória:** Insira pequenos grampos ou fios jumpers unindo a metade esquerda à metade direita das linhas `+` e `-` em todos os barramentos que você for utilizar além da coluna 30. Sem essas pontes, sensores posicionados à direita da placa não receberão energia!

---

## ⚡ Passo 1: Fonte de Alimentação MB102 e Malha de Energia

O primeiro passo é preparar uma infraestrutura de energia segura e estável:
* **Barramento 1 (5V):** Restrito exclusivamente ao aquecedor cerâmico do sensor de gás MQ-135.
* **Barramentos 2, 3 e 4 (3.3V):** Tensão de operação de toda a lógica do circuito, sensores e ESP32, impedindo sobretensão nas portas analógicas/digitais do microcontrolador.
* **Malha GND Comum:** Todos os trilhos azuis (`-`) interligados, garantindo o mesmo plano de referência (0V).

```text
   [FONTE MB102]
  +-------------+
  | [Jumper:5V] |---> [+] Barramento 1 (Vermelho): 5V EXCLUSIVO (MQ-135)
  |             |---> [-] Barramento 1 (Azul)    : GND ---+
  |  (Proto Sup)|                                         |
  | [Jumper:3V3]|---> [+] Barramento 2 (Vermelho): 3.3V --|--+
  +-------------+---> [-] Barramento 2 (Azul)    : GND ---|--|---+
                                                          |  |   |
                      [+] Barramento 3 (Vermelho): 3.3V <-|--+   | (Fio Preto:
                      [-] Barramento 3 (Azul)    : GND <--+------|  Terra Comum)
                                                                 |
                      [+] Barramento 4 (Vermelho): 3.3V <--------+ (Fio Vermelho: 3.3V)
                      [-] Barramento 4 (Azul)    : GND <---------+ (Fio Preto: GND)
```

### Instruções de Montagem:
1. **Configuração dos Jumpers Amarelos da MB102:**
   - No lado **superior** da fonte, posicione o jumper seletor em **5V**.
   - No lado **inferior** da fonte, posicione o jumper seletor em **3.3V**.
2. **Encaixe da Fonte:** Insira a fonte MB102 na extremidade esquerda da **Protoboard Superior** (colunas `1` a `12`), alinhando os 4 pinos inferiores diretamente nos Barramentos 1 e 2.
3. **Unificação dos Terras (`GND`):** Com fios pretos, conecte:
   - Linha azul (`-`) do Barramento 1 à linha azul (`-`) do Barramento 2.
   - Linha azul (`-`) do Barramento 2 à linha azul (`-`) do Barramento 3.
   - Linha azul (`-`) do Barramento 3 à linha azul (`-`) do Barramento 4.
4. **Distribuição da Tensão de 3.3V:** Com fios vermelhos, conecte:
   - Linha vermelha (`+`) do Barramento 2 à linha vermelha (`+`) do Barramento 3.
   - Linha vermelha (`+`) do Barramento 3 à linha vermelha (`+`) do Barramento 4.

> [!CAUTION]
> **Nunca interligue o Barramento 1 (5V) com os Barramentos 2, 3 ou 4 (3.3V)**. O contato acidental de 5V nas linhas de 3.3V queimará o ESP32 e o sensor BMP280.

---

## 🧠 Passo 2: Posicionamento do Microcontrolador ESP32

Como a placa ESP32 NodeMCU-32S possui largura de 0.9 polegadas (22,8 mm), caso seja espetada no centro de uma única protoboard tradicional, ela cobrirá as colunas adjacentes, inviabilizando a conexão dos jumpers.

Utilizaremos o **espaço divisório entre as duas protoboards**, garantindo **4 furos livres por pino** para conexão dos sinais e alimentação!

```text
Protoboard Superior (Parte Inferior - Fileiras 'a' a 'e'):
Coluna:    1   2   3   4   5   6   7   8  ...  19
Fileira e: [ ] [ ] [ ] [ ] [ ] [ ] [ ] [ ] ... [ ]  <-- 4 furos livres p/ jumpers!
Fileira d: [ ] [ ] [ ] [ ] [ ] [ ] [ ] [ ] ... [ ]
Fileira c: [ ] [ ] [ ] [ ] [ ] [ ] [ ] [ ] ... [ ]
Fileira b: [ ] [ ] [ ] [ ] [ ] [ ] [ ] [ ] ... [ ]
Fileira a: (P) (P) (P) (P) (P) (P) (P) (P) ... (P)  <-- Pinos Superiores do ESP32
           =======================================
           | [USB]      ESP32 DEVKIT             |  <-- Sobre o vão central
           |          (NodeMCU 30 pinos)         |      (Barramentos 2 e 3)
           =======================================
Fileira j: (P) (P) (P) (P) (P) (P) (P) (P) ... (P)  <-- Pinos Inferiores do ESP32
Fileira i: [ ] [ ] [ ] [ ] [ ] [ ] [ ] [ ] ... [ ]
Fileira h: [ ] [ ] [ ] [ ] [ ] [ ] [ ] [ ] ... [ ]
Fileira g: [ ] [ ] [ ] [ ] [ ] [ ] [ ] [ ] ... [ ]
Fileira f: [ ] [ ] [ ] [ ] [ ] [ ] [ ] [ ] ... [ ]  <-- 4 furos livres p/ jumpers!
Protoboard Inferior (Parte Superior - Fileiras 'f' a 'j')
```

### Instruções de Montagem:
1. **Posicionamento Físico:** Encaixe a fileira superior de pinos do ESP32 na fileira **`a`** da Protoboard Superior (colunas `1` a `15` ou `19`, dependendo do modelo de 30 ou 38 pinos), e a fileira inferior de pinos na fileira **`j`** da Protoboard Inferior.
   *(Nota: Se as travas plásticas mantiverem os barramentos 2 e 3 no meio e a distância for excessiva, desencaixe uma das réguas plásticas centrais ou use a Protoboard Inferior com o ESP32 deslocado um furo para cima).*
2. **Alimentação e Aterramento do ESP32:**
   - **GND:** Puxe um jumper preto do pino `GND` do ESP32 para a linha azul (`-`) do **Barramento 4 (GND)**.
   - **3V3:** Puxe um jumper vermelho do pino `3V3` do ESP32 para a linha vermelha (`+`) do **Barramento 4 (3.3V)**. *(Durante o desenvolvimento, se a alimentação vier pelo cabo USB do PC, o pino 3V3 alimentará o circuito; quando na bancada autônoma, a MB102 alimentará o circuito).*

---

## 🌡️ Passo 3: Sensor de Temperatura e Umidade (DHT22 / AM2302)

O módulo DHT22 em plaquinha PCB preta possui 3 pinos serigrafados (`+`, `OUT`/`DAT`, `-`), integrando internamente o resistor de *pull-up* necessário para a linha de comunicação One-Wire.

```text
Protoboard Inferior (Colunas 25, 26, 27):
            +-----------+
            |   DHT22   |
            |  (Branco) |
            +-----------+
              |   |   |    <-- Pinos inseridos na Fileira 'e' (Colunas 25, 26, 27)
Coluna:      25  26  27
Pino:        [+] [OUT][-]
              |    |   |
              |    |   +-----> (Fio Preto)    Ligar no [-] Barramento 4 (GND)
              |    +---------> (Fio Amarelo)  Ligar no pino [GPIO 4] do ESP32
              +--------------> (Fio Vermelho) Ligar no [+] Barramento 4 (3.3V)
```

### Instruções de Conexão:
1. Espete os 3 pinos do DHT22 na **Protoboard Inferior**, fileira **`e`**, ocupando as colunas **`25`**, **`26`** e **`27`**.
2. Conecte os fios nas colunas correspondentes (fileiras `a` a `d`):
   - **Coluna 25 (`+` / VCC):** Jumper vermelho para o **Barramento 4 (`+` 3.3V)**.
   - **Coluna 26 (`OUT` / DATA):** Jumper amarelo diretamente para o **GPIO 4** do ESP32.
   - **Coluna 27 (`-` / GND):** Jumper preto para o **Barramento 4 (`-` GND)**.

---

## 🧭 Passo 4: Sensor de Pressão Atmosférica e Altitude (BMP280)

O sensor Bosch BMP280 (módulo roxo `GY-BMP280-3.3`) comunica-se via barramento **I2C**, oferecendo alta precisão barométrica para cálculo de pressão e altitude.

> [!CAUTION]
> **PERIGO DE QUEIMA:** O BMP280 suporta no máximo 3.6V. Conecte sua alimentação impreterivelmente na malha de **3.3V**.

```text
Protoboard Inferior (Colunas 35 a 40):
         +-------------------------+
         |      GY-BMP280-3.3      |
         |  VCC GND SCL SDA CSB SDO|
         +-------------------------+
             |   |   |   |   |   |   <-- Pinos inseridos na Fileira 'e' (Colunas 35 a 40)
Coluna:     35  36  37  38  39  40
             |   |   |   |       |
             |   |   |   |       +--> (Fio Preto)    Ligar no [-] Barramento 4 (GND) -> Fixa I2C em 0x76
             |   |   |   +----------> (Fio Azul)     Ligar no [GPIO 21 (SDA)] do ESP32
             |   |   +--------------> (Fio Verde)    Ligar no [GPIO 22 (SCL)] do ESP32
             |   +------------------> (Fio Preto)    Ligar no [-] Barramento 4 (GND)
             +----------------------> (Fio Vermelho) Ligar no [+] Barramento 4 (3.3V)
```

### Instruções de Conexão:
1. Insira os 6 pinos do BMP280 na **Protoboard Inferior**, fileira **`e`**, colunas **`35` a `40`**.
2. Faça as ligações nas fileiras livres (`a` a `d`):
   - **Coluna 35 (`VCC`):** Jumper vermelho no **Barramento 4 (`+` 3.3V)**.
   - **Coluna 36 (`GND`):** Jumper preto no **Barramento 4 (`-` GND)**.
   - **Coluna 37 (`SCL`):** Jumper verde no pino **GPIO 22** (I2C SCL) do ESP32.
   - **Coluna 38 (`SDA`):** Jumper azul no pino **GPIO 21** (I2C SDA) do ESP32.
   - **Coluna 39 (`CSB`):** Deixe desconectado (modo I2C habilitado por padrão).
   - **Coluna 40 (`SDO`):** Jumper preto para o **Barramento 4 (`-` GND)**. Essa ligação força o bit menos significativo de endereço para 0, garantindo o endereço I2C fixo em **`0x76`**.

---

## ☀️ Passo 5: Sensor de Luminosidade (Módulo LDR Azul)

O módulo fotossensível com comparador integrado possui 4 pinos (`AO`, `DO`, `GND`, `VCC`). Para medição contínua e analógica da radiação luminosa, utilizaremos a saída `AO` conectada ao canal **ADC1** do ESP32.

```text
Protoboard Superior (Colunas 25 a 28):
         +-------------------+
         |  MÓDULO LDR AZUL  |
         |  AO  DO  GND  VCC |
         +-------------------+
            |   |    |    |    <-- Pinos inseridos na Fileira 'f' (Colunas 25 a 28)
Coluna:    25  26   27   28
            |        |    |
            |        |    +--> (Fio Vermelho) Ligar no [+] Barramento 2 (3.3V)
            |        +-------> (Fio Preto)    Ligar no [-] Barramento 2 (GND)
            +----------------> (Fio Branco)   Ligar no [GPIO 34 (ADC1)] do ESP32
```

### Instruções de Conexão:
1. Insira os 4 pinos do módulo LDR na **Protoboard Superior**, fileira **`f`**, ocupando as colunas **`25` a `28`**.
2. Conecte os jumpers nos furos das fileiras `g` a `j`:
   - **Coluna 28 (`VCC`):** Jumper vermelho no **Barramento 2 (`+` 3.3V)**.
   - **Coluna 27 (`GND`):** Jumper preto no **Barramento 2 (`-` GND)**.
   - **Coluna 26 (`DO`):** Deixar desconectado (saída digital do trimpot não necessária).
   - **Coluna 25 (`AO`):** Jumper branco diretamente no **GPIO 34** do ESP32 (*ADC1_CH6*).

---

## 🌧️ Passo 6: Pluviômetro / Sensor de Chuva (DSK MH-RD)

O sistema de medição pluviométrica opera com duas partes acopladas: a placa sensora de gotas com trilhas niqueladas expostas e o módulo comparador azul.

```text
  [Placa Coletora DSK MH-RD]
        |          |
        +----+ +---+  (2 Jumpers Fêmea-Fêmea, sem polaridade fixa)
             | |
         +---v-v-------------+
         | MÓDULO CHUVA AZUL |
         |  VCC  GND  DO  AO |
         +-------------------+
             |    |   |   |    <-- Pinos inseridos na Fileira 'f' (Colunas 35 a 38)
Coluna:     35   36  37  38
             |    |       |
             |    |       +--> (Fio Laranja)  Ligar no [GPIO 35 (ADC1)] do ESP32
             |    +----------> (Fio Preto)    Ligar no [-] Barramento 2 (GND)
             +---------------> (Fio Vermelho) Ligar no [+] Barramento 2 (3.3V)
```

### Instruções de Conexão:
1. Insira os 4 pinos do módulo comparador na **Protoboard Superior**, fileira **`f`**, colunas **`35` a `38`**.
2. Conecte os jumpers nas fileiras `g` a `j`:
   - **Coluna 35 (`VCC`):** Jumper vermelho no **Barramento 2 (`+` 3.3V)**.
   - **Coluna 36 (`GND`):** Jumper preto no **Barramento 2 (`-` GND)**.
   - **Coluna 37 (`DO`):** Deixar desconectado (ou ligar no GPIO 27 para detecção binária de chuva imediata).
   - **Coluna 38 (`AO`):** Jumper laranja diretamente no **GPIO 35** do ESP32 (*ADC1_CH7*).
3. Conecte os **2 pinos superiores** do módulo azul aos **2 terminais da placa coletora DSK MH-RD** utilizando 2 cabos fêmea-fêmea (não há polaridade positiva ou negativa entre essas duas vias).

---

## 💨 Passo 7: Sensor de Gases e Qualidade do Ar (MQ-135)

O sensor eletroquímico MQ-135 possui um filamento resistivo interno de $\text{SnO}_2$ (dióxido de estanho) que exige **5.0V** contínuos para manter sua temperatura operacional de aquecimento (pre-heating).

```text
Protoboard Superior (Colunas 48 a 51):
         +-------------------+
         |  MQ-135 (Prateado)|
         |  VCC  GND  DO  AO |
         +-------------------+
             |    |   |   |    <-- Pinos inseridos na Fileira 'f' (Colunas 48 a 51)
Coluna:     48   49  50  51
             |    |       |
             |    |       +--> (Fio Roxo)     Ligar no [GPIO 32 (ADC1)] do ESP32 (*)
             |    +----------> (Fio Preto)    Ligar no [-] Barramento 1 (GND)
             +---------------> (Fio Vermelho) Ligar no [+] Barramento 1 (5V EXCLUSIVO)
```

### Instruções de Conexão:
1. Verifique a serigrafia do módulo azul `Flying-Fish` do MQ-135 para identificar os 4 pinos (`VCC`, `GND`, `DO`, `AO`).
2. Insira os 4 pinos na **Protoboard Superior**, fileira **`f`**, colunas **`48` a `51`**.
3. Conecte os fios nas fileiras `g` a `j`:
   - **Coluna 48 (`VCC`):** Jumper vermelho ligado diretamente na linha vermelha (`+`) do **Barramento 1 (5V)**.
   - **Coluna 49 (`GND`):** Jumper preto ligado na linha azul (`-`) do **Barramento 1 (GND)**.
   - **Coluna 50 (`DO`):** Deixar desconectado.
   - **Coluna 51 (`AO`):** Jumper roxo para o **GPIO 32** do ESP32 (*ADC1_CH4*).

> [!TIP]
> **Recomendação de Engenharia com Divisor de Tensão ($1\text{ k}\Omega / 2\text{ k}\Omega$):**  
> Como o MQ-135 é alimentado em 5V, sua saída analógica `AO` pode atingir picos próximos de 5V sob alta concentração de fumaça/gases. Para total proteção do conversor analógico do ESP32, conforme demonstrado em [Cálculo dos Divisores de Tensão](file:///home/wvs/Documents/ccomp-unip/2sem/pim2/ecopulse/hardware/calculo_divisores_tensao.md):  
> Intercale um resistor $R_1 = 1\text{ k}\Omega$ entre o pino `AO` e um nó livre da protoboard, e um resistor $R_2 = 2\text{ k}\Omega$ desse nó para o GND. O sinal atenuado com fator $\frac{2}{3}$ ($5\text{V} \rightarrow 3.33\text{V}$) é então conectado com segurança absoluta ao **GPIO 32**.

---

## 📊 8. Tabela Resumo Consolidada de Fiação e Cores

| Componente | Pino do Sensor | Barramento / Posição | Porta no ESP32 | Cor do Jumper Sugerida | Função Elétrica |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Fonte MB102** | Entrada Sup. / Inf. | Colunas 1 a 12 | — | Pinos MB102 | Fornece 5V (Topo) e 3.3V (Base) |
| **Ponte GND** | Trilhos Azuis | Barr. 1, 2, 3 e 4 | — | Preto | Malha de referência 0V unificada |
| **Ponte 3.3V** | Trilhos Vermelhos | Barr. 2 para 3 e 4 | — | Vermelho | Distribuição lógica segura 3.3V |
| **ESP32** | `GND` / `3V3` | Colunas 1 a 15 | Barr. 4 (-) / Barr. 4 (+) | Preto / Vermelho | Alimentação da CPU |
| **DHT22** | `VCC` / `OUT` / `GND` | Colunas 25, 26, 27 | Barr. 4 (+) / **GPIO 4** / Barr. 4 (-) | Vermelho / Amarelo / Preto | Temperatura e Umidade (One-Wire) |
| **BMP280** | `VCC` / `GND` | Colunas 35 e 36 | Barr. 4 (+) / Barr. 4 (-) | Vermelho / Preto | Alimentação (3.3V máx!) |
| | `SCL` / `SDA` | Colunas 37 e 38 | **GPIO 22** / **GPIO 21** | Verde / Azul | Barramento I2C Padrão |
| | `SDO` | Coluna 40 | Barr. 4 (-) | Preto | Fixa endereço I2C em `0x76` |
| **Módulo LDR** | `VCC` / `GND` | Colunas 28 e 27 | Barr. 2 (+) / Barr. 2 (-) | Vermelho / Preto | Alimentação 3.3V |
| | `AO` | Coluna 25 | **GPIO 34** (ADC1) | Branco | Sinal analógico de luz |
| **Sensor Chuva** | `VCC` / `GND` | Colunas 35 e 36 | Barr. 2 (+) / Barr. 2 (-) | Vermelho / Preto | Alimentação 3.3V |
| | `AO` | Coluna 38 | **GPIO 35** (ADC1) | Laranja | Sinal analógico de precipitação |
| | 2 Vias Placa | Terminais Sup. | Placa DSK MH-RD | 2x Jumpers Fêmea-Fêmea | Detecção de gotas condutivas |
| **MQ-135** | `VCC` / `GND` | Colunas 48 e 49 | **Barr. 1 (+)** / Barr. 1 (-) | Vermelho / Preto | 5.0V exclusivo p/ aquecedor |
| | `AO` | Coluna 51 | **GPIO 32** (ADC1) | Roxo | Sinal analógico de gases |

---

## ✅ 9. Checklist de Segurança Pré-Energização (30 Segundos)

Antes de plugar a fonte MB102 na tomada ou conectar o cabo micro-USB ao notebook, realize esta inspeção visual obrigatória:

- [ ] **Alimentação do BMP280:** O fio vermelho do sensor roxo vai para o Barramento 4 (3.3V) e **jamais** para o Barramento 1 (5V)?
- [ ] **Desobstrução do ESP32:** O ESP32 possui furos livres em ambas as laterais para conexões sem perigo de curto entre fileiras opostas?
- [ ] **Pontes Centrais da Coluna 30:** Seus jumpers de continuidade entre a metade esquerda e direita dos barramentos estão instalados?
- [ ] **GND Comum Unificado:** Todos os trilhos azuis (`-`) dos Barramentos 1, 2, 3 e 4 estão conectados com fios pretos de interligação?
- [ ] **Exclusividade do Barramento 1:** O pino `VCC` do MQ-135 é o **único** componente conectado ao Barramento 1 de 5V?
- [ ] **Pinos Analógicos Confinados ao ADC1:** As três entradas analógicas estão conectadas exclusivamente nos GPIOs 32, 34 e 35 (imunes ao rádio Wi-Fi)?

Uma vez aprovado o checklist, o circuito pode ser energizado com total segurança para os primeiros testes de telemetria!
