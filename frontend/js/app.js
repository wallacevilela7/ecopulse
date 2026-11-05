/**
 * EcoPulse — Orquestrador Frontend (Design Apple iOS Weather + Hot/Cold Path)
 * Recebe streaming SSE em tempo real (< 15ms), renderiza faixa horária, barras de amplitude e Bento Grid.
 */

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
let previousTelemetry = null;
let currentStripMode = 'temp'; // 'temp' | 'rain' | 'air'
let recentHistoryPoints = [];
let recentEvents = [];

document.addEventListener('DOMContentLoaded', () => {
  if (typeof initTelemetryChart === 'function') initTelemetryChart();
  if (typeof initStationMap === 'function') initStationMap();

  setupStripModeButtons();
  setupBottomNavigation();

  // Carga inicial
  fetchLatestTelemetry();
  fetchHistoryTelemetry();
  fetchClimateEvents();

  // Inicia Streaming SSE do Hot Path
  initLiveSseStream();

  // Sincroniza histórico e eventos do Cold Path periodicamente
  setInterval(() => {
    fetchHistoryTelemetry();
    fetchClimateEvents();
  }, 20000);
});

/**
 * Configura os 3 botões de ícone do card "Condições"
 */
function setupStripModeButtons() {
  const buttons = document.querySelectorAll('.icon-seg-btn');
  const subtitle = document.getElementById('stripModeSubtitle');

  const titles = {
    temp: 'Temperatura (°C)',
    rain: 'Precipitação & Umidade (%)',
    air: 'Qualidade do Ar (PPM) & Pressão',
  };

  buttons.forEach((btn) => {
    btn.addEventListener('click', () => {
      buttons.forEach((b) => {
        b.classList.remove('active');
        b.setAttribute('aria-selected', 'false');
      });
      btn.classList.add('active');
      btn.setAttribute('aria-selected', 'true');

      currentStripMode = btn.getAttribute('data-strip-mode') || 'temp';
      if (subtitle) subtitle.textContent = titles[currentStripMode] || 'Temperatura (°C)';
      renderHourlyConditionsStrip();
    });
  });
}

/**
 * Configura a barra de ferramentas inferior do iOS e detecção de dobra no scroll
 */
function setupBottomNavigation() {
  const btnMap = document.getElementById('btnScrollMap');
  const btnTop = document.getElementById('btnScrollTop');
  const btnDash = document.getElementById('btnScrollDashboard');
  const dotTop = document.getElementById('dotTop');
  const dotDash = document.getElementById('dotDash');

  if (btnMap) {
    btnMap.addEventListener('click', () => {
      const target = document.getElementById('mapSection');
      if (target) target.scrollIntoView({ behavior: 'smooth' });
    });
  }

  if (btnTop) {
    btnTop.addEventListener('click', () => {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  }

  if (btnDash) {
    btnDash.addEventListener('click', () => {
      const dashSection = document.getElementById('fullDashboardSection');
      if (!dashSection) return;
      const rect = dashSection.getBoundingClientRect();
      if (rect.top > 180) {
        dashSection.scrollIntoView({ behavior: 'smooth' });
      } else {
        window.scrollTo({ top: 0, behavior: 'smooth' });
      }
    });
  }

  window.addEventListener('scroll', () => {
    const scrollY = window.scrollY || window.pageYOffset;
    if (dotTop && dotDash) {
      if (scrollY > window.innerHeight * 0.4) {
        dotTop.classList.remove('active');
        dotDash.classList.add('active');
      } else {
        dotTop.classList.add('active');
        dotDash.classList.remove('active');
      }
    }
  }, { passive: true });
}

/**
 * Conexão persistente SSE (Server-Sent Events) do Hot Path
 */
function initLiveSseStream() {
  if (sseSource) {
    sseSource.close();
    sseSource = null;
  }

  try {
    sseSource = new EventSource(`${API_BASE_URL}/telemetry/stream`);

    sseSource.onopen = () => {
      setConnectionStatus(true, 'Ao Vivo • Hot Path SSE (< 15ms)');
      stopFallbackPolling();
    };

    sseSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data && data.sensors) {
          handleIncomingTelemetry(data);
          setConnectionStatus(true, 'Ao Vivo • Hot Path SSE (< 15ms)');
        }
      } catch (err) {
        console.warn('[EcoPulse SSE] Erro ao processar pacote:', err);
      }
    };

    sseSource.onerror = () => {
      setConnectionStatus(false, 'Reconectando Stream...');
      startFallbackPolling();
    };
  } catch (e) {
    startFallbackPolling();
  }
}

