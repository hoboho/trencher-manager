/**
 * Headless smoke test for the Terencher mobile UI.
 *
 * Boots the real ES modules inside jsdom (using the localStorage data layer),
 * exercises navigation across every screen, and asserts that rendering did not
 * throw and produced meaningful DOM.
 */
import { JSDOM } from 'jsdom';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
import esbuild from 'esbuild';

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, '..');

const failures = [];
function check(name, cond, detail = '') {
  if (cond) console.log(`  ✓ ${name}`);
  else {
    failures.push(`${name}${detail ? ` — ${detail}` : ''}`);
    console.log(`  ✗ ${name}${detail ? ` — ${detail}` : ''}`);
  }
}

/* Bundle the app so relative ESM imports resolve in the jsdom context. */
const bundled = await esbuild.build({
  entryPoints: [path.join(root, 'src/main.js')],
  bundle: true,
  format: 'iife',
  write: false,
  logLevel: 'silent',
});
const code = bundled.outputFiles[0].text;

const html = readFileSync(path.join(root, 'src/index.html'), 'utf8');

/* jsdom has no layout, but the code paths we exercise are DOM-only. */
const dom = new JSDOM(html, {
  runScripts: 'dangerously',
  pretendToBeVisual: true,
  url: 'https://localhost/',
});

const { window } = dom;
const errors = [];
window.addEventListener('error', (e) => errors.push(String(e.error?.message ?? e.message)));
window.onerror = (m) => errors.push(String(m));

const origError = console.error;
window.console.error = (...a) => { errors.push(a.join(' ')); };

// Seed a little data so list screens have something to render.
window.localStorage.setItem('theme', 'dark');
window.localStorage.setItem(
  'terencher.db',
  JSON.stringify({
    projects: [
      { id: 1, name: 'Trench A1', client_name: 'ACME', location: 'Tehran', contract_amount: 1000000, received_amount: 400000, start_date: '2024-01-01', status: 'active', total_length: 120 },
      { id: 2, name: 'Trench B2', client_name: 'Beta Co', contract_amount: 500000, received_amount: 500000, start_date: '2024-02-01', status: 'completed' },
    ],
    machines: [{ id: 1, name: 'CAT 6015', model: '6015B', status: 'active', trenching_depth: 2, fuel_consumption_rate: 18, maintenance_cost_per_hour: 500000 }],
    operators: [{ id: 1, name: 'Ali Rezaei', hourly_rate: 400000, overtime_rate: 600000, overtime_threshold: 8, specialization: 'Heavy' }],
    transactions: [
      { id: 1, transaction_type: 'income', amount: 500000, category: 'project_payment', date: '2024-02-01', project_id: 1 },
      { id: 2, transaction_type: 'expense', amount: 120000, category: 'fuel', date: '2024-02-02', project_id: 1 },
    ],
  })
);

const script = window.document.createElement('script');
script.textContent = code;
window.document.body.appendChild(script);

await new Promise((r) => setTimeout(r, 60));

console.log('\nApp shell');
const doc = window.document;
check('app shell rendered', !!doc.querySelector('.appbar'), 'no .appbar');
check('background blobs present', doc.querySelectorAll('#bg .blob').length === 4);
check('tab bar rendered', doc.querySelectorAll('.tabbar .tab').length === 5, `got ${doc.querySelectorAll('.tabbar .tab').length}`);
check('all 7 screens mounted', doc.querySelectorAll('.screen').length === 7, `got ${doc.querySelectorAll('.screen').length}`);
check('default screen is dashboard', doc.querySelector('#screen-dashboard')?.classList.contains('active'));
check('RTL applied for Persian', doc.documentElement.dir === 'rtl');

console.log('\nDashboard');
const hero = doc.querySelector('#hero-profit')?.textContent ?? '';
check('net profit rendered', /[\d۰-۹]/.test(hero), `hero="${hero}"`);
check('stat grid populated', doc.querySelectorAll('#stat-grid .stat').length === 4);
check('recent projects listed', doc.querySelectorAll('#recent .card').length === 2);

/* Walk every tab the way a user would. */
const go = (id) => {
  const tab = doc.querySelector(`.tab[data-screen="${id}"]`) || doc.querySelector(`#btn-${id}`);
  tab.dispatchEvent(new window.MouseEvent('click', { bubbles: true }));
};

