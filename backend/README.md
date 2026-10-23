# Backend API - Planejamento e Especificação

Este diretório hospedará a API RESTful da estação **EcoPulse**, responsável por receber a telemetria do ESP32, persistir os registros em banco de dados e fornecer dados agregados para o frontend.

---

## 1. Stack Tecnológica Planejada

* **Linguagem:** Python 3.10+
* **Framework Web:** FastAPI (alta performance, tipagem estática e OpenAPI/Swagger nativo)
* **Servidor ASGI:** Uvicorn
* **Validação e Tipagem:** Pydantic v2
* **Persistência / ORM:** SQLAlchemy / asyncpg ou Psycopg2
* **Banco de Dados:** PostgreSQL (séries temporais)
* **Testes:** Pytest

---

## 2. Estrutura de Diretórios Planejada

```
backend/
├── app/
│   ├── main.py              # Ponto de entrada e configuração do FastAPI
│   ├── config.py            # Carregamento de variáveis de ambiente (.env)
│   ├── database.py          # Gerenciamento de conexões e sessões do banco
│   ├── models.py            # Modelos ORM (tabelas do banco de dados)
│   ├── schemas.py           # DTOs de validação de entrada/saída (Pydantic)
│   ├── services/            # Camada de regras de negócio (cálculos e alertas)
│   │   ├── weather_math.py  # Fórmulas meteorológicas (Sensação térmica, orvalho)
│   │   ├── alert_engine.py  # Regras de detecção de eventos meteorológicos críticos
│   │   └── geometry.py      # Cálculos de raio e distância geográfica
│   └── routers/             # Endpoints REST segregados por domínio
│       ├── telemetry.py     # Rotas de ingestão e histórico de sensores
│       └── alerts.py        # Rotas de gerenciamento de alertas
├── infra/                   # Scripts de Docker, Nginx e deploy
├── tests/                   # Testes unitários e de integração
├── requirements.txt         # Dependências do projeto
└── .env.example             # Variáveis de ambiente modelo
```

---

## 3. Próximos Passos (Construção Conjunta Passo a Passo)

1. [ ] Configuração do ambiente virtual Python (`.venv`) e instalação de dependências mínimas.
2. [ ] Criação dos schemas Pydantic baseados no contrato [`docs/contratos/payload_exemplo.json`](file:///home/wvs/Documents/ccomp-unip/2sem/pim2/ecopulse/docs/contratos/payload_exemplo.json).
3. [ ] Implementação das funções matemáticas puras de meteorologia e testes com Pytest.
4. [ ] Implementação dos endpoints e conexão com o banco de dados.
