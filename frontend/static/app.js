/**
 * JANA-GATISHAKTI / CIVIC-PULSE BRICS - Core Frontend Controller
 * Digital Public Infrastructure for Multilingual Citizen Voice Aggregation & Capital Allocation
 */

let mapInstance = null;
let mapMarkers = [];
let allHotspots = [];
let allRecommendations = [];
let allDistricts = [];
let activeCountry = "IN";
let activeSector = "all";
let speechRecognition = null;
let isRecording = false;

// Color mapping per sector
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

// Ready on load
document.addEventListener("DOMContentLoaded", () => {
  initMap();
  setupSpeechRecognition();
  loadAllData();
  setupEventHandlers();
});

// Initialize Leaflet Map
function initMap() {
  const mapElement = document.getElementById("leaflet-map");
  if (!mapElement) return;

  // Default centered on India (Aspirational Districts cluster)
  mapInstance = L.map("leaflet-map", {
    zoomControl: true,
    attributionControl: false
  }).setView([21.5, 80.0], 5);

  // High contrast dark carto tiles for sovereign command center aesthetic
  L.tileLayer("https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png", {
    maxZoom: 18,
    subdomains: "abcd"
  }).addTo(mapInstance);
}

// Load data from FastAPI backend
async function loadAllData() {
  try {
    const [districtsRes, hotspotsRes, recsRes, auditsRes] = await Promise.all([
      fetch(`/api/districts?country=${activeCountry}`),
      fetch(`/api/hotspots?country=${activeCountry}`),
      fetch(`/api/recommendations?country=${activeCountry}`),
      fetch(`/api/audits`)
    ]);

    allDistricts = await districtsRes.json();
    allHotspots = await hotspotsRes.json();
    allRecommendations = await recsRes.json();
    const auditData = await auditsRes.json();

    populateDistrictSelect();
    renderMapHotspots();
    renderRecommendations();
    renderAudits(auditData);
    updateSummaryStats();
  } catch (err) {
    console.error("Error loading sovereign DPI data:", err);
  }
}

// Render Hotspots onto Leaflet Map
function renderMapHotspots() {
  if (!mapInstance) return;

  // Clear existing markers
  mapMarkers.forEach(m => mapInstance.removeLayer(m));
  mapMarkers = [];

  const filteredHotspots = allHotspots.filter(h => {
    const matchCountry = activeCountry === "all" || h.country_code === activeCountry;
    const matchSector = activeSector === "all" || h.sector === activeSector;
    return matchCountry && matchSector;
  });

  filteredHotspots.forEach(h => {
    const color = SECTOR_COLORS[h.sector] || "#38BDF8";
    const isCritical = h.urgency_level === "CRITICAL";
    const radius = Math.max(12, Math.min(28, h.disparity_score * 0.3));

    // Custom circle marker
    const circle = L.circleMarker([h.lat, h.lon], {
      radius: radius,
      fillColor: color,
      color: isCritical ? "#EF4444" : "#FFFFFF",
      weight: isCritical ? 2.5 : 1.5,
      opacity: 0.9,
      fillOpacity: 0.75
    }).addTo(mapInstance);

    // Rich Tooltip & Popup
    const popupHtml = `
      <div class="p-2 space-y-2 text-sm text-slate-100 min-w-[260px]">
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
            <div class="text-slate-400">Affected Citizens</div>
            <div class="font-bold text-slate-200">${Number(h.estimated_affected_population).toLocaleString()}</div>
          </div>
          <div>
            <div class="text-slate-400">Sector Deficit</div>
            <div class="font-bold text-amber-400">${h.sector_deficit_index}%</div>
          </div>
          <div>
            <div class="text-slate-400">Corroborated Voices</div>
            <div class="font-bold text-emerald-400">${h.total_corroborations} voices</div>
          </div>
        </div>
        ${h.is_government_blind_spot ? `
          <div class="bg-red-950/60 border border-red-500/40 rounded p-1.5 text-xs text-red-300">
            ⚠️ <strong>Government Blind Spot:</strong> Severe deficit with stalled schemes.
          </div>
        ` : ''}
        <div class="text-xs text-slate-300 italic bg-slate-900/60 p-2 rounded border border-slate-800">
          "${h.sample_testimonies[0] || 'Multiple voice requests logged.'}"
        </div>
        <button onclick="inspectProjectByHotspot('${h.hotspot_id}')" class="w-full mt-2 py-1.5 px-3 bg-cyan-600 hover:bg-cyan-500 text-white rounded font-medium text-xs transition">
          Formulate Capital Project Dossier →
        </button>
      </div>
    `;

    circle.bindPopup(popupHtml);
    mapMarkers.push(circle);
  });

  // Re-center map if there are markers
  if (mapMarkers.length > 0) {
    const group = new L.featureGroup(mapMarkers);
    mapInstance.fitBounds(group.getBounds().pad(0.2));
  }
}

