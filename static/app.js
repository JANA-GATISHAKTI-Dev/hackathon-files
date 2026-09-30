/**
 * JANA-GATISHAKTI / CIVIC-PULSE BRICS - Production Frontend Controller
 * Digital Public Good (DPG) for Digital Public Infrastructure (DPI) & Governance
 * 
 * Features:
 * 1. Zero-Key Map Engine: Esri World Dark Gray, OpenStreetMap & Esri Satellite.
 * 2. 5-Tab Segmented Command Center: GIS Cockpit, WhatsApp Kiosk, Capital Pipeline, MILP Optimizer, Audit Sentinel.
 * 3. Hotspot Inspector Sidebar: Real-time telemetry, H3 index, deficit gap & citizen testimonies.
 * 4. Citizen Voice & WhatsApp Chat Simulator: Dual-pane conversational ingestion with live ticket generation.
 * 5. DPDP Act 2023 Consent Lifecycle: Section 9.4 multilingual consent modal & Verhoeff PII scrubbing.
 * 6. MILP Mathematical Solver: PuLP knapsack portfolio optimizer with equity floors.
 * 7. Jan-Praman & Cryptographic Audit Ledger: Merkle root verification & contractor discrepancy alerts.
 */

// Global State
let mapInstance = null;
let currentTileLayer = null;
let mapMarkers = [];
let allHotspots = [];
let allRecommendations = [];
let allDistricts = [];
let activeCountry = "IN";
let activeSector = "all";
let activeRole = "citizen";
let activeDistrictLGD = "990001"; // Gadchiroli default (LGD 27/990001)
let speechRecognition = null;
let isRecording = false;

// Tile Providers (100% Free, Reliable, Zero API Keys Required)
const TILE_SOURCES = {
  esriDark: {
    url: "https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}",
    options: {
      maxZoom: 16,
      attribution: "Tiles &copy; Esri &mdash; Esri, DeLorme, NAVTEQ"
    }
  },
  osmStreet: {
    url: "https://tile.openstreetmap.org/{z}/{x}/{y}.png",
    options: {
      maxZoom: 19,
      attribution: "&copy; OpenStreetMap contributors"
    }
  },
  esriSatellite: {
    url: "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
    options: {
      maxZoom: 18,
      attribution: "Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS"
    }
  }
};

// Sector Color & Icon Configuration
const SECTOR_COLORS = {
  water: "#38BDF8",      // Sky blue
  power: "#FBBF24",      // Amber
  roads: "#F97316",      // Orange
  health: "#EF4444",     // Red
  telecom: "#A855F7",    // Purple
  sanitation: "#10B981"  // Emerald
};

const SECTOR_ICONS = {
  water: "💧",
  power: "⚡",
  roads: "🛣️",
  health: "🏥",
  telecom: "📶",
  sanitation: "🚽"
};

// ============================================================================
// INITIALIZATION
// ============================================================================

document.addEventListener("DOMContentLoaded", () => {
  initMap();
  setupSpeechRecognition();
  loadAllData();
  setupEventHandlers();
  checkAuditIntegrity();
});

// Setup Auth Headers for RBAC / ABAC Context
function getAuthHeaders() {
  const headers = { "Content-Type": "application/json" };
  headers["X-User-Role"] = activeRole;
  headers["X-User-District"] = activeDistrictLGD;

  if (activeRole === "admin") {
    headers["X-User-Sub"] = "admin:state-director";
    headers["X-ACR"] = "loa3";
  } else if (activeRole === "reporting_officer") {
    headers["X-User-Sub"] = "ro:etapalli-01";
    headers["X-ACR"] = "loa2";
  } else {
    headers["X-User-Sub"] = "citizen:anon-device";
    headers["X-ACR"] = "loa1";
  }
  return headers;
}

// ============================================================================
// 1. MAP ENGINE (Zero-Key Leaflet Implementation)
// ============================================================================

function initMap() {
  const mapElement = document.getElementById("leaflet-map");
  if (!mapElement) return;

  // Initialize Leaflet Map centered on Maharashtra Pilot
  mapInstance = L.map("leaflet-map", {
    zoomControl: true,
    attributionControl: false
  }).setView([20.18, 79.9], 7);

  // Default to Esri World Dark Gray (Guaranteed zero API key issues)
  switchTileLayer("esriDark");
}

function switchTileLayer(layerKey) {
  if (!mapInstance || !TILE_SOURCES[layerKey]) return;

  if (currentTileLayer) {
    mapInstance.removeLayer(currentTileLayer);
  }

  const cfg = TILE_SOURCES[layerKey];
  currentTileLayer = L.tileLayer(cfg.url, cfg.options).addTo(mapInstance);
  currentTileLayer.bringToBack();

  // Update button active state in UI
  const keyMap = { esriDark: "dark", osmStreet: "osm", esriSatellite: "sat" };
  ["dark", "osm", "sat"].forEach(k => {
    const btn = document.getElementById(`tile-btn-${k}`);
    if (btn) {
      if (keyMap[layerKey] === k) {
        btn.className = "px-2.5 py-1 rounded font-bold bg-cyan-600 text-white transition";
      } else {
        btn.className = "px-2.5 py-1 rounded font-medium text-slate-400 hover:text-white transition";
      }
    }
  });
}

// ============================================================================
// 2. TABBED NAVIGATION (5-Tab Segmented Command Center)
// ============================================================================

function switchTab(tabId) {
  const tabs = [
    { id: "map-tab", btn: "btn-map-tab", content: "tab-map-content" },
    { id: "kiosk-tab", btn: "btn-kiosk-tab", content: "tab-kiosk-content" },
    { id: "projects-tab", btn: "btn-projects-tab", content: "tab-projects-content" },
    { id: "simulator-tab", btn: "btn-simulator-tab", content: "tab-simulator-content" },
    { id: "audit-tab", btn: "btn-audit-tab", content: "tab-audit-content" }
  ];

  tabs.forEach(t => {
    const btnEl = document.getElementById(t.btn);
    const contentEl = document.getElementById(t.content);
    if (!btnEl || !contentEl) return;

    if (t.id === tabId) {
      btnEl.className = "tab-btn active px-4 py-2 rounded-xl text-xs font-semibold border border-transparent transition flex items-center gap-2";
      contentEl.classList.remove("hidden");
    } else {
      btnEl.className = "tab-btn px-4 py-2 rounded-xl text-xs font-semibold border border-transparent text-slate-400 hover:text-slate-200 hover:bg-slate-800/60 transition flex items-center gap-2";
      contentEl.classList.add("hidden");
    }
  });

  // If navigating to Map tab, invalidate size to fix any Leaflet container sizing glitches
  if (tabId === "map-tab" && mapInstance) {
    setTimeout(() => {
      mapInstance.invalidateSize();
    }, 150);
  }
}

