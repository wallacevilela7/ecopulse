# Fluxo de Dados e Topologia de Nuvem: Hot/Cold Path - EcoPulse

> **Documento de Arquitetura de Nuvem e Ciclo de Vida da Informação**  
> **Projeto Integrado Multidisciplinar II (PIM II) — UNIP**  
> **Padrão:** Separação entre Fluxo em Tempo Real (In-Memory Hot Path) e Persistência Otimizada (Cold Path em PostgreSQL)

---

## 1. Topologia Integrada da Infraestrutura

```
[Bancada de Hardware / Nó Físico ESP32]
┌────────────────────────────────────────────────────────┐
│  Estação EcoPulse (ESP32 NodeMCU)                      │
│  - Leitura não-bloqueante dos 5 sensores               │
│  - Transmissão contínua: HTTP POST a cada 2.5s         │
└──────────────────────────┬─────────────────────────────┘
                           │
                           │ HTTP/HTTPS POST /api/v1/telemetry (JSON + X-API-Key)
                           ▼ (Internet Pública / Wi-Fi)
[Instância AWS EC2 (Free Tier) - Docker Compose]
┌─────────────────────────────────────────────────────────────────────────┐
│ Host Linux (Ubuntu LTS)                                                 │
│                                                                         │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │ Container: Nginx (Porteiro / Reverse Proxy) - Porta Pública 80    │  │
│  └───────────────┬──────────────────────────────────▲────────────────┘  │
│                  │                                  │                   │
│   Proxy pass /api/* para o Backend     Entrega estáticos do Frontend    │
│   (proxy_buffering off para SSE)       (HTML5 / CSS Apple / JS)         │
│                  │                                  │                   │
│                  ▼                                  │                   │
│  ┌──────────────────────────────────────────────────┴────────────────┐  │
│  │ Container: API Backend (FastAPI Core)                             │  │
│  │                                                                   │  │
│  │  ┌─────────────────────────────────────────────────────────────┐  │  │
│  │  │ HOT PATH (Memória RAM - Zero I/O de Disco)                  │  │  │
│  │  │ - Cache de estado instantâneo (In-Memory State)             │  │  │
│  │  │ - TelemetryBroadcaster (asyncio.Queue Pub/Sub)              │  │  │
│  │  │ - Canal SSE /api/v1/telemetry/stream (Latência < 15ms)      │  │  │
│  │  └──────────────────────────────┬──────────────────────────────┘  │  │
│  │                                 │ (Entrega instantânea na tela)   │  │
│  │                                 ▼                                 │  │
│  │                     [ Dashboard Web SPA ]                         │  │
│  │                                                                   │  │
│  │  ┌─────────────────────────────────────────────────────────────┐  │  │
│  │  │ COLD PATH (Persistência Otimizada no PostgreSQL)            │  │  │
│  │  │ - Buffer Agregador Temporal (Janela de 5 minutos)           │  │  │
│  │  │ - Detector de Anomalias / Deadband (Chuva, Barômetro, Gás)  │  │  │
│  │  │ - Redução de 99,17% no volume de escrita                    │  │  │
│  │  └──────────────────────────────┬──────────────────────────────┘  │  │
│  └─────────────────────────────────┼─────────────────────────────────┘  │
│                                    │ Conexão SQL Interna                │
│                                    │ (Rede Docker "ecopulse_net")       │
│                                    ▼                                    │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │ Container: PostgreSQL 16 Alpine                                   │  │
│  │ - Porta 5432 protegida (NÃO exposta à Internet)                   │  │
│  │ - Persistência: volume permanente "postgres_data" no disco EC2    │  │
│  │ - Tabelas: tb_telemetry_aggregated_5m e tb_telemetry_events       │  │
│  └───────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Ciclo de Vida da Telemetria

### 2.1. O Caminho Quente (Hot Path — Da Amostra ao Pixel na Tela)
1. **Amostragem:** O ESP32 realiza a leitura física dos sensores na bancada e transmite via `POST /api/v1/telemetry`.
2. **Ingestão em Memória:** O FastAPI valida as credenciais (`X-API-Key`) e o esquema Pydantic, atualizando uma estrutura de dados volátil na memória RAM.
3. **Distribuição Reativa:** O `TelemetryBroadcaster` injeta o payload imediatamente na fila assíncrona de cada cliente Web conectado ao endpoint de streaming SSE (`/api/v1/telemetry/stream`).
4. **Renderização Visual:** O JavaScript do navegador recebe o frame em menos de **15 milissegundos**, dispara os *flashes* sutis de oscilação nos cards Apple e atualiza o Chart.js.
5. **Benefício de Engenharia:** Não ocorre nenhuma chamada ao PostgreSQL para a visualização ao vivo. A tela é fluida e o banco de dados não sofre contenção.

### 2.2. O Caminho Frio (Cold Path — Da Amostra ao Registro Histórico no PostgreSQL)
1. **Bufferização e Estatística:** Paralelamente à exibição em tela, cada amostra é acumulada em uma fila de buffer em memória.
2. **Condição Normal (Janela de 5 Minutos):**
   * A cada 300 segundos, o buffer encerra o período (~120 amostras).
   * Calcula: Médias aritméticas, valores mínimos e valores máximos de Temperatura, Umidade, Pressão, Qualidade do Ar e Luz, além do índice de precipitação acumulada.
   * Executa um único `INSERT` na tabela `tb_telemetry_aggregated_5m`.
   * Esvazia o buffer e inicia a próxima janela.
3. **Condição de Exceção (Disparo por Deadband / Anomalia):**
   * Se o sensor de chuva indicar início de precipitação, se o barômetro registrar queda abrupta ($\Delta P \ge 2\text{ hPa}$) ou se o MQ-135 acusar salto de gases, o sistema grava imediatamente uma linha na tabela `tb_telemetry_events`.
   * Essa estratégia preserva a integridade de eventos críticos com resolução de segundos, sem sobrecarregar a rotina normal do banco.

---

## 3. Segurança e Isolamento Operacional

* **PostgreSQL Isolado na Rede Privada:** A porta `5432` permanece sem qualquer exposição para fora da máquina EC2, acessível apenas pelo hostname `db:5432` dentro da rede Docker `ecopulse_net`.
* **Zero-Downtime Rolling Update:** A esteira CI/CD atualiza a API backend sem derrubar o container do PostgreSQL nem interromper a persistência do volume `postgres_data`.
* **Histórico de Versões:** O fluxo legado v1 (gravação direta a cada tick) encontra-se arquivado para consultas em [**`ecopulse/docs/archive/fluxo_dados_v1_legado.md`**](file:///home/wvs/Documents/pim2/ecopulse/docs/archive/fluxo_dados_v1_legado.md).
