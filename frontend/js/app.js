/**
 * EcoPulse Clima — Controlador Principal (Climatempo + Google Weather + Apple Bento)
 */

(function () {
  // Detecta se está rodando localmente (arquivo local file://, localhost, 127.0.0.1 ou porta de dev)
  // Em produção na AWS EC2 (Nginx na porta 80), usa caminho relativo "" (/api/v1/...)
  const isFileProtocol = window.location.protocol === "file:" || !window.location.hostname;
  const isLocalHost =
    window.location.hostname === "localhost" ||
    window.location.hostname === "127.0.0.1" ||
    window.location.hostname.startsWith("192.168.");
  const isDevPort =
    window.location.port !== "" &&
    window.location.port !== "80" &&
    window.location.port !== "443" &&
    window.location.port !== "8000";

  const API_BASE = isFileProtocol
    ? "http://127.0.0.1:8000"
    : isLocalHost || isDevPort
    ? `http://${window.location.hostname}:8000`
    : "";

  let eventSource = null;
  let historyLimit = 24;
  let previousPressure = null;

  function fmtNum(val, decimals = 1, fallback = "--") {
    if (val === null || val === undefined || Number.isNaN(Number(val))) {
      return fallback;
    }
    return Number(val).toFixed(decimals).replace(".", ",");
  }

  function fmtTime(isoStr, withSeconds = false) {
    if (!isoStr) return "--:--";
    const d = new Date(isoStr);
    if (Number.isNaN(d.getTime())) return "--:--";
    return d.toLocaleTimeString("pt-BR", {
      hour: "2-digit",
      minute: "2-digit",
      ...(withSeconds ? { second: "2-digit" } : {}),
    });
  }

  function calcDewPoint(tempC, humPct) {
    if (tempC == null || humPct == null || humPct <= 0) return null;
    const a = 17.27;
    const b = 237.7;
    const alpha = (a * tempC) / (b + tempC) + Math.log(humPct / 100.0);
    return (b * alpha) / (a - alpha);
  }

  function calcFeelsLike(tempC, humPct) {
    if (tempC == null || humPct == null) return null;
    const vaporPressure = (humPct / 100.0) * 6.105 * Math.exp((17.27 * tempC) / (237.7 + tempC));
    return tempC + 0.33 * vaporPressure - 4.0;
  }

  function setConnectionStatus(state, text) {
    const dot = document.getElementById("status-dot");
    const label = document.getElementById("status-text");
    if (dot) {
      dot.className = "live-dot";
      if (state === "online") dot.classList.add("online");
      if (state === "offline") dot.classList.add("offline");
    }
    if (label) label.textContent = text;
  }

  // Ícones SVG Coloridos Estilo Google Weather
  function getWeatherIllustration(isRaining, lightPct) {
    if (isRaining) {
      return `
        <svg viewBox="0 0 64 64" width="68" height="68">
          <path d="M46 36H20a10 10 0 0 1-.8-19.96A14 14 0 0 1 46 20a8 8 0 0 1 0 16z" fill="#94A3B8"/>
          <line x1="24" y1="42" x2="21" y2="52" stroke="#0284C7" stroke-width="3" stroke-linecap="round"/>
          <line x1="33" y1="42" x2="30" y2="52" stroke="#0284C7" stroke-width="3" stroke-linecap="round"/>
          <line x1="42" y1="42" x2="39" y2="52" stroke="#0284C7" stroke-width="3" stroke-linecap="round"/>
        </svg>`;
    }
    if (lightPct != null && lightPct < 20) {
      return `
        <svg viewBox="0 0 64 64" width="68" height="68">
          <path d="M42 38A16 16 0 0 1 26 22a16.2 16.2 0 0 1 2.2-8.2A16 16 0 1 0 48.2 35.8 16.2 16.2 0 0 1 42 38z" fill="#F59E0B"/>
          <circle cx="46" cy="18" r="1.8" fill="#FBBF24"/>
          <circle cx="38" cy="12" r="1.2" fill="#FBBF24"/>
        </svg>`;
    }
    if (lightPct != null && lightPct < 65) {
      return `
        <svg viewBox="0 0 64 64" width="68" height="68">
          <circle cx="24" cy="24" r="11" fill="#F59E0B"/>
          <path d="M46 42H22a9 9 0 0 1-.7-17.97A12.5 12.5 0 0 1 45.5 27a7.5 7.5 0 0 1 .5 15z" fill="#CBD5E1"/>
        </svg>`;
    }
    return `
      <svg viewBox="0 0 64 64" width="68" height="68">
        <circle cx="32" cy="32" r="15" fill="#F59E0B"/>
        <g stroke="#F59E0B" stroke-width="3.2" stroke-linecap="round">
          <line x1="32" y1="7" x2="32" y2="12"/>
          <line x1="32" y1="52" x2="32" y2="57"/>
          <line x1="7" y1="32" x2="12" y2="32"/>
          <line x1="52" y1="32" x2="57" y2="32"/>
          <line x1="14.3" y1="14.3" x2="17.8" y2="17.8"/>
          <line x1="46.2" y1="46.2" x2="49.7" y2="49.7"/>
          <line x1="49.7" y1="14.3" x2="46.2" y2="17.8"/>
          <line x1="17.8" y1="46.2" x2="14.3" y2="49.7"/>
        </g>
      </svg>`;
  }

  function normalizeTelemetry(packet) {
    if (!packet) return null;
    const s = packet.sensors || {};
    const d = packet.diagnostics || {};
    const ext = packet.extremes || {};

    const tempC = s.temperature_c ?? packet.temperature_c ?? packet.temp_avg ?? null;
    const humPct = s.humidity_pct ?? packet.humidity_pct ?? packet.humidity_avg ?? null;
    const pressHpa = s.pressure_hpa ?? packet.pressure_hpa ?? packet.pressure_avg ?? null;
    const altM = s.altitude_m ?? packet.altitude_m ?? packet.altitude_avg ?? null;
    const aqiPpm = s.air_quality_ppm ?? packet.air_quality_ppm ?? packet.air_quality_avg ?? null;
    const lightPct = s.luminosity_pct ?? packet.luminosity_pct ?? packet.luminosity_avg ?? null;
    const rainPct = s.rain_intensity_pct ?? packet.rain_intensity_pct ?? packet.rain_intensity_avg ?? 0.0;
    const isRaining = Boolean(s.is_raining ?? packet.is_raining ?? packet.is_raining_period ?? false);

    return {
      deviceId: packet.device_id || "esp32-meteo-01",
      recordedAt: packet.recorded_at || packet.window_end || new Date().toISOString(),
      tempC,
      humPct,
      pressHpa,
      altM,
      aqiPpm,
      lightPct,
      rainPct,
      isRaining,
      tempMin: ext.temp_min ?? packet.temp_min ?? tempC,
      tempMax: ext.temp_max ?? packet.temp_max ?? tempC,
      pressMin: ext.pressure_min ?? packet.pressure_min ?? pressHpa,
      pressMax: ext.pressure_max ?? packet.pressure_max ?? pressHpa,
      aqiMax: ext.air_quality_max ?? packet.air_quality_max ?? aqiPpm,
      rssi: d.wifi_rssi_dbm ?? packet.wifi_rssi_dbm ?? null,
      uptime: d.uptime_seconds ?? packet.uptime_seconds ?? null,
      pipeline: packet.pipeline || null,
    };
  }

  function updateCurrentWeatherUI(rawPacket) {
    const data = normalizeTelemetry(rawPacket);
    if (!data) return;

    document.getElementById("header-device-id").textContent = data.deviceId;
    document.getElementById("last-update-time").textContent = fmtTime(data.recordedAt, true);

    // Hero Card (Esquerda)
    document.getElementById("val-temp").textContent = fmtNum(data.tempC, 1);
    document.getElementById("val-temp-min").textContent = `${fmtNum(data.tempMin, 1)}°`;
    document.getElementById("val-temp-max").textContent = `${fmtNum(data.tempMax, 1)}°`;

    const feels = calcFeelsLike(data.tempC, data.humPct);
    const dew = calcDewPoint(data.tempC, data.humPct);
    document.getElementById("val-feels-like").textContent = `${fmtNum(feels, 1)}°C`;
    document.getElementById("val-dew-point").textContent = `${fmtNum(dew, 1)}°C`;

    // Condição geral e ícone
    const heroIcon = document.getElementById("hero-weather-icon");
    const condPill = document.getElementById("hero-condition-text");
    const isRainingActive = data.isRaining && data.rainPct >= 5;

    if (heroIcon) {
      heroIcon.innerHTML = getWeatherIllustration(isRainingActive, data.lightPct);
    }
    if (condPill) {
      if (isRainingActive) condPill.textContent = "Chuva no local";
      else if (data.lightPct != null && data.lightPct < 20) condPill.textContent = "Noite / Escuro";
      else if (data.lightPct != null && data.lightPct < 65) condPill.textContent = "Parcialmente nublado";
      else condPill.textContent = "Ensolarado / Claridade alta";
    }

    // 1. Mini-Card: Chuva
    document.getElementById("val-rain").textContent = fmtNum(data.rainPct, 0, "0");
    document.getElementById("bar-rain").style.width = `${Math.min(100, Math.max(0, data.rainPct))}%`;
    const rainBadge = document.getElementById("badge-rain-state");
    const rainDesc = document.getElementById("val-rain-desc");
    if (!isRainingActive) {
      rainBadge.textContent = "Sem chuva";
      rainBadge.className = "status-tag tag-green";
      rainDesc.textContent = "Tempo seco no momento";
    } else {
      rainBadge.textContent = data.rainPct >= 50 ? "Chuva forte" : "Chovendo";
      rainBadge.className = "status-tag tag-amber";
      rainDesc.textContent = "Precipitação detectada pelo sensor";
    }

    // 2. Mini-Card: Umidade
    document.getElementById("val-humidity").textContent = fmtNum(data.humPct, 0);
    document.getElementById("bar-humidity").style.width = `${Math.min(100, Math.max(0, data.humPct || 0))}%`;
    const humBadge = document.getElementById("val-humidity-state");
    if (data.humPct != null) {
      if (data.humPct < 35) {
        humBadge.textContent = "Ar seco";
        humBadge.className = "status-tag tag-amber";
      } else if (data.humPct > 75) {
        humBadge.textContent = "Úmido";
        humBadge.className = "status-tag";
      } else {
        humBadge.textContent = "Confortável";
        humBadge.className = "status-tag tag-green";
      }
    }

    // 3. Mini-Card: Luminosidade
    document.getElementById("val-light").textContent = fmtNum(data.lightPct, 0);
    document.getElementById("bar-light").style.width = `${Math.min(100, Math.max(0, data.lightPct || 0))}%`;
    const lightBadge = document.getElementById("badge-light-state");
    const lightDesc = document.getElementById("val-light-desc");
    if (data.lightPct != null) {
      if (data.lightPct < 20) {
        lightBadge.textContent = "Baixa";
        lightDesc.textContent = "Ambiente escuro ou noturno";
      } else if (data.lightPct < 70) {
        lightBadge.textContent = "Moderada";
        lightDesc.textContent = "Claridade suave / interna";
      } else {
        lightBadge.textContent = "Intensa";
        lightDesc.textContent = "Alta incidência luminosa";
      }
    }

    // 4. Mini-Card: Qualidade do Ar
    document.getElementById("val-aqi").textContent = fmtNum(data.aqiPpm, 0);
    document.getElementById("val-aqi-max").textContent = `${fmtNum(data.aqiMax, 0)} ppm`;
    document.getElementById("bar-aqi").style.width = `${Math.min(100, Math.max(4, ((data.aqiPpm || 10) / 1000) * 100))}%`;
    const aqiBadge = document.getElementById("badge-aqi-class");
    if (data.aqiPpm != null) {
      if (data.aqiPpm >= 1000) {
        aqiBadge.textContent = "Moderada";
        aqiBadge.className = "status-tag tag-amber";
      } else {
        aqiBadge.textContent = "Boa";
        aqiBadge.className = "status-tag tag-green";
      }
    }

    // 5. Mini-Card: Pressão
    document.getElementById("val-pressure").textContent = fmtNum(data.pressHpa, 1, "----");
    document.getElementById("val-pressure-min").textContent = fmtNum(data.pressMin, 0, "----");
    document.getElementById("val-pressure-max").textContent = fmtNum(data.pressMax, 0, "----");
    const trendEl = document.getElementById("val-pressure-trend");
    if (data.pressHpa != null) {
      if (previousPressure !== null) {
        const diff = data.pressHpa - previousPressure;
        if (diff >= 0.4) trendEl.textContent = `Subindo (+${fmtNum(diff, 1)} hPa)`;
        else if (diff <= -0.4) trendEl.textContent = `Caindo (${fmtNum(diff, 1)} hPa)`;
        else trendEl.textContent = "Estável no momento";
      }
      previousPressure = data.pressHpa;
    }

    // 6. Mini-Card: Altitude e Wi-Fi
    document.getElementById("val-altitude").textContent = fmtNum(data.altM, 0, "---");
    if (data.rssi != null) {
      document.getElementById("diag-rssi").textContent = `${data.rssi} dBm`;
    }

    // Estatísticas do Sistema
    if (data.pipeline) {
      const hot = data.pipeline.hot_ticks_total || 0;
      const cold = data.pipeline.cold_writes_total || 0;
      const saved = hot > 0 && cold <= hot ? `${((1 - cold / hot) * 100).toFixed(0)}%` : "0%";
      document.getElementById("diag-hot-ticks").textContent = String(hot);
      document.getElementById("diag-cold-writes").textContent = String(cold);
      document.getElementById("diag-io-saved").textContent = saved;
    }

    if (window.EcoPulseMap) {
      window.EcoPulseMap.updateStationPopup(data.tempC, data.humPct, data.pressHpa);
    }
  }

  // Renderiza a lista histórica com barras de amplitude estilo Climatempo / iPhone
  function renderClimatempoList(historyList) {
    const container = document.getElementById("windows-list-body");
    if (!container) return;

    if (!Array.isArray(historyList) || historyList.length === 0) {
      container.innerHTML = `<div class="empty-state">Nenhuma medição consolidada disponível ainda.</div>`;
      return;
    }

    const items = [...historyList].reverse().slice(0, 20).map(normalizeTelemetry);
    const allMins = items.map((x) => x.tempMin ?? x.tempC ?? 20);
    const allMaxs = items.map((x) => x.tempMax ?? x.tempC ?? 25);
    const globalMin = Math.min(...allMins) - 0.5;
    const globalMax = Math.max(...allMaxs) + 0.5;
    const totalSpan = Math.max(1, globalMax - globalMin);

    container.innerHTML = items
      .map((d) => {
        const tMin = d.tempMin ?? d.tempC ?? 20;
        const tMax = d.tempMax ?? d.tempC ?? 20;
        const leftPct = Math.max(0, Math.min(85, ((tMin - globalMin) / totalSpan) * 100));
        const widthPct = Math.max(12, Math.min(100 - leftPct, ((tMax - tMin) / totalSpan) * 100));
        const rainText = d.isRaining && d.rainPct >= 5 ? `${fmtNum(d.rainPct, 0)}%` : "0%";

        return `
          <div class="ct-row">
            <div class="ct-time-col">
              <span>${fmtTime(d.recordedAt)}</span>
            </div>
            <div class="ct-rain-col" title="Intensidade de chuva">
              <svg viewBox="0 0 16 16" width="13" height="13" fill="currentColor">
                <path d="M8 1.5l4.2 4.2a6 6 0 1 1-8.4 0L8 1.5z"/>
              </svg>
              <span>${rainText}</span>
            </div>
            <div class="ct-temp-bar-col">
              <span class="ct-min">${fmtNum(tMin, 1)}°</span>
              <div class="ct-bar-track">
                <div class="ct-bar-fill" style="left:${leftPct}%;width:${widthPct}%;"></div>
              </div>
              <span class="ct-max">${fmtNum(tMax, 1)}°</span>
            </div>
            <div class="ct-meta-col">
              Umid. ${fmtNum(d.humPct, 0)}%
            </div>
          </div>
        `;
      })
      .join("");
  }

  function renderEventsList(eventsList) {
    const container = document.getElementById("events-list-body");
    const badge = document.getElementById("events-count-badge");
    const banner = document.getElementById("alert-banner");

    if (badge) {
      badge.textContent = Array.isArray(eventsList) ? String(eventsList.length) : "0";
    }

    if (!Array.isArray(eventsList) || eventsList.length === 0) {
      if (container) {
        container.innerHTML = `<div class="empty-state">Nenhum alerta climático registrado recentemente.</div>`;
      }
      if (banner) banner.classList.add("hidden");
      return;
    }

    const latest = eventsList[0];
    if (banner && latest) {
      const ageMin = (Date.now() - new Date(latest.recorded_at).getTime()) / 60000;
      if (ageMin <= 15 && latest.severity !== "INFO") {
        banner.classList.remove("hidden");
        document.getElementById("alert-title").textContent = latest.title;
        document.getElementById("alert-description").textContent = latest.description;
        document.getElementById("alert-time").textContent = fmtTime(latest.recorded_at);
      } else {
        banner.classList.add("hidden");
      }
    }

    if (container) {
      container.innerHTML = eventsList
        .map(
          (ev) => `
          <div class="event-item">
            <div class="event-item-top">
              <strong>${ev.title}</strong>
              <span class="status-tag">${fmtTime(ev.recorded_at)}</span>
            </div>
            <p class="event-item-desc">${ev.description}</p>
          </div>
        `
        )
        .join("");
    }
  }

  async function syncAllData() {
    try {
      const [latestRes, historyRes, eventsRes, healthRes] = await Promise.all([
        fetch(`${API_BASE}/api/v1/telemetry/latest`),
        fetch(`${API_BASE}/api/v1/telemetry/history?limit=${historyLimit}`),
        fetch(`${API_BASE}/api/v1/telemetry/events?limit=15`),
        fetch(`${API_BASE}/health`),
      ]);

      if (latestRes.ok) {
        const latest = await latestRes.json();
        if (latest && latest.status !== "empty") {
          updateCurrentWeatherUI(latest);
        }
      }

      if (historyRes.ok) {
        const history = await historyRes.json();
        renderClimatempoList(history);
        if (window.EcoPulseCharts) {
          window.EcoPulseCharts.renderOrUpdate(history);
        }
      }

      if (eventsRes.ok) {
        const events = await eventsRes.json();
        renderEventsList(events);
      }

      if (healthRes.ok) {
        const health = await healthRes.json();
        if (health && health.pipeline_metrics) {
          const m = health.pipeline_metrics;
          document.getElementById("diag-hot-ticks").textContent = String(m.hot_path_ticks_received);
          document.getElementById("diag-cold-writes").textContent = String(m.cold_path_db_writes);
          document.getElementById("diag-io-saved").textContent = `${Number(m.disk_io_reduction_pct || 0).toFixed(0)}%`;
        }
      }
    } catch (err) {
      console.warn("[EcoPulse] Erro ao sincronizar dados:", err);
    }
  }

  function connectRealtimeStream() {
    if (eventSource) eventSource.close();
    eventSource = new EventSource(`${API_BASE}/api/v1/telemetry/stream`);

    eventSource.onopen = function () {
      setConnectionStatus("online", "Ao vivo");
    };

    eventSource.onmessage = function (event) {
      try {
        const packet = JSON.parse(event.data);
        setConnectionStatus("online", "Ao vivo");
        updateCurrentWeatherUI(packet);

        if (window.EcoPulseCharts) {
          window.EcoPulseCharts.pushLiveSample(packet, historyLimit);
        }
        if (packet.pipeline && packet.pipeline.cold_path_persisted) {
          syncAllData();
        }
      } catch (err) {
        console.error("[EcoPulse] Erro no pacote SSE:", err);
      }
    };

    eventSource.onerror = function () {
      setConnectionStatus("offline", "Reconectando...");
    };
  }

  function setupInteractions() {
    // Abas estilo Google Weather para o gráfico
    const gTabs = document.querySelectorAll("[data-chart-mode]");
    gTabs.forEach((btn) => {
      btn.addEventListener("click", () => {
        gTabs.forEach((b) => {
          b.classList.remove("active");
          b.setAttribute("aria-selected", "false");
        });
        btn.classList.add("active");
        btn.setAttribute("aria-selected", "true");
        if (window.EcoPulseCharts) {
          window.EcoPulseCharts.setMode(btn.getAttribute("data-chart-mode"));
        }
      });
    });

    // Abas do Histórico (Medições vs Alertas)
    const logTabs = document.querySelectorAll("[data-log-tab]");
    const tabWin = document.getElementById("tab-content-windows");
    const tabEv = document.getElementById("tab-content-events");
    logTabs.forEach((btn) => {
      btn.addEventListener("click", () => {
        logTabs.forEach((b) => b.classList.remove("active"));
        btn.classList.add("active");
        if (btn.getAttribute("data-log-tab") === "events") {
          tabWin.classList.add("hidden");
          tabEv.classList.remove("hidden");
        } else {
          tabEv.classList.add("hidden");
          tabWin.classList.remove("hidden");
        }
      });
    });

    // Seletor de quantidade de medições
    const limitSelect = document.getElementById("history-limit-select");
    if (limitSelect) {
      limitSelect.addEventListener("change", (e) => {
        historyLimit = Number(e.target.value) || 24;
        syncAllData();
      });
    }

    // Tema Claro (Padrão Climatempo/Google) / Modo Escuro
    const themeBtn = document.getElementById("btn-theme-toggle");
    const themeLabel = document.getElementById("theme-label");
    const savedTheme = localStorage.getItem("ecopulse_ui_theme_v3") || "light";
    document.documentElement.setAttribute("data-theme", savedTheme);
    if (themeLabel) {
      themeLabel.textContent = savedTheme === "dark" ? "Modo claro" : "Modo escuro";
    }

    if (themeBtn) {
      themeBtn.addEventListener("click", () => {
        const curr = document.documentElement.getAttribute("data-theme") === "dark" ? "dark" : "light";
        const next = curr === "dark" ? "light" : "dark";
        document.documentElement.setAttribute("data-theme", next);
        localStorage.setItem("ecopulse_ui_theme_v3", next);
        if (themeLabel) {
          themeLabel.textContent = next === "dark" ? "Modo claro" : "Modo escuro";
        }
        if (window.EcoPulseCharts) window.EcoPulseCharts.renderOrUpdate();
        if (window.EcoPulseMap) window.EcoPulseMap.updateThemeTiles();
      });
    }

    const refreshBtn = document.getElementById("btn-refresh");
    if (refreshBtn) {
      refreshBtn.addEventListener("click", syncAllData);
    }
  }

  document.addEventListener("DOMContentLoaded", () => {
    setupInteractions();
    if (window.EcoPulseMap) window.EcoPulseMap.init();
    syncAllData();
    connectRealtimeStream();
    setInterval(syncAllData, 15000);
  });
})();