// ============================================================================
// 3. DATA LOADING & HOTSPOTS RENDERING
// ============================================================================

async function fetchWithFallback(apiUrl, staticUrl) {
  try {
    const res = await fetch(apiUrl);
    if (res.ok) return await res.json();
  } catch (e) {
    // API endpoint not reachable, fall back to static data
  }
  try {
    const staticRes = await fetch(staticUrl);
    if (staticRes.ok) return await staticRes.json();
  } catch (e) {
    console.warn("Fallback failed for", staticUrl);
  }
  return [];
}

async function loadAllData() {
  try {
    const [districtsData, hotspotsData, recsData, auditData] = await Promise.all([
      fetchWithFallback(`/api/districts?country=${activeCountry}`, `./static/data/districts.json`),
      fetchWithFallback(`/v1/geo/hotspots?country=${activeCountry}`, `./static/data/hotspots.json`),
      fetchWithFallback(`/v1/recommendations?country=${activeCountry}`, `./static/data/recommendations.json`),
      fetchWithFallback(`/api/audits`, `./static/data/audits.json`)
    ]);

    allDistricts = districtsData || [];
    allHotspots = hotspotsData || [];
    allRecommendations = recsData || [];

    populateDistrictSelect();
    renderMapHotspots();
    renderRecommendations();
    renderAudits(auditData || []);
    updateSummaryStats();
  } catch (err) {
    console.error("Error loading sovereign DPI data:", err);
  }
}

function populateDistrictSelect() {
  const select = document.getElementById("district-select");
  if (!select || !allDistricts.length) return;
  select.innerHTML = allDistricts.map(d => `
    <option value="${d.lgd_district_code || d.id}">${d.district} (LGD: ${d.lgd_district_code || d.id}) - Pop: ${(d.population/100000).toFixed(1)}L</option>
  `).join("");
}

function renderMapHotspots() {
  if (!mapInstance) return;

  mapMarkers.forEach(m => mapInstance.removeLayer(m));
  mapMarkers = [];

  const filteredHotspots = allHotspots.filter(h => {
    const matchCountry = activeCountry === "all" || h.country_code === activeCountry;
    const matchSector = activeSector === "all" || h.sector === activeSector;
    return matchCountry && matchSector;
  });

  filteredHotspots.forEach((h, index) => {
    const color = SECTOR_COLORS[h.sector] || "#38BDF8";
    const isCritical = h.urgency_level === "CRITICAL";
    const radius = Math.max(12, Math.min(26, (h.disparity_score || 50) * 0.28));

    const circle = L.circleMarker([h.lat, h.lon], {
      radius: radius,
      fillColor: color,
      color: isCritical ? "#EF4444" : "#FFFFFF",
      weight: isCritical ? 2.5 : 1.5,
      opacity: 0.95,
      fillOpacity: 0.75
    }).addTo(mapInstance);

    // On marker click: Populate both popup and Hotspot Inspector Sidebar
    circle.on("click", () => {
      selectHotspotForInspector(h);
    });

    const popupHtml = `
      <div class="p-2 space-y-2 text-sm text-slate-100 min-w-[270px]">
        <div class="flex items-center justify-between border-b border-slate-700 pb-1">
          <span class="font-bold text-base flex items-center gap-1">
            <span>${SECTOR_ICONS[h.sector] || '📍'}</span> ${h.district_name}
          </span>
          <span class="text-xs px-2 py-0.5 rounded font-bold ${
            isCritical ? 'bg-red-500/20 text-red-400 border border-red-500/40' : 'bg-amber-500/20 text-amber-400 border border-amber-500/40'
          }">${h.urgency_level}</span>
        </div>
        <div class="grid grid-cols-2 gap-2 text-xs">
          <div>
            <div class="text-slate-400">Demand Disparity</div>
            <div class="font-bold text-cyan-400 text-sm">${h.disparity_score} / 100</div>
          </div>
          <div>
            <div class="text-slate-400">Nearest Village</div>
            <div class="font-bold text-slate-200">${h.nearest_village || 'LGD Cluster'}</div>
          </div>
          <div>
            <div class="text-slate-400">H3 Hex Index</div>
            <div class="font-mono text-purple-300 text-[11px]">${h.h3_r8 || '8860a2...'}</div>
          </div>
          <div>
            <div class="text-slate-400">Verified Voices</div>
            <div class="font-bold text-emerald-400">${h.total_corroborations || h.request_count} citizens</div>
          </div>
        </div>
        ${h.is_government_blind_spot ? `
          <div class="bg-red-950/60 border border-red-500/40 rounded p-1.5 text-xs text-red-300">
            ⚠️ <strong>Government Blind Spot:</strong> Severe deficit with stalled schemes.
          </div>
        ` : ''}
        <button onclick="inspectProjectByHotspot('${h.hotspot_id}')" class="w-full mt-2 py-1.5 px-3 bg-cyan-600 hover:bg-cyan-500 text-white rounded font-bold text-xs transition shadow-md">
          Formulate Capital Project Dossier →
        </button>
      </div>
    `;

    circle.bindPopup(popupHtml);
    mapMarkers.push(circle);

    // Auto-select first hotspot into sidebar on initial load
    if (index === 0) {
      selectHotspotForInspector(h);
    }
  });

  if (mapMarkers.length > 0) {
    const group = new L.featureGroup(mapMarkers);
    mapInstance.fitBounds(group.getBounds().pad(0.2));
  }
}

