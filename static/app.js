/**
 * Seguros Atlas — Seguros de Gastos Médicos Mayores
 * Frontend Application Controller (Plans, Vertex AI Search, Gemini Agent,
 * Actuarial Cotizador, Agent Assignment & Executive Dashboard BI)
 */

let CATALOG_PLANS = [];
let SINIESTRO_GUIDE = null;
let ATLAS_AGENTS = [];
let CHAT_HISTORY = [];
let CHAT_SESSION_ID = "sess-" + Math.random().toString(36).substring(2, 10);
let DASHBOARD_DATA = null;
let chartDailyInstance = null;
let chartPlanInstance = null;

const fmtMXN = (num) =>
  new Intl.NumberFormat("es-MX", {
    style: "currency",
    currency: "MXN",
    maximumFractionDigits: 2,
  }).format(Number(num || 0));

document.addEventListener("DOMContentLoaded", async () => {
  await loadCatalog();
  previewQuoteLive();
  await loadDashboardData();
});

async function loadCatalog() {
  try {
    const res = await fetch("/api/catalog");
    const data = await res.json();
    CATALOG_PLANS = data.plans || [];
    SINIESTRO_GUIDE = data.siniestroGuide || null;
    ATLAS_AGENTS = data.agents || [];
    renderPlansGrid("Todos");
    renderSiniestroHotlines();
  } catch (err) {
    console.error("Error loading catalog:", err);
  }
}

/* ============================================================================
 * View Switching: Customer Portal vs. Executive Dashboard (Paso 5)
 * ========================================================================== */
function switchMainView(viewName) {
  const portalEl = document.getElementById("customerPortalView");
  const dashEl = document.getElementById("executiveDashboardView");
  const btnDash = document.getElementById("btnToggleDashboard");

  if (viewName === "dashboard") {
    portalEl.style.display = "none";
    dashEl.classList.add("active-view");
    btnDash.classList.add("active-mode");
    btnDash.innerHTML = "🏠 Volver al Portal de Clientes";
    loadDashboardData();
    window.scrollTo({ top: 0, behavior: "smooth" });
  } else {
    portalEl.style.display = "block";
    dashEl.classList.remove("active-view");
    btnDash.classList.remove("active-mode");
    btnDash.innerHTML = "📊 Tablero Directivo (BI)";
  }
}

function toggleExecutiveView() {
  const dashEl = document.getElementById("executiveDashboardView");
  if (dashEl.classList.contains("active-view")) {
    switchMainView("portal");
  } else {
    switchMainView("dashboard");
  }
}

/* ============================================================================
 * Paso 1 & 2: Render Plans Grid & Dedicated Plan Detail Modal
 * ========================================================================== */
function filterPlans(category, btnEl) {
  document.querySelectorAll(".category-tab").forEach((b) => b.classList.remove("active"));
  if (btnEl) btnEl.classList.add("active");
  renderPlansGrid(category);
}

function renderPlansGrid(category) {
  const container = document.getElementById("plansGridContainer");
  if (!container) return;

  const filtered =
    category === "Todos"
      ? CATALOG_PLANS
      : CATALOG_PLANS.filter((p) => p.category === category);

  container.innerHTML = filtered
    .map(
      (plan) => `
    <article class="plan-card" id="plan-${plan.id}">
      <div class="plan-card-top" style="border-top-color: ${plan.color};">
        <span class="plan-card-badge">${plan.badge}</span>
        <div class="plan-title-row">
          <img src="${plan.icon}" alt="${plan.name}" />
          <div>
            <h3>${plan.name}</h3>
            <small style="color: var(--atlas-text-muted); font-weight: 600;">${plan.category}</small>
          </div>
        </div>
        <p class="plan-tagline">${plan.tagline}</p>
        <div class="plan-kpi-strip">
          <div class="plan-kpi-box">
            <small>Suma Asegurada</small>
            <strong>${plan.suma_asegurada_default}</strong>
          </div>
          <div class="plan-kpi-box">
            <small>Maternidad</small>
            <strong>${plan.maternity_aid}</strong>
          </div>
        </div>
      </div>
      <ul class="plan-highlights-list">
        ${(plan.highlights || []).slice(0, 5).map((h) => `<li>${h}</li>`).join("")}
      </ul>
      <div class="plan-card-footer">
        <button type="button" class="btn btn-executive" onclick="openPlanDetailModal('${plan.id}')">
          🔎 Ver Detalle del Plan
        </button>
        <button type="button" class="btn btn-orange" onclick="selectPlanForQuote('${plan.id}')">
          ⚡ Cotizar Plan
        </button>
      </div>
    </article>
  `
    )
    .join("");
}

