# Stack Tecnológica e Especificações do Projeto (EcoPulse v3.0 — Versão Final)

**Projeto Integrado Multidisciplinar II (PIM II - UNIP)**  
**Documento de Referência Técnica Global — Arquitetura Dual-Pipeline Hot/Cold Path & Cloud AWS EC2**

---

## 1. Camada de Borda (Hardware & Firmware)

* **Microcontrolador:** ESP32 DevKit V1 (30 pinos, Dual-Core Xtensa LX6 240 MHz, 520 KB SRAM)
* **ADC:** Bloco ADC1 exclusivo de 12 bits (GPIOs 32, 34, 35) operando simultaneamente ao rádio Wi-Fi 2.4 GHz, com multisampling de 16 amostras e leitura de descarte para estabilização do capacitor *Sample-and-Hold*
* **Sensores Integrados:**
  * `DHT22 (AM2302)`: Termo-higrômetro digital One-Wire (GPIO 4)
  * `BMP280`: Barômetro e altímetro I2C (GPIO 21 SDA / GPIO 22 SCL, endereço `0x76`)
  * `MQ-135`: Sensor de gases e qualidade do ar (GPIO 32 com divisor resistivo 1kΩ / 2kΩ, fator $\times 1,5$)
  * `LDR 5mm (Módulo LM393)`: Fotoresistor analógico de luminosidade inversa calibrada (GPIO 35)
  * `LM393 + Placa MH-RD`: Sensor analógico de precipitação pluvial calibrado (`CHUVA_LIMIAR_SECO = 500`, GPIO 34)
* **Alimentação Híbrida de Bancada:** Fonte regulada MB102 (5.0V dedicado ao aquecedor térmico do MQ-135 e 3.3V para sensores) combinada à alimentação USB direta no regulador da ESP32 para suprir picos de corrente (`~400 mA`) do transceptor Wi-Fi sem *brownout*

---

## 2. Camada de Backend & Dual-Pipeline (Hot/Cold Path)

* **Linguagem & Runtime:** Python 3.11+
* **Framework Web & ASGI:** FastAPI + Uvicorn
* **Validação Estrita:** Pydantic v2
* **Hot Path (Caminho Quente — Tempo Real):**
  * Cache de estado instantâneo e ring-buffer circular em memória RAM (`HotColdTelemetryEngine`, últimas 24 amostras)
  * Barramento Pub/Sub assíncrono (`asyncio.Queue`) com entrega via **Server-Sent Events (SSE)** em `< 15ms`
  * Zero operações de escrita em disco nos ciclos intermediários
* **Cold Path (Caminho Frio — Persistência Inteligente WMO-No. 8 / INMET):**
  * Consolidação estatística a cada **5 minutos** (média, mínima e máxima) na tabela `tb_telemetry_aggregated_5m`
  * Detector de **Deadband / Exceção Climática** (início/fim de chuva, variação de luminosidade no LDR $\Delta \ge 15\%$, umidade $\Delta \ge 8\%$, temperatura $\Delta \ge 1,5^\circ\text{C}$, queda barométrica $\ge 2\text{ hPa}$, pico de gases $\ge 50\text{ PPM}$) com persistência imediata em `tb_telemetry_events` e reset da janela estatística
  * Redução comprovada superior a **98% de I/O de disco** em produção
* **ORM & Testes:** SQLAlchemy 2.0 + Pytest (6 testes automatizados com banco SQLite em memória isolado via `StaticPool`)

---

## 3. Camada de Banco de Dados, Domínio HTTPS & Infraestrutura Cloud (AWS EC2)

* **Domínio Público & Segurança TLS:** [https://ecopulse-unip.duckdns.org](https://ecopulse-unip.duckdns.org) (DuckDNS apontando para o IP público `54.235.41.91` da AWS EC2, certificado SSL/TLS oficial **Let's Encrypt / Certbot** com suporte a `HTTP/2` e `TLSv1.3`).
* **Topologia Unificada Single-Host (AWS Free Tier):** Instância EC2 `t3.micro` (Ubuntu Server 24.04 LTS) orquestrada via **Docker Compose** em rede bridge isolada (`ecopulse_net`):
  1. **`webserver` (Nginx Alpine):** Portas públicas `80` (ingestão HTTP da ESP32 + redirect para HTTPS) e `443` (HTTPS TLS); serve o Frontend com Gzip e faz proxy reverso para `/api/` com `proxy_buffering off` para SSE.
  2. **`api` (FastAPI Container):** Porta `8000` conectada à rede `ecopulse_net` com dependência de *healthcheck* do banco.
  3. **`db` (PostgreSQL 16 Alpine):** Porta interna `5432` (isolada da internet) com volume persistente `postgres_data` e *healthcheck* (`pg_isready`).
* **Fallback Local de Bancada:** SQLite 3 automático quando executado fora do Docker sem PostgreSQL ativo.
* **CI/CD Zero-Downtime:** GitHub Actions (`.github/workflows/deploy.yml`) executando Pytest e *rolling update* automático na AWS EC2 via SSH com verificação pós-deploy (`/health`).

---

## 4. Camada de Frontend v3.0 (Climatempo + Google Weather + Apple Bento)

* **Arquitetura:** Single Page Application (SPA) responsiva em HTML5, CSS3 Vanilla (Design Tokens Light/Dark) e JavaScript ES6+
* **Design System Híbrido (v3.0):**
  * **Inspiração Google Weather:** Card principal limpo com ícone meteorológico SVG colorido dinâmico, sensação térmica, ponto de orvalho e gráfico de curva suave em abas (`Temperatura`, `Umidade e Chuva`, `Luz e Ar`, `Pressão`) com Chart.js.
  * **Inspiração Climatempo:** Pílulas de mínima (`↓` azul) e máxima (`↑` laranja) e lista histórica consolidada com barras horizontais de amplitude térmica.
  * **Inspiração Apple Weather (Bento Grid):** 6 mini-cards de propósito único (`Chuva`, `Umidade`, `Luminosidade`, `Qualidade do Ar`, `Pressão` e `Altitude Local`).
  * **Geolocalização Híbrida em 3 Camadas + OpenStreetMap:** GPS nativo do navegador (`navigator.geolocation` via HTTPS), fallback automático por IP (`ipwho.is`), geocodificação reversa de bairro/cidade via Nominatim e mapa interativo Leaflet com tiles oficiais do OpenStreetMap.
