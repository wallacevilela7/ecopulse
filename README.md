# EcoPulse - Estação Meteorológica Inteligente IoT

> **Projeto Integrado Multidisciplinar II (PIM II)**  
> **Curso:** Ciência da Computação — 2º Semestre  
> **Instituição:** Universidade Paulista (UNIP)  
> **Autor:** Wallace Vilela  
> **Status:** Fase 6 — Dual-Pipeline Hot/Cold Path (WMO-No. 8 / INMET), Dashboard v3.0 (Climatempo + Google Weather + Apple Bento) e Deploy AWS EC2 (Docker Compose)

---

## 1. Visão Geral do Projeto

O **EcoPulse** é um ecossistema computacional IoT para monitoramento micrometeorológico e qualidade do ar em tempo real:
1. **Nó de Borda (Edge):** ESP32 com cluster de 5 sensores físicos operando no bloco ADC1 (compatível com rádio Wi-Fi), reconexão automática e envio reativo de baixa latência (`2,5s` ou imediato em oscilações bruscas).
2. **Hot Path (Tempo Real):** Ingestão em memória RAM no FastAPI (com ring-buffer das últimas 24 amostras) e transmissão instantânea via **Server-Sent Events (SSE)** com latência `< 15ms` e zero I/O de disco.
3. **Cold Path (Persistência Inteligente WMO-No. 8 / INMET):** Consolidação estatística a cada **5 minutos** (média, mínima e máxima) e disparo imediato por **Deadband** (início/fim de chuva, variação de luminosidade no LDR $\Delta \ge 15\%$, umidade $\Delta \ge 8\%$, temperatura $\Delta \ge 1,5^\circ\text{C}$, queda barométrica e pico de gases) no **PostgreSQL / SQLite**, reduzindo mais de **95%** do volume de escrita em disco.
4. **Interface Web v3.0 (Climatempo + Google Weather + Apple Weather):** Primeira dobra limpa com card principal e abas de curvas suaves estilo Google Weather (`Temperatura`, `Umidade e Chuva`, `Luz e Ar`, `Pressão`), 6 mini-cards Bento estilo iPhone, lista histórica com barras de amplitude térmica estilo Climatempo e geolocalização híbrida em 3 camadas (GPS HTML5 + IP fallback + geocodificação reversa Nominatim).
5. **Infraestrutura Cloud (AWS EC2):** Topologia unificada Single-Host com Docker Compose (`Nginx Reverse Proxy + FastAPI + PostgreSQL 16` com healthcheck e persistência em volume) pronta para execução imediata.