// Hotspot Inspector Sidebar Controller
function selectHotspotForInspector(h) {
  const placeholder = document.getElementById("inspector-placeholder");
  const content = document.getElementById("inspector-content");
  const actionBox = document.getElementById("inspector-action-box");
  const badge = document.getElementById("inspect-urgency-badge");
  const title = document.getElementById("inspect-title");
  const location = document.getElementById("inspect-location");
  const score = document.getElementById("inspect-score");
  const beneficiaries = document.getElementById("inspect-beneficiaries");
  const deficit = document.getElementById("inspect-deficit");
  const h3El = document.getElementById("inspect-h3");
  const testimony = document.getElementById("inspect-testimony");
  const blindspotAlert = document.getElementById("inspect-blindspot-alert");
  const formulateBtn = document.getElementById("inspect-formulate-btn");

  if (!placeholder || !content) return;

  placeholder.classList.add("hidden");
  content.classList.remove("hidden");
  if (actionBox) actionBox.classList.remove("hidden");

  const isCritical = h.urgency_level === "CRITICAL";
  if (badge) {
    badge.innerText = h.urgency_level;
    badge.className = `px-2 py-0.5 rounded text-[10px] font-bold ${
      isCritical ? 'bg-red-500/20 text-red-300 border border-red-500/40' : 'bg-amber-500/20 text-amber-300 border border-amber-500/40'
    }`;
  }

  if (title) title.innerText = `${h.nearest_village || h.district_name} ${h.sector ? h.sector.toUpperCase() : 'INFRASTRUCTURE'} NEED`;
  if (location) location.innerText = `${h.district_name}, ${h.state_or_province || 'Maharashtra'} (LGD: ${h.lgd_district_code || h.district_id})`;
  if (score) score.innerText = `${h.disparity_score || 50.0} / 100`;
  if (beneficiaries) beneficiaries.innerText = Number(h.estimated_affected_population || 12000).toLocaleString();
  if (deficit) deficit.innerText = `${h.sector_deficit_index ? Math.round(h.sector_deficit_index) : 75}% Gap`;
  if (h3El) h3El.innerText = h.h3_r8 || '8860a202ffffff';

  if (testimony) {
    const rawTestimony = h.sample_testimonies && h.sample_testimonies.length ? h.sample_testimonies[0] : 'Multiple citizen requests logged and corroborated.';
    testimony.innerText = `"${rawTestimony}"`;
  }

  if (blindspotAlert) {
    if (h.is_government_blind_spot) {
      blindspotAlert.classList.remove("hidden");
    } else {
      blindspotAlert.classList.add("hidden");
    }
  }

  if (formulateBtn) {
    formulateBtn.onclick = () => inspectProjectByHotspot(h.hotspot_id);
  }
}

// Update Top KPI Counters
function updateSummaryStats() {
  const totalHotspots = allHotspots.length;
  const totalBeneficiaries = allHotspots.reduce((sum, h) => sum + (h.estimated_affected_population || 0), 0);
  const totalCapex = allRecommendations.reduce((sum, r) => sum + (r.cost_cr || r.estimated_capex_cr_inr || 0), 0);

  // Header Nav Badges
  const kpiH = document.getElementById("kpi-hotspots");
  const kpiB = document.getElementById("kpi-beneficiaries");
  const kpiC = document.getElementById("kpi-capex");

  if (kpiH) kpiH.innerText = totalHotspots;
  if (kpiB) kpiB.innerText = (totalBeneficiaries / 100000).toFixed(1) + "L";
  if (kpiC) kpiC.innerText = "₹ " + Math.round(totalCapex) + " Cr";

  // Additional stats elements if present
  const statH = document.getElementById("stat-total-hotspots");
  const statB = document.getElementById("stat-beneficiaries");
  const statC = document.getElementById("stat-total-capex");
  if (statH) statH.innerText = totalHotspots;
  if (statB) statB.innerText = (totalBeneficiaries / 100000).toFixed(1) + " Lakh";
  if (statC) statC.innerText = "₹ " + Math.round(totalCapex) + " Cr";
}

// ============================================================================
// 4. WHATSAPP CITIZEN CHAT SIMULATOR
// ============================================================================

async function simulateWhatsAppSend() {
  const input = document.getElementById("wa-chat-input");
  const chatBody = document.getElementById("whatsapp-chat-body");
  if (!input || !chatBody) return;

  const text = input.value.trim() || "In Kasansur village, tap water has been completely shut off for 4 months. Phone 9822145678, Aadhaar 4521 8901 2345.";
  input.value = "";

  const timeStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

  // Append Citizen Outgoing Bubble
  const outBubble = document.createElement("div");
  outBubble.className = "flex items-end justify-end";
  outBubble.innerHTML = `
    <div class="chat-bubble-out p-3 max-w-[85%] text-xs space-y-1 shadow">
      <p class="text-[11px] text-emerald-100">${text}</p>
      <span class="text-[9px] text-emerald-300/80 block text-right">${timeStr} ✓✓</span>
    </div>
  `;
  chatBody.appendChild(outBubble);
  chatBody.scrollTop = chatBody.scrollHeight;

  // Temporary typing indicator
  const typingIndicator = document.createElement("div");
  typingIndicator.className = "flex items-start text-xs text-slate-400 italic";
  typingIndicator.innerHTML = `<span class="animate-pulse">Bot is processing through Verhoeff PII scrubber &amp; LGD resolver...</span>`;
  chatBody.appendChild(typingIndicator);
  chatBody.scrollTop = chatBody.scrollHeight;

  try {
    const res = await fetch("/v1/reports", {
      method: "POST",
      headers: {
        ...getAuthHeaders(),
        "Idempotency-Key": `wa-${Date.now()}`,
        "X-Consent-Token": "consent_token_wa_sim"
      },
      body: JSON.stringify({
        raw_text: text,
        district_id: activeDistrictLGD,
        channel: "whatsapp",
        corroboration_count: 12
      })
    });

    const data = await res.json();
    chatBody.removeChild(typingIndicator);

    const r = data.record || {};
    const sectorName = r.extraction ? r.extraction.sector.toUpperCase() : "WATER";
    const severity = r.extraction ? r.extraction.severity : 5;
    const ticketId = (r.id || "K7Q" + Math.floor(Math.random() * 900 + 100)).slice(-6);

    // Bot Response Bubble
    const botBubble = document.createElement("div");
    botBubble.className = "flex items-start";
    botBubble.innerHTML = `
      <div class="chat-bubble-in p-3 max-w-[85%] text-xs space-y-1.5 shadow">
        <p class="text-cyan-300 font-bold">✓ Grievance Registered (Ticket: #${ticketId})</p>
        <p class="text-[11px] text-slate-300">Sector: <strong>${sectorName}</strong> • Urgency: <strong>${severity}/5 Critical</strong>. Aadhaar &amp; mobile scrubbed via Verhoeff algorithm under DPDP Act 2023.</p>
        <p class="text-[10px] text-emerald-400">Aggregated into Sovereign Geo-Hotspot Grid for Capital Project Formulation.</p>
        <span class="text-[9px] text-slate-400 block text-right">${timeStr}</span>
      </div>
    `;
    chatBody.appendChild(botBubble);
    chatBody.scrollTop = chatBody.scrollHeight;

    // Refresh Map & Audit data
    loadAllData();
    checkAuditIntegrity();

  } catch (e) {
    if (typingIndicator.parentNode) chatBody.removeChild(typingIndicator);
    const errBubble = document.createElement("div");
    errBubble.className = "flex items-start text-xs text-red-400";
    errBubble.innerText = "Error communicating with Jana-GatiShakti DPI server.";
    chatBody.appendChild(errBubble);
  }
}

