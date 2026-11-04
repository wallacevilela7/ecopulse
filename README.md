# EcoPulse - Estação Meteorológica Inteligente IoT

> **Projeto Integrado Multidisciplinar II (PIM II)**  
> **Curso:** Ciência da Computação — 2º Semestre  
> **Instituição:** Universidade Paulista (UNIP)  
> **Autor:** Wallace Vilela  
> **Status:** Fase 5 Concluída — Firmware Reativo, Ingestão HTTP, Persistência SQL, Streaming SSE e Dashboard Apple iOS

---

## 1. Visão Geral do Projeto

O **EcoPulse** é um sistema computacional IoT para monitoramento micrometeorológico e qualidade do ar em tempo real. O ecossistema abrange:
1. **Nó de Borda (Edge):** ESP32 com cluster de 5 sensores físicos operando no bloco ADC1.
2. **Ingestão & Backend:** API RESTful em Python (FastAPI) com validação estrita (Pydantic) e autenticação `X-API-Key`.
3. **Persistência:** Camada ORM com SQLAlchemy para séries temporais (compatibilidade dual: SQLite local e AWS RDS PostgreSQL).
4. **Infraestrutura em Nuvem (AWS):** Arquitetura conteinerizada (Docker Compose / EC2 `t2.micro`), banco RDS gerenciado e distribuição global do dashboard via S3 + CloudFront (HTTPS).