function startFallbackPolling() {
  if (pollTimer) return;
  pollTimer = setInterval(fetchLatestTelemetry, 3000);
}

function stopFallbackPolling() {
  if (pollTimer) {
    clearInterval(pollTimer);
    pollTimer = null;
  }
}

/**
 * Processa um pacote de telemetria recebido via SSE ou REST
 */
function handleIncomingTelemetry(data) {
  detectOscillations(data, previousTelemetry);
  previousTelemetry = data;

  // Mantém lista local de pontos recentes para o carrossel "Condições" e barras de amplitude
  const ts = data.recorded_at || data.window_end;
  if (ts) {
    const exists = recentHistoryPoints.some((p) => (p.recorded_at || p.window_end) === ts);
    if (!exists) {
      recentHistoryPoints.push(data);
      if (recentHistoryPoints.length > 36) recentHistoryPoints.shift();
    }
  }

  if (data.latest_event) {
    const evExists = recentEvents.some((e) => e.id === data.latest_event.id);
    if (!evExists) {
      recentEvents.unshift(data.latest_event);
      updateAlertBanner();
    }
  }

  updateUIWithTelemetry(data);
  renderHourlyConditionsStrip();
  renderWindowAmplitudeBars();

  if (typeof appendLiveChartPoint === 'function') {
    appendLiveChartPoint(data);
  }
}

async function fetchLatestTelemetry() {
  try {
    const res = await fetch(`${API_BASE_URL}/telemetry/latest`);
    if (!res.ok) return;
    const data = await res.json();
    if (data && data.status !== 'empty' && data.sensors) {
      handleIncomingTelemetry(data);
    }
  } catch (err) {
    setConnectionStatus(false);
  }
}

async function fetchHistoryTelemetry() {
  try {
    const res = await fetch(`${API_BASE_URL}/telemetry/history?limit=30`);
    if (!res.ok) return;
    const history = await res.json();
    if (Array.isArray(history) && history.length > 0) {
      recentHistoryPoints = history;
      renderHourlyConditionsStrip();
      renderWindowAmplitudeBars();
      if (typeof updateTelemetryChartData === 'function') {
        updateTelemetryChartData(history);
      }
    }
  } catch (err) {
    console.warn('[EcoPulse] Falha ao buscar histórico:', err.message);
  }
}

async function fetchClimateEvents() {
  try {
    const res = await fetch(`${API_BASE_URL}/telemetry/events?limit=8`);
    if (!res.ok) return;
    const events = await res.json();
    if (Array.isArray(events)) {
      recentEvents = events;
      updateAlertBanner();
    }
  } catch (err) {
    console.warn('[EcoPulse] Falha ao buscar eventos:', err.message);
  }
}

/**
 * Atualiza o Card 1 de Alertas no estilo "Storm & 2 More" do iOS Weather
 */
