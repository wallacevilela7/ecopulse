# Stack Tecnológica e Especificações do Projeto (EcoPulse)

**Projeto Integrado Multidisciplinar II (PIM II - UNIP)**  
**Documento de Referência Técnica Global**

---

## 1. Camada de Borda (Hardware & Firmware)

* **Microcontrolador:** ESP32 DevKit V1 (30 pinos)
  * *CPU:* Xtensa Dual-Core 32-bit LX6 (240 MHz)
  * *Memória:* 520 KB SRAM, 4 MB Flash
  * *Conectividade:* Wi-Fi 802.11 b/g/n (2.4 GHz) + Bluetooth v4.2 BR/EDR e BLE
  * *ADC:* Bloco ADC1 exclusivo de 12 bits (GPIOs 32, 34, 35) para coexistência com rádio Wi-Fi
* **Sensores Integrados:**
  * `DHT22 (AM2302)`: Termo-higrômetro digital (Faixa: -40 a 80 °C / 0 a 100% UR) no GPIO 4
  * `BMP280`: Barômetro/Altimétrico I2C Bosch (Faixa: 300 a 1100 hPa) no GPIO 21 (SDA) e 22 (SCL)
  * `MQ-135`: Sensor de gases e qualidade do ar no GPIO 32 (com divisor resistivo 1kΩ/2kΩ, 5V -> máx 3.33V)
  * `LDR 5mm`: Fotossensor analógico de luminosidade no GPIO 35
  * `Pluviômetro LM393 + MH-RD`: Sensor analógico de precipitação no GPIO 34
* **Alimentação:** Módulo de fonte para protoboard MB102 (5.0V exclusivo para MQ-135; 3.3V para barramentos do ESP32 e demais sensores; malha de GND comum)
* **Linguagem & Framework:** C++ (Arduino Core para ESP32)
* **Bibliotecas Embarcadas:** `WiFi.h`, `HTTPClient.h`, `WebServer.h`, `Wire.h`, `DHT.h`, `Adafruit_BMP280.h`

---

## 2. Camada de Backend & Ingestão

* **Linguagem:** Python 3.14 / 3.11+
* **Framework Web:** FastAPI (ASGI framework moderno de alta performance)
* **Servidor ASGI:** Uvicorn (com suporte a uvloop e httptools)
* **Validação de Dados:** Pydantic v2 (validação estrita de contratos e schemas em tempo de execução)
* **ORM & Acesso a Dados:** SQLAlchemy 2.0 (abstração relacional com chaveamento transparente SQLite/PostgreSQL)
* **Segurança:** Autenticação via token no cabeçalho HTTP (`X-API-Key`) e CORS liberado para o dashboard
* **Testes Automatizados:** Pytest com HTTPX / TestClient

---

## 3. Camada de Banco de Dados (Persistência)

* **Ambiente de Desenvolvimento Local:** SQLite 3 (arquivo local `ecopulse.db`, zero dependências externas)
* **Ambiente de Produção em Nuvem:** AWS RDS PostgreSQL 16
  * *Instância:* `db.t4g.micro` ou `db.t3.micro` (AWS Free Tier)
  * *vCPU:* 2 vCPUs (t4g ARM Graviton2) ou 2 vCPUs (t3 x86)
  * *Memória:* 1 GiB RAM
  * *Armazenamento:* 20 GiB SSD gp3 com backups automatizados
  * *Indexação:* Índice composto B-Tree em `(device_id, recorded_at DESC)` para queries em O(1)

---

## 4. Camada de Nuvem & Infraestrutura (AWS)

* **Servidor de Aplicação / Deploy:** AWS EC2 ou AWS App Runner
  * *Opção EC2:* `t2.micro` (ou `t3.micro` / `t4g.small` conforme região)
    * *vCPU:* 1 vCPU (Intel Xeon 3.3 GHz)
    * *Memória:* 1 GiB RAM
    * *Rede:* Até 5 Gbps (EBS-optimized)
    * *Armazenamento de Boot:* 30 GiB EBS gp3 (Free Tier)
    * *Sistema Operacional:* Ubuntu Server 24.04 LTS ou Amazon Linux 2023
  * *Opção App Runner:* Container gerenciado sem necessidade de gerenciar instâncias de SO
* **Hospedagem Frontend:** AWS S3 (Bucket configurado para Static Website Hosting)
* **Distribuição CDN & SSL:** AWS CloudFront com certificado TLS 1.3 gratuito via AWS Certificate Manager (ACM)
* **Segurança de Rede:** AWS Security Groups restringindo porta 5432 do PostgreSQL apenas ao IP do backend

---

## 5. Camada de Frontend (Dashboard)

* **Arquitetura:** Single Page Application (SPA) estática
* **Tecnologias:** HTML5 Semântico, Vanilla CSS moderno (Dark Mode, Glassmorphism, CSS Grid/Flexbox) e JavaScript ES6+
* **Gráficos & Séries Temporais:** Chart.js / Canvas API (temperatura, umidade, pressão e qualidade do ar)
* **Atualização:** Polling assíncrono via `fetch()` consumindo `/api/v1/telemetry/latest` e `/api/v1/telemetry/history`
