# EcoPulse — Frontend Dashboard (Apple iOS Style)

Dashboard web de monitoramento meteorológico da estação **EcoPulse**, inspirado na linguagem visual e de experiência de usuário (UX/UI) da **Apple** (iOS Weather, Apple Health e macOS Sonoma).

---

## 1. Características de Design & Arquitetura

* **Estética Apple Dark Mode:**
  * Efeito *Glassmorphism* com `backdrop-filter: blur(28px) saturate(190%)` e bordas translúcidas de 1px.
  * Tipografia nativa San Francisco (`-apple-system`, `SF Pro Display`, `SF Pro Text`).
  * Hero Card com indicador de temperatura em grande escala e sumário em tempo real.
  * *Bento Grid* responsivo com cartões arredondados (`22px`) e microinterações táteis.
* **Carregamento Instantâneo & Desempenho:**
  * Desenvolvido puramente com **HTML5 Semântico**, **CSS3 Moderno** e **JavaScript ES6+**.
  * Zero dependências de frameworks pesados (sem React, Vue ou bundles de build de centenas de megabytes).
  * Compactação Gzip e cache inteligente configurados no Nginx.
* **Componentes Especializados:**
  1. **Qualidade do Ar (MQ-135):** Barra de gradiente contínua estilo Apple com ponteiro dinâmico e classificação OMS (Excelente, Boa, Moderada, Crítica).
  2. **Precipitação & Chuva (LM393):** Indicador visual de presença de gotas e barra de intensidade de chuva.
  3. **Pressão Barométrica & Altitude (BMP280):** Leitura barométrica em hPa com cálculo de tendência atmosférica e altitude.
  4. **Luminosidade (LDR):** Porcentagem de luz ambiente e categorização de radiação solar.
  5. **Umidade & Ponto de Orvalho (DHT22):** Cálculo automático de Ponto de Orvalho e Sensação Térmica (*Heat Index*).
  6. **Diagnóstico ESP32:** Monitoramento de sinal Wi-Fi (dBm), memória SRAM livre (KB) e Uptime.
  7. **Histórico Analítico (Chart.js):** Curvas suaves com interpolação cúbica e alternância via *Segmented Controls* Apple.
  8. **Geolocalização (Leaflet.js):** Mapa em tema escuro com marcador pulsante e raio de cobertura matemática de 450m (Geometria Analítica).

---

## 2. Estrutura de Arquivos

```
frontend/
├── index.html           # Marcação semântica principal e estrutura dos cards
├── css/
│   └── styles.css       # Design System Apple, variáveis CSS, glassmorphism e responsividade
├── js/
│   ├── app.js           # Orquestrador assíncrono, cálculos meteorológicos e polling
│   ├── charts.js        # Configuração do Chart.js com gradientes e controles segmentados
│   └── map.js           # Inicialização do mapa Leaflet e anéis de cobertura
├── assets/              # Ícones e elementos visuais
└── README.md            # Este documento
```

---

## 3. Como Executar Localmente

### Opção 1: Diretamente no Navegador (com Backend Local Ativo)
1. Certifique-se de que o backend FastAPI esteja em execução (`http://localhost:8000`).
2. Abra o arquivo `frontend/index.html` em qualquer navegador moderno.
3. O script detectará automaticamente a origem e consumirá `http://localhost:8000/api/v1`.

### Opção 2: Integrado com Nginx e Docker Compose (Produção / AWS)
```bash
cd ecopulse/infra/aws
docker compose up -d
```
Acesse `http://localhost` (ou o IP público da sua instância AWS EC2).
