# Stack Tecnológica e Especificações do Projeto (EcoPulse v2.0)

**Projeto Integrado Multidisciplinar II (PIM II - UNIP)**  
**Documento de Referência Técnica Global — Arquitetura Hot/Cold Path**

---

## 1. Camada de Borda (Hardware & Firmware)

* **Microcontrolador:** ESP32 DevKit V1 (30 pinos, Dual-Core Xtensa LX6 240 MHz, 520 KB SRAM)
* **ADC:** Bloco ADC1 exclusivo de 12 bits (GPIOs 32, 34, 35) operando simultaneamente ao rádio Wi-Fi 2.4 GHz
* **Sensores Integrados:**
  * `DHT22 (AM2302)`: Termo-higrômetro digital (GPIO 4)
  * `BMP280`: Barômetro e altímetro I2C (GPIO 21 SDA / GPIO 22 SCL)
  * `MQ-135`: Sensor de gases e qualidade do ar (GPIO 32 com divisor resistivo 1kΩ / 2kΩ)
  * `LDR 5mm`: Fotoresistor analógico de luminosidade (GPIO 35)
  * `LM393 + Placa MH-RD`: Sensor analógico de precipitação pluvial (GPIO 34)
* **Alimentação:** Fonte regulada MB102 (5.0V para aquecedor do MQ-135; 3.3V para ESP32 e demais sensores; GND comum)

---

## 2. Camada de Backend & Dual-Pipeline (Hot/Cold Path)

* **Linguagem & Runtime:** Python 3.11+
* **Framework Web & ASGI:** FastAPI + Uvicorn
* **Validação Estrita:** Pydantic v2
* **Hot Path (Caminho Quente — Tempo Real):**
  * Cache de estado instantâneo e ring-buffer em memória RAM (`HotColdTelemetryEngine`)
  * Barramento Pub/Sub assíncrono (`asyncio.Queue`) com entrega via **Server-Sent Events (SSE)** em `< 15ms`
  * Zero operações de escrita em disco nos ciclos intermediários
* **Cold Path (Caminho Frio — Persistência Inteligente WMO-No. 8 / INMET):**
  * Consolidação estatística a cada **5 minutos** (média, mínima e máxima) na tabela `tb_telemetry_aggregated_5m`
  * Detector de **Deadband / Exceção Climática** (chuva súbita, queda barométrica $\ge 2\text{ hPa}$, pico de gases $\ge 50\text{ PPM}$) com persistência imediata em `tb_telemetry_events`
  * Redução de **99,17% de I/O de disco** comparado à gravação ingênua por tick
* **ORM & Testes:** SQLAlchemy 2.0 + Pytest

---

## 3. Camada de Banco de Dados & Infraestrutura Cloud (AWS EC2)

* **Topologia Unificada Single-Host (AWS Free Tier):** Instância EC2 `t2.micro` / `t3.micro` (Ubuntu Server LTS) orquestrada via **Docker Compose** em rede bridge isolada (`ecopulse_net`):
  1. **`webserver` (Nginx Alpine):** Porta pública 80; serve o Frontend com Gzip e faz proxy reverso para `/api/` com `proxy_buffering off` para SSE.
  2. **`api` (FastAPI Container):** Porta interna 8000 (não exposta externamente).
  3. **`db` (PostgreSQL 16 Alpine):** Porta interna 5432 (totalmente isolada da internet) com volume persistente `postgres_data`.
* **Fallback Local de Bancada:** SQLite 3 automático quando executado fora do Docker sem PostgreSQL ativo.
* **CI/CD Zero-Downtime:** GitHub Actions (`.github/workflows/deploy.yml`) executando Pytest e *rolling update* via SSH.

---

## 4. Camada de Frontend (Apple iOS Weather UI)

* **Arquitetura:** Single Page Application (SPA) leve em HTML5, CSS3 Vanilla e JavaScript ES6+
* **Design System:** Inspirado no aplicativo nativo **Clima (Weather) do iOS**:
  * **1ª Dobra (Condições Atuais + Peek):** Hero centralizado flutuante (`22°`), Banner de Alertas (`Storm & More` style), faixa horizontal de `Condições` e *peek* do card de Amplitude Térmica com barras gradientes laranjas.
  * **2ª Dobra (Dashboard Completo ao rolar):** Bento Grid dos 5 sensores físicos, Sensação Térmica, Ponto de Orvalho, Gráfico Chart.js, Mapa Leaflet (Raio 450m) e telemetria do pipeline Hot/Cold Path.
  * **Barra Inferior Flutuante:** Navegação rápida entre Topo, Dashboard Completo e Mapa.
