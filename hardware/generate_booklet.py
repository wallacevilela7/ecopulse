import os
import base64
import subprocess

BASE_DIR = "/home/wvs/Documents/ccomp-unip/2sem/pim2/ecopulse/hardware"
IMG_PATH = os.path.join(BASE_DIR, "assets", "protoboard_esquematico_mb102.png")
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
    margin: 11mm 13mm 11mm 13mm;
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
    font-size: 8.9pt;
    line-height: 1.37;
  }

  /* Page Break Utilities */
  .page {
    page-break-after: always;
    height: 100%;
    position: relative;
    padding-bottom: 24px;
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
    font-size: 25pt;
    font-weight: 800;
    line-height: 1.18;
    color: #ffffff;
    margin-bottom: 12px;
  }

  .cover-subtitle {
    font-size: 12.5pt;
    color: #cbd5e1;
    font-weight: 400;
    max-width: 92%;
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
    font-size: 9.8pt;
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
    font-size: 13.5pt;
    font-weight: 800;
    color: #0f172a;
    border-left: 5px solid #059669;
    padding-left: 10px;
    margin-bottom: 8px;
    display: flex;
    align-items: center;
    gap: 8px;
  }

  h2.step-title {
    font-size: 10.8pt;
    font-weight: 700;
    color: #0f172a;
    margin-top: 7px;
    margin-bottom: 4px;
    display: flex;
    align-items: center;
    gap: 6px;
  }

  p {
    margin-bottom: 5px;
    color: #334155;
  }

  /* Callout Boxes */
  .callout {
    border-radius: 6px;
    padding: 6px 10px;
    margin: 5px 0;
    font-size: 8.1pt;
    line-height: 1.35;
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
    font-size: 6.8pt;
    line-height: 1.20;
    padding: 6px 8px;
    border-radius: 6px;
    border: 1px solid #1e293b;
    margin: 4px 0;
    overflow: hidden;
    white-space: pre;
  }

  /* Lists */
  ul.step-instructions {
    list-style: none;
    margin: 4px 0;
  }

  ul.step-instructions li {
    position: relative;
    padding-left: 15px;
    margin-bottom: 3px;
    font-size: 8.3pt;
    color: #1e293b;
  }

  ul.step-instructions li::before {
    content: "•";
    color: #059669;
    font-weight: bold;
    font-size: 10pt;
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
    font-size: 7.6pt;
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
    font-size: 7.7pt;
    margin: 5px 0;
  }

  table.tech-table th {
    background-color: #0f172a;
    color: #f8fafc;
    text-align: left;
    padding: 4px 6px;
    font-weight: 600;
    font-size: 7.5pt;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  table.tech-table td {
    padding: 3.6px 6px;
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
    padding: 4.5px 7px;
    border-radius: 5px;
    margin-bottom: 4px;
    font-size: 8.1pt;
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
    padding: 7px 9px;
  }

  .img-container {
    text-align: center;
    margin: 6px 0;
  }

  .img-container img {
    max-width: 95%;
    max-height: 220px;
    border-radius: 8px;
    border: 1px solid #cbd5e1;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  }

  .img-caption {
    font-size: 7.2pt;
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
        Guia passo a passo de engenharia física para montagem da Estação Meteorológica EcoPulse em arquitetura de Menor Caminho e Fiação Rente (Topologia Zero-Crossing), matriz de dupla protoboard acoplada, fonte MB102 bi-volt e kit padronizado de jumpers rígidos em U.
      </p>

      <div class="cover-specs">
        <div class="spec-item">
          <div class="spec-label">Topologia</div>
          <div class="spec-value">Zero-Crossing (Fiação Rente em U)</div>
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
    A estação meteorológica <strong>EcoPulse</strong> foi projetada segundo rigorosos critérios de modularidade, baixa indutância e eliminação de emaranhados de fios, agrupando componentes por afinidade de porta lógica para o menor caminho físico.
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
        <td>Controle seletivo bi-volt e barramentos duplos de alimentação</td>
      </tr>
      <tr>
        <td><strong>03</strong></td>
        <td>Protoboard 830 Pts (com Travas)</td>
        <td>2</td>
        <td>—</td>
        <td>Acopladas horizontalmente pelas travas plásticas laterais</td>
      </tr>
      <tr>
        <td><strong>04</strong></td>
        <td>Sensor DHT22 / AM2302 (Placa Preta)</td>
        <td>1</td>
        <td><span class="badge-pin badge-3v3">3.3V</span></td>
        <td>Temperatura (-40°C a +80°C) e Umidade (0 a 100%) no GPIO 4</td>
      </tr>
      <tr>
        <td><strong>05</strong></td>
        <td>Sensor Barométrico BMP280 (Roxo)</td>
        <td>1</td>
        <td><span class="badge-pin badge-3v3">3.3V (Estrito!)</span></td>
        <td>Pressão atmosférica (300 a 1100 hPa) via I2C (GPIO 21/22)</td>
      </tr>
      <tr>
        <td><strong>06</strong></td>
        <td>Módulo LDR com Comparador (Azul)</td>
        <td>1</td>
        <td><span class="badge-pin badge-3v3">3.3V</span></td>
        <td>Radiação luminosa ambiente via saída analógica AO (GPIO 34)</td>
      </tr>
      <tr>
        <td><strong>07</strong></td>
        <td>Sensor de Chuva DSK MH-RD + Placa</td>
        <td>1</td>
        <td><span class="badge-pin badge-3v3">3.3V</span></td>
        <td>Detecção de precipitação pluviométrica por AO (GPIO 35)</td>
      </tr>
      <tr>
        <td><strong>08</strong></td>
        <td>Sensor MQ-135 Flying-Fish (Ar/Gases)</td>
        <td>1</td>
        <td><span class="badge-pin badge-5v">5.0V (Aquecedor)</span></td>
        <td>Detecção de gases (NH3, NOx, fumaça, CO2) no GPIO 32</td>
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
        <td>Kit de Jumpers Rígidos em U & Flexíveis</td>
        <td>1 kit</td>
        <td>—</td>
        <td>Fiação estruturada em U (2 a 13 furos) rente à bancada</td>
      </tr>
    </tbody>
  </table>

  <div class="img-container">
    <img src="data:image/png;base64,__IMG_B64__" alt="Esquemático Protoboard">
    <div class="img-caption">Figura 1.1: Visão superior da montagem física na bancada em layout de menor caminho (Zero-Crossing com jumpers rígidos em U).</div>
  </div>

  <div class="callout callout-info">
    <strong>Princípio do Menor Caminho (Zero-Crossing):</strong> Sensores com saídas digitais/I2C (DHT22 e BMP280) foram posicionados na <strong>Protoboard Superior</strong> onde estão seus pinos correspondentes (GPIOs 4, 21 e 22). Sensores analógicos (LDR e Chuva) foram posicionados na <strong>Protoboard Inferior</strong> colados ao ADC1 (GPIOs 34 e 35). Zero fios cruzam o vão central!
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
    A disposição espacial foi projetada para que cada sinal viaje em linha reta através do menor número possível de furos, utilizando os grampos em U padronizados da sua caixinha:
  </p>

  <pre class="ascii-box">
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
  </pre>

  <div class="callout callout-warning">
    <strong>Pontes da Coluna 30:</strong> Insira jumpers rígidos em U (vermelhos/laranjas de 3 a 5 furos) unindo o lado esquerdo ao direito nas linhas vermelhas e azuis dos Barramentos 1 a 4 para garantir continuidade elétrica de ponta a ponta da bancada.
  </div>

  <h2 class="step-title">⚡ Passo 1: Fonte MB102 e Distribuição de Energia</h2>
  <p>
    Encaixada na extremidade esquerda da Protoboard Superior (colunas 1 a 8), regulando as duas tensões independentes da bancada.
  </p>

  <pre class="ascii-box">
   [FONTE MB102]
  +-------------+
  | [Jumper:5V] |---> [+] Barramento 1 (Vermelho): 5.0V EXCLUSIVO (MQ-135)
  |             |---> [-] Barramento 1 (Azul)    : GND Comum ---+
  |  (Proto Sup)|                                               |
  | [Jumper:3V3]|---> [+] Barramento 2 (Vermelho): 3.3V --------|--+
  +-------------+---> [-] Barramento 2 (Azul)    : GND Comum ---|--|---+
                                                                |  |   |
                      [+] Barramento 3 (Vermelho): 3.3V <-------|--+   | (Fios Pretos:
                      [-] Barramento 3 (Azul)    : GND Comum <--+------|  GND Comum)
                                                                       |
                      [+] Barramento 4 (Vermelho): 3.3V <--------------+ (Fios Vermelhos: 3.3V)
                      [-] Barramento 4 (Azul)    : GND Comum <---------+ (Fios Pretos: GND)
  </pre>

  <ul class="step-instructions">
    <li><strong>Seletores da MB102:</strong> Jumper superior em <strong>5V</strong> e inferior em <strong>3.3V</strong>.</li>
    <li><strong>Ponte de GND Comum (Jumpers Pretos):</strong> Interligue todos os trilhos azuis: Barramento 1 (-) ao 2 (-), 2 (-) ao 3 (-), e 3 (-) ao 4 (-).</li>
    <li><strong>Distribuição de 3.3V (Jumpers Vermelhos):</strong> Conecte a linha vermelha do Barramento 2 (+) ao 3 (+) e deste para o Barramento 4 (+).</li>
  </ul>

  <div class="page-footer">
    <span>EcoPulse — Estação Meteorológica IoT (UNIP PIM II)</span>
    <span>Página 3</span>
  </div>
</div>

<!-- ================= PAGE 4: PASSO 2 & PASSO 3 ================= -->
<div class="page">
  <h1 class="section-title">🔌 3. Instalação do Processador e Sensor DHT22</h1>

  <h2 class="step-title">🧠 Passo 2: Microcontrolador ESP32 no Vão Direito (Colunas 48 a 62)</h2>
  <p>
    O microcontrolador une a <strong>fileira 'a'</strong> da Protoboard Superior à <strong>fileira 'j'</strong> da Protoboard Inferior. A porta Micro-USB fica na borda externa da mesa para conexão segura ao PC.
  </p>

  <pre class="ascii-box">
Protoboard Superior (Parte Inferior - Fileiras 'e' a 'a'):
Coluna:    ...  48   49   50   51   52   53   ...   58   ...   61   62
Fileira e: ... [ ]  [ ]  [ ]  [ ]  [ ]  [ ]  ...  [ ]  ...  [ ]  [ ]  <-- 4 furos livres p/ jumpers!
Fileira d: ... [ ]  [ ]  [ ]  [ ]  [ ]  [ ]  ...  [ ]  ...  [ ]  [ ]
Fileira c: ... [ ]  [ ]  [ ]  [ ]  [ ]  [ ]  ...  [ ]  ...  [ ]  [ ]
Fileira b: ... [ ]  [ ]  [ ]  [ ]  [ ]  [ ]  ...  [ ]  ...  [ ]  [ ]
Fileira a: ... (P)  (P)  (P)  (P)  (P)  (P)  ...  (P)  ...  (P)  (P)  <-- Pinos Superiores do ESP32
Pino:          D23  D22  TX0  RX0  D21  D19  ...  D4   ...  GND  3V3
               ======================================================
               | [Antena]          ESP32 NODEMCU           [USB PC] |  <-- Sobre o vão central
               ======================================================
Pino:          EN   VP   VN   D34  D35  D32  ...  D14  ...  GND  VIN
Fileira j: ... (P)  (P)  (P)  (P)  (P)  (P)  ...  (P)  ...  (P)  (P)  <-- Pinos Inferiores do ESP32
Fileira i: ... [ ]  [ ]  [ ]  [ ]  [ ]  [ ]  ...  [ ]  ...  [ ]  [ ]  <-- Entradas Analógicas ADC1!
Fileira h: ... [ ]  [ ]  [ ]  [ ]  [ ]  [ ]  ...  [ ]  ...  [ ]  [ ]
Protoboard Inferior (Parte Superior - Fileiras 'j' a 'f')
  </pre>

  <ul class="step-instructions">
    <li><strong>Alimentação 3.3V Local (Jumper Verde 2 Furos):</strong> Ligue o pino <span class="badge-pin badge-3v3">3V3</span> (coluna 62, fileira b) ao Barramento 2 (+) e <span class="badge-pin badge-gnd">GND</span> (coluna 61, fileira b) ao Barramento 2 (-).</li>
    <li><strong>Aterramento Inferior:</strong> Ligue o pino <span class="badge-pin badge-gnd">GND</span> inferior (coluna 61, fileira i) ao Barramento 3 (-).</li>
  </ul>

  <hr style="border: 0; border-top: 1px dashed #cbd5e1; margin: 8px 0;">

  <h2 class="step-title">🌡️ Passo 3: Sensor de Temperatura e Umidade (DHT22)</h2>
  <p>
    Posicionado na <strong>Protoboard Superior</strong> (colunas 54 a 56, fileira `e`), colado na porta D4 do ESP32.
  </p>

  <pre class="ascii-box">
Protoboard Superior (Colunas 54, 55, 56):
            +-----------+
            |   DHT22   |
            |  (Branco) |
            +-----------+
              |   |   |    <-- Pinos inseridos na Fileira 'e' (Colunas 54, 55, 56)
Coluna:      54  55  56
Pino:        [+] [OUT][-]
              |    |   |
              |    |   +-----> (Jumper Verde 2 Furos)   Ligar no [-] Barramento 2 (GND)
              |    +---------> (Jumper Laranja 3 Furos) Ligar no pino [GPIO 4 (coluna 58)] do ESP32!
              +--------------> (Jumper Verde 2 Furos)   Ligar no [+] Barramento 2 (3.3V)
  </pre>

  <ul class="step-instructions">
    <li><strong>Coluna 54 (`+` / VCC):</strong> Jumper verde de 2 furos no <span class="badge-pin badge-3v3">Barramento 2 (3.3V)</span>.</li>
    <li><strong>Coluna 55 (`OUT` / DAT):</strong> Jumper laranja em U de 3 furos ligando diretamente na coluna 58, fileira `b` (<span class="badge-pin badge-gpio">GPIO 4</span>). Fiação 100% rente sem sobras!</li>
    <li><strong>Coluna 56 (`-` / GND):</strong> Jumper verde de 2 furos no <span class="badge-pin badge-gnd">Barramento 2 (GND)</span>.</li>
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
    Posicionado na <strong>Protoboard Superior</strong> (colunas 43 a 48, fileira `e`). Suas linhas I2C alcançam os pinos GPIO 21 e 22 em linha reta horizontal através de pequenos jumpers rígidos em U.
  </p>

  <pre class="ascii-box">
Protoboard Superior (Colunas 43 a 48 - Fileira 'e'):
         +-------------------------+
         |      GY-BMP280-3.3      |
         |  VCC GND SCL SDA CSB SDO|
         +-------------------------+
             |   |   |   |   |   |   <-- Pinos inseridos na Fileira 'e' (Colunas 43 a 48)
Coluna:     43  44  45  46  47  48
             |   |   |   |       |
             |   |   |   |       +--> (Jumper Verde 2 Furos)   Ligar no [-] Barramento 2 (GND) -> Endereço 0x76
             |   |   |   +----------> (Jumper Amarelo 6 Furos) Ligar no [GPIO 21 (col 52, fil b)] do ESP32!
             |   |   +--------------> (Jumper Vermelho 4 Furos)Ligar no [GPIO 22 (col 49, fil b)] do ESP32!
             |   +------------------> (Jumper Verde 2 Furos)   Ligar no [-] Barramento 2 (GND)
             +----------------------> (Jumper Verde 2 Furos)   Ligar no [+] Barramento 2 (3.3V)
  </pre>

  <ul class="step-instructions">
    <li><strong>Coluna 43 (VCC) & 44 (GND):</strong> Jumpers verdes de 2 furos no <span class="badge-pin badge-3v3">Barramento 2 (3.3V)</span> e <span class="badge-pin badge-gnd">GND</span>.</li>
    <li><strong>Coluna 45 (SCL):</strong> Jumper vermelho/laranja em U de 4 furos ligado diretamente ao <span class="badge-pin badge-gpio">GPIO 22</span> (coluna 49, fileira `b`).</li>
    <li><strong>Coluna 46 (SDA):</strong> Jumper amarelo em U de 6 furos ligado diretamente ao <span class="badge-pin badge-gpio">GPIO 21</span> (coluna 52, fileira `b`).</li>
    <li><strong>Coluna 48 (SDO):</strong> Jumper verde de 2 furos no Barramento 2 (-) GND (fixa endereço em <code>0x76</code>).</li>
  </ul>

  <hr style="border: 0; border-top: 1px dashed #cbd5e1; margin: 8px 0;">

  <h2 class="step-title">☀️ Passo 5: Módulo Sensor de Luminosidade (LDR Azul)</h2>
  <p>
    Posicionado na <strong>Protoboard Inferior</strong> (colunas 44 a 47, fileira `f`), imediatamente alinhado com a porta analógica D34 do microcontrolador.
  </p>

  <pre class="ascii-box">
Protoboard Inferior (Colunas 44 a 47 - Fileira 'f'):
         +-------------------+
         |  MÓDULO LDR AZUL  |
         |  AO  DO  GND  VCC |
         +-------------------+
            |   |    |    |    <-- Pinos inseridos na Fileira 'f' (Colunas 44 a 47)
Coluna:    44  45   46   47
            |        |    |
            |        |    +--> (Jumper Verde 2 Furos)   Ligar no [+] Barramento 3 (3.3V)
            |        +-------> (Jumper Verde 2 Furos)   Ligar no [-] Barramento 3 (GND)
            +----------------> (Jumper Amarelo 7 Furos) Ligar no [GPIO 34 (col 51, fil i)] do ESP32!
  </pre>

  <ul class="step-instructions">
    <li><strong>Coluna 47 (VCC) & 46 (GND):</strong> Jumpers verdes de 2 furos no <span class="badge-pin badge-3v3">Barramento 3 (3.3V)</span> e <span class="badge-pin badge-gnd">GND</span>.</li>
    <li><strong>Coluna 45 (DO):</strong> Deixar desconectado.</li>
    <li><strong>Coluna 44 (AO):</strong> Jumper amarelo em U de 7 furos ligado diretamente ao <span class="badge-pin badge-adc">GPIO 34 (coluna 51, fileira `i`)</span>.</li>
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
    Comparador LM393 posicionado na <strong>Protoboard Inferior</strong> (colunas 36 a 39, fileira `f`).
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
             |    |   |   |    <-- Pinos inseridos na Fileira 'f' (Colunas 36 a 39)
Coluna:     36   37  38  39
             |    |       |
             |    |       +--> (Jumper Azul 13 Furos) Ligar no [GPIO 35 (col 52, fil i)] do ESP32!
             |    +----------> (Jumper Verde 2 Furos) Ligar no [-] Barramento 3 (GND)
             +---------------> (Jumper Verde 2 Furos) Ligar no [+] Barramento 3 (3.3V)
  </pre>

  <ul class="step-instructions">
    <li><strong>Alimentação:</strong> VCC (coluna 36) e GND (coluna 37) no <span class="badge-pin badge-3v3">Barramento 3</span> com jumpers verdes de 2 furos.</li>
    <li><strong>Sinal Analógico:</strong> AO (coluna 39) com jumper azul em U de 13 furos ligado diretamente ao <span class="badge-pin badge-adc">GPIO 35 (coluna 52, fileira `i`)</span> do ESP32.</li>
    <li><strong>Placa Coletora Externa:</strong> 2 fios fêmea-fêmea ligando o topo do comparador à placa coletora.</li>
  </ul>

  <hr style="border: 0; border-top: 1px dashed #cbd5e1; margin: 8px 0;">

  <h2 class="step-title">💨 Passo 7: Sensor de Gases Atmosféricos (MQ-135)</h2>
  <p>
    Posicionado na <strong>Protoboard Superior</strong> (colunas 16 a 19, fileira `f`), ao lado da fonte MB102 para receber 5.0V direto do Barramento 1.
  </p>

  <pre class="ascii-box">
Protoboard Superior (Colunas 16 a 19):
         +-------------------+
         |  MQ-135 (Prateado)|
         |  VCC  GND  DO  AO |
         +-------------------+
             |    |   |   |    <-- Pinos inseridos na Fileira 'f' (Colunas 16 a 19)
Coluna:     16   17  18  19
             |    |       |
             |    |       +--> (Divisor 1k/2k Cols 20-22) -> Cabo Limpo -> [GPIO 32 (col 53, fil i)] ESP32
             |    +----------> (Jumper Verde 2 Furos)     Ligar no [-] Barramento 1 (GND)
             +---------------> (Jumper Verde 2 Furos)     Ligar no [+] Barramento 1 (5.0V EXCLUSIVO)
  </pre>

  <ul class="step-instructions">
    <li><strong>Alimentação 5.0V Exclusivo:</strong> VCC (coluna 16) no <span class="badge-pin badge-5v">Barramento 1 (5V)</span> com jumper de 2 furos.</li>
    <li><strong>Aterramento:</strong> GND (coluna 17) no <span class="badge-pin badge-gnd">Barramento 1 (GND)</span> com jumper de 2 furos.</li>
    <li><strong>Divisor Resistivo:</strong> Resistor de 1 kΩ liga da coluna 19 (AO) à coluna 21. Resistor de 2 kΩ liga da coluna 21 ao Barramento 1 (GND).</li>
    <li><strong>Sinal Atenuado:</strong> 1 condutor parte da coluna 21 até o <span class="badge-pin badge-adc">GPIO 32 (coluna 53, fileira `i`)</span> do ESP32.</li>
  </ul>

  <div class="callout callout-tip">
    <strong>Proteção por Divisor de Tensão:</strong> O divisor reduz o sinal de 5V para o patamar seguro de 3.33V (V_out = 5.0 * 2000 / 3000 = 3.33V), garantindo operação ininterrupta sem risco aos transistores de entrada CMOS do ESP32.
  </div>

  <div class="page-footer">
    <span>EcoPulse — Estação Meteorológica IoT (UNIP PIM II)</span>
    <span>Página 6</span>
  </div>
</div>

<!-- ================= PAGE 7: TABELA MESTRA, GUIA JUMPERS & DEDUÇÃO ================= -->
<div class="page">
  <h1 class="section-title">📊 6. Tabela Mestra e Guia de Jumpers Rígidos em U</h1>
  <p>
    Consolidação de todas as conexões e mapeamento do kit de jumpers rígidos em U padronizados por cor:
  </p>

  <table class="tech-table">
    <thead>
      <tr>
        <th>Componente</th>
        <th>Pino</th>
        <th>Posição na Protoboard</th>
        <th>Porta no ESP32</th>
        <th>Jumper Recomendado</th>
        <th>Comportamento / Observações</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>Fonte MB102</strong></td>
        <td>Sup. / Inf.</td>
        <td>Colunas 1 a 8 (Proto Sup.)</td>
        <td>—</td>
        <td>Amarelo (Seletores)</td>
        <td>5V no Barramento 1; 3.3V no Barramento 2</td>
      </tr>
      <tr>
        <td><strong>Malha GND</strong></td>
        <td>Trilhos (-)</td>
        <td>Barramentos 1, 2, 3 e 4</td>
        <td>GND ESP32 (Col. 61)</td>
        <td>Preto</td>
        <td>Referencial de potencial elétrico comum (0V)</td>
      </tr>
      <tr>
        <td><strong>ESP32 DevKit</strong></td>
        <td>3V3 / GND</td>
        <td>Colunas 48 a 62 (Vão Direito)</td>
        <td>Barr. 2 (+) / Barr. 2 (-)</td>
        <td>Verde (U 2 furos)</td>
        <td>Alimentação local 3.3V e aterramento</td>
      </tr>
      <tr>
        <td><strong>DHT22</strong></td>
        <td>OUT</td>
        <td>Coluna 55 (Proto Sup. 'e')</td>
        <td><span class="badge-pin badge-gpio">GPIO 4 (Col. 58)</span></td>
        <td>Laranja (U 3 furos)</td>
        <td>Sinal digital One-Wire (Distância: 3 furos)</td>
      </tr>
      <tr>
        <td><strong>BMP280</strong></td>
        <td>SCL / SDA</td>
        <td>Colunas 45 e 46 (Proto Sup.)</td>
        <td><span class="badge-pin badge-gpio">GPIO 22 / GPIO 21</span></td>
        <td>Vermelho / Amarelo (U)</td>
        <td>Barramento I2C (Distância: 4 a 6 furos)</td>
      </tr>
      <tr>
        <td><strong>Módulo LDR</strong></td>
        <td>AO</td>
        <td>Coluna 44 (Proto Inf. 'f')</td>
        <td><span class="badge-pin badge-adc">GPIO 34 (ADC1 - Col. 51)</span></td>
        <td>Amarelo (U 7 furos)</td>
        <td>Sinal analógico (Distância: 7 furos)</td>
      </tr>
      <tr>
        <td><strong>Sensor Chuva</strong></td>
        <td>AO</td>
        <td>Coluna 39 (Proto Inf. 'f')</td>
        <td><span class="badge-pin badge-adc">GPIO 35 (ADC1 - Col. 52)</span></td>
        <td>Azul (U 13 furos)</td>
        <td>Sinal analógico pluviométrico em linha reta</td>
      </tr>
      <tr>
        <td><strong>Sensor MQ-135</strong></td>
        <td>VCC / AO</td>
        <td>Colunas 16 e 19 (Proto Sup.)</td>
        <td><span class="badge-pin badge-5v">Barr. 1</span> / <span class="badge-pin badge-adc">GPIO 32</span></td>
        <td>Verde (2 furos) / Flexível</td>
        <td>VCC estrito em 5V; AO com divisor resistivo</td>
      </tr>
    </tbody>
  </table>

  <h2 class="step-title" style="margin-top: 6px;">📏 Guia de Utilização do Kit de Jumpers Rígidos em U</h2>
  <table class="tech-table">
    <thead>
      <tr>
        <th>Tamanho / Cor</th>
        <th>Alcance</th>
        <th>Aplicação Específica no Circuito EcoPulse</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>Verde Pequeno</strong></td>
        <td>2 furos</td>
        <td>VCC e GND locais de todos os 5 módulos; pinos 3V3 e GND do ESP32; pino SDO do BMP280.</td>
      </tr>
      <tr>
        <td><strong>Laranja</strong></td>
        <td>3 furos</td>
        <td><strong>OUT do DHT22</strong> (coluna 55) ao <strong>GPIO 4</strong> (coluna 58). Fiação rente à placa.</td>
      </tr>
      <tr>
        <td><strong>Vermelho</strong></td>
        <td>4 a 5 furos</td>
        <td><strong>SCL do BMP280</strong> (coluna 45) ao <strong>GPIO 22</strong> (coluna 49); pontes da coluna 30.</td>
      </tr>
      <tr>
        <td><strong>Amarelo</strong></td>
        <td>6 a 7 furos</td>
        <td><strong>SDA do BMP280</strong> (coluna 46) ao <strong>GPIO 21</strong> (coluna 52); <strong>AO do LDR</strong> (coluna 44) ao <strong>GPIO 34</strong> (coluna 51).</td>
      </tr>
      <tr>
        <td><strong>Azul / Marrom</strong></td>
        <td>10 a 13 furos</td>
        <td><strong>AO do Sensor de Chuva</strong> (coluna 39) ao <strong>GPIO 35</strong> (coluna 52). Linha horizontal direta.</td>
      </tr>
      <tr>
        <td><strong>Jumpers Longos</strong></td>
        <td>> 15 furos</td>
        <td>Pontes verticais de GND Comum e distribuição de 3.3V entre os barramentos 2, 3 e 4.</td>
      </tr>
    </tbody>
  </table>

  <h2 class="step-title" style="margin-top: 6px;">📐 Demonstração Matemática do Divisor de Tensão</h2>
  <div class="card-box">
    <p style="font-size: 8.1pt;">
      O conversor ADC do ESP32 satura em V_ref = 3.3V. Como o MQ-135 opera em V_in = 5.0V, adota-se o divisor resistivo para atenuar o sinal:
    </p>
    <div style="text-align: center; font-size: 9.5pt; font-weight: bold; margin: 4px 0; color: #0f172a; font-family: monospace;">
      V_out = V_in * [ R2 / (R1 + R2) ] &nbsp;=&gt;&nbsp; 5.0V * [ 2000 / (1000 + 2000) ] = 3.33V
    </div>
    <p style="font-size: 7.8pt; color: #64748b; margin-top: 2px;">
      O pico atenuado de 3.33V opera dentro da tolerância do ESP32 (máx. 3.6V), assegurando integridade e vida útil ilimitada à porta CMOS.
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
      <strong>Tensão Restrita do Sensor BMP280:</strong> Certifique-se de que o jumper de alimentação do sensor roxo está conectado ao Barramento 2 (3.3V) e <em>jamais</em> ao Barramento 1 (5V).
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

  <h2 class="step-title" style="margin-top: 10px;">💻 Procedimento de Validação no Monitor Serial</h2>
  <div class="card-box" style="font-size: 8.3pt;">
    <ol style="margin-left: 18px; line-height: 1.45;">
      <li>Conecte o cabo micro-USB ao computador e selecione a porta serial correspondente (ex: <code>/dev/ttyUSB0</code> ou <code>COM3</code>).</li>
      <li>Abra o <strong>PlatformIO Monitor Serial</strong> ou Arduino IDE na velocidade de <strong>115200 baud</strong>.</li>
      <li>Pressione o botão <strong>EN (Reset)</strong> no ESP32. A saída inicial deverá reportar:
        <br><code style="background: #e2e8f0; padding: 2px 6px; border-radius: 4px; font-size: 7.8pt; color: #0f172a;">[BMP280] Sensor detectado no endereco 0x76.</code>
        <br><code style="background: #e2e8f0; padding: 2px 6px; border-radius: 4px; font-size: 7.8pt; color: #0f172a;">[DHT22] Sensor de Temperatura e Umidade inicializado.</code>
      </li>
      <li>Coloque a mão sobre o sensor LDR para verificar a variação imediata no valor de radiação lido.</li>
      <li>Pingue 1 gota d'água na placa pluviométrica para observar a queda da leitura analógica de ~4095 para valores abaixo de 1500.</li>
    </ol>
  </div>

  <div style="margin-top: 14px; border: 1px solid #cbd5e1; border-radius: 8px; padding: 9px; background: #f8fafc;">
    <div style="font-size: 8.6pt; font-weight: bold; color: #0f172a; margin-bottom: 5px;">Ficha de Homologação de Bancada (Laboratório UNIP)</div>
    <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; font-size: 7.8pt; color: #475569;">
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
