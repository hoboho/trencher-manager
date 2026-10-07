import { api } from '../core/api.js';
import { t } from '../core/i18n.js';
import { esc, emptyMarkup, toast } from '../core/ui.js';
import { money, moneyShort, num, pct } from '../core/format.js';

let data = null;

function bar(label, value, max, display) {
  const width = max > 0 ? Math.max(3, Math.round((value / max) * 100)) : 0;
  return `
    <div class="bar-item">
      <div class="bar-top">
        <span class="b-lbl">${esc(label)}</span>
        <span class="b-val">${esc(display)}</span>
      </div>
      <div class="progress"><i style="width:${width}%"></i></div>
    </div>`;
}

function panel(title, bodyMarkup) {
  return `
    <div class="card glass">
      <div class="section-title" style="margin:0 0 14px">${esc(title)}</div>
      ${bodyMarkup}
    </div>`;
}

function build() {
  if (!data) return '';
  const { projects, machines, operators, transactions } = data;

  const income = transactions
    .filter((x) => x.transaction_type === 'income')
    .reduce((a, x) => a + (Number(x.amount) || 0), 0);
  const expense = transactions
    .filter((x) => x.transaction_type === 'expense')
    .reduce((a, x) => a + (Number(x.amount) || 0), 0);

  /* Projects by status */
  const statusCount = {};
  projects.forEach((p) => {
    statusCount[p.status] = (statusCount[p.status] || 0) + 1;
  });
  const statusMax = Math.max(1, ...Object.values(statusCount));
  const statusBars = Object.entries(statusCount)
    .map(([s, c]) => bar(t(`common.${s}`), c, statusMax, `${num(c)} ${t('common.item')}`))
    .join('');

  /* Expenses by category */
  const catSum = {};
  transactions.forEach((x) => {
    catSum[x.category] = (catSum[x.category] || 0) + (Number(x.amount) || 0);
  });
  const catMax = Math.max(1, ...Object.values(catSum));
  const CATEGORY_LABEL = {
    project_payment: 'finance.projectPayment',
    salary: 'finance.salary',
    maintenance: 'finance.maintenance',
    fuel: 'finance.fuel',
    other: 'finance.other',
  };
  const catBars = Object.entries(catSum)
    .sort((a, b) => b[1] - a[1])
    .map(([c, v]) => bar(t(CATEGORY_LABEL[c] || 'finance.other'), v, catMax, moneyShort(v)))
    .join('');

  /* Top projects by contract value */
  const top = [...projects]
    .sort((a, b) => (Number(b.contract_amount) || 0) - (Number(a.contract_amount) || 0))
    .slice(0, 5);
  const topMax = Math.max(1, ...top.map((p) => Number(p.contract_amount) || 0));
  const topBars = top
    .map((p) => {
      const collected = pct(p.received_amount, p.contract_amount);
      return bar(p.name, Number(p.contract_amount) || 0, topMax, `${moneyShort(p.contract_amount)} • ${num(collected)}%`);
    })
    .join('');

  const summary = `
    <div class="stat-grid">
      <div class="stat glass"><div class="stat-ico">🏗️</div><div class="stat-val">${esc(num(projects.length))}</div><div class="stat-lbl">${esc(t('dashboard.totalProjects'))}</div></div>
      <div class="stat glass"><div class="stat-ico">🚜</div><div class="stat-val">${esc(num(machines.length))}</div><div class="stat-lbl">${esc(t('dashboard.totalMachines'))}</div></div>
      <div class="stat glass"><div class="stat-ico">👷</div><div class="stat-val">${esc(num(operators.length))}</div><div class="stat-lbl">${esc(t('dashboard.totalOperators'))}</div></div>
      <div class="stat glass"><div class="stat-ico">💵</div><div class="stat-val ${income - expense >= 0 ? 'amount-pos' : 'amount-neg'}">${esc(moneyShort(income - expense))}</div><div class="stat-lbl">${esc(t('dashboard.netProfit'))}</div></div>
    </div>`;

  if (!projects.length && !transactions.length) {
    return emptyMarkup('📊', t('reports.noData'));
  }

  return `
    ${panel(t('reports.summary'), summary)}
    <div style="height:14px"></div>
    ${panel(t('reports.byStatus'), statusBars || emptyMarkup('📁', t('reports.noData')))}
    <div style="height:14px"></div>
    ${panel(t('reports.byCategory'), catBars || emptyMarkup('💸', t('reports.noData')))}
    <div style="height:14px"></div>
    ${panel(t('reports.topProjects'), topBars || emptyMarkup('🏗️', t('reports.noData')))}
    <div style="height:14px"></div>
    ${panel(t('dashboard.financial'), `
      <div class="about-row"><span class="k">${esc(t('finance.totalIncome'))}</span><span class="v amount-pos">${esc(money(income))}</span></div>
      <div class="about-row"><span class="k">${esc(t('finance.totalExpense'))}</span><span class="v amount-neg">${esc(money(expense))}</span></div>
      <div class="divider"></div>
      <div class="about-row"><span class="k">${esc(t('common.total'))}</span><span class="v">${esc(money(income - expense))}</span></div>
    `)}`;
}

function paint() {
  const host = document.getElementById('report-body');
  if (host) host.innerHTML = build();
}

/** Export everything currently shown as a CSV file. */
function exportCsv() {
  if (!data) return;
  const lines = [];
  lines.push('section,label,value');
  const { projects, machines, operators, transactions } = data;
  lines.push(`projects,count,${projects.length}`);
  lines.push(`machines,count,${machines.length}`);
  lines.push(`operators,count,${operators.length}`);
  transactions.forEach((x) => lines.push(`transaction,${x.category},${x.amount}`));

  const csv = lines.join('\n');
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `terencher-report-${new Date().toISOString().slice(0, 10)}.csv`;
  a.click();
  URL.revokeObjectURL(url);
  toast(t('common.success'), 'ok');
}

export function load() {
  return Promise.all([api.listProjects(), api.listMachines(), api.listOperators(), api.listTransactions()]).then(
    ([projects, machines, operators, transactions]) => {
      data = { projects: projects || [], machines: machines || [], operators: operators || [], transactions: transactions || [] };
      paint();
    }
  );
}

export function render(host) {
  host.innerHTML = `
    <div class="section-title">${esc(t('reports.title'))}</div>
    <div id="report-body"><div class="skeleton"></div><div class="skeleton"></div><div class="skeleton"></div></div>
    <div style="height:6px"></div>
    <button class="btn btn-primary" id="export-csv">📤 ${esc(t('reports.summary'))} (CSV)</button>
    <div style="height:12px"></div>`;

  host.querySelector('#export-csv').addEventListener('click', exportCsv);
  return load();
}

export const meta = { id: 'reports', icon: '📊', labelKey: 'nav.reports' };
