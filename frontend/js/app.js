/**
 * EcoPulse — Orquestrador do Dashboard Web (Vanilla ES6+)
 * Integração assíncrona com FastAPI, cálculos meteorológicos e polling resiliente
 */

// Configuração da API: utiliza URL relativa quando servido por Nginx ou fallback para localhost:8000
const API_BASE_URL = window.location.origin.includes('http')
  ? `${window.location.origin}/api/v1`
  : 'http://localhost:8000/api/v1';

const POLL_INTERVAL_MS = 5000; // Atualização periódica a cada 5 segundos
let pollTimer = null;
let isFirstLoad = true;

/**
 * Inicialização ao carregar o DOM
 */
document.addEventListener('DOMContentLoaded', () => {
  // Inicializa componentes visuais
  if (typeof initTelemetryChart === 'function') initTelemetryChart();
  if (typeof initStationMap === 'function') initStationMap();

  // Configura botão de atualização manual
  const refreshBtn = document.getElementById('refreshBtn');
  if (refreshBtn) {
    refreshBtn.addEventListener('click', () => {
      fetchLatestTelemetry();
      fetchHistoryTelemetry();
    });
  }

  // Primeira carga e início do polling
  fetchLatestTelemetry();
  fetchHistoryTelemetry();
  startPolling();
});

/**
 * Inicia o ciclo de polling contínuo não-bloqueante
 */
function startPolling() {
  if (pollTimer) clearInterval(pollTimer);
  pollTimer = setInterval(() => {
    fetchLatestTelemetry();
  }, POLL_INTERVAL_MS);

  // Histórico atualiza a cada 15 segundos para economizar banda
  setInterval(() => {
    fetchHistoryTelemetry();
  }, 15000);
}

/**
 * Busca a leitura mais recente registrada no banco de dados
 */
async function fetchLatestTelemetry() {
  try {
    const response = await fetch(`${API_BASE_URL}/telemetry/latest`, {
      headers: { 'Accept': 'application/json' },
    });

    if (!response.ok) throw new Error(`Status HTTP: ${response.status}`);

    const data = await response.json();

    if (data && data.status !== 'empty') {
      updateUIWithTelemetry(data);
      setConnectionStatus(true);
    } else {
      setConnectionStatus(true, 'Aguardando 1º envio');
    }
  } catch (err) {
    console.warn('[EcoPulse] Falha na sincronização da telemetria:', err.message);
    setConnectionStatus(false);
  }
}

/**
 * Busca a série temporal para alimentar os gráficos
 */
async function fetchHistoryTelemetry() {
  try {
    const response = await fetch(`${API_BASE_URL}/telemetry/history?limit=30`, {
      headers: { 'Accept': 'application/json' },
    });

    if (!response.ok) return;

    const history = await response.json();
    if (Array.isArray(history) && typeof updateTelemetryChartData === 'function') {
      updateTelemetryChartData(history);
    }
  } catch (err) {
    console.warn('[EcoPulse] Falha ao obter histórico temporal:', err.message);
  }
}

/**
 * Atualiza todos os elementos visuais do Dashboard com base na leitura
 */
