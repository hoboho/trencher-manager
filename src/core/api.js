/**
 * Data access layer.
 *
 * On device it talks to the Rust backend through Tauri's `invoke` bridge.
 * In a plain browser (or a quick `vite` preview) it falls back to a
 * localStorage-backed store that mirrors the same contract, so the UI can be
 * developed and reviewed without the Android toolchain.
 */

const tauri = globalThis.__TAURI__;
const nativeInvoke = tauri?.core?.invoke;

export const isNative = typeof nativeInvoke === 'function';

/* ────────────────────────── browser fallback store ────────────────────────── */

const KEY = 'terencher.db';

function readStore() {
  try {
    return JSON.parse(localStorage.getItem(KEY)) || { projects: [], machines: [], operators: [], transactions: [] };
  } catch {
    return { projects: [], machines: [], operators: [], transactions: [] };
  }
}

function writeStore(db) {
  localStorage.setItem(KEY, JSON.stringify(db));
}

function nextId(list) {
  return list.reduce((m, r) => Math.max(m, r.id || 0), 0) + 1;
}

const COLLECTIONS = ['projects', 'machines', 'operators', 'transactions'];

const PLURALS = {
  project: 'projects',
  machine: 'machines',
  operator: 'operators',
  transaction: 'transactions',
};

function mockInvoke(cmd, args = {}) {
  const db = readStore();

  if (cmd === 'get_dashboard_stats') {
    const p = db.projects;
    const t = db.transactions;
    const sum = (type) => t.filter((x) => x.transaction_type === type).reduce((a, x) => a + (Number(x.amount) || 0), 0);
    const income = sum('income');
    const expense = sum('expense');
    return Promise.resolve({
      total_projects: p.length,
      active_projects: p.filter((x) => x.status === 'active').length,
      total_machines: db.machines.length,
      active_machines: db.machines.filter((x) => x.status === 'active').length,
      total_operators: db.operators.length,
      total_income: income,
      total_expense: expense,
      net_profit: income - expense,
      recent_projects: [...p].slice(-5).reverse(),
    });
  }

  const listMatch = /^get_(\w+)$/.exec(cmd);
  if (listMatch && COLLECTIONS.includes(listMatch[1])) {
    return Promise.resolve([...db[listMatch[1]]].reverse());
  }

  const createMatch = /^create_(\w+)$/.exec(cmd);
  if (createMatch) {
    const key = PLURALS[createMatch[1]];
    const row = { ...args[createMatch[1]], id: nextId(db[key]), created_at: new Date().toISOString() };
    db[key].push(row);
    writeStore(db);
    return Promise.resolve(row.id);
  }

  const updateMatch = /^update_(\w+)$/.exec(cmd);
  if (updateMatch) {
    const key = PLURALS[updateMatch[1]];
    const row = args[updateMatch[1]];
    const i = db[key].findIndex((r) => r.id === row.id);
    if (i >= 0) db[key][i] = { ...db[key][i], ...row };
    writeStore(db);
    return Promise.resolve(null);
  }

  const deleteMatch = /^delete_(\w+)$/.exec(cmd);
  if (deleteMatch) {
    const key = PLURALS[deleteMatch[1]];
    db[key] = db[key].filter((r) => r.id !== args.id);
    writeStore(db);
    return Promise.resolve(null);
  }

  return Promise.reject(new Error(`Unknown command: ${cmd}`));
}

/* ───────────────────────────── exported API ───────────────────────────── */

function call(cmd, args) {
  return isNative ? nativeInvoke(cmd, args) : mockInvoke(cmd, args);
}

export const api = {
  dashboard: () => call('get_dashboard_stats'),

  listProjects: () => call('get_projects'),
  createProject: (project) => call('create_project', { project }),
  updateProject: (project) => call('update_project', { project }),
  deleteProject: (id) => call('delete_project', { id }),

  listMachines: () => call('get_machines'),
  createMachine: (machine) => call('create_machine', { machine }),
  updateMachine: (machine) => call('update_machine', { machine }),
  deleteMachine: (id) => call('delete_machine', { id }),

  listOperators: () => call('get_operators'),
  createOperator: (operator) => call('create_operator', { operator }),
  updateOperator: (operator) => call('update_operator', { operator }),
  deleteOperator: (id) => call('delete_operator', { id }),

  listTransactions: () => call('get_transactions'),
  createTransaction: (transaction) => call('create_transaction', { transaction }),
  updateTransaction: (transaction) => call('update_transaction', { transaction }),
  deleteTransaction: (id) => call('delete_transaction', { id }),
};