function openPlanDetailModal(planId) {
  const plan = CATALOG_PLANS.find((p) => p.id === planId);
  if (!plan) return;

  const modal = document.getElementById("planDetailModal");
  const body = document.getElementById("planDetailModalBody");

  const coveragesRows = Object.entries(plan.coverages || {})
    .map(
      ([k, v]) => `
      <tr>
        <td style="font-weight:700; color: var(--atlas-blue-deep); width: 36%;">${k}</td>
        <td>${v}</td>
      </tr>`
    )
    .join("");

  const hospitalsHtml = (plan.hospitals_sample || [])
    .map((h) => `<li style="margin-bottom:0.35rem;">🏥 ${h}</li>`)
    .join("");

  body.innerHTML = `
    <div style="display:flex; align-items:center; gap:1rem; margin-bottom:1rem; border-bottom:2px solid var(--atlas-border); padding-bottom:1rem;">
      <img src="${plan.icon}" alt="${plan.name}" style="width:68px; height:68px; object-fit:contain;" />
      <div>
        <span class="plan-card-badge" style="margin-bottom:0.25rem;">${plan.badge}</span>
        <h2 style="font-size:1.75rem; color: var(--atlas-blue-deep);">${plan.name} — Seguros Atlas</h2>
        <p style="color: var(--atlas-text-muted); font-size:0.92rem;">${plan.tagline}</p>
      </div>
    </div>

    <p style="font-size:0.95rem; margin-bottom:1.25rem; color: var(--atlas-text);">
      ${plan.description}
    </p>

    <div class="kpi-cards-grid" style="margin-bottom:1.25rem;">
      <div class="kpi-exec-card" style="padding:0.9rem;">
        <small>Suma Asegurada</small>
        <div class="kpi-value" style="font-size:1.2rem;">${plan.suma_asegurada_default}</div>
      </div>
      <div class="kpi-exec-card" style="padding:0.9rem;">
        <small>Nivel Hospitalario</small>
        <div class="kpi-value" style="font-size:1.05rem;">${plan.hospital_level}</div>
      </div>
      <div class="kpi-exec-card" style="padding:0.9rem;">
        <small>Ayuda por Maternidad</small>
        <div class="kpi-value" style="font-size:1.2rem;">${plan.maternity_aid}</div>
      </div>
      <div class="kpi-exec-card" style="padding:0.9rem;">
        <small>Emergencia Extranjero</small>
        <div class="kpi-value" style="font-size:1.02rem;">${plan.foreign_emergency}</div>
      </div>
    </div>

    <h3 style="color: var(--atlas-blue-deep); font-size:1.1rem; margin-bottom:0.6rem;">
      Detalle de Coberturas Incluidas en ${plan.name}
    </h3>
    <div class="comparison-table-wrap" style="margin-top:0; margin-bottom:1.25rem;">
      <table class="comparison-table" style="min-width:100%;">
        <tbody>${coveragesRows}</tbody>
      </table>
    </div>

    <h3 style="color: var(--atlas-blue-deep); font-size:1.05rem; margin-bottom:0.5rem;">
      Principales Hospitales y Clínicas en Convenio (${plan.name})
    </h3>
    <ul style="list-style:none; padding:0.9rem 1.1rem; background:var(--atlas-bg); border-radius:12px; margin-bottom:1.25rem; font-size:0.88rem;">
      ${hospitalsHtml}
    </ul>

    <div style="background: var(--atlas-blue-soft); padding: 1rem 1.25rem; border-radius: 12px; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:1rem;">
      <div style="max-width:520px;">
        <strong style="color: var(--atlas-blue-deep);">Perfil Recomendado:</strong>
        <p style="font-size:0.85rem; color: var(--atlas-text);">${plan.ideal_for}</p>
      </div>
      <div style="display:flex; gap:0.65rem;">
        <button type="button" class="btn btn-orange" onclick="closePlanDetailModal(); selectPlanForQuote('${plan.id}');">
          🧮 Cotizar ${plan.name} Ahora
        </button>
      </div>
    </div>
  `;

  modal.classList.add("open");
}

function closePlanDetailModal() {
  document.getElementById("planDetailModal").classList.remove("open");
}

function selectPlanForQuote(planId) {
  switchMainView("portal");
  const selectEl = document.getElementById("qPlanId");
  if (selectEl) {
    selectEl.value = planId;
    previewQuoteLive();
  }
  const cotSection = document.getElementById("cotizador-section");
  if (cotSection) {
    cotSection.scrollIntoView({ behavior: "smooth" });
  }
}

/* ============================================================================
 * Paso 3: Buscador Inteligente con Vertex AI Search
 * ========================================================================== */
function runQuickSearch(queryText) {
  const input = document.getElementById("vertexSearchInput");
  if (input) {
    input.value = queryText;
    executeVertexSearch(queryText);
  }
}

