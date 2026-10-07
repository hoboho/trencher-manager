/** Small DOM helpers shared by every screen. */

const ESCAPES = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' };

/** Escape untrusted text before it is interpolated into a template string. */
export function esc(value) {
  if (value === null || value === undefined) return '';
  return String(value).replace(/[&<>"']/g, (c) => ESCAPES[c]);
}

export function $(sel, root = document) {
  return root.querySelector(sel);
}

export function $$(sel, root = document) {
  return Array.from(root.querySelectorAll(sel));
}

/** Replace the innerHTML of a host element and return the host. */
export function html(host, markup) {
  const node = typeof host === 'string' ? $(host) : host;
  if (node) node.innerHTML = markup;
  return node;
}

/* ───────────────────────────────── toast ───────────────────────────────── */

let toastTimer;

export function toast(message, kind = 'ok') {
  const el = $('#toast');
  if (!el) return;
  el.textContent = message;
  el.className = `show ${kind}`;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => {
    el.className = '';
  }, 2400);
}

/* ────────────────────────────── bottom sheet ────────────────────────────── */

export const sheet = {
  open(markup) {
    const overlay = $('#overlay');
    const body = $('#sheet-body');
    if (!overlay || !body) return;
    body.innerHTML = markup;
    overlay.classList.add('show');
    body.parentElement.scrollTop = 0;
  },

  close() {
    const overlay = $('#overlay');
    if (overlay) overlay.classList.remove('show');
  },

  isOpen() {
    return Boolean($('#overlay')?.classList.contains('show'));
  },
};

/** Inline confirmation rendered inside the active screen. */
export function confirmDialog(title, message, { confirmLabel = 'OK', danger = true } = {}) {
  return new Promise((resolve) => {
    const markup = `
      <div class="grabber"></div>
      <h2>${esc(title)}</h2>
      <p style="color:var(--text-2);font-size:14px;line-height:1.7;margin-bottom:20px">${esc(message)}</p>
      <div class="btn-row">
        <button class="btn btn-ghost" data-act="no">${esc(__t('common.cancel'))}</button>
        <button class="btn ${danger ? 'btn-danger' : 'btn-primary'}" data-act="yes">${esc(confirmLabel)}</button>
      </div>`;

    sheet.open(markup);
    const body = $('#sheet-body');
    body.onclick = (e) => {
      const act = e.target.closest('[data-act]')?.dataset.act;
      if (!act) return;
      body.onclick = null;
      sheet.close();
      resolve(act === 'yes');
    };
  });
}

/** Placeholder markup used while a screen loads. */
export function loadingMarkup() {
  return `<div class="spinner"></div>`;
}

export function emptyMarkup(icon, title, sub = '') {
  return `
    <div class="empty">
      <div class="e-ico">${icon}</div>
      <div class="e-title">${esc(title)}</div>
      ${sub ? `<div class="e-sub">${esc(sub)}</div>` : ''}
    </div>`;
}

/* Small indirection so ui.js does not import i18n at module load (avoids cycles). */
let translate = (k) => k;
export function bindTranslator(fn) {
  translate = fn;
}
function __t(key) {
  return translate(key);
}
export { __t as tt };
