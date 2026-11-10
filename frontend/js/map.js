/**
 * EcoPulse Clima — Geolocalização Híbrida e Mapa da Estação (Leaflet.js)
 * Como a ESP32 não possui módulo GPS dedicado, a localização da estação é resolvida em 3 camadas:
 *  1. Geolocalização precisa via HTML5 (GPS / Triangulação Wi-Fi do navegador)
 *  2. Fallback automático por Geolocalização de IP (ipwho.is)
 *  3. Geocodificação reversa via OpenStreetMap Nominatim (Bairro, Cidade e UF) + clique direto no mapa
 */

window.EcoPulseMap = (function () {
  const STORAGE_KEY = "ecopulse_station_geo_v1";
  let currentCoords = [-23.5505, -46.6333];
  let currentPlaceName = "São Paulo, SP";
  let currentSuburb = "";

  let map = null;
  let tileLayer = null;
  let marker = null;
  let lastWeather = { tempC: null, humPct: null, pressHpa: null };

  const TILE_LIGHT = "https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png";
  const TILE_DARK = "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png";

  function applyLocationLabels(cityState, suburb, lat, lon, sourceLabel) {
    currentPlaceName = cityState || "São Paulo, SP";
    currentSuburb = suburb || "";

    const navLoc = document.getElementById("navbar-location-text");
    if (navLoc) {
      navLoc.textContent = currentSuburb ? `${currentSuburb} • ${currentPlaceName}` : currentPlaceName;
    }

    const heroCity = document.getElementById("hero-city-title");
    if (heroCity) {
      heroCity.textContent = currentPlaceName;
    }

    const heroEyebrow = document.getElementById("hero-eyebrow-location");
    if (heroEyebrow) {
      heroEyebrow.textContent = currentSuburb
        ? `Agora na Estação • ${currentSuburb}`
        : "Agora na Estação";
    }

    const mapSub = document.getElementById("map-subtitle-coords");
    if (mapSub && lat != null && lon != null) {
      const src = sourceLabel ? ` (${sourceLabel})` : "";
      mapSub.textContent = `${Number(lat).toFixed(4)}, ${Number(lon).toFixed(4)}${src}`;
    }
  }

  async function reverseGeocode(lat, lon, sourceLabel) {
    try {
      const url = `https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat=${lat}&lon=${lon}&accept-language=pt-BR`;
      const res = await fetch(url, { headers: { Accept: "application/json" } });
      if (!res.ok) throw new Error("Nominatim HTTP error");
      const data = await res.json();
      const addr = data.address || {};

      const suburb =
        addr.suburb ||
        addr.neighbourhood ||
        addr.city_district ||
        addr.quarter ||
        addr.borough ||
        "";
      const city =
        addr.city ||
        addr.town ||
        addr.municipality ||
        addr.village ||
        "São Paulo";
      const stateCode = addr["ISO3166-2-lvl4"]
        ? addr["ISO3166-2-lvl4"].replace("BR-", "")
        : addr.state || "SP";

      const cityState = `${city}, ${stateCode}`;
      applyLocationLabels(cityState, suburb, lat, lon, sourceLabel);

      localStorage.setItem(
        STORAGE_KEY,
        JSON.stringify({ lat, lon, cityState, suburb, sourceLabel })
      );
      refreshPopup();
    } catch (_err) {
      applyLocationLabels(currentPlaceName, currentSuburb, lat, lon, sourceLabel);
    }
  }

  function moveStationTo(lat, lon, sourceLabel = "GPS/Wi-Fi", doReverse = true) {
    currentCoords = [Number(lat), Number(lon)];
    if (map && marker) {
      marker.setLatLng(currentCoords);
      map.setView(currentCoords, 15, { animate: true });
    }
    if (doReverse) {
      reverseGeocode(currentCoords[0], currentCoords[1], sourceLabel);
    } else {
      applyLocationLabels(currentPlaceName, currentSuburb, lat, lon, sourceLabel);
    }
  }

  async function detectViaIPFallback() {
    try {
      const res = await fetch("https://ipwho.is/");
      if (!res.ok) return;
      const data = await res.json();
      if (data && data.success && data.latitude && data.longitude) {
        const cityState = data.city
          ? `${data.city}, ${data.region_code || "SP"}`
          : "São Paulo, SP";
        currentPlaceName = cityState;
        moveStationTo(data.latitude, data.longitude, "Rede IP", true);
      }
    } catch (_e) {
      // Mantém coordenada padrão caso esteja offline
    }
  }

  function requestBrowserGeolocation(userTriggered = false) {
    const btn = document.getElementById("btn-locate-station");
    if (!("geolocation" in navigator)) {
      if (userTriggered) detectViaIPFallback();
      return;
    }

    if (btn && userTriggered) {
      btn.textContent = "Localizando...";
    }

    navigator.geolocation.getCurrentPosition(
      (pos) => {
        if (btn) btn.textContent = "📍 Localizar estação";
        moveStationTo(pos.coords.latitude, pos.coords.longitude, "GPS / Wi-Fi", true);
      },
      (_err) => {
        if (btn) btn.textContent = "📍 Localizar estação";
        if (!localStorage.getItem(STORAGE_KEY)) {
          detectViaIPFallback();
        }
      },
      {
        enableHighAccuracy: true,
        timeout: 8000,
        maximumAge: 60000,
      }
    );
  }

  function refreshPopup() {
    if (!marker) return;
    const t =
      lastWeather.tempC != null
        ? `${Number(lastWeather.tempC).toFixed(1).replace(".", ",")} °C`
        : "--";
    const h =
      lastWeather.humPct != null ? `${Number(lastWeather.humPct).toFixed(0)}%` : "--";
    const p =
      lastWeather.pressHpa != null
        ? `${Number(lastWeather.pressHpa).toFixed(0)} hPa`
        : "--";
    const locTitle = currentSuburb
      ? `${currentSuburb} — ${currentPlaceName}`
      : currentPlaceName;

    marker.setPopupContent(
      `<div style="font-family:'Inter',sans-serif;font-size:12.5px;line-height:1.45;">
        <strong>Estação EcoPulse</strong><br/>
        <span style="color:#64748b;">${locTitle}</span><br/>
        Temp: <strong>${t}</strong> • Umid: <strong>${h}</strong><br/>
        Pressão: ${p}
      </div>`
    );
  }

  function init() {
    const el = document.getElementById("station-map");
    if (!el || typeof L === "undefined") return;

    // 1. Verifica se já existe posição calibrada salva no navegador
    try {
      const saved = JSON.parse(localStorage.getItem(STORAGE_KEY) || "null");
      if (saved && saved.lat && saved.lon) {
        currentCoords = [Number(saved.lat), Number(saved.lon)];
        currentPlaceName = saved.cityState || "São Paulo, SP";
        currentSuburb = saved.suburb || "";
        applyLocationLabels(
          currentPlaceName,
          currentSuburb,
          currentCoords[0],
          currentCoords[1],
          saved.sourceLabel || "Salvo"
        );
      }
    } catch (_e) {}

    map = L.map("station-map", {
      center: currentCoords,
      zoom: 14,
      zoomControl: true,
      attributionControl: false,
    });

    updateThemeTiles();

    const icon = L.divIcon({
      className: "station-pin",
      html: `<div style="width:16px;height:16px;border-radius:50%;background:#0284c7;border:3px solid #ffffff;box-shadow:0 2px 8px rgba(2,132,199,0.55);"></div>`,
      iconSize: [16, 16],
      iconAnchor: [8, 8],
    });

    marker = L.marker(currentCoords, { icon, draggable: true }).addTo(map);
    refreshPopup();

    // Permite clicar no mapa ou arrastar o pino para ajustar o ponto exato da bancada/estação
    map.on("click", (e) => {
      moveStationTo(e.latlng.lat, e.latlng.lng, "Ajuste manual", true);
    });

    marker.on("dragend", () => {
      const pos = marker.getLatLng();
      moveStationTo(pos.lat, pos.lng, "Ajuste manual", true);
    });

    const btnLocate = document.getElementById("btn-locate-station");
    if (btnLocate) {
      btnLocate.addEventListener("click", () => requestBrowserGeolocation(true));
    }

    // Se ainda não tinha localização salva, tenta obter automaticamente
    if (!localStorage.getItem(STORAGE_KEY)) {
      requestBrowserGeolocation(false);
    }

    setTimeout(() => {
      if (map) map.invalidateSize();
    }, 250);
  }

  function updateThemeTiles() {
    if (!map) return;
    const isDark = document.documentElement.getAttribute("data-theme") === "dark";
    const url = isDark ? TILE_DARK : TILE_LIGHT;

    if (tileLayer) {
      map.removeLayer(tileLayer);
    }
    tileLayer = L.tileLayer(url, { maxZoom: 18 }).addTo(map);
  }

  function updateStationPopup(tempC, humPct, pressHpa) {
    lastWeather = { tempC, humPct, pressHpa };
    refreshPopup();
  }

  return {
    init,
    updateThemeTiles,
    updateStationPopup,
    requestBrowserGeolocation,
  };
})();
