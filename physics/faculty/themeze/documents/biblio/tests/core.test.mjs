import test from 'node:test'; import assert from 'node:assert/strict'; import { readFileSync } from 'node:fs';
import * as C from '../js/core.js';
const raw = JSON.parse(readFileSync(new URL('../catalog.json', import.meta.url)));
const docs = C.prepare(raw);

test('catalogue : ids uniques, 2318 fichiers, 16 dossiers, 55 documents annotés', () => {
  assert.equal(new Set(docs.map(d => d.id)).size, docs.length);
  assert.equal(docs.length, 2318); assert.equal(raw.folders.length, 16);
  assert.equal(docs.filter(d => d.meta).length, 55);
});
test('recherche : accents/casse indifférents, auteur, intersection, phrase exacte', () => {
  const a = C.search(docs, C.parseQuery('frederic helein')), b = C.search(docs, C.parseQuery('Frédéric HÉLEIN'));
  assert.ok(a.length > 0); assert.equal(a.length, b.length);
  assert.ok(C.search(docs, C.parseQuery('author:"Jules FILLETTE"')).every(r => r.doc.author.includes('Jules FILLETTE')));
  const u = C.search(docs, C.parseQuery('author:fillette category:cours'), { mode: 'union' }).length;
  const i = C.search(docs, C.parseQuery('author:fillette category:cours'), { mode: 'intersection' });
  assert.ok(i.length > 0 && i.length <= u && i.every(r => r.doc.author.join().includes('FILLETTE') && r.doc.category.includes('Cours')));
  assert.equal(C.parseQuery('type:pdf "ads cft"')[1].exact, true);
});
test('recherche : métadonnées des chemins corrigés (ex. Supergravity freedman) retrouvées', () => {
  assert.ok(C.search(docs, C.parseQuery('name:supergravity'), {}).some(r => r.doc.meta));
  assert.ok(C.search(docs, C.parseQuery('perihelie')).length > 0);
});
test('recherche : portée dossier + types', () => {
  const r = C.search(docs, [], { scope: 'M-Theory' }); assert.ok(r.length > 100 && r.every(x => x.doc.folder === 'M-Theory'));
  assert.ok(C.search(docs, C.parseQuery('type:pptx'), { kinds: ['doc'] }).every(x => x.doc.ext === 'pptx'));
});
test('double page : paires à gauche, impaires à droite, page 1 à droite', () => {
  assert.deepEqual(C.slots(1, 10, true), [null, 1]); assert.deepEqual(C.slots(2, 10, true), [2, 3]);
  assert.deepEqual(C.slots(3, 10, true), [2, 3]); assert.deepEqual(C.slots(10, 10, true), [10, null]);
  assert.deepEqual(C.slots(9, 9, true), [8, 9]); assert.deepEqual(C.slots(5, 10, false), [5]);
  for (let t = 1; t < 12; t++) for (let p = 1; p <= t; p++) { const [l, r] = C.slots(p, t, true); assert.ok(l === null || l % 2 === 0); assert.ok(r === null || r % 2 === 1); }
});
test('double page : navigation par paire, bornes, retour à la page 1', () => {
  assert.equal(C.nextPage(1, 10, true), 2); assert.equal(C.nextPage(2, 10, true), 4); assert.equal(C.nextPage(10, 10, true), 10);
  assert.equal(C.nextPage(9, 9, true), 9); assert.equal(C.prevPage(4, 10, true), 2); assert.equal(C.prevPage(2, 10, true), 1); assert.equal(C.prevPage(1, 10, true), 1);
  let p = 1, n = 0; while (C.nextPage(p, 11, true) !== p) { p = C.nextPage(p, 11, true); n++; } assert.equal(p, 10); assert.equal(n, 5);
});
test('tranches : abréviation ≤ max, sans débordement', () => {
  for (const d of docs.filter(x => x.kind === 'doc')) assert.ok(C.abbreviate(d.title, 18).length <= 19, d.title);
  assert.equal(C.abbreviate('Quantum Field Theory', 8).length <= 9, true);
});
test('bureaux : indépendance, progression, doublon, suppression, rechargement', () => {
  const mem = {}; const st = { getItem: k => mem[k] ?? null, setItem: (k, v) => { mem[k] = v; } };
  let s = C.createStore(st); const a = s.newDesk('Mécanique quantique'), b = s.newDesk('Relativité');
  s.addBook(a.id, 'x1'); s.addBook(a.id, 'x2'); s.addBook(b.id, 'x1');
  s.progress(a.id, 'x1', { page: 42 }); s.progress(b.id, 'x1', { page: 7 }); s.flush();
  let r = C.createStore(st);
  assert.equal(r.desk(a.id).books.find(x => x.id === 'x1').page, 42); assert.equal(r.desk(b.id).books[0].page, 7);
  r.addBook(a.id, 'x1'); assert.equal(r.desk(a.id).books.length, 2);          // pas de doublon
  const c = r.dupDesk(a.id); r.progress(c.id, 'x1', { page: 1 }); assert.equal(r.desk(a.id).books[0].page, 42);
  r.deleteDesk(a.id); assert.equal(r.desk(b.id).books.length, 1); assert.ok(r.state.active);
  r.toggleList('cart', 'x1'); r.toggleList('cart', 'x2'); r.move('cart', 'x2', -1); assert.deepEqual(r.state.cart, ['x2', 'x1']);
  assert.throws(() => r.importJSON('{"a":1}')); r.importJSON(r.exportJSON()); assert.equal(r.state.cart.length, 2);
});
test('persistance indisponible : pas de plantage', () => {
  const s = C.createStore({ getItem() { throw new Error('x'); }, setItem() { throw new Error('quota'); } });
  s.newDesk('A'); s.flush(); assert.equal(s.ok, false);
});
test('recommandations explicables', () => {
  const d = docs.find(x => x.meta && x.keywords.includes('Supergravity Models')); const r = C.related(d, docs, 5);
  assert.ok(r.length && r.every(x => x.why.length));
});
