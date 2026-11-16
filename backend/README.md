# EcoPulse Backend v2.1 — Dual-Pipeline (Hot Path & Cold Path)

API em **FastAPI** e **SQLAlchemy 2.0** projetada para conciliar exibição em tempo real (`< 15ms`) com armazenamento otimizado no **PostgreSQL 16** (ou **SQLite** em bancada local), em conformidade com as recomendações da **WMO-No. 8** e do **INMET**.

---

## 1. Arquitetura Dual-Pipeline

1. **Hot Path (Memória RAM + Ring-Buffer + Streaming SSE):**
   * Recebe leituras do ESP32 a cada 2,5 segundos (`POST /api/v1/telemetry`).
   * Atualiza o estado instantâneo e o *ring-buffer* circular das últimas 24 leituras em RAM (`HotColdTelemetryEngine`) e faz broadcast imediato via **Server-Sent Events** (`GET /api/v1/telemetry/stream`).
   * **Zero I/O de disco** nos ciclos intermediários.
   * A rota `GET /api/v1/telemetry/history` mescla automaticamente as janelas consolidadas do banco de dados com as amostras recentes em memória RAM.
2. **Cold Path (Persistência Inteligente no PostgreSQL / SQLite):**
   * **Janela Temporal de 5 Minutos (`WINDOW_5M`):** Consolida média, mínima e máxima na tabela `tb_telemetry_aggregated_5m`, reduzindo o volume de escrita em mais de **98%**.
   * **Detector de Deadband (`DEADBAND_EVENT`):** Mudanças abruptas — início/fim de chuva (`RAIN_START` / `RAIN_STOP`), variação brusca de luminosidade no LDR $\Delta \ge 15\%$ (`LUMINOSITY_SHIFT`), salto de umidade $\Delta \ge 8\%$ (`HUMIDITY_SHIFT`), queda barométrica $\ge 2.0\text{ hPa}$ (`PRESSURE_DROP`), pico de gases $\ge 50\text{ PPM}$ (`GAS_SPIKE`) ou variação térmica $\ge 1.5^\circ\text{C}$ (`TEMP_SPIKE`) — disparam gravação imediata em `tb_telemetry_events`, resetam a janela de consolidação e enviam o alerta em tempo real via SSE ao frontend.

---

## 2. Como Executar e Testar

```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Executar a suíte de 6 testes automatizados (banco SQLite isolado em memória via `StaticPool`):
```bash
PYTHONPATH=. pytest tests/ -v
```
