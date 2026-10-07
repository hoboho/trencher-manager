import { esc, sheet, toast } from './ui.js';
import { t } from './i18n.js';
import { todayISO } from './format.js';

/**
 * Declarative form inside the bottom sheet.
 *
 * @param {object}   opts
 * @param {string}   opts.title    Sheet heading.
 * @param {string}   opts.saveKey  i18n key for the submit button.
 * @param {Array}    opts.fields   Field descriptors (see below).
 * @param {object}   opts.values   Initial values (edit mode).
 * @param {Function} opts.onSave   Receives the collected `values` object.
 *
 * Field descriptor:
 *   { key, label (i18n key), type: 'text'|'number'|'date'|'textarea'|'select',
 *     required?, options?, placeholder?, half? }
 */
export function openForm({ title, saveKey = 'common.save', fields, values = {}, onSave }) {
  const inputFor = (f) => {
    const value = values[f.key] ?? '';
    const attrs = `data-key="${esc(f.key)}" class="input"`;
    const ph = f.placeholder ? ` placeholder="${esc(f.placeholder)}"` : '';

    if (f.type === 'textarea') {
      return `<textarea ${attrs}${ph}>${esc(value)}</textarea>`;
    }
    if (f.type === 'select') {
      const opts = f.options
        .map((o) => `<option value="${esc(o.value)}"${String(value) === String(o.value) ? ' selected' : ''}>${esc(o.label)}</option>`)
        .join('');
      return `<select ${attrs}>${opts}</select>`;
    }
    const type = f.type === 'number' ? 'number' : f.type === 'date' ? 'date' : 'text';
    const step = f.type === 'number' ? ' step="any" inputmode="decimal"' : '';
    return `<input ${attrs} type="${type}"${step} value="${esc(value)}"${ph}>`;
  };

  const markup = `
    <div class="grabber"></div>
    <h2>${esc(title)}</h2>
    <form id="entity-form" novalidate>
      ${fields
        .map((f) => {
          const req = f.required ? ' <span style="color:var(--danger)">*</span>' : '';
          const cls = f.half ? 'field half' : 'field';
          return `<div class="${cls}"><label>${esc(t(f.label))}${req}</label>${inputFor(f)}</div>`;
        })
        .join('')}
      <div class="btn-row" style="margin-top:18px">
        <button type="button" class="btn btn-ghost" data-act="cancel">${esc(t('common.cancel'))}</button>
        <button type="submit" class="btn btn-primary">${esc(t(saveKey))}</button>
      </div>
    </form>`;

  sheet.open(markup);

  const form = document.getElementById('entity-form');
  form.querySelector('[data-act="cancel"]').addEventListener('click', () => sheet.close());

  // Auto-close the on-screen keyboard when leaving a numeric field is not
  // needed here; the webview handles it.
  form.addEventListener('submit', (e) => {
    e.preventDefault();
    const out = {};
    let missing = null;

    for (const f of fields) {
      const input = form.querySelector(`[data-key="${f.key}"]`);
      let raw = input.value.trim();
      if (f.required && !raw) {
        missing = f;
        break;
      }
      if (f.type === 'number') out[f.key] = raw === '' ? null : Number(raw);
      else out[f.key] = raw === '' ? null : raw;
    }

    if (missing) {
      toast(`${t(fields.find((f) => f === missing).label)}: ${t('common.fillRequired')}`, 'err');
      form.querySelector(`[data-key="${missing.key}"]`)?.focus();
      return;
    }

    onSave(out);
  });

  // Focus the first field for a snappy feel.
  setTimeout(() => form.querySelector('.input')?.focus(), 260);
}

/** Default value helper for date fields. */
export const defaultDate = todayISO;
