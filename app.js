/* Mini CRM - LocalStorage backed single-page app */

const STORAGE_KEY = 'mini-crm-v1';
const DEAL_STAGES = [
  { id: 'lead', label: 'Lead' },
  { id: 'qualified', label: 'Qualifiziert' },
  { id: 'proposal', label: 'Angebot' },
  { id: 'won', label: 'Gewonnen' },
  { id: 'lost', label: 'Verloren' },
];
const ACTIVITY_TYPES = [
  { id: 'note', label: 'Notiz' },
  { id: 'call', label: 'Anruf' },
  { id: 'meeting', label: 'Meeting' },
  { id: 'email', label: 'E-Mail' },
];

const uid = () => Math.random().toString(36).slice(2, 10) + Date.now().toString(36).slice(-4);
const fmtDate = (iso) => iso ? new Date(iso).toLocaleDateString('de-DE') : '—';
const fmtDateTime = (iso) => iso ? new Date(iso).toLocaleString('de-DE') : '—';
const fmtMoney = (n) => (Number(n) || 0).toLocaleString('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 });
const escape = (s) => String(s ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

/* ---------- State ---------- */
const defaultState = () => ({
  contacts: [],
  companies: [],
  deals: [],
  activities: [],
});

let state = defaultState();
let currentView = 'dashboard';
let searchTerm = '';

function loadState() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) state = { ...defaultState(), ...JSON.parse(raw) };
  } catch (e) {
    console.warn('Failed to load state', e);
    state = defaultState();
  }
}
function saveState() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
}

function toast(msg) {
  const el = document.getElementById('toast');
  el.textContent = msg;
  el.classList.remove('hidden');
  clearTimeout(toast._t);
  toast._t = setTimeout(() => el.classList.add('hidden'), 2200);
}

/* ---------- Lookups ---------- */
const getCompany = (id) => state.companies.find(c => c.id === id);
const getContact = (id) => state.contacts.find(c => c.id === id);
const getDeal = (id) => state.deals.find(d => d.id === id);

/* ---------- Routing ---------- */
function setView(view) {
  currentView = view;
  document.querySelectorAll('.nav-btn').forEach(b => b.classList.toggle('active', b.dataset.view === view));
  document.getElementById('viewTitle').textContent = {
    dashboard: 'Dashboard',
    contacts: 'Kontakte',
    companies: 'Firmen',
    deals: 'Pipeline',
    activities: 'Aktivitäten',
  }[view];
  document.getElementById('primaryAction').style.display = view === 'dashboard' ? 'none' : 'inline-block';
  document.getElementById('primaryAction').textContent = {
    contacts: '+ Kontakt',
    companies: '+ Firma',
    deals: '+ Deal',
    activities: '+ Aktivität',
  }[view] || '+ Neu';
  render();
}

/* ---------- Render dispatcher ---------- */
function render() {
  const root = document.getElementById('view');
  if (currentView === 'dashboard') root.innerHTML = renderDashboard();
  else if (currentView === 'contacts') root.innerHTML = renderContacts();
  else if (currentView === 'companies') root.innerHTML = renderCompanies();
  else if (currentView === 'deals') { root.innerHTML = renderDeals(); attachDealHandlers(); }
  else if (currentView === 'activities') root.innerHTML = renderActivities();
  attachRowHandlers();
}