function handleVertexSearch(e) {
  e.preventDefault();
  const input = document.getElementById("vertexSearchInput");
  if (input && input.value.trim()) {
    executeVertexSearch(input.value.trim());
  }
}

async function executeVertexSearch(queryText) {
  const btn = document.getElementById("vertexSearchBtn");
  const container = document.getElementById("vertexResultsContainer");
  const summaryEl = document.getElementById("vertexAiSummaryText");
  const docsGrid = document.getElementById("vertexDocsGrid");
  const engineLabel = document.getElementById("vertexEngineLabel");

  btn.disabled = true;
  btn.textContent = "Buscando en Vertex AI...";
  container.classList.add("visible");
  summaryEl.innerHTML = "<em>Consultando índice semántico Vertex AI Search y sintetizando respuesta con Gemini...</em>";

  try {
    const res = await fetch("/api/search", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query: queryText }),
    });
    const data = await res.json();

    engineLabel.textContent = data.engine || "Vertex AI Search";
    summaryEl.innerHTML = formatSimpleMarkdown(data.aiSummary || "");

    docsGrid.innerHTML = (data.results || [])
      .map(
        (doc) => `
      <div class="vertex-doc-card">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.35rem;">
          <span style="font-size:0.7rem; font-weight:800; color: var(--atlas-blue); text-transform:uppercase;">
            ${doc.category}
          </span>
          <span style="font-size:0.72rem; background:#E6F4EA; color:#137333; padding:0.12rem 0.45rem; border-radius:999px; font-weight:700;">
            Relevancia ${Math.round((doc.score || 0.92) * 100)}%
          </span>
        </div>
        <h4>${doc.title}</h4>
        <p>${doc.content}</p>
      </div>
    `
      )
      .join("");
  } catch (err) {
    summaryEl.textContent = "Error al consultar el buscador inteligente. Intenta nuevamente.";
  } finally {
    btn.disabled = false;
    btn.textContent = "Buscar con IA";
  }
}

/* ============================================================================
 * Paso 4: Siniestros Hotlines & Gemini Conversational Agent
 * ========================================================================== */
function renderSiniestroHotlines() {
  const grid = document.getElementById("siniestroHotlinesGrid");
  if (!grid || !SINIESTRO_GUIDE) return;

  grid.innerHTML = (SINIESTRO_GUIDE.emergency_hotlines || [])
    .map(
      (item) => `
    <div class="hotline-card">
      <span class="plan-card-badge" style="background: var(--atlas-red-soft); color: var(--atlas-red);">
        ${item.badge}
      </span>
      <h3 style="font-size:1.05rem; color: var(--atlas-blue-deep); margin-bottom:0.25rem;">${item.name}</h3>
      <p style="font-size:0.8rem; color: var(--atlas-text-muted); margin-bottom:0.65rem;">${item.subtitle}</p>
      ${(item.phones || [])
        .map(
          (p) => `
        <div style="margin-top:0.35rem;">
          <small style="display:block; font-size:0.72rem; color:var(--atlas-text-muted);">${p.label}:</small>
          <a href="tel:${p.tel}" class="hotline-phone-link">📞 ${p.number}</a>
        </div>
      `
        )
        .join("")}
    </div>
  `
    )
    .join("");
}

function toggleChatDrawer(forceState) {
  const drawer = document.getElementById("geminiChatDrawer");
  if (typeof forceState === "boolean") {
    drawer.classList.toggle("open", forceState);
  } else {
    drawer.classList.toggle("open");
  }
}

function openChatWithPrompt(promptText) {
  toggleChatDrawer(true);
  sendQuickChat(promptText);
}

function sendQuickChat(promptText) {
  const input = document.getElementById("chatInputBox");
  if (input) {
    input.value = promptText;
    submitChatMessage(promptText);
    input.value = "";
  }
}

function handleChatSubmit(e) {
  e.preventDefault();
  const input = document.getElementById("chatInputBox");
  if (!input || !input.value.trim()) return;
  const text = input.value.trim();
  input.value = "";
  submitChatMessage(text);
}

