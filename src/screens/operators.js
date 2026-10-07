import { api } from '../core/api.js';
import { t } from '../core/i18n.js';
import { esc, emptyMarkup, toast, confirmDialog, sheet } from '../core/ui.js';
import { openForm } from '../core/form.js';
import { money, num } from '../core/format.js';

let rows = [];
let query = '';

const FIELDS = [
  { key: 'name', label: 'operators.operatorName', required: true },
  { key: 'hourly_rate', label: 'operators.hourlyRate', type: 'number', required: true },
  { key: 'overtime_rate', label: 'operators.overtimeRate', type: 'number', required: true },
  { key: 'overtime_threshold', label: 'operators.overtimeThreshold', type: 'number' },
  { key: 'specialization', label: 'operators.specialization' },
  { key: 'contact', label: 'operators.contact' },
  { key: 'skills', label: 'operators.skills' },
  { key: 'notes', label: 'operators.notes', type: 'textarea' },
];

const BLANK = {
  name: '',
  hourly_rate: '',
  overtime_rate: '',
  overtime_threshold: 8,
  contact: '',
  skills: '',
  specialization: '',
  notes: '',
};

function initials(name) {
  const parts = String(name || '').trim().split(/\s+/);
  return parts.slice(0, 2).map((p) => p[0] || '').join('').toUpperCase() || '👤';
}

function card(o) {
  return `
    <div class="card glass" data-id="${o.id}">
      <div class="card-head">
        <div class="card-ico" style="font-weight:800;font-size:16px">${esc(initials(o.name))}</div>
        <div class="card-body">
          <div class="card-title">${esc(o.name)}</div>
          <div class="card-sub">${esc(o.specialization || o.contact || '—')}</div>
        </div>
      </div>
      <div class="card-rows">
        <div class="card-row"><span class="k">${esc(t('operators.hourlyRate'))}</span><span class="v">${esc(money(o.hourly_rate))}</span></div>
        <div class="card-row"><span class="k">${esc(t('operators.overtimeRate'))}</span><span class="v">${esc(money(o.overtime_rate))}</span></div>
        <div class="card-row"><span class="k">${esc(t('operators.overtimeThreshold'))}</span><span class="v">${esc(num(o.overtime_threshold, 0))}</span></div>
        ${o.skills ? `<div class="card-row"><span class="k">${esc(t('operators.skills'))}</span><span class="v">${esc(o.skills)}</span></div>` : ''}
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
  return rows.filter((o) =>
    [o.name, o.specialization, o.skills, o.contact].filter(Boolean).some((v) => String(v).toLowerCase().includes(q))
  );
}

function paint() {
  const list = document.getElementById('operator-list');
  if (!list) return;
  const items = visible();
  list.innerHTML = items.length ? items.map(card).join('') : emptyMarkup('👷', t('operators.empty'));
  const count = document.getElementById('operator-count');
  if (count) count.textContent = `${num(items.length)} ${t('common.item')}`;
}

function openEditor(existing = BLANK, id = null) {
  openForm({
    title: t(id ? 'operators.editOperator' : 'operators.addOperator'),
    fields: FIELDS,
    values: existing,
    onSave: (values) => {
      const action = id ? api.updateOperator({ ...values, id }) : api.createOperator(values);
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
  return api.listOperators().then((data) => {
    rows = data || [];
    paint();
  });
}

export function render(host) {
  host.innerHTML = `
    <div class="toolbar">
      <div class="search-wrap">
        <span class="s-ico">🔍</span>
        <input class="input" id="operator-search" placeholder="${esc(t('common.search'))}" value="${esc(query)}">
      </div>
    </div>
    <div class="section-title">${esc(t('operators.title'))}<span class="count" id="operator-count"></span></div>
    <div id="operator-list" class="stagger"><div class="skeleton"></div><div class="skeleton"></div></div>`;

  host.querySelector('#operator-search').addEventListener('input', (e) => {
    query = e.target.value;
    paint();
  });

  host.querySelector('#operator-list').addEventListener('click', (e) => {
    const btn = e.target.closest('[data-act]');
    const cardEl = e.target.closest('.card');
    if (!btn || !cardEl) return;
    const id = Number(cardEl.dataset.id);
    const row = rows.find((r) => r.id === id);
    if (!row) return;

    if (btn.dataset.act === 'edit') {
      openEditor(row, id);
    } else {
      confirmDialog(t('common.delete'), t('operators.deleteConfirm') || t('common.deleteConfirm'), {
        confirmLabel: t('common.delete'),
      }).then((yes) => {
        if (!yes) return;
        api.deleteOperator(id).then(() => {
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

export const meta = { id: 'operators', icon: '👷', labelKey: 'nav.operators' };
