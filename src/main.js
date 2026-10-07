import { t, lang, setLang, applyDirection, onLangChange, isRTL } from './core/i18n.js';
import { esc, sheet, bindTranslator, toast } from './core/ui.js';

import * as dashboard from './screens/dashboard.js';
import * as projects from './screens/projects.js';
import * as machines from './screens/machines.js';
import * as operators from './screens/operators.js';
import * as finance from './screens/finance.js';
import * as reports from './screens/reports.js';
import * as settings from './screens/settings.js';

/* Five tabs mirror the PyQt sidebar; reports/settings live behind the appbar. */
const TABS = [dashboard, projects, machines, operators, finance];
const EXTRA = [reports, settings];
const ALL = [...TABS, ...EXTRA];

const state = { active: 'dashboard', loaded: new Set() };

bindTranslator(t);

/* ───────────────────────────── theme bootstrap ───────────────────────────── */

function initTheme() {
  const saved = localStorage.getItem('theme');
  const prefersDark = window.matchMedia?.('(prefers-color-scheme: dark)').matches;
  document.documentElement.dataset.theme = saved || (prefersDark ? 'dark' : 'light');
}

/* ─────────────────────────────── app markup ─────────────────────────────── */

function shellMarkup() {
  const tabs = TABS.map(
    (s) => `
      <button class="tab" data-screen="${s.meta.id}">
        <span class="tab-ico">${s.meta.icon}</span>
        <span data-i18n="${s.meta.labelKey}">${esc(t(s.meta.labelKey))}</span>
      </button>`
  ).join('');

  return `
    <div id="bg">
      <span class="blob b1"></span>
      <span class="blob b2"></span>
      <span class="blob b3"></span>
      <span class="blob b4"></span>
    </div>

    <header class="appbar glass">
      <div class="brand">
        <div class="logo">🛠️</div>
        <div style="min-width:0">
          <h1 id="appbar-title"></h1>
          <div class="sub" id="appbar-sub"></div>
        </div>
      </div>
      <button class="icon-btn" id="btn-reports" title="Reports">📊</button>
      <button class="icon-btn" id="btn-settings" title="Settings">⚙️</button>
    </header>

    <main id="main">
      ${ALL.map((s) => `<section class="screen" id="screen-${s.meta.id}" data-screen="${s.meta.id}"></section>`).join('')}
    </main>

    <button class="fab" id="fab">＋</button>

    <nav class="tabbar" id="tabbar">${tabs}</nav>

    <div class="overlay" id="overlay">
      <div class="sheet" id="sheet-body-host"><div id="sheet-body"></div></div>
    </div>

    <div id="toast"></div>`;
}

/* ──────────────────────────────── routing ──────────────────────────────── */

function syncChrome() {
  const mod = ALL.find((s) => s.meta.id === state.active);
  const title = document.getElementById('appbar-title');
  const sub = document.getElementById('appbar-sub');
  if (title) title.textContent = t(mod?.meta.labelKey ?? 'app.name');
  if (sub) sub.textContent = t('app.subtitle');

  document.querySelectorAll('.tab').forEach((el) => {
    el.classList.toggle('active', el.dataset.screen === state.active);
  });

  const fab = document.getElementById('fab');
  if (fab) fab.style.display = mod?.onFab ? 'grid' : 'none';
}

export function go(id) {
  const mod = ALL.find((s) => s.meta.id === id);
  if (!mod) return;
  state.active = id;

  document.querySelectorAll('.screen').forEach((el) => {
    el.classList.toggle('active', el.dataset.screen === id);
  });

  syncChrome();

  // Scroll the content area back to the top on navigation. Guarded because
  // not every webview/host implements scrollTo on the element.
  const main = document.getElementById('main');
  if (main && typeof main.scrollTo === 'function') {
    main.scrollTo({ top: 0, behavior: 'smooth' });
  } else if (main) {
    main.scrollTop = 0;
  }

  const host = document.getElementById(`screen-${id}`);
  if (host && !state.loaded.has(id)) {
    state.loaded.add(id);
    Promise.resolve(mod.render(host)).catch((err) => {
      toast(String(err?.message ?? err), 'err');
    });
  } else if (host && mod.load) {
    // refresh stale data when re-entering a screen
    mod.load(host).catch(() => {});
  }
}

/** Force a full re-render (used after a language change). */
function reloadAll() {
  state.loaded.clear();
  ALL.forEach((s) => {
    const host = document.getElementById(`screen-${s.meta.id}`);
    if (host) host.innerHTML = '';
  });
  document.querySelectorAll('[data-i18n]').forEach((el) => {
    el.textContent = t(el.dataset.i18n);
  });
  syncChrome();
  const active = ALL.find((s) => s.meta.id === state.active);
  const host = document.getElementById(`screen-${state.active}`);
  if (active && host) {
    state.loaded.add(state.active);
    Promise.resolve(active.render(host)).catch(() => {});
  }
}

/* ──────────────────────────────── boot ──────────────────────────────── */

function boot() {
  initTheme();
  applyDirection();

  document.getElementById('app').innerHTML = shellMarkup();

  document.getElementById('tabbar').addEventListener('click', (e) => {
    const tab = e.target.closest('.tab');
    if (tab) go(tab.dataset.screen);
  });

  document.getElementById('btn-reports').addEventListener('click', () => go('reports'));
  document.getElementById('btn-settings').addEventListener('click', () => go('settings'));

  document.getElementById('fab').addEventListener('click', () => {
    const mod = ALL.find((s) => s.meta.id === state.active);
    mod?.onFab?.();
  });

  // Tap the dimmed area to dismiss the sheet.
  document.getElementById('overlay').addEventListener('click', (e) => {
    if (e.target.id === 'overlay') sheet.close();
  });

  // Hardware / gesture back button closes the sheet first, then goes to dashboard.
  window.addEventListener('popstate', () => {
    if (sheet.isOpen()) {
      sheet.close();
      history.pushState(null, '', location.href);
    } else if (state.active !== 'dashboard') {
      go('dashboard');
      history.pushState(null, '', location.href);
    }
  });
  history.pushState(null, '', location.href);

  onLangChange(() => {
    applyDirection();
    reloadAll();
    settings.onLangChanged?.();
  });

  go('dashboard');
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', boot);
} else {
  boot();
}
