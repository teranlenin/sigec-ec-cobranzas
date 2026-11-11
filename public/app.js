/**
 * SIGEC-EC v2.0 - Web Edition (Vercel Static SPA)
 * Motor interactivo de analítica, neurocobranza, simulación estocástica y trazabilidad.
 */

const fmtUSD = (val) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(val || 0);
const fmtInt = (val) => new Intl.NumberFormat('en-US').format(Math.round(val || 0));
const fmtPct = (val) => `${((val || 0) * 100).toFixed(1)}%`;

const state = {
  master: [],
  filtered: [],
  activeMod: 'mod1',
  visitasLog: JSON.parse(localStorage.getItem('sigec_visitas_log') || '[]')
};

const $ = (id) => document.getElementById(id);

function escapeHtml(str) {
  return String(str ?? '')
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;');
}

function downloadFile(filename, content, mime) {
  const blob = new Blob([content], { type: mime });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

function toCsv(rows, columns) {
  const header = columns.join(',');
  const lines = rows.map(r => columns.map(c => `"${String(r[c] ?? '').replaceAll('"', '""')}"`).join(','));
  return '\uFEFF' + [header, ...lines].join('\n');
}

function setupTabs(btnSelector, paneSelector, onSwitch) {
  const btns = document.querySelectorAll(btnSelector);
  const panes = document.querySelectorAll(paneSelector);
  btns.forEach(btn => {
    btn.addEventListener('click', () => {
      btns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      const target = btn.dataset.tab;
      panes.forEach(p => p.classList.toggle('hidden', p.id !== target));
      if (onSwitch) onSwitch(target);
    });
  });
}

function populateFilters() {
  const fillSelect = (id, allLabel, values) => {
    const el = $(id);
    el.innerHTML = `<option value="Todos">${allLabel}</option>` +
      values.sort().map(v => `<option value="${escapeHtml(v)}">${escapeHtml(v)}</option>`).join('');
  };
  fillSelect('fltBalde', 'Todos', [...new Set(state.master.map(d => d.bucket_mora))]);
  fillSelect('fltParroquia', 'Todas', [...new Set(state.master.map(d => d.parroquia_dm_quito))]);
  fillSelect('fltSector', 'Todos', [...new Set(state.master.map(d => d.sector_productivo))]);

  const caseOpts = state.master.map(d =>
    `<option value="${d.id_caso}">${d.id_caso} — ${escapeHtml(d.sector_productivo)} (${fmtUSD(d.saldo_usd)})</option>`
  ).join('');
  $('cockpitSelect').innerHTML = caseOpts;
  $('cockpitSelect').value = 'SIM-00004';
  $('auditClientSelect').innerHTML = caseOpts;
  $('auditClientSelect').value = 'SIM-00004';
  $('exportSelect').innerHTML = caseOpts;
  $('exportSelect').value = 'SIM-00001';
}

function applyGlobalFilters() {
  const balde = $('fltBalde').value;
  const parroquia = $('fltParroquia').value;
  const sector = $('fltSector').value;
  const presc = $('fltPresc').value;

  state.filtered = state.master.filter(d => {
    if (balde !== 'Todos' && d.bucket_mora !== balde) return false;
    if (parroquia !== 'Todos' && d.parroquia_dm_quito !== parroquia) return false;
    if (sector !== 'Todos' && d.sector_productivo !== sector) return false;
    if (presc === 'Alertas' && !String(d.estado_prescripcion).includes('Alerta')) return false;
    if (presc === 'Vigente' && String(d.estado_prescripcion).includes('Alerta')) return false;
    return true;
  });

  const totalSaldo = state.filtered.reduce((s, d) => s + d.saldo_usd, 0);
  $('sideCount').textContent = fmtInt(state.filtered.length);
  $('sideSaldo').textContent = fmtUSD(totalSaldo);

  renderActiveModule();
}

function renderActiveModule() {
  if (state.activeMod === 'mod1') renderDashboard();
  else if (state.activeMod === 'mod2') renderExplorador();
  else if (state.activeMod === 'mod3') renderCockpit();
  else if (state.activeMod === 'mod4') renderRutas();
  else if (state.activeMod === 'mod5') renderStochastic();
  else if (state.activeMod === 'mod6') renderFoda();
  else if (state.activeMod === 'mod7') renderExportMd();
}

/* ---------------- MOD 1: DASHBOARD ---------------- */
function renderDashboard() {
  const data = state.filtered;
  const saldoTot = data.reduce((s, d) => s + d.saldo_usd, 0);
  const recupTot = data.reduce((s, d) => s + d.recuperacion_esperada_30d_usd, 0);
  const visitasCnt = data.filter(d => d.elegible_visita_campo).length;
  const bloqCnt = data.filter(d => d.bloqueo_legal).length;

  $('kpiGrid').innerHTML = [
    ['Saldo Cartera Total', fmtUSD(saldoTot).replace('.00', ''), 'USD exigibles al corte', 'text-navy-800'],
    ['Recuperación Esp. 30d', fmtUSD(recupTot).replace('.00', ''), 'Valor esperado neto', 'text-tealbrand-600'],
    ['Cuentas Auditadas', fmtInt(data.length), 'Casos activos en universo', 'text-navy-800'],
    ['Ruta de Campo (Visitas)', fmtInt(visitasCnt), 'Saldos ≥ $3k o alertas', 'text-navy-700'],
    ['Bloqueo Normativo', fmtInt(bloqCnt), 'Disputas / LOPDP revisión', 'text-red-600']
  ].map(([t, v, c, cls]) => `
    <div class="metric-card">
      <div class="text-[11px] font-bold uppercase tracking-wider text-slate-500">${t}</div>
      <div class="text-2xl font-extrabold ${cls} mt-1">${v}</div>
      <div class="text-xs text-slate-500 mt-1">${c}</div>
    </div>
  `).join('');

  // Aging buckets stacked bar
  const bucketsMap = {};
  data.forEach(d => {
    if (!bucketsMap[d.bucket_mora]) bucketsMap[d.bucket_mora] = { cap: 0, mora: 0 };
    bucketsMap[d.bucket_mora].cap += d.capital_total_usd;
    bucketsMap[d.bucket_mora].mora += d.interes_mora_usd;
  });
  const bKeys = Object.keys(bucketsMap).sort();
  Plotly.newPlot('chartBuckets', [
    { x: bKeys, y: bKeys.map(k => bucketsMap[k].cap), name: 'Capital Exigible', type: 'bar', marker: { color: '#1A365D' } },
    { x: bKeys, y: bKeys.map(k => bucketsMap[k].mora), name: 'Interés de Mora', type: 'bar', marker: { color: '#0D9488' } }
  ], { barmode: 'stack', margin: { t: 10, b: 60, l: 55, r: 15 }, legend: { orientation: 'h', y: 1.1 } }, { responsive: true });

  // Donut perfiles
  const perfMap = {};
  data.forEach(d => { perfMap[d.perfil_conductual_observado] = (perfMap[d.perfil_conductual_observado] || 0) + 1; });
  Plotly.newPlot('chartPerfiles', [{
    labels: Object.keys(perfMap),
    values: Object.values(perfMap),
    type: 'pie',
    hole: 0.48,
    marker: { colors: ['#2B6CB0', '#0D9488', '#DD6B20', '#E53E3E'] }
  }], { margin: { t: 10, b: 20, l: 10, r: 10 }, showlegend: false }, { responsive: true });

  // Parroquias H-bar
  const parrMap = {};
  data.forEach(d => { parrMap[d.parroquia_dm_quito] = (parrMap[d.parroquia_dm_quito] || 0) + d.saldo_usd; });
  const parrEntries = Object.entries(parrMap).sort((a, b) => a[1] - b[1]);
  Plotly.newPlot('chartParroquias', [{
    x: parrEntries.map(e => e[1]),
    y: parrEntries.map(e => e[0]),
    type: 'bar',
    orientation: 'h',
    marker: { color: '#2B6CB0' }
  }], { margin: { t: 10, b: 40, l: 115, r: 20 }, xaxis: { title: 'Saldo USD' } }, { responsive: true });

  // Scatter Mora vs Saldo
  Plotly.newPlot('chartScatter', [{
    x: data.map(d => d.dias_mora),
    y: data.map(d => d.saldo_usd),
    text: data.map(d => `${d.id_caso} | ${d.sector_productivo} | ${d.parroquia_dm_quito}`),
    mode: 'markers',
    marker: {
      color: data.map(d => d.prob_pago_30d_calibrada),
      colorscale: 'Tealgrn',
      size: 6,
      showscale: true,
      colorbar: { title: 'Prob.' }
    },
    type: 'scatter'
  }], { margin: { t: 10, b: 45, l: 55, r: 10 }, xaxis: { title: 'Días de Mora' }, yaxis: { title: 'Saldo USD' } }, { responsive: true });
}

/* ---------------- MOD 2: EXPLORADOR ---------------- */
function renderExplorador() {
  const q = ($('searchTableInput').value || '').trim().toLowerCase();
  const hab = state.filtered.filter(d => !d.bloqueo_legal && (
    !q || d.id_caso.toLowerCase().includes(q) || d.parroquia_dm_quito.toLowerCase().includes(q) || d.sector_productivo.toLowerCase().includes(q)
  ));
  $('habCountLbl').textContent = `Mostrando ${hab.length} casos habilitados (primeros 200 en tabla)`;
  $('tbodyHabilitados').innerHTML = hab.slice(0, 200).map(d => `
    <tr class="hover:bg-slate-50">
      <td class="p-2 font-bold text-navy-800">${d.id_caso}</td>
      <td class="p-2">${escapeHtml(d.parroquia_dm_quito)}</td>
      <td class="p-2">${escapeHtml(d.sector_productivo)}</td>
      <td class="p-2 text-right font-semibold">${fmtUSD(d.saldo_usd)}</td>
      <td class="p-2 text-right">${d.dias_mora} d</td>
      <td class="p-2">${escapeHtml(d.bucket_mora)}</td>
      <td class="p-2">${escapeHtml(d.perfil_conductual_observado)}</td>
      <td class="p-2 text-right font-semibold text-tealbrand-600">${fmtPct(d.prob_pago_30d_calibrada)}</td>
      <td class="p-2">${escapeHtml(d.via_procesal_idonea)}</td>
    </tr>
  `).join('');

  const bloq = state.filtered.filter(d => d.bloqueo_legal);
  $('tbodyBloqueados').innerHTML = bloq.map(d => `
    <tr class="hover:bg-red-50/40">
      <td class="p-2 font-bold text-red-700">${d.id_caso}</td>
      <td class="p-2">${escapeHtml(d.parroquia_dm_quito)}</td>
      <td class="p-2">${escapeHtml(d.sector_productivo)}</td>
      <td class="p-2 text-right font-semibold">${fmtUSD(d.saldo_usd)}</td>
      <td class="p-2">${escapeHtml(d.bucket_mora)}</td>
      <td class="p-2 text-red-700 font-semibold">${escapeHtml(d.disputa_saldo)}</td>
      <td class="p-2">${escapeHtml(d.consentimiento_contacto_simulado)}</td>
      <td class="p-2">${escapeHtml(d.motivo_declarado)}</td>
    </tr>
  `).join('');

  const presc = state.filtered.filter(d => String(d.estado_prescripcion).includes('Alerta'))
    .sort((a, b) => a.dias_para_prescripcion_cambiaria - b.dias_para_prescripcion_cambiaria);
  const prescSaldo = presc.reduce((s, d) => s + d.saldo_usd, 0);
  $('prescSummaryBanner').innerHTML = `Se identifican <strong>${presc.length} cuentas en riesgo de prescripción</strong> con saldo acumulado de <strong>${fmtUSD(prescSaldo)}</strong>. Requieren acción procesal o novación para interrumpir el cómputo de 3 años (Art. 479 Código de Comercio).`;
  $('tbodyPrescripcion').innerHTML = presc.map(d => `
    <tr class="hover:bg-amber-50/50">
      <td class="p-2 font-bold text-navy-800">${d.id_caso}</td>
      <td class="p-2">${escapeHtml(d.parroquia_dm_quito)}</td>
      <td class="p-2">${escapeHtml(d.sector_productivo)}</td>
      <td class="p-2 text-right font-semibold">${fmtUSD(d.saldo_usd)}</td>
      <td class="p-2 text-right">${d.dias_mora}</td>
      <td class="p-2 text-right font-bold text-red-600">${d.dias_para_prescripcion_cambiaria} d</td>
      <td class="p-2">${escapeHtml(d.estado_prescripcion)}</td>
      <td class="p-2">${escapeHtml(d.titulo_ejecutivo_tipo)}</td>
    </tr>
  `).join('');
}

/* ---------------- MOD 3: COCKPIT 1 A 1 ---------------- */
function renderCockpit() {
  const id = $('cockpitSelect').value;
  const c = state.master.find(d => d.id_caso === id);
  if (!c) return;

  if (c.bloqueo_legal) {
    $('cockpitBody').innerHTML = `
      <div class="bg-red-50 border-l-4 border-red-600 p-5 rounded-xl text-red-900 space-y-2 shadow-sm">
        <h3 class="text-lg font-extrabold">🛑 CUENTA BLOQUEADA POR COMPLIANCE NORMATIVO</h3>
        <p class="text-sm"><strong>Causa:</strong> Disputa de saldo (${escapeHtml(c.disputa_saldo)}) o Consentimiento LOPDP (${escapeHtml(c.consentimiento_contacto_simulado)}).</p>
        <p class="text-sm"><strong>Mandato:</strong> Abstención absoluta de cobro. Derivar expediente a la Unidad de Liquidación y Servicio al Cliente.</p>
      </div>`;
    return;
  }

  const prescColor = c.dias_para_prescripcion_cambiaria < 180 ? 'text-red-600' : (c.dias_para_prescripcion_cambiaria < 365 ? 'text-amber-600' : 'text-emerald-700');
  const waHref = `https://api.whatsapp.com/send?text=${encodeURIComponent(c.mensaje_whatsapp_personalizado)}`;

  $('cockpitBody').innerHTML = `
    <h3 class="text-lg font-bold text-navy-800">Ficha Técnica 360°: ${c.id_caso} — ${escapeHtml(c.parroquia_dm_quito)}</h3>
    <div class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
      <div class="metric-card">
        <div class="text-[11px] font-bold uppercase text-slate-500">Identificación y Actividad</div>
        <div class="text-base font-bold text-navy-800 mt-1">${escapeHtml(c.tipo_deudor)}</div>
        <div class="text-xs text-slate-600 mt-2 space-y-0.5">
          <div><strong>Sector:</strong> ${escapeHtml(c.sector_productivo)}</div>
          <div><strong>Producto:</strong> ${escapeHtml(c.producto)}</div>
          <div><strong>Edad:</strong> ${c.edad} años</div>
        </div>
      </div>
      <div class="metric-card">
        <div class="text-[11px] font-bold uppercase text-slate-500">Estado Financiero Auditado</div>
        <div class="text-2xl font-extrabold text-navy-800 mt-1">${fmtUSD(c.saldo_usd)}</div>
        <div class="text-xs text-slate-600 mt-2 space-y-0.5">
          <div><strong>Capital:</strong> ${fmtUSD(c.capital_total_usd)}</div>
          <div><strong>Interés Mora:</strong> ${fmtUSD(c.interes_mora_usd)}</div>
          <div><strong>Gastos Cobro:</strong> ${fmtUSD(c.gastos_cobranza_usd)}</div>
        </div>
      </div>
      <div class="metric-card">
        <div class="text-[11px] font-bold uppercase text-slate-500">Diagnóstico Procesal COGEP</div>
        <div class="text-base font-bold ${prescColor} mt-1">Prescripción: ${c.dias_para_prescripcion_cambiaria} días</div>
        <div class="text-xs text-slate-600 mt-2 space-y-0.5">
          <div><strong>Título:</strong> ${escapeHtml(c.titulo_ejecutivo_tipo).slice(0, 38)}...</div>
          <div><strong>Vía:</strong> ${escapeHtml(c.via_procesal_idonea)}</div>
          <div><strong>LTV Garantía:</strong> ${Number(c.ltv_ratio).toFixed(2)}</div>
        </div>
      </div>
      <div class="metric-card">
        <div class="text-[11px] font-bold uppercase text-slate-500">Perfil Conductual Observado</div>
        <div class="text-sm font-bold text-navy-700 mt-1">${escapeHtml(c.perfil_conductual_observado)}</div>
        <div class="text-xs text-slate-600 mt-2 space-y-0.5">
          <div><strong>Kept Rate:</strong> ${fmtPct(c.ratio_cumplimiento_promesas)}</div>
          <div><strong>Últ. Respuesta:</strong> ${escapeHtml(c.respuesta_ultimo_contacto)}</div>
          <div><strong>Canal Óptimo:</strong> ${escapeHtml(c.canal_predilecto_neuroperfil).slice(0, 32)}</div>
        </div>
      </div>
    </div>

    <div class="bg-white rounded-xl border border-slate-200 p-5 shadow-sm space-y-4">
      <h3 class="font-bold text-navy-800 text-base">🪜 Simulador Interactivo de Negociación: Escalera de Resolución</h3>
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-5 text-xs">
        <div class="border border-slate-200 rounded-lg p-4 bg-slate-50 space-y-2">
          <div class="font-bold text-navy-800 text-sm">Nivel 1: Condonación por Pago Inmediato (48h)</div>
          <label class="block font-semibold">Condonación Mora y Gastos: <span id="lblCondPct">100%</span></label>
          <input id="slCondPct" type="range" min="0" max="100" step="10" value="100" class="w-full accent-tealbrand-600" />
          <div id="resNivel1" class="bg-white p-3 rounded border border-slate-200"></div>
        </div>
        <div class="border border-slate-200 rounded-lg p-4 bg-slate-50 space-y-2">
          <div class="font-bold text-navy-800 text-sm">Nivel 2: Compromiso Blindado (Abono Inicial 72h)</div>
          <div class="flex gap-3">
            <div class="flex-1">
              <label class="block font-semibold">Abono inicial: <span id="lblAbonoPct">30%</span></label>
              <input id="slAbonoPct" type="range" min="15" max="50" step="5" value="30" class="w-full accent-tealbrand-600" />
            </div>
            <div>
              <label class="block font-semibold">Cuotas saldo</label>
              <select id="selCuotasSaldo" class="border border-slate-300 rounded px-2 py-1 bg-white"><option>2</option><option selected>3</option><option>4</option></select>
            </div>
          </div>
          <div id="resNivel2" class="bg-white p-3 rounded border border-slate-200"></div>
        </div>
        <div class="border border-slate-200 rounded-lg p-4 bg-slate-50 space-y-2">
          <div class="font-bold text-navy-800 text-sm">Nivel 3: Reestructuración Flujo MYPE (Sistema Francés)</div>
          <div class="flex gap-3">
            <div class="flex-1">
              <label class="block font-semibold">Plazo (meses)</label>
              <select id="selPlazoMeses" class="w-full border border-slate-300 rounded px-2 py-1 bg-white"><option>6</option><option selected>12</option><option>18</option><option>24</option></select>
            </div>
            <div class="flex-1">
              <label class="block font-semibold">Tasa Anual (%)</label>
              <input id="inpTasaAnual" type="number" step="0.5" value="15.5" class="w-full border border-slate-300 rounded px-2 py-1 bg-white" />
            </div>
          </div>
          <div id="resNivel3" class="bg-white p-3 rounded border border-slate-200"></div>
        </div>
        <div class="border border-amber-200 rounded-lg p-4 bg-amber-50 space-y-2">
          <div class="font-bold text-amber-900 text-sm">Nivel 4: Escalado Prejudicial Formal (COGEP)</div>
          <div><strong>Vía Aplicable:</strong> ${escapeHtml(c.via_procesal_idonea)}</div>
          <div><strong>Medida Cautelar (Art. 351):</strong> ${escapeHtml(c.medida_cautelar_aplicable)}</div>
          <div class="bg-white p-2.5 rounded border border-amber-200 font-mono text-[11px] text-slate-700">
            REQUERIMIENTO PREJUDICIAL ${c.id_caso}: Saldo exigible ${fmtUSD(c.saldo_usd)} amparado en ${escapeHtml(c.titulo_ejecutivo_tipo)}.
          </div>
        </div>
      </div>
    </div>

    <div class="bg-white rounded-xl border border-slate-200 p-5 shadow-sm space-y-4">
      <h3 class="font-bold text-navy-800 text-base">📞 Guion de Gestión en 6 Pasos &amp; Simulador de Objeciones</h3>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
        <div class="space-y-2">
          <div class="p-3 rounded bg-slate-50 border border-slate-200"><strong>Paso 1 (Pre-llamada):</strong> Saldo ${fmtUSD(c.saldo_usd)} | Mora ${c.dias_mora} d | Título: ${escapeHtml(c.titulo_ejecutivo_tipo)}</div>
          <div class="p-3 rounded bg-blue-50 border border-blue-200"><strong>Paso 2 (Apertura):</strong> "Buenos días estimado/a, le saluda su asesor de ${escapeHtml(c.producto)} para acercarle una solución financiera personalizada para su negocio."</div>
          <div class="p-3 rounded bg-slate-50 border border-slate-200"><strong>Paso 3 (Validación LOPDP):</strong> "¿Me confirma por favor los 4 últimos dígitos de su RUC o cédula antes de revisar el detalle?"</div>
        </div>
        <div class="space-y-2">
          <div class="p-3 rounded bg-teal-50 border border-teal-200"><strong>Paso 4 (Propuesta Alta Velocidad):</strong> ${escapeHtml(c.estrategia_recuperacion_maxima)}</div>
          <div class="p-3 rounded bg-slate-50 border border-slate-200 space-y-1.5">
            <strong>Paso 5 (Simulador de Objeción MYPE):</strong>
            <select id="selObjecion" class="w-full border border-slate-300 rounded px-2 py-1 bg-white">
              <option value="ventas">No tengo dinero / Las ventas están en cero</option>
              <option value="planilla">Un contratista / Municipio no me paga la planilla</option>
              <option value="intereses">Intereses y recargos muy altos</option>
              <option value="semana">Llámenme la otra semana</option>
            </select>
            <div id="objecionResp" class="p-2 rounded bg-emerald-50 border border-emerald-200 text-emerald-900 font-medium"></div>
          </div>
          <div class="p-3 rounded bg-amber-50 border border-amber-200"><strong>Paso 6 (Cierre Firme):</strong> Pactar monto exacto + fecha/hora límite + canal de depósito + foto de comprobante.</div>
        </div>
      </div>
    </div>

    <div class="bg-white rounded-xl border border-slate-200 p-5 shadow-sm space-y-3">
      <div class="flex flex-wrap items-center justify-between gap-2">
        <h3 class="font-bold text-navy-800 text-base">💬 Mensaje Digital (WhatsApp / SMS)</h3>
        <a href="${waHref}" target="_blank" rel="noopener" class="px-4 py-2 rounded-lg bg-emerald-600 text-white text-xs font-bold hover:bg-emerald-700">📲 Abrir en WhatsApp Web</a>
      </div>
      <textarea readonly rows="3" class="w-full border border-slate-300 rounded-lg p-3 text-xs bg-slate-50">${escapeHtml(c.mensaje_whatsapp_personalizado)}</textarea>
    </div>
  `;

  const updateSliders = () => {
    const condPct = Number($('slCondPct').value);
    $('lblCondPct').textContent = `${condPct}%`;
    const descUsd = (c.interes_mora_usd + c.gastos_cobranza_usd) * (condPct / 100);
    const neto = c.saldo_usd - descUsd;
    $('resNivel1').innerHTML = `<div>Ahorro cliente: <strong class="text-tealbrand-600">${fmtUSD(descUsd)}</strong></div><div>Pago neto en 48h: <strong class="text-navy-800 text-sm">${fmtUSD(neto)}</strong></div>`;

    const abonoPct = Number($('slAbonoPct').value);
    const nCuotas = Number($('selCuotasSaldo').value);
    $('lblAbonoPct').textContent = `${abonoPct}%`;
    const abonoUsd = c.saldo_usd * (abonoPct / 100);
    const cuotaRem = (c.saldo_usd - abonoUsd) / nCuotas;
    $('resNivel2').innerHTML = `<div>Abono inicial (72h): <strong class="text-navy-800">${fmtUSD(abonoUsd)}</strong></div><div>${nCuotas} cuotas de: <strong class="text-tealbrand-600">${fmtUSD(cuotaRem)}</strong></div>`;

    const meses = Number($('selPlazoMeses').value);
    const tasaMens = (Number($('inpTasaAnual').value) / 100) / 12;
    const capReest = c.capital_total_usd + c.interes_corriente_usd;
    const cuotaFr = tasaMens > 0 ? (capReest * tasaMens) / (1 - Math.pow(1 + tasaMens, -meses)) : capReest / meses;
    $('resNivel3').innerHTML = `<div>Capital + Int. Ord.: <strong>${fmtUSD(capReest)}</strong></div><div>Cuota mensual fija (${meses}m): <strong class="text-navy-800 text-sm">${fmtUSD(cuotaFr)}</strong></div>`;
  };
  ['slCondPct', 'slAbonoPct', 'selCuotasSaldo', 'selPlazoMeses', 'inpTasaAnual'].forEach(el => $(el).addEventListener('input', updateSliders));
  updateSliders();

  const objMap = {
    ventas: "Táctica: 'Entiendo el bache de ventas de su negocio. No le pido liquidar todo hoy; acordemos un abono mínimo de arranque para congelar recargos.'",
    planilla: "Táctica: 'Sabemos de las demoras institucionales. Facilítenos copia de la factura radicada y pactamos un abono inicial simbólico mientras liquida.'",
    intereses: "Táctica: 'Aquí tiene el desglose exacto de su capital. Si cancela el capital esta semana, tramitamos la condonación total de la mora acumulada.'",
    semana: "Táctica: 'Si lo dejamos abierto para la otra semana el sistema escala el expediente. Dejemos pactado hoy un valor realista con fecha fija.'"
  };
  const updateObj = () => { $('objecionResp').textContent = objMap[$('selObjecion').value]; };
  $('selObjecion').addEventListener('change', updateObj);
  updateObj();
}

/* ---------------- MOD 4: RUTAS DE CAMPO ---------------- */
function renderRutas() {
  const rutasAll = state.master.filter(d => d.elegible_visita_campo);
  const parrSel = $('rutaParroquiaSelect');
  if (!parrSel.options.length) {
    const parrs = [...new Set(rutasAll.map(d => d.parroquia_dm_quito))].sort();
    parrSel.innerHTML = '<option value="Todas">Todas las Parroquias</option>' + parrs.map(p => `<option value="${escapeHtml(p)}">${escapeHtml(p)}</option>`).join('');
  }
  const pVal = parrSel.value || 'Todas';
  const filtradas = (pVal === 'Todas' ? rutasAll : rutasAll.filter(d => d.parroquia_dm_quito === pVal))
    .sort((a, b) => b.saldo_usd - a.saldo_usd);

  const totSaldo = rutasAll.reduce((s, d) => s + d.saldo_usd, 0);
  $('rutaKpis').innerHTML = [
    ['Clientes en Ruta de Campo', `${rutasAll.length} casos`],
    ['Saldo Total en Ruta', fmtUSD(totSaldo)],
    ['Saldo Promedio por Visita', fmtUSD(totSaldo / Math.max(1, rutasAll.length))]
  ].map(([t, v]) => `<div class="metric-card"><div class="text-[11px] font-bold uppercase text-slate-500">${t}</div><div class="text-xl font-extrabold text-navy-800 mt-1">${v}</div></div>`).join('');

  $('rutaBadgeInfo').textContent = `📍 ${filtradas.length} clientes priorizados en: ${pVal}`;

  const parrCounts = {};
  rutasAll.forEach(d => { parrCounts[d.parroquia_dm_quito] = (parrCounts[d.parroquia_dm_quito] || 0) + 1; });
  Plotly.newPlot('chartRutas', [{
    x: Object.keys(parrCounts),
    y: Object.values(parrCounts),
    type: 'bar',
    marker: { color: '#2B6CB0' }
  }], { margin: { t: 10, b: 60, l: 40, r: 10 } }, { responsive: true });

  $('tbodyRutas').innerHTML = filtradas.map(d => `
    <tr class="hover:bg-slate-50">
      <td class="p-2 font-bold text-navy-800">${d.id_caso}</td>
      <td class="p-2">${escapeHtml(d.parroquia_dm_quito)}</td>
      <td class="p-2">${escapeHtml(d.sector_productivo)}</td>
      <td class="p-2 text-right font-semibold">${fmtUSD(d.saldo_usd)}</td>
      <td class="p-2 text-right">${d.dias_mora}</td>
      <td class="p-2">${escapeHtml(d.bucket_mora)}</td>
      <td class="p-2">${escapeHtml(d.respuesta_ultimo_contacto)}</td>
      <td class="p-2">${escapeHtml(d.estado_prescripcion)}</td>
    </tr>
  `).join('');

  $('visitaCasoId').innerHTML = filtradas.map(d => `<option value="${d.id_caso}">${d.id_caso} — ${escapeHtml(d.parroquia_dm_quito)} (${fmtUSD(d.saldo_usd)})</option>`).join('');
  const today = new Date().toISOString().slice(0, 10);
  if (!$('visitaFecha').value) $('visitaFecha').value = today;
  if (!$('visitaFechaLimite').value) $('visitaFechaLimite').value = new Date(Date.now() + 3 * 86400000).toISOString().slice(0, 10);
  renderVisitasLog();
}

function renderVisitasLog() {
  if (!state.visitasLog.length) {
    $('visitaLogBox').innerHTML = '<em>Aún no se han registrado visitas de campo en esta sesión.</em>';
    return;
  }
  $('visitaLogBox').innerHTML = `<strong>Registros guardados (${state.visitasLog.length}):</strong> ` +
    state.visitasLog.slice(-5).reverse().map(v => `<span class="inline-block mr-2 px-2 py-1 rounded bg-emerald-50 border border-emerald-200 text-emerald-900 mt-1">${v.id_caso} · ${escapeHtml(v.resultado)} (${fmtUSD(v.monto_compromiso_usd)})</span>`).join('');
}

/* ---------------- MOD 5: STOCHASTIC ---------------- */
function renderStochastic() {
  const estados = ['B0', 'B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'Cura', 'Castigo'];
  const z = [
    [0.25, 0.15, 0.05, 0.01, 0.00, 0.00, 0.00, 0.54, 0.00],
    [0.10, 0.30, 0.25, 0.05, 0.01, 0.00, 0.00, 0.29, 0.00],
    [0.05, 0.10, 0.35, 0.30, 0.05, 0.01, 0.00, 0.14, 0.00],
    [0.02, 0.04, 0.10, 0.40, 0.32, 0.04, 0.00, 0.08, 0.00],
    [0.01, 0.02, 0.04, 0.10, 0.45, 0.33, 0.01, 0.04, 0.01],
    [0.00, 0.01, 0.02, 0.04, 0.10, 0.50, 0.28, 0.02, 0.03],
    [0.00, 0.00, 0.01, 0.01, 0.03, 0.05, 0.70, 0.01, 0.19],
    [0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 1.00, 0.00],
    [0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 1.00]
  ];
  Plotly.newPlot('chartMarkov', [{
    z, x: estados, y: estados, type: 'heatmap', colorscale: 'Blues',
    text: z.map(r => r.map(v => v.toFixed(2))), texttemplate: '%{text}', showscale: true
  }], { margin: { t: 20, b: 50, l: 60, r: 20 }, xaxis: { title: 'Estado t+1' }, yaxis: { title: 'Estado t', autorange: 'reversed' } }, { responsive: true });

  runMonteCarlo();
}

function runMonteCarlo() {
  const nSims = Number($('mcIter').value);
  const descPct = Number($('mcDesc').value);
  $('mcIterLbl').textContent = nSims;
  $('mcDescLbl').textContent = `${descPct}%`;

  const factorPago = 1 - (descPct / 100);
  const probs = state.master.map(d => Math.min(0.90, Math.max(0.05, d.prob_pago_30d_calibrada * (0.5 + 0.5 * d.ratio_cumplimiento_promesas))));
  const saldos = state.master.map(d => d.saldo_usd);

  // Deterministic PRNG (Mulberry32) for reproducibility
  let seed = 42;
  const rand = () => { seed |= 0; seed = seed + 0x6D2B79F5 | 0; let t = Math.imul(seed ^ seed >>> 15, 1 | seed); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; };

  const sims = [];
  for (let i = 0; i < nSims; i++) {
    let total = 0;
    for (let j = 0; j < saldos.length; j++) {
      if (rand() < probs[j]) {
        total += saldos[j] * factorPago * (0.3 + 0.7 * rand());
      }
    }
    sims.push(total);
  }

  const sorted = [...sims].sort((a, b) => a - b);
  const mean = sims.reduce((a, b) => a + b, 0) / nSims;
  const p05 = sorted[Math.floor(0.05 * nSims)];
  const p95 = sorted[Math.floor(0.95 * nSims)];

  $('mcMetrics').innerHTML = [
    ['Recuperación Media Estimada', fmtUSD(mean), 'text-navy-800'],
    ['Piso Conservador (VaR 95%)', fmtUSD(p05), 'text-red-600'],
    ['Escenario Optimista (P95)', fmtUSD(p95), 'text-tealbrand-600']
  ].map(([t, v, cls]) => `<div class="metric-card"><div class="text-[11px] font-bold uppercase text-slate-500">${t}</div><div class="text-xl font-extrabold ${cls}">${v}</div></div>`).join('');

  Plotly.newPlot('chartMonteCarlo', [{
    x: sims, type: 'histogram', nbinsx: 40, marker: { color: '#0D9488' }
  }], {
    title: `Distribución de Densidad (${nSims} Iteraciones)`,
    xaxis: { title: 'USD Recuperados en 30 Días' },
    shapes: [
      { type: 'line', x0: mean, x1: mean, y0: 0, y1: 1, yref: 'paper', line: { color: '#1A365D', dash: 'dash', width: 2 } },
      { type: 'line', x0: p05, x1: p05, y0: 0, y1: 1, yref: 'paper', line: { color: '#DC2626', dash: 'dot', width: 2 } }
    ],
    margin: { t: 40, b: 50, l: 45, r: 20 }
  }, { responsive: true });
}

/* ---------------- MOD 6: FODA & EXPLICABILIDAD ---------------- */
function pearson(xs, ys) {
  const n = xs.length;
  const mx = xs.reduce((a, b) => a + b, 0) / n;
  const my = ys.reduce((a, b) => a + b, 0) / n;
  let num = 0, dx = 0, dy = 0;
  for (let i = 0; i < n; i++) {
    const vx = xs[i] - mx, vy = ys[i] - my;
    num += vx * vy; dx += vx * vx; dy += vy * vy;
  }
  return num / Math.sqrt(dx * dy);
}

function renderFoda() {
  $('swotCardsGrid').innerHTML = `
    <div class="swot-card bg-emerald-50 border border-emerald-200 border-l-4 border-l-emerald-600">
      <div class="font-extrabold text-emerald-900 text-sm mb-2">💪 FORTALEZAS (Origen Interno / Operativo)</div>
      <ul class="list-disc pl-4 space-y-1 text-emerald-950">
        <li><strong>Cuadre Contable Perfecto (100%):</strong> $4.036.961,46 USD verificados al centavo.</li>
        <li><strong>Consentimiento Pleno LOPDP (75,9%):</strong> 759 clientes habilitados para contacto omnicanal.</li>
        <li><strong>Cartera Temprana Recuperable (53,8%):</strong> 538 cuentas B0–B2 ($1.864.952 USD).</li>
        <li><strong>Títulos Ejecutivos Formales:</strong> 250 pagarés a la orden con cláusula de aceleración (Art. 347 COGEP).</li>
      </ul>
    </div>
    <div class="swot-card bg-teal-50 border border-teal-200 border-l-4 border-l-teal-600">
      <div class="font-extrabold text-teal-900 text-sm mb-2">🚀 OPORTUNIDADES (Origen Externo / Estratégico)</div>
      <ul class="list-disc pl-4 space-y-1 text-teal-950">
        <li><strong>Potencial de Caja a 30 Días:</strong> $2.026.814,73 USD de recuperación esperada neta.</li>
        <li><strong>Apertura a Negociación:</strong> 241 clientes (24,1%) solicitaron reprogramación voluntaria.</li>
        <li><strong>Eficiencia Digital de Bajo Costo:</strong> 886 cuentas P3 aptas para autogestión y botón de pago.</li>
        <li><strong>Condonación Condicionada:</strong> $390.875 USD en mora condonables para recuperar capital en 48h.</li>
      </ul>
    </div>
    <div class="swot-card bg-amber-50 border border-amber-200 border-l-4 border-l-amber-600">
      <div class="font-extrabold text-amber-900 text-sm mb-2">⚠️ DEBILIDADES (Origen Interno / Brechas)</div>
      <ul class="list-disc pl-4 space-y-1 text-amber-950">
        <li><strong>Postergación Crónica:</strong> 325 casos registran promesas previas con 0% de cumplimiento.</li>
        <li><strong>Canal Telefónico Agotado:</strong> 161 cuentas en buzón y 96 en rechazo/evasión.</li>
        <li><strong>Kept Rate Global Insuficiente:</strong> Promedio general de cumplimiento de apenas 37,2%.</li>
        <li><strong>Monocorte Temporal:</strong> Una sola fecha de corte (2026-10-29).</li>
      </ul>
    </div>
    <div class="swot-card bg-red-50 border border-red-200 border-l-4 border-l-red-600">
      <div class="font-extrabold text-red-900 text-sm mb-2">🛑 AMENAZAS (Origen Externo / Riesgos Críticos)</div>
      <ul class="list-disc pl-4 space-y-1 text-red-950">
        <li><strong>Prescripción Cambiaria Inminente (Art. 479 C.Com):</strong> 49 cuentas ($265.594,66 USD) en alerta &lt;12m / &lt;6m.</li>
        <li><strong>Litigiosidad por Disputa:</strong> 58 cuentas ($238.412 USD) en auditoría de liquidación.</li>
        <li><strong>Inconsistencia de Títulos:</strong> 604 casos comerciales/consumo rotulados como tarjeta.</li>
        <li><strong>Rodamiento B3 a B4:</strong> 210 cuentas ($851.340 USD) al borde de cartera vencida (provisiones 35%-50%).</li>
      </ul>
    </div>
  `;

  $('swotMetricsRow').innerHTML = [
    ['Fortaleza: Temprana B0–B2', '$1,864,952', '538 cuentas (46,2% saldo)'],
    ['Oportunidad: Refinanciamiento', '241 cuentas', '24,1% apertura directa'],
    ['Debilidad: 0% Cumplimiento', '325 cuentas', 'Kept Rate = 0,0%'],
    ['Amenaza: Alerta Prescripción', '$265,595', '49 cuentas en B6']
  ].map(([t, v, s]) => `<div class="metric-card"><div class="text-[11px] font-bold uppercase text-slate-500">${t}</div><div class="text-xl font-extrabold text-navy-800 mt-1">${v}</div><div class="text-xs text-slate-500">${s}</div></div>`).join('');

  // Matriz de correlacion dinamica
  const cols = ['dias_mora', 'saldo_usd', 'capital_total_usd', 'interes_mora_usd', 'pagos_12m', 'promesas_12m', 'ratio_cumplimiento_promesas', 'prob_pago_30d_calibrada', 'recuperacion_esperada_30d_usd', 'dias_para_prescripcion_cambiaria'];
  const labels = ['Días Mora', 'Saldo USD', 'Capital', 'Int. Mora', 'Pagos 12m', 'Promesas 12m', 'Kept Rate', 'Prob. 30d', 'Recup. Esp.', 'Días Presc.'];
  const matrix = cols.map(c1 => cols.map(c2 => pearson(state.master.map(d => d[c1]), state.master.map(d => d[c2]))));

  Plotly.newPlot('chartCorr', [{
    z: matrix, x: labels, y: labels, type: 'heatmap', colorscale: 'RdBu', zmin: -1, zmax: 1, reversescale: true,
    text: matrix.map(r => r.map(v => v.toFixed(2))), texttemplate: '%{text}'
  }], { margin: { t: 20, b: 80, l: 95, r: 20 }, yaxis: { autorange: 'reversed' } }, { responsive: true });

  renderAuditClient();
}

function renderAuditClient() {
  const id = $('auditClientSelect').value;
  const c = state.master.find(d => d.id_caso === id);
  if (!c) return;

  const kept = c.promesas_12m > 0 ? c.promesas_cumplidas_12m / c.promesas_12m : 0;
  const diasPresc = 1095 - c.dias_mora;
  const ltv = c.avaluo_garantia_usd > 0 ? c.saldo_usd / c.avaluo_garantia_usd : 0;

  $('auditClientOutput').innerHTML = `
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-4 text-xs">
      <div class="bg-slate-50 border border-slate-200 rounded-lg p-4">
        <div class="font-bold text-navy-800 mb-2">1. Parámetros Brutos de Entrada (${c.id_caso})</div>
        <pre class="font-mono text-[11px] overflow-x-auto text-slate-700">${escapeHtml(JSON.stringify({
          id_caso: c.id_caso, saldo_usd: c.saldo_usd, dias_mora: c.dias_mora, bucket_mora: c.bucket_mora,
          promesas_12m: c.promesas_12m, promesas_cumplidas_12m: c.promesas_cumplidas_12m,
          respuesta_ultimo_contacto: c.respuesta_ultimo_contacto, disputa_saldo: c.disputa_saldo,
          consentimiento: c.consentimiento_contacto_simulado, avaluo_garantia_usd: c.avaluo_garantia_usd
        }, null, 2))}</pre>
      </div>
      <div class="bg-slate-50 border border-slate-200 rounded-lg p-4 space-y-3 font-mono text-[11px]">
        <div class="font-sans font-bold text-navy-800 text-xs">2. Deducción Matemática de Ratios Intermedios</div>
        <div><strong>Kept Rate:</strong> ${c.promesas_cumplidas_12m} / ${c.promesas_12m} = <strong>${kept.toFixed(2)} (${fmtPct(kept)})</strong></div>
        <div><strong>Días para Prescripción:</strong> 1.095 − ${c.dias_mora} = <strong>${diasPresc} días restantes</strong></div>
        <div><strong>LTV Garantía:</strong> ${fmtUSD(c.saldo_usd)} / ${fmtUSD(c.avaluo_garantia_usd)} = <strong>${ltv.toFixed(2)}</strong></div>
      </div>
    </div>
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
      <div class="p-4 rounded-lg ${c.bloqueo_legal ? 'bg-red-50 border border-red-200 text-red-900' : 'bg-emerald-50 border border-emerald-200 text-emerald-900'}">
        <div class="font-bold mb-1">Compuerta 1: Cumplimiento Legal</div>
        <div>${c.bloqueo_legal ? '❌ BLOQUEADO: Disputa o LOPDP en revisión.' : '✅ HABILITADO: Sin disputa y consentimiento vigente.'}</div>
      </div>
      <div class="p-4 rounded-lg bg-blue-50 border border-blue-200 text-blue-900">
        <div class="font-bold mb-1">Compuerta 2: Clasificación de Perfil</div>
        <div>🏷️ <strong>${escapeHtml(c.perfil_conductual_observado)}</strong></div>
      </div>
      <div class="p-4 rounded-lg ${c.elegible_visita_campo ? 'bg-amber-50 border border-amber-200 text-amber-900' : 'bg-slate-50 border border-slate-200 text-slate-800'}">
        <div class="font-bold mb-1">Compuerta 3: Canal Asignado</div>
        <div>${c.elegible_visita_campo ? '📍 RUTA DE CAMPO (Visita Presencial MYPE)' : '📲 CANAL DIGITAL / TELEFÓNICO'}</div>
      </div>
    </div>
  `;
}

/* ---------------- MOD 7: EXPORTADOR ---------------- */
function renderExportMd() {
  const id = $('exportSelect').value;
  const c = state.master.find(d => d.id_caso === id);
  if (!c) return;
  const md = `# EXPEDIENTE DE AUDITORÍA Y COBRANZA — CASO ${c.id_caso}
**Rótulo:** SIMULACIÓN CALIBRADA DIDÁCTICA / DATOS SINTÉTICOS.
**Fecha de Corte:** ${c.fecha_corte} · **Jurisdicción:** República del Ecuador.

## 1. Identificación y Actividad MYPE
- **Deudor:** ${c.tipo_deudor}
- **Sector Económico:** ${c.sector_productivo}
- **Ubicación:** Parroquia ${c.parroquia_dm_quito}, DM Quito
- **Producto:** ${c.producto}

## 2. Liquidación Contable Auditada
- **Saldo Total Exigible:** ${fmtUSD(c.saldo_usd)}
- **Capital Total:** ${fmtUSD(c.capital_total_usd)}
- **Interés Corriente:** ${fmtUSD(c.interes_corriente_usd)}
- **Interés de Mora Legal:** ${fmtUSD(c.interes_mora_usd)}
- **Gastos de Cobranza:** ${fmtUSD(c.gastos_cobranza_usd)}
- **Días de Mora:** ${c.dias_mora} días (${c.bucket_mora})

## 3. Diagnóstico Jurídico COGEP
- **Título:** ${c.titulo_ejecutivo_tipo}
- **Vía Procesal:** ${c.via_procesal_idonea}
- **Días para Prescripción:** ${c.dias_para_prescripcion_cambiaria} días (${c.estado_prescripcion})
- **Garantía:** ${c.garantia_declarada} (LTV: ${Number(c.ltv_ratio).toFixed(2)})

## 4. Perfil Conductual y Estrategia
- **Perfil Observado:** ${c.perfil_conductual_observado}
- **Kept Rate:** ${fmtPct(c.ratio_cumplimiento_promesas)}
- **Next Best Action:** ${c.next_best_action}

## 5. Guion Operativo
${c.guion_llamada_personalizado}
`;
  $('exportMdPreview').value = md;
}

/* ---------------- BOOTSTRAP ---------------- */
async function init() {
  const res = await fetch('/data/cartera.json');
  state.master = await res.json();
  state.filtered = [...state.master];

  $('loadingBanner').classList.add('hidden');
  $(state.activeMod).classList.remove('hidden');

  populateFilters();

  // Sidebar nav
  document.querySelectorAll('.nav-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      state.activeMod = btn.dataset.mod;
      document.querySelectorAll('.mod-section').forEach(s => s.classList.toggle('hidden', s.id !== state.activeMod));
      if (window.innerWidth < 1024) $('sidebar').classList.add('hidden');
      renderActiveModule();
    });
  });

  $('mobileMenuBtn').addEventListener('click', () => $('sidebar').classList.toggle('hidden'));

  ['fltBalde', 'fltParroquia', 'fltSector', 'fltPresc'].forEach(id => $(id).addEventListener('change', applyGlobalFilters));
  $('resetFiltersBtn').addEventListener('click', () => {
    ['fltBalde', 'fltParroquia', 'fltSector', 'fltPresc'].forEach(id => { $(id).selectedIndex = 0; });
    applyGlobalFilters();
  });

  setupTabs('.exp-tab', '.exp-pane');
  setupTabs('.stoch-tab', '.stoch-pane', (t) => { if (t === 'stochMonteCarlo') runMonteCarlo(); });
  setupTabs('.foda-tab', '.foda-pane', (t) => { if (t === 'fodaCorr') Plotly.Plots.resize('chartCorr'); });
  setupTabs('.comp-tab', '.comp-pane');

  $('searchTableInput').addEventListener('input', renderExplorador);
  $('downloadHabCsv').addEventListener('click', () => {
    const cols = ['id_caso', 'parroquia_dm_quito', 'sector_productivo', 'saldo_usd', 'dias_mora', 'bucket_mora', 'perfil_conductual_observado', 'prob_pago_30d_calibrada', 'via_procesal_idonea'];
    const rows = state.filtered.filter(d => !d.bloqueo_legal);
    downloadFile('cartera_habilitada_gestion.csv', toCsv(rows, cols), 'text/csv;charset=utf-8');
  });

  $('cockpitSelect').addEventListener('change', renderCockpit);
  $('rutaParroquiaSelect').addEventListener('change', renderRutas);
  $('visitaForm').addEventListener('submit', (e) => {
    e.preventDefault();
    state.visitasLog.push({
      id_caso: $('visitaCasoId').value,
      fecha_visita: $('visitaFecha').value,
      resultado: $('visitaResultado').value,
      monto_compromiso_usd: Number($('visitaMonto').value || 0),
      fecha_cumplimiento: $('visitaFechaLimite').value,
      observaciones: $('visitaObs').value,
      timestamp: new Date().toISOString()
    });
    localStorage.setItem('sigec_visitas_log', JSON.stringify(state.visitasLog));
    renderVisitasLog();
    $('visitaObs').value = '';
  });
  $('downloadVisitasCsv').addEventListener('click', () => {
    const cols = ['id_caso', 'fecha_visita', 'resultado', 'monto_compromiso_usd', 'fecha_cumplimiento', 'observaciones', 'timestamp'];
    downloadFile('registro_visitas_campo.csv', toCsv(state.visitasLog, cols), 'text/csv;charset=utf-8');
  });

  $('mcIter').addEventListener('input', runMonteCarlo);
  $('mcDesc').addEventListener('input', runMonteCarlo);
  $('auditClientSelect').addEventListener('change', renderAuditClient);
  $('exportSelect').addEventListener('change', renderExportMd);
  $('downloadMdBtn').addEventListener('click', () => {
    downloadFile(`expediente_${$('exportSelect').value}.md`, $('exportMdPreview').value, 'text/markdown;charset=utf-8');
  });

  applyGlobalFilters();
}

init();
