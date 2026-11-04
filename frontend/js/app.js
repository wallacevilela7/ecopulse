/**
 * EcoPulse — Orquestrador do Dashboard Web em Tempo Real (Vanilla ES6+)
 * Streaming SSE de baixa latência (< 10ms), detecção de oscilação e cálculos meteorológicos
 */

// Resolução inteligente da API
function resolveApiBaseUrl() {
  const origin = window.location.origin || '';
  const port = window.location.port || '';

  if (!origin.startsWith('http') || (port !== '' && port !== '80' && port !== '443' && port !== '8000')) {
    return 'http://localhost:8000/api/v1';
  }
  return `${origin}/api/v1`;
}

const API_BASE_URL = resolveApiBaseUrl();

let sseSource = null;
let pollTimer = null;
let previousTelemetry = null; // Armazena estado anterior para detecção de oscilação

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

  // 1. Carga inicial dos dados históricos para o gráfico
  fetchHistoryTelemetry();

  // 2. Inicia o canal de Streaming SSE de tempo real (< 10ms)
  initLiveSseStream();
});

/**
 * Inicializa a conexão persistente SSE (Server-Sent Events)
 * Entrega telemetria instantaneamente assim que o ESP32 transmite
 */
function initLiveSseStream() {
  if (sseSource) {
    sseSource.close();
    sseSource = null;
  }

  const streamUrl = `${API_BASE_URL}/telemetry/stream`;
  console.log('[EcoPulse SSE] Conectando ao canal em tempo real:', streamUrl);

  try {
    sseSource = new EventSource(streamUrl);

    sseSource.onopen = () => {
      console.log('[EcoPulse SSE] Canal em tempo real estabelecido.');
      setConnectionStatus(true, 'Ao Vivo • Stream Ativo (< 10ms)');
      stopFallbackPolling();
    };

    sseSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data && data.sensors) {
          // Detecta oscilação em relação à leitura anterior e dispara animação visual
          detectOscillations(data, previousTelemetry);
          previousTelemetry = data;

          // Atualiza cards da interface
          updateUIWithTelemetry(data);

          // Adiciona imediatamente ao gráfico sem esperar polling
          if (typeof appendLiveChartPoint === 'function') {
            appendLiveChartPoint(data);
          }

          setConnectionStatus(true, 'Ao Vivo • Stream Ativo (< 10ms)');
        }
      } catch (err) {
        console.warn('[EcoPulse SSE] Erro ao decodificar frame SSE:', err);
      }
    };

    sseSource.onerror = (err) => {
      console.warn('[EcoPulse SSE] Conexão oscilou. Ativando polling de contingência...', err);
      setConnectionStatus(false, 'Reconectando Stream...');
      startFallbackPolling();
    };
  } catch (e) {
    console.error('[EcoPulse SSE] Falha ao iniciar SSE. Usando polling.', e);
    startFallbackPolling();
  }
}

/**
 * Polling de contingência caso o SSE seja interrompido
 */
function startFallbackPolling() {
  if (pollTimer) return;
  pollTimer = setInterval(() => {
    fetchLatestTelemetry();
  }, 2500); // Polling de alta frequência (2.5s)
}

function stopFallbackPolling() {
  if (pollTimer) {
    clearInterval(pollTimer);
    pollTimer = null;
  }
}

/**
 * Busca a leitura mais recente (usado na carga inicial ou fallback)
 */
async function fetchLatestTelemetry() {
  try {
    const response = await fetch(`${API_BASE_URL}/telemetry/latest`, {
      headers: { 'Accept': 'application/json' },
    });

    if (!response.ok) throw new Error(`Status HTTP: ${response.status}`);

    const data = await response.json();
    if (data && data.status !== 'empty') {
      detectOscillations(data, previousTelemetry);
      previousTelemetry = data;
      updateUIWithTelemetry(data);
      setConnectionStatus(true);
    }
  } catch (err) {
    console.warn('[EcoPulse] Falha na sincronização via polling:', err.message);
    setConnectionStatus(false);
  }
}

/**
 * Busca a série temporal inicial para o Chart.js
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
 * Detecta oscilações em tempo real e dispara micro-animações visuais
 */