Consulte o inventário técnico completo em [**TECH_STACK.md**](file:///home/wvs/Documents/pim2/ecopulse/TECH_STACK.md).

---

## 2. Estrutura do Repositório

```
ecopulse/
├── .github/                               # Automação e Integração Contínua
│   └── workflows/
│       └── deploy.yml                     # Pipeline CI/CD (Pytest + Deploy Zero-Downtime AWS EC2)
│
├── docs/                                  # Documentação formal de engenharia (PIM II)
│   ├── arquitetura.md                     # Arquitetura Dual-Pipeline (Hot/Cold Path e PostgreSQL)
│   ├── fluxo-dados.md                     # Topologia em nuvem, ciclo de dados e isolamento do BD
│   ├── referencias_tecnicas_abnt.pdf      # Documento técnico ABNT com fundamentação e normas WMO/INMET
│   ├── gerar_referencias_abnt.py          # Script compilador do documento ABNT
│   ├── diagrama_classes.md                # Diagramas de classes UML estruturais
│   ├── diagrama_sequencia.md              # Sequência temporal Hot Path SSE vs Cold Path BD
│   ├── modelo_dados.md                    # Modelagem relacional (tb_telemetry_aggregated_5m e events)
│   ├── contrato_api.md                    # Especificação OpenAPI/REST e SSE
│   ├── relatorio_tecnico_integracao_telemetria.md # Relatório técnico de bancada e diagnóstico
│   ├── archive/                           # [ARQUIVO] Versões arquiteturais legadas (v0 e v1)
│   └── contratos/                         # Payloads JSON versionados de exemplo
│
├── hardware/                              # Engenharia de hardware, circuito e protoboard
│   ├── README.md                          # Lista detalhada de materiais (BOM)
│   ├── pinout_conexoes.md                 # Tabela e mapeamento completo de pinos do ESP32
│   ├── guia_montagem_circuito.md          # Roteiro passo a passo de montagem em bancada
│   ├── calculo_divisores_tensao.md        # Dimensionamento do divisor resistivo do MQ-135
│   ├── manual_montagem_ecopulse.pdf       # Livreto ilustrado de bancada formatado para impressão
│   ├── generate_booklet.py                # Script de compilação do livreto técnico
│   ├── generate_svg_schematic.py          # Gerador vetorial SVG do esquemático elétrico
│   └── assets/                            # Renderizações e diagramas de protoboard MB102
│
├── firmware/                              # Firmware C++ para ESP32 (Arduino / PlatformIO)
│   ├── README.md                          # Instruções de compilação e upload
│   ├── include/
│   │   └── config.h.example               # Template de credenciais de rede Wi-Fi e API
│   ├── platformio.ini.example             # Configuração de build para PlatformIO
│   └── src/
│       └── main.cpp                       # Código embarcado (sensores, WebServer, Telnet e HTTP reativo)
│
├── backend/                               # API Dual-Pipeline (FastAPI + SQLAlchemy)
│   ├── README.md                          # Documentação e execução local da API
│   ├── app/
│   │   ├── main.py                        # Motor Hot/Cold Path, rotas REST e canal SSE
│   │   ├── schemas.py                     # Modelos de validação estrita Pydantic v2
│   │   ├── models.py                      # Tabelas tb_telemetry_aggregated_5m e tb_telemetry_events
│   │   └── database.py                    # Engine com fallback resiliente PostgreSQL/SQLite
│   ├── tests/
│   │   └── test_telemetry.py              # Testes unitários automatizados do Hot/Cold Path (Pytest)
│   ├── requirements.txt                   # Dependências Python
│   └── .env.example                       # Variáveis de ambiente de referência
│
├── frontend/                              # Interface Web SPA (Design System Apple iOS Weather)
│   ├── README.md                          # Especificação de UX/UI (1ª Dobra + Peek + 2ª Dobra)
│   ├── index.html                         # Marcação semântica responsiva
│   ├── css/
│   │   └── styles.css                     # Estética iOS Weather, barras de amplitude e Bento Grid
│   └── js/
│       ├── app.js                         # Receptor SSE, faixas horárias, alertas e cálculos
│       ├── charts.js                      # Gráficos de séries temporais interativos (Chart.js)
│       └── map.js                         # Geolocalização e raio sensorial (Leaflet.js)
│
├── infra/                                 # Infraestrutura como código e deploy em nuvem
│   └── aws/
│       ├── Dockerfile                     # Imagem Docker otimizada da API FastAPI
│       ├── docker-compose.yml             # Orquestração unificada (Nginx, API e PostgreSQL)
│       ├── nginx.conf                     # Reverse proxy, compressão Gzip e canal SSE
│       ├── setup_ec2.sh                   # Script de provisionamento da instância EC2
│       └── README.md                      # Guia operacional de implantação na nuvem
│
├── TECH_STACK.md                          # Inventário e especificações técnicas de todo o projeto
├── LICENSE                                # Licença de código aberto MIT
├── .gitignore                             # Filtro de segredos e arquivos locais
└── README.md                              # Documento mestre do projeto
```

---

## 3. Resumo da Camada de Hardware (Sensores Validados)

Todos os sensores analógicos operam estritamente no bloco **ADC1** do ESP32 para garantir compatibilidade plena com o rádio Wi-Fi:

| Grandeza | Sensor | Pino no ESP32 | Alimentação | Tratamento de Sinal |
| :--- | :--- | :---: | :---: | :--- |
| **Temperatura e Umidade** | DHT22 (AM2302) | GPIO 4 | 3.3V | Digital One-Wire; rejeição de leituras `NaN`. |
| **Pressão e Altitude** | BMP280 | D21 (SDA) / D22 (SCL) | 3.3V | I2C síncrono (100 kHz, endereço `0x76`); auto-reconexão. |
| **Qualidade do Ar / Gases** | MQ-135 | GPIO 32 (ADC1) | **5.0V** | Divisor 1kΩ / 2kΩ (atenua para máx 3.33V); curva analítica PPM. |
| **Luminosidade Ambiente** | LDR 5mm (LM393) | GPIO 35 (ADC1) | 3.3V | Leitura inversa calibrada (`0%` escuro a `100%` luz intensa) + Deadband (`>= 15%`). |
| **Precipitação / Chuva** | LM393 + Placa MH-RD | GPIO 34 (ADC1) | 3.3V | Limiar calibrado de circuito aberto (`ADC >= 500` = `0%` seco; condução abaixo de `500`). |

---

## 4. Como Executar o Projeto (Local e AWS EC2)

### 4.1. Execução Local (FastAPI servindo Frontend + API + SQLite)
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
* **Dashboard Web completo:** `http://localhost:8000`
* **Documentação Swagger interativa:** `http://localhost:8000/docs`
* **Testes unitários isolados (in-memory SQLite):** `PYTHONPATH=. pytest tests/ -v`

### 4.2. Execução em Produção na AWS EC2 (Docker Compose: Nginx + FastAPI + PostgreSQL 16)
```bash
cd infra/aws
chmod +x setup_ec2.sh && ./setup_ec2.sh
docker compose up -d --build
```
* **Dashboard Web (Nginx porta 80):** `http://<IP_PUBLICO_EC2>`
* **API / Telemetria ESP32:** `http://<IP_PUBLICO_EC2>/api/v1/telemetry`
* Consulte o passo a passo completo de criação da EC2 em [**infra/aws/README.md**](file:///home/wvs/Documents/pim2/ecopulse/infra/aws/README.md).

### 4.3. Firmware (ESP32)
1. Crie seu arquivo `firmware/include/config.h` a partir do `config.h.example`.
2. Configure seu SSID, senha de Wi-Fi e o endereço do servidor (`http://<IP_LOCAL_OU_EC2>:8000/api/v1/telemetry` ou porta `80` na EC2) na constante `API_URL`.
3. Suba o código `firmware/src/main.cpp` para o ESP32 via Arduino IDE ou PlatformIO.
4. O ESP32 transmitirá ao Hot Path a cada 2,5 segundos (ou imediatamente em eventos de oscilação de chuva, gases ou luminosidade).

---

## 5. Diário de Bordo e Roadmap de Evolução

- [x] **Etapa 1 — Especificações Técnicas e Modelagem UML**
- [x] **Etapa 2 — Validação e Integração do Hardware de Bancada (5 Sensores no ADC1/I2C)**
- [x] **Etapa 3 — Firmware Reativo, Reconexão Automática Wi-Fi e Calibração Analógica**
- [x] **Etapa 4 — Arquitetura Dual-Pipeline Hot/Cold Path (WMO-No. 8 / INMET), Deadband LDR/Chuva e Banco Relacional**
- [x] **Etapa 5 — Interface Web v3.0 (Climatempo + Google Weather + Apple Bento) e Geolocalização Híbrida**
- [x] **Etapa 6 — Orquestração Cloud AWS EC2 (Docker Compose: Nginx + FastAPI + PostgreSQL 16)**

---

## 6. Licença

Este projeto é distribuído sob a licença **MIT**. Consulte [LICENSE](file:///home/wvs/Documents/pim2/ecopulse/LICENSE) para mais detalhes.
