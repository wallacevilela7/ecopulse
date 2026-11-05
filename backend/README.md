# EcoPulse Backend — Dual-Pipeline (Hot Path & Cold Path)

API em **FastAPI** e **SQLAlchemy 2.0** projetada para conciliar exibição em tempo real (`< 15ms`) com armazenamento otimizado no **PostgreSQL**, em conformidade com as recomendações da **WMO-No. 8** e do **INMET**.

---

## 1. Arquitetura Dual-Pipeline

1. **Hot Path (Memória RAM + Streaming SSE):**
   * Recebe leituras do ESP32 a cada 2,5 segundos (`POST /api/v1/telemetry`).
   * Atualiza o estado instantâneo em RAM (`HotColdTelemetryEngine`) e faz broadcast via **Server-Sent Events** (`GET /api/v1/telemetry/stream`).
   * **Zero I/O de disco** nos ciclos intermediários.
2. **Cold Path (Persistência Inteligente no PostgreSQL):**
   * **Janela Temporal de 5 Minutos (`WINDOW_5M`):** Consolida média, mínima e máxima na tabela `tb_telemetry_aggregated_5m`, reduzindo o volume de escrita em **99,17%**.
   * **Detector de Deadband (`DEADBAND_EVENT`):** Mudanças abruptas (início/fim de chuva, queda barométrica $\ge 2.0\text{ hPa}$, salto de gases $\ge 50\text{ PPM}$ ou variação térmica $\ge 1.5^\circ\text{C}$) disparam gravação imediata em `tb_telemetry_events` e snapshot na série temporal.

---

## 2. Como Executar e Testar

```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Executar a suíte de testes automatizados:
```bash
PYTHONPATH=. pytest tests/ -v
```
