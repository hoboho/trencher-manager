import fa from '../locales/fa.js';
import en from '../locales/en.js';

const DICTS = { fa, en };
const listeners = new Set();

const state = {
  lang: localStorage.getItem('lang') || 'fa',
};

export function lang() {
  return state.lang;
}

export function isRTL() {
  return state.lang === 'fa';
}

export function setLang(next) {
  if (!DICTS[next]) return;
  state.lang = next;
  localStorage.setItem('lang', next);
  listeners.forEach((fn) => fn(next));
}

export function onLangChange(fn) {
  listeners.add(fn);
  return () => listeners.delete(fn);
}

/** Translate a dotted key, e.g. t('projects.title'). */
export function t(key) {
  const parts = key.split('.');
  let node = DICTS[state.lang];
  for (const p of parts) {
    if (node && typeof node === 'object' && p in node) node = node[p];
    else return key;
  }
  return typeof node === 'string' ? node : key;
}

/** Apply <html lang/dir> for the active language. */
export function applyDirection() {
  const root = document.documentElement;
  root.lang = state.lang;
  root.dir = isRTL() ? 'rtl' : 'ltr';
}