Consulte o inventário técnico completo em [**TECH_STACK.md**](file:///home/wvs/Documents/ccomp-unip/2sem/pim2/ecopulse/TECH_STACK.md).

---

## 2. Estrutura do Repositório

```
ecopulse/
├── .github/                               # Automação e Integração Contínua
│   └── workflows/
│       └── deploy.yml                     # Pipeline CI/CD (Pytest + Deploy Zero-Downtime AWS EC2)
│
├── docs/                                  # Documentação formal de engenharia (PIM II)
│   ├── arquitetura.md                     # Visão sistêmica e camadas arquiteturais
│   ├── fluxo-dados.md                     # Topologia em nuvem, ciclo de dados e isolamento do BD
│   ├── diagrama_classes.md                # Diagramas de classes UML estruturais
│   ├── diagrama_sequencia.md              # Sequência temporal e fluxos de telemetria
│   ├── modelo_dados.md                    # Modelagem relacional e índices do PostgreSQL/SQLite
│   ├── contrato_api.md                    # Especificação OpenAPI/REST e schemas
│   ├── relatorio_tecnico_integracao_telemetria.md # Relatório técnico de bancada e diagnóstico
│   ├── implementacao_infraestrutura_cloud_aws.md  # Arquitetura e dimensionamento AWS
│   ├── assets/                            # Imagens e esquemáticos da documentação
│   └── contratos/                         # Payloads JSON versionados de exemplo
│
├── hardware/                              # Engenharia de hardware, circuito e protoboard
│   ├── README.md                          # Lista detalhada de materiais (BOM)
│   ├── pinout_conexoes.md                 # Tabela e mapeamento completo de pinos do ESP32
│   ├── guia_montagem_circuito.md          # Roteiro passo a passo de montagem em bancada
│   ├── calculo_divisores_tensao.md        # Dimensionamento do divisor resistivo do MQ-135
│   ├── manual_montagem_ecopulse.pdf       # Livreto ilustrado de bancada formatado para impressão
│   ├── manual_montagem_ecopulse.html      # Fonte HTML do livreto com diagramas visuais
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
├── backend/                               # API RESTful e Streaming (FastAPI + SQLAlchemy)
│   ├── README.md                          # Documentação e execução local da API
│   ├── app/
│   │   ├── main.py                        # Endpoints REST e canal de Streaming SSE em tempo real
│   │   ├── schemas.py                     # Modelos de validação estrita Pydantic v2
│   │   ├── models.py                      # Entidades relacionais SQLAlchemy
│   │   └── database.py                    # Engine com fallback resiliente SQLite/Postgres
│   ├── tests/
│   │   └── test_telemetry.py              # Testes unitários automatizados (Pytest)
│   ├── requirements.txt                   # Dependências Python (FastAPI, SQLAlchemy, Uvicorn, etc.)
│   └── .env.example                       # Variáveis de ambiente de referência
│
├── frontend/                              # Dashboard Web SPA (Design System Apple iOS)
│   ├── README.md                          # Especificação de UX/UI e componentes visuais
│   ├── index.html                         # Interface SPA semântica com Bento Grid
│   ├── css/
│   │   └── styles.css                     # Glassmorphism, design tokens Apple e micro-animações
│   └── js/
│       ├── app.js                         # Orquestrador assíncrono, receptor SSE e cálculos
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
| **Luminosidade Ambiente** | LDR 5mm | GPIO 35 (ADC1) | 3.3V | Mapeamento percentual calibrado (penumbra/luz alta). |
| **Precipitação / Chuva** | LM393 + Placa MH-RD | GPIO 34 (ADC1) | 3.3V | Leitura analógica inversa (ADC 4095 = seco; ADC decrescente com água). |

---

## 4. Como Executar o Projeto Localmente

### 4.1. Backend (FastAPI + Banco de Dados)
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
* **Documentação Swagger interativa:** `http://localhost:8000/docs`
* **Testes unitários:** `PYTHONPATH=. pytest tests/`

### 4.2. Firmware (ESP32)
1. Crie seu arquivo `firmware/include/config.h` a partir do `config.h.example`.
2. Configure seu SSID, senha de Wi-Fi e o IP do computador na variável `API_URL`.
3. Suba o código `firmware/src/main.cpp` para o ESP32 via Arduino IDE ou PlatformIO.
4. O ESP32 iniciará a transmissão periódica para o Backend a cada 10 segundos.

---

## 5. Diário de Bordo e Roadmap de Evolução

- [x] **Etapa 1 — Especificações Técnicas e Modelagem UML:**
  - Definição da arquitetura e cálculos dos divisores de tensão.
  - Elaboração de diagramas UML (Classes, Sequência e ERD) e contratos de API.
- [x] **Etapa 2 — Validação e Integração do Hardware de Bancada:**
  - Montagem do cluster de 5 sensores na protoboard com fonte MB102.
  - Implementação de multisampling no ADC1 e isolamento de falha mecânica de bancada documentado cientificamente.
- [x] **Etapa 3 — Firmware e Pipeline de Telemetria:**
  - Implementação de transmissão HTTP POST com JSON padronizado e token `X-API-Key`.
  - Suporte a monitoramento simultâneo via USB Serial, Telnet e WebServer embutido.
- [x] **Etapa 4 — Camada de Ingestão, Persistência e Nuvem:**
  - Criação do receptor FastAPI com validação estrita Pydantic v2.
  - Implementação do banco relacional com SQLAlchemy (SQLite local / PostgreSQL RDS).
  - Estruturação dos scripts e arquitetura para deploy na AWS (`infra/aws/`).
- [x] **Etapa 5 — Dashboard Frontend e Streaming em Tempo Real:**
  - Interface SPA no design system Apple (iOS Weather / Bento Grid) com Glassmorphism.
  - Streaming Server-Sent Events (SSE) com latência inferior a 15ms e animações de oscilação.
  - Séries temporais interativas (Chart.js) e geolocalização sensorial (Leaflet.js).
- [ ] **Etapa 6 — Deploy e Publicação em Nuvem (AWS EC2 / Nginx):**
  - Publicação da infraestrutura unificada na nuvem AWS via esteira CI/CD (GitHub Actions).
  - Redação da monografia acadêmica do PIM II conforme normas ABNT da UNIP.

---

## 6. Licença

Este projeto é distribuído sob a licença **MIT**. Consulte [LICENSE](file:///home/wvs/Documents/ccomp-unip/2sem/pim2/ecopulse/LICENSE) para mais detalhes.