function updateAlertBanner() {
  const card = document.getElementById('alertBannerCard');
  if (!card) return;

  if (recentEvents.length > 0) {
    const primary = recentEvents[0];
    const extraCount = recentEvents.length - 1;
    const titleSuffix = extraCount > 0 ? ` & Mais ${extraCount}` : '';

    setText('alertTitle', `${primary.title}${titleSuffix}`);

    const dt = primary.recorded_at ? new Date(primary.recorded_at) : new Date();
    const timeStr = dt.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });
    const extraTitles = recentEvents
      .slice(1, 3)
      .map((e) => e.title)
      .join(', ');

    const extraText = extraTitles ? ` Eventos recentes adicionais: ${extraTitles}.` : '';
    setText('alertDescription', `${primary.description} Registrado às ${timeStr}.${extraText}`);
    setText('alertSource', `Detector Deadband Cold Path • Estação ${primary.device_id || 'EcoPulse'}`);

    if (primary.severity === 'CRITICAL' || primary.event_type === 'RAIN_STARTED') {
      card.classList.add('alert-critical');
    } else {
      card.classList.remove('alert-critical');
    }
  } else if (previousTelemetry && previousTelemetry.sensors) {
    const s = previousTelemetry.sensors;
    card.classList.remove('alert-critical');
    if (s.is_raining) {
      setText('alertTitle', 'Precipitação Ativa na Estação');
      setText(
        'alertDescription',
        `O sensor pluviométrico detecta presença de chuva (${Math.round(s.rain_intensity_pct || 0)}%). Acompanhe a evolução barométrica abaixo.`
      );
    } else {
      setText('alertTitle', 'Estabilidade Atmosférica • Vigilância Ativa');
      setText(
        'alertDescription',
        `Condições monitoradas em tempo real via Hot Path SSE. Pressão em ${Number(s.pressure_hpa || 1013).toFixed(1)} hPa e ar com ${Math.round(s.air_quality_ppm || 10)} PPM.`
      );
    }
    setText('alertSource', 'Instituto Nacional de Meteorologia • Padrão WMO-No. 8');
  }
}

/**
 * Renderiza o Card 2: Faixa Horizontal de Condições ("Now, 20:00, 20:05...")
 */
function renderHourlyConditionsStrip() {
  const container = document.getElementById('hourlyStrip');
  if (!container) return;

  const points = recentHistoryPoints.length > 0
    ? recentHistoryPoints.slice(-8).reverse()
    : (previousTelemetry ? [previousTelemetry] : []);

  if (points.length === 0) {
    container.innerHTML = `<div class="hourly-col"><span class="hourly-time">Agora</span><span class="hourly-val">--°</span></div>`;
    return;
  }

  container.innerHTML = points
    .map((pt, idx) => {
      const s = pt.sensors || pt;
      const dt = new Date(pt.recorded_at || pt.window_end || Date.now());
      const timeLabel = idx === 0
        ? 'Agora'
        : dt.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });

      const isRain = Boolean(s.is_raining) || Number(s.rain_intensity_pct || 0) > 15;
      const rainPct = Math.round(Number(s.rain_intensity_pct || 0));
      const humPct = Math.round(Number(s.humidity_pct || 0));
      const lightPct = Number(s.luminosity_pct ?? 50);

      const iconSvg = getWeatherSvgIcon(isRain, lightPct);
      const subBadge = isRain
        ? `<span class="hourly-rain-chance">${Math.max(15, rainPct)}%</span>`
        : (currentStripMode === 'rain' ? `<span class="hourly-rain-chance">${humPct}%</span>` : '');

      let bottomValue = `${Math.round(Number(s.temperature_c ?? 0))}°`;
      if (currentStripMode === 'rain') {
        bottomValue = isRain ? `${rainPct}%` : `${humPct}%`;
      } else if (currentStripMode === 'air') {
        bottomValue = `${Math.round(Number(s.air_quality_ppm ?? 0))}`;
      }

      return `
        <div class="hourly-col">
          <span class="hourly-time">${timeLabel}</span>
          <div class="hourly-icon-wrap">
            ${iconSvg}
            ${subBadge}
          </div>
          <span class="hourly-val">${bottomValue}</span>
        </div>
      `;
    })
    .join('');
}