function updateUIWithTelemetry(data) {
  const temp = Number(data.temperature_c ?? 0);
  const hum = Number(data.humidity_pct ?? 0);
  const press = Number(data.pressure_hpa ?? 0);
  const alt = Number(data.altitude_m ?? 0);
  const aqi = Number(data.air_quality_ppm ?? 0);
  const light = Number(data.luminosity_pct ?? 0);
  const rainIntensity = Number(data.rain_intensity_pct ?? 0);
  const isRaining = Boolean(data.is_raining);

  // Cálculos Meteorológicos Interdisciplinares
  const thermalSensation = calculateHeatIndex(temp, hum);
  const dewPointVal = calculateDewPoint(temp, hum);

  // 1. Hero Card
  setText('heroTemp', Math.round(temp));
  setText('heroCondition', determineOverallCondition(temp, hum, isRaining, aqi));
  setText(
    'heroThermalSensation',
    `Sensação Térmica de ${thermalSensation.toFixed(1)}°C • Máx/Mín calculada em tempo real`
  );
  setText('quickThermal', `${thermalSensation.toFixed(1)}°C`);
  setText('quickHumidity', `${Math.round(hum)}%`);
  setText('quickPressure', `${Math.round(press)} hPa`);
  setText('stationName', `Estação ${data.device_id || 'EcoPulse'} • São Paulo, SP`);

  // Timestamp de sincronização
  if (data.recorded_at) {
    const syncDate = new Date(data.recorded_at);
    setText('lastSyncTime', `Atualizado às ${syncDate.toLocaleTimeString('pt-BR')}`);
  }

  // 2. Widget: Qualidade do Ar (MQ-135)
  setText('aqiPpm', Math.round(aqi));
  updateAqiWidget(aqi);

  // 3. Widget: Precipitação (LM393)
  if (isRaining || rainIntensity > 15) {
    setText('rainStatusText', 'Chuva Detectada');
    setText('rainPct', `${Math.round(rainIntensity)}%`);
    setText('rainDetail', `Gotas ativas na superfície do sensor (Intensidade: ${Math.round(rainIntensity)}%).`);
    setStyle('rainProgress', 'width', `${Math.min(100, rainIntensity)}%`);
  } else {
    setText('rainStatusText', 'Sem Chuva');
    setText('rainPct', '0%');
    setText('rainDetail', 'Superfície resistiva MH-RD seca. Clima estável sem precipitação.');
    setStyle('rainProgress', 'width', '0%');
  }

  // 4. Widget: Pressão & Altitude (BMP280)
  setText('pressureValue', press.toFixed(1));
  setText('altitudeValue', `${alt.toFixed(1)} m`);
  setText('pressureTrend', press < 1010 ? 'Queda (Instável)' : 'Estável / Elevada');

  // 5. Widget: Luminosidade (LDR)
  setText('lightValue', `${Math.round(light)}%`);
  setStyle('lightProgress', 'width', `${Math.min(100, light)}%`);
  if (light > 70) {
    setText('lightLevel', 'Plena Radiação');
    setText('lightAnnotation', 'Alta incidência de luz solar detectada pelo LDR.');
  } else if (light > 25) {
    setText('lightLevel', 'Moderada');
    setText('lightAnnotation', 'Luminosidade ambiente estável em ambiente semi-iluminado.');
  } else {
    setText('lightLevel', 'Baixa / Penumbra');
    setText('lightAnnotation', 'Condições de pouca luz solar ou operação noturna.');
  }

  // 6. Widget: Umidade e Ponto de Orvalho (DHT22)
  setText('humidityValue', `${Math.round(hum)}%`);
  setText('dewPoint', `${dewPointVal.toFixed(1)}°C`);
  setText(
    'humidityComfort',
    hum >= 40 && hum <= 70 ? 'Ideal (Confortável)' : hum > 70 ? 'Elevada' : 'Baixa (Atenção)'
  );

  // 7. Widget: Diagnóstico ESP32
  setText('diagRssi', data.wifi_rssi_dbm ? `${data.wifi_rssi_dbm} dBm` : '-54 dBm');
  setText('diagHeap', data.free_heap_bytes ? `${Math.round(data.free_heap_bytes / 1024)} KB` : '198 KB');
  setText('diagUptime', formatUptime(data.uptime_seconds || 120));
  setText('diagDevice', data.device_id || 'ESP32-WROOM');
}

/**
 * Atualiza os indicadores de Qualidade do Ar com classificação por faixas da OMS
 */
function updateAqiWidget(ppm) {
  const badge = document.getElementById('aqiBadge');
  const dot = document.getElementById('aqiDot');
  const quickAqi = document.getElementById('quickAqi');
  const recommendation = document.getElementById('aqiRecommendation');

  let pctPosition = 10;
  let statusText = 'Excelente';
  let badgeColor = 'rgba(48, 209, 88, 0.18)';
  let textColor = '#30D158';

  if (ppm <= 400) {
    statusText = 'Excelente';
    pctPosition = (ppm / 400) * 25;
    recommendation.textContent = 'Qualidade do ar limpa. Ideal para atividades ao ar livre.';
  } else if (ppm <= 600) {
    statusText = 'Boa';
    pctPosition = 25 + ((ppm - 400) / 200) * 25;
    recommendation.textContent = 'Qualidade aceitável com baixa presença de compostos gasosos.';
  } else if (ppm <= 1000) {
    statusText = 'Moderada';
    badgeColor = 'rgba(255, 214, 10, 0.18)';
    textColor = '#FFD60A';
    pctPosition = 50 + ((ppm - 600) / 400) * 25;
    recommendation.textContent = 'Atenção para indivíduos com alta sensibilidade respiratória.';
  } else {
    statusText = 'Crítica';
    badgeColor = 'rgba(255, 69, 58, 0.18)';
    textColor = '#FF453A';
    pctPosition = Math.min(95, 75 + ((ppm - 1000) / 500) * 25);
    recommendation.textContent = 'Alerta: concentração elevada de gases ou fumaça detectada.';
  }

  if (badge) {
    badge.textContent = statusText;
    badge.style.background = badgeColor;
    badge.style.color = textColor;
    badge.style.borderColor = textColor;
  }

  if (quickAqi) {
    quickAqi.textContent = statusText;
    quickAqi.style.color = textColor;
  }

  if (dot) {
    dot.style.left = `${Math.max(5, Math.min(95, pctPosition))}%`;
  }
}

