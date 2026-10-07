import { api } from '../core/api.js';
import { t } from '../core/i18n.js';
import { esc, emptyMarkup, toast, confirmDialog, sheet } from '../core/ui.js';
import { openForm } from '../core/form.js';
import { money, moneyShort, num, date, todayISO } from '../core/format.js';

let rows = [];
let projects = [];
let typeFilter = 'all';

const CATEGORIES = ['project_payment', 'salary', 'maintenance', 'fuel', 'other'];
const CATEGORY_LABEL = {
  project_payment: 'finance.projectPayment',
  salary: 'finance.salary',
  maintenance: 'finance.maintenance',
  fuel: 'finance.fuel',
  other: 'finance.other',
};

function fields() {
  return [
    {
      key: 'transaction_type',
      label: 'finance.transactionType',
      type: 'select',
      required: true,
      options: [
        { value: 'income', label: t('common.income') },
        { value: 'expense', label: t('common.expense') },
      ],
    },
    { key: 'amount', label: 'common.amount', type: 'number', required: true },
    {
      key: 'category',
      label: 'finance.category',
      type: 'select',
      options: CATEGORIES.map((c) => ({ value: c, label: t(CATEGORY_LABEL[c]) })),
    },
    { key: 'date', label: 'common.date', type: 'date', required: true },
    {
      key: 'project_id',
      label: 'finance.linkedProject',
      type: 'select',
      options: [
        { value: '', label: t('finance.none') },
        ...projects.map((p) => ({ value: String(p.id), label: p.name })),
      ],
    },
    { key: 'description', label: 'common.description', type: 'textarea' },
  ];
}

const BLANK = {
  transaction_type: 'income',
  amount: '',
  category: 'project_payment',
  date: todayISO(),
  project_id: '',
  description: '',
};

function card(x) {
  const isIncome = x.transaction_type === 'income';
  return `
    <div class="card glass" data-id="${x.id}">
      <div class="card-head">
        <div class="card-ico">${isIncome ? '📥' : '📤'}</div>
        <div class="card-body">
          <div class="card-title ${isIncome ? 'amount-pos' : 'amount-neg'}">
            ${isIncome ? '+' : '−'} ${esc(money(x.amount))}
          </div>
          <div class="card-sub">${esc(t(CATEGORY_LABEL[x.category] || 'finance.other'))} • ${esc(date(x.date))}</div>
        </div>
        <span class="badge ${isIncome ? 'income' : 'expense'}">${esc(t(isIncome ? 'common.income' : 'common.expense'))}</span>
      </div>
      <div class="card-rows">
        ${x.project_name ? `<div class="card-row"><span class="k">${esc(t('finance.linkedProject'))}</span><span class="v">${esc(x.project_name)}</span></div>` : ''}
        ${x.description ? `<div class="card-row"><span class="k">${esc(t('common.description'))}</span><span class="v">${esc(x.description)}</span></div>` : ''}
      </div>
      <div class="act-row">
        <button class="act" data-act="edit">✏️ ${esc(t('common.edit'))}</button>
        <button class="act del" data-act="delete">🗑️ ${esc(t('common.delete'))}</button>
      </div>
    </div>`;
}

function summary() {
  const income = rows.filter((r) => r.transaction_type === 'income').reduce((a, r) => a + (Number(r.amount) || 0), 0);
  const expense = rows.filter((r) => r.transaction_type === 'expense').reduce((a, r) => a + (Number(r.amount) || 0), 0);
  const balance = income - expense;

  const set = (id, val) => {
    const el = document.getElementById(id);
    if (el) el.textContent = val;
  };
  set('fin-balance', money(balance));
  set('fin-income', moneyShort(income));
  set('fin-expense', moneyShort(expense));
}

function paint() {
  const list = document.getElementById('finance-list');
  if (!list) return;
  const items = typeFilter === 'all' ? rows : rows.filter((r) => r.transaction_type === typeFilter);
  list.innerHTML = items.length ? items.map(card).join('') : emptyMarkup('💰', t('finance.empty'));
  const count = document.getElementById('finance-count');
  if (count) count.textContent = `${num(items.length)} ${t('common.item')}`;
  summary();
}

function openEditor(existing = BLANK, id = null) {
  openForm({
    title: t(id ? 'finance.editTransaction' : 'finance.addTransaction'),
    fields: fields(),
    values: existing,
    onSave: (values) => {
      const payload = {
        ...values,
        project_id: values.project_id === '' || values.project_id === null ? null : Number(values.project_id),
      };
      const action = id ? api.updateTransaction({ ...payload, id }) : api.createTransaction(payload);
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
  return Promise.all([api.listTransactions(), api.listProjects()]).then(([txs, ps]) => {
    rows = txs || [];
    projects = ps || [];
    paint();
  });
}

export function render(host) {
  host.innerHTML = `
    <div class="hero" style="background:linear-gradient(135deg,var(--primary),var(--accent) 70%,var(--warning))">
      <div class="hero-label">${esc(t('finance.balance'))}</div>
      <div class="hero-value" id="fin-balance">—</div>
      <div class="hero-meta">
        <div class="hero-pill">↑ <b id="fin-income">—</b> ${esc(t('common.income'))}</div>
        <div class="hero-pill">↓ <b id="fin-expense">—</b> ${esc(t('common.expense'))}</div>
      </div>
    </div>
    <div class="chip-row" id="finance-chips">
      <button class="chip ${typeFilter === 'all' ? 'on' : ''}" data-type="all">${esc(t('common.all'))}</button>
      <button class="chip ${typeFilter === 'income' ? 'on' : ''}" data-type="income">${esc(t('common.income'))}</button>
      <button class="chip ${typeFilter === 'expense' ? 'on' : ''}" data-type="expense">${esc(t('common.expense'))}</button>
    </div>
    <div class="section-title">${esc(t('finance.title'))}<span class="count" id="finance-count"></span></div>
    <div id="finance-list" class="stagger"><div class="skeleton"></div><div class="skeleton"></div></div>`;

  host.querySelector('#finance-chips').addEventListener('click', (e) => {
    const chip = e.target.closest('.chip');
    if (!chip) return;
    typeFilter = chip.dataset.type;
    host.querySelectorAll('.chip').forEach((c) => c.classList.toggle('on', c === chip));
    paint();
  });

  host.querySelector('#finance-list').addEventListener('click', (e) => {
    const btn = e.target.closest('[data-act]');
    const cardEl = e.target.closest('.card');
    if (!btn || !cardEl) return;
    const id = Number(cardEl.dataset.id);
    const row = rows.find((r) => r.id === id);
    if (!row) return;

    if (btn.dataset.act === 'edit') {
      openEditor({ ...row, project_id: row.project_id ? String(row.project_id) : '' }, id);
    } else {
      confirmDialog(t('common.delete'), t('common.deleteConfirm'), { confirmLabel: t('common.delete') }).then((yes) => {
        if (!yes) return;
        api.deleteTransaction(id).then(() => {
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

export const meta = { id: 'finance', icon: '💰', labelKey: 'nav.finance' };