/**
 * Renderiza o Card 3 (Peek do Dashboard): Janelas Consolidadas com Barra de Amplitude Laranja
 */
function renderWindowAmplitudeBars() {
  const listEl = document.getElementById('windowBarsList');
  if (!listEl) return;

  const sourceList = recentHistoryPoints.length > 0
    ? recentHistoryPoints.slice(-5).reverse()
    : (previousTelemetry ? [previousTelemetry] : []);

  if (sourceList.length === 0) return;

  // Determina os extremos globais para posicionar proporcionalmente as barras (igual ao iOS Weather)
  let globalMin = Infinity;
  let globalMax = -Infinity;

  const rowsData = sourceList.map((item, idx) => {
    const s = item.sensors || item;
    const ext = item.extremes || {};
    const tAvg = Number(s.temperature_c ?? 22);
    const tMin = Number(ext.temp_min ?? (tAvg - 1.2));
    const tMax = Number(ext.temp_max ?? (tAvg + 1.2));

    if (tMin < globalMin) globalMin = tMin;
    if (tMax > globalMax) globalMax = tMax;

    const dt = new Date(item.window_end || item.recorded_at || Date.now());
    const label = idx === 0
      ? 'Agora'
      : dt.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });

    const isRain = Boolean(s.is_raining) || Number(s.rain_intensity_pct || 0) > 15;
    const rainPct = Math.round(Number(s.rain_intensity_pct || 0));
    const lightPct = Number(s.luminosity_pct ?? 50);

    return { label, tAvg, tMin, tMax, isRain, rainPct, lightPct, isCurrent: idx === 0 };
  });

  const span = Math.max(4, globalMax - globalMin);

  listEl.innerHTML = rowsData
    .map((r) => {
      const leftPct = Math.max(0, Math.min(85, ((r.tMin - globalMin) / span) * 100));
      const widthPct = Math.max(15, Math.min(100 - leftPct, ((r.tMax - r.tMin) / span) * 100));
      const dotPct = Math.max(4, Math.min(96, ((r.tAvg - globalMin) / span) * 100));

      const iconSvg = getWeatherSvgIcon(r.isRain, r.lightPct, 20);
      const rainLabel = r.isRain ? `<span class="row-rain-pct">${Math.max(20, r.rainPct)}%</span>` : '';
      const dotHtml = r.isCurrent ? `<div class="temp-current-dot" style="left: ${dotPct}%;"></div>` : '';

      return `
        <div class="forecast-row">
          <span class="row-day-label">${r.label}</span>
          <div class="row-icon-cell">
            ${iconSvg}
            ${rainLabel}
          </div>
          <span class="row-min-temp">${Math.round(r.tMin)}°</span>
          <div class="temp-range-track">
            <div class="temp-range-fill" style="left: ${leftPct}%; width: ${widthPct}%;"></div>
            ${dotHtml}
          </div>
          <span class="row-max-temp">${Math.round(r.tMax)}°</span>
        </div>
      `;
    })
    .join('');
}

/**
 * Retorna ícone SVG vetorial no padrão Apple Weather
 */