// Render Bankable AI Recommendations
function renderRecommendations() {
  const container = document.getElementById("recommendations-list");
  if (!container) return;

  const filteredRecs = allRecommendations.filter(r => {
    const matchCountry = activeCountry === "all" || r.country_code === activeCountry;
    const matchSector = activeSector === "all" || r.sector === activeSector;
    return matchCountry && matchSector;
  });

  if (filteredRecs.length === 0) {
    container.innerHTML = `<div class="p-6 text-center text-slate-400">No project recommendations matching current filters.</div>`;
    return;
  }

  container.innerHTML = filteredRecs.map((r, idx) => `
    <div class="glass-panel p-4 rounded-xl border border-slate-700/60 hover:border-cyan-500/50 transition space-y-3">
      <div class="flex items-start justify-between gap-3">
        <div>
          <div class="flex items-center gap-2">
            <span class="text-base">${SECTOR_ICONS[r.sector] || '📍'}</span>
            <span class="text-xs font-mono text-cyan-400 font-semibold">${r.project_id}</span>
            <span class="text-xs px-2 py-0.5 rounded-full font-bold ${
              r.urgency_grade.includes('CRITICAL') ? 'bg-red-500/20 text-red-400' : 'bg-amber-500/20 text-amber-400'
            }">${r.urgency_grade}</span>
          </div>
          <h4 class="font-bold text-slate-100 text-sm mt-1">${r.project_title}</h4>
          <p class="text-xs text-slate-400">${r.district_name}, ${r.state_or_province} (${r.country})</p>
        </div>
        <div class="text-right">
          <div class="text-xs text-slate-400">MCDA Priority</div>
          <div class="text-lg font-black text-cyan-400 font-mono">${r.mcda_priority_score}</div>
        </div>
      </div>

      <div class="grid grid-cols-3 gap-2 bg-slate-900/60 p-2.5 rounded-lg border border-slate-800 text-xs">
        <div>
          <span class="text-slate-400 block">Est. Capex</span>
          <span class="font-bold text-amber-400 font-mono">₹ ${r.estimated_capex_cr_inr} Cr</span>
          <span class="text-[10px] text-slate-500">($${r.estimated_capex_usd_mn}M)</span>
        </div>
        <div>
          <span class="text-slate-400 block">Beneficiaries</span>
          <span class="font-bold text-emerald-400">${Number(r.projected_beneficiaries).toLocaleString()}</span>
        </div>
        <div>
          <span class="text-slate-400 block">Timeline</span>
          <span class="font-bold text-slate-200">${r.execution_timeline_months} Months</span>
        </div>
      </div>

      <div class="flex items-center justify-between text-xs pt-1">
        <span class="text-slate-400 truncate max-w-[220px]" title="${r.funding_scheme}">
          🏛️ ${r.funding_scheme}
        </span>
        <button onclick="openDossierModal('${r.project_id}')" class="px-3 py-1 bg-cyan-600/30 hover:bg-cyan-600/60 text-cyan-300 border border-cyan-500/40 rounded font-medium transition">
          View Dossier Memo →
        </button>
      </div>
    </div>
  `).join("");
}

// Render Citizen Verification Audits
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

