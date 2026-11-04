# Fluxo de Dados e Topologia de Nuvem Unificada - EcoPulse

> **Documento de Arquitetura e Engenharia de Infraestrutura**  
> **Projeto Integrado Multidisciplinar II (PIM II) — UNIP**  
> **Topologia:** Host Único EC2 (Free Tier) com Docker Compose, Nginx Reverse Proxy, FastAPI e PostgreSQL Isolado.

---

## 1. Visão Geral da Arquitetura Unificada

Para equilibrar custo computacional zero (compatível com a camada gratuita AWS Free Tier `t2.micro`), alta segurança e facilidade de manutenção sem a complexidade excessiva de gerenciar múltiplos serviços desintegrados (ECS, RDS e S3 separados), o ecossistema **EcoPulse** adota uma arquitetura conteinerizada coesa operando sob orquestração de rede privada.

```
[Mundo Físico / Bancada de Sensores]
┌────────────────────────────────────────────────────────┐
│  Estação EcoPulse (ESP32 NodeMCU)                      │
│  - Cluster ADC1: MQ-135, LDR, Sensor Chuva             │
│  - Digital / I2C: DHT22, BMP280                        │
│  - Firmware C++ não-bloqueante (Loop 10s)              │
└──────────────────────────┬─────────────────────────────┘
                           │
                           │ HTTP/HTTPS POST /api/v1/telemetry
                           │ Payload JSON + Header X-API-Key
                           ▼ (Internet Pública via Wi-Fi)
[Nuvem AWS - Instância EC2 t2.micro]
┌─────────────────────────────────────────────────────────────────────────┐
│ Host Linux (Ubuntu Server LTS)                                          │
│                                                                         │
│  Portas Públicas Expostas no Security Group:                            │
│  - Porta 80 (HTTP) e 443 (HTTPS)                                        │
│  - Porta 22 (SSH restrito para CI/CD e manutenção)                      │
│                                                                         │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │ Container: Nginx (Porteiro / Reverse Proxy & Web Server)          │  │
│  │ Ouve nas portas públicas 80/443                                   │  │
│  └───────────────┬──────────────────────────────────▲────────────────┘  │
│                  │                                  │                   │
│   Roteamento /api/* para o Backend     Entrega estáticos do Frontend    │
│   (proxy_pass http://backend:8000)     (HTML5 / CSS Apple / Vanilla JS) │
│                  │                                  │                   │
│                  ▼                                  │                   │
│  ┌──────────────────────────────────┐   ┌───────────┴────────────────┐  │
│  │ Container: API Backend (FastAPI) │   │ Volume Estático /frontend  │  │
│  │ - Pydantic v2 (Validação estrita)│   │ Interface SPA Estilo iOS   │  │
│  │ - Regras de negócio e telemetria │   │ Cards, Gráficos e Mapas    │  │
│  │ - SQLAlchemy ORM                 │   └────────────────────────────┘  │
│  └───────────────┬──────────────────┘                                   │
│                  │                                                      │
│                  │ Conexão SQL Interna (Rede Docker "ecopulse_net")     │
│                  │ Host: "postgres:5432"                                │
│                  ▼                                                      │
│  ┌──────────────────────────────────┐                                   │
│  │ Container: PostgreSQL 16 Alpine  │                                   │
│  │ - Porta 5432 FECHADA para a web  │                                   │
│  │ - Persistência: volume docker    │                                   │
│  │   "postgres_data" no disco EC2   │                                   │
│  └──────────────────────────────────┘                                   │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Ciclo de Vida da Informação e Comunicação

### 2.1. Ingestão de Dados (ESP32 $\rightarrow$ Nuvem)
1. O microcontrolador ESP32 amostra os 5 sensores em intervalos periódicos (10 segundos).
2. Empacota a leitura em formato JSON estruturado com métricas climáticas e diagnósticos (Wi-Fi RSSI, uptime, heap).
3. Abre conexão TCP com a porta 80/443 da instância AWS EC2 enviando a chave de segurança `X-API-Key`.
4. O **Nginx** recebe a requisição, reconhece o prefixo `/api/` e faz o repasse transparente (*reverse proxy*) para o socket interno do **FastAPI** (`backend:8000`).
5. O FastAPI valida o esquema via Pydantic e grava o registro na tabela `tb_telemetry_records` do **PostgreSQL** por meio de conexão autenticada na rede interna isolada.
6. A resposta `HTTP 201 Created` é retornada ao ESP32, fechando o ciclo em menos de 100ms.

### 2.2. Visualização do Usuário (Navegador $\rightarrow$ Dashboard)
1. O usuário acessa a URL raiz `http://ec2-dominio.com/` pelo navegador de seu smartphone ou desktop.
2. O **Nginx** serve instantaneamente os arquivos estáticos pré-renderizados (`index.html`, `styles.css`, `app.js`).
3. O script cliente assíncrono executa uma chamada `GET /api/v1/telemetry/latest` e `GET /api/v1/telemetry/history`.
4. Como a requisição é feita para a mesma origem (`/api/...`), **não há bloqueios de CORS** nem necessidade de configurar IPs distintos.
5. Os dados alimentam os medidores, os gráficos temporais e a localização no mapa com design responsivo no padrão Apple/iOS.

---

## 3. Segurança e Isolamento do Banco de Dados

* **Nenhuma Exposição Pública:** A porta `5432` do PostgreSQL não possui mapeamento no host da EC2 (`ports:` não exposto para a máquina hospedeira), tornando matematicamente impossível qualquer ataque externo de força bruta ou varredura de portas contra o banco de dados.
* **Rede Interna Bridge do Docker:** Apenas os containers pertencentes à rede `ecopulse_net` conseguem resolver o hostname `postgres` e estabelecer comunicação TCP.
* **Persistência de Dados (Data Durability):** Todos os dados relacionais são persistidos no volume nomeado `postgres_data`, localizado no sistema de arquivos permanente da EC2 (`/var/lib/docker/volumes/...`). Mesmo que containers sofram reinicialização ou atualização de imagem, as séries temporais permanecem intactas.

---

## 4. Estratégia de Deploy e CI/CD Zero-Downtime

O fluxo de atualização contínua é gerenciado pelo **GitHub Actions**:
1. **Etapa de Integração Contínua (CI):**
   * Linter estático e testes unitários automatizados com `pytest` cobrindo o backend.
2. **Etapa de Entrega Contínua (CD):**
   * Disparada apenas em commits na branch `main`.
   * Conexão segura via SSH com a instância EC2.
   * Execução de *rolling update* do Docker Compose:
     ```bash
     docker compose pull
     docker compose up -d --no-deps --build backend
     ```
   * O container anterior do FastAPI só é substituído quando o novo container passa no healthcheck interno, garantindo que o ESP32 e os usuários nunca recebam erro 502/503.
