/**
 * EcoPulse Clima — Gráfico Suave Estilo Google Weather (Chart.js)
 * Modos:
 *  - thermo: Curva suave de Temperatura (°C) em âmbar/laranja
 *  - humidity_rain: Umidade relativa (%) e Intensidade de Chuva (%)
 *  - pressure: Pressão atmosférica (hPa)
 */

window.EcoPulseCharts = (function () {
  let chartInstance = null;
  let currentMode = "thermo";
  let cachedSeries = [];

  function getTokens() {
    const isDark = document.documentElement.getAttribute("data-theme") === "dark";
    return {
      grid: isDark ? "rgba(255, 255, 255, 0.06)" : "rgba(15, 23, 42, 0.06)",
      tick: isDark ? "#94a3b8" : "#64748b",
      tooltipBg: isDark ? "#0f172a" : "#0f172a",
      amber: "#f59e0b",
      amberFill: isDark ? "rgba(245, 158, 11, 0.16)" : "rgba(245, 158, 11, 0.14)",
      blue: "#0284c7",
      blueFill: isDark ? "rgba(56, 189, 248, 0.16)" : "rgba(2, 132, 199, 0.12)",
      cyan: "#06b6d4",
      purple: "#6366f1",
      purpleFill: isDark ? "rgba(129, 140, 248, 0.16)" : "rgba(99, 102, 241, 0.12)",
    };
  }

  function extractMetric(item, key, fallbackKey) {
    if (item && item.sensors && item.sensors[key] != null) {
      return Number(item.sensors[key]);
    }
    if (item && item[key] != null) {
      return Number(item[key]);
    }
    if (fallbackKey && item && item[fallbackKey] != null) {
      return Number(item[fallbackKey]);
    }
    return null;
  }

  function formatHourLabel(isoStr) {
    if (!isoStr) return "--:--";
    const d = new Date(isoStr);
    if (Number.isNaN(d.getTime())) return "--:--";
    return d.toLocaleTimeString("pt-BR", {
      hour: "2-digit",
      minute: "2-digit",
    });
  }

  function buildModeDataset(series, mode) {
    const t = getTokens();

    if (mode === "humidity_rain") {
      const hums = series.map((x) => extractMetric(x, "humidity_pct", "humidity_avg"));
      const rains = series.map((x) => extractMetric(x, "rain_intensity_pct", "rain_intensity_avg") || 0);
      return {
        datasets: [
          {
            label: "Umidade (%)",
            data: hums,
            borderColor: t.blue,
            backgroundColor: t.blueFill,
            borderWidth: 2.5,
            pointRadius: 3,
            pointHoverRadius: 5,
            fill: true,
            tension: 0.38,
          },
          {
            label: "Chuva (%)",
            data: rains,
            borderColor: t.cyan,
            backgroundColor: "transparent",
            borderWidth: 2,
            borderDash: [4, 4],
            pointRadius: 2.5,
            fill: false,
            tension: 0.35,
          },
        ],
        unitSuffix: "%",
      };
    }

    if (mode === "pressure") {
      const press = series.map((x) => extractMetric(x, "pressure_hpa", "pressure_avg"));
      return {
        datasets: [
          {
            label: "Pressão (hPa)",
            data: press,
            borderColor: t.purple,
            backgroundColor: t.purpleFill,
            borderWidth: 2.5,
            pointRadius: 3,
            pointHoverRadius: 5,
            fill: true,
            tension: 0.35,
          },
        ],
        unitSuffix: " hPa",
      };
    }

    // Default: "thermo" (Estilo Google Weather)
    const temps = series.map((x) => extractMetric(x, "temperature_c", "temp_avg"));
    return {
      datasets: [
        {
          label: "Temperatura (°C)",
          data: temps,
          borderColor: t.amber,
          backgroundColor: t.amberFill,
          borderWidth: 3,
          pointRadius: 3.5,
          pointBackgroundColor: t.amber,
          pointHoverRadius: 6,
          fill: true,
          tension: 0.4,
        },
      ],
      unitSuffix: "°C",
    };
  }

  function renderOrUpdate(series) {
    if (Array.isArray(series)) {
      cachedSeries = series;
    }
    const ctx = document.getElementById("mainSynopticChart");
    if (!ctx) return;

    const t = getTokens();
    const labels = cachedSeries.map((item) => formatHourLabel(item.recorded_at || item.window_end));
    const spec = buildModeDataset(cachedSeries, currentMode);

    if (chartInstance) {
      chartInstance.destroy();
    }

    chartInstance = new Chart(ctx, {
      type: "line",
      data: {
        labels,
        datasets: spec.datasets,
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        animation: { duration: 250 },
        interaction: {
          mode: "index",
          intersect: false,
        },
        plugins: {
          legend: {
            display: spec.datasets.length > 1,
            position: "top",
            align: "end",
            labels: {
              color: t.tick,
              boxWidth: 10,
              font: { family: "'Inter', sans-serif", size: 12, weight: "600" },
            },
          },
          tooltip: {
            backgroundColor: t.tooltipBg,
            padding: 10,
            cornerRadius: 10,
            titleFont: { family: "'Inter', sans-serif", size: 12 },
            bodyFont: { family: "'Inter', sans-serif", size: 13, weight: "600" },
          },
        },
        scales: {
          x: {
            grid: { display: false },
            ticks: {
              color: t.tick,
              maxRotation: 0,
              autoSkip: true,
              maxTicksLimit: 7,
              font: { family: "'Inter', sans-serif", size: 11.5 },
            },
          },
          y: {
            grid: { color: t.grid },
            border: { display: false },
            ticks: {
              color: t.tick,
              maxTicksLimit: 5,
              font: { family: "'Inter', sans-serif", size: 11.5 },
              callback: (v) => `${Number(v).toFixed(currentMode === "pressure" ? 0 : 1)}${spec.unitSuffix}`,
            },
          },
        },
      },
    });
  }

  function setMode(mode) {
    currentMode = mode;
    renderOrUpdate(cachedSeries);
  }

  function pushLiveSample(sample, maxPoints = 24) {
    if (!sample) return;
    const ts = sample.recorded_at || sample.window_end;
    if (cachedSeries.length > 0) {
      const last = cachedSeries[cachedSeries.length - 1];
      if ((last.recorded_at || last.window_end) === ts) {
        cachedSeries[cachedSeries.length - 1] = sample;
      } else {
        cachedSeries.push(sample);
      }
    } else {
      cachedSeries.push(sample);
    }
    if (cachedSeries.length > maxPoints) {
      cachedSeries = cachedSeries.slice(-maxPoints);
    }
    renderOrUpdate(cachedSeries);
  }

  return {
    renderOrUpdate,
    setMode,
    pushLiveSample,
  };
})();
