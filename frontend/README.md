# EcoPulse Frontend — Apple iOS Weather Experience

Interface Web SPA responsiva inspirada no aplicativo **Clima (Weather) do iOS**, projetada com separação entre as **Condições Atuais** (Primeira Dobra) e o **Dashboard Analítico de Engenharia** (Segunda Dobra com *Scroll Peek*).

---

## 1. Estrutura Visual em Duas Dobras

### A. Primeira Dobra (Condições Atuais + *Peek* do Dashboard)
1. **Hero Flutuante Centralizado:** Indicador `HOME • ESTAÇÃO ECOPULSE`, cidade, temperatura atual em fonte ultrafina (`96px`), condição climática e extremos diários (`Máx. / Mín.`).
2. **Card de Alerta Meteorológico (`Storm & More` style):** Exibe anomalias capturadas pelo detector de *Deadband* do Cold Path (`/api/v1/telemetry/events`) ou o status de vigilância ativa.
3. **Card `Condições` (Faixa Horizontal):** Carrossel com `Agora` e leituras recentes, ícones vetoriais dinâmicos e seletor em pílula com 3 modos (`Temperatura`, `Chuva/Umidade` e `Gases/Pressão`).
4. **Peek do Dashboard (Quase Aparecendo na Base):** Convite visual à rolagem exibindo o card de **Janelas Consolidadas & Amplitude Térmica** com as barras horizontais gradientes laranjas (`20° ━━━●━━ 27°`).

### B. Segunda Dobra (Ao Rolar a Tela — Dashboard Completo)
* **Bento Grid dos 5 Sensores Físicos:** Qualidade do Ar (MQ-135), Precipitação (LM393), Sensação Térmica (Rothfusz), Umidade & Ponto de Orvalho (DHT22), Pressão & Altitude (BMP280) e Luminosidade (LDR).
* **Gráfico de Série Temporal (Chart.js)** e **Mapa de Cobertura Sensorial (Leaflet 450m)** + **Métricas ao Vivo do Pipeline Hot/Cold Path**.
* **Barra Inferior Flutuante (iOS Bottom Toolbar):** Atalhos diretos para Mapa, Topo e Dashboard Completo.
