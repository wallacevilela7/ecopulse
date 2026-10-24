import os
import subprocess

svg_content = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 740" width="100%" height="100%" style="background-color: #0b1120; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
  <defs>
    <!-- Gradientes -->
    <linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0b1120"/>
      <stop offset="100%" stop-color="#020617"/>
    </linearGradient>
    <linearGradient id="mb102Grad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#1e293b"/>
      <stop offset="100%" stop-color="#0f172a"/>
    </linearGradient>
    <linearGradient id="esp32Grad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#1e293b"/>
      <stop offset="100%" stop-color="#090d16"/>
    </linearGradient>
    <linearGradient id="shieldGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#94a3b8"/>
      <stop offset="50%" stop-color="#cbd5e1"/>
      <stop offset="100%" stop-color="#64748b"/>
    </linearGradient>
    <linearGradient id="protoGrad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#f8fafc"/>
      <stop offset="100%" stop-color="#f1f5f9"/>
    </linearGradient>
    <linearGradient id="jumperYellow" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#fef08a"/>
      <stop offset="100%" stop-color="#eab308"/>
    </linearGradient>

    <!-- Filtros de Sombra e Brilho -->
    <filter id="cardShadow" x="-5%" y="-5%" width="110%" height="110%">
      <feDropShadow dx="0" dy="5" stdDeviation="5" flood-color="#000000" flood-opacity="0.5"/>
    </filter>
    <filter id="glowGreen" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="3" result="blur" />
      <feComposite in="SourceGraphic" in2="blur" operator="over" />
    </filter>
  </defs>

  <rect width="1200" height="740" fill="url(#bgGrad)"/>

  <!-- ================= HEADER SUPERIOR ================= -->
  <g transform="translate(25, 15)">
    <rect x="0" y="0" width="1150" height="52" rx="8" fill="#1e293b" stroke="#334155" stroke-width="1.5" filter="url(#cardShadow)"/>
    <text x="25" y="32" fill="#38bdf8" font-size="15" font-weight="900" letter-spacing="1">ESQUEMÁTICO DE LABORATÓRIO: DUPLA PROTOBOARD COM FONTE MB102</text>
    <text x="25" y="45" fill="#94a3b8" font-size="8.5" font-weight="600">PROJETO ECOPULSE • ENGENHARIA DE HARDWARE • PIM II &amp; PROJETO DIRIGIDO II (UNIP)</text>
    
    <!-- Badge de Controle de Tensão da MB102 -->
    <rect x="740" y="10" width="395" height="32" rx="16" fill="#064e3b" stroke="#10b981" stroke-width="1.5"/>
    <circle cx="760" cy="26" r="6" fill="#34d399" filter="url(#glowGreen)"/>
    <text x="775" y="30" fill="#ecfdf5" font-size="10.5" font-weight="800">OBJETIVO DA MB102: CONTROLE SELETIVO BI-VOLT (5V &amp; 3.3V)</text>
  </g>

  <!-- ================= PROTOBOARD SUPERIOR ================= -->
  <g transform="translate(225, 85)" filter="url(#cardShadow)">
    <rect x="0" y="0" width="950" height="250" rx="8" fill="url(#protoGrad)" stroke="#cbd5e1" stroke-width="2"/>
    <text x="800" y="24" fill="#64748b" font-size="11" font-weight="bold">PROTOBOARD SUPERIOR</text>
    
    <!-- Coordenadas das Colunas (1 a 60) -->
    <g fill="#94a3b8" font-size="7.5" font-family="monospace">
      <text x="40" y="47">1</text><text x="110" y="47">10</text><text x="200" y="47">20</text>
      <text x="290" y="47">25</text><text x="360" y="47">30</text><text x="435" y="47">35</text>
      <text x="580" y="47">48</text><text x="640" y="47">51</text><text x="760" y="47">60</text>
    </g>

    <!-- Barramento 1 (Superior) -->
    <rect x="15" y="10" width="920" height="30" rx="4" fill="#e2e8f0" stroke="#cbd5e1" stroke-width="1"/>
    <!-- Linha Vermelha (+) 5V -->
    <line x1="25" y1="18" x2="925" y2="18" stroke="#ef4444" stroke-width="3"/>
    <text x="930" y="21" fill="#ef4444" font-size="12" font-weight="900">+</text>
    <!-- Linha Azul (-) GND -->
    <line x1="25" y1="32" x2="925" y2="32" stroke="#3b82f6" stroke-width="3"/>
    <text x="930" y="35" fill="#3b82f6" font-size="14" font-weight="900">-</text>

    <!-- Rótulo Barramento 1 (5V Exclusivo) -->
    <rect x="250" y="12" width="370" height="15" rx="3" fill="#fee2e2" stroke="#ef4444"/>
    <text x="256" y="23" fill="#991b1b" font-size="8.8" font-weight="900">BARRAMENTO 1 (VERMELHO): 5.0V EXCLUSIVO P/ MQ-135</text>

    <!-- Matriz de Conexões: Fileiras 'f' a 'j' -->
    <rect x="15" y="52" width="920" height="68" rx="4" fill="#ffffff" stroke="#e2e8f0" stroke-width="1"/>
    <text x="22" y="70" fill="#94a3b8" font-size="8.5" font-family="monospace">j</text>
    <text x="22" y="82" fill="#94a3b8" font-size="8.5" font-family="monospace">i</text>
    <text x="22" y="94" fill="#94a3b8" font-size="8.5" font-family="monospace">h</text>
    <text x="22" y="106" fill="#94a3b8" font-size="8.5" font-family="monospace">f</text>

    <!-- Canal Central Divisório (Protoboard Superior) -->
    <rect x="15" y="123" width="920" height="14" fill="#cbd5e1"/>

    <!-- Matriz de Conexões: Fileiras 'a' a 'e' -->
    <rect x="15" y="140" width="920" height="68" rx="4" fill="#ffffff" stroke="#e2e8f0" stroke-width="1"/>
    <text x="22" y="158" fill="#94a3b8" font-size="8.5" font-family="monospace">e</text>
    <text x="22" y="170" fill="#94a3b8" font-size="8.5" font-family="monospace">d</text>
    <text x="22" y="182" fill="#94a3b8" font-size="8.5" font-family="monospace">b</text>
    <text x="22" y="194" fill="#94a3b8" font-size="8.5" font-family="monospace">a</text>

    <!-- Barramento 2 (Inferior da Protoboard Superior) -->
    <rect x="15" y="210" width="920" height="30" rx="4" fill="#e2e8f0" stroke="#cbd5e1" stroke-width="1"/>
    <line x1="25" y1="218" x2="925" y2="218" stroke="#10b981" stroke-width="3"/>
    <line x1="25" y1="232" x2="925" y2="232" stroke="#3b82f6" stroke-width="3"/>

    <!-- Rótulo Barramento 2 (Deslocado para x=380 para não colidir com o ESP32) -->
    <rect x="380" y="212" width="370" height="15" rx="3" fill="#dcfce7" stroke="#10b981"/>
    <text x="386" y="223" fill="#166534" font-size="8.8" font-weight="900">BARRAMENTO 2 (VERMELHO): 3.3V SEGURO (ESP32 E SENSORES)</text>
  </g>

  <!-- ================= PROTOBOARD INFERIOR ================= -->
  <g transform="translate(225, 395)" filter="url(#cardShadow)">
    <rect x="0" y="0" width="950" height="250" rx="8" fill="url(#protoGrad)" stroke="#cbd5e1" stroke-width="2"/>
    <text x="800" y="24" fill="#64748b" font-size="11" font-weight="bold">PROTOBOARD INFERIOR</text>

    <!-- Barramento 3 (Superior da Protoboard Inferior) -->
    <rect x="15" y="10" width="920" height="30" rx="4" fill="#e2e8f0" stroke="#cbd5e1" stroke-width="1"/>
    <line x1="25" y1="18" x2="925" y2="18" stroke="#10b981" stroke-width="3"/>
    <line x1="25" y1="32" x2="925" y2="32" stroke="#3b82f6" stroke-width="3"/>

    <!-- Rótulo Barramento 3 (Deslocado para x=380 para não colidir) -->
    <rect x="380" y="12" width="370" height="15" rx="3" fill="#dcfce7" stroke="#10b981"/>
    <text x="386" y="23" fill="#166534" font-size="8.8" font-weight="900">BARRAMENTO 3 (VERMELHO): 3.3V (PONTE DO BARRAMENTO 2)</text>

    <!-- Matriz de Conexões: Fileiras 'f' a 'j' -->
    <rect x="15" y="52" width="920" height="68" rx="4" fill="#ffffff" stroke="#e2e8f0" stroke-width="1"/>
    <text x="22" y="70" fill="#94a3b8" font-size="8.5" font-family="monospace">j</text>
    <text x="22" y="82" fill="#94a3b8" font-size="8.5" font-family="monospace">i</text>
    <text x="22" y="94" fill="#94a3b8" font-size="8.5" font-family="monospace">h</text>
    <text x="22" y="106" fill="#94a3b8" font-size="8.5" font-family="monospace">f</text>

    <!-- Canal Central Divisório (Protoboard Inferior) -->
    <rect x="15" y="123" width="920" height="14" fill="#cbd5e1"/>

    <!-- Matriz de Conexões: Fileiras 'a' a 'e' -->
    <rect x="15" y="140" width="920" height="68" rx="4" fill="#ffffff" stroke="#e2e8f0" stroke-width="1"/>
    <text x="22" y="158" fill="#94a3b8" font-size="8.5" font-family="monospace">e</text>
    <text x="22" y="170" fill="#94a3b8" font-size="8.5" font-family="monospace">d</text>
    <text x="22" y="182" fill="#94a3b8" font-size="8.5" font-family="monospace">b</text>
    <text x="22" y="194" fill="#94a3b8" font-size="8.5" font-family="monospace">a</text>

    <!-- Barramento 4 (Inferior da Protoboard Inferior) -->
    <rect x="15" y="210" width="920" height="30" rx="4" fill="#e2e8f0" stroke="#cbd5e1" stroke-width="1"/>
    <line x1="25" y1="218" x2="925" y2="218" stroke="#10b981" stroke-width="3"/>
    <line x1="25" y1="232" x2="925" y2="232" stroke="#3b82f6" stroke-width="3"/>

    <!-- Rótulo Barramento 4 -->
    <rect x="380" y="212" width="370" height="15" rx="3" fill="#dcfce7" stroke="#10b981"/>
    <text x="386" y="223" fill="#166534" font-size="8.8" font-weight="900">BARRAMENTO 4 (VERMELHO): 3.3V (ALIMENTAÇÃO ESP32 / DHT / BMP)</text>
  </g>

  <!-- ================= MÓDULO FONTE MB102 (EXTREMA ESQUERDA) ================= -->
  <!-- Espetada diretamente nas colunas 1 a 12 dos Barramentos 1 e 2 -->
  <g transform="translate(25, 80)" filter="url(#cardShadow)">
    <rect x="0" y="0" width="190" height="260" rx="10" fill="url(#mb102Grad)" stroke="#475569" stroke-width="2.5"/>
    
    <!-- Identificação da Placa MB102 -->
    <rect x="10" y="10" width="170" height="32" rx="5" fill="#0f172a" stroke="#334155"/>
    <text x="18" y="28" fill="#38bdf8" font-size="12" font-weight="900" letter-spacing="1">FONTE MB102</text>
    <text x="18" y="38" fill="#94a3b8" font-size="7.5" font-weight="bold">BREADBOARD POWER SUPPLY</text>

    <!-- Conector Jack DC (Entrada 9V-12V) -->
    <g transform="translate(15, 52)">
      <rect x="0" y="0" width="42" height="46" rx="4" fill="#0f172a" stroke="#64748b" stroke-width="1.5"/>
      <circle cx="21" cy="23" r="10" fill="#1e293b" stroke="#cbd5e1" stroke-width="2"/>
      <circle cx="21" cy="23" r="4" fill="#e2e8f0"/>
      <text x="2" y="58" fill="#94a3b8" font-size="7.5" font-weight="bold">JACK 9-12V</text>
    </g>

    <!-- Conector USB Type-A (Entrada 5V) -->
    <g transform="translate(72, 52)">
      <rect x="0" y="0" width="48" height="46" rx="3" fill="#cbd5e1" stroke="#94a3b8" stroke-width="1.5"/>
      <rect x="6" y="8" width="36" height="30" fill="#0f172a"/>
      <text x="2" y="58" fill="#94a3b8" font-size="7.5" font-weight="bold">USB 5V IN</text>
    </g>

    <!-- Chave Liga/Desliga com Botão Vermelho -->
    <g transform="translate(138, 52)">
      <rect x="0" y="0" width="38" height="46" rx="4" fill="#1e293b" stroke="#475569"/>
      <circle cx="19" cy="20" r="12" fill="#dc2626" stroke="#991b1b" stroke-width="2"/>
      <circle cx="19" cy="20" r="6" fill="#ef4444"/>
      <text x="2" y="58" fill="#fca5a5" font-size="7.5" font-weight="bold">ON/OFF</text>
    </g>

    <!-- LED Verde de Alimentação Ativa -->
    <circle cx="155" cy="120" r="6" fill="#22c55e" stroke="#16a34a" stroke-width="1.5" filter="url(#glowGreen)"/>
    <text x="135" y="136" fill="#86efac" font-size="8" font-weight="bold">PWR LED</text>

    <!-- SELETOR 1: JUMPER SUPERIOR CONFIGURADO EM 5V -->
    <g transform="translate(15, 125)">
      <rect x="0" y="0" width="105" height="50" rx="6" fill="#0f172a" stroke="#ef4444" stroke-width="1.5"/>
      <text x="8" y="14" fill="#fca5a5" font-size="8" font-weight="bold">SELETOR SUPERIOR</text>
      <!-- Pinos 5V - OFF - 3.3V -->
      <circle cx="20" cy="32" r="3" fill="#cbd5e1"/>
      <circle cx="45" cy="32" r="3" fill="#cbd5e1"/>
      <circle cx="70" cy="32" r="3" fill="#cbd5e1"/>
      <!-- Jumper Amarelo fechando 5V e Centro -->
      <rect x="12" y="22" width="40" height="20" rx="4" fill="url(#jumperYellow)" stroke="#ca8a04" stroke-width="1.2"/>
      <text x="17" y="36" fill="#713f12" font-size="10" font-weight="900">5.0V</text>
      <text x="75" y="36" fill="#94a3b8" font-size="7.5">3.3V</text>
    </g>

    <!-- SELETOR 2: JUMPER INFERIOR CONFIGURADO EM 3.3V -->
    <g transform="translate(15, 190)">
      <rect x="0" y="0" width="105" height="50" rx="6" fill="#0f172a" stroke="#10b981" stroke-width="1.5"/>
      <text x="8" y="14" fill="#86efac" font-size="8" font-weight="bold">SELETOR INFERIOR</text>
      <!-- Pinos 5V - OFF - 3.3V -->
      <circle cx="20" cy="32" r="3" fill="#cbd5e1"/>
      <circle cx="45" cy="32" r="3" fill="#cbd5e1"/>
      <circle cx="70" cy="32" r="3" fill="#cbd5e1"/>
      <text x="14" y="36" fill="#94a3b8" font-size="7.5">5.0V</text>
      <!-- Jumper Amarelo fechando Centro e 3.3V -->
      <rect x="37" y="22" width="40" height="20" rx="4" fill="url(#jumperYellow)" stroke="#ca8a04" stroke-width="1.2"/>
      <text x="42" y="36" fill="#713f12" font-size="10" font-weight="900">3.3V</text>
    </g>

    <!-- Pinos Físicos da MB102 inseridos nos Barramentos 1 e 2 -->
    <!-- Saída Superior 5V -> Barramento 1 (+) -->
    <path d="M 190, 24 L 240, 24" stroke="#ef4444" stroke-width="5" stroke-linecap="round"/>
    <path d="M 190, 38 L 240, 38" stroke="#3b82f6" stroke-width="5" stroke-linecap="round"/>
    <!-- Saída Inferior 3.3V -> Barramento 2 (+) -->
    <path d="M 190, 224 L 240, 224" stroke="#10b981" stroke-width="5" stroke-linecap="round"/>
    <path d="M 190, 238 L 240, 238" stroke="#3b82f6" stroke-width="5" stroke-linecap="round"/>
  </g>

  <!-- ================= MALHA DE ENERGIA (PONTES E GND COMUM) ================= -->
  <!-- Ponte GND Comum: Barramento 1 (-) interligado com Barramento 2 (-) -->
  <path d="M 245, 122 C 220, 150 220, 270 245, 318" fill="none" stroke="#020617" stroke-width="3.5" stroke-dasharray="5,2"/>
  <circle cx="245" cy="122" r="4" fill="#020617"/>
  <circle cx="245" cy="318" r="4" fill="#020617"/>

  <!-- Ponte GND Comum: Barramento 2 (-) interligado com Barramento 3 (-) e 4 (-) -->
  <path d="M 265, 318 C 235, 360 235, 390 265, 432" fill="none" stroke="#020617" stroke-width="4"/>
  <path d="M 265, 432 C 235, 490 235, 590 265, 630" fill="none" stroke="#020617" stroke-width="4"/>
  <circle cx="265" cy="432" r="4" fill="#020617"/>
  <circle cx="265" cy="630" r="4" fill="#020617"/>

  <!-- Placa de Identificação GND Comum -->
  <rect x="175" y="360" width="85" height="22" rx="4" fill="#0f172a" stroke="#38bdf8" stroke-width="1.2"/>
  <text x="181" y="375" fill="#38bdf8" font-size="8.5" font-weight="900">GND COMUM</text>

  <!-- Distribuição de 3.3V: Barramento 2 (+) para Barramento 3 (+) e 4 (+) -->
  <path d="M 285, 305 C 265, 345 265, 380 285, 418" fill="none" stroke="#10b981" stroke-width="4"/>
  <path d="M 285, 418 C 265, 480 265, 580 285, 615" fill="none" stroke="#10b981" stroke-width="4"/>
  <circle cx="285" cy="305" r="4" fill="#10b981"/>
  <circle cx="285" cy="418" r="4" fill="#10b981"/>
  <circle cx="285" cy="615" r="4" fill="#10b981"/>

  <!-- Placa de Identificação da Ponte 3.3V -->
  <rect x="275" y="355" width="85" height="22" rx="4" fill="#064e3b" stroke="#10b981" stroke-width="1.2"/>
  <text x="283" y="370" fill="#ecfdf5" font-size="8.5" font-weight="900">DISTRIB. 3.3V</text>

  <!-- ================= COMPONENTES ================= -->

  <!-- 1. ESP32 NODEMCU (VÃO CENTRAL ENTRE AS DUAS PROTOBOARDS) -->
  <g transform="translate(370, 295)" filter="url(#cardShadow)">
    <rect x="0" y="0" width="210" height="135" rx="8" fill="url(#esp32Grad)" stroke="#64748b" stroke-width="2"/>
    
    <!-- Blindagem Metálica RF (ESP-WROOM-32) -->
    <rect x="75" y="24" width="82" height="88" rx="4" fill="url(#shieldGrad)" stroke="#cbd5e1" stroke-width="1.2"/>
    <text x="83" y="54" fill="#0f172a" font-size="10.5" font-weight="900">ESP-WROOM-32</text>
    <text x="85" y="70" fill="#334155" font-size="8" font-weight="bold">Wi-Fi &amp; BLE</text>
    <text x="85" y="84" fill="#059669" font-size="7.5" font-weight="bold">ADC1 Habilitado</text>

    <!-- Antena PCB em zigue-zague -->
    <rect x="166" y="30" width="34" height="76" fill="#064e3b" stroke="#047857" stroke-width="1"/>
    <path d="M 172, 40 H 194 V 50 H 172 V 60 H 194 V 70 H 172 V 80 H 194 V 90" fill="none" stroke="#d97706" stroke-width="2"/>

    <!-- Conector Micro-USB -->
    <rect x="-10" y="52" width="16" height="32" rx="2" fill="#cbd5e1" stroke="#475569" stroke-width="1.5"/>

    <!-- Pinos Superiores (Fileira 'a' da Protoboard Superior) -->
    <g fill="#e2e8f0" stroke="#475569" stroke-width="1">
      <rect x="15" y="-8" width="8" height="10"/><rect x="33" y="-8" width="8" height="10"/>
      <rect x="51" y="-8" width="8" height="10"/><rect x="69" y="-8" width="8" height="10"/>
      <rect x="87" y="-8" width="8" height="10"/><rect x="105" y="-8" width="8" height="10"/>
      <rect x="123" y="-8" width="8" height="10"/><rect x="141" y="-8" width="8" height="10"/>
      <rect x="159" y="-8" width="8" height="10"/><rect x="177" y="-8" width="8" height="10"/>
    </g>

    <!-- Pinos Inferiores (Fileira 'j' da Protoboard Inferior) -->
    <g fill="#e2e8f0" stroke="#475569" stroke-width="1">
      <rect x="15" y="133" width="8" height="10"/><rect x="33" y="133" width="8" height="10"/>
      <rect x="51" y="133" width="8" height="10"/><rect x="69" y="133" width="8" height="10"/>
      <rect x="87" y="133" width="8" height="10"/><rect x="105" y="133" width="8" height="10"/>
      <rect x="123" y="133" width="8" height="10"/><rect x="141" y="133" width="8" height="10"/>
      <rect x="159" y="133" width="8" height="10"/><rect x="177" y="133" width="8" height="10"/>
    </g>

    <text x="12" y="24" fill="#ffffff" font-size="11" font-weight="900">ESP32 NODEMCU</text>
    <text x="12" y="122" fill="#38bdf8" font-size="8" font-weight="bold">SOBRE O VÃO CENTRAL</text>
  </g>

  <!-- 2. SENSOR DHT22 (TEMPERATURA E UMIDADE - PROTO INFERIOR) -->
  <g transform="translate(630, 460)" filter="url(#cardShadow)">
    <rect x="0" y="0" width="75" height="105" rx="5" fill="#1e293b" stroke="#475569" stroke-width="1.5"/>
    <rect x="6" y="6" width="63" height="72" rx="3" fill="#ffffff" stroke="#cbd5e1" stroke-width="1"/>
    <!-- Grelha do DHT22 -->
    <line x1="16" y1="20" x2="59" y2="20" stroke="#94a3b8" stroke-width="2"/>
    <line x1="16" y1="32" x2="59" y2="32" stroke="#94a3b8" stroke-width="2"/>
    <line x1="16" y1="44" x2="59" y2="44" stroke="#94a3b8" stroke-width="2"/>
    <line x1="16" y1="56" x2="59" y2="56" stroke="#94a3b8" stroke-width="2"/>
    <text x="18" y="70" fill="#059669" font-size="9" font-weight="900">DHT22</text>
    <text x="11" y="94" fill="#f8fafc" font-size="8" font-weight="bold">+  OUT  -</text>
  </g>

  <!-- 3. SENSOR BMP280 (PRESSÃO E ALTITUDE I2C - PROTO INFERIOR) -->
  <g transform="translate(760, 470)" filter="url(#cardShadow)">
    <rect x="0" y="0" width="120" height="85" rx="5" fill="#6b21a8" stroke="#c084fc" stroke-width="1.5"/>
    <rect x="42" y="16" width="36" height="28" rx="2" fill="#cbd5e1" stroke="#475569" stroke-width="1.2"/>
    <circle cx="50" cy="24" r="2" fill="#0f172a"/>
    <text x="14" y="58" fill="#f3e8ff" font-size="9.5" font-weight="900">GY-BMP280 (3.3V)</text>
    <text x="8" y="76" fill="#e9d5ff" font-size="7" font-weight="bold">VCC GND SCL SDA CSB SDO</text>
  </g>

  <!-- 4. MÓDULO SENSOR DE LUZ LDR AZUL (PROTO SUPERIOR) -->
  <g transform="translate(630, 145)" filter="url(#cardShadow)">
    <rect x="0" y="0" width="85" height="95" rx="5" fill="#1d4ed8" stroke="#93c5fd" stroke-width="1.5"/>
    <rect x="14" y="12" width="24" height="24" fill="#0284c7" stroke="#38bdf8"/>
    <circle cx="26" cy="24" r="5" fill="#e2e8f0"/>
    <circle cx="60" cy="24" r="11" fill="#dc2626" stroke="#991b1b" stroke-width="1.5"/>
    <text x="16" y="52" fill="#ffffff" font-size="9.5" font-weight="900">LDR AZUL</text>
    <text x="10" y="80" fill="#bfdbfe" font-size="7.5" font-weight="bold">AO  DO  GND  VCC</text>
  </g>

  <!-- 5. PLUVIÔMETRO / SENSOR DE CHUVA (PROTO SUPERIOR) -->
  <g transform="translate(760, 145)" filter="url(#cardShadow)">
    <rect x="0" y="0" width="95" height="95" rx="5" fill="#1d4ed8" stroke="#93c5fd" stroke-width="1.5"/>
    <rect x="18" y="12" width="24" height="24" fill="#0284c7"/>
    <circle cx="30" cy="24" r="5" fill="#e2e8f0"/>
    <text x="12" y="52" fill="#ffffff" font-size="9" font-weight="900">CHUVA LM393</text>
    <text x="8" y="80" fill="#bfdbfe" font-size="7.5" font-weight="bold">VCC  GND  DO  AO</text>
  </g>
  <!-- Placa Coletora DSK MH-RD -->
  <g transform="translate(885, 145)" filter="url(#cardShadow)">
    <rect x="0" y="0" width="85" height="95" rx="5" fill="#f1f5f9" stroke="#94a3b8" stroke-width="1.5"/>
    <path d="M 12,18 H 73 M 12,28 H 73 M 12,38 H 73 M 12,48 H 73 M 12,58 H 73 M 12,68 H 73 M 12,78 H 73" stroke="#2563eb" stroke-width="2.5"/>
    <text x="8" y="90" fill="#0f172a" font-size="7.5" font-weight="900">PLACA DSK MH-RD</text>
    <line x1="-30" y1="22" x2="0" y2="22" stroke="#38bdf8" stroke-width="2.5"/>
    <line x1="-30" y1="34" x2="0" y2="34" stroke="#38bdf8" stroke-width="2.5"/>
  </g>

  <!-- 6. SENSOR MQ-135 (QUALIDADE DO AR / GASES - PROTO SUPERIOR) -->
  <g transform="translate(1005, 135)" filter="url(#cardShadow)">
    <rect x="0" y="0" width="110" height="115" rx="6" fill="#1d4ed8" stroke="#93c5fd" stroke-width="1.5"/>
    <!-- Cúpula Metálica do Sensor -->
    <circle cx="55" cy="45" r="32" fill="url(#shieldGrad)" stroke="#334155" stroke-width="2"/>
    <circle cx="55" cy="45" r="23" fill="none" stroke="#f8fafc" stroke-width="2" stroke-dasharray="3,3"/>
    <text x="28" y="49" fill="#0f172a" font-size="11" font-weight="900">MQ-135</text>
    <text x="18" y="88" fill="#fef08a" font-size="8.5" font-weight="bold">AQUECEDOR 5V</text>
    <text x="14" y="105" fill="#bfdbfe" font-size="7.5" font-weight="bold">VCC  GND  DO  AO</text>
  </g>

  <!-- ================= FIAÇÃO E CONEXÕES ELÉTRICAS ================= -->
  <!-- MQ-135: Alimentação 5V exclusiva vindo do Barramento 1 (Vermelho) -->
  <path d="M 1025, 135 L 1025, 105" stroke="#ef4444" stroke-width="4" stroke-linecap="round"/>
  <circle cx="1025" cy="105" r="4.5" fill="#ef4444"/>
  <rect x="990" y="70" width="130" height="20" rx="3" fill="#fee2e2" stroke="#ef4444"/>
  <text x="996" y="84" fill="#991b1b" font-size="8.5" font-weight="bold">VCC → 5V (BARR. 1)</text>

  <!-- MQ-135: Saída Analógica AO passando pelo Divisor Resistivo 1k/2k para GPIO 32 -->
  <path d="M 1095, 250 C 1095, 315 620, 315 580, 315" fill="none" stroke="#a855f7" stroke-width="3"/>
  <circle cx="580" cy="315" r="4" fill="#a855f7"/>
  <rect x="850" y="303" width="200" height="22" rx="4" fill="#1e293b" stroke="#a855f7" stroke-width="1.2"/>
  <text x="858" y="318" fill="#e9d5ff" font-size="8.5" font-weight="bold">DIVISOR 1kΩ / 2kΩ → GPIO 32 (ADC1)</text>

  <!-- DHT22: Sinal OUT para GPIO 4 (Fio Amarelo) -->
  <path d="M 667, 460 C 667, 435 605, 435 580, 428" fill="none" stroke="#eab308" stroke-width="3"/>
  <circle cx="580" cy="428" r="4" fill="#eab308"/>
  <rect x="600" y="420" width="60" height="18" rx="3" fill="#0f172a" stroke="#eab308"/>
  <text x="605" y="433" fill="#fde047" font-size="8.5" font-weight="900">GPIO 4</text>

  <!-- BMP280: Linhas I2C SDA (GPIO 21) e SCL (GPIO 22) -->
  <path d="M 808, 470 C 808, 455 610, 455 580, 435" fill="none" stroke="#3b82f6" stroke-width="3"/>
  <path d="M 796, 470 C 796, 445 605, 445 580, 432" fill="none" stroke="#10b981" stroke-width="3"/>
  <rect x="670" y="445" width="115" height="18" rx="3" fill="#0f172a" stroke="#38bdf8"/>
  <text x="676" y="458" fill="#38bdf8" font-size="8" font-weight="bold">SCL (22) / SDA (21)</text>

  <!-- LDR: Sinal Analógico AO para GPIO 34 (Fio Branco) -->
  <path d="M 642, 240 C 642, 280 600, 280 580, 287" fill="none" stroke="#ffffff" stroke-width="3"/>
  <circle cx="580" cy="287" r="4" fill="#ffffff"/>
  <rect x="650" y="260" width="95" height="18" rx="3" fill="#0f172a" stroke="#ffffff"/>
  <text x="656" y="273" fill="#ffffff" font-size="8" font-weight="bold">GPIO 34 (ADC1)</text>

  <!-- Sensor de Chuva: Sinal Analógico AO para GPIO 35 (Fio Laranja) -->
  <path d="M 835, 240 C 835, 290 605, 295 580, 295" fill="none" stroke="#f97316" stroke-width="3"/>
  <circle cx="580" cy="295" r="4" fill="#f97316"/>
  <rect x="750" y="280" width="95" height="18" rx="3" fill="#0f172a" stroke="#f97316"/>
  <text x="756" y="293" fill="#fb923c" font-size="8" font-weight="bold">GPIO 35 (ADC1)</text>

  <!-- ================= LEGENDA COMPLETA NO RODAPÉ ================= -->
  <g transform="translate(25, 660)">
    <rect x="0" y="0" width="1150" height="65" rx="8" fill="#1e293b" stroke="#334155" stroke-width="1.5" filter="url(#cardShadow)"/>
    <text x="20" y="22" fill="#38bdf8" font-size="10.5" font-weight="900">RESUMO DE ENGENHARIA ELÉTRICA &amp; NÍVEIS DE TENSÃO:</text>
    
    <rect x="20" y="34" width="14" height="14" rx="2" fill="#ef4444"/>
    <text x="40" y="45" fill="#fca5a5" font-size="9" font-weight="bold">Barramento 1 (5.0V Exclusivo MQ-135)</text>

    <rect x="290" y="34" width="14" height="14" rx="2" fill="#10b981"/>
    <text x="310" y="45" fill="#86efac" font-size="9" font-weight="bold">Barramentos 2, 3 e 4 (3.3V Lógica ESP32 &amp; Sensores)</text>

    <rect x="640" y="34" width="14" height="14" rx="2" fill="#020617" stroke="#cbd5e1"/>
    <text x="660" y="45" fill="#cbd5e1" font-size="9" font-weight="bold">Malha GND Unificada (Referência Comum 0V)</text>

    <rect x="920" y="34" width="14" height="14" rx="2" fill="#a855f7"/>
    <text x="940" y="45" fill="#e9d5ff" font-size="9" font-weight="bold">ADC1 Exclusivo (GPIO 32, 34, 35)</text>
  </g>
</svg>
"""

svg_path = "/home/wvs/Documents/ccomp-unip/2sem/pim2/ecopulse/hardware/assets/protoboard_esquematico_mb102.svg"
png_path = "/home/wvs/Documents/ccomp-unip/2sem/pim2/ecopulse/hardware/assets/protoboard_esquematico_mb102.png"

with open(svg_path, "w", encoding="utf-8") as f:
    f.write(svg_content)

print("SVG refinado salvo!")

cmd = [
    "google-chrome",
    "--headless",
    "--disable-gpu",
    f"--screenshot={png_path}",
    "--window-size=1200,740",
    "--default-background-color=00000000",
    svg_path
]
subprocess.run(cmd, check=True)
print("PNG gerado com sucesso!")
