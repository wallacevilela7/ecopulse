# EcoPulse - Estação Meteorológica Inteligente IoT

> **Projeto Integrado Multidisciplinar II (PIM II)**  
> **Curso:** Ciência da Computação — 2º Semestre  
> **Instituição:** Universidade Paulista (UNIP)  
> **Autor:** Wallace Vilela  
> **Status:** Fase 1 — Especificação Arquitetural, Hardware e Modelagem UML

---

## 1. Visão Geral do Projeto

O **EcoPulse** é um sistema completo de monitoramento meteorológico e qualidade ambiental baseado em Internet das Coisas (IoT). O projeto integra um nó sensor físico de baixo custo baseado no microcontrolador **ESP32**, uma **API RESTful assíncrona em Python (FastAPI)** para recepção e processamento analítico dos dados, um banco de dados de séries temporais e um **Dashboard Web interativo** para visualização pública e emissão de alertas em tempo real.

O objetivo do projeto é demonstrar a aplicação prática e integrada das disciplinas do 2º semestre do curso de Ciência da Computação:
* **Engenharia de Software & POO:** Modelagem arquitetural em camadas, diagramas de classe UML e padrões de projeto (*Repository Pattern*, *HAL*).
* **Sistemas Embarcados & Eletrônica:** Aquisição de sinais analógicos e digitais, comunicação via barramentos I2C e One-Wire, e dimensionamento de divisores de tensão para proteção de hardware.
* **Redes de Computadores:** Protocolos TCP/IP, Wi-Fi 802.11 b/g/n, sincronização de tempo via NTP e transporte HTTP/1.1 com serialização JSON.
* **Bancos de Dados:** Modelagem relacional e estruturação de séries temporais com estratégias de indexação por dispositivo e tempo.

---

## 2. Estrutura do Repositório

O repositório foi organizado de forma modular, segregando responsabilidades desde o início do desenvolvimento:

```
ecopulse/
├── docs/                      # Documentação de engenharia e modelagem de software
│   ├── arquitetura.md         # Diagrama de rede e visão sistêmica em camadas
│   ├── diagrama_classes.md    # Diagrama de classes UML (Firmware HAL e Backend API)
│   ├── diagrama_sequencia.md  # Diagramas de sequência dos fluxos de telemetria e falhas
│   ├── modelo_dados.md        # Diagrama ER e modelagem do banco de dados relacional
│   ├── contrato_api.md        # Especificação OpenAPI/REST com rotas, headers e códigos HTTP
│   └── contratos/             # Payloads JSON reais e versionados (v1.0)
│
├── hardware/                  # Engenharia eletrônica, IoT e esquemáticos elétricos
│   ├── README.md              # Lista de materiais (BOM) e visão geral dos componentes
│   ├── manual_montagem_ecopulse.pdf # Livreto diagramado ilustrado para bancada/laboratório
│   ├── guia_montagem_circuito.md # Roteiro passo a passo minucioso para montagem na protoboard
│   ├── pinout_conexoes.md     # Mapeamento pino a pino ESP32 x Sensores com tensões
│   ├── calculo_divisores_tensao.md # Fórmulas matemáticas e dimensionamento dos resistores
│   └── assets/                # Diagramas visuais da bancada e fotos do esquemático
│
├── backend/                   # API RESTful em Python / FastAPI (Estrutura e requisitos)
│   ├── app/                   # Código-fonte da aplicação (construção progressiva)
│   ├── infra/                 # Infraestrutura de deploy (Docker Compose e banco)
│   ├── tests/                 # Testes unitários com Pytest
│   ├── requirements.txt       # Dependências planejadas
│   └── .env.example           # Variáveis de ambiente de referência
│
├── frontend/                  # Dashboard Web para visualização das métricas
│   ├── css/                   # Estilos visuais e tokens de design system
│   ├── js/                    # Módulos JavaScript (gráficos, mapas e telemetria)
│   └── README.md              # Especificação de UX/UI
│
├── firmware/                  # Código-fonte C++ para ESP32 (PlatformIO)
│   ├── include/               # Cabeçalhos e configurações de rede
│   ├── src/                   # Lógica modular (HAL, cliente HTTP e ciclo de amostragem)
│   └── platformio.ini.example # Configuração de compilação e dependências
│
├── .gitignore                 # Filtro completo para Python, C++, Node e segredos
├── LICENSE                    # Licença MIT
└── README.md                  # Este documento
```

---

## 3. Resumo da Camada de Hardware (Sensores)

