# Infraestrutura em Nuvem (AWS) - EcoPulse

Este diretório contém os scripts, configurações e receitas de implantação da infraestrutura do projeto na nuvem Amazon Web Services (AWS).

---

## 📁 Estrutura do Diretório

```
infra/aws/
├── Dockerfile              # Containerização do Backend FastAPI
├── docker-compose.yml      # Orquestração da API e PostgreSQL
├── setup_ec2.sh            # Script de provisionamento automático da VM EC2
├── private/                # [IGNORADO PELO GIT] Arquivos .pem, chaves SSH e senhas
└── README.md               # Este guia
```

---

## 🔒 Segurança de Credenciais Privadas

O subdiretório `infra/aws/private/` está configurado no `.gitignore` global. Guarde nele:
* Pares de chaves SSH (`.pem`, `.id_rsa`);
* Arquivos `.env.aws` com senhas de produção do RDS PostgreSQL;
* Credenciais de acesso AWS CLI (`credentials`).

---

## 🚀 Como Subir o Backend no EC2

1. Conecte-se na sua instância EC2:
   ```bash
   ssh -i private/ecopulse-key.pem ubuntu@<IP_PUBLICO_EC2>
   ```
2. Clone o repositório ou copie os arquivos:
   ```bash
   git clone <URL_REPOSITORIO>
   cd ecopulse/infra/aws
   ```
3. Execute o script de configuração inicial:
   ```bash
   chmod +x setup_ec2.sh && ./setup_ec2.sh
   ```
4. Suba os containers com Docker Compose:
   ```bash
   docker compose up -d --build
   ```
5. Acesse a documentação da API no navegador:
   `http://<IP_PUBLICO_EC2>:8000/docs`
