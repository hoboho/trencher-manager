import { lang } from './i18n.js';

const FA_DIGITS = ['۰', '۱', '۲', '۳', '۴', '۵', '۶', '۷', '۸', '۹'];

function toFaDigits(str) {
  return str.replace(/\d/g, (d) => FA_DIGITS[Number(d)]);
}

function localizeDigits(str) {
  return lang() === 'fa' ? toFaDigits(str) : str;
}

/** Group thousands with the locale separator. */
export function num(value, digits = 0) {
  const n = Number(value);
  if (!Number.isFinite(n)) return localizeDigits('0');
  const s = n.toLocaleString('en-US', {
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
  });
  return localizeDigits(s);
}

const CURRENCY = { fa: 'ریال', en: 'Rial' };

/** Format a money amount with its unit. */
export function money(value) {
  return `${num(value)} ${CURRENCY[lang()] ?? ''}`.trim();
}

/** Compact money, e.g. ۱٫۲ م for millions. */
export function moneyShort(value) {
  const n = Number(value) || 0;
  const abs = Math.abs(n);
  if (abs >= 1_000_000_000) return `${num(n / 1_000_000_000, 1)} ${lang() === 'fa' ? 'میلیارد' : 'B'}`;
  if (abs >= 1_000_000) return `${num(n / 1_000_000, 1)} ${lang() === 'fa' ? 'میلیون' : 'M'}`;
  if (abs >= 1_000) return `${num(n / 1_000, 1)} ${lang() === 'fa' ? 'هزار' : 'K'}`;
  return num(n);
}

/** ISO date -> localized short date. */
export function date(value) {
  if (!value) return '—';
  const d = new Date(String(value).length <= 10 ? `${value}T00:00:00` : value);
  if (Number.isNaN(d.getTime())) return String(value);
  const s = d.toLocaleDateString('en-GB', { year: 'numeric', month: '2-digit', day: '2-digit' });
  return localizeDigits(s);
}

/** Today as YYYY-MM-DD for <input type="date">. */
export function todayISO() {
  return new Date().toISOString().slice(0, 10);
}

/** Clamp 0..1 to a percentage integer. */
export function pct(part, whole) {
  const w = Number(whole) || 0;
  if (w <= 0) return 0;
  return Math.max(0, Math.min(100, Math.round((Number(part) || 0) / w * 100)));
}

export function localize(text) {
  return localizeDigits(String(text));
}
