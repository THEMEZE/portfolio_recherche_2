// core.js — logique pure (aucun accès DOM) : testable avec `node --test tests/`
export const fold = s => String(s ?? '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
export const clamp = (n, a, b) => Math.min(b, Math.max(a, n));
export const hash = s => { let h = 2166136261; for (const c of String(s)) h = Math.imul(h ^ c.charCodeAt(0), 16777619); return h >>> 0; };

/* ---------- Catalogue : enrichissement côté client (aucune duplication dans catalog.json) ---------- */
export function prepare(raw) {
  return raw.docs.map(d => {
    const parts = d.path.split('/'), dir = parts.slice(0, -1);
    const title = d.name.replace(/\.[^.]+$/, '').replace(/_+/g, ' ').trim();
    const kw = [...new Set([...dir, ...(d.keywords || [])])];           // comme search.html : dossiers = mots-clés hérités
    const doc = { ...d, title, dir, folder: dir[0] || '(racine)', author: d.author || [], category: d.category || [], keywords: kw };
    doc._f = { name: [fold(d.name), fold(title)], author: doc.author.map(fold), category: doc.category.map(fold),
               keywords: kw.map(fold), dir: dir.map(fold), ext: d.ext };
    return doc;
  });
}

/* ---------- Recherche (logique de search.html : tags typés, union/intersection, scores) ---------- */
const TYPES = ['author', 'keyword', 'category', 'name', 'folder', 'type'];
export function parseQuery(input) {
  const tags = [], re = /(?:(\w+):)?(?:"([^"]+)"|(\S+))/g; let m;
  while ((m = re.exec(input))) {
    const typ = m[1] && TYPES.includes(m[1].toLowerCase()) ? m[1].toLowerCase() : null;
    const value = m[2] ?? (m[1] && !typ ? m[1] + ':' + m[3] : m[3]);
    tags.push({ type: typ || 'text', value, exact: m[2] != null });
  }
  return tags;
}
const W = { name: [20, 10], author: [10, 5], category: [6, 3], keyword: [4, 2], folder: [6, 3] };  // [exact, partiel]
function hit(values, v) {      // meilleur score sur une liste de champs déjà normalisés
  let best = 0;
  for (const f of values) best = Math.max(best, f === v ? 2 : f.includes(v) ? 1 : 0);
  return best;
}
export function scoreTag(doc, tag) {
  const v = fold(tag.value), f = doc._f; if (!v) return 0;
  const by = { name: f.name, author: f.author, category: f.category, keyword: f.keywords, folder: f.dir };
  if (tag.type === 'type') return f.ext === v ? 8 : 0;
  const one = k => { const h = hit(by[k], v); return h ? W[k][h === 2 ? 0 : 1] : 0; };
  if (tag.type !== 'text') return one(tag.type);
  return Math.max(...['name', 'author', 'category', 'keyword', 'folder'].map(one));
}
export function search(docs, tags, { mode = 'union', scope = '', kinds = ['doc'] } = {}) {
  const pool = docs.filter(d => kinds.includes(d.kind) && (!scope || (d.dir.join('/') + '/').startsWith(scope + '/') || d.dir.join('/') === scope));
  if (!tags.length) return pool.map(doc => ({ doc, score: 0 }));
  const out = [];
  for (const doc of pool) {
    const s = tags.map(t => scoreTag(doc, t)), total = s.reduce((a, b) => a + b, 0);
    if (mode === 'intersection' ? s.every(x => x > 0) : total > 0) out.push({ doc, score: total });
  }
  return out.sort((a, b) => b.score - a.score || a.doc.title.localeCompare(b.doc.title, 'fr'));
}
export function suggest(docs, q, n = 10) {          // suggestions typées, insensibles aux accents/casse
  const v = fold(q), seen = new Map(); if (!v) return [];
  const add = (type, label) => { if (fold(label).includes(v) && !seen.has(type + label)) seen.set(type + label, { type, value: label }); };
  for (const d of docs) { if (d.kind !== 'doc') continue;
    d.keywords.forEach(k => add('keyword', k)); d.author.forEach(a => add('author', a)); d.category.forEach(c => add('category', c));
    if (d._f.name[0].includes(v)) add('name', d.name);
    if (seen.size > 400) break; }
  const rank = { keyword: 0, author: 1, category: 2, name: 3 };
  return [...seen.values()].sort((a, b) => fold(a.value).startsWith(v) !== fold(b.value).startsWith(v) ? (fold(a.value).startsWith(v) ? -1 : 1) : rank[a.type] - rank[b.type]).slice(0, n);
}
export const SORTS = {
  relevance: () => 0, title: (a, b) => a.title.localeCompare(b.title, 'fr'),
  author: (a, b) => (a.author[0] || '\uffff').localeCompare(b.author[0] || '\uffff', 'fr') || a.title.localeCompare(b.title, 'fr'),
  folder: (a, b) => a.dir.join('/').localeCompare(b.dir.join('/'), 'fr') || a.title.localeCompare(b.title, 'fr'),
  ext: (a, b) => a.ext.localeCompare(b.ext) || a.title.localeCompare(b.title, 'fr'),
};