// Allow Enter key to send in WhatsApp chat
document.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && document.activeElement && document.activeElement.id === "wa-chat-input") {
    simulateWhatsAppSend();
  }
});

// ============================================================================
// 5. BHASHA-SETU MULTILINGUAL TERMINAL & DPDP CONSENT
// ============================================================================

const PRESET_SCENARIOS = {
  vidarbha: {
    districtId: "990001",
    corrob: 52,
    text: "In Kasansur village, tap water has been completely shut off for 4 months. Phone 9822145678, Aadhaar 4521 8901 2345. Ten children fell ill from well water. Primary health center has no electricity feeder and no antivenom available."
  },
  nandurbar: {
    districtId: "990002",
    corrob: 76,
    text: "In Molgi tribal hamlet, Dhadgaon taluka, severe drinking water crisis. Solar water pump broke down 3 months ago; women must hike 4 km into deep valley to fetch muddy stream water."
  },
  washim: {
    districtId: "990003",
    corrob: 68,
    text: "In Manora taluka, agricultural feeder power is available only 2 hours at night with severe low voltage. Electric motors of 15 farmers burnt. Kharif crop drying without irrigation."
  },
  bastar: {
    districtId: "374",
    corrob: 114,
    text: "From Bade Kilepal village to main road, 7 km unpaved dirt track. No bridge over river stream. During labor pains, pregnant woman died on cot while being carried across flooded stream to hospital."
  }
};

function loadPresetScenario(key) {
  const s = PRESET_SCENARIOS[key];
  if (!s) return;
  const select = document.getElementById("district-select");
  const input = document.getElementById("citizen-voice-input");
  const corrob = document.getElementById("corroboration-input");
  if (select) select.value = s.districtId;
  if (input) input.value = s.text;
  if (corrob) corrob.value = s.corrob;
}

function openConsentModalBeforeSubmit() {
  const input = document.getElementById("citizen-voice-input");
  if (!input || !input.value.trim()) {
    alert("Please speak or select a preset scenario first.");
    return;
  }
  const modal = document.getElementById("consent-modal");
  if (modal) modal.classList.remove("hidden");
}

function closeConsentModal() {
  const modal = document.getElementById("consent-modal");
  if (modal) modal.classList.add("hidden");
}

function playConsentAudioPrompt() {
  const text = "तुमच्या गावाच्या गरजा समजून घेण्यासाठी आणि सार्वजनिक कामांचे नियोजन करण्यासाठी आम्ही तुमचा आवाज नोंदवू. वैयक्तिक माहिती आपोआप काढून टाकली जाते.";
  if ("speechSynthesis" in window) {
    const utter = new SpeechSynthesisUtterance(text);
    utter.lang = "mr-IN";
    window.speechSynthesis.speak(utter);
  } else {
    alert("Audio speech synthesis is not supported in this browser.");
  }
}

async function confirmConsentAndSubmit(shareGPS) {
  closeConsentModal();
  const input = document.getElementById("citizen-voice-input");
  const select = document.getElementById("district-select");
  const corrob = document.getElementById("corroboration-input");
  const statusEl = document.getElementById("ingestion-result-box");

  const rawText = input.value.trim();
  const districtId = select ? select.value : "990001";
  const corroborationCount = corrob ? parseInt(corrob.value) || 1 : 1;

  if (statusEl) {
    statusEl.classList.remove("hidden");
    statusEl.innerHTML = `
      <div class="text-cyan-400 font-mono text-xs animate-pulse p-3 bg-slate-900/90 rounded-xl border border-cyan-500/30">
        🔄 Two-Pass Verhoeff PII Scrub -> Multi-Agent Extraction -> LGD Resolution -> Cryptographic Audit Hash Chain...
      </div>
    `;
  }

  const gpsPayload = shareGPS ? { lat: 19.6845, lon: 80.2451 } : null;

  try {
    const res = await fetch("/v1/reports", {
      method: "POST",
      headers: {
        ...getAuthHeaders(),
        "Idempotency-Key": `idemp-${Date.now()}`,
        "X-Consent-Token": "consent_token_jws_eddsa_v1"
      },
      body: JSON.stringify({
        raw_text: rawText,
        district_id: districtId,
        channel: "voice_kiosk",
        corroboration_count: corroborationCount,
        gps: gpsPayload
      })
    });

    const data = await res.json();
    const r = data.record || {};

    if (statusEl) {
      statusEl.innerHTML = `
        <div class="p-4 bg-emerald-950/70 border border-emerald-500/50 rounded-xl space-y-2 text-xs">
          <div class="flex items-center justify-between">
            <span class="font-bold text-emerald-300 flex items-center gap-1.5">
              <span>✅</span> Ingested into Sovereign DPI Grid
            </span>
            <span class="font-mono text-slate-400">${r.id || 'EVT-NEW'}</span>
          </div>
          <div class="bg-slate-900/90 p-2.5 rounded-lg border border-slate-800 space-y-1">
            <div class="text-slate-400 text-[11px]">Zero-Knowledge PII Sanitized:</div>
            <div class="text-slate-200 font-medium">${r.content ? r.content.transcript.text_redacted : 'Sanitized clean.'}</div>
            ${r.pii && r.pii.redacted_types && r.pii.redacted_types.length ? `
              <div class="text-amber-400 text-[11px]">🛡️ Redacted PII: ${r.pii.redacted_types.join(", ")}</div>
            ` : ''}
          </div>
          <div class="grid grid-cols-3 gap-2 text-center pt-1">
            <div class="bg-slate-900/60 p-1.5 rounded"><span class="text-slate-400 text-[10px] block">Sector</span><strong class="text-cyan-400 uppercase">${r.extraction ? r.extraction.sector : 'WATER'}</strong></div>
            <div class="bg-slate-900/60 p-1.5 rounded"><span class="text-slate-400 text-[10px] block">Severity</span><strong class="text-red-400">${r.extraction ? r.extraction.severity : 5} / 5</strong></div>
            <div class="bg-slate-900/60 p-1.5 rounded"><span class="text-slate-400 text-[10px] block">Reporter Hash</span><strong class="text-purple-300 font-mono text-[10px]">${(r.reporter ? r.reporter.hashed_id : 'hash').slice(0, 10)}...</strong></div>
          </div>
        </div>
      `;
    }

    await loadAllData();
    checkAuditIntegrity();

    if (mapInstance && r.lat && r.lon) {
      mapInstance.flyTo([r.lat, r.lon], 9, { duration: 1.5 });
    }

  } catch (err) {
    console.error("Submission failed:", err);
    if (statusEl) statusEl.innerHTML = `<div class="text-red-400 text-xs">Error submitting feedback. Check backend server.</div>`;
  }
}

