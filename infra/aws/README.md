# Infraestrutura em Nuvem (AWS EC2) - EcoPulse

Este diretório contém toda a orquestração Docker Compose para rodar o **EcoPulse** na AWS EC2 com um único comando:
1. **`webserver` (Nginx Alpine):** Serve o Frontend v3.0 na porta `80` e faz proxy reverso para a API com suporte a streaming SSE em tempo real (`proxy_buffering off`).
2. **`api` (FastAPI Dual-Pipeline):** Motor Hot Path (RAM + SSE) e Cold Path (Janelas de 5 min + Deadband).
3. **`db` (PostgreSQL 16 Alpine):** Banco relacional com volume persistente (`postgres_data`) e healthcheck automático.

---

## 📁 Estrutura do Diretório

```
infra/aws/
├── Dockerfile              # Containerização do Backend FastAPI (Python 3.11)
├── docker-compose.yml      # Orquestração completa (Nginx + FastAPI + PostgreSQL 16)
├── nginx.conf              # Reverse proxy na porta 80 + suporte a SSE em tempo real
├── setup_ec2.sh            # Script que instala Docker e Docker Compose no Ubuntu 24.04
├── private/                # [IGNORADO PELO GIT] Chaves .pem e variáveis privadas
└── README.md               # Guia passo a passo de implantação na AWS EC2
```

---

## 🚀 Passo a Passo Completo na AWS EC2

### 1. Criar a Instância no Console da AWS
1. Acesse **EC2 -> Launch Instance (Executar instância)**.
2. **Name:** `ecopulse-server`
3. **AMI (Sistema Operacional):** **Ubuntu Server 24.04 LTS (HVM), SSD Volume Type** (64-bit x86).
4. **Instance Type:** `t2.micro` ou `t3.micro` (Free Tier eligible).
5. **Key pair (login):** Crie ou selecione um par de chaves RSA `.pem` (ex: `ecopulse-key.pem`) e salve em `infra/aws/private/`.
6. **Network Settings (Security Group / Firewall):**
   Marque **Allow SSH traffic** e **Allow HTTP traffic from the internet**, ou configure as seguintes **Inbound Rules (Regras de Entrada)**:
   - **SSH (`22` TCP):** `0.0.0.0/0` (ou Meu IP)
   - **HTTP (`80` TCP):** `0.0.0.0/0` *(Frontend + API via Nginx + Envio da ESP32)*
   - **Custom TCP (`8000` TCP):** `0.0.0.0/0` *(Opcional: acesso direto ao FastAPI/Swagger)*
7. **Configure Storage:** `8 GiB` a `20 GiB` `gp3` (incluso no Free Tier até 30 GB).
8. Clique em **Launch Instance**.

---

### 2. Conectar via SSH e Instalar Docker
No seu computador Linux, dê permissão na chave `.pem` e conecte na instância:
```bash
chmod 400 infra/aws/private/ecopulse-key.pem
ssh -i infra/aws/private/ecopulse-key.pem ubuntu@<IP_PUBLICO_EC2>
```

Dentro da instância EC2, clone o repositório e rode o script de provisionamento:
```bash
git clone https://github.com/wallacevilela7/ecopulse.git
cd ecopulse/infra/aws
chmod +x setup_ec2.sh
./setup_ec2.sh
```
*(Ao terminar, saia com `exit` e reconecte no SSH para ativar o grupo `docker`, ou use `newgrp docker`).*

---

### 3. Subir Tudo (Nginx + FastAPI + Banco PostgreSQL)
Dentro de `~/ecopulse/infra/aws` na EC2, execute:
```bash
docker compose up -d --build
```

Verifique se os 3 containers estão saudáveis:
```bash
docker compose ps
```
- **Dashboard Web Oficial (HTTPS Let's Encrypt):** [https://ecopulse-unip.duckdns.org](https://ecopulse-unip.duckdns.org)
- **Swagger / Documentação da API:** [https://ecopulse-unip.duckdns.org/docs](https://ecopulse-unip.duckdns.org/docs)
- **Healthcheck do Pipeline:** [https://ecopulse-unip.duckdns.org/health](https://ecopulse-unip.duckdns.org/health)

---

### 4. Emissão do Certificado HTTPS (Let's Encrypt) + DuckDNS
Para emitir/renovar o certificado TLS oficial em `/etc/letsencrypt` para o domínio `ecopulse-unip.duckdns.org`:
```bash
docker compose stop webserver
docker run --rm -v /etc/letsencrypt:/etc/letsencrypt -p 80:80 certbot/certbot certonly \
  --standalone -d ecopulse-unip.duckdns.org --non-interactive --agree-tos -m wallace.vilela9@gmail.com
docker compose up -d webserver
```

---

### 5. Apontar a ESP32 para a AWS EC2
No arquivo [`firmware/include/config.h`](../../firmware/include/config.h), mantenha o endpoint HTTP na porta `80` da EC2 (`54.235.41.91`):
```cpp
#define API_URL "http://54.235.41.91/api/v1/telemetry"
```
*(O Nginx aceita o `POST /api/v1/telemetry` diretamente na porta `80` sem exigir handshake TLS na placa embarcada, enquanto redireciona usuários de navegador para `https://ecopulse-unip.duckdns.org` na porta `443`).*