/* ---------- Dashboard ---------- */
function renderDashboard() {
  const openDeals = state.deals.filter(d => d.stage !== 'won' && d.stage !== 'lost');
  const wonDeals = state.deals.filter(d => d.stage === 'won');
  const pipelineValue = openDeals.reduce((s, d) => s + (Number(d.value) || 0), 0);
  const wonValue = wonDeals.reduce((s, d) => s + (Number(d.value) || 0), 0);
  const recent = [...state.activities].sort((a, b) => (b.date || '').localeCompare(a.date || '')).slice(0, 6);

  const stageRows = DEAL_STAGES.map(s => {
    const deals = state.deals.filter(d => d.stage === s.id);
    const val = deals.reduce((sum, d) => sum + (Number(d.value) || 0), 0);
    return `<tr><td><span class="badge badge-${s.id}">${s.label}</span></td><td>${deals.length}</td><td>${fmtMoney(val)}</td></tr>`;
  }).join('');

  return `
    <div class="kpis">
      <div class="kpi"><div class="label">Kontakte</div><div class="value">${state.contacts.length}</div></div>
      <div class="kpi"><div class="label">Firmen</div><div class="value">${state.companies.length}</div></div>
      <div class="kpi"><div class="label">Offene Pipeline</div><div class="value">${fmtMoney(pipelineValue)}</div><div class="sub">${openDeals.length} offene Deals</div></div>
      <div class="kpi"><div class="label">Gewonnen</div><div class="value">${fmtMoney(wonValue)}</div><div class="sub">${wonDeals.length} Abschlüsse</div></div>
    </div>

    <div class="panel">
      <div class="panel-header">Pipeline-Übersicht</div>
      <table>
        <thead><tr><th>Stadium</th><th>Anzahl</th><th>Wert</th></tr></thead>
        <tbody>${stageRows}</tbody>
      </table>
    </div>

    <div class="panel">
      <div class="panel-header">Letzte Aktivitäten</div>
      ${recent.length === 0 ? `<div class="empty"><h3>Noch keine Aktivitäten</h3><p>Lege Notizen, Anrufe oder Meetings an.</p></div>` : `
        <table>
          <thead><tr><th>Datum</th><th>Typ</th><th>Betreff</th><th>Kontakt</th></tr></thead>
          <tbody>${recent.map(a => `
            <tr>
              <td>${fmtDateTime(a.date)}</td>
              <td><span class="badge badge-${a.type}">${ACTIVITY_TYPES.find(t => t.id === a.type)?.label || a.type}</span></td>
              <td>${escape(a.subject)}</td>
              <td>${escape(getContact(a.contactId)?.name || '—')}</td>
            </tr>`).join('')}</tbody>
        </table>`}
    </div>
  `;
}

/* ---------- Contacts ---------- */
function renderContacts() {
  const filtered = state.contacts.filter(c => matchesSearch(c, ['name', 'email', 'phone', 'title']));
  if (filtered.length === 0) return emptyState('Keine Kontakte', 'Lege deinen ersten Kontakt an.');
  return `
    <div class="panel">
      <table>
        <thead><tr><th>Name</th><th>Position</th><th>Firma</th><th>E-Mail</th><th>Telefon</th><th></th></tr></thead>
        <tbody>
          ${filtered.map(c => `
            <tr>
              <td><strong>${escape(c.name)}</strong></td>
              <td>${escape(c.title || '—')}</td>
              <td>${escape(getCompany(c.companyId)?.name || '—')}</td>
              <td>${c.email ? `<a href="mailto:${escape(c.email)}">${escape(c.email)}</a>` : '—'}</td>
              <td>${escape(c.phone || '—')}</td>
              <td class="row-actions">
                <button class="icon-btn" data-edit="contact" data-id="${c.id}">Bearbeiten</button>
                <button class="icon-btn danger" data-delete="contact" data-id="${c.id}">Löschen</button>
              </td>
            </tr>`).join('')}
        </tbody>
      </table>
    </div>
  `;
}

/* ---------- Companies ---------- */
function renderCompanies() {
  const filtered = state.companies.filter(c => matchesSearch(c, ['name', 'industry', 'website']));
  if (filtered.length === 0) return emptyState('Keine Firmen', 'Lege deine erste Firma an.');
  return `
    <div class="panel">
      <table>
        <thead><tr><th>Name</th><th>Branche</th><th>Website</th><th>Kontakte</th><th>Deals</th><th></th></tr></thead>
        <tbody>
          ${filtered.map(c => {
            const contactCount = state.contacts.filter(x => x.companyId === c.id).length;
            const dealCount = state.deals.filter(x => x.companyId === c.id).length;
            return `
            <tr>
              <td><strong>${escape(c.name)}</strong></td>
              <td>${escape(c.industry || '—')}</td>
              <td>${c.website ? `<a href="${escape(c.website)}" target="_blank" rel="noopener">${escape(c.website)}</a>` : '—'}</td>
              <td>${contactCount}</td>
              <td>${dealCount}</td>
              <td class="row-actions">
                <button class="icon-btn" data-edit="company" data-id="${c.id}">Bearbeiten</button>
                <button class="icon-btn danger" data-delete="company" data-id="${c.id}">Löschen</button>
              </td>
            </tr>`;
          }).join('')}
        </tbody>
      </table>
    </div>
  `;
}

