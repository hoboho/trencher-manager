import { api } from '../core/api.js';
import { t } from '../core/i18n.js';
import { esc, emptyMarkup, toast, confirmDialog, sheet } from '../core/ui.js';
import { openForm } from '../core/form.js';
import { money, num, date } from '../core/format.js';

let rows = [];
let query = '';

const FIELDS = [
  { key: 'name', label: 'machines.machineName', required: true },
  { key: 'model', label: 'machines.model' },
  { key: 'purchase_date', label: 'machines.purchaseDate', type: 'date' },
  { key: 'purchase_price', label: 'machines.purchasePrice', type: 'number' },
  { key: 'fuel_consumption_rate', label: 'machines.fuelConsumption', type: 'number' },
  { key: 'fuel_cost_per_liter', label: 'machines.fuelCost', type: 'number' },
  { key: 'maintenance_cost_per_hour', label: 'machines.maintenanceCost', type: 'number' },
  { key: 'trenching_depth', label: 'machines.trenchingDepth', type: 'number' },
  { key: 'trenching_width', label: 'machines.trenchingWidth', type: 'number' },
  { key: 'maximum_speed', label: 'machines.maxSpeed', type: 'number' },
  { key: 'weight', label: 'machines.weight', type: 'number' },
  {
    key: 'status',
    label: 'common.status',
    type: 'select',
    options: [
      { value: 'active', label: t('common.active') },
      { value: 'inactive', label: t('common.inactive') },
    ],
  },
];

const BLANK = {
  name: '',
  model: '',
  purchase_date: '',
  purchase_price: '',
  fuel_consumption_rate: '',
  fuel_cost_per_liter: '',
  maintenance_cost_per_hour: '',
  trenching_depth: '',
  trenching_width: '',
  maximum_speed: '',
  weight: '',
  status: 'active',
};

function card(m) {
  return `
    <div class="card glass" data-id="${m.id}">
      <div class="card-head">
        <div class="card-ico">🚜</div>
        <div class="card-body">
          <div class="card-title">${esc(m.name)}</div>
          <div class="card-sub">${esc(m.model || '—')}</div>
        </div>
        <span class="badge ${esc(m.status)}">${esc(t(`common.${m.status}`))}</span>
      </div>
      <div class="card-rows">
        ${m.trenching_depth ? `<div class="card-row"><span class="k">${esc(t('machines.trenchingDepth'))}</span><span class="v">${esc(num(m.trenching_depth, 2))}</span></div>` : ''}
        ${m.trenching_width ? `<div class="card-row"><span class="k">${esc(t('machines.trenchingWidth'))}</span><span class="v">${esc(num(m.trenching_width, 2))}</span></div>` : ''}
        ${m.fuel_consumption_rate ? `<div class="card-row"><span class="k">${esc(t('machines.fuelConsumption'))}</span><span class="v">${esc(num(m.fuel_consumption_rate, 1))}</span></div>` : ''}
        ${m.maintenance_cost_per_hour ? `<div class="card-row"><span class="k">${esc(t('machines.maintenanceCost'))}</span><span class="v">${esc(money(m.maintenance_cost_per_hour))}</span></div>` : ''}
        ${m.purchase_price ? `<div class="card-row"><span class="k">${esc(t('machines.purchasePrice'))}</span><span class="v">${esc(money(m.purchase_price))}</span></div>` : ''}
        ${m.purchase_date ? `<div class="card-row"><span class="k">${esc(t('machines.purchaseDate'))}</span><span class="v">${esc(date(m.purchase_date))}</span></div>` : ''}
      </div>
      <div class="act-row">
        <button class="act" data-act="edit">✏️ ${esc(t('common.edit'))}</button>
        <button class="act del" data-act="delete">🗑️ ${esc(t('common.delete'))}</button>
      </div>
    </div>`;
}

function visible() {
  const q = query.trim().toLowerCase();
  if (!q) return rows;
  return rows.filter((m) => [m.name, m.model].filter(Boolean).some((v) => String(v).toLowerCase().includes(q)));
}

function paint() {
  const list = document.getElementById('machine-list');
  if (!list) return;
  const items = visible();
  list.innerHTML = items.length ? items.map(card).join('') : emptyMarkup('🚜', t('machines.empty'));
  const count = document.getElementById('machine-count');
  if (count) count.textContent = `${num(items.length)} ${t('common.item')}`;
}

function openEditor(existing = BLANK, id = null) {
  openForm({
    title: t(id ? 'machines.editMachine' : 'machines.addMachine'),
    fields: FIELDS,
    values: existing,
    onSave: (values) => {
      const action = id ? api.updateMachine({ ...values, id }) : api.createMachine(values);
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
  return api.listMachines().then((data) => {
    rows = data || [];
    paint();
  });
}

export function render(host) {
  host.innerHTML = `
    <div class="toolbar">
      <div class="search-wrap">
        <span class="s-ico">🔍</span>
        <input class="input" id="machine-search" placeholder="${esc(t('common.search'))}" value="${esc(query)}">
      </div>
    </div>
    <div class="section-title">${esc(t('machines.title'))}<span class="count" id="machine-count"></span></div>
    <div id="machine-list" class="stagger"><div class="skeleton"></div><div class="skeleton"></div></div>`;

  host.querySelector('#machine-search').addEventListener('input', (e) => {
    query = e.target.value;
    paint();
  });

  host.querySelector('#machine-list').addEventListener('click', (e) => {
    const btn = e.target.closest('[data-act]');
    const cardEl = e.target.closest('.card');
    if (!btn || !cardEl) return;
    const id = Number(cardEl.dataset.id);
    const row = rows.find((r) => r.id === id);
    if (!row) return;

    if (btn.dataset.act === 'edit') {
      openEditor(row, id);
    } else {
      confirmDialog(t('common.delete'), t('machines.deleteConfirm') || t('common.deleteConfirm'), {
        confirmLabel: t('common.delete'),
      }).then((yes) => {
        if (!yes) return;
        api.deleteMachine(id).then(() => {
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

export const meta = { id: 'machines', icon: '🚜', labelKey: 'nav.machines' };
