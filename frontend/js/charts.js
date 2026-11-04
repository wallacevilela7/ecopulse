/**
 * EcoPulse — Módulo de Visualização Gráfica (Chart.js no padrão Apple)
 * Renderização de séries temporais com interpolação cúbica suave e gradientes translúcidos
 */

let chartInstance = null;
let currentMetric = 'temperature';
let cachedHistoryData = [];

// Definições de estilo e paletas Apple para cada métrica
const METRIC_CONFIGS = {
  temperature: {
    label: 'Temperatura (°C)',
    color: '#0A84FF',
    gradientStart: 'rgba(10, 132, 255, 0.45)',
    gradientEnd: 'rgba(10, 132, 255, 0.0)',
    unit: '°C',
    field: 'temperature_c',
    minPadding: 2,
    maxPadding: 2,
  },
  humidity: {
    label: 'Umidade Relativa (%)',
    color: '#64D2FF',
    gradientStart: 'rgba(100, 210, 255, 0.45)',
    gradientEnd: 'rgba(100, 210, 255, 0.0)',
    unit: '%',
    field: 'humidity_pct',
    min: 0,
    max: 100,
  },
  pressure: {
    label: 'Pressão Barométrica (hPa)',
    color: '#BF5AF2',
    gradientStart: 'rgba(191, 90, 242, 0.45)',
    gradientEnd: 'rgba(191, 90, 242, 0.0)',
    unit: ' hPa',
    field: 'pressure_hpa',
    minPadding: 4,
    maxPadding: 4,
  },
  air_quality: {
    label: 'Qualidade do Ar (PPM)',
    color: '#30D158',
    gradientStart: 'rgba(48, 209, 88, 0.45)',
    gradientEnd: 'rgba(48, 209, 88, 0.0)',
    unit: ' PPM',
    field: 'air_quality_ppm',
    min: 0,
  },
  light: {
    label: 'Luminosidade Ambiente (%)',
    color: '#FFD60A',
    gradientStart: 'rgba(255, 214, 10, 0.45)',
    gradientEnd: 'rgba(255, 214, 10, 0.0)',
    unit: '%',
    field: 'luminosity_pct',
    min: 0,
    max: 100,
  },
};

/**
 * Inicializa a instância do Chart.js com configuração personalizada
 */
