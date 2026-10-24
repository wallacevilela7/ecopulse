import os
import subprocess

svg_content = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1320 800" width="100%" height="100%" style="background-color: #0b1120; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
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
      <feDropShadow dx="0" dy="6" stdDeviation="6" flood-color="#000000" flood-opacity="0.6"/>
    </filter>
    <filter id="glowGreen" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="3" result="blur" />
      <feComposite in="SourceGraphic" in2="blur" operator="over" />
    </filter>
  </defs>

  <rect width="1320" height="800" fill="url(#bgGrad)"/>

  <!-- ================= CABEÇALHO SUPERIOR ================= -->
  <g transform="translate(30, 15)">
    <rect x="0" y="0" width="1260" height="52" rx="8" fill="#1e293b" stroke="#334155" stroke-width="1.5" filter="url(#cardShadow)"/>
    <text x="25" y="32" fill="#38bdf8" font-size="14.5" font-weight="900" letter-spacing="1">LAYOUT DE MENOR CAMINHO E ZERO-CROSSING (JUMPERS EM U)</text>
    <text x="25" y="45" fill="#94a3b8" font-size="8.5" font-weight="600">DISTRIBUIÇÃO POR AFINIDADE DE BORDA: SENSORES DIGITAIS/I2C NO TOPO • SENSORES ANALÓGICOS NA BASE • FIAÇÃO RENTE</text>
    
    <!-- Badge de Otimização Topológica -->
    <rect x="850" y="10" width="395" height="32" rx="16" fill="#064e3b" stroke="#10b981" stroke-width="1.5"/>
    <circle cx="870" cy="26" r="6" fill="#34d399" filter="url(#glowGreen)"/>
    <text x="885" y="30" fill="#ecfdf5" font-size="10" font-weight="800">SEM EMARANHADO: 100% FIAÇÃO RENTE EM U</text>
  </g>

  <!-- ================= PROTOBOARD SUPERIOR ================= -->
  <g transform="translate(200, 85)" filter="url(#cardShadow)">
    <rect x="0" y="0" width="1070" height="260" rx="8" fill="url(#protoGrad)" stroke="#cbd5e1" stroke-width="2"/>
    <text x="910" y="24" fill="#64748b" font-size="11" font-weight="bold">PROTOBOARD SUPERIOR</text>
    
    <!-- Coordenadas das Colunas (1 a 63) -->
    <g fill="#94a3b8" font-size="7.5" font-family="monospace">
      <text x="45" y="47">1</text><text x="120" y="47">10</text><text x="180" y="47">16 (MQ)</text>
      <text x="290" y="47">25</text><text x="360" y="47">30</text><text x="470" y="47">43 (BMP)</text>
      <text x="590" y="47">54 (DHT)</text><text x="690" y="47">48 (ESP)</text><text x="850" y="47">60</text><text x="910" y="47">63</text>
    </g>

    <!-- Barramento 1 (Superior) -->
    <rect x="15" y="10" width="1040" height="30" rx="4" fill="#e2e8f0" stroke="#cbd5e1" stroke-width="1"/>
    <!-- Linha Azul (-) GND na borda externa -->
    <line x1="25" y1="18" x2="1045" y2="18" stroke="#3b82f6" stroke-width="3"/>
    <text x="1050" y="21" fill="#3b82f6" font-size="14" font-weight="900">-</text>
    <!-- Linha Vermelha (+) 5V na borda interna -->
    <line x1="25" y1="32" x2="1045" y2="32" stroke="#ef4444" stroke-width="3"/>
    <text x="1050" y="35" fill="#ef4444" font-size="12" font-weight="900">+</text>

    <!-- Rótulo Barramento 1 (5V Exclusivo) -->
    <rect x="230" y="12" width="380" height="15" rx="3" fill="#fee2e2" stroke="#ef4444"/>
    <text x="236" y="23" fill="#991b1b" font-size="8.8" font-weight="900">BARRAMENTO 1 (VERMELHO): 5.0V EXCLUSIVO P/ MQ-135</text>

    <!-- Matriz de Conexões: Fileiras 'j' a 'f' -->
    <rect x="15" y="52" width="1040" height="70" rx="4" fill="#ffffff" stroke="#e2e8f0" stroke-width="1"/>
    <text x="22" y="70" fill="#94a3b8" font-size="8.5" font-family="monospace">j</text>
    <text x="22" y="83" fill="#94a3b8" font-size="8.5" font-family="monospace">i</text>
    <text x="22" y="96" fill="#94a3b8" font-size="8.5" font-family="monospace">h</text>
    <text x="22" y="109" fill="#94a3b8" font-size="8.5" font-family="monospace">g</text>
    <text x="22" y="120" fill="#94a3b8" font-size="8.5" font-family="monospace">f</text>

    <!-- Canal Central Divisório (Protoboard Superior) -->
    <rect x="15" y="126" width="1040" height="14" fill="#cbd5e1"/>

    <!-- Matriz de Conexões: Fileiras 'e' a 'a' -->
    <rect x="15" y="144" width="1040" height="70" rx="4" fill="#ffffff" stroke="#e2e8f0" stroke-width="1"/>
    <text x="22" y="162" fill="#94a3b8" font-size="8.5" font-family="monospace">e (BMP &amp; DHT)</text>
    <text x="22" y="175" fill="#94a3b8" font-size="8.5" font-family="monospace">d</text>
    <text x="22" y="188" fill="#94a3b8" font-size="8.5" font-family="monospace">c</text>
    <text x="22" y="201" fill="#94a3b8" font-size="8.5" font-family="monospace">b (Jumpers Entrada)</text>
    <text x="22" y="212" fill="#0284c7" font-size="9" font-family="monospace" font-weight="900">a (Topo do ESP32)</text>

    <!-- Barramento 2 (Inferior da Protoboard Superior) -->
    <rect x="15" y="218" width="1040" height="32" rx="4" fill="#e2e8f0" stroke="#cbd5e1" stroke-width="1"/>
    <!-- Linha Vermelha (+) 3.3V -->
    <line x1="25" y1="226" x2="1045" y2="226" stroke="#10b981" stroke-width="3"/>
    <text x="1050" y="229" fill="#10b981" font-size="12" font-weight="900">+</text>
    <!-- Linha Azul (-) GND -->
    <line x1="25" y1="240" x2="1045" y2="240" stroke="#3b82f6" stroke-width="3"/>
    <text x="1050" y="243" fill="#3b82f6" font-size="14" font-weight="900">-</text>

    <!-- Rótulo Barramento 2 (3.3V Seguro) -->
    <rect x="230" y="220" width="290" height="15" rx="3" fill="#dcfce7" stroke="#10b981"/>
    <text x="236" y="231" fill="#166534" font-size="8.8" font-weight="900">BARRAMENTO 2 (VERMELHO): 3.3V SEGURO</text>
  </g>

  <!-- TRAVAS LATERAIS ENCAIXADAS (SUPORTEZINHO PLÁSTICO DAS PROTOBOARDS) -->
  <g transform="translate(185, 345)">
    <rect x="0" y="0" width="16" height="40" rx="3" fill="#cbd5e1" stroke="#94a3b8" stroke-width="1.5"/>
    <rect x="1085" y="0" width="16" height="40" rx="3" fill="#cbd5e1" stroke="#94a3b8" stroke-width="1.5"/>
    <text x="25" y="24" fill="#64748b" font-size="8.5" font-weight="bold">TRAVAS LATERAIS ACOPLADAS (PROTOS UNIDAS)</text>
  </g>

  <!-- ================= PROTOBOARD INFERIOR ================= -->
  <g transform="translate(200, 395)" filter="url(#cardShadow)">
    <rect x="0" y="0" width="1070" height="260" rx="8" fill="url(#protoGrad)" stroke="#cbd5e1" stroke-width="2"/>
    <text x="910" y="24" fill="#64748b" font-size="11" font-weight="bold">PROTOBOARD INFERIOR</text>

    <!-- Barramento 3 (Superior da Protoboard Inferior) -->
    <rect x="15" y="10" width="1040" height="32" rx="4" fill="#e2e8f0" stroke="#cbd5e1" stroke-width="1"/>
    <line x1="25" y1="18" x2="1045" y2="18" stroke="#10b981" stroke-width="3"/>
    <text x="1050" y="21" fill="#10b981" font-size="12" font-weight="900">+</text>
    <line x1="25" y1="32" x2="1045" y2="32" stroke="#3b82f6" stroke-width="3"/>
    <text x="1050" y="35" fill="#3b82f6" font-size="14" font-weight="900">-</text>

    <!-- Rótulo Barramento 3 -->
    <rect x="230" y="12" width="380" height="15" rx="3" fill="#dcfce7" stroke="#10b981"/>
    <text x="236" y="23" fill="#166534" font-size="8.8" font-weight="900">BARRAMENTO 3 (VERMELHO): 3.3V (ALIMENTA LDR &amp; CHUVA)</text>

    <!-- Matriz de Conexões: Fileiras 'j' a 'f' -->
    <rect x="15" y="52" width="1040" height="70" rx="4" fill="#ffffff" stroke="#e2e8f0" stroke-width="1"/>
    <text x="22" y="70" fill="#0284c7" font-size="9" font-family="monospace" font-weight="900">j (Base do ESP32)</text>
    <text x="22" y="83" fill="#94a3b8" font-size="8.5" font-family="monospace">i (Jumpers Entrada ADC)</text>
    <text x="22" y="96" fill="#94a3b8" font-size="8.5" font-family="monospace">h</text>
    <text x="22" y="109" fill="#94a3b8" font-size="8.5" font-family="monospace">g</text>
    <text x="22" y="120" fill="#94a3b8" font-size="8.5" font-family="monospace">f (LDR &amp; Chuva)</text>

    <!-- Canal Central Divisório (Protoboard Inferior) -->
    <rect x="15" y="126" width="1040" height="14" fill="#cbd5e1"/>

    <!-- Matriz de Conexões: Fileiras 'e' a 'a' (LIVRES) -->
    <rect x="15" y="144" width="1040" height="70" rx="4" fill="#ffffff" stroke="#e2e8f0" stroke-width="1"/>
    <text x="22" y="162" fill="#94a3b8" font-size="8.5" font-family="monospace">e</text>
    <text x="22" y="175" fill="#94a3b8" font-size="8.5" font-family="monospace">d</text>
    <text x="22" y="188" fill="#94a3b8" font-size="8.5" font-family="monospace">c</text>
    <text x="22" y="201" fill="#94a3b8" font-size="8.5" font-family="monospace">b</text>
    <text x="22" y="212" fill="#94a3b8" font-size="8.5" font-family="monospace">a</text>
    <text x="350" y="180" fill="#cbd5e1" font-size="10" font-weight="bold">ÁREA INFERIOR DESIMPEDIDA (LIVRE DE FIOS)</text>

    <!-- Barramento 4 (Inferior da Protoboard Inferior) -->
    <rect x="15" y="218" width="1040" height="32" rx="4" fill="#e2e8f0" stroke="#cbd5e1" stroke-width="1"/>
    <line x1="25" y1="226" x2="1045" y2="226" stroke="#10b981" stroke-width="3"/>
    <text x="1050" y="229" fill="#10b981" font-size="12" font-weight="900">+</text>
    <line x1="25" y1="240" x2="1045" y2="240" stroke="#3b82f6" stroke-width="3"/>
    <text x="1050" y="243" fill="#3b82f6" font-size="14" font-weight="900">-</text>

    <!-- Rótulo Barramento 4 -->
    <rect x="230" y="220" width="380" height="15" rx="3" fill="#dcfce7" stroke="#10b981"/>
    <text x="236" y="231" fill="#166534" font-size="8.8" font-weight="900">BARRAMENTO 4 (VERMELHO): 3.3V RESERVA EXPANSÃO</text>
  </g>

  <!-- ================= MÓDULO FONTE MB102 (EXTREMA ESQUERDA) ================= -->
  <g transform="translate(25, 80)" filter="url(#cardShadow)">
    <rect x="0" y="0" width="180" height="265" rx="10" fill="url(#mb102Grad)" stroke="#475569" stroke-width="2.5"/>
    
    <!-- Identificação da Placa MB102 -->
    <rect x="10" y="10" width="160" height="32" rx="5" fill="#0f172a" stroke="#334155"/>
    <text x="18" y="28" fill="#38bdf8" font-size="12" font-weight="900" letter-spacing="1">FONTE MB102</text>
    <text x="18" y="38" fill="#94a3b8" font-size="7.5" font-weight="bold">HW-131 BREADBOARD POWER</text>

    <!-- Conector USB Type-A -->
    <g transform="translate(15, 50)">
      <rect x="0" y="0" width="55" height="48" rx="3" fill="#cbd5e1" stroke="#94a3b8" stroke-width="1.5"/>
      <rect x="8" y="8" width="40" height="32" fill="#0f172a"/>
      <text x="2" y="60" fill="#94a3b8" font-size="7.5" font-weight="bold">USB 5V IN</text>
    </g>

    <!-- Conector Jack DC -->
    <g transform="translate(15, 120)">
      <rect x="0" y="0" width="45" height="48" rx="4" fill="#0f172a" stroke="#64748b" stroke-width="1.5"/>
      <circle cx="22" cy="24" r="11" fill="#1e293b" stroke="#cbd5e1" stroke-width="2"/>
      <circle cx="22" cy="24" r="4.5" fill="#e2e8f0"/>
      <text x="2" y="60" fill="#94a3b8" font-size="7.5" font-weight="bold">JACK 9-12V</text>
    </g>

    <!-- Chave Liga/Desliga -->
    <g transform="translate(15, 185)">
      <rect x="0" y="0" width="38" height="36" rx="4" fill="#1e293b" stroke="#475569"/>
      <circle cx="19" cy="18" r="10" fill="#dc2626" stroke="#991b1b" stroke-width="1.5"/>
      <circle cx="19" cy="18" r="5" fill="#ffffff"/>
      <text x="2" y="48" fill="#fca5a5" font-size="7.5" font-weight="bold">ON/OFF</text>
    </g>

    <!-- LED Verde de Alimentação Ativa -->
    <circle cx="150" cy="95" r="6" fill="#22c55e" stroke="#16a34a" stroke-width="1.5" filter="url(#glowGreen)"/>
    <text x="130" y="112" fill="#86efac" font-size="8" font-weight="bold">PWR LED</text>

    <!-- SELETOR 1: JUMPER SUPERIOR CONFIGURADO EM 5V -->
    <g transform="translate(80, 52)">
      <rect x="0" y="0" width="85" height="42" rx="5" fill="#0f172a" stroke="#ef4444" stroke-width="1.2"/>
      <text x="6" y="12" fill="#fca5a5" font-size="7.5" font-weight="bold">JUMPER 5V (SUP)</text>
      <circle cx="16" cy="26" r="3" fill="#cbd5e1"/>
      <circle cx="38" cy="26" r="3" fill="#cbd5e1"/>
      <circle cx="60" cy="26" r="3" fill="#cbd5e1"/>
      <!-- Jumper Amarelo em 5V -->
      <rect x="10" y="18" width="32" height="16" rx="3" fill="url(#jumperYellow)" stroke="#ca8a04" stroke-width="1.2"/>
      <text x="14" y="30" fill="#713f12" font-size="9" font-weight="900">5.0V</text>
    </g>

    <!-- SELETOR 2: JUMPER INFERIOR CONFIGURADO EM 3.3V -->
    <g transform="translate(75, 190)">
      <rect x="0" y="0" width="90" height="42" rx="5" fill="#0f172a" stroke="#10b981" stroke-width="1.2"/>
      <text x="6" y="12" fill="#86efac" font-size="7.5" font-weight="bold">JUMPER 3.3V (INF)</text>
      <circle cx="16" cy="26" r="3" fill="#cbd5e1"/>
      <circle cx="38" cy="26" r="3" fill="#cbd5e1"/>
      <circle cx="60" cy="26" r="3" fill="#cbd5e1"/>
      <!-- Jumper Amarelo em 3.3V -->
      <rect x="34" y="18" width="32" height="16" rx="3" fill="url(#jumperYellow)" stroke="#ca8a04" stroke-width="1.2"/>
      <text x="37" y="30" fill="#713f12" font-size="9" font-weight="900">3.3V</text>
    </g>

    <!-- Pinos Físicos da MB102 inseridos nos Barramentos 1 e 2 -->
    <path d="M 180, 24 L 215, 24" stroke="#ef4444" stroke-width="5" stroke-linecap="round"/>
    <path d="M 180, 38 L 215, 38" stroke="#3b82f6" stroke-width="5" stroke-linecap="round"/>
    <path d="M 180, 230 L 215, 230" stroke="#10b981" stroke-width="5" stroke-linecap="round"/>
    <path d="M 180, 244 L 215, 244" stroke="#3b82f6" stroke-width="5" stroke-linecap="round"/>
  </g>

  <!-- ================= MICROCONTROLADOR ESP32 NODEMCU (COLUNAS 48 A 62) ================= -->
  <g transform="translate(940, 310)" filter="url(#cardShadow)">
    <rect x="0" y="0" width="220" height="145" rx="8" fill="url(#esp32Grad)" stroke="#64748b" stroke-width="2.5"/>
    
    <!-- Blindagem Metálica RF (ESP-WROOM-32) -->
    <rect x="25" y="24" width="85" height="95" rx="4" fill="url(#shieldGrad)" stroke="#cbd5e1" stroke-width="1.2"/>
    <text x="32" y="55" fill="#0f172a" font-size="10.5" font-weight="900">ESP-WROOM-32</text>
    <text x="34" y="72" fill="#334155" font-size="8.5" font-weight="bold">Wi-Fi &amp; BLE</text>
    <text x="34" y="88" fill="#059669" font-size="8" font-weight="bold">ADC1 Habilitado</text>

    <!-- Antena PCB em zigue-zague (voltada para o centro) -->
    <rect x="-8" y="32" width="28" height="80" fill="#064e3b" stroke="#047857" stroke-width="1"/>
    <path d="M -2, 42 H 14 V 52 H -2 V 62 H 14 V 72 H -2 V 82 H 14 V 92" fill="none" stroke="#d97706" stroke-width="2"/>

    <!-- Conector Micro-USB (no lado DIREITO, voltado para fora!) -->
    <rect x="210" y="55" width="18" height="35" rx="2" fill="#cbd5e1" stroke="#475569" stroke-width="1.5"/>
    <text x="145" y="76" fill="#94a3b8" font-size="8" font-weight="bold">USB PC</text>

    <!-- Botões EN e BOOT -->
    <circle cx="195" cy="35" r="5" fill="#475569"/>
    <circle cx="195" cy="110" r="5" fill="#475569"/>
    <text x="175" y="38" fill="#cbd5e1" font-size="7">EN</text>
    <text x="165" y="113" fill="#cbd5e1" font-size="7">BOOT</text>

    <!-- PINOS SUPERIORES: Espetados na Fileira 'a' da Protoboard Superior -->
    <g fill="#e2e8f0" stroke="#475569" stroke-width="1">
      <rect x="20" y="-8" width="8" height="10"/><rect x="36" y="-8" width="8" height="10"/>
      <rect x="52" y="-8" width="8" height="10"/><rect x="68" y="-8" width="8" height="10"/>
      <rect x="84" y="-8" width="8" height="10"/><rect x="100" y="-8" width="8" height="10"/>
      <rect x="116" y="-8" width="8" height="10"/><rect x="132" y="-8" width="8" height="10"/>
      <rect x="148" y="-8" width="8" height="10"/><rect x="164" y="-8" width="8" height="10"/>
      <rect x="180" y="-8" width="8" height="10"/><rect x="196" y="-8" width="8" height="10"/>
    </g>
    <!-- Rótulos Pinos Superiores -->
    <text x="18" y="16" fill="#34d399" font-size="7.5" font-weight="bold">D22</text>
    <text x="66" y="16" fill="#38bdf8" font-size="7.5" font-weight="bold">D21</text>
    <text x="130" y="16" fill="#fde047" font-size="7.5" font-weight="bold">D4</text>
    <text x="176" y="16" fill="#cbd5e1" font-size="7.5" font-weight="bold">GND</text>
    <text x="194" y="16" fill="#86efac" font-size="7.5" font-weight="900">3V3</text>

    <!-- PINOS INFERIORES: Espetados na Fileira 'j' da Protoboard Inferior -->
    <g fill="#e2e8f0" stroke="#475569" stroke-width="1">
      <rect x="20" y="143" width="8" height="10"/><rect x="36" y="143" width="8" height="10"/>
      <rect x="52" y="143" width="8" height="10"/><rect x="68" y="143" width="8" height="10"/>
      <rect x="84" y="143" width="8" height="10"/><rect x="100" y="143" width="8" height="10"/>
      <rect x="116" y="143" width="8" height="10"/><rect x="132" y="143" width="8" height="10"/>
      <rect x="148" y="143" width="8" height="10"/><rect x="164" y="143" width="8" height="10"/>
      <rect x="180" y="143" width="8" height="10"/><rect x="196" y="143" width="8" height="10"/>
    </g>
    <!-- Rótulos Pinos Inferiores -->
    <text x="48" y="126" fill="#ffffff" font-size="7.5" font-weight="bold">D34</text>
    <text x="64" y="126" fill="#fb923c" font-size="7.5" font-weight="bold">D35</text>
    <text x="80" y="126" fill="#c084fc" font-size="7.5" font-weight="bold">D32</text>
    <text x="176" y="126" fill="#cbd5e1" font-size="7.5" font-weight="bold">GND</text>
    <text x="194" y="126" fill="#fca5a5" font-size="7.5" font-weight="bold">VIN</text>

    <text x="35" y="112" fill="#ffffff" font-size="9.5" font-weight="900">ESP32 NODEMCU (DIREITA)</text>
  </g>

  <!-- ================= PROTOBOARD SUPERIOR: CLUSTER DIGITAL & I2C ================= -->

  <!-- 1. MQ-135 AO LADO DA MB102 (COLUNAS 16 A 19 - PROTO SUPERIOR) -->
  <g transform="translate(360, 140)" filter="url(#cardShadow)">
    <rect x="0" y="0" width="85" height="105" rx="6" fill="#1d4ed8" stroke="#93c5fd" stroke-width="1.5"/>
    <circle cx="42" cy="40" r="26" fill="url(#shieldGrad)" stroke="#334155" stroke-width="2"/>
    <circle cx="42" cy="40" r="19" fill="none" stroke="#f8fafc" stroke-width="2" stroke-dasharray="3,3"/>
    <text x="20" y="44" fill="#0f172a" font-size="10" font-weight="900">MQ-135</text>
    <text x="10" y="78" fill="#fef08a" font-size="7.5" font-weight="bold">5V DIRETO BARR 1</text>
    <text x="6" y="96" fill="#bfdbfe" font-size="7" font-weight="bold">VCC  GND  DO  AO</text>
  </g>
  <!-- Jumper U 2 furos: VCC no Barramento 1 (5V) -->
  <path d="M 372, 140 V 118" stroke="#ef4444" stroke-width="3" stroke-linecap="round"/>
  <circle cx="372" cy="118" r="3.5" fill="#ef4444"/>
  <!-- Jumper U 2 furos: GND no Barramento 1 (GND) -->
  <path d="M 388, 140 V 103" stroke="#020617" stroke-width="3" stroke-linecap="round"/>
  <circle cx="388" cy="103" r="3.5" fill="#020617"/>

  <!-- Divisor Resistivo MQ-135 (Colunas 20-22) -->
  <g transform="translate(460, 155)">
    <rect x="0" y="0" width="95" height="35" rx="4" fill="#1e293b" stroke="#cbd5e1" stroke-width="1"/>
    <text x="6" y="14" fill="#f8fafc" font-size="7.5" font-weight="bold">DIVISOR RESISTIVO</text>
    <text x="6" y="27" fill="#86efac" font-size="7.5">1kΩ (série) + 2kΩ (GND)</text>
  </g>
  <line x1="432" y1="235" x2="460" y2="175" stroke="#c084fc" stroke-width="2"/>
  <!-- Linha única de sinal atenuado para D32 -->
  <path d="M 555, 175 C 650, 175 750, 360 1022, 453" fill="none" stroke="#c084fc" stroke-width="2.5"/>
  <circle cx="1022" cy="453" r="3.5" fill="#c084fc"/>
  <rect x="700" y="340" width="160" height="18" rx="3" fill="#1e293b" stroke="#c084fc"/>
  <text x="706" y="353" fill="#e9d5ff" font-size="8" font-weight="bold">SINAL ATENUADO → GPIO 32</text>

  <!-- 2. SENSOR BMP280 (COLUNAS 43 A 48 - PROTO SUPERIOR FILEIRA 'e') -->
  <g transform="translate(680, 230)" filter="url(#cardShadow)">
    <rect x="0" y="0" width="115" height="75" rx="5" fill="#6b21a8" stroke="#c084fc" stroke-width="1.5"/>
    <rect x="42" y="12" width="30" height="22" rx="2" fill="#cbd5e1" stroke="#475569" stroke-width="1"/>
    <circle cx="50" cy="18" r="1.5" fill="#0f172a"/>
    <text x="12" y="48" fill="#f3e8ff" font-size="8.5" font-weight="900">GY-BMP280 (3.3V)</text>
    <text x="8" y="65" fill="#e9d5ff" font-size="6.8" font-weight="bold">VCC GND SCL SDA CSB SDO</text>
  </g>
  <!-- VCC & GND do BMP280 ligados com Jumper U 2 furos no Barramento 2 (3.3V) -->
  <path d="M 692, 305 V 315" stroke="#10b981" stroke-width="3" stroke-linecap="round"/>
  <circle cx="692" cy="315" r="3.5" fill="#10b981"/>
  <path d="M 708, 305 V 325" stroke="#020617" stroke-width="3" stroke-linecap="round"/>
  <circle cx="708" cy="325" r="3.5" fill="#020617"/>
  <path d="M 785, 305 V 325" stroke="#020617" stroke-width="3" stroke-linecap="round"/> <!-- SDO ao GND -->
  
  <!-- Jumper Rígido em U: SCL (BMP) -> D22 (ESP32) [APENAS 4 FUROS HORIZONTAIS!] -->
  <path d="M 725, 230 C 725, 190 958, 190 958, 302" fill="none" stroke="#34d399" stroke-width="3"/>
  <circle cx="725" cy="230" r="3.5" fill="#34d399"/><circle cx="958" cy="302" r="3.5" fill="#34d399"/>
  <rect x="735" y="180" width="105" height="16" rx="3" fill="#064e3b" stroke="#34d399"/>
  <text x="740" y="191" fill="#86efac" font-size="7.5" font-weight="bold">SCL (U 4 FUROS) → D22</text>

  <!-- Jumper Rígido em U: SDA (BMP) -> D21 (ESP32) [APENAS 6 FUROS HORIZONTAIS!] -->
  <path d="M 740, 230 C 740, 205 1006, 205 1006, 302" fill="none" stroke="#38bdf8" stroke-width="3"/>
  <circle cx="740" cy="230" r="3.5" fill="#38bdf8"/><circle cx="1006" cy="302" r="3.5" fill="#38bdf8"/>
  <rect x="850" y="198" width="105" height="16" rx="3" fill="#0c4a6e" stroke="#38bdf8"/>
  <text x="855" y="209" fill="#bae6fd" font-size="7.5" font-weight="bold">SDA (U 6 FUROS) → D21</text>

  <!-- 3. SENSOR DHT22 (COLUNAS 54 A 57 - PROTO SUPERIOR FILEIRA 'e') -->
  <g transform="translate(830, 220)" filter="url(#cardShadow)">
    <rect x="0" y="0" width="65" height="85" rx="5" fill="#1e293b" stroke="#475569" stroke-width="1.5"/>
    <rect x="5" y="5" width="55" height="55" rx="3" fill="#ffffff" stroke="#cbd5e1" stroke-width="1"/>
    <text x="14" y="42" fill="#059669" font-size="8.5" font-weight="900">DHT22</text>
    <text x="8" y="74" fill="#f8fafc" font-size="7.5" font-weight="bold">+  OUT  -</text>
  </g>
  <!-- VCC & GND do DHT22 ligados no Barramento 2 -->
  <path d="M 840, 305 V 315" stroke="#10b981" stroke-width="3" stroke-linecap="round"/>
  <circle cx="840" cy="315" r="3.5" fill="#10b981"/>
  <path d="M 885, 305 V 325" stroke="#020617" stroke-width="3" stroke-linecap="round"/>
  <circle cx="885" cy="325" r="3.5" fill="#020617"/>

  <!-- Jumper Rígido em U: OUT (DHT22) -> D4 (ESP32) [APENAS 2 FUROS HORIZONTAIS!] -->
  <path d="M 862, 220 C 862, 170 1070, 170 1070, 302" fill="none" stroke="#fde047" stroke-width="3"/>
  <circle cx="862" cy="220" r="3.5" fill="#fde047"/><circle cx="1070" cy="302" r="3.5" fill="#fde047"/>
  <rect x="915" y="162" width="125" height="16" rx="3" fill="#713f12" stroke="#fde047"/>
  <text x="920" y="173" fill="#fef08a" font-size="7.5" font-weight="bold">OUT (U 2-3 FUROS) → D4</text>


  <!-- ================= PROTOBOARD INFERIOR: CLUSTER ANALÓGICO ADC1 ================= -->

  <!-- 4. SENSOR DE CHUVA LM393 (COLUNAS 36 A 39 - PROTO INFERIOR FILEIRA 'f') -->
  <g transform="translate(620, 460)" filter="url(#cardShadow)">
    <rect x="0" y="0" width="85" height="90" rx="5" fill="#1d4ed8" stroke="#93c5fd" stroke-width="1.5"/>
    <rect x="14" y="10" width="20" height="20" fill="#0284c7"/>
    <circle cx="24" cy="20" r="4" fill="#e2e8f0"/>
    <text x="8" y="48" fill="#ffffff" font-size="8" font-weight="900">CHUVA LM393</text>
    <text x="8" y="76" fill="#bfdbfe" font-size="7" font-weight="bold">VCC  GND  DO  AO</text>
  </g>
  <!-- VCC e GND do LM393 no Barramento 3 (3.3V) -->
  <path d="M 632, 460 V 425" stroke="#10b981" stroke-width="3" stroke-linecap="round"/>
  <circle cx="632" cy="425" r="3.5" fill="#10b981"/>
  <path d="M 650, 460 V 440" stroke="#020617" stroke-width="3" stroke-linecap="round"/>
  <circle cx="650" cy="440" r="3.5" fill="#020617"/>

  <!-- Jumper Rígido em U: AO CHUVA -> D35 (ESP32) [DIRETO NA MESMA BORDA!] -->
  <path d="M 692, 550 C 692, 585 1006, 585 1006, 453" fill="none" stroke="#fb923c" stroke-width="3"/>
  <circle cx="692" cy="550" r="3.5" fill="#fb923c"/><circle cx="1006" cy="453" r="3.5" fill="#fb923c"/>
  <rect x="740" y="575" width="135" height="16" rx="3" fill="#7c2d12" stroke="#fb923c"/>
  <text x="745" y="586" fill="#fed7aa" font-size="7.5" font-weight="bold">AO CHUVA (U 12 FUROS) → D35</text>

  <!-- 5. MÓDULO LDR AZUL (COLUNAS 44 A 47 - PROTO INFERIOR FILEIRA 'f') -->
  <g transform="translate(760, 460)" filter="url(#cardShadow)">
    <rect x="0" y="0" width="85" height="90" rx="5" fill="#1d4ed8" stroke="#93c5fd" stroke-width="1.5"/>
    <rect x="14" y="10" width="20" height="20" fill="#0284c7" stroke="#38bdf8"/>
    <circle cx="24" cy="20" r="4" fill="#e2e8f0"/>
    <circle cx="56" cy="20" r="9" fill="#dc2626" stroke="#991b1b" stroke-width="1.5"/>
    <text x="14" y="48" fill="#ffffff" font-size="8.5" font-weight="900">LDR AZUL</text>
    <text x="8" y="76" fill="#bfdbfe" font-size="7" font-weight="bold">AO  DO  GND  VCC</text>
  </g>
  <!-- VCC e GND do LDR no Barramento 3 -->
  <path d="M 830, 460 V 425" stroke="#10b981" stroke-width="3" stroke-linecap="round"/>
  <circle cx="830" cy="425" r="3.5" fill="#10b981"/>
  <path d="M 810, 460 V 440" stroke="#020617" stroke-width="3" stroke-linecap="round"/>
  <circle cx="810" cy="440" r="3.5" fill="#020617"/>

  <!-- Jumper Rígido em U: AO LDR -> D34 (ESP32) [APENAS 7 FUROS HORIZONTAIS!] -->
  <path d="M 772, 550 C 772, 568 990, 568 990, 453" fill="none" stroke="#ffffff" stroke-width="3"/>
  <circle cx="772" cy="550" r="3.5" fill="#ffffff"/><circle cx="990" cy="453" r="3.5" fill="#ffffff"/>
  <rect x="830" y="555" width="125" height="16" rx="3" fill="#1e293b" stroke="#ffffff"/>
  <text x="835" y="566" fill="#ffffff" font-size="7.5" font-weight="bold">AO LDR (U 7 FUROS) → D34</text>

  <!-- ================= PONTES DA COLUNA 30 E GND COMUM ================= -->
  <!-- Pontes da Coluna 30 (Jumpers em U de 3 furos) -->
  <g stroke="#f59e0b" stroke-width="3" fill="none">
    <path d="M 550, 95 H 570"/><path d="M 550, 115 H 570"/>
    <path d="M 550, 305 H 570"/><path d="M 550, 325 H 570"/>
    <path d="M 550, 405 H 570"/><path d="M 550, 425 H 570"/>
    <path d="M 550, 615 H 570"/><path d="M 550, 635 H 570"/>
  </g>
  <rect x="500" y="300" width="120" height="18" rx="3" fill="#78350f" stroke="#f59e0b"/>
  <text x="506" y="312" fill="#fef3c7" font-size="7.5" font-weight="bold">PONTES DA COLUNA 30</text>

  <!-- Malha GND Comum (Jumpers Pretos) -->
  <path d="M 225, 103 C 205, 120 205, 290 225, 325" fill="none" stroke="#020617" stroke-width="3.5" stroke-dasharray="4,2"/>
  <circle cx="225" cy="103" r="3.5" fill="#020617"/>
  <circle cx="225" cy="325" r="3.5" fill="#020617"/>
  <path d="M 235, 325 C 215, 360 215, 380 235, 427" fill="none" stroke="#020617" stroke-width="4"/>
  <circle cx="235" cy="427" r="3.5" fill="#020617"/>
  <path d="M 235, 427 C 215, 480 215, 600 235, 635" fill="none" stroke="#020617" stroke-width="4"/>
  <circle cx="235" cy="635" r="3.5" fill="#020617"/>

  <!-- Distribuição de 3.3V -->
  <path d="M 255, 311 C 240, 350 240, 375 255, 413" fill="none" stroke="#10b981" stroke-width="4"/>
  <circle cx="255" cy="311" r="3.5" fill="#10b981"/><circle cx="255" cy="413" r="3.5" fill="#10b981"/>
  <path d="M 255, 413 C 240, 480 240, 580 255, 621" fill="none" stroke="#10b981" stroke-width="4"/>
  <circle cx="255" cy="621" r="3.5" fill="#10b981"/>

  <!-- ================= PAINEL DE JUMPERS RÍGIDOS E LEGENDA ================= -->
  <g transform="translate(30, 675)">
    <rect x="0" y="0" width="1260" height="110" rx="8" fill="#1e293b" stroke="#334155" stroke-width="1.5" filter="url(#cardShadow)"/>
    <text x="25" y="24" fill="#38bdf8" font-size="11" font-weight="900">GUIA DE JUMPERS RÍGIDOS EM U (DIRETO DA SUA FOTO) APLICADOS AO CIRCUITO:</text>
    
    <!-- Exemplos de Jumpers Rígidos em U -->
    <g transform="translate(25, 40)">
      <!-- Jumper 2 furos (Verde pequeno) -->
      <path d="M 0,20 V 5 H 12 V 20" stroke="#22c55e" stroke-width="2.5" fill="none"/>
      <text x="-4" y="34" fill="#86efac" font-size="7">2 Furos (VCC/GND)</text>

      <!-- Jumper 3 furos (Laranja) -->
      <path d="M 65,20 V 5 H 85 V 20" stroke="#f97316" stroke-width="2.5" fill="none"/>
      <text x="65" y="34" fill="#fdba74" font-size="7">3 Furos (OUT DHT)</text>

      <!-- Jumper 4-5 furos (Vermelho) -->
      <path d="M 130,20 V 5 H 165 V 20" stroke="#ef4444" stroke-width="2.5" fill="none"/>
      <text x="130" y="34" fill="#fca5a5" font-size="7">4-5 Furos (SCL)</text>

      <!-- Jumper 6-7 furos (Amarelo) -->
      <path d="M 205,20 V 5 H 255 V 20" stroke="#eab308" stroke-width="2.5" fill="none"/>
      <text x="205" y="34" fill="#fef08a" font-size="7">7 Furos (AO LDR)</text>

      <!-- Jumper 10-12 furos (Azul) -->
      <path d="M 285,20 V 5 H 350 V 20" stroke="#3b82f6" stroke-width="2.5" fill="none"/>
      <text x="285" y="34" fill="#93c5fd" font-size="7">12 Furos (AO Chuva)</text>
    </g>

    <!-- Legenda de Tensões e Funções -->
    <g transform="translate(480, 35)">
      <rect x="0" y="0" width="14" height="14" rx="2" fill="#ef4444"/>
      <text x="20" y="11" fill="#fca5a5" font-size="8.5" font-weight="bold">5.0V Exclusivo (Barramento 1 - Aquecedor MQ-135)</text>

      <rect x="0" y="24" width="14" height="14" rx="2" fill="#10b981"/>
      <text x="20" y="35" fill="#86efac" font-size="8.5" font-weight="bold">3.3V Seguro (Barramentos 2, 3 e 4 - Lógica do ESP32 e Sensores)</text>
    </g>

    <g transform="translate(870, 35)">
      <rect x="0" y="0" width="14" height="14" rx="2" fill="#020617" stroke="#cbd5e1"/>
      <text x="20" y="11" fill="#cbd5e1" font-size="8.5" font-weight="bold">GND Comum Unificado (Referência Única 0V)</text>

      <rect x="0" y="24" width="14" height="14" rx="2" fill="#c084fc"/>
      <text x="20" y="35" fill="#e9d5ff" font-size="8.5" font-weight="bold">ADC1 Exclusivo no ESP32 (GPIOs 32, 34, 35)</text>
    </g>
  </g>
</svg>
"""

svg_path = "/home/wvs/Documents/ccomp-unip/2sem/pim2/ecopulse/hardware/assets/protoboard_esquematico_mb102.svg"
png_path = "/home/wvs/Documents/ccomp-unip/2sem/pim2/ecopulse/hardware/assets/protoboard_esquematico_mb102.png"

with open(svg_path, "w", encoding="utf-8") as f:
    f.write(svg_content)

print("SVG de Menor Caminho salvo!")

cmd = [
    "google-chrome",
    "--headless",
    "--disable-gpu",
    f"--screenshot={png_path}",
    "--window-size=1320,800",
    "--default-background-color=00000000",
    svg_path
]
subprocess.run(cmd, check=True)
print("PNG de Menor Caminho gerado com sucesso!")