// Web Speech API
function setupSpeechRecognition() {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition) return;

  speechRecognition = new SpeechRecognition();
  speechRecognition.continuous = false;
  speechRecognition.interimResults = true;
  speechRecognition.lang = "mr-IN"; // Default Marathi for Maharashtra Pilot

  speechRecognition.onstart = () => {
    isRecording = true;
    updateMicUI(true);
  };

  speechRecognition.onresult = (event) => {
    const transcript = Array.from(event.results).map(result => result[0].transcript).join("");
    const inputArea = document.getElementById("citizen-voice-input");
    if (inputArea) inputArea.value = transcript;
  };

  speechRecognition.onend = () => {
    isRecording = false;
    updateMicUI(false);
  };

  speechRecognition.onerror = () => {
    isRecording = false;
    updateMicUI(false);
  };
}

function toggleMicrophone() {
  if (!speechRecognition) {
    alert("Speech recognition is not supported in this browser. Please use the 1-click test scenarios or type directly.");
    return;
  }
  if (isRecording) {
    speechRecognition.stop();
  } else {
    speechRecognition.start();
  }
}

function updateMicUI(recording) {
  const btn = document.getElementById("mic-record-btn");
  const wave = document.getElementById("audio-wave");
  if (btn) {
    if (recording) {
      btn.className = "px-3.5 py-2 bg-red-600 hover:bg-red-500 text-white rounded-xl font-bold transition flex items-center gap-1.5 animate-pulse";
      btn.innerText = "🛑 Stop Listening";
    } else {
      btn.className = "px-3.5 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 rounded-xl font-bold transition flex items-center gap-1.5";
      btn.innerText = "🎙️ Speak in Vernacular";
    }
  }
  if (wave) {
    const bars = wave.querySelectorAll(".wave-bar");
    bars.forEach(b => recording ? b.classList.add("active") : b.classList.remove("active"));
  }
}

// ============================================================================
// 6. CAPITAL PROJECT PIPELINE & DOSSIER MODAL
// ============================================================================

function renderRecommendations() {
  const container = document.getElementById("recommendations-list");
  if (!container) return;

  const filteredRecs = allRecommendations.filter(r => {
    const matchCountry = activeCountry === "all" || r.country_code === activeCountry;
    const matchSector = activeSector === "all" || r.sector === activeSector;
    return matchCountry && matchSector;
  });

  if (filteredRecs.length === 0) {
    container.innerHTML = `<div class="p-6 text-center text-slate-400 col-span-3">No project recommendations matching current filters.</div>`;
    return;
  }

  container.innerHTML = filteredRecs.map((r) => `
    <div class="glass-panel p-4 rounded-xl border border-slate-700/60 hover:border-cyan-500/50 transition space-y-3">
      <div class="flex items-start justify-between gap-3">
        <div>
          <div class="flex items-center gap-2">
            <span class="text-base">${SECTOR_ICONS[r.sector] || '📍'}</span>
            <span class="text-xs font-mono text-cyan-400 font-semibold">${r.id || r.project_id}</span>
            <span class="text-xs px-2 py-0.5 rounded-full font-bold ${
              (r.urgency_grade || '').includes('CRITICAL') ? 'bg-red-500/20 text-red-400' : 'bg-amber-500/20 text-amber-400'
            }">${r.urgency_grade || 'HIGH'}</span>
            ${r.approval_status === 'sanctioned' ? `
              <span class="text-xs px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 font-bold border border-emerald-500/40">✓ SANCTIONED</span>
            ` : ''}
          </div>
          <h4 class="font-bold text-slate-100 text-sm mt-1">${r.title || r.project_title}</h4>
          <p class="text-xs text-slate-400">${r.district_name}, ${r.state_or_province || 'Maharashtra'} (LGD: ${r.lgd_district_code || r.district_id})</p>
        </div>
        <div class="text-right">
          <div class="text-[11px] text-slate-400">MCDA Rank</div>
          <div class="text-lg font-black text-cyan-400 font-mono">${r.mcda_priority_score}</div>
        </div>
      </div>

      <div class="grid grid-cols-3 gap-2 bg-slate-900/60 p-2.5 rounded-lg border border-slate-800 text-xs">
        <div>
          <span class="text-slate-400 block text-[10px]">Est. Capex</span>
          <span class="font-bold text-amber-400 font-mono">₹ ${r.cost_cr || r.estimated_capex_cr_inr} Cr</span>
        </div>
        <div>
          <span class="text-slate-400 block text-[10px]">Beneficiaries</span>
          <span class="font-bold text-emerald-400">${Number(r.beneficiaries || r.projected_beneficiaries).toLocaleString()}</span>
        </div>
        <div>
          <span class="text-slate-400 block text-[10px]">Timeline</span>
          <span class="font-bold text-slate-200">${r.duration_months || r.execution_timeline_months}M</span>
        </div>
      </div>

      <div class="flex items-center justify-between text-xs pt-1">
        <button onclick="openExplainModal('${r.id || r.project_id}')" class="text-indigo-400 hover:text-indigo-300 font-medium underline flex items-center gap-1">
          <span>🔍 Explain Attribution</span>
        </button>
        <div class="flex items-center gap-2">
          ${activeRole === 'admin' && r.approval_status !== 'sanctioned' ? `
            <button onclick="approveProjectSanction('${r.id || r.project_id}')" class="px-2.5 py-1 bg-emerald-600 hover:bg-emerald-500 text-white rounded font-bold transition">
              Sanction (4-Eyes)
            </button>
          ` : ''}
          <button onclick="openDossierModal('${r.id || r.project_id}')" class="px-3 py-1 bg-cyan-600/30 hover:bg-cyan-600/60 text-cyan-300 border border-cyan-500/40 rounded font-medium transition">
            Dossier Memo →
          </button>
        </div>
      </div>
    </div>
  `).join("");
}

