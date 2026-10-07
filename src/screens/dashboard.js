import { api } from '../core/api.js';
import { t } from '../core/i18n.js';
import { esc, emptyMarkup } from '../core/ui.js';
import { money, moneyShort, num, pct } from '../core/format.js';

function statusBadge(status) {
  const label = t(`common.${status}`) || status;
  return `<span class="badge ${esc(status)}">${esc(label)}</span>`;
}

function projectCard(p) {
  const progress = pct(p.received_amount, p.contract_amount);
  return `
    <div class="card glass">
      <div class="card-head">
        <div class="card-ico">🏗️</div>
        <div class="card-body">
          <div class="card-title">${esc(p.name)}</div>
          <div class="card-sub">${esc(p.client_name || '—')}</div>
        </div>
        ${statusBadge(p.status)}
      </div>
      <div class="progress"><i style="width:${progress}%"></i></div>
      <div class="card-rows">
        <div class="card-row"><span class="k">${esc(t('projects.contractAmount'))}</span><span class="v">${esc(moneyShort(p.contract_amount))}</span></div>
        <div class="card-row"><span class="k">${esc(t('projects.progress'))}</span><span class="v">${esc(num(progress))}%</span></div>
      </div>
    </div>`;
}

export function render(host) {
  host.innerHTML = `
    <div class="hero">
      <div class="hero-label">${esc(t('dashboard.netProfit'))}</div>
      <div class="hero-value" id="hero-profit">—</div>
      <div class="hero-meta">
        <div class="hero-pill">↑ <b id="hero-income">—</b> ${esc(t('common.income'))}</div>
        <div class="hero-pill">↓ <b id="hero-expense">—</b> ${esc(t('common.expense'))}</div>
      </div>
    </div>
    <div class="section-title">${esc(t('dashboard.overview'))}</div>
    <div class="stat-grid stagger" id="stat-grid"><div class="skeleton"></div><div class="skeleton"></div></div>
    <div class="section-title">${esc(t('dashboard.recentProjects'))}</div>
    <div id="recent" class="stagger"></div>`;

  api.dashboard().then((s) => {
    const profitEl = document.getElementById('hero-profit');
    if (profitEl) profitEl.textContent = money(s.net_profit);
    const inc = document.getElementById('hero-income');
    const exp = document.getElementById('hero-expense');
    if (inc) inc.textContent = moneyShort(s.total_income);
    if (exp) exp.textContent = moneyShort(s.total_expense);

    const grid = document.getElementById('stat-grid');
    if (grid) {
      const stats = [
        { ico: '🏗️', val: s.total_projects, lbl: t('dashboard.totalProjects'), extra: `${num(s.active_projects)} ${t('common.active')}` },
        { ico: '🚜', val: s.total_machines, lbl: t('dashboard.totalMachines'), extra: `${num(s.active_machines)} ${t('common.active')}` },
        { ico: '👷', val: s.total_operators, lbl: t('dashboard.totalOperators') },
        { ico: '💰', val: moneyShort(s.net_profit), lbl: t('dashboard.netProfit') },
      ];
      grid.innerHTML = stats
        .map(
          (x) => `
        <div class="stat glass">
          <div class="stat-ico">${x.ico}</div>
          <div class="stat-val">${esc(x.val)}</div>
          <div class="stat-lbl">${esc(x.lbl)}</div>
          ${x.extra ? `<div class="stat-lbl" style="color:var(--primary)">${esc(x.extra)}</div>` : ''}
        </div>`
        )
        .join('');
    }

    const recent = document.getElementById('recent');
    if (recent) {
      recent.innerHTML = s.recent_projects?.length
        ? s.recent_projects.map(projectCard).join('')
        : emptyMarkup('🗂️', t('dashboard.noRecent'));
    }
  });
}

export const meta = { id: 'dashboard', icon: '◎', labelKey: 'nav.dashboard' };