| Grandeza | Sensor | Interface no ESP32 | Tensão de Alimentação | Proteção / Circuito Passivo |
| :--- | :--- | :--- | :---: | :--- |
| **Temperatura e Umidade** | DHT22 (AM2302) | GPIO 4 (Digital One-Wire) | 3.3V | Resistor pull-up de 10 kΩ |
| **Pressão Barométrica** | BMP280 | GPIO 21 (SDA) / 22 (SCL) | 3.3V | Barramento digital I2C (0x76) |
| **Luminosidade Ambiente** | LDR 5mm | GPIO 34 (Analógico ADC1) | 3.3V | Divisor resistivo com 10 kΩ |
| **Qualidade do Ar / Gases** | MQ-135 | GPIO 32 (Analógico ADC1) | **5.0V** | Divisor 1kΩ / 2kΩ (atenua 5V para 3.3V) |
| **Detecção de Chuva** | Montimport | GPIO 35 (Analógico ADC1) | 3.3V | Placa comparadora LM393 |

---

## 4. Documentação Técnica Completa

Para aprofundar em cada pilar da engenharia do projeto, consulte a documentação detalhada:

* 📐 [**Arquitetura do Sistema e Diagrama de Rede**](file:///home/wvs/Documents/ccomp-unip/2sem/pim2/ecopulse/docs/arquitetura.md)
* 🧩 [**Diagrama de Classes UML (Firmware & Backend)**](file:///home/wvs/Documents/ccomp-unip/2sem/pim2/ecopulse/docs/diagrama_classes.md)
* ⏱️ [**Diagramas de Sequência (Fluxos e Tolerância a Falhas)**](file:///home/wvs/Documents/ccomp-unip/2sem/pim2/ecopulse/docs/diagrama_sequencia.md)
* 🗄️ [**Modelo de Dados e Diagrama Entidade-Relacionamento**](file:///home/wvs/Documents/ccomp-unip/2sem/pim2/ecopulse/docs/modelo_dados.md)
* 🔌 [**Contrato REST da API e Dicionário do Payload**](file:///home/wvs/Documents/ccomp-unip/2sem/pim2/ecopulse/docs/contrato_api.md)
* ⚡ [**Guia de Montagem e Pinout de Hardware**](file:///home/wvs/Documents/ccomp-unip/2sem/pim2/ecopulse/hardware/README.md)
* 🧮 [**Cálculo e Engenharia dos Divisores de Tensão**](file:///home/wvs/Documents/ccomp-unip/2sem/pim2/ecopulse/hardware/calculo_divisores_tensao.md)

---

## 5. Diário de Bordo e Roadmap de Evolução (Commit por Dia)

Este projeto segue a premissa de **construção passo a passo orientada à aprendizagem contínua**, registrando cada marco em commits claros no GitHub:

- [x] **Dia 1 — Concepção, Especificações Técnicas e Diagramas UML:**
  - Levantamento dos requisitos e plano de ensino do PIM II (UNIP).
  - Definição da arquitetura distribuída (ESP32 + FastAPI + PostgreSQL + Dashboard Web).
  - Dimensionamento dos divisores de tensão e esquemático da protoboard com fonte MB102.
  - Elaboração dos diagramas de arquitetura, classes, sequência e entidade-relacionamento.
  - Estruturação inicial do repositório e diretórios sem código antecipado.
- [ ] **Dia 2 — Testes Unitários de Bancada do Hardware (Firmware Inicial):**
  - Configuração do projeto PlatformIO.
  - Validação individual das leituras no Monitor Serial (DHT22, BMP280, LDR, Chuva e MQ-135).
- [ ] **Dia 3 — Fundação do Backend (Schemas e Cálculos Meteorológicos):**
  - Implementação dos modelos Pydantic com base no payload JSON versionado.
  - Implementação das funções puras de sensação térmica (*Heat Index*), ponto de orvalho e índice AQI com testes Pytest.
- [ ] **Dia 4 — Ingestão de Telemetria e Banco de Dados:**
  - Configuração do banco de dados relacional e migrações.
  - Implementação do endpoint `POST /api/v1/telemetry` com autenticação via `X-API-Key`.
- [ ] **Dia 5 — Conectividade Wi-Fi e Integração Ponta a Ponta:**
  - Implementação da classe `TelemetryHttpClient` no ESP32.
  - Transmissão real dos dados do microcontrolador para a API na nuvem/rede local.
- [ ] **Dia 6 — Interface Web (Dashboard Interativo):**
  - Construção do layout responsivo com visualização de métricas em tempo real e gráficos temporais.
- [ ] **Dia 7 — Validação Final e Documentação Acadêmica:**
  - Consolidação dos resultados, geração de relatórios e preparação do artigo/banner do PIM II.

---

## 6. Licença

Este projeto é distribuído sob a licença **MIT**. Consulte o arquivo [LICENSE](file:///home/wvs/Documents/ccomp-unip/2sem/pim2/ecopulse/LICENSE) para maiores detalhes.
