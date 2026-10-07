import { api } from '../core/api.js';
import { t } from '../core/i18n.js';
import { esc, emptyMarkup, toast, confirmDialog, sheet } from '../core/ui.js';
import { openForm } from '../core/form.js';
import { money, moneyShort, num, date, pct, todayISO } from '../core/format.js';

let rows = [];
let query = '';
let statusFilter = 'all';

const STATUSES = ['active', 'completed', 'paused', 'cancelled'];

const FIELDS = [
  { key: 'name', label: 'projects.projectName', required: true },
  { key: 'client_name', label: 'projects.clientName' },
  { key: 'client_contact', label: 'projects.clientContact' },
  { key: 'location', label: 'projects.location' },
  { key: 'contract_amount', label: 'projects.contractAmount', type: 'number', required: true },
  { key: 'received_amount', label: 'projects.receivedAmount', type: 'number' },
  { key: 'start_date', label: 'projects.startDate', type: 'date', required: true },
  { key: 'end_date', label: 'projects.endDate', type: 'date' },
  { key: 'total_length', label: 'projects.totalLength', type: 'number' },
  { key: 'average_depth', label: 'projects.avgDepth', type: 'number' },
  { key: 'average_width', label: 'projects.avgWidth', type: 'number' },
  {
    key: 'status',
    label: 'common.status',
    type: 'select',
    options: STATUSES.map((s) => ({ value: s, label: t(`common.${s}`) })),
  },
  { key: 'description', label: 'projects.description', type: 'textarea' },
  { key: 'notes', label: 'projects.notes', type: 'textarea' },
];

const BLANK = {
  name: '',
  client_name: '',
  client_contact: '',
  location: '',
  contract_amount: '',
  received_amount: 0,
  start_date: todayISO(),
  end_date: '',
  total_length: '',
  average_depth: '',
  average_width: '',
  status: 'active',
  description: '',
  notes: '',
};

function card(p) {
  const progress = pct(p.received_amount, p.contract_amount);
  const remaining = Math.max(0, (Number(p.contract_amount) || 0) - (Number(p.received_amount) || 0));
  return `
    <div class="card glass" data-id="${p.id}">
      <div class="card-head">
        <div class="card-ico">🏗️</div>
        <div class="card-body">
          <div class="card-title">${esc(p.name)}</div>
          <div class="card-sub">${esc(p.client_name || '—')}${p.location ? ` • ${esc(p.location)}` : ''}</div>
        </div>
        <span class="badge ${esc(p.status)}">${esc(t(`common.${p.status}`))}</span>
      </div>
      <div class="progress"><i style="width:${progress}%"></i></div>
      <div class="card-rows">
        <div class="card-row"><span class="k">${esc(t('projects.contractAmount'))}</span><span class="v">${esc(money(p.contract_amount))}</span></div>
        <div class="card-row"><span class="k">${esc(t('projects.receivedAmount'))}</span><span class="v amount-pos">${esc(money(p.received_amount))}</span></div>
        <div class="card-row"><span class="k">${esc(t('projects.remaining'))}</span><span class="v amount-neg">${esc(money(remaining))}</span></div>
        <div class="card-row"><span class="k">${esc(t('projects.startDate'))}</span><span class="v">${esc(date(p.start_date))}</span></div>
        ${p.total_length ? `<div class="card-row"><span class="k">${esc(t('projects.totalLength'))}</span><span class="v">${esc(num(p.total_length, 1))}</span></div>` : ''}
      </div>
      <div class="act-row">
        <button class="act" data-act="edit">✏️ ${esc(t('common.edit'))}</button>
        <button class="act del" data-act="delete">🗑️ ${esc(t('common.delete'))}</button>
      </div>
    </div>`;
}

function visible() {
  const q = query.trim().toLowerCase();
  return rows.filter((p) => {
    const matchesStatus = statusFilter === 'all' || p.status === statusFilter;
    if (!matchesStatus) return false;
    if (!q) return true;
    return [p.name, p.client_name, p.location, p.client_contact]
      .filter(Boolean)
      .some((v) => String(v).toLowerCase().includes(q));
  });
}

function paint() {
  const list = document.getElementById('project-list');
  if (!list) return;
  const items = visible();
  list.innerHTML = items.length
    ? items.map(card).join('')
    : emptyMarkup('🏗️', t('projects.empty'));

  const count = document.getElementById('project-count');
  if (count) count.textContent = `${num(items.length)} ${t('common.item')}`;
}

function openEditor(existing = BLANK, id = null) {
  openForm({
    title: t(id ? 'projects.editProject' : 'projects.addProject'),
    fields: FIELDS,
    values: existing,
    onSave: (values) => {
      const action = id ? api.updateProject({ ...values, id }) : api.createProject(values);
      action
        .then(() => {
          sheet.close();
          return load();
        })
        .then(() => toast(t('common.saved'), 'ok'))
        .catch((err) => toast(String(err?.message ?? err), 'err'));
    },
  });
}

export function load() {
  return api.listProjects().then((data) => {
    rows = data || [];
    paint();
  });
}

export function render(host) {
  host.innerHTML = `
    <div class="toolbar">
      <div class="search-wrap">
        <span class="s-ico">🔍</span>
        <input class="input" id="project-search" placeholder="${esc(t('common.search'))}" value="${esc(query)}">
      </div>
    </div>
    <div class="chip-row" id="project-chips">
      <button class="chip ${statusFilter === 'all' ? 'on' : ''}" data-status="all">${esc(t('common.all'))}</button>
      ${STATUSES.map((s) => `<button class="chip ${statusFilter === s ? 'on' : ''}" data-status="${s}">${esc(t(`common.${s}`))}</button>`).join('')}
    </div>
    <div class="section-title">${esc(t('projects.title'))}<span class="count" id="project-count"></span></div>
    <div id="project-list" class="stagger"><div class="skeleton"></div><div class="skeleton"></div></div>`;

  host.querySelector('#project-search').addEventListener('input', (e) => {
    query = e.target.value;
    paint();
  });

  host.querySelector('#project-chips').addEventListener('click', (e) => {
    const chip = e.target.closest('.chip');
    if (!chip) return;
    statusFilter = chip.dataset.status;
    host.querySelectorAll('.chip').forEach((c) => c.classList.toggle('on', c === chip));
    paint();
  });

  host.querySelector('#project-list').addEventListener('click', (e) => {
    const btn = e.target.closest('[data-act]');
    const cardEl = e.target.closest('.card');
    if (!btn || !cardEl) return;
    const id = Number(cardEl.dataset.id);
    const row = rows.find((r) => r.id === id);
    if (!row) return;

    if (btn.dataset.act === 'edit') {
      openEditor(row, id);
    } else {
      confirmDialog(t('projects.editProject'), t('common.deleteConfirm'), {
        confirmLabel: t('common.delete'),
      }).then((yes) => {
        if (!yes) return;
        api.deleteProject(id).then(() => {
          toast(t('common.deleted'), 'ok');
          load();
        });
      });
    }
  });

  return load();
}

export function onFab() {
  openEditor(BLANK, null);
}

export const meta = { id: 'projects', icon: '🏗️', labelKey: 'nav.projects' };