function initTelemetryChart() {
  const canvas = document.getElementById('telemetryChart');
  if (!canvas) return;

  const ctx = canvas.getContext('2d');

  chartInstance = new Chart(ctx, {
    type: 'line',
    data: {
      labels: [],
      datasets: [
        {
          label: METRIC_CONFIGS[currentMetric].label,
          data: [],
          borderColor: METRIC_CONFIGS[currentMetric].color,
          borderWidth: 2.5,
          pointRadius: 0,
          pointHoverRadius: 6,
          pointHoverBackgroundColor: '#ffffff',
          pointHoverBorderColor: METRIC_CONFIGS[currentMetric].color,
          pointHoverBorderWidth: 3,
          tension: 0.4, // Interpolação suave e orgânica (estilo iOS Health)
          fill: true,
          backgroundColor: createGradient(ctx, METRIC_CONFIGS[currentMetric]),
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: {
        mode: 'index',
        intersect: false,
      },
      plugins: {
        legend: {
          display: false,
        },
        tooltip: {
          enabled: true,
          backgroundColor: 'rgba(18, 26, 44, 0.88)',
          titleColor: '#ffffff',
          bodyColor: '#64D2FF',
          borderColor: 'rgba(255, 255, 255, 0.15)',
          borderWidth: 1,
          padding: 12,
          cornerRadius: 12,
          displayColors: false,
          callbacks: {
            label: function (context) {
              const cfg = METRIC_CONFIGS[currentMetric];
              return `${cfg.label}: ${context.parsed.y}${cfg.unit}`;
            },
          },
        },
      },
      scales: {
        x: {
          grid: {
            display: false,
            drawBorder: false,
          },
          ticks: {
            color: 'rgba(255, 255, 255, 0.4)',
            font: {
              family: '-apple-system, BlinkMacSystemFont, "SF Pro Text", sans-serif',
              size: 11,
            },
            maxRotation: 0,
            autoSkip: true,
            maxTicksLimit: 7,
          },
        },
        y: {
          grid: {
            color: 'rgba(255, 255, 255, 0.05)',
            drawBorder: false,
          },
          ticks: {
            color: 'rgba(255, 255, 255, 0.4)',
            font: {
              family: '-apple-system, BlinkMacSystemFont, "SF Pro Text", sans-serif',
              size: 11,
            },
            padding: 8,
          },
        },
      },
    },
  });

  setupSegmentedControls();
}

/**
 * Cria o degradê translúcido vertical
 */
function createGradient(ctx, config) {
  const gradient = ctx.createLinearGradient(0, 0, 0, 280);
  gradient.addColorStop(0, config.gradientStart);
  gradient.addColorStop(1, config.gradientEnd);
  return gradient;
}

/**
 * Atualiza o dataset do gráfico a partir dos registros recebidos da API
 */
function updateTelemetryChartData(records) {
  if (!chartInstance || !records || records.length === 0) return;

  cachedHistoryData = records;

  const cfg = METRIC_CONFIGS[currentMetric];
  const labels = records.map((r) => {
    const d = new Date(r.recorded_at);
    return d.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
  });

  const values = records.map((r) => {
    const s = r.sensors || r;
    return s[cfg.field] !== undefined ? s[cfg.field] : null;
  });

  chartInstance.data.labels = labels;
  chartInstance.data.datasets[0].label = cfg.label;
  chartInstance.data.datasets[0].data = values;
  chartInstance.data.datasets[0].borderColor = cfg.color;
  chartInstance.data.datasets[0].pointHoverBorderColor = cfg.color;

  const ctx = chartInstance.ctx;
  chartInstance.data.datasets[0].backgroundColor = createGradient(ctx, cfg);

  // Ajustes de limites de escala
  if (cfg.min !== undefined) chartInstance.options.scales.y.min = cfg.min;
  else delete chartInstance.options.scales.y.min;

  if (cfg.max !== undefined) chartInstance.options.scales.y.max = cfg.max;
  else delete chartInstance.options.scales.y.max;

  chartInstance.update('none'); // Update rápido sem travamentos

  // Atualiza contador de pontos no rodapé
  const counterEl = document.getElementById('chartPointsCount');
  if (counterEl) {
    counterEl.textContent = `${records.length} medições registradas na série temporal`;
  }
}

/**
 * Adiciona uma medição pontual recebida via Streaming SSE em tempo real (< 10ms)
 */
function appendLiveChartPoint(record) {
  if (!chartInstance || !record) return;

  const cfg = METRIC_CONFIGS[currentMetric];
  const s = record.sensors || record;
  const val = s[cfg.field] !== undefined ? s[cfg.field] : null;
  if (val === null) return;

  const d = new Date(record.recorded_at || Date.now());
  const label = d.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit', second: '2-digit' });

  // Adiciona ao cache
  cachedHistoryData.push(record);
  if (cachedHistoryData.length > 40) {
    cachedHistoryData.shift();
  }

  // Adiciona ao dataset visual
  chartInstance.data.labels.push(label);
  chartInstance.data.datasets[0].data.push(val);

  if (chartInstance.data.labels.length > 40) {
    chartInstance.data.labels.shift();
    chartInstance.data.datasets[0].data.shift();
  }

  chartInstance.update(); // Transição visual fluida

  const counterEl = document.getElementById('chartPointsCount');
  if (counterEl) {
    counterEl.textContent = `${chartInstance.data.labels.length} medições ativas • Streaming Contínuo`;
  }
}

/**
 * Configura os botões da barra segmentada Apple
 */
function setupSegmentedControls() {
  const buttons = document.querySelectorAll('.segment-btn');
  buttons.forEach((btn) => {
    btn.addEventListener('click', () => {
      buttons.forEach((b) => {
        b.classList.remove('active');
        b.setAttribute('aria-selected', 'false');
      });
      btn.classList.add('active');
      btn.setAttribute('aria-selected', 'true');

      const metric = btn.getAttribute('data-metric');
      if (METRIC_CONFIGS[metric]) {
        currentMetric = metric;
        if (cachedHistoryData.length > 0) {
          updateTelemetryChartData(cachedHistoryData);
        }
      }
    });
  });
}

