/**
 * EcoPulse — Módulo de Geolocalização e Cobertura (Leaflet.js)
 * Estética Apple Maps Dark Mode & Aplicação de Geometria Analítica (Circunferência de Cobertura)
 */

let mapInstance = null;
let stationMarker = null;
let coverageCircle = null;

// Coordenadas padrão da Estação (Campus UNIP / São Paulo)
const DEFAULT_LAT = -23.55052;
const DEFAULT_LNG = -46.633308;
const COVERAGE_RADIUS_METERS = 450; // Raio sensorial (450 metros)

/**
 * Inicializa o mapa com camada escura elegante
 */
function initStationMap() {
  const mapElement = document.getElementById('mapContainer');
  if (!mapElement) return;

  // Criação da instância do mapa com zoom suave
  mapInstance = L.map('mapContainer', {
    center: [DEFAULT_LAT, DEFAULT_LNG],
    zoom: 15,
    zoomControl: false,
    attributionControl: false,
  });

  // Camada de azulejos (Tiles) Dark Matter da CartoDB (estética minimalista Apple)
  L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', {
    maxZoom: 19,
    subdomains: 'abcd',
  }).addTo(mapInstance);

  // Controle de Zoom reposicionado no canto inferior direito
  L.control.zoom({ position: 'bottomright' }).addTo(mapInstance);

  // Ícone de Marcador Personalizado estilo Apple Pulse Pin
  const customIcon = L.divIcon({
    className: 'custom-apple-marker',
    html: `
      <div style="position: relative; width: 24px; height: 24px;">
        <div style="position: absolute; width: 24px; height: 24px; border-radius: 50%; background: rgba(10, 132, 255, 0.35); animation: pulseDot 2s infinite ease-in-out;"></div>
        <div style="position: absolute; top: 4px; left: 4px; width: 16px; height: 16px; border-radius: 50%; background: #0A84FF; border: 2px solid #ffffff; box-shadow: 0 2px 8px rgba(0,0,0,0.5);"></div>
      </div>
    `,
    iconSize: [24, 24],
    iconAnchor: [12, 12],
  });

  stationMarker = L.marker([DEFAULT_LAT, DEFAULT_LNG], { icon: customIcon }).addTo(mapInstance);

  // Círculo de cobertura sensorial (Aplicação de Geometria Analítica: (x - h)² + (y - k)² ≤ R²)
  coverageCircle = L.circle([DEFAULT_LAT, DEFAULT_LNG], {
    color: '#0A84FF',
    fillColor: '#0A84FF',
    fillOpacity: 0.12,
    weight: 1.5,
    radius: COVERAGE_RADIUS_METERS,
  }).addTo(mapInstance);

  stationMarker.bindPopup(`
    <div style="font-family: -apple-system, sans-serif; padding: 4px; color: #111;">
      <strong style="font-size: 13px;">Estação EcoPulse • Nó 01</strong><br>
      <span style="font-size: 11px; color: #555;">Cluster de 5 Sensores Ativos</span><br>
      <span style="font-size: 10px; color: #0A84FF; font-weight: 600;">Raio Nominal: ${COVERAGE_RADIUS_METERS}m</span>
    </div>
  `);

  // Atualiza coordenadas na legenda
  const coordsPill = document.getElementById('mapCoords');
  if (coordsPill) {
    coordsPill.textContent = `${DEFAULT_LAT.toFixed(4)}° S, ${DEFAULT_LNG.toFixed(4)}° W • Raio: ${COVERAGE_RADIUS_METERS}m`;
  }
}

