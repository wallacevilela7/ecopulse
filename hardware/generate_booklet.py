import os
import base64
import subprocess

BASE_DIR = "/home/wvs/Documents/ccomp-unip/2sem/pim2/ecopulse/hardware"
IMG_PATH = os.path.join(BASE_DIR, "assets", "protoboard_esquematico.jpg")
HTML_OUT = os.path.join(BASE_DIR, "manual_montagem_ecopulse.html")
PDF_OUT = os.path.join(BASE_DIR, "manual_montagem_ecopulse.pdf")

# Read and encode base64 image
with open(IMG_PATH, "rb") as f:
    img_b64 = base64.b64encode(f.read()).decode("utf-8")

html_content = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<title>Manual Ilustrado de Montagem - EcoPulse</title>
<style>
  @page {
    size: A4 portrait;
    margin: 12mm 14mm 12mm 14mm;
  }

  * {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
  }

  body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    color: #1e293b;
    background-color: #ffffff;
    font-size: 9.3pt;
    line-height: 1.42;
  }

  /* Page Break Utilities */
  .page {
    page-break-after: always;
    height: 100%;
    position: relative;
    padding-bottom: 26px;
  }

  .page:last-child {
    page-break-after: avoid;
  }

  .page-footer {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-top: 1px solid #cbd5e1;
    padding-top: 4px;
    font-size: 7.5pt;
    color: #64748b;
  }

  /* Cover Page */
  .cover-container {
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    height: 980px;
    padding: 40px 30px;
    background: linear-gradient(145deg, #0f172a 0%, #1e293b 60%, #064e3b 100%);
    color: #ffffff;
    border-radius: 12px;
  }

  .cover-header {
    border-bottom: 2px solid #10b981;
    padding-bottom: 15px;
  }

  .cover-institution {
    font-size: 11pt;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #94a3b8;
    font-weight: 600;
  }

  .cover-course {
    font-size: 13pt;
    color: #38bdf8;
    font-weight: 700;
    margin-top: 4px;
  }

  .cover-body {
    margin: auto 0;
  }

  .cover-badge {
    display: inline-block;
    background: rgba(16, 185, 129, 0.2);
    border: 1px solid #10b981;
    color: #34d399;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 9pt;
    font-weight: 600;
    margin-bottom: 15px;
  }

  .cover-title {
    font-size: 26pt;
    font-weight: 800;
    line-height: 1.15;
    color: #ffffff;
    margin-bottom: 12px;
  }

  .cover-subtitle {
    font-size: 13pt;
    color: #cbd5e1;
    font-weight: 400;
    max-width: 90%;
    line-height: 1.4;
  }

  .cover-specs {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 12px;
    margin-top: 35px;
    background: rgba(15, 23, 42, 0.6);
    padding: 16px;
    border-radius: 8px;
    border: 1px solid #334155;
  }

  .spec-item {
    border-left: 3px solid #10b981;
    padding-left: 10px;
  }

  .spec-label {
    font-size: 7.5pt;
    text-transform: uppercase;
    color: #94a3b8;
    letter-spacing: 0.5px;
  }

  .spec-value {
    font-size: 10pt;
    font-weight: 700;
    color: #f8fafc;
    margin-top: 2px;
  }

  .cover-footer {
    border-top: 1px solid #334155;
    padding-top: 15px;
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
    font-size: 8.5pt;
    color: #94a3b8;
  }

  /* Typography and Layout */
  h1.section-title {
    font-size: 14pt;
    font-weight: 800;
    color: #0f172a;
    border-left: 5px solid #059669;
    padding-left: 10px;
    margin-bottom: 10px;
    display: flex;
    align-items: center;
    gap: 8px;
  }

  h2.step-title {
    font-size: 11.5pt;
    font-weight: 700;
    color: #0f172a;
    margin-top: 8px;
    margin-bottom: 5px;
    display: flex;
    align-items: center;
    gap: 6px;
  }

  p {
    margin-bottom: 6px;
    color: #334155;
  }

  /* Callout Boxes */
  .callout {
    border-radius: 6px;
    padding: 7px 11px;
    margin: 6px 0;
    font-size: 8.3pt;
    line-height: 1.38;
    border-left: 4px solid;
  }

  .callout-warning {
    background-color: #fffbeb;
    border-color: #f59e0b;
    color: #92400e;
  }

  .callout-danger {
    background-color: #fef2f2;
    border-color: #ef4444;
    color: #991b1b;
  }

  .callout-tip {
    background-color: #ecfdf5;
    border-color: #10b981;
    color: #065f46;
  }

  .callout-info {
    background-color: #f0f9ff;
    border-color: #0284c7;
    color: #075985;
  }

  /* ASCII Diagram Box */
  pre.ascii-box {
    background-color: #0f172a;
    color: #38bdf8;
    font-family: "Consolas", "Fira Code", monospace;
    font-size: 7.0pt;
    line-height: 1.22;
    padding: 7px 9px;
    border-radius: 6px;
    border: 1px solid #1e293b;
    margin: 5px 0;
    overflow: hidden;
    white-space: pre;
  }

  /* Lists */
  ul.step-instructions {
    list-style: none;
    margin: 5px 0;
  }

  ul.step-instructions li {
    position: relative;
    padding-left: 16px;
    margin-bottom: 3.5px;
    font-size: 8.6pt;
    color: #1e293b;
  }

  ul.step-instructions li::before {
    content: "•";
    color: #059669;
    font-weight: bold;
    font-size: 11pt;
    position: absolute;
    left: 4px;
    top: -2px;
  }

  /* Pin Badge */
  .badge-pin {
    display: inline-block;
    padding: 1px 5px;
    border-radius: 4px;
    font-family: monospace;
    font-size: 7.8pt;
    font-weight: 700;
  }
  .badge-gpio { background: #e0e7ff; color: #3730a3; }
  .badge-3v3  { background: #dcfce7; color: #166534; }
  .badge-5v   { background: #ffedd5; color: #9a3412; }
  .badge-gnd  { background: #f1f5f9; color: #475569; border: 1px solid #cbd5e1; }
  .badge-adc  { background: #f3e8ff; color: #6b21a8; }

  /* Tables */
  table.tech-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 8.0pt;
    margin: 6px 0;
  }

  table.tech-table th {
    background-color: #0f172a;
    color: #f8fafc;
    text-align: left;
    padding: 5px 7px;
    font-weight: 600;
    font-size: 7.8pt;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  table.tech-table td {
    padding: 4.5px 7px;
    border-bottom: 1px solid #e2e8f0;
    color: #334155;
  }

  table.tech-table tr:nth-child(even) td {
    background-color: #f8fafc;
  }

  /* Checkbox Checklist */
  .checklist-item {
    display: flex;
    align-items: flex-start;
    gap: 8px;
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    padding: 5px 8px;
    border-radius: 5px;
    margin-bottom: 5px;
    font-size: 8.3pt;
  }

  .checkbox-box {
    width: 13px;
    height: 13px;
    border: 2px solid #059669;
    border-radius: 3px;
    flex-shrink: 0;
    margin-top: 2px;
  }

  .card-box {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 7px;
    padding: 8px 10px;
  }

  .img-container {
    text-align: center;
    margin: 8px 0;
  }

  .img-container img {
    max-width: 95%;
    max-height: 230px;
    border-radius: 8px;
    border: 1px solid #cbd5e1;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  }

  .img-caption {
    font-size: 7.3pt;
    color: #64748b;
    margin-top: 3px;
    font-style: italic;
  }
</style>
</head>
<body>

<!-- ================= PAGE 1: CAPA ================= -->
<div class="page">
  <div class="cover-container">
    <div class="cover-header">
      <div class="cover-institution">Universidade Paulista — UNIP</div>
      <div class="cover-course">Bacharelado em Ciência da Computação</div>
    </div>

    <div class="cover-body">
      <div class="cover-badge">PIM II & Projeto Dirigido II • Smart Campus IoT</div>
      <h1 class="cover-title">Manual Ilustrado<br>de Montagem de Bancada</h1>
      <p class="cover-subtitle">
        Guia passo a passo de engenharia física para montagem da Estação Meteorológica EcoPulse em matriz de dupla protoboard (830 pontos), com microcontrolador ESP32 e 5 transdutores ambientais.
      </p>

      <div class="cover-specs">
        <div class="spec-item">
          <div class="spec-label">Processamento</div>
          <div class="spec-value">ESP32 NodeMCU (30 pinos)</div>
        </div>
        <div class="spec-item">
          <div class="spec-label">Alimentação</div>
          <div class="spec-value">Fonte MB102 (5V & 3.3V)</div>
        </div>
        <div class="spec-item">
          <div class="spec-label">Malha Sensorial</div>
          <div class="spec-value">5 Sensores Multigrandezas</div>
        </div>
      </div>
    </div>

    <div class="cover-footer">
      <div>
        <strong>Projeto EcoPulse</strong> • Repositório Oficial<br>
        Documento Homologado de Engenharia Eletrônica
      </div>
      <div style="text-align: right;">
        <strong>Campus São Paulo / SP</strong><br>
        Semestre 2 / Outubro de 2026
      </div>
    </div>
  </div>
</div>

<!-- ================= PAGE 2: BOM & FOTO PROTÓTIPO ================= -->
<div class="page">
  <h1 class="section-title">📋 1. Especificações Técnicas e Lista de Materiais (BOM)</h1>
  <p>
    A estação meteorológica <strong>EcoPulse</strong> foi projetada segundo rigorosos critérios de segurança elétrica e modularidade, permitindo testes, calibração e substituição ágil de sensores em bancada sem a necessidade de soldagem direta.
  </p>

  <table class="tech-table">
    <thead>
      <tr>
        <th>Item</th>
        <th>Componente / Modelo</th>
        <th>Qtd.</th>
        <th>Tensão Operacional</th>
        <th>Finalidade no Projeto EcoPulse</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>01</strong></td>
        <td>ESP32 NodeMCU-32S (30 pinos)</td>
        <td>1</td>
        <td><span class="badge-pin badge-3v3">3.3V (VCC) / 5V (VIN)</span></td>
        <td>Microcontrolador mestre, Wi-Fi 2.4GHz, leituras ADC e I2C</td>
      </tr>
      <tr>
        <td><strong>02</strong></td>
        <td>Módulo Fonte Protoboard MB102</td>
        <td>1</td>
        <td><span class="badge-pin badge-5v">5.0V</span> / <span class="badge-pin badge-3v3">3.3V</span></td>
        <td>Isolamento galvânico e barramentos duplos de alimentação</td>
      </tr>
      <tr>
        <td><strong>03</strong></td>
        <td>Protoboard Transparente/Branca 830 Pts</td>
        <td>2</td>
        <td>—</td>
        <td>Acopladas horizontalmente para matriz física de conexões</td>
      </tr>
      <tr>
        <td><strong>04</strong></td>
        <td>Sensor DHT22 / AM2302 (Placa Preta)</td>
        <td>1</td>
        <td><span class="badge-pin badge-3v3">3.3V</span></td>
        <td>Temperatura ambiente (-40°C a +80°C) e Umidade (0 a 100%)</td>
      </tr>
      <tr>
        <td><strong>05</strong></td>
        <td>Sensor Barométrico BMP280 (Roxo)</td>
        <td>1</td>
        <td><span class="badge-pin badge-3v3">3.3V (Estrito!)</span></td>
        <td>Pressão atmosférica (300 a 1100 hPa) e estimativa de altitude</td>
      </tr>
      <tr>
        <td><strong>06</strong></td>
        <td>Módulo LDR com Comparador (Azul)</td>
        <td>1</td>
        <td><span class="badge-pin badge-3v3">3.3V</span></td>
        <td>Índice de radiação luminosa ambiente via saída analógica AO</td>
      </tr>
      <tr>
        <td><strong>07</strong></td>
        <td>Sensor de Chuva DSK MH-RD + Placa</td>
        <td>1</td>
        <td><span class="badge-pin badge-3v3">3.3V</span></td>
        <td>Detecção de precipitação pluviométrica por condutividade</td>
      </tr>
      <tr>
        <td><strong>08</strong></td>
        <td>Sensor MQ-135 Flying-Fish (Ar/Gases)</td>
        <td>1</td>
        <td><span class="badge-pin badge-5v">5.0V (Aquecedor)</span></td>
        <td>Detecção de NH3, NOx, álcool, benzeno, fumaça e CO2</td>
      </tr>
      <tr>
        <td><strong>09</strong></td>
        <td>Resistores 1 kΩ e 2 kΩ (1/4W 5%)</td>
        <td>1+1</td>
        <td>—</td>
        <td>Divisor de tensão atenuador 5V → 3.3V para saída do MQ-135</td>
      </tr>
      <tr>
        <td><strong>10</strong></td>
        <td>Jumpers Macho-Macho & Fêmea-Fêmea</td>
        <td>~35</td>
        <td>—</td>
        <td>Fiação estruturada codificada por cores</td>
      </tr>
    </tbody>
  </table>

  <div class="img-container">
    <img src="data:image/jpeg;base64,__IMG_B64__" alt="Esquemático Protoboard">
    <div class="img-caption">Figura 1.1: Visão superior da montagem física na bancada de ensaios com dupla protoboard acoplada.</div>
  </div>

  <div class="callout callout-info">
    <strong>Arquitetura das Linhas de Conversão Analógica (ADC):</strong> Todos os sensores analógicos (LDR, Chuva e MQ-135) foram obrigatoriamente alocados no <strong>ADC1 do ESP32</strong> (canais GPIO 32, 34 e 35). Essa decisão de engenharia impede travamentos ou ruídos causados pelo rádio Wi-Fi, o qual compartilha hardware com o ADC2.
  </div>

  <div class="page-footer">
    <span>EcoPulse — Estação Meteorológica IoT (UNIP PIM II)</span>
    <span>Página 2</span>
  </div>
</div>

<!-- ================= PAGE 3: TOPOGRAFIA & PASSO 1 ================= -->
<div class="page">
  <h1 class="section-title">🗺️ 2. Topografia das Coordenadas da Dupla Protoboard</h1>
  <p>
    Para evitar qualquer erro na inserção de componentes e jumpers, considere as duas protoboards de 830 pontos acopladas horizontalmente na sua bancada (Superior e Inferior):
  </p>

  <pre class="ascii-box">
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
  </pre>

  <div class="callout callout-warning">
    <strong>Aviso Crítico (Interrupção na Coluna 30):</strong> Nas protoboards de 830 pontos, as trilhas de alimentação lateral possuem um corte interno entre as colunas 30 e 33. Coloque pequenos grampos jumpers unindo a metade esquerda à metade direita nas linhas vermelhas e azuis de todos os barramentos utilizados.
  </div>

  <h2 class="step-title">⚡ Passo 1: Fonte MB102 e Malha de Distribuição de Energia</h2>
  <p>
    A fonte MB102 permite gerar tensões simultâneas de <strong>5.0V</strong> (essencial para o sensor MQ-135) e <strong>3.3V</strong> (tensão limite suportada pelo ESP32 e sensor BMP280).
  </p>

  <pre class="ascii-box">
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
  </pre>

  <ul class="step-instructions">
    <li><strong>Ajuste dos Jumpers da MB102:</strong> Posicione o jumper amarelo do lado <em>superior</em> em <strong>5V</strong> e o do lado <em>inferior</em> em <strong>3.3V</strong>.</li>
    <li><strong>Fixação na Protoboard:</strong> Espete os 4 pinos inferiores da MB102 na extremidade esquerda da Protoboard Superior (colunas 1 a 12), encaixando nos Barramentos 1 e 2.</li>
    <li><strong>Ponte de GND Comum (Fios Pretos):</strong> Interligue todos os trilhos azuis: Barramento 1 (-) com Barramento 2 (-), Barramento 2 (-) com Barramento 3 (-), e Barramento 3 (-) com Barramento 4 (-).</li>
    <li><strong>Distribuição de 3.3V (Fios Vermelhos):</strong> Conecte a linha vermelha do Barramento 2 (+) ao Barramento 3 (+) e deste para o Barramento 4 (+). <em>Nunca conecte o Barramento 1 aos demais barramentos vermelhos!</em></li>
  </ul>

  <div class="page-footer">
    <span>EcoPulse — Estação Meteorológica IoT (UNIP PIM II)</span>
    <span>Página 3</span>
  </div>
</div>

<!-- ================= PAGE 4: PASSO 2 & PASSO 3 ================= -->
<div class="page">
  <h1 class="section-title">🔌 3. Instalação do Processador e Sensor DHT22</h1>

  <h2 class="step-title">🧠 Passo 2: Posicionamento Estratégico do ESP32 NodeMCU</h2>
  <p>
    Devido à largura do módulo ESP32, se ele for inserido no meio de apenas uma protoboard, todos os furos de uma das laterais ficam cobertos. Utilizando o <strong>vão central entre as duas protoboards</strong>, garantimos <strong>4 furos livres por pino</strong> para fiação organizada.
  </p>

  <pre class="ascii-box">
Protoboard Superior (Parte Inferior - Fileiras 'a' a 'e'):
Coluna:    1   2   3   4   5   6   7   8  ...  15
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
  </pre>

  <ul class="step-instructions">
    <li><strong>Inserção Física:</strong> Espete os pinos superiores do ESP32 na fileira <strong>`a`</strong> da Protoboard Superior (colunas 1 a 15) e os inferiores na fileira <strong>`j`</strong> da Protoboard Inferior.</li>
    <li><strong>Conexão de Aterramento:</strong> Ligue um jumper preto do pino <span class="badge-pin badge-gnd">GND</span> do ESP32 ao Barramento 4 (-).</li>
    <li><strong>Conexão de Alimentação:</strong> Ligue um jumper vermelho do pino <span class="badge-pin badge-3v3">3V3</span> do ESP32 ao Barramento 4 (+). <em>(Em bancada conectada ao PC, a USB alimenta o ESP32 e distribui 3.3V ao circuito).</em></li>
  </ul>

  <hr style="border: 0; border-top: 1px dashed #cbd5e1; margin: 10px 0;">

  <h2 class="step-title">🌡️ Passo 3: Sensor de Temperatura e Umidade (DHT22)</h2>
  <p>
    O módulo DHT22 em plaquinha PCB preta possui 3 pinos: alimentação positiva, terra e sinal One-Wire. O resistor de <em>pull-up</em> já está soldado internamente na placa.
  </p>

  <pre class="ascii-box">
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
  </pre>

  <ul class="step-instructions">
    <li><strong>Posicionamento:</strong> Espete os 3 pinos na <strong>Protoboard Inferior</strong>, fileira <strong>`e`</strong>, colunas <strong>25</strong>, <strong>26</strong> e <strong>27</strong>.</li>
    <li><strong>Coluna 25 (`+` / VCC):</strong> Ligue com jumper vermelho no <span class="badge-pin badge-3v3">Barramento 4 (3.3V)</span>.</li>
    <li><strong>Coluna 26 (`OUT` / DAT):</strong> Ligue com jumper amarelo diretamente no <span class="badge-pin badge-gpio">GPIO 4 (D4)</span> do ESP32.</li>
    <li><strong>Coluna 27 (`-` / GND):</strong> Ligue com jumper preto no <span class="badge-pin badge-gnd">Barramento 4 (GND)</span>.</li>
  </ul>

  <div class="page-footer">
    <span>EcoPulse — Estação Meteorológica IoT (UNIP PIM II)</span>
    <span>Página 4</span>
  </div>
</div>

<!-- ================= PAGE 5: PASSO 4 & PASSO 5 ================= -->
<div class="page">
  <h1 class="section-title">📡 4. Barramento I2C (BMP280) e Sensor de Luz (LDR)</h1>

  <h2 class="step-title">🧭 Passo 4: Sensor de Pressão Atmosférica e Altitude (BMP280)</h2>
  <p>
    O módulo roxo <strong>GY-BMP280-3.3</strong> opera via comunicação digital I2C. Requer apenas duas linhas de clock/dados (<span class="badge-pin badge-gpio">SCL</span> e <span class="badge-pin badge-gpio">SDA</span>) e medição de alta precisão barométrica.
  </p>

  <div class="callout callout-danger">
    <strong>ALERTA DE TENSÃO MÁXIMA:</strong> O chip Bosch BMP280 queima instantaneamente se submetido a 5V. Ligue-o <strong>exclusivamente</strong> nos barramentos de 3.3V.
  </div>

  <pre class="ascii-box">
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
  </pre>

  <ul class="step-instructions">
    <li><strong>Posicionamento:</strong> Espete os 6 pinos na <strong>Protoboard Inferior</strong>, fileira <strong>`e`</strong>, colunas <strong>35 a 40</strong>.</li>
    <li><strong>Coluna 35 (VCC):</strong> Jumper vermelho no <span class="badge-pin badge-3v3">Barramento 4 (3.3V)</span>.</li>
    <li><strong>Coluna 36 (GND):</strong> Jumper preto no <span class="badge-pin badge-gnd">Barramento 4 (GND)</span>.</li>
    <li><strong>Coluna 37 (SCL):</strong> Jumper verde ligado diretamente ao <span class="badge-pin badge-gpio">GPIO 22</span> do ESP32.</li>
    <li><strong>Coluna 38 (SDA):</strong> Jumper azul ligado diretamente ao <span class="badge-pin badge-gpio">GPIO 21</span> do ESP32.</li>
    <li><strong>Coluna 39 (CSB):</strong> Deixar desconectado (mantém modo I2C ativado).</li>
    <li><strong>Coluna 40 (SDO):</strong> Jumper preto ligado ao <span class="badge-pin badge-gnd">GND</span>. Fixa o endereço do sensor em <code>0x76</code>.</li>
  </ul>

  <hr style="border: 0; border-top: 1px dashed #cbd5e1; margin: 10px 0;">

  <h2 class="step-title">☀️ Passo 5: Módulo Sensor de Luminosidade (LDR Azul)</h2>
  <p>
    O módulo LDR com comparador LM393 permite leitura contínua da luz solar incidente por meio da sua porta analógica <span class="badge-pin badge-adc">AO</span>.
  </p>

  <pre class="ascii-box">
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
  </pre>

  <ul class="step-instructions">
    <li><strong>Posicionamento:</strong> Espete os 4 pinos na <strong>Protoboard Superior</strong>, fileira <strong>`f`</strong>, colunas <strong>25 a 28</strong>.</li>
    <li><strong>Coluna 28 (VCC):</strong> Jumper vermelho no <span class="badge-pin badge-3v3">Barramento 2 (3.3V)</span>.</li>
    <li><strong>Coluna 27 (GND):</strong> Jumper preto no <span class="badge-pin badge-gnd">Barramento 2 (GND)</span>.</li>
    <li><strong>Coluna 26 (DO):</strong> Deixar desconectado.</li>
    <li><strong>Coluna 25 (AO):</strong> Jumper branco conectado ao <span class="badge-pin badge-adc">GPIO 34 (D34 - ADC1)</span> do ESP32.</li>
  </ul>

  <div class="page-footer">
    <span>EcoPulse — Estação Meteorológica IoT (UNIP PIM II)</span>
    <span>Página 5</span>
  </div>
</div>

<!-- ================= PAGE 6: PASSO 6 & PASSO 7 ================= -->
<div class="page">
  <h1 class="section-title">🌧️ 5. Pluviômetro e Qualidade do Ar (MQ-135)</h1>

  <h2 class="step-title">🌧️ Passo 6: Sensor Pluviométrico de Chuva (DSK MH-RD)</h2>
  <p>
    Formado por uma placa coletora de gotas exposta e uma plaquinha amplificadora LM393. A variação de condutividade hídrica entre as trilhas gera uma curva analógica inversamente proporcional à intensidade de precipitação.
  </p>

  <pre class="ascii-box">
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
  </pre>

  <ul class="step-instructions">
    <li><strong>Posicionamento do Comparador:</strong> Espete os 4 pinos na <strong>Protoboard Superior</strong>, fileira <strong>`f`</strong>, colunas <strong>35 a 38</strong>.</li>
    <li><strong>Conexões Elétricas:</strong> VCC (coluna 35) no <span class="badge-pin badge-3v3">Barramento 2 (3.3V)</span>, GND (coluna 36) no <span class="badge-pin badge-gnd">GND</span>, e AO (coluna 38) no <span class="badge-pin badge-adc">GPIO 35 (ADC1)</span> do ESP32.</li>
    <li><strong>Acoplamento da Placa Coletora:</strong> Use 2 jumpers fêmea-fêmea para ligar os 2 pinos superiores do módulo comparador aos 2 pinos da placa grande coletora DSK MH-RD (não há ordem de polaridade entre esses 2 fios).</li>
  </ul>

  <hr style="border: 0; border-top: 1px dashed #cbd5e1; margin: 10px 0;">

  <h2 class="step-title">💨 Passo 7: Sensor de Gases Atmosféricos (MQ-135)</h2>
  <p>
    O sensor MQ-135 integra uma resistência térmica interna de óxido de estanho (SnO2) que requer <strong>5.0V estáveis</strong> para operar em temperatura adequada de clivagem química.
  </p>

  <pre class="ascii-box">
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
  </pre>

  <ul class="step-instructions">
    <li><strong>Posicionamento:</strong> Espete os 4 pinos na <strong>Protoboard Superior</strong>, fileira <strong>`f`</strong>, colunas <strong>48 a 51</strong>.</li>
    <li><strong>Alimentação 5V:</strong> Ligue o VCC (coluna 48) na linha vermelha do <span class="badge-pin badge-5v">Barramento 1 (5.0V Exclusivo)</span>.</li>
    <li><strong>Aterramento:</strong> Ligue o GND (coluna 49) na linha azul do <span class="badge-pin badge-gnd">Barramento 1 (GND)</span>.</li>
    <li><strong>Sinal Analógico:</strong> Ligue a saída AO (coluna 51) com fio roxo ao <span class="badge-pin badge-adc">GPIO 32 (ADC1)</span> do ESP32.</li>
  </ul>

  <div class="callout callout-tip">
    <strong>Proteção por Divisor de Tensão (1 kΩ / 2 kΩ):</strong> Caso o ambiente apresente alta concentração de gases e a saída atinja 5V, conecte um resistor de 1 kΩ do pino AO a uma linha livre, e um resistor de 2 kΩ dessa linha para o GND. Conecte o GPIO 32 nessa junção central (tensão máxima atenuada: 3.33V).
  </div>

  <div class="page-footer">
    <span>EcoPulse — Estação Meteorológica IoT (UNIP PIM II)</span>
    <span>Página 6</span>
  </div>
</div>

<!-- ================= PAGE 7: TABELA MESTRA & DEDUAÇÃO MATEMÁTICA ================= -->
<div class="page">
  <h1 class="section-title">📊 6. Tabela Mestra de Fiação e Fundamentação Elétrica</h1>
  <p>
    Consolidação completa de todas as conexões do circuito para conferência rápida de bancada:
  </p>

  <table class="tech-table">
    <thead>
      <tr>
        <th>Componente</th>
        <th>Pino</th>
        <th>Posição na Protoboard</th>
        <th>Porta no ESP32</th>
        <th>Cor Recomendada</th>
        <th>Comportamento / Observações</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>Fonte MB102</strong></td>
        <td>Sup. / Inf.</td>
        <td>Colunas 1 a 12 (Proto Sup.)</td>
        <td>—</td>
        <td>Amarelo (Jumpers)</td>
        <td>5V no Barramento 1; 3.3V no Barramento 2</td>
      </tr>
      <tr>
        <td><strong>Malha GND</strong></td>
        <td>Trilhos (-)</td>
        <td>Barramentos 1, 2, 3 e 4</td>
        <td>Pino GND ESP32</td>
        <td>Preto</td>
        <td>Referência de potencial elétrico comum (0V)</td>
      </tr>
      <tr>
        <td><strong>ESP32 DevKit</strong></td>
        <td>3V3 / GND</td>
        <td>Colunas 1 a 15 (Vão Central)</td>
        <td>Barr. 4 (+) / Barr. 4 (-)</td>
        <td>Vermelho / Preto</td>
        <td>Alimentação principal da CPU e barramento 3.3V</td>
      </tr>
      <tr>
        <td><strong>DHT22</strong></td>
        <td>OUT</td>
        <td>Coluna 26 (Proto Inf. 'e')</td>
        <td><span class="badge-pin badge-gpio">GPIO 4</span></td>
        <td>Amarelo</td>
        <td>Sinal digital One-Wire (Pull-up interno na PCB)</td>
      </tr>
      <tr>
        <td><strong>BMP280</strong></td>
        <td>SDA / SCL</td>
        <td>Colunas 38 e 37 (Proto Inf.)</td>
        <td><span class="badge-pin badge-gpio">GPIO 21 / GPIO 22</span></td>
        <td>Azul / Verde</td>
        <td>Barramento I2C padrão. SDO no GND fixa end. <code>0x76</code></td>
      </tr>
      <tr>
        <td><strong>Módulo LDR</strong></td>
        <td>AO</td>
        <td>Coluna 25 (Proto Sup. 'f')</td>
        <td><span class="badge-pin badge-adc">GPIO 34 (ADC1)</span></td>
        <td>Branco</td>
        <td>Sinal analógico (Mais escuro = maior tensão/ADC)</td>
      </tr>
      <tr>
        <td><strong>Sensor Chuva</strong></td>
        <td>AO</td>
        <td>Coluna 38 (Proto Sup. 'f')</td>
        <td><span class="badge-pin badge-adc">GPIO 35 (ADC1)</span></td>
        <td>Laranja</td>
        <td>Sinal analógico (Seco = ~4095; Chuva forte = ~0)</td>
      </tr>
      <tr>
        <td><strong>Sensor MQ-135</strong></td>
        <td>VCC / AO</td>
        <td>Colunas 48 e 51 (Proto Sup.)</td>
        <td><span class="badge-pin badge-5v">Barr. 1</span> / <span class="badge-pin badge-adc">GPIO 32</span></td>
        <td>Vermelho / Roxo</td>
        <td>VCC ligado estritamente em 5V para pré-aquecimento</td>
      </tr>
    </tbody>
  </table>

  <h2 class="step-title" style="margin-top: 12px;">📐 Demonstração Matemática do Divisor de Tensão</h2>
  <div class="card-box">
    <p style="font-size: 8.5pt;">
      O conversor ADC do ESP32 possui tensão de saturação em V_ref = 3.3V. Como o sensor MQ-135 é alimentado com V_in = 5.0V, a aplicação direta poderia sobrecarregar a porta lógica interna. O dimensionamento adota a regra do divisor resistivo:
    </p>
    <div style="text-align: center; font-size: 10pt; font-weight: bold; margin: 6px 0; color: #0f172a; font-family: monospace;">
      V_out = V_in * [ R2 / (R1 + R2) ]
    </div>
    <p style="font-size: 8.5pt;">
      Adotando resistores comerciais de precisão R1 = 1 kΩ e R2 = 2 kΩ:
    </p>
    <div style="text-align: center; font-size: 9.5pt; font-family: monospace; color: #059669; margin: 4px 0;">
      V_out(max) = 5.0V * (2000 / (1000 + 2000)) = 5.0V * 0.6667 = 3.33V
    </div>
    <p style="font-size: 8pt; color: #64748b; margin-top: 4px;">
      O valor de pico obtido de 3.33V opera rigorosamente dentro da tolerância de entrada dos pinos analógicos do chip ESP32 (máx. 3.6V em regime transitório), assegurando vida útil ilimitada aos transistores de entrada CMOS.
    </p>
  </div>

  <div class="page-footer">
    <span>EcoPulse — Estação Meteorológica IoT (UNIP PIM II)</span>
    <span>Página 7</span>
  </div>
</div>

<!-- ================= PAGE 8: CHECKLIST & PROCEDIMENTO ================= -->
<div class="page">
  <h1 class="section-title">✅ 7. Checklist de Segurança e Primeiro Teste Serial</h1>
  <p>
    Antes de conectar a fonte de alimentação na rede ou plugar o cabo USB no notebook, realize a conferência visual e tátil dos itens abaixo:
  </p>

  <div class="checklist-item">
    <div class="checkbox-box"></div>
    <div>
      <strong>Tensão Restrita do Sensor BMP280:</strong> Certifique-se de que o jumper de alimentação do sensor roxo está conectado ao Barramento 4 (3.3V) e <em>jamais</em> ao Barramento 1 (5V).
    </div>
  </div>

  <div class="checklist-item">
    <div class="checkbox-box"></div>
    <div>
      <strong>Ausência de Curto no Vão do ESP32:</strong> Confirme que nenhuma perna de jumper ou resistor está cruzando diretamente a ranhura central do microcontrolador conectando pinos opostos em curto.
    </div>
  </div>

  <div class="checklist-item">
    <div class="checkbox-box"></div>
    <div>
      <strong>Pontes Centrais de Continuidade (Coluna 30):</strong> Verifique se os barramentos de alimentação possuem as pontes metálicas ligando a metade esquerda e direita da matriz de 830 pontos.
    </div>
  </div>

  <div class="checklist-item">
    <div class="checkbox-box"></div>
    <div>
      <strong>Referência Negativa Unificada (GND Comum):</strong> Teste se a linha azul do Barramento 1 (5V) está em curto elétrico direto com os Barramentos 2, 3 e 4 e com o GND do ESP32.
    </div>
  </div>

  <div class="checklist-item">
    <div class="checkbox-box"></div>
    <div>
      <strong>Isolamento do Barramento 1 (5V Exclusivo):</strong> O pino VCC do MQ-135 é o <em>único</em> condutor alimentado pela linha vermelha superior da fonte MB102.
    </div>
  </div>

  <div class="checklist-item">
    <div class="checkbox-box"></div>
    <div>
      <strong>Canais Analógicos no ADC1:</strong> As três saídas analógicas (LDR no GPIO 34, Chuva no GPIO 35 e MQ-135 no GPIO 32) não interferem no rádio Wi-Fi.
    </div>
  </div>

  <h2 class="step-title" style="margin-top: 12px;">💻 Procedimento de Validação no Monitor Serial</h2>
  <div class="card-box" style="font-size: 8.5pt;">
    <ol style="margin-left: 18px; line-height: 1.5;">
      <li>Conecte o cabo micro-USB ao computador e selecione a porta serial correspondente (ex: <code>/dev/ttyUSB0</code> ou <code>COM3</code>).</li>
      <li>Abra o <strong>PlatformIO Monitor Serial</strong> ou Arduino IDE na velocidade de <strong>115200 baud</strong>.</li>
      <li>Pressione o botão <strong>EN (Reset)</strong> no ESP32. A saída inicial deverá reportar:
        <br><code style="background: #e2e8f0; padding: 2px 6px; border-radius: 4px; font-size: 8pt; color: #0f172a;">[BMP280] Sensor detectado no endereco 0x76.</code>
        <br><code style="background: #e2e8f0; padding: 2px 6px; border-radius: 4px; font-size: 8pt; color: #0f172a;">[DHT22] Sensor de Temperatura e Umidade inicializado.</code>
      </li>
      <li>Coloque a mão sobre o sensor LDR para verificar a variação imediata no valor de radiação lido.</li>
      <li>Pingue 1 gota d'água na placa pluviométrica para observar a queda da leitura analógica de ~4095 para valores abaixo de 1500.</li>
    </ol>
  </div>

  <div style="margin-top: 16px; border: 1px solid #cbd5e1; border-radius: 8px; padding: 10px; background: #f8fafc;">
    <div style="font-size: 8.8pt; font-weight: bold; color: #0f172a; margin-bottom: 6px;">Ficha de Homologação de Bancada (Laboratório UNIP)</div>
    <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; font-size: 8pt; color: #475569;">
      <div><strong>Data da Montagem:</strong> ____ / ____ / 2026</div>
      <div><strong>Operador / Aluno:</strong> Wallace Vilela</div>
      <div><strong>Status do Circuito:</strong> [  ] Aprovado  [  ] Ajustes</div>
    </div>
  </div>

  <div class="page-footer">
    <span>EcoPulse — Estação Meteorológica IoT (UNIP PIM II)</span>
    <span>Página 8</span>
  </div>
</div>

</body>
</html>
"""

html_content = html_content.replace("__IMG_B64__", img_b64)

with open(HTML_OUT, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"HTML gerado em: {HTML_OUT}")

cmd = [
    "google-chrome",
    "--headless",
    "--disable-gpu",
    "--no-pdf-header-footer",
    f"--print-to-pdf={PDF_OUT}",
    HTML_OUT
]

res = subprocess.run(cmd, capture_output=True, text=True)
if res.returncode == 0:
    print(f"PDF gerado com sucesso em: {PDF_OUT}")
else:
    print(f"Erro ao gerar PDF: {res.stderr}")