// Update Top Stat Counters
function updateSummaryStats() {
  const totalHotspotsEl = document.getElementById("stat-total-hotspots");
  const criticalHotspotsEl = document.getElementById("stat-critical-hotspots");
  const beneficiariesEl = document.getElementById("stat-beneficiaries");
  const capexEl = document.getElementById("stat-total-capex");

  if (totalHotspotsEl) totalHotspotsEl.innerText = allHotspots.length;
  if (criticalHotspotsEl) criticalHotspotsEl.innerText = allHotspots.filter(h => h.urgency_level === "CRITICAL").length;
  
  const totalBeneficiaries = allHotspots.reduce((sum, h) => sum + (h.estimated_affected_population || 0), 0);
  if (beneficiariesEl) beneficiariesEl.innerText = (totalBeneficiaries / 100000).toFixed(1) + " Lakh";

  const totalCapex = allRecommendations.reduce((sum, r) => sum + (r.estimated_capex_cr_inr || 0), 0);
  if (capexEl) capexEl.innerText = "₹ " + Math.round(totalCapex) + " Cr";
}

// Populate District Selection in Voice Terminal
function populateDistrictSelect() {
  const select = document.getElementById("district-select");
  if (!select) return;
  select.innerHTML = allDistricts.map(d => `
    <option value="${d.id}">${d.district} (${d.state || d.country}) - Pop: ${(d.population/100000).toFixed(1)}L</option>
  `).join("");
}

// Speech Recognition Setup (Web Speech API)
function setupSpeechRecognition() {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition) {
    console.warn("Web Speech API not supported in this browser; fallback presets active.");
    return;
  }

  speechRecognition = new SpeechRecognition();
  speechRecognition.continuous = false;
  speechRecognition.interimResults = true;
  speechRecognition.lang = "hi-IN"; // Default Hindi, can adapt

  speechRecognition.onstart = () => {
    isRecording = true;
    updateMicUI(true);
  };

  speechRecognition.onresult = (event) => {
    const transcript = Array.from(event.results)
      .map(result => result[0].transcript)
      .join("");
    const inputArea = document.getElementById("citizen-voice-input");
    if (inputArea) inputArea.value = transcript;
  };

  speechRecognition.onend = () => {
    isRecording = false;
    updateMicUI(false);
  };

  speechRecognition.onerror = (e) => {
    console.error("Speech recognition error:", e);
    isRecording = false;
    updateMicUI(false);
  };
}

function toggleMicrophone() {
  if (!speechRecognition) {
    alert("Speech recognition not supported in this browser. Please use the quick preset scenarios or type in the box.");
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
      btn.classList.add("bg-red-600", "animate-pulse");
      btn.innerText = "🛑 Stop Listening";
    } else {
      btn.classList.remove("bg-red-600", "animate-pulse");
      btn.innerText = "🎙️ Speak in Vernacular";
    }
  }
  if (wave) {
    const bars = wave.querySelectorAll(".wave-bar");
    bars.forEach(b => recording ? b.classList.add("active") : b.classList.remove("active"));
  }
}