async function submitChatMessage(messageText) {
  const area = document.getElementById("chatMessagesArea");
  area.insertAdjacentHTML(
    "beforeend",
    `<div class="chat-bubble user">${escapeHtml(messageText)}</div>`
  );
  const loadingId = "loading-" + Date.now();
  area.insertAdjacentHTML(
    "beforeend",
    `<div id="${loadingId}" class="chat-bubble bot"><em>Atlas Med AI (Gemini) está analizando tu consulta...</em></div>`
  );
  area.scrollTop = area.scrollHeight;

  try {
    const titularName = document.getElementById("qTitularName")?.value || "Prospecto Web";
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        sessionId: CHAT_SESSION_ID,
        message: messageText,
        history: CHAT_HISTORY,
        leadContext: { name: titularName },
      }),
    });
    const data = await res.json();

    CHAT_HISTORY.push({ role: "user", content: messageText });
    CHAT_HISTORY.push({ role: "model", content: data.reply || "" });

    const loadingEl = document.getElementById(loadingId);
    if (loadingEl) {
      let extraHtml = "";
      if (data.autoQuote && data.autoQuote.quote) {
        const q = data.autoQuote.quote;
        extraHtml = `
          <div style="margin-top:0.65rem; padding:0.65rem; background:var(--atlas-orange-soft); border:1px solid var(--atlas-orange); border-radius:10px;">
            <strong style="color:var(--atlas-blue-deep);">✅ Cotización guardada en Firestore (${q.folio})</strong><br/>
            <span>Prima Mensual: <strong>${fmtMXN(q.monthlyPremium)}</strong></span><br/>
            <button type="button" class="btn btn-executive" style="margin-top:0.4rem; padding:0.3rem 0.7rem; font-size:0.75rem;" onclick="switchMainView('dashboard')">
              Ver en Tablero Directivo →
            </button>
          </div>
        `;
        renderQuoteResultCard(data.autoQuote, true);
        loadDashboardData();
      }
      loadingEl.innerHTML = formatSimpleMarkdown(data.reply || "") + extraHtml;
    }
  } catch (err) {
    const loadingEl = document.getElementById(loadingId);
    if (loadingEl) {
      loadingEl.textContent =
        "Ocurrió un error temporal al conectar con el agente. Para emergencias médicas llama a CITAMED 55 9177 5144.";
    }
  }
  area.scrollTop = area.scrollHeight;
}

/* ============================================================================
 * Paso 5: Cotizador Rápido Actuarial & Asignación de Agente Profesional
 * ========================================================================== */
function addDependentRow() {
  const container = document.getElementById("dependentsContainer");
  const idx = container.children.length + 1;
  const row = document.createElement("div");
  row.className = "dependent-row";
  row.innerHTML = `
    <select class="form-control dep-relation" style="flex:1;" onchange="previewQuoteLive()">
      <option value="Cónyuge">Cónyuge</option>
      <option value="Hijo(a)" ${idx > 1 ? "selected" : ""}>Hijo(a)</option>
    </select>
    <input type="number" class="form-control dep-age" style="width:110px;" value="${idx === 1 ? 33 : 6}" min="0" max="99" placeholder="Edad" onchange="previewQuoteLive()" />
    <button type="button" class="btn" style="background:#FEE2E2; color:#B91C1C; padding:0.45rem 0.75rem;" onclick="this.parentElement.remove(); previewQuoteLive();">✕</button>
  `;
  container.appendChild(row);
  previewQuoteLive();
}

function collectQuoteFormPayload() {
  const deps = [];
  document.querySelectorAll("#dependentsContainer .dependent-row").forEach((row) => {
    const rel = row.querySelector(".dep-relation")?.value || "Hijo(a)";
    const age = parseInt(row.querySelector(".dep-age")?.value || "8", 10);
    deps.push({ relation: rel, age: isNaN(age) ? 8 : age });
  });

  return {
    titularName: document.getElementById("qTitularName")?.value || "Prospecto Seguros Atlas",
    titularAge: parseInt(document.getElementById("qTitularAge")?.value || "35", 10),
    titularGender: document.getElementById("qTitularGender")?.value || "Masculino",
    email: document.getElementById("qEmail")?.value || "cliente@ejemplo.com.mx",
    phone: document.getElementById("qPhone")?.value || "55 9177 5220",
    postalCode: "05120",
    city: document.getElementById("qState")?.value || "CDMX",
    state: document.getElementById("qState")?.value || "CDMX",
    planId: document.getElementById("qPlanId")?.value || "med-plus",
    deductible: parseInt(document.getElementById("qDeductible")?.value || "25000", 10),
    coinsurance: parseInt(document.getElementById("qCoinsurance")?.value || "10", 10),
    paymentFrequency: document.getElementById("qFrequency")?.value || "Mensual",
    dependents: deps,
    zeroAccidentDeductible: !!document.getElementById("qZeroAcc")?.checked,
    dentalPremium: !!document.getElementById("qDental")?.checked,
    foreignEmergencyPlus: !!document.getElementById("qForeign")?.checked,
    maternityExtended: !!document.getElementById("qMaternity")?.checked,
    source: "cotizador_web",
  };
}

/**
 * Local instant preview calculation matching backend actuarial rules
 * before the user clicks "Generar Cotización Oficial y Asignar Agente"
 */