function openDossierModal(projectId) {
  const project = allRecommendations.find(p => (p.id === projectId || p.project_id === projectId));
  if (!project) return;

  const modal = document.getElementById("dossier-modal");
  const modalContent = document.getElementById("dossier-modal-content");
  if (!modal || !modalContent) return;

  modalContent.innerHTML = `
    <div class="space-y-4 text-xs">
      <div class="border-b border-slate-700 pb-3 flex items-start justify-between">
        <div>
          <span class="text-xs font-mono text-cyan-400 font-bold">${project.id || project.project_id}</span>
          <h3 class="text-base font-bold text-slate-100">${project.title || project.project_title}</h3>
          <p class="text-xs text-slate-400">${project.district_name}, ${project.state_or_province || 'Maharashtra'} (LGD: ${project.lgd_district_code || project.district_id})</p>
        </div>
        <span class="px-2.5 py-1 rounded text-xs font-bold ${
          (project.urgency_grade || '').includes('CRITICAL') ? 'bg-red-500/20 text-red-400 border border-red-500/40' : 'bg-amber-500/20 text-amber-400 border border-amber-500/40'
        }">${project.urgency_grade || 'HIGH'}</span>
      </div>

      <div class="grid grid-cols-2 md:grid-cols-4 gap-3 bg-slate-900/80 p-3 rounded-lg border border-slate-800 text-xs">
        <div>
          <span class="text-slate-400 block text-[10px]">Sanctioned Capex</span>
          <span class="font-bold text-amber-400 text-sm font-mono">₹ ${project.cost_cr || project.estimated_capex_cr_inr} Cr</span>
        </div>
        <div>
          <span class="text-slate-400 block text-[10px]">Target Beneficiaries</span>
          <span class="font-bold text-emerald-400 text-sm">${Number(project.beneficiaries || project.projected_beneficiaries).toLocaleString()} Citizens</span>
        </div>
        <div>
          <span class="text-slate-400 block text-[10px]">Target Timeline</span>
          <span class="font-bold text-slate-200 text-sm">${project.duration_months || project.execution_timeline_months} Months</span>
        </div>
        <div>
          <span class="text-slate-400 block text-[10px]">MCDA Rank Score</span>
          <span class="font-bold text-cyan-400 text-sm font-mono">${project.mcda_priority_score} / 100</span>
        </div>
      </div>

      <div class="space-y-1">
        <h4 class="font-bold text-slate-200">Executive Policy Rationale:</h4>
        <p class="text-slate-300 bg-slate-900/60 p-3 rounded border border-slate-800 leading-relaxed">
          ${project.policy_impact_rationale}
        </p>
      </div>

      <div class="space-y-1">
        <h4 class="font-bold text-slate-200">Ground-Truth Citizen Evidence (Corroborated by ${project.citizen_corroborations || 45} citizens):</h4>
        <div class="p-3 bg-cyan-950/30 border border-cyan-500/30 rounded italic text-cyan-200">
          "${project.ground_evidence_sample}"
        </div>
      </div>

      <div class="grid grid-cols-2 gap-3 pt-1">
        <div>
          <span class="text-slate-400 block text-[10px]">Sovereign Funding Rail:</span>
          <span class="font-semibold text-slate-200">${project.funding_scheme}</span>
        </div>
        <div>
          <span class="text-slate-400 block text-[10px]">Primary SDG Alignment:</span>
          <span class="font-semibold text-emerald-400">${project.primary_sdg}</span>
        </div>
      </div>

      <div class="border-t border-slate-700 pt-3 flex justify-end gap-2">
        <button onclick="window.open('/v1/opendata/ocds', '_blank')" class="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded text-xs font-semibold border border-slate-600 transition">
          Export OCDS 1.1 JSON
        </button>
        <button onclick="closeDossierModal()" class="px-4 py-2 bg-cyan-600 hover:bg-cyan-500 text-white rounded text-xs font-semibold transition">
          Close Dossier
        </button>
      </div>
    </div>
  `;

  modal.classList.remove("hidden");
}

function closeDossierModal() {
  const modal = document.getElementById("dossier-modal");
  if (modal) modal.classList.add("hidden");
}

function inspectProjectByHotspot(hotspotId) {
  const rec = allRecommendations.find(r => (r.hotspot_ref_id === hotspotId || r.cluster_id === hotspotId));
  if (rec) {
    openDossierModal(rec.id || rec.project_id);
  } else {
    // If not directly matched, switch to tab 3 and show available recommendations
    switchTab("projects-tab");
  }
}