/* ---------- Deals / Pipeline ---------- */
function renderDeals() {
  const filtered = state.deals.filter(d => matchesSearch(d, ['title']));
  return `
    <div class="pipeline">
      ${DEAL_STAGES.map(stage => {
        const deals = filtered.filter(d => d.stage === stage.id);
        const total = deals.reduce((s, d) => s + (Number(d.value) || 0), 0);
        return `
          <div class="pipeline-col">
            <div class="pipeline-col-header">
              <span>${stage.label} <span class="count">${deals.length}</span></span>
              <span style="font-size: 12px; color: var(--muted);">${fmtMoney(total)}</span>
            </div>
            <div class="pipeline-list" data-stage="${stage.id}">
              ${deals.map(d => `
                <div class="deal-card" draggable="true" data-deal="${d.id}">
                  <div class="title">${escape(d.title)}</div>
                  <div class="meta">${escape(getCompany(d.companyId)?.name || 'Keine Firma')}</div>
                  <div class="value">${fmtMoney(d.value)}</div>
                  <div class="row-actions" style="margin-top: 8px;">
                    <button class="icon-btn" data-edit="deal" data-id="${d.id}">Bearbeiten</button>
                    <button class="icon-btn danger" data-delete="deal" data-id="${d.id}">×</button>
                  </div>
                </div>`).join('')}
            </div>
          </div>`;
      }).join('')}
    </div>
  `;
}

function attachDealHandlers() {
  document.querySelectorAll('.deal-card').forEach(card => {
    card.addEventListener('dragstart', (e) => {
      e.dataTransfer.setData('text/plain', card.dataset.deal);
      e.dataTransfer.effectAllowed = 'move';
    });
  });
  document.querySelectorAll('.pipeline-list').forEach(list => {
    list.addEventListener('dragover', (e) => {
      e.preventDefault();
      list.classList.add('drag-over');
    });
    list.addEventListener('dragleave', () => list.classList.remove('drag-over'));
    list.addEventListener('drop', (e) => {
      e.preventDefault();
      list.classList.remove('drag-over');
      const dealId = e.dataTransfer.getData('text/plain');
      const deal = getDeal(dealId);
      if (deal && deal.stage !== list.dataset.stage) {
        deal.stage = list.dataset.stage;
        deal.updatedAt = new Date().toISOString();
        saveState();
        toast('Deal verschoben');
        render();
      }
    });
  });
}

/* ---------- Activities ---------- */
function renderActivities() {
  const filtered = state.activities
    .filter(a => matchesSearch(a, ['subject', 'notes']))
    .sort((a, b) => (b.date || '').localeCompare(a.date || ''));
  if (filtered.length === 0) return emptyState('Keine Aktivitäten', 'Lege eine Notiz, einen Anruf oder ein Meeting an.');
  return `
    <div class="panel">
      <table>
        <thead><tr><th>Datum</th><th>Typ</th><th>Betreff</th><th>Kontakt</th><th>Deal</th><th>Notizen</th><th></th></tr></thead>
        <tbody>
          ${filtered.map(a => `
            <tr>
              <td>${fmtDateTime(a.date)}</td>
              <td><span class="badge badge-${a.type}">${ACTIVITY_TYPES.find(t => t.id === a.type)?.label || a.type}</span></td>
              <td><strong>${escape(a.subject)}</strong></td>
              <td>${escape(getContact(a.contactId)?.name || '—')}</td>
              <td>${escape(getDeal(a.dealId)?.title || '—')}</td>
              <td style="max-width: 280px; white-space: pre-wrap;">${escape(a.notes || '')}</td>
              <td class="row-actions">
                <button class="icon-btn" data-edit="activity" data-id="${a.id}">Bearbeiten</button>
                <button class="icon-btn danger" data-delete="activity" data-id="${a.id}">Löschen</button>
              </td>
            </tr>`).join('')}
        </tbody>
      </table>
    </div>
  `;
}