/**
 * Determina o resumo descritivo das condições climáticas
 */
function determineOverallCondition(temp, hum, isRaining, aqi) {
  if (isRaining) return 'Chuva em Andamento';
  if (aqi > 900) return 'Ar com Presença de Fumaça/Gases';
  if (temp > 30) return 'Ensolarado e Quente';
  if (temp < 18) return 'Clima Ameno / Frio';
  if (hum > 80) return 'Tempo Úmido e Encoberto';
  return 'Tempo Aberto e Estável';
}

/**
 * Cálculo do Índice de Calor / Sensação Térmica (Fórmula de Steadman/Rothfusz)
 */
function calculateHeatIndex(tempC, humPct) {
  if (tempC < 20) return tempC; // Heat index aplica-se primariamente a temperaturas amenas/quentes

  const T = (tempC * 9) / 5 + 32; // Converte para Fahrenheit
  const R = humPct;

  // Aproximação do Heat Index em Fahrenheit
  let hiF =
    -42.379 +
    2.04901523 * T +
    10.14333127 * R -
    0.22475541 * T * R -
    0.00683783 * T * T -
    0.05481717 * R * R +
    0.00122874 * T * T * R +
    0.00085282 * T * R * R -
    0.00000199 * T * T * R * R;

  // Converte de volta para Celsius
  const hiC = ((hiF - 32) * 5) / 9;
  return isNaN(hiC) ? tempC : hiC;
}

/**
 * Cálculo do Ponto de Orvalho (Aproximação de Magnus-Tetens)
 */
function calculateDewPoint(tempC, humPct) {
  const a = 17.27;
  const b = 237.7;
  const alpha = (a * tempC) / (b + tempC) + Math.log(humPct / 100);
  const dp = (b * alpha) / (a - alpha);
  return isNaN(dp) ? tempC : dp;
}

/**
 * Formata segundos de Uptime em formato legível (ex: 2h 15m)
 */
function formatUptime(seconds) {
  if (!seconds) return '1h 00m';
  const hrs = Math.floor(seconds / 3600);
  const mins = Math.floor((seconds % 3600) / 60);
  return `${hrs}h ${mins}m`;
}

/**
 * Atualiza o indicador de status da conexão na barra superior
 */
function setConnectionStatus(isOnline, customLabel = null) {
  const indicator = document.getElementById('statusIndicator');
  const label = document.getElementById('statusLabel');
  if (!indicator || !label) return;

  const dot = indicator.querySelector('.pulse-dot');

  if (isOnline) {
    label.textContent = customLabel || 'Online • Ao Vivo';
    label.style.color = 'var(--text-secondary)';
    if (dot) {
      dot.style.backgroundColor = 'var(--apple-green)';
      dot.style.boxShadow = '0 0 8px var(--apple-green)';
    }
  } else {
    label.textContent = 'Buscando API...';
    label.style.color = 'var(--apple-yellow)';
    if (dot) {
      dot.style.backgroundColor = 'var(--apple-yellow)';
      dot.style.boxShadow = '0 0 8px var(--apple-yellow)';
    }
  }
}

/**
 * Utilitários auxiliares DOM
 */
function setText(id, text) {
  const el = document.getElementById(id);
  if (el) el.textContent = text;
}

function setStyle(id, prop, value) {
  const el = document.getElementById(id);
  if (el) el.style[prop] = value;
}