// Quick Scenario Presets for Easy Demo
const PRESET_SCENARIOS = {
  vidarbha: {
    districtId: "IN-DIST-01",
    channel: "voice_ivr",
    corrob: 52,
    text: "माझं नाव आनंदराव कोवासे आहे, मोबाइल 9822145678. कासनसूर गावात नळाचे पाणी ४ महिन्यांपासून पूर्ण बंद आहे. विहिरीचे पाणी पिऊन १० मुले आजारी पडली आहेत. प्राथमिक आरोग्य केंद्रात वीज नाही आणि अँटीव्हेनम उपलब्ध नाही."
  },
  bastar: {
    districtId: "IN-DIST-03",
    channel: "voice_ivr",
    corrob: 114,
    text: "हमारे बडेकिलेपाल गांव से मुख्य सड़क तक 7 किलोमीटर कोई पक्की सड़क नहीं है। नाले पर पुलिया नहीं है। पिछले हफ्ते प्रसव पीड़ा के दौरान एक गर्भवती महिला को खाट पर ले जाते समय रास्ते में दम तोड़ दिया।"
  },
  bundelkhand: {
    districtId: "IN-DIST-02",
    channel: "voice_ivr",
    corrob: 89,
    text: "मानिकपुर के रानीपुर मजरे में जल जीवन मिशन की पाइपलाइन तो बिछा दी गई लेकिन पानी एक दिन भी नहीं आया। आधार कार्ड नंबर 4521 8901 2345 है। महिलाएं 3 किलोमीटर दूर पथरीले रास्ते से पानी लाती हैं।"
  },
  raichur: {
    districtId: "IN-DIST-04",
    channel: "whatsapp",
    corrob: 92,
    text: "ನನ್ನ ಹೆಸರು ಮಲ್ಲೇಶಪ್ಪ, ಮಾನ್ವಿ ತಾಲ್ಲೂಕು. ನಮ್ಮ ಗ್ರಾಮದ ಕೊಳವೆ ಬಾವಿ ನೀರಿನಲ್ಲಿ ಆರ್ಸೆನಿಕ್ ಮತ್ತು ಫ್ಲೋರೈಡ್ ವಿಷಕಾರಿ ಪ್ರಮಾಣದಲ್ಲಿದೆ. ಶುದ್ಧ ಕುಡಿಯುವ ನೀರಿನ ಘಟಕ (RO ಪ್ಲಾಂಟ್) 8 ತಿಂಗಳಿನಿಂದ ಮುಚ್ಚಲ್ಪಟ್ಟಿದೆ."
  },
  nuh: {
    districtId: "IN-DIST-05",
    channel: "whatsapp",
    corrob: 81,
    text: "कन्या उच्च विद्यालय में 400 छात्राएं हैं लेकिन एक भी चालू शौचालय नहीं है। पानी की पाइपलाइन टूटी है। लड़कियां दोपहर बाद स्कूल छोड़कर घर चली जाती हैं। फोन: 9812034567।"
  },
  brazil: {
    districtId: "BR-DIST-01",
    channel: "voice_ivr",
    corrob: 65,
    text: "Olá, meu nome é Maria Silva, CPF 123.456.789-00, telefone (74) 99123-4567. A nossa cisterna comunitária secou há três meses. O posto de saúde está sem energia solar."
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

// Ingest Live Feedback
async function submitCitizenFeedback() {
  const input = document.getElementById("citizen-voice-input");
  const select = document.getElementById("district-select");
  const corrob = document.getElementById("corroboration-input");
  const statusEl = document.getElementById("ingestion-result-box");

  if (!input || !input.value.trim()) {
    alert("Please speak or enter citizen feedback text.");
    return;
  }

  const rawText = input.value.trim();
  const districtId = select ? select.value : "IN-DIST-01";
  const corroborationCount = corrob ? parseInt(corrob.value) || 1 : 1;

  if (statusEl) {
    statusEl.classList.remove("hidden");
    statusEl.innerHTML = `
      <div class="text-cyan-400 font-mono text-xs animate-pulse">
        🔄 Processing vernacular audio stream -> Scrubbing PII -> Extracting Sector & Urgency -> Updating Geospatial Grid...
      </div>
    `;
  }

  try {
    const res = await fetch("/api/feedback/submit", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        raw_text: rawText,
        district_id: districtId,
        channel: "voice_ivr",
        corroboration_count: corroborationCount
      })
    });

    const data = await res.json();
    const r = data.processed_record;

    if (statusEl) {
      statusEl.innerHTML = `
        <div class="p-3 bg-emerald-950/60 border border-emerald-500/50 rounded-lg space-y-2 text-xs">
          <div class="flex items-center justify-between">
            <span class="font-bold text-emerald-300">✅ Ingested into Sovereign DPI Grid</span>
            <span class="font-mono text-slate-400">${r.id}</span>
          </div>
          <div class="bg-slate-900/80 p-2 rounded border border-slate-800 space-y-1">
            <div class="text-slate-400">Zero-Knowledge PII Sanitized:</div>
            <div class="text-slate-200 font-medium">${r.sanitized_content}</div>
            ${r.redacted_pii && r.redacted_pii.length ? `
              <div class="text-amber-400 text-[11px]">🛡️ Redacted PII: ${r.redacted_pii.join(", ")}</div>
            ` : ''}
          </div>
          <div class="grid grid-cols-3 gap-2">
            <div><span class="text-slate-400">Classified Sector:</span> <strong class="text-cyan-400 uppercase">${r.sector}</strong></div>
            <div><span class="text-slate-400">Severity:</span> <strong class="text-red-400">${r.severity} / 5</strong></div>
            <div><span class="text-slate-400">Language:</span> <strong class="text-purple-400 uppercase">${r.original_language}</strong></div>
          </div>
        </div>
      `;
    }

    // Refresh map and project recommendations dynamically!
    await loadAllData();

    // Pan map to new report
    if (mapInstance && r.lat && r.lon) {
      mapInstance.flyTo([r.lat, r.lon], 9, { duration: 1.5 });
    }

  } catch (err) {
    console.error("Submission failed:", err);
    if (statusEl) statusEl.innerHTML = `<div class="text-red-400 text-xs">Error submitting feedback. Check backend server.</div>`;
  }
}