/* ---------- Helpers ---------- */
function matchesSearch(obj, fields) {
  if (!searchTerm) return true;
  const q = searchTerm.toLowerCase();
  return fields.some(f => String(obj[f] || '').toLowerCase().includes(q));
}
function emptyState(title, sub) {
  return `<div class="panel"><div class="empty"><h3>${escape(title)}</h3><p>${escape(sub)}</p></div></div>`;
}

function attachRowHandlers() {
  document.querySelectorAll('[data-edit]').forEach(b => {
    b.addEventListener('click', (e) => {
      e.stopPropagation();
      openModal(b.dataset.edit, b.dataset.id);
    });
  });
  document.querySelectorAll('[data-delete]').forEach(b => {
    b.addEventListener('click', (e) => {
      e.stopPropagation();
      const kind = b.dataset.delete;
      const id = b.dataset.id;
      if (!confirm('Wirklich löschen?')) return;
      deleteEntity(kind, id);
    });
  });
}

function deleteEntity(kind, id) {
  if (kind === 'contact') {
    state.contacts = state.contacts.filter(x => x.id !== id);
    state.activities.forEach(a => { if (a.contactId === id) a.contactId = null; });
    state.deals.forEach(d => { if (d.contactId === id) d.contactId = null; });
  } else if (kind === 'company') {
    state.companies = state.companies.filter(x => x.id !== id);
    state.contacts.forEach(c => { if (c.companyId === id) c.companyId = null; });
    state.deals.forEach(d => { if (d.companyId === id) d.companyId = null; });
  } else if (kind === 'deal') {
    state.deals = state.deals.filter(x => x.id !== id);
    state.activities.forEach(a => { if (a.dealId === id) a.dealId = null; });
  } else if (kind === 'activity') {
    state.activities = state.activities.filter(x => x.id !== id);
  }
  saveState();
  toast('Gelöscht');
  render();
}

/* ---------- Modal / Forms ---------- */
const FORMS = {
  contact: {
    title: (e) => e ? 'Kontakt bearbeiten' : 'Neuer Kontakt',
    fields: () => [
      { name: 'name', label: 'Name', type: 'text', required: true },
      { name: 'title', label: 'Position', type: 'text' },
      { name: 'email', label: 'E-Mail', type: 'email' },
      { name: 'phone', label: 'Telefon', type: 'text' },
      { name: 'companyId', label: 'Firma', type: 'select', options: [{ value: '', label: '—' }, ...state.companies.map(c => ({ value: c.id, label: c.name }))] },
      { name: 'notes', label: 'Notizen', type: 'textarea' },
    ],
    collection: 'contacts',
  },
  company: {
    title: (e) => e ? 'Firma bearbeiten' : 'Neue Firma',
    fields: () => [
      { name: 'name', label: 'Name', type: 'text', required: true },
      { name: 'industry', label: 'Branche', type: 'text' },
      { name: 'website', label: 'Website', type: 'text' },
      { name: 'address', label: 'Adresse', type: 'textarea' },
    ],
    collection: 'companies',
  },
  deal: {
    title: (e) => e ? 'Deal bearbeiten' : 'Neuer Deal',
    fields: () => [
      { name: 'title', label: 'Titel', type: 'text', required: true },
      { name: 'value', label: 'Wert (EUR)', type: 'number' },
      { name: 'stage', label: 'Stadium', type: 'select', options: DEAL_STAGES.map(s => ({ value: s.id, label: s.label })) },
      { name: 'companyId', label: 'Firma', type: 'select', options: [{ value: '', label: '—' }, ...state.companies.map(c => ({ value: c.id, label: c.name }))] },
      { name: 'contactId', label: 'Kontakt', type: 'select', options: [{ value: '', label: '—' }, ...state.contacts.map(c => ({ value: c.id, label: c.name }))] },
      { name: 'expectedClose', label: 'Erwartetes Closing', type: 'date' },
      { name: 'notes', label: 'Notizen', type: 'textarea' },
    ],
    collection: 'deals',
  },
  activity: {
    title: (e) => e ? 'Aktivität bearbeiten' : 'Neue Aktivität',
    fields: () => [
      { name: 'type', label: 'Typ', type: 'select', options: ACTIVITY_TYPES.map(t => ({ value: t.id, label: t.label })) },
      { name: 'subject', label: 'Betreff', type: 'text', required: true },
      { name: 'date', label: 'Datum & Zeit', type: 'datetime-local' },
      { name: 'contactId', label: 'Kontakt', type: 'select', options: [{ value: '', label: '—' }, ...state.contacts.map(c => ({ value: c.id, label: c.name }))] },
      { name: 'dealId', label: 'Deal', type: 'select', options: [{ value: '', label: '—' }, ...state.deals.map(d => ({ value: d.id, label: d.title }))] },
      { name: 'notes', label: 'Notizen', type: 'textarea' },
    ],
    collection: 'activities',
  },
};