function previewQuoteLive() {
  const payload = collectQuoteFormPayload();
  const plan =
    CATALOG_PLANS.find((p) => p.id === payload.planId) || {
      id: "med-plus",
      name: "Med Plus",
      suma_asegurada_default: "$100,000,000 MXN",
      hospital_level: "Nivel Amplio Nacional",
      maternity_aid: "$30,000 MXN",
      base_annual_premium: 22600,
    };

  const ageFactor = (a) => {
    if (a < 18) return 0.56;
    if (a <= 24) return 0.76;
    if (a <= 29) return 0.89;
    if (a <= 34) return 1.0;
    if (a <= 39) return 1.19;
    if (a <= 44) return 1.43;
    if (a <= 49) return 1.76;
    if (a <= 54) return 2.21;
    if (a <= 59) return 2.79;
    if (a <= 64) return 3.55;
    return 4.48;
  };
  const dedMap = { 15000: 1.24, 25000: 1.0, 40000: 0.83, 60000: 0.7 };
  const coMap = { 5: 1.17, 10: 1.0, 15: 0.9, 20: 0.82 };

  const base = Number(plan.base_annual_premium || 22600);
  const gFactor =
    payload.titularGender.toLowerCase().startsWith("f") &&
    payload.titularAge >= 18 &&
    payload.titularAge <= 44
      ? 1.11
      : 1.0;
  const dF = dedMap[payload.deductible] || 1.0;
  const cF = coMap[payload.coinsurance] || 1.0;

  const titularNet = base * ageFactor(payload.titularAge) * gFactor * dF * cF;
  let depNet = 0;
  payload.dependents.forEach((d) => {
    const rF = d.relation.toLowerCase().includes("hijo") ? 0.92 : 1.02;
    depNet += base * ageFactor(d.age) * rF * dF * cF;
  });

  const famDisc = payload.dependents.length >= 2 ? (titularNet + depNet) * 0.08 : 0;
  let riders = 0;
  const lives = 1 + payload.dependents.length;
  if (payload.zeroAccidentDeductible) riders += 1250 * (1 + 0.35 * payload.dependents.length);
  if (payload.dentalPremium) riders += 890 * lives;
  if (payload.foreignEmergencyPlus && payload.planId !== "plan-mundial")
    riders += 2150 * (1 + 0.4 * payload.dependents.length);
  if (payload.maternityExtended) riders += 3400;

  const net = Math.max(4500, titularNet + depNet - famDisc + riders);
  const fee = 1350;
  const iva = (net + fee) * 0.16;
  const annual = net + fee + iva;
  const monthly = annual / 12;

  const defaultAgent =
    ATLAS_AGENTS.find((a) => (a.plans_focus || []).includes(payload.planId)) ||
    ATLAS_AGENTS[0] || {
      name: "Act. Alejandro Monroy Betancourt",
      title: "Agente Profesional Certificado Senior",
      cedula: "CNSF-B184729-MX",
      branch: "Roma Norte, CDMX",
      phone: "55 9177 5220 Ext. 3208",
      email: "amonroy.agente@segurosatlas-asesores.com.mx",
      avatar_initials: "AM",
    };

  renderQuoteResultCard(
    {
      quote: {
        folio: "VISTA-PREVIA-EN-VIVO",
        planName: plan.name,
        sumInsured: plan.suma_asegurada_default,
        hospitalLevel: plan.hospital_level,
        deductible: payload.deductible,
        coinsurance: payload.coinsurance,
        titularName: payload.titularName,
        titularAge: payload.titularAge,
        dependentsCount: payload.dependents.length,
        annualPremium: annual,
        monthlyPremium: monthly,
      },
      breakdown: {
        titularNetPremium: titularNet,
        dependentsNetPremium: depNet,
        familyDiscount: famDisc,
        ridersCost: riders,
        policyFee: fee,
        iva: iva,
        annualPremium: annual,
        monthlyPremium: monthly,
        paymentFrequency: payload.paymentFrequency,
      },
      agent: defaultAgent,
    },
    false
  );
}

