# EcoPulse Frontend v3.0 — Climatempo + Google Weather + Apple Bento

Interface Web SPA responsiva que combina a clareza de dados do **Climatempo**, a simplicidade visual e curvas suaves do **Google Weather** e a organização modular em mini-cards Bento do aplicativo **Clima do iPhone**, com suporte nativo a modo claro e escuro.

---

## 1. Arquitetura Visual e Componentes

### A. Seção Principal — Condições Agora e Sensores Ao Vivo (`hero-bento-grid`)
1. **Card Principal (Estilo Google Weather + Climatempo):**
   - Localização dinâmica (`Agora na Estação • Bairro / Cidade, UF`), condição climática resumida e ícone vetorial colorido dinâmico (Sol, Parcialmente Nublado, Noite ou Chuva).
   - Temperatura atual em destaque (`°C`), pílulas de mínima (`↓` azul) e máxima (`↑` laranja), **Sensação Térmica** e **Ponto de Orvalho** (equação de Magnus-Tetens).
   - **Gráfico de Curva Suave em Abas (Chart.js):** 4 modos interativos (`Temperatura`, `Umidade e Chuva`, `Luz e Ar` e `Pressão`) atualizados em tempo real via Server-Sent Events (SSE).
2. **Grade Direita de 6 Mini-Cards Bento (Estilo iPhone):**
   - **Chuva (Pluviômetro LM393):** Percentual de precipitação, barra de progresso e estado (`Sem chuva` / `Chovendo`).
   - **Umidade Relativa (DHT22):** Percentual e faixa de conforto humano (`40% a 70%`).
   - **Luminosidade Ambiente (LDR 5mm):** Percentual calibrado (`0%` a `100%`) e classificação (`Baixa`, `Moderada`, `Intensa`).
   - **Qualidade do Ar (MQ-135):** Concentração estimada em `ppm` e pico registrado no período.
   - **Pressão Atmosférica (BMP280):** Valor em `hPa`, extremos e tendência barométrica (`Estável`, `Subindo` ou `Caindo`).
   - **Altitude Local & Diagnóstico Wi-Fi:** Altitude barométrica calculada (`m`) e potência do sinal RSSI (`dBm`).

### B. Seção Inferior — Histórico Consolidado, Alertas e Geolocalização Híbrida
1. **Histórico de Medições (Estilo Climatempo 15 Dias):** Lista de medições consolidadas com horário local, indicador de chuva, barras horizontais de amplitude térmica (`Mín ━━━ Máx`) e metadados de luz/umidade, além da aba de **Alertas / Eventos** do detector de *Deadband*.
2. **Geolocalização Híbrida em 3 Camadas (`js/map.js`):**
   - **Camada 1:** Geolocalização precisa via HTML5 (`navigator.geolocation` habilitada pelo HTTPS em `https://ecopulse-unip.duckdns.org`).
   - **Camada 2:** Fallback automático por geolocalização de IP (`ipwho.is`).
   - **Camada 3:** Geocodificação reversa via **OpenStreetMap Nominatim** (bairro, cidade e estado) e mapa interativo **Leaflet + OpenStreetMap** com pino arrastável.
3. **Resumo Operacional do Pipeline Hot/Cold Path:** Contador ao vivo de amostras em RAM, janelas salvas no banco relacional e percentual de economia de I/O de disco.