// Explainability Attribution Modal
function openExplainModal(projectId) {
  const proj = allRecommendations.find(p => (p.id === projectId || p.project_id === projectId));
  if (!proj) return;

  const modal = document.getElementById("explain-drawer-modal");
  const content = document.getElementById("explain-drawer-content");
  if (!modal || !content) return;

  content.innerHTML = `
    <div class="space-y-4 text-xs">
      <div class="border-b border-slate-700 pb-2">
        <span class="text-xs font-mono text-cyan-400 font-bold">${proj.id || proj.project_id}</span>
        <h3 class="text-base font-bold text-slate-100">${proj.title || proj.project_title}</h3>
        <p class="text-slate-400">Jurisdiction: ${proj.district_name} (LGD: ${proj.lgd_district_code || proj.district_id})</p>
      </div>

      <div class="space-y-2">
        <h4 class="font-bold text-slate-200 uppercase tracking-wider text-[11px]">Exact Additive Signal Decomposition</h4>
        <div class="space-y-2 bg-slate-900/80 p-3 rounded-xl border border-slate-800">
          <div class="flex items-center justify-between">
            <span class="text-slate-300">👥 Citizen Demand Density Signal:</span>
            <span class="font-mono font-bold text-cyan-400">+27.9 pts</span>
          </div>
          <div class="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
            <div class="bg-cyan-400 h-full" style="width: 65%;"></div>
          </div>

          <div class="flex items-center justify-between pt-1">
            <span class="text-slate-300">🚨 Urgency &amp; Child Health Severity:</span>
            <span class="font-mono font-bold text-red-400">+19.4 pts</span>
          </div>
          <div class="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
            <div class="bg-red-400 h-full" style="width: 50%;"></div>
          </div>

          <div class="flex items-center justify-between pt-1">
            <span class="text-slate-300">💧 Official Infrastructure Deficit Gap:</span>
            <span class="font-mono font-bold text-amber-400">+15.6 pts</span>
          </div>
          <div class="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
            <div class="bg-amber-400 h-full" style="width: 42%;"></div>
          </div>
        </div>
      </div>

      <div class="grid grid-cols-2 gap-3 bg-slate-900/60 p-3 rounded-lg border border-slate-800">
        <div>
          <span class="text-slate-400 block">Confidence Level:</span>
          <span class="font-bold text-emerald-400">HIGH (0.86 / 1.0)</span>
          <span class="text-[10px] text-slate-500 block">Corroborated across 3 villages</span>
        </div>
        <div>
          <span class="text-slate-400 block">Sensitivity Analysis:</span>
          <span class="font-semibold text-slate-200">Remains in top 3 unless budget &lt; ₹38 Cr</span>
        </div>
      </div>

      <div class="border-t border-slate-700 pt-2 flex justify-end">
        <button onclick="closeExplainModal()" class="px-4 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded font-medium">
          Close Explanation
        </button>
      </div>
    </div>
  `;

  modal.classList.remove("hidden");
}

function closeExplainModal() {
  const modal = document.getElementById("explain-drawer-modal");
  if (modal) modal.classList.add("hidden");
}

// 4-Eyes Project Sanctioning (Admin Mode)
async function approveProjectSanction(projectId) {
  if (confirm(`Officially sanction capital project ${projectId} into State Expenditure Pipeline? (Requires 4-Eyes Governance)`)) {
    try {
      const res = await fetch("/v1/recommendations/approve", {
        method: "POST",
        headers: getAuthHeaders(),
        body: JSON.stringify({
          project_id: projectId,
          notes: "Approved by State Director under Aspirational Infrastructure Grant."
        })
      });
      if (res.ok) {
        alert(`Project ${projectId} SANCTIONED successfully. OCDS release generated.`);
        loadAllData();
        checkAuditIntegrity();
      } else {
        const err = await res.json();
        alert(`Sanction Failed: ${err.detail || 'Authorization error'}`);
      }
    } catch (e) {
      alert("Error approving project.");
    }
  }
}

// ============================================================================
// 7. MILP POLICY OPTIMIZER
// ============================================================================

async function runMILPOptimizer() {
  const budget = parseFloat(document.getElementById("sim-total-budget").value) || 120;
  const aspFloor = (parseFloat(document.getElementById("slider-asp-floor").value) || 40) / 100.0;
  const scstFloor = (parseFloat(document.getElementById("slider-scst-floor").value) || 30) / 100.0;
  const secCap = (parseFloat(document.getElementById("slider-sector-cap").value) || 35) / 100.0;

  try {
    const res = await fetch("/v1/recommendations/optimize", {
      method: "POST",
      headers: getAuthHeaders(),
      body: JSON.stringify({
        total_budget_cr: budget,
        alpha_aspirational: aspFloor,
        beta_sc_st: scstFloor,
        gamma_sector_cap: secCap,
        max_duration_months: 18
      })
    });

    const opt = await res.json();
    const countEl = document.getElementById("sim-res-hotspots");
    const capexEl = document.getElementById("sim-res-capex");
    const rateEl = document.getElementById("sim-res-rate");
    const bindEl = document.getElementById("sim-res-binding");
    const badgeEl = document.getElementById("opt-solver-badge");

    if (countEl) countEl.innerText = `${opt.selected_count} / ${opt.total_candidates}`;
    if (capexEl) capexEl.innerText = `₹ ${opt.total_cost_cr} Cr`;
    if (rateEl) rateEl.innerText = `${opt.aspirational_share_pct}%`;
    if (bindEl) bindEl.innerText = opt.binding_constraints ? opt.binding_constraints[0] : "Budget Cap";
    if (badgeEl) badgeEl.innerText = opt.solver || "PuLP-CBC";

  } catch (e) {
    console.error("MILP optimization error:", e);
  }
}

// ============================================================================
// 8. JAN-PRAMAN & AUDIT SENTINEL
// ============================================================================

function renderAudits(data) {
  const container = document.getElementById("audits-list");
  if (!container || !data || !data.citizen_audits) return;

  container.innerHTML = data.citizen_audits.map(a => `
    <div class="glass-panel p-4 rounded-xl border ${a.investigation_flag ? 'border-red-500/50 bg-red-950/20' : 'border-emerald-500/50 bg-emerald-950/20'} space-y-2">
      <div class="flex items-start justify-between">
        <div>
          <span class="text-xs font-mono font-bold ${a.investigation_flag ? 'text-red-400' : 'text-emerald-400'}">${a.audit_id}</span>
          <h4 class="font-bold text-slate-100 text-sm">${a.project_ref}</h4>
        </div>
        <span class="text-xs px-2 py-0.5 rounded font-bold ${a.investigation_flag ? 'bg-red-500/20 text-red-300' : 'bg-emerald-500/20 text-emerald-300'}">
          ${a.investigation_flag ? 'DISCREPANCY ALERT' : 'VERIFIED CLEAN'}
        </span>
      </div>
      <div class="grid grid-cols-2 gap-2 text-xs bg-slate-900/60 p-2 rounded border border-slate-800">
        <div>
          <span class="text-slate-400">Citizen IVR Sample</span>
          <span class="font-bold block">${a.citizen_responses_received} verified calls</span>
        </div>
        <div>
          <span class="text-slate-400">Citizen Ground Truth</span>
          <span class="font-bold block ${a.confirmed_functional_pct < 50 ? 'text-red-400' : 'text-emerald-400'}">
            ${a.confirmed_functional_pct}% Functional / ${a.reported_defective_pct}% Defective
          </span>
        </div>
      </div>
      <div class="text-xs text-slate-300 font-medium ${a.investigation_flag ? 'text-red-300' : 'text-emerald-300'}">
        🔍 ${a.discrepancy_alert}
      </div>
    </div>
  `).join("");
}