async function handleQuoteSubmit(e) {
  e.preventDefault();
  const btn = document.getElementById("btnSubmitQuote");
  btn.disabled = true;
  btn.textContent = "Calculando y Asignando Agente Certificado...";

  try {
    const payload = collectQuoteFormPayload();
    const res = await fetch("/api/quotes", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await res.json();
    renderQuoteResultCard(data, true);
    await loadDashboardData();
  } catch (err) {
    console.error("Error generating quote:", err);
  } finally {
    btn.disabled = false;
    btn.textContent = "🚀 Generar Cotización Oficial y Asignar Agente Seguros Atlas";
  }
}

function renderQuoteResultCard(data, isOfficialSaved) {
  const container = document.getElementById("quoteResultContent");
  if (!container || !data || !data.quote) return;

  const q = data.quote;
  const b = data.breakdown || {};
  const ag = data.agent || {};

  const statusBanner = isOfficialSaved
    ? `<div style="background:#ECFDF5; border:1.5px solid #10B981; color:#065F46; padding:0.75rem 1rem; border-radius:10px; margin-bottom:1rem; font-size:0.84rem; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:0.5rem;">
         <span>✅ <strong>Cotización Oficial Registrada (${q.folio})</strong> · Guardada en Firestore y Tablero Directivo</span>
         <button type="button" class="btn btn-executive" style="padding:0.32rem 0.75rem; font-size:0.75rem;" onclick="switchMainView('dashboard')">
           📊 Ver en Tablero Directivo
         </button>
       </div>`
    : `<div style="background:var(--atlas-blue-soft); color:var(--atlas-blue-deep); padding:0.6rem 0.95rem; border-radius:10px; margin-bottom:1rem; font-size:0.8rem; font-weight:600;">
         ⚡ Simulación Actuarial en Tiempo Real — Haz clic en <strong>"Generar Cotización Oficial"</strong> para emitir tu folio y consolidar en el Tablero Directivo.
       </div>`;

  container.innerHTML = `
    ${statusBanner}

    <div class="price-hero-Banner">
      <div style="display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:0.5rem;">
        <div>
          <span style="font-size:0.75rem; text-transform:uppercase; letter-spacing:0.05em; opacity:0.88;">
            Plan Seleccionado · Folio ${q.folio}
          </span>
          <h3 style="font-size:1.5rem; margin:0.15rem 0;">${q.planName}</h3>
          <small style="opacity:0.9;">Suma Asegurada: <strong>${q.sumInsured}</strong> · ${1 + Number(q.dependentsCount || 0)} Asegurado(s)</small>
        </div>
        <div style="text-align:right;">
          <small style="display:block; font-size:0.75rem; opacity:0.9;">Inversión Mensual Estimada</small>
          <div class="monthly-big">${fmtMXN(q.monthlyPremium)} <span style="font-size:0.9rem; font-weight:600;">/ mes</span></div>
          <small style="opacity:0.92;">Prima Total Anual: <strong>${fmtMXN(q.annualPremium)}</strong> (IVA incl.)</small>
        </div>
      </div>
    </div>

    <h4 style="color:var(--atlas-blue-deep); font-size:0.95rem; margin-bottom:0.6rem;">
      Desglose Actuarial Transparente (Reglas de Mercado SGMM)
    </h4>
    <div class="comparison-table-wrap" style="margin-top:0; margin-bottom:1rem; box-shadow:none;">
      <table class="comparison-table" style="min-width:100%; font-size:0.83rem;">
        <tbody>
          <tr>
            <td>Prima Neta Titular (${q.titularAge} años · Deducible $${Number(q.deductible).toLocaleString()} / Coaseguro ${q.coinsurance}%)</td>
            <td style="text-align:right; font-weight:700;">${fmtMXN(b.titularNetPremium)}</td>
          </tr>
          <tr>
            <td>Prima Dependientes Adicionales (${q.dependentsCount || 0} dependientes)</td>
            <td style="text-align:right; font-weight:700;">${fmtMXN(b.dependentsNetPremium)}</td>
          </tr>
          ${
            Number(b.familyDiscount || 0) > 0
              ? `<tr style="color:var(--atlas-success);">
                   <td>Descuento Póliza Familiar (8% por 2+ dependientes)</td>
                   <td style="text-align:right; font-weight:700;">- ${fmtMXN(b.familyDiscount)}</td>
                 </tr>`
              : ""
          }
          <tr>
            <td>Coberturas Adicionales Seleccionadas (Cero Deducible Acc., Dental, etc.)</td>
            <td style="text-align:right; font-weight:700;">${fmtMXN(b.ridersCost)}</td>
          </tr>
          <tr>
            <td>Derecho de Póliza + IVA (16%)</td>
            <td style="text-align:right; font-weight:700;">${fmtMXN(Number(b.policyFee || 1350) + Number(b.iva || 0))}</td>
          </tr>
          <tr style="background:var(--atlas-blue-soft); font-weight:800; color:var(--atlas-blue-deep);">
            <td>Prima Total Anualizada Consolidable</td>
            <td style="text-align:right;">${fmtMXN(q.annualPremium)} MXN</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Assigned Professional Seguros Atlas Agent Card -->
    <div class="agent-assigned-card">
      <div style="font-size:0.74rem; font-weight:800; text-transform:uppercase; color:#B45309; margin-bottom:0.45rem;">
        🤝 Agente Profesional Certificado de Seguros Atlas Asignado
      </div>
      <div class="agent-header">
        <div class="agent-avatar">${ag.avatar_initials || "SA"}</div>
        <div>
          <strong style="font-size:1.05rem; color:var(--atlas-blue-deep); display:block;">${ag.name}</strong>
          <span style="font-size:0.8rem; color:var(--atlas-slate-dark); display:block;">${ag.title || ag.specialty}</span>
          <span style="font-size:0.76rem; color:var(--atlas-blue-dark); font-weight:700;">
            Cédula Oficial: ${ag.cedula} · 📍 ${ag.branch}
          </span>
        </div>
      </div>
      <p style="font-size:0.81rem; color:var(--atlas-text); margin-bottom:0.8rem;">
        ${ag.bio || "Especialista certificado por la CNSF para acompañarte en la contratación, endosos y atención de siniestros."}
      </p>
      <div style="display:flex; gap:0.6rem; flex-wrap:wrap;">
        <a href="tel:${(ag.phone || "5591775220").replace(/\D/g, "")}" class="btn btn-executive" style="font-size:0.78rem; padding:0.45rem 0.9rem;">
          📞 Llamar: ${ag.phone}
        </a>
        <a href="mailto:${ag.email}?subject=Cotización%20Seguros%20Atlas%20${q.folio}" class="btn btn-orange" style="font-size:0.78rem; padding:0.45rem 0.9rem;">
          ✉️ Contactar a mi Agente (${ag.email})
        </a>
      </div>
    </div>
  `;
}

/* ============================================================================
 * Paso 5: Tablero Directivo (Executive BI Dashboard) with Chart.js
 * ========================================================================== */
async function loadDashboardData() {
  try {
    const res = await fetch("/api/dashboard");
    DASHBOARD_DATA = await res.json();
    renderExecutiveDashboard();
  } catch (err) {
    console.error("Error loading executive dashboard:", err);
  }
}

function renderExecutiveDashboard() {
  if (!DASHBOARD_DATA) return;
  const kpis = DASHBOARD_DATA.kpis || {};

  document.getElementById("kpiTotalAnnualPotential").textContent = fmtMXN(
    kpis.totalAnnualPotentialMXN
  );
  document.getElementById("kpiTotalMonthlyPotential").textContent = fmtMXN(
    kpis.totalMonthlyPotentialMXN
  );
  document.getElementById("kpiTotalQuotes").textContent = Number(
    kpis.totalQuotes || 0
  ).toLocaleString("es-MX");
  document.getElementById("kpiTotalLives").textContent = `${
    kpis.totalInsuredLives || 0
  } vidas asegurables en pipeline`;
  document.getElementById("kpiAvgTicket").textContent = fmtMXN(kpis.avgAnnualTicketMXN);
  document.getElementById("kpiConversionRate").textContent = `Prima Emitida Confirmada: ${fmtMXN(
    kpis.issuedAnnualPremiumMXN
  )}`;

  // 1. Plan Summary Table
  const planBody = document.getElementById("dashPlanSummaryBody");
  if (planBody) {
    planBody.innerHTML = (DASHBOARD_DATA.byPlan || [])
      .map(
        (p) => `
      <tr>
        <td>
          <span style="display:inline-block; width:10px; height:10px; border-radius:50%; background:${p.color}; margin-right:6px;"></span>
          <strong>${p.planName}</strong>
        </td>
        <td><strong>${p.quotesCount}</strong></td>
        <td>${fmtMXN(p.avgPremiumMXN)}</td>
        <td style="font-weight:800; color:var(--atlas-blue-deep);">${fmtMXN(p.annualPotentialMXN)}</td>
      </tr>
    `
      )
      .join("");
  }

  // 2. Agent Summary Table
  const agentBody = document.getElementById("dashAgentSummaryBody");
  if (agentBody) {
    agentBody.innerHTML = (DASHBOARD_DATA.byAgent || [])
      .map(
        (a) => `
      <tr>
        <td><strong>${a.agentName}</strong></td>
        <td><small>${a.branch}</small></td>
        <td><strong>${a.quotesCount}</strong></td>
        <td style="font-weight:800; color:var(--atlas-blue-deep);">${fmtMXN(a.annualPotentialMXN)}</td>
      </tr>
    `
      )
      .join("");
  }

  // 3. Recent Quotes Table
  renderRecentQuotesTable();

  // 4. Render Charts
  renderDashboardCharts();
}

function renderRecentQuotesTable() {
  if (!DASHBOARD_DATA) return;
  const filterVal = document.getElementById("dashFilterPlan")?.value || "ALL";
  const tbody = document.getElementById("dashRecentQuotesBody");
  if (!tbody) return;

  const list = (DASHBOARD_DATA.recentQuotes || []).filter(
    (q) => filterVal === "ALL" || q.planId === filterVal
  );

  tbody.innerHTML = list
    .map(
      (q) => `
    <tr>
      <td><code style="font-weight:700; color:var(--atlas-blue-deep);">${q.folio}</code></td>
      <td>${q.dateKey || ""}</td>
      <td>
        <strong>${escapeHtml(q.titularName)}</strong><br/>
        <small style="color:var(--atlas-text-muted);">${q.titularAge} años · ${1 + Number(q.dependentsCount || 0)} asegurado(s) · ${q.state || "CDMX"}</small>
      </td>
      <td><strong>${q.planName}</strong></td>
      <td>$${Number(q.deductible || 25000).toLocaleString()} / ${q.coinsurance || 10}%</td>
      <td><small>${q.assignedAgentName || "Agente Atlas"}</small></td>
      <td>
        <span style="font-size:0.72rem; padding:0.18rem 0.55rem; border-radius:999px; background:${
          q.source === "agente_gemini" ? "#E8F0FE" : "var(--atlas-orange-soft)"
        }; font-weight:700;">
          ${q.source === "agente_gemini" ? "🤖 Gemini AI" : "🧮 Cotizador Web"}
        </span>
      </td>
      <td>${fmtMXN(q.monthlyPremium)}</td>
      <td style="font-weight:800; color:var(--atlas-blue-deep);">${fmtMXN(q.annualPremium)}</td>
    </tr>
  `
    )
    .join("");
}

function renderDashboardCharts() {
  if (typeof Chart === "undefined" || !DASHBOARD_DATA) return;

  const daily = DASHBOARD_DATA.dailySeries || [];
  const labels = daily.map((d) => d.dateKey);

  const planMeta = [
    { id: "med-optimo", label: "Med Óptimo", color: "#508CBE" },
    { id: "med-plus", label: "Med Plus", color: "#FAA632" },
    { id: "med-plus-elite", label: "Med Plus Elite", color: "#6F6259" },
    { id: "plan-mundial", label: "Plan Mundial", color: "#D9272E" },
    { id: "med-optimo-empresas", label: "Óptimo Empresas", color: "#0D9488" },
    { id: "med-plus-empresas", label: "Plus Empresas", color: "#7C3AED" },
    { id: "basicos-estandarizados", label: "Básico Estand.", color: "#64748B" },
  ];

  const stackedDatasets = planMeta.map((pm) => ({
    type: "bar",
    label: pm.label,
    data: daily.map((d) => (d.byPlanCount && d.byPlanCount[pm.id]) || 0),
    backgroundColor: pm.color,
    stack: "quotesStack",
    yAxisID: "yQuotes",
    borderRadius: 4,
  }));

  stackedDatasets.push({
    type: "line",
    label: "Potencial Diario (MXN)",
    data: daily.map((d) => d.totalAnnualPotential || 0),
    borderColor: "#183B5B",
    backgroundColor: "rgba(24, 59, 91, 0.12)",
    borderWidth: 2.5,
    tension: 0.3,
    yAxisID: "yAmount",
  });

  const ctxDaily = document.getElementById("chartDailyQuotes");
  if (ctxDaily) {
    if (chartDailyInstance) chartDailyInstance.destroy();
    chartDailyInstance = new Chart(ctxDaily, {
      data: { labels, datasets: stackedDatasets },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: { mode: "index", intersect: false },
        scales: {
          x: { stacked: true },
          yQuotes: {
            type: "linear",
            position: "left",
            stacked: true,
            title: { display: true, text: "N° de Cotizaciones" },
            ticks: { stepSize: 1 },
          },
          yAmount: {
            type: "linear",
            position: "right",
            grid: { drawOnChartArea: false },
            title: { display: true, text: "Potencial Anual (MXN)" },
          },
        },
      },
    });
  }

  const byPlan = (DASHBOARD_DATA.byPlan || []).filter((p) => p.annualPotentialMXN > 0);
  const ctxPlan = document.getElementById("chartPlanPotential");
  if (ctxPlan) {
    if (chartPlanInstance) chartPlanInstance.destroy();
    chartPlanInstance = new Chart(ctxPlan, {
      type: "doughnut",
      data: {
        labels: byPlan.map((p) => p.planName),
        datasets: [
          {
            data: byPlan.map((p) => p.annualPotentialMXN),
            backgroundColor: byPlan.map((p) => p.color),
            borderWidth: 2,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: "bottom" },
        },
      },
    });
  }
}

/* ============================================================================
 * Helpers
 * ========================================================================== */
function escapeHtml(str) {
  return String(str || "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function formatSimpleMarkdown(text) {
  let html = escapeHtml(text);
  html = html.replace(/^### (.*$)/gm, '<h4 style="color:var(--atlas-blue-deep); margin:0.5rem 0 0.25rem;">$1</h4>');
  html = html.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
  html = html.replace(/\*(.*?)\*/g, "<em>$1</em>");
  html = html.replace(/`(.*?)`/g, '<code style="background:#EEF2F6; padding:0.1rem 0.35rem; border-radius:4px; font-weight:700;">$1</code>');
  html = html.replace(/\n/g, "<br/>");
  return html;
}