const screens = ['projects', 'machines', 'operators', 'finance', 'reports', 'settings'];
for (const id of screens) {
  go(id);
  await new Promise((r) => setTimeout(r, 40));
  const host = doc.querySelector(`#screen-${id}`);
  console.log(`\nScreen: ${id}`);
  check('active', host.classList.contains('active'), 'not activated');
  check('non-empty content', host.textContent.trim().length > 20, `len=${host.textContent.trim().length}`);
  check('no skeleton left behind', host.querySelectorAll('.skeleton').length === 0, `${host.querySelectorAll('.skeleton').length} skeleton(s)`);
}

console.log('\nData binding');
check('project cards rendered', doc.querySelectorAll('#project-list .card').length === 2, `got ${doc.querySelectorAll('#project-list .card').length}`);
check('machine card rendered', doc.querySelectorAll('#machine-list .card').length === 1);
check('operator card rendered', doc.querySelectorAll('#operator-list .card').length === 1);
check('transaction cards rendered', doc.querySelectorAll('#finance-list .card').length === 2);
check('finance balance computed', /[\d۰-۹]/.test(doc.querySelector('#fin-balance')?.textContent ?? ''));
check('reports panels rendered', doc.querySelectorAll('#report-body .card').length >= 4, `got ${doc.querySelectorAll('#report-body .card').length}`);
check('settings controls rendered', !!doc.querySelector('#lang-seg') && !!doc.querySelector('#theme-seg'));

console.log('\nSearch + tabs interactions');
const search = doc.querySelector('#project-search');
search.value = 'B2';
search.dispatchEvent(new window.Event('input', { bubbles: true }));
await new Promise((r) => setTimeout(r, 20));
check('search filters list', doc.querySelectorAll('#project-list .card').length === 1, `got ${doc.querySelectorAll('#project-list .card').length}`);

search.value = '';
search.dispatchEvent(new window.Event('input', { bubbles: true }));
const chips = doc.querySelectorAll('#project-chips .chip');
chips[1].dispatchEvent(new window.MouseEvent('click', { bubbles: true }));
await new Promise((r) => setTimeout(r, 20));
check('status chip filters list', doc.querySelectorAll('#project-list .card').length === 1, `got ${doc.querySelectorAll('#project-list .card').length}`);

/* Reset the status filter so the assertion is unambiguous. */
doc.querySelector('#project-chips [data-status="all"]').dispatchEvent(new window.MouseEvent('click', { bubbles: true }));
await new Promise((r) => setTimeout(r, 20));
check('filter reset shows all rows', doc.querySelectorAll('#project-list .card').length === 2, `got ${doc.querySelectorAll('#project-list .card').length}`);

console.log('\nFAB / bottom sheet');
go('projects');
await new Promise((r) => setTimeout(r, 30));
doc.querySelector('#fab').dispatchEvent(new window.MouseEvent('click', { bubbles: true }));
await new Promise((r) => setTimeout(r, 30));
check('sheet opened', doc.querySelector('#overlay').classList.contains('show'));
check('form has project fields', doc.querySelectorAll('#entity-form .input').length >= 10, `got ${doc.querySelectorAll('#entity-form .input').length}`);

/* Submit the form and confirm the row is persisted. */
const form = doc.querySelector('#entity-form');
form.querySelector('[data-key="name"]').value = 'New Trench';
form.querySelector('[data-key="contract_amount"]').value = '2500000';
form.dispatchEvent(new window.Event('submit', { bubbles: true, cancelable: true }));
await new Promise((r) => setTimeout(r, 80));
check('sheet closed after save', !doc.querySelector('#overlay').classList.contains('show'));
check('new project appears', doc.querySelectorAll('#project-list .card').length === 3, `got ${doc.querySelectorAll('#project-list .card').length}`);
check(
  'new project persisted to store',
  (JSON.parse(window.localStorage.getItem('terencher.db')).projects || []).some((p) => p.name === 'New Trench')
);

console.log('\nLanguage switch');
go('settings');
await new Promise((r) => setTimeout(r, 40));
doc.querySelector('#lang-seg [data-lang="en"]').dispatchEvent(new window.MouseEvent('click', { bubbles: true }));
await new Promise((r) => setTimeout(r, 60));
check('direction flipped to LTR', doc.documentElement.dir === 'ltr');
check('tab labels translated', doc.querySelector('.tabbar .tab span:last-child').textContent.trim() === 'Dashboard', doc.querySelector('.tabbar .tab span:last-child').textContent.trim());

console.log('\nRuntime errors');
window.console.error = origError;
check('no uncaught errors', errors.length === 0, errors.slice(0, 3).join(' | '));

console.log(`\n${failures.length === 0 ? '✅ ALL CHECKS PASSED' : `❌ ${failures.length} FAILURE(S)`}`);
if (failures.length) {
  console.log(failures.map((f) => ` - ${f}`).join('\n'));
  process.exit(1);
}