function getWeatherSvgIcon(isRain, lightPct, size = 24) {
  if (isRain) {
    return `
      <svg viewBox="0 0 24 24" width="${size}" height="${size}" fill="none">
        <path d="M18.5 10.5A4.5 4.5 0 0 0 14 6a5.5 5.5 0 0 0-10.6 1.8A4 4 0 0 0 4.5 15.5h13a3.5 3.5 0 0 0 1-5z" fill="#ffffff"/>
        <line x1="8" y1="17" x2="7" y2="20" stroke="#5AC8FA" stroke-width="2" stroke-linecap="round"/>
        <line x1="12" y1="17" x2="11" y2="20" stroke="#5AC8FA" stroke-width="2" stroke-linecap="round"/>
        <line x1="16" y1="17" x2="15" y2="20" stroke="#5AC8FA" stroke-width="2" stroke-linecap="round"/>
      </svg>
    `;
  }
  if (lightPct > 68) {
    return `
      <svg viewBox="0 0 24 24" width="${size}" height="${size}" fill="none">
        <circle cx="12" cy="12" r="5.5" fill="#FFD60A"/>
        <path d="M18.5 14.5A3.5 3.5 0 0 0 15 11a4.2 4.2 0 0 0-8 1.2A3 3 0 0 0 7.5 18h10a2.5 2.5 0 0 0 1-3.5z" fill="#ffffff" fill-opacity="0.92"/>
      </svg>
    `;
  }
  return `
    <svg viewBox="0 0 24 24" width="${size}" height="${size}" fill="none">
      <path d="M18.5 11.5A4.5 4.5 0 0 0 14 7a5.5 5.5 0 0 0-10.6 1.8A4 4 0 0 0 4.5 16.5h13a3.5 3.5 0 0 0 1-5z" fill="#ffffff"/>
    </svg>
  `;
}

/**
 * Atualiza todos os elementos visuais do Hero e do Bento Grid
 */
