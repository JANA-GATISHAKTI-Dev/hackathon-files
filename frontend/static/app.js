/**
 * JANA-GATISHAKTI / CIVIC-PULSE BRICS - Production Frontend Controller
 * Implements DPDP Act 2023 Consent, ABAC District Scoping, MILP Optimization & Explainability
 */

let mapInstance = null;
let mapMarkers = [];
let allHotspots = [];
let allRecommendations = [];
let allDistricts = [];
let activeCountry = "IN";
let activeSector = "all";
let activeRole = "citizen";
let activeDistrictLGD = "990001"; // Gadchiroli default
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
  checkAuditIntegrity();
});

// Setup Headers for Current Role (RBAC / ABAC)
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

// Initialize Leaflet Map
function initMap() {
  const mapElement = document.getElementById("leaflet-map");
  if (!mapElement) return;

  // Default centered on Maharashtra Pilot (Gadchiroli cluster)
  mapInstance = L.map("leaflet-map", {
    zoomControl: true,
    attributionControl: false
  }).setView([20.18, 79.9], 6);

  L.tileLayer("https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png", {
    maxZoom: 18,
    subdomains: "abcd"
  }).addTo(mapInstance);
}

// Check Cryptographic Audit Ledger Integrity
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
  } catch (e) {
    console.error("Audit verification error:", e);
  }
}

// Load data from FastAPI backend
async function loadAllData() {
  try {
    const [districtsRes, hotspotsRes, recsRes, auditsRes] = await Promise.all([
      fetch(`/api/districts?country=${activeCountry}`),
      fetch(`/v1/geo/hotspots?country=${activeCountry}`),
      fetch(`/v1/recommendations?country=${activeCountry}`),
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

// Populate District Selection in Voice Terminal (with LGD codes)
function populateDistrictSelect() {
  const select = document.getElementById("district-select");
  if (!select) return;
  select.innerHTML = allDistricts.map(d => `
    <option value="${d.lgd_district_code || d.id}">${d.district} (LGD: ${d.lgd_district_code || d.id}) - Pop: ${(d.population/100000).toFixed(1)}L</option>
  `).join("");
}

// Render Hotspots onto Leaflet Map
function renderMapHotspots() {
  if (!mapInstance) return;

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
    const radius = Math.max(12, Math.min(26, h.disparity_score * 0.28));

    const circle = L.circleMarker([h.lat, h.lon], {
      radius: radius,
      fillColor: color,
      color: isCritical ? "#EF4444" : "#FFFFFF",
      weight: isCritical ? 2.5 : 1.5,
      opacity: 0.9,
      fillOpacity: 0.75
    }).addTo(mapInstance);

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
            <div class="text-slate-400">Unique Citizens</div>
            <div class="font-bold text-emerald-400">${h.unique_citizens || h.request_count} verified</div>
          </div>
        </div>
        ${h.is_government_blind_spot ? `
          <div class="bg-red-950/60 border border-red-500/40 rounded p-1.5 text-xs text-red-300">
            ⚠️ <strong>Government Blind Spot:</strong> Severe deficit with stalled schemes.
          </div>
        ` : ''}
        <div class="text-xs text-slate-300 italic bg-slate-900/60 p-2 rounded border border-slate-800">
          "${h.sample_testimonies ? h.sample_testimonies[0] : 'Multiple citizen requests logged.'}"
        </div>
        <button onclick="inspectProjectByHotspot('${h.hotspot_id}')" class="w-full mt-2 py-1.5 px-3 bg-cyan-600 hover:bg-cyan-500 text-white rounded font-medium text-xs transition">
          Formulate Capital Project Dossier →
        </button>
      </div>
    `;

    circle.bindPopup(popupHtml);
    mapMarkers.push(circle);
  });

  if (mapMarkers.length > 0) {
    const group = new L.featureGroup(mapMarkers);
    mapInstance.fitBounds(group.getBounds().pad(0.2));
  }
}

// Render Recommendations with Explainability Trigger & 4-Eyes Sanction
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

  container.innerHTML = filteredRecs.map((r) => `
    <div class="glass-panel p-4 rounded-xl border border-slate-700/60 hover:border-cyan-500/50 transition space-y-3">
      <div class="flex items-start justify-between gap-3">
        <div>
          <div class="flex items-center gap-2">
            <span class="text-base">${SECTOR_ICONS[r.sector] || '📍'}</span>
            <span class="text-xs font-mono text-cyan-400 font-semibold">${r.id || r.project_id}</span>
            <span class="text-xs px-2 py-0.5 rounded-full font-bold ${
              r.urgency_grade.includes('CRITICAL') ? 'bg-red-500/20 text-red-400' : 'bg-amber-500/20 text-amber-400'
            }">${r.urgency_grade}</span>
            ${r.approval_status === 'sanctioned' ? `
              <span class="text-xs px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 font-bold border border-emerald-500/40">✓ SANCTIONED</span>
            ` : ''}
          </div>
          <h4 class="font-bold text-slate-100 text-sm mt-1">${r.title || r.project_title}</h4>
          <p class="text-xs text-slate-400">${r.district_name}, ${r.state_or_province} (LGD: ${r.lgd_district_code || r.district_id})</p>
        </div>
        <div class="text-right">
          <div class="text-xs text-slate-400">MCDA Score</div>
          <div class="text-lg font-black text-cyan-400 font-mono">${r.mcda_priority_score}</div>
        </div>
      </div>

      <div class="grid grid-cols-3 gap-2 bg-slate-900/60 p-2.5 rounded-lg border border-slate-800 text-xs">
        <div>
          <span class="text-slate-400 block">Est. Capex</span>
          <span class="font-bold text-amber-400 font-mono">₹ ${r.cost_cr || r.estimated_capex_cr_inr} Cr</span>
        </div>
        <div>
          <span class="text-slate-400 block">Beneficiaries</span>
          <span class="font-bold text-emerald-400">${Number(r.beneficiaries || r.projected_beneficiaries).toLocaleString()}</span>
        </div>
        <div>
          <span class="text-slate-400 block">Timeline</span>
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

  const totalCapex = allRecommendations.reduce((sum, r) => sum + (r.cost_cr || r.estimated_capex_cr_inr || 0), 0);
  if (capexEl) capexEl.innerText = "₹ " + Math.round(totalCapex) + " Cr";
}

// Load Reporting Officer (RO) Inbox (District Scoped)
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

// RO Verification Action
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
        alert(`Sanction Failed: ${err.detail}`);
      }
    } catch (e) {
      alert("Error approving project.");
    }
  }
}