function openModal(kind, id) {
  const def = FORMS[kind];
  if (!def) return;
  const entity = id ? state[def.collection].find(x => x.id === id) : null;
  const data = entity ? { ...entity } : defaultFor(kind);

  document.getElementById('modalTitle').textContent = def.title(entity);
  const form = document.getElementById('modalForm');
  form.innerHTML = def.fields().map(f => renderField(f, data[f.name])).join('') + `
    <div class="form-actions">
      <button type="button" class="btn-secondary" id="modalCancel">Abbrechen</button>
      <button type="submit" class="btn-primary">Speichern</button>
    </div>
  `;
  document.getElementById('modalBackdrop').classList.remove('hidden');

  document.getElementById('modalCancel').onclick = closeModal;

  form.onsubmit = (e) => {
    e.preventDefault();
    const fd = new FormData(form);
    const updated = { ...data };
    def.fields().forEach(f => {
      const v = fd.get(f.name);
      updated[f.name] = f.type === 'number' ? (v === '' ? null : Number(v)) : (v || null);
    });
    if (!updated.id) updated.id = uid();
    updated.updatedAt = new Date().toISOString();
    if (!entity) {
      updated.createdAt = updated.updatedAt;
      state[def.collection].push(updated);
    } else {
      const idx = state[def.collection].findIndex(x => x.id === entity.id);
      state[def.collection][idx] = updated;
    }
    saveState();
    closeModal();
    toast(entity ? 'Aktualisiert' : 'Erstellt');
    render();
  };
}

function defaultFor(kind) {
  if (kind === 'deal') return { stage: 'lead' };
  if (kind === 'activity') return { type: 'note', date: new Date().toISOString().slice(0, 16) };
  return {};
}

function renderField(f, value) {
  const v = value ?? '';
  const req = f.required ? 'required' : '';
  if (f.type === 'textarea') {
    return `<div class="form-row"><label>${f.label}</label><textarea name="${f.name}" ${req}>${escape(v)}</textarea></div>`;
  }
  if (f.type === 'select') {
    const opts = f.options.map(o => `<option value="${escape(o.value)}" ${String(o.value) === String(v) ? 'selected' : ''}>${escape(o.label)}</option>`).join('');
    return `<div class="form-row"><label>${f.label}</label><select name="${f.name}" ${req}>${opts}</select></div>`;
  }
  return `<div class="form-row"><label>${f.label}</label><input type="${f.type}" name="${f.name}" value="${escape(v)}" ${req} /></div>`;
}

function closeModal() {
  document.getElementById('modalBackdrop').classList.add('hidden');
}