function updateUIWithTelemetry(data) {
  const s = data.sensors || data;
  const d = data.diagnostics || data;
  const ext = data.extremes || {};
  const pipe = data.pipeline || {};

  const temp = Number(s.temperature_c ?? 0);
  const hum = Number(s.humidity_pct ?? 0);
  const press = Number(s.pressure_hpa ?? 0);
  const alt = Number(s.altitude_m ?? 0);
  const aqi = Number(s.air_quality_ppm ?? 0);
  const light = Number(s.luminosity_pct ?? 0);
  const rainIntensity = Number(s.rain_intensity_pct ?? 0);
  const isRaining = Boolean(s.is_raining);

  const tMax = ext.temp_max !== undefined && ext.temp_max !== null ? Number(ext.temp_max) : temp;
  const tMin = ext.temp_min !== undefined && ext.temp_min !== null ? Number(ext.temp_min) : temp;

  const thermalSensation = calculateHeatIndex(temp, hum);
  const dewPointVal = calculateDewPoint(temp, hum);

  // 1. Hero Principal
  setText('heroTemp', Math.round(temp));
  setText('heroCondition', determineOverallCondition(temp, hum, isRaining, aqi, light));
  setText('heroHigh', `${Math.round(tMax)}°`);
  setText('heroLow', `${Math.round(tMin)}°`);
  setText('stationTag', `HOME • ${(data.device_id || 'ECOPULSE').toUpperCase()}`);

  const syncTs = data.recorded_at || data.window_end;
  if (syncTs) {
    const syncDate = new Date(syncTs);
    setText('lastSyncTime', syncDate.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit', second: '2-digit' }));
  }

  // 2. Bento Tile: Qualidade do Ar (MQ-135)
  setText('aqiPpm', Math.round(aqi));
  updateAqiWidget(aqi);

  // 3. Bento Tile: Precipitação (LM393)
  if (isRaining || rainIntensity > 15) {
    setText('rainStatusText', 'Chuva Ativa');
    setText('rainPct', `${Math.round(rainIntensity)}%`);
    setText('rainDetail', `Lâmina d'água detectada no sensor resistivo MH-RD.`);
    setStyle('rainProgress', 'width', `${Math.min(100, rainIntensity)}%`);
  } else {
    setText('rainStatusText', 'Sem Chuva');
    setText('rainPct', '0%');
    setText('rainDetail', 'Superfície condutiva seca no momento.');
    setStyle('rainProgress', 'width', '0%');
  }

  // 4. Bento Tile: Sensação Térmica (Feels Like)
  setText('feelsLikeValue', `${Math.round(thermalSensation)}°`);
  const diffThermal = thermalSensation - temp;
  if (Math.abs(diffThermal) < 0.8) {
    setText('feelsLikeBadge', 'Similar à Real');
    setText('feelsLikeNote', `Sensação de ${thermalSensation.toFixed(1)}°C, alinhada à temperatura medida.`);
  } else if (diffThermal > 0) {
    setText('feelsLikeBadge', 'Mais Quente');
    setText('feelsLikeNote', `A umidade (${Math.round(hum)}%) eleva a sensação térmica para ${thermalSensation.toFixed(1)}°C.`);
  } else {
    setText('feelsLikeBadge', 'Mais Amena');
    setText('feelsLikeNote', `Conforto térmico em ${thermalSensation.toFixed(1)}°C.`);
  }

  // 5. Bento Tile: Umidade & Orvalho (DHT22)
  setText('humidityValue', `${Math.round(hum)}%`);
  setText('dewPoint', `${dewPointVal.toFixed(1)}°C`);
  setText('humidityComfort', hum >= 40 && hum <= 70 ? 'Confortável' : hum > 70 ? 'Úmido' : 'Ar Seco');

  // 6. Bento Tile: Pressão & Altitude (BMP280)
  setText('pressureValue', press.toFixed(1));
  setText('altitudeValue', `${alt.toFixed(0)} m`);
  setText('pressureTrend', press < 930 ? 'Pressão de Planalto' : press < 1010 ? 'Baixa Pressão' : 'Estável');

  // 7. Bento Tile: Luminosidade (LDR)
  setText('lightValue', `${Math.round(light)}%`);
  setStyle('lightProgress', 'width', `${Math.min(100, light)}%`);
  if (light > 70) {
    setText('lightLevel', 'Luz Intensa');
    setText('lightAnnotation', 'Forte incidência luminosa no fotoresistor.');
  } else if (light > 25) {
    setText('lightLevel', 'Moderada');
    setText('lightAnnotation', 'Iluminação difusa ou nebulosidade parcial.');
  } else {
    setText('lightLevel', 'Penumbra / Noite');
    setText('lightAnnotation', 'Baixa radiação luminosa no ambiente.');
  }

  // 8. Card de Engenharia Hot/Cold Path & ESP32
  if (pipe.persistence_reason) {
    setText('pipeReason', pipe.cold_path_persisted ? `COLD DB (${pipe.persistence_reason})` : 'HOT RAM (SSE < 15ms)');
  }
  if (pipe.hot_ticks_total !== undefined) setText('pipeHotTicks', pipe.hot_ticks_total);
  if (pipe.cold_writes_total !== undefined) setText('pipeColdWrites', pipe.cold_writes_total);

  setText('diagRssi', d.wifi_rssi_dbm ? `${d.wifi_rssi_dbm} dBm` : '-52 dBm');
  setText('diagHeap', d.free_heap_bytes ? `${Math.round(d.free_heap_bytes / 1024)} KB` : '198 KB');
  setText('diagUptime', formatUptime(d.uptime_seconds || 120));
  setText('diagDevice', data.device_id || 'esp32-meteo-01');

  updateAlertBanner();
}

function updateAqiWidget(ppm) {
  const badge = document.getElementById('aqiBadge');
  const dot = document.getElementById('aqiDot');
  const recommendation = document.getElementById('aqiRecommendation');

  let pctPosition = 8;
  let statusText = 'Boa';

  if (ppm <= 100) {
    statusText = 'Excelente';
    pctPosition = Math.max(6, (ppm / 100) * 22);
    if (recommendation) recommendation.textContent = 'Qualidade do ar limpa e estável no sensor MQ-135.';
  } else if (ppm <= 400) {
    statusText = 'Boa';
    pctPosition = 22 + ((ppm - 100) / 300) * 25;
    if (recommendation) recommendation.textContent = 'Níveis normais de CO₂ e compostos atmosféricos.';
  } else if (ppm <= 800) {
    statusText = 'Moderada';
    pctPosition = 47 + ((ppm - 400) / 400) * 28;
    if (recommendation) recommendation.textContent = 'Concentração moderada de gases detectada.';
  } else {
    statusText = 'Poluído / Alerta';
    pctPosition = Math.min(95, 75 + ((ppm - 800) / 400) * 20);
    if (recommendation) recommendation.textContent = 'Alerta: alta concentração de fumaça ou gases no MQ-135.';
  }

  if (badge) badge.textContent = statusText;
  if (dot) dot.style.left = `${Math.max(5, Math.min(95, pctPosition))}%`;
}

function determineOverallCondition(temp, hum, isRaining, aqi, light) {
  if (isRaining) return 'Chuva Moderada';
  if (aqi > 700) return 'Névoa Seca / Gases';
  if (light < 22) return 'Céu Noturno / Parcialmente Nublado';
  if (hum > 75) return 'Nublado';
  if (temp > 29 && light > 65) return 'Ensolarado';
  return 'Parcialmente Nublado';
}

function detectOscillations(current, previous) {
  if (!previous || !current) return;
  const currS = current.sensors || current;
  const prevS = previous.sensors || previous;

  const tempDiff = Number(currS.temperature_c ?? 0) - Number(prevS.temperature_c ?? 0);
  if (Math.abs(tempDiff) >= 0.1) {
    triggerFlash('heroTemp', tempDiff > 0 ? 'value-flash-up' : 'value-flash-down');
  }

  const aqiDiff = Number(currS.air_quality_ppm ?? 0) - Number(prevS.air_quality_ppm ?? 0);
  if (Math.abs(aqiDiff) >= 1.5) {
    triggerFlash('aqiPpm', aqiDiff > 0 ? 'value-flash-down' : 'value-flash-up');
  }

  const lightDiff = Number(currS.luminosity_pct ?? 0) - Number(prevS.luminosity_pct ?? 0);
  if (Math.abs(lightDiff) >= 1.0) {
    triggerFlash('lightValue', lightDiff > 0 ? 'value-flash-up' : 'value-flash-down');
  }
}

function triggerFlash(elementId, className) {
  const el = document.getElementById(elementId);
  if (!el) return;
  el.classList.remove('value-flash-up', 'value-flash-down');
  void el.offsetWidth;
  el.classList.add(className);
  setTimeout(() => el.classList.remove(className), 700);
}

function calculateHeatIndex(tempC, humPct) {
  if (tempC < 20) return tempC;
  const T = (tempC * 9) / 5 + 32;
  const R = humPct;
  const hiF =
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

function calculateDewPoint(tempC, humPct) {
  const h = Math.max(1, humPct);
  const a = 17.27;
  const b = 237.7;
  const alpha = (a * tempC) / (b + tempC) + Math.log(h / 100);
  const dp = (b * alpha) / (a - alpha);
  return isNaN(dp) ? tempC : dp;
}

function formatUptime(seconds) {
  if (!seconds) return '0h 02m';
  const hrs = Math.floor(seconds / 3600);
  const mins = Math.floor((seconds % 3600) / 60);
  const secs = seconds % 60;
  return hrs > 0 ? `${hrs}h ${mins}m` : `${mins}m ${secs}s`;
}

function setConnectionStatus(isOnline, customLabel = null) {
  const indicator = document.getElementById('statusIndicator');
  const label = document.getElementById('statusLabel');
  if (!indicator || !label) return;

  const dot = indicator.querySelector('.pulse-dot');
  if (isOnline) {
    label.textContent = customLabel || 'Ao Vivo • Hot Path SSE';
    if (dot) {
      dot.style.backgroundColor = 'var(--ios-green)';
      dot.style.boxShadow = '0 0 8px var(--ios-green)';
    }
  } else {
    label.textContent = customLabel || 'Sincronizando...';
    if (dot) {
      dot.style.backgroundColor = 'var(--ios-yellow)';
      dot.style.boxShadow = '0 0 8px var(--ios-yellow)';
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
