# Especificação e Plano de Implementação: Infraestrutura em Nuvem AWS para o EcoPulse

**Projeto Integrado Multidisciplinar II (PIM II)**  
**Curso:** Ciência da Computação — Universidade Paulista (UNIP)  
**Projeto:** EcoPulse — Estação Meteorológica e Monitoramento Ambiental Inteligente  
**Módulo:** Infraestrutura em Nuvem (Cloud Architecture - AWS), Persistência Gerenciada e Disponibilização Pública  
**Data:** Outubro de 2026  

---

## 1. Sumário Executivo e Visão Geral

O objetivo desta fase é transformar o protótipo físico de bancada em um **produto IoT de escala real**, acessível publicamente via web através de uma URL pública (ex.: `https://ecopulse-projeto.com` ou subdomínio AWS CloudFront).

### 🎯 Proposta de Valor para a Apresentação do PIM II:
1. **Acesso Público Global:** Qualquer pessoa ou avaliador da banca poderá acessar a URL pelo navegador do celular ou computador e visualizar as leituras meteorológicas em tempo real.
2. **Utilização Prática de Computação em Nuvem (AWS):** Demonstra maturidade acadêmica em arquitetura de microsserviços, banco de dados gerenciado em nuvem e distribuição de conteúdo CDN com SSL/TLS.
3. **Custo Zero (100% elegível ao AWS Free Tier / Créditos):** A infraestrutura é inteiramente dimensionada para operar sem custos operacionais adicionais.

---

## 2. Topologia da Arquitetura em Nuvem (AWS Cloud Architecture)

A infraestrutura foi desenhada para suportar duas modalidades operacionais de alto valor para o projeto:

```mermaid
flowchart TD
    subgraph EDGE["Camada Física / Bancada (Borda IoT)"]
        Sensors["Cluster 5 Sensores<br/>(DHT22, BMP280, MQ-135, LDR, Chuva)"]
        ESP["ESP32 Microcontroller<br/>(Wi-Fi 802.11 b/g/n)"]
        Sensors -->|Sinais Elétricos / I2C| ESP
    end

    subgraph AWS["Nuvem Amazon Web Services (AWS - Região us-east-1)"]
        subgraph INGESTION["Camada de Ingestão e Processamento"]
            API["FastAPI Backend Container<br/>(AWS App Runner / EC2 t4g.small)<br/>POST /api/v1/telemetry"]
        end

        subgraph DATABASE["Camada de Persistência Gerenciada"]
            RDS[("AWS RDS PostgreSQL<br/>(Engine 16 - db.t4g.micro)<br/>Multi-AZ / Automated Backups")]
        end

        subgraph FRONTEND_HOST["Camada de Apresentação e CDN"]
            S3["AWS S3 Bucket<br/>(Static Website Hosting)"]
            CF["AWS CloudFront (CDN Global)<br/>Certificado HTTPS (ACM)<br/>ecopulse-projeto.com"]
            S3 --> CF
        end
    end

    subgraph CLIENTS["Usuários e Avaliadores (Internet)"]
        Browser["Navegador Web / Mobile<br/>(Professores / Avaliadores UNIP)"]
    end

    %% Fluxos de Dados
    ESP -->|HTTPS POST + X-API-Key| API
    API -->|SQLAlchemy ORM (TCP 5432)| RDS
    Browser -->|HTTPS GET :443| CF
    Browser -.->|Consome API :443| API
    API -.->|Query Histórico & Latest| RDS
```

---

## 3. As Duas Abordagens Possíveis de Implantação

### 🏆 Abordagem A: 100% Autônoma em Nuvem (Padrão Ouro de Engenharia IoT)
* **Como funciona:** O ESP32 envia as leituras diretamente via Wi-Fi para o endpoint público da API na AWS (`https://api.ecopulse.../api/v1/telemetry`).
* **Vantagem Espetacular para o PIM:** **Independência total de computadores locais!** Você pode levar a protoboard do EcoPulse para a sala de apresentação da UNIP, plugar na tomada ou num powerbank, conectar no 4G do celular e a estação transmitirá direto para a nuvem. O site atualizará sozinho durante a apresentação diante dos professores.

### 🔄 Abordagem B: Gateway Híbrido de Bancada
* **Como funciona:** O ESP32 envia para o backend rodando no seu computador local (ex.: na mesma rede Wi-Fi). Esse backend local processa os dados e conecta-se via internet ao **banco de dados em nuvem (AWS RDS PostgreSQL)**. O Frontend online (na AWS) consulta o banco em nuvem e exibe os dados para o público.
* **Vantagem:** Permite manter depuração serial USB em tempo real na bancada enquanto alimenta o banco online.

> **Nota de Projeto:** O código que desenvolvemos com **SQLAlchemy** é agnóstico. Ele suporta tanto a Abordagem A quanto a Abordagem B apenas alterando a variável `DATABASE_URL` no `.env`.

---

## 4. Dimensionamento e Custo na AWS (Free Tier / Créditos)

A arquitetura foi minuciosamente planejada para caber no pacote **AWS Free Tier (Nível Gratuito)**:

| Serviço AWS | Componente do EcoPulse | Tipo de Instância / Capacidade | Limite Gratuito Mensal | Custo Real |
| :--- | :--- | :---: | :---: | :---: |
| **Amazon RDS** | Banco de Dados Relacional das Leituras | PostgreSQL 16 (`db.t4g.micro` ou `db.t3.micro`) | 750 horas/mês + 20 GB de SSD gp2/gp3 | **$ 0.00** |
| **AWS App Runner** ou **EC2** | Servidor da API FastAPI e Ingestão | Container gerenciado ou VM Linux `t4g.small` | 750 horas/mês (EC2) / Créditos AWS | **$ 0.00** |
| **Amazon S3** | Armazenamento dos Arquivos do Dashboard | Bucket estático (`index.html`, CSS, JS) | 5 GB de armazenamento + 20.000 requisições GET | **$ 0.00** |
| **Amazon CloudFront** | Distribuição Global e SSL/HTTPS | CDN mundial com terminação TLS | 1 TB de transferência de dados/mês | **$ 0.00** |
| **AWS Certificate Manager (ACM)** | Certificado de Segurança SSL (`https://`) | Certificado público auto-renovável | Gratuito e ilimitado para CloudFront/ALB | **$ 0.00** |

---

## 5. Estratégia de Persistência com SQLAlchemy no PostgreSQL Gerenciado

O banco de dados relacional armazenará as séries temporais em tabela otimizada com índices para retorno instantâneo:

```sql
-- DDL Principal de Telemetria no PostgreSQL
CREATE TABLE tb_telemetry_records (
    id SERIAL PRIMARY KEY,
    device_id VARCHAR(50) NOT NULL,
    recorded_at TIMESTAMP WITH TIME ZONE NOT NULL,
    received_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Sensores Ambientais
    temperature_c NUMERIC(5,2),
    humidity_pct NUMERIC(5,2),
    pressure_hpa NUMERIC(6,2),
    altitude_m NUMERIC(6,2),
    air_quality_ppm NUMERIC(7,2),
    luminosity_pct NUMERIC(5,2),
    rain_intensity_pct NUMERIC(5,2),
    is_raining BOOLEAN DEFAULT FALSE,
    
    -- Diagnósticos Operacionais
    uptime_seconds INTEGER,
    wifi_rssi_dbm SMALLINT,
    free_heap_bytes INTEGER
);

-- Índices Estratégicos para Alta Performance
CREATE INDEX idx_telemetry_device_time 
ON tb_telemetry_records (device_id, recorded_at DESC);
```

### Conexão via Variável de Ambiente (`.env`):
No código da API, a conexão com o RDS em nuvem é expressa simplesmente por:
```env
DATABASE_URL=postgresql://ecopulse_admin:SUA_SENHA_FORTE@ecopulse-db.cxxxxxx.us-east-1.rds.amazonaws.com:5432/ecopulse_db
```

---

## 6. Roteiro de Execução Passo a Passo (Roadmap Prático)

Para mantermos o método de desenvolvimento controlado (**Planejar $\rightarrow$ Documentar $\rightarrow$ Executar $\rightarrow$ Validar $\rightarrow$ Commitar**), este projeto em nuvem será executado nos seguintes passos:

### 📍 Passo 1: Modelagem e Conector de Banco (Backend)
* Criar a camada ORM (`database.py` e `models.py`) em SQLAlchemy capaz de chavear transparentemente entre SQLite (para testes locais rápidos) e PostgreSQL (para a nuvem AWS).
* Implementar os métodos de inserção e busca (`/latest` e `/history`).

### 📍 Passo 2: Provisionamento do AWS RDS PostgreSQL
* Criar a instância de banco de dados gerenciado no console da AWS dentro do Free Tier (`db.t4g.micro` em `us-east-1`).
* Configurar o *Security Group* para liberar o tráfego da porta 5432 com segurança.

### 📍 Passo 3: Containerização e Deploy do Backend na AWS
* Criar o `Dockerfile` otimizado para o FastAPI com Uvicorn.
* Realizar o deploy do container (via AWS App Runner ou EC2) para gerar a URL pública HTTPS (ex.: `https://api.ecopulse...`).

### 📍 Passo 4: Atualização de Rota no Firmware do ESP32
* No arquivo `config.h`, atualizar `API_URL` para o endereço público HTTPS gerado na AWS.
* Testar a transmissão direta do ESP32 para a nuvem.

### 📍 Passo 5: Frontend e Domínio Público
* Construir a interface web responsiva (cards meteorológicos em tempo real, gráficos de evolução temporal e indicadores de status dos sensores).
* Publicar no Amazon S3 + CloudFront para disponibilização pública com domínio customizado e HTTPS.

---

## 7. Segurança da Informação e Melhores Práticas (DevSecOps)

1. **Proteção contra Acessos Não Autorizados:**
   * O endpoint `POST /api/v1/telemetry` exige o cabeçalho `X-API-Key`. Somente requisições com a chave correta conseguem inserir medições no banco de dados.
2. **Isolamento de Credenciais:**
   * Nenhuma credencial de banco ou senha de API é versionada no Git (todas gerenciadas via `.env` e `config.h`, ambos protegidos pelo `.gitignore`).
3. **Comunicação Criptografada de Ponta a Ponta:**
   * Tráfego Web e de telemetria operam estritamente sob TLS 1.3 / HTTPS.

---
*Documento de especificação de arquitetura Cloud AWS para o PIM II — UNIP Ciência da Computação.*