/* ---------- Tranches (aspect seulement : aucune dimension physique n'existe dans les données) ---------- */
export function abbreviate(title, max) {
  const t = title.replace(/\.[a-z0-9]{2,4}$/i, '').replace(/_+/g, ' ').trim();
  if (t.length <= max) return t;
  const stop = /^(the|of|and|de|du|des|la|le|les|et|a|an|in|to|for|on|un|une|pdf)$/i;
  const sig = t.split(/[\s\-–—:,.()[\]]+/).filter(w => w && !stop.test(w));
  let out = '';
  for (const w of sig) { const n = (out + ' ' + w).trim(); if (n.length > max - 1) break; out = n; }
  if (out.length >= Math.min(6, max)) return out + '…';
  return sig.map(w => (/^\d/.test(w) ? w : w[0].toUpperCase())).join('').slice(0, max);
}
export function spineStyle(doc, folders) {
  const h = hash(doc.id), idx = Math.max(0, folders.indexOf(doc.folder));
  const thick = { pptx: 8, ppt: 8, docx: -4, doc: -4 }[doc.ext] || 0;
  return { w: 20 + (h % 22) + thick, h: 96 + ((h >> 6) % 46), hue: (idx * 47 + 8) % 360, sat: 24 + ((h >> 12) % 16), light: 27 + ((h >> 16) % 13) };
}

/* ---------- Double page : pages paires à gauche, impaires à droite ---------- */
export const DUAL_MIN = 880;   // largeur (px) du volet de lecture à partir de laquelle on passe en double page
export const leftOf = p => (p % 2 === 0 ? p : p - 1);
export function slots(p, total, dual) {   // pages affichées pour la page courante p ; null = emplacement vide
  p = clamp(p, 1, Math.max(1, total));
  if (!dual) return [p];
  const l = leftOf(p); return [l >= 1 ? l : null, l + 1 <= total ? l + 1 : null];
}
export function nextPage(p, total, dual) { if (!dual) return Math.min(p + 1, total); const n = leftOf(p) + 2; return n <= total ? n : p; }
export function prevPage(p, total, dual) { if (!dual) return Math.max(p - 1, 1); const n = leftOf(p) - 2; return n >= 1 ? n : 1; }

/* ---------- Recommandations explicables ---------- */
export function related(doc, docs, n = 6) {
  const res = [];
  for (const o of docs) {
    if (o.id === doc.id || o.kind !== 'doc') continue;
    const kw = o.keywords.filter(k => doc.keywords.includes(k) && !doc.dir.includes(k));
    const au = o.author.filter(a => doc.author.includes(a)), ca = o.category.filter(c => doc.category.includes(c));
    const sameDir = o.dir.join('/') === doc.dir.join('/');
    const score = kw.length * 3 + au.length * 4 + ca.length + (sameDir ? 2 : 0);
    if (score > 0 && (kw.length || au.length || sameDir)) res.push({ doc: o, score, why: [...kw.map(k => 'mot-clé « ' + k + ' »'), ...au.map(a => 'auteur ' + a), ...(sameDir ? ['même dossier'] : [])] });
  }
  return res.sort((a, b) => b.score - a.score).slice(0, n);
}