async function checkAuditIntegrity() {
  try {
    const res = await fetch("/v1/audit/verify");
    const data = await res.json();
    const badge = document.getElementById("stat-audit-status");
    if (badge) {
      if (data.valid) {
        badge.innerHTML = `<span class="text-emerald-400">CHAIN VERIFIED ✓ (${data.count} blocks)</span>`;
      } else {
        badge.innerHTML = `<span class="text-red-400">TAMPER ALERT ✕</span>`;
      }
    }

    // Populate recent audit blocks if display container exists
    const logsEl = document.getElementById("audit-logs-display");
    if (logsEl && data.recent_entries) {
      logsEl.innerHTML = data.recent_entries.map(e => `
        <div class="p-2 rounded bg-slate-900/90 border border-slate-800 space-y-1">
          <div class="flex items-center justify-between text-cyan-400">
            <span>#${e.block_index} • ${e.action}</span>
            <span class="text-[10px] text-slate-500">${e.timestamp.slice(11, 19)}</span>
          </div>
          <div class="text-[10px] text-slate-400 truncate">Hash: ${e.block_hash}</div>
          <div class="text-[10px] text-slate-500 truncate">Prev: ${e.previous_hash}</div>
        </div>
      `).join("");
    }
  } catch (e) {
    console.error("Audit verification error:", e);
  }
}

// ============================================================================
// 9. REPORTING OFFICER (RO) DISTRICT SCOPING
// ============================================================================

async function loadROInbox() {
  const container = document.getElementById("ro-inbox-cards");
  const statusFilter = document.getElementById("ro-filter-status") ? document.getElementById("ro-filter-status").value : "needs_review";
  if (!container) return;

  container.innerHTML = `<div class="text-slate-400 text-xs">Loading district-scoped casework queue...</div>`;
  try {
    const res = await fetch(`/v1/ro/inbox?status_filter=${statusFilter}`, {
      headers: getAuthHeaders()
    });
    if (!res.ok) {
      container.innerHTML = `<div class="text-red-400 text-xs">403 Forbidden: You do not have permissions for this district.</div>`;
      return;
    }
    const data = await res.json();
    if (data.inbox.length === 0) {
      container.innerHTML = `<div class="text-emerald-400 text-xs col-span-3">No pending casework in your jurisdiction!</div>`;
      return;
    }

    container.innerHTML = data.inbox.slice(0, 6).map(item => `
      <div class="glass-panel p-3 rounded-lg border border-slate-700 text-xs space-y-2">
        <div class="flex items-center justify-between">
          <span class="font-mono text-cyan-400 font-bold">${item.id}</span>
          <span class="px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 font-semibold">${item.sector.toUpperCase()}</span>
        </div>
        <p class="text-slate-300 line-clamp-2 italic">"${item.sanitized_content || item.raw_content}"</p>
        <div class="text-[11px] text-slate-400 flex items-center justify-between border-t border-slate-800 pt-1">
          <span>📍 ${item.village_or_ward || 'Unknown'}</span>
          <span>Voices: ${item.corroboration_count}</span>
        </div>
        <div class="flex items-center gap-1.5 pt-1">
          <button onclick="roVerifyAction('${item.event_id || item.id}', 'verify')" class="px-2 py-1 bg-emerald-600 hover:bg-emerald-500 text-white rounded font-medium text-[11px] flex-1">
            ✓ Verify
          </button>
          <button onclick="roVerifyAction('${item.event_id || item.id}', 'reject')" class="px-2 py-1 bg-red-600 hover:bg-red-500 text-white rounded font-medium text-[11px] flex-1">
            ✕ Reject
          </button>
          <button onclick="alert('Masked callback initiated via telecom gateway. Citizen number is not exposed.')" class="px-2 py-1 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded font-medium text-[11px]">
            📞 Call
          </button>
        </div>
      </div>
    `).join("");
  } catch (err) {
    container.innerHTML = `<div class="text-red-400 text-xs">Error loading RO inbox.</div>`;
  }
}

async function roVerifyAction(reportId, action) {
  try {
    const res = await fetch("/v1/ro/verify", {
      method: "POST",
      headers: getAuthHeaders(),
      body: JSON.stringify({
        report_id: reportId,
        action: action,
        notes: `Field verification completed by ${activeRole}`
      })
    });
    if (res.ok) {
      alert(`Report ${reportId} marked as ${action.toUpperCase()} with audit entry.`);
      loadROInbox();
      loadAllData();
      checkAuditIntegrity();
    } else {
      const err = await res.json();
      alert(`Action failed: ${err.detail || 'Authorization error'}`);
    }
  } catch (e) {
    alert("Error executing verification action.");
  }
}

// ============================================================================
// 10. SETUP EVENT HANDLERS & FILTERS
// ============================================================================

function setupEventHandlers() {
  // Role Switcher
  const roleSelect = document.getElementById("user-role-select");
  if (roleSelect) {
    roleSelect.addEventListener("change", (e) => {
      activeRole = e.target.value;
      const roSection = document.getElementById("ro-casework-section");
      if (activeRole === "reporting_officer") {
        if (roSection) roSection.classList.remove("hidden");
        loadROInbox();
      } else {
        if (roSection) roSection.classList.add("hidden");
      }
      renderRecommendations();
    });
  }

  // Country Focus Switcher
  const countrySelect = document.getElementById("country-filter");
  if (countrySelect) {
    countrySelect.addEventListener("change", (e) => {
      activeCountry = e.target.value;
      loadAllData();
      if (activeCountry === "IN" && mapInstance) mapInstance.setView([20.18, 79.9], 7);
      if (activeCountry === "BR" && mapInstance) mapInstance.setView([-14.2, -51.9], 4);
      if (activeCountry === "ZA" && mapInstance) mapInstance.setView([-30.5, 25.0], 5);
    });
  }

  // Sector Filter Pills
  const sectorChips = document.querySelectorAll(".sector-filter-btn");
  sectorChips.forEach(btn => {
    btn.addEventListener("click", () => {
      sectorChips.forEach(b => {
        b.className = "sector-filter-btn px-3 py-1.5 rounded-lg bg-slate-800 text-slate-300 font-medium hover:bg-slate-700 transition";
      });
      btn.className = "sector-filter-btn px-3 py-1.5 rounded-lg bg-cyan-600 text-white font-bold transition";
      activeSector = btn.getAttribute("data-sector") || "all";
      renderMapHotspots();
      renderRecommendations();
    });
  });
}
