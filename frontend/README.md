# Frontend Dashboard - Planejamento e Especificação

Este diretório conterá o dashboard web da estação **EcoPulse**, uma interface rica, moderna e responsiva voltada para a visualização das métricas climáticas e emissão de alertas em tempo real.

---

## 1. Diretrizes de Interface e Experiência do Usuário (UX/UI)

* **Tema e Identidade Visual:** Interface moderna em Dark Mode com acentos em tons esmeralda/ciano, gradientes suaves e elementos em *glassmorphism*.
* **Sem Frameworks Pesados:** Construção limpa utilizando HTML5 semântico, Vanilla CSS modular e JavaScript moderno (ES6+), mantendo o bundle ultraleve e de carregamento instantâneo.
* **Componentes Principais Planejados:**
  1. **Hero de Métricas em Tempo Real:** Cards interativos para Temperatura, Umidade, Pressão, Luminosidade, Qualidade do Ar e Detecção de Chuva.
  2. **Medidores de Nível (Gauges / Badges):** Indicador visual de qualidade do ar (AQI) com codificação semafórica (Verde = Boa, Amarelo = Moderada, Vermelho = Crítica).
  3. **Gráficos Analíticos de Série Temporal:** Gráficos interativos (via Chart.js ou Canvas nativo) com alternância de períodos (últimas 6h, 12h, 24h).
  4. **Painel de Geolocalização:** Mapa interativo (via Leaflet.js / OpenStreetMap) com as coordenadas geográficas da estação.
  5. **Central de Alertas:** Notificações flutuantes e banner dinâmico disparados quando condições climáticas extremas são detectadas pela API.

---

## 2. Estrutura de Diretórios Planejada

```
frontend/
├── css/
│   └── styles.css       # Design system, tokens de cor, variáveis e tipografia
├── js/
│   ├── app.js           # Orquestrador da aplicação, consumo da API e polling
│   ├── charts.js        # Configuração e renderização dos gráficos temporais
│   └── map.js           # Inicialização e marcação do mapa geográfico
├── assets/              # Ícones SVG, logotipos e favicons
├── index.html           # Página principal da aplicação
└── README.md            # Documentação técnica do frontend
```

---

## 3. Próximos Passos (Construção Conjunta Passo a Passo)

1. [ ] Criação do protótipo e grid responsivo no `index.html`.
2. [ ] Definição do sistema de design e variáveis CSS em `css/styles.css`.
3. [ ] Implementação do serviço de integração com a API Backend (`js/app.js`).
4. [ ] Renderização dos gráficos dinâmicos e mapa de cobertura.