// Interactive What-If Budget Simulator
async function runBudgetSimulation() {
  const budgetInput = document.getElementById("sim-total-budget");
  const totalBudget = budgetInput ? parseFloat(budgetInput.value) || 100 : 100;

  const w_water = parseFloat(document.getElementById("slider-water").value) || 30;
  const w_roads = parseFloat(document.getElementById("slider-roads").value) || 25;
  const w_power = parseFloat(document.getElementById("slider-power").value) || 15;
  const w_health = parseFloat(document.getElementById("slider-health").value) || 15;
  const w_telecom = parseFloat(document.getElementById("slider-telecom").value) || 10;
  const w_sanitation = parseFloat(document.getElementById("slider-sanitation").value) || 5;

  const allocations = {
    water: w_water,
    roads: w_roads,
    power: w_power,
    health: w_health,
    telecom: w_telecom,
    sanitation: w_sanitation
  };

  try {
    const res = await fetch("/api/simulate-budget", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        total_budget_cr: totalBudget,
        allocations: allocations
      })
    });

    const result = await res.json();

    document.getElementById("sim-res-hotspots").innerText = `${result.hotspots_resolved_count} / ${result.total_hotspots_evaluated}`;
    document.getElementById("sim-res-rate").innerText = `${result.resolution_rate_pct}%`;
    document.getElementById("sim-res-beneficiaries").innerText = Number(result.total_beneficiaries_reached).toLocaleString();
    document.getElementById("sim-res-deficit-drop").innerText = `-${result.projected_deficit_reduction_pct}%`;
    document.getElementById("sim-res-satisfaction").innerText = `+${result.projected_satisfaction_surge_pct}%`;

  } catch (e) {
    console.error("Simulation error:", e);
  }
}