/* ---------- Persistance (localStorage, injectable pour les tests) ---------- */
export const defaultState = () => ({ v: 1, cart: [], favs: [], recent: [], desks: [], active: null, prefs: { mode: 'auto' } });
export const uid = () => Math.random().toString(36).slice(2, 9);
export function createStore(storage, key = 'biblio.v1') {
  let s; try { s = { ...defaultState(), ...JSON.parse(storage.getItem(key) || '{}') }; } catch { s = defaultState(); }
  let timer = null, ok = true; const subs = new Set();
  const flush = () => { clearTimeout(timer); timer = null; try { storage.setItem(key, JSON.stringify(s)); ok = true; } catch { ok = false; } };
  const touch = () => { clearTimeout(timer); timer = setTimeout(flush, 350); };   // sauvegarde différée
  const commit = () => { touch(); subs.forEach(f => f()); };
  const desk = id => s.desks.find(d => d.id === (id ?? s.active));
  const A = {
    get state() { return s; }, get ok() { return ok; }, flush, subscribe: f => (subs.add(f), () => subs.delete(f)), desk,
    toggleList(list, id) { const a = s[list], i = a.indexOf(id); i < 0 ? a.push(id) : a.splice(i, 1); commit(); },
    move(list, id, dir) { const a = s[list], i = a.indexOf(id), j = i + dir; if (i < 0 || j < 0 || j >= a.length) return; [a[i], a[j]] = [a[j], a[i]]; commit(); },
    clearCart() { s.cart = []; commit(); },
    newDesk(name) { const d = { id: uid(), name: name?.trim() || 'Bureau ' + (s.desks.length + 1), created: Date.now(), modified: Date.now(), books: [], current: null }; s.desks.push(d); s.active = d.id; commit(); return d; },
    renameDesk(id, name) { const d = desk(id); if (d && name.trim()) { d.name = name.trim(); d.modified = Date.now(); commit(); } },
    dupDesk(id) { const d = desk(id); if (!d) return; const c = JSON.parse(JSON.stringify(d)); Object.assign(c, { id: uid(), name: d.name + ' (copie)', created: Date.now(), modified: Date.now() }); s.desks.push(c); s.active = c.id; commit(); return c; },
    deleteDesk(id) { s.desks = s.desks.filter(d => d.id !== id); if (s.active === id) s.active = s.desks[0]?.id ?? null; commit(); },   // ne touche jamais aux fichiers
    setActive(id) { if (desk(id)) { s.active = id; commit(); } },
    addBook(deskId, docId, open = true) {
      const d = desk(deskId); if (!d) return null; let b = d.books.find(x => x.id === docId);
      if (!b) { b = { id: docId, page: 1, zoom: 1, open, added: Date.now(), t: 0 }; d.books.push(b); }
      if (open) { b.open = true; d.current = docId; } d.modified = Date.now(); commit(); return b;
    },
    removeBook(deskId, docId) { const d = desk(deskId); if (!d) return; d.books = d.books.filter(b => b.id !== docId); if (d.current === docId) d.current = d.books.find(b => b.open)?.id ?? d.books[0]?.id ?? null; commit(); },
    closeBook(deskId, docId) { const d = desk(deskId), b = d?.books.find(x => x.id === docId); if (!b) return; b.open = false; if (d.current === docId) d.current = d.books.find(x => x.open)?.id ?? null; commit(); },
    selectBook(deskId, docId) { const d = desk(deskId), b = d?.books.find(x => x.id === docId); if (!b) return; b.open = true; b.t = Date.now(); d.current = docId; this.pushRecent(docId); commit(); },
    moveBook(deskId, docId, dir) { const d = desk(deskId); if (!d) return; const a = d.books, i = a.findIndex(b => b.id === docId), j = i + dir; if (i < 0 || j < 0 || j >= a.length) return; [a[i], a[j]] = [a[j], a[i]]; commit(); },
    progress(deskId, docId, patch) { const d = desk(deskId), b = d?.books.find(x => x.id === docId); if (!b) return; Object.assign(b, patch, { t: Date.now() }); d.modified = Date.now(); touch(); },  // sans re-rendu
    pref(k, v) { s.prefs[k] = v; touch(); },
    pushRecent(id) { s.recent = [{ id, t: Date.now() }, ...s.recent.filter(r => r.id !== id)].slice(0, 30); },
    desksHaving: id => s.desks.filter(d => d.books.some(b => b.id === id)),
    exportJSON: () => JSON.stringify(s, null, 1),
    importJSON(txt) { const o = JSON.parse(txt); if (!o || !Array.isArray(o.desks) || !Array.isArray(o.cart)) throw new Error('Fichier de sauvegarde invalide'); Object.keys(s).forEach(k => delete s[k]); Object.assign(s, defaultState(), o); commit(); }   // en place : les références à state restent valides,
  };
  return A;
}