/* ---------- Demo data ---------- */
function seedDemo() {
  if (state.contacts.length || state.companies.length || state.deals.length) {
    if (!confirm('Bestehende Daten werden überschrieben. Fortfahren?')) return;
  }
  state = defaultState();
  const acme = { id: uid(), name: 'Acme GmbH', industry: 'Software', website: 'https://acme.example', address: 'Hauptstr. 1, Berlin', createdAt: new Date().toISOString() };
  const lumen = { id: uid(), name: 'Lumen AG', industry: 'Energie', website: 'https://lumen.example', address: 'Industrieweg 5, München', createdAt: new Date().toISOString() };
  const nordic = { id: uid(), name: 'Nordic Logistik', industry: 'Logistik', website: 'https://nordic.example', address: 'Hafenstr. 12, Hamburg', createdAt: new Date().toISOString() };
  state.companies = [acme, lumen, nordic];

  const anna = { id: uid(), name: 'Anna Schulz', title: 'CTO', email: 'anna@acme.example', phone: '+49 30 123456', companyId: acme.id };
  const peter = { id: uid(), name: 'Peter Klein', title: 'Einkauf', email: 'peter@lumen.example', phone: '+49 89 987654', companyId: lumen.id };
  const sara = { id: uid(), name: 'Sara Vogt', title: 'Geschäftsführerin', email: 'sara@nordic.example', phone: '+49 40 555111', companyId: nordic.id };
  state.contacts = [anna, peter, sara];

  state.deals = [
    { id: uid(), title: 'Acme Jahreslizenz', value: 24000, stage: 'qualified', companyId: acme.id, contactId: anna.id, expectedClose: '2026-07-15' },
    { id: uid(), title: 'Lumen Pilot-Projekt', value: 8500, stage: 'proposal', companyId: lumen.id, contactId: peter.id, expectedClose: '2026-06-30' },
    { id: uid(), title: 'Nordic Erweiterung', value: 42000, stage: 'lead', companyId: nordic.id, contactId: sara.id, expectedClose: '2026-09-01' },
    { id: uid(), title: 'Acme Beratung Q1', value: 12000, stage: 'won', companyId: acme.id, contactId: anna.id, expectedClose: '2026-03-15' },
  ];

  state.activities = [
    { id: uid(), type: 'call', subject: 'Erstgespräch', date: new Date(Date.now() - 86400000 * 2).toISOString().slice(0, 16), contactId: anna.id, notes: 'Anna ist interessiert an einer Demo nächste Woche.' },
    { id: uid(), type: 'meeting', subject: 'Demo & Discovery', date: new Date(Date.now() - 86400000).toISOString().slice(0, 16), contactId: peter.id, dealId: state.deals[1].id, notes: 'Anforderungen geklärt, Angebot folgt.' },
    { id: uid(), type: 'note', subject: 'Recherche-Notiz', date: new Date().toISOString().slice(0, 16), contactId: sara.id, notes: 'Wachsende Logistik-Sparte – Potenzial für Mehrjahresvertrag.' },
  ];
  saveState();
  toast('Demodaten geladen');
  render();
}

/* ---------- Import / Export ---------- */
function exportData() {
  const blob = new Blob([JSON.stringify(state, null, 2)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `crm-export-${new Date().toISOString().slice(0, 10)}.json`;
  a.click();
  URL.revokeObjectURL(url);
}

function importData(file) {
  const reader = new FileReader();
  reader.onload = (e) => {
    try {
      const data = JSON.parse(e.target.result);
      if (!data.contacts || !data.companies) throw new Error('Ungültiges Format');
      if (!confirm('Aktuelle Daten überschreiben?')) return;
      state = { ...defaultState(), ...data };
      saveState();
      toast('Import erfolgreich');
      render();
    } catch (err) {
      alert('Import fehlgeschlagen: ' + err.message);
    }
  };
  reader.readAsText(file);
}

function resetAll() {
  if (!confirm('Alle Daten löschen?')) return;
  state = defaultState();
  saveState();
  toast('Alles zurückgesetzt');
  render();
}

/* ---------- Init ---------- */
function init() {
  loadState();

  document.querySelectorAll('.nav-btn').forEach(btn => {
    btn.addEventListener('click', () => setView(btn.dataset.view));
  });

  document.getElementById('primaryAction').addEventListener('click', () => {
    const map = { contacts: 'contact', companies: 'company', deals: 'deal', activities: 'activity' };
    if (map[currentView]) openModal(map[currentView]);
  });

  document.getElementById('globalSearch').addEventListener('input', (e) => {
    searchTerm = e.target.value.trim();
    render();
  });

  document.getElementById('modalClose').addEventListener('click', closeModal);
  document.getElementById('modalBackdrop').addEventListener('click', (e) => {
    if (e.target.id === 'modalBackdrop') closeModal();
  });
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') closeModal();
  });

  document.getElementById('exportBtn').addEventListener('click', exportData);
  document.getElementById('importBtn').addEventListener('click', () => document.getElementById('importFile').click());
  document.getElementById('importFile').addEventListener('change', (e) => {
    if (e.target.files[0]) importData(e.target.files[0]);
    e.target.value = '';
  });
  document.getElementById('seedBtn').addEventListener('click', seedDemo);
  document.getElementById('resetBtn').addEventListener('click', resetAll);

  setView('dashboard');
}

init();