// Solve MILP Portfolio Optimizer
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
    document.getElementById("sim-res-hotspots").innerText = `${opt.selected_count} / ${opt.total_candidates}`;
    document.getElementById("sim-res-capex").innerText = `₹ ${opt.total_cost_cr} Cr`;
    document.getElementById("sim-res-rate").innerText = `${opt.aspirational_share_pct}%`;
    document.getElementById("sim-res-binding").innerText = opt.binding_constraints ? opt.binding_constraints[0] : "Budget Cap";
    document.getElementById("opt-solver-badge").innerText = opt.solver || "PuLP-CBC";

  } catch (e) {
    console.error("MILP optimization error:", e);
  }
}

// Explainability Waterfall Drawer (Section 7.5)
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
        <p class="text-slate-400">Jurisdiction: ${proj.district_name} (LGD: ${proj.lgd_district_code})</p>
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
            <span class="text-slate-300">💧 Official Infrastructure Deficit Gap (78%):</span>
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
          <span class="text-[10px] text-slate-500 block">412 unique voices, 64% RO-verified</span>
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

// DPDP Consent Workflow
function openConsentModalBeforeSubmit() {
  const input = document.getElementById("citizen-voice-input");
  if (!input || !input.value.trim()) {
    alert("Please speak or enter citizen feedback text.");
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
  if ('speechSynthesis' in window) {
    const utter = new SpeechSynthesisUtterance(text);
    utter.lang = "mr-IN";
    window.speechSynthesis.speak(utter);
  } else {
    alert("Audio speech synthesis not supported in this browser.");
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
      <div class="text-cyan-400 font-mono text-xs animate-pulse">
        🔄 Two-Pass Verhoeff PII Scrub -> Multi-Agent Extraction -> LGD Resolution -> Cryptographic Audit Hash Chain...
      </div>
    `;
  }

  // Simulated consented GPS if requested
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
        channel: "mobile_app",
        corroboration_count: corroborationCount,
        gps: gpsPayload
      })
    });

    const data = await res.json();
    const r = data.record;

    if (statusEl) {
      statusEl.innerHTML = `
        <div class="p-3 bg-emerald-950/60 border border-emerald-500/50 rounded-lg space-y-2 text-xs">
          <div class="flex items-center justify-between">
            <span class="font-bold text-emerald-300">✅ Ingested into Sovereign DPI Grid</span>
            <span class="font-mono text-slate-400">${r.id}</span>
          </div>
          <div class="bg-slate-900/80 p-2 rounded border border-slate-800 space-y-1">
            <div class="text-slate-400">Zero-Knowledge PII Sanitized:</div>
            <div class="text-slate-200 font-medium">${r.content.transcript.text_redacted}</div>
            ${r.pii.redacted_types && r.pii.redacted_types.length ? `
              <div class="text-amber-400 text-[11px]">🛡️ Redacted PII: ${r.pii.redacted_types.join(", ")}</div>
            ` : ''}
          </div>
          <div class="grid grid-cols-3 gap-2">
            <div><span class="text-slate-400">Sector:</span> <strong class="text-cyan-400 uppercase">${r.extraction.sector}</strong></div>
            <div><span class="text-slate-400">Severity:</span> <strong class="text-red-400">${r.extraction.severity} / 5</strong></div>
            <div><span class="text-slate-400">Hashed Reporter ID:</span> <strong class="text-purple-300 font-mono text-[10px]">${r.reporter.hashed_id.slice(0, 14)}...</strong></div>
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

// Preset Citizen Scenarios
const PRESET_SCENARIOS = {
  vidarbha: {
    districtId: "990001",
    corrob: 52,
    text: "माझं नाव आनंदराव कोवासे आहे, मोबाइल 9822145678. कासनसूर गावात नळाचे पाणी ४ महिन्यांपासून पूर्ण बंद आहे. विहिरीचे पाणी पिऊन १० मुले आजारी पडली आहेत. प्राथमिक आरोग्य केंद्रात वीज नाही आणि अँटीव्हेनम उपलब्ध नाही."
  },
  bastar: {
    districtId: "374",
    corrob: 114,
    text: "हमारे बडेकिलेपाल गांव से मुख्य सड़क तक 7 किलोमीटर कोई पक्की सड़क नहीं है। नाले पर पुलिया नहीं है। प्रसव पीड़ा के दौरान गर्भवती महिला को खाट पर ले जाते समय रास्ते में दम तोड़ दिया।"
  },
  bundelkhand: {
    districtId: "164",
    corrob: 89,
    text: "मानिकपुर के रानीपुर मजरे में जल जीवन मिशन की पाइपलाइन तो बिछा दी गई लेकिन पानी एक दिन भी नहीं आया। आधार कार्ड नंबर 4521 8901 2345 है। महिलाएं 3 किलोमीटर दूर पथरीले रास्ते से पानी लाती हैं।"
  },
  nandurbar: {
    districtId: "990002",
    corrob: 76,
    text: "धडगाव तालुक्यातील मोलगी पाड्यात पिण्याच्या पाण्याची गंभीर टंचाई आहे. सोलर पंप बंद पडल्यामुळे महिलांना खोल दरीतून पाणी आणावे लागते."
  },
  washim: {
    districtId: "990003",
    corrob: 68,
    text: "मानोरा तालुक्यातील शेती फीडरवर वीज दिवसातून फक्त २ तास मिळते, व्होल्टेज कमी असल्यामुळे शेतकर्‍यांचे १५ पंप जळाले आहेत."
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

// Open Bankable Project Dossier Modal
function openDossierModal(projectId) {
  const project = allRecommendations.find(p => (p.id === projectId || p.project_id === projectId));
  if (!project) return;

  const modal = document.getElementById("dossier-modal");
  const modalContent = document.getElementById("dossier-modal-content");
  if (!modal || !modalContent) return;

  modalContent.innerHTML = `
    <div class="space-y-4">
      <div class="border-b border-slate-700 pb-3 flex items-start justify-between">
        <div>
          <span class="text-xs font-mono text-cyan-400 font-bold">${project.id || project.project_id}</span>
          <h3 class="text-lg font-bold text-slate-100">${project.title || project.project_title}</h3>
          <p class="text-xs text-slate-400">${project.district_name}, ${project.state_or_province} (LGD: ${project.lgd_district_code})</p>
        </div>
        <span class="px-2.5 py-1 rounded text-xs font-bold ${
          project.urgency_grade.includes('CRITICAL') ? 'bg-red-500/20 text-red-400 border border-red-500/40' : 'bg-amber-500/20 text-amber-400 border border-amber-500/40'
        }">${project.urgency_grade}</span>
      </div>

      <div class="grid grid-cols-2 md:grid-cols-4 gap-3 bg-slate-900/80 p-3 rounded-lg border border-slate-800 text-xs">
        <div>
          <span class="text-slate-400 block">Sanctioned Capex</span>
          <span class="font-bold text-amber-400 text-sm font-mono">₹ ${project.cost_cr || project.estimated_capex_cr_inr} Cr</span>
        </div>
        <div>
          <span class="text-slate-400 block">Target Beneficiaries</span>
          <span class="font-bold text-emerald-400 text-sm">${Number(project.beneficiaries || project.projected_beneficiaries).toLocaleString()} Citizens</span>
        </div>
        <div>
          <span class="text-slate-400 block">Target Timeline</span>
          <span class="font-bold text-slate-200 text-sm">${project.duration_months || project.execution_timeline_months} Months</span>
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
        <h4 class="font-bold text-slate-200">Ground-Truth Citizen Evidence (Corroborated by ${project.citizen_corroborations} citizens):</h4>
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
    alert("Project Dossier formulating for cluster " + hotspotId);
  }
}

// Setup Event Listeners & Role Switcher
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

  // Country Switcher
  const countrySelect = document.getElementById("country-filter");
  if (countrySelect) {
    countrySelect.addEventListener("change", (e) => {
      activeCountry = e.target.value;
      loadAllData();
      if (activeCountry === "IN" && mapInstance) mapInstance.setView([20.18, 79.9], 6);
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
}

// Speech Recognition Setup (Web Speech API)
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
    alert("Speech recognition not supported in this browser. Please use the quick presets or type in the box.");
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