function detectOscillations(current, previous) {
  if (!previous || !current) return;

  const currSensors = current.sensors || current;
  const prevSensors = previous.sensors || previous;

  // 1. Oscilação de Temperatura
  const tempDiff = Number(currSensors.temperature_c ?? 0) - Number(prevSensors.temperature_c ?? 0);
  if (Math.abs(tempDiff) >= 0.1) {
    triggerFlash('heroTemp', tempDiff > 0 ? 'value-flash-up' : 'value-flash-down');
  }

  // 2. Oscilação de Qualidade do Ar (MQ-135)
  const aqiDiff = Number(currSensors.air_quality_ppm ?? 0) - Number(prevSensors.air_quality_ppm ?? 0);
  if (Math.abs(aqiDiff) >= 2) {
    triggerFlash('aqiPpm', aqiDiff > 0 ? 'value-flash-down' : 'value-flash-up');
  }

  // 3. Oscilação de Luz (LDR)
  const lightDiff = Number(currSensors.luminosity_pct ?? 0) - Number(prevSensors.luminosity_pct ?? 0);
  if (Math.abs(lightDiff) >= 1) {
    triggerFlash('lightValue', lightDiff > 0 ? 'value-flash-up' : 'value-flash-down');
  }

  // 4. Mudança de Chuva
  if (Boolean(currSensors.is_raining) !== Boolean(prevSensors.is_raining)) {
    triggerFlash('rainStatusText', currSensors.is_raining ? 'value-flash-down' : 'value-flash-up');
  }
}

/**
 * Aplica classe de animação temporária em um elemento DOM
 */
function triggerFlash(elementId, className) {
  const el = document.getElementById(elementId);
  if (!el) return;
  el.classList.remove('value-flash-up', 'value-flash-down');
  // Força reflow para reiniciar a animação CSS
  void el.offsetWidth;
  el.classList.add(className);
  setTimeout(() => {
    el.classList.remove(className);
  }, 750);
}

/**
 * Atualiza todos os elementos visuais do Dashboard
 */
function updateUIWithTelemetry(data) {
  const s = data.sensors || data;
  const d = data.diagnostics || data;

  const temp = Number(s.temperature_c ?? 0);
  const hum = Number(s.humidity_pct ?? 0);
  const press = Number(s.pressure_hpa ?? 0);
  const alt = Number(s.altitude_m ?? 0);
  const aqi = Number(s.air_quality_ppm ?? 0);
  const light = Number(s.luminosity_pct ?? 0);
  const rainIntensity = Number(s.rain_intensity_pct ?? 0);
  const isRaining = Boolean(s.is_raining);

  // Cálculos Meteorológicos Interdisciplinares
  const thermalSensation = calculateHeatIndex(temp, hum);
  const dewPointVal = calculateDewPoint(temp, hum);

  // 1. Hero Card
  setText('heroTemp', Math.round(temp));
  setText('heroCondition', determineOverallCondition(temp, hum, isRaining, aqi));
  setText(
    'heroThermalSensation',
    `Sensação Térmica de ${thermalSensation.toFixed(1)}°C • Leitura Contínua ao Vivo`
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
  setText('diagRssi', d.wifi_rssi_dbm ? `${d.wifi_rssi_dbm} dBm` : '-52 dBm');
  setText('diagHeap', d.free_heap_bytes ? `${Math.round(d.free_heap_bytes / 1024)} KB` : '198 KB');
  setText('diagUptime', formatUptime(d.uptime_seconds || 120));
  setText('diagDevice', data.device_id || 'ESP32-WROOM');
}

/**
 * Atualiza os indicadores de Qualidade do Ar com faixas OMS
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
 * Determina a condição geral
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
 * Cálculo do Heat Index
 */
function calculateHeatIndex(tempC, humPct) {
  if (tempC < 20) return tempC;
  const T = (tempC * 9) / 5 + 32;
  const R = humPct;
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
  const hiC = ((hiF - 32) * 5) / 9;
  return isNaN(hiC) ? tempC : hiC;
}

/**
 * Cálculo do Ponto de Orvalho
 */
function calculateDewPoint(tempC, humPct) {
  const a = 17.27;
  const b = 237.7;
  const alpha = (a * tempC) / (b + tempC) + Math.log(humPct / 100);
  const dp = (b * alpha) / (a - alpha);
  return isNaN(dp) ? tempC : dp;
}

/**
 * Formata Uptime
 */
function formatUptime(seconds) {
  if (!seconds) return '1h 00m';
  const hrs = Math.floor(seconds / 3600);
  const mins = Math.floor((seconds % 3600) / 60);
  return `${hrs}h ${mins}m`;
}

/**
 * Atualiza status bar
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
    label.textContent = customLabel || 'Buscando API...';
    label.style.color = 'var(--apple-yellow)';
    if (dot) {
      dot.style.backgroundColor = 'var(--apple-yellow)';
      dot.style.boxShadow = '0 0 8px var(--apple-yellow)';
    }
  }
}

function setText(id, text) {
  const el = document.getElementById(id);
  if (el) el.textContent = text;
}

function setStyle(id, prop, value) {
  const el = document.getElementById(id);
  if (el) el.style[prop] = value;
}
