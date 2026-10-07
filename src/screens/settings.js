import { t, lang, setLang } from '../core/i18n.js';
import { esc, toast } from '../core/ui.js';
import { isNative } from '../core/api.js';

const VERSION = '0.1.0';

function theme() {
  return document.documentElement.dataset.theme || 'dark';
}

function setTheme(next) {
  document.documentElement.dataset.theme = next;
  localStorage.setItem('theme', next);
}

function paint() {
  const host = document.getElementById('settings-body');
  if (!host) return;
  const dark = theme() === 'dark';
  const fa = lang() === 'fa';

  host.innerHTML = `
    <div class="card glass">
      <div class="section-title" style="margin:0 0 6px">${esc(t('settings.language'))}</div>
      <div class="seg" id="lang-seg">
        <button class="${fa ? 'on' : ''}" data-lang="fa">${esc(t('settings.persian'))}</button>
        <button class="${!fa ? 'on' : ''}" data-lang="en">${esc(t('settings.english'))}</button>
      </div>
      <div class="section-title" style="margin:12px 0 6px">${esc(t('settings.theme'))}</div>
      <div class="seg" id="theme-seg">
        <button class="${!dark ? 'on' : ''}" data-theme="light">☀️ ${esc(t('settings.lightMode'))}</button>
        <button class="${dark ? 'on' : ''}" data-theme="dark">🌙 ${esc(t('settings.darkMode'))}</button>
      </div>
    </div>

    <div class="card glass">
      <div class="section-title" style="margin:0 0 6px">${esc(t('settings.about'))}</div>
      <div class="about-row"><span class="k">${esc(t('app.name'))}</span><span class="v">${esc(t('app.subtitle'))}</span></div>
      <div class="about-row"><span class="k">${esc(t('settings.version'))}</span><span class="v">${esc(VERSION)}</span></div>
      <div class="about-row"><span class="k">${esc(t('settings.techStack'))}</span><span class="v">Rust · Tauri 2</span></div>
      <div class="about-row"><span class="k">${esc(t('settings.dataLocation'))}</span><span class="v">${esc(isNative ? 'SQLite' : 'localStorage')}</span></div>
      <div class="about-row"><span class="k">${esc(t('settings.storage'))}</span><span class="v">${esc(t('settings.localOnly'))}</span></div>
    </div>`;

  host.querySelector('#lang-seg').addEventListener('click', (e) => {
    const btn = e.target.closest('[data-lang]');
    if (!btn) return;
    setLang(btn.dataset.lang);
  });

  host.querySelector('#theme-seg').addEventListener('click', (e) => {
    const btn = e.target.closest('[data-theme]');
    if (!btn) return;
    setTheme(btn.dataset.theme);
    paint();
    toast(t('common.success'), 'ok');
  });
}

export function render(host) {
  host.innerHTML = `<div class="section-title">${esc(t('settings.title'))}</div><div id="settings-body"><div class="skeleton"></div></div>`;
  paint();
  return Promise.resolve();
}

export function onLangChanged() {
  paint();
}

export const meta = { id: 'settings', icon: '⚙️', labelKey: 'nav.settings' };