// Open Bankable Project Dossier Modal
function openDossierModal(projectId) {
  const project = allRecommendations.find(p => p.project_id === projectId);
  if (!project) return;

  const modal = document.getElementById("dossier-modal");
  const modalContent = document.getElementById("dossier-modal-content");
  if (!modal || !modalContent) return;

  modalContent.innerHTML = `
    <div class="space-y-4">
      <div class="border-b border-slate-700 pb-3 flex items-start justify-between">
        <div>
          <span class="text-xs font-mono text-cyan-400 font-bold">${project.project_id}</span>
          <h3 class="text-lg font-bold text-slate-100">${project.project_title}</h3>
          <p class="text-xs text-slate-400">${project.district_name}, ${project.state_or_province} (${project.country})</p>
        </div>
        <span class="px-2.5 py-1 rounded text-xs font-bold ${
          project.urgency_grade.includes('CRITICAL') ? 'bg-red-500/20 text-red-400 border border-red-500/40' : 'bg-amber-500/20 text-amber-400 border border-amber-500/40'
        }">${project.urgency_grade}</span>
      </div>

      <div class="grid grid-cols-2 md:grid-cols-4 gap-3 bg-slate-900/80 p-3 rounded-lg border border-slate-800 text-xs">
        <div>
          <span class="text-slate-400 block">Sanctioned Capex</span>
          <span class="font-bold text-amber-400 text-sm font-mono">₹ ${project.estimated_capex_cr_inr} Cr</span>
          <span class="text-[10px] text-slate-500">($${project.estimated_capex_usd_mn}M USD)</span>
        </div>
        <div>
          <span class="text-slate-400 block">Target Beneficiaries</span>
          <span class="font-bold text-emerald-400 text-sm">${Number(project.projected_beneficiaries).toLocaleString()} Citizens</span>
        </div>
        <div>
          <span class="text-slate-400 block">Target Timeline</span>
          <span class="font-bold text-slate-200 text-sm">${project.execution_timeline_months} Months</span>
        </div>
        <div>
          <span class="text-slate-400 block">MCDA Rank Score</span>
          <span class="font-bold text-cyan-400 text-sm font-mono">${project.mcda_priority_score} / 100</span>
        </div>
      </div>

      <div class="space-y-2 text-xs">
        <h4 class="font-bold text-slate-200">Executive Policy Rationale:</h4>
        <p class="text-slate-300 bg-slate-900/60 p-3 rounded border border-slate-800 leading-relaxed">
          ${project.policy_impact_rationale}
        </p>
      </div>

      <div class="space-y-1 text-xs">
        <h4 class="font-bold text-slate-200">Ground-Truth Citizen Testimony (Corroborated by ${project.citizen_corroborations} citizens):</h4>
        <div class="p-3 bg-cyan-950/30 border border-cyan-500/30 rounded italic text-cyan-200">
          "${project.ground_evidence_sample}"
        </div>
      </div>

      <div class="grid grid-cols-2 gap-3 text-xs pt-1">
        <div>
          <span class="text-slate-400 block">Sovereign Funding Rail:</span>
          <span class="font-semibold text-slate-200">${project.funding_scheme}</span>
        </div>
        <div>
          <span class="text-slate-400 block">Primary SDG Alignment:</span>
          <span class="font-semibold text-emerald-400">${project.primary_sdg}</span>
        </div>
      </div>

      <div class="border-t border-slate-700 pt-3 flex justify-end gap-2">
        <button onclick="downloadOCDSMemo('${project.project_id}')" class="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded text-xs font-semibold border border-slate-600 transition">
          Export OCDS (Open Contracting JSON)
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
  const rec = allRecommendations.find(r => r.hotspot_ref_id === hotspotId);
  if (rec) {
    openDossierModal(rec.project_id);
  } else {
    alert("Project Dossier formulating for hotspot " + hotspotId);
  }
}

// Download OCDS Memo
function downloadOCDSMemo(projectId) {
  window.open("/api/dpg/ocds", "_blank");
}

// Setup Event Listeners & Filter Switches
function setupEventHandlers() {
  // Country Switcher
  const countrySelect = document.getElementById("country-filter");
  if (countrySelect) {
    countrySelect.addEventListener("change", (e) => {
      activeCountry = e.target.value;
      loadAllData();
      if (activeCountry === "IN" && mapInstance) mapInstance.setView([21.5, 80.0], 5);
      if (activeCountry === "BR" && mapInstance) mapInstance.setView([-14.2, -51.9], 4);
      if (activeCountry === "ZA" && mapInstance) mapInstance.setView([-30.5, 25.0], 5);
    });
  }

  // Sector Filter Chips
  const sectorChips = document.querySelectorAll(".sector-filter-btn");
  sectorChips.forEach(btn => {
    btn.addEventListener("click", () => {
      sectorChips.forEach(b => b.classList.remove("bg-cyan-600", "text-white"));
      btn.classList.add("bg-cyan-600", "text-white");
      activeSector = btn.getAttribute("data-sector") || "all";
      renderMapHotspots();
      renderRecommendations();
    });
  });

  // Budget Sliders auto-calculation
  const sliders = ["water", "roads", "power", "health", "telecom", "sanitation"];
  sliders.forEach(s => {
    const el = document.getElementById(`slider-${s}`);
    const valEl = document.getElementById(`val-${s}`);
    if (el && valEl) {
      el.addEventListener("input", () => {
        valEl.innerText = `${el.value}%`;
        runBudgetSimulation();
      });
    }
  });

  const totalBudgetInput = document.getElementById("sim-total-budget");
  if (totalBudgetInput) {
    totalBudgetInput.addEventListener("input", runBudgetSimulation);
  }
}
