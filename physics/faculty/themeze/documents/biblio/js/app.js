// app.js — vues Bibliothèque / Dossiers / Recherche / Panier / Bureaux, reliées à un unique store et à un unique catalogue
import * as C from './core.js';
import { Reader, readable } from './reader.js';

const $ = (s, r = document) => r.querySelector(s), $$ = (s, r = document) => [...r.querySelectorAll(s)];
const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
let memOnly = false, storage;
try { localStorage.setItem('_t', '1'); localStorage.removeItem('_t'); storage = localStorage; }
catch { memOnly = true; const m = {}; storage = { getItem: k => m[k] ?? null, setItem: (k, v) => { m[k] = v; } }; }
const store = C.createStore(storage), st = store.state;
const main = $('#main');
let raw, docs, byId, BASE, reader = null, mounted = null, dispose = null, tree = null;
const S = { tags: [], mode: 'union', scope: '', sort: 'relevance', all: false, cap: 150 };   // état de filtre partagé entre les espaces
const url = d => BASE + d.path.split('/').map(encodeURIComponent).join('/');
const kinds = () => (S.all ? ['doc', 'media', 'code', 'other'] : ['doc']);
const unsorted = () => S.sort === 'relevance' && S.tags.length;
function results(scope = S.scope) {
  const r = C.search(docs, S.tags, { mode: S.mode, scope, kinds: kinds() });
  return unsorted() ? r.map(x => x.doc) : r.map(x => x.doc).sort(C.SORTS[S.sort === 'relevance' ? 'folder' : S.sort]);
}
const empty = (t, sub = '') => `<div class="empty"><p><strong>${esc(t)}</strong></p>${sub ? `<p>${sub}</p>` : ''}</div>`;
const deskNames = id => store.desksHaving(id).map(d => d.name);

/* ---------- modale minimale (focus géré, Échap) ---------- */
function modal(html, onSubmit) {
  const o = document.createElement('div'); o.className = 'overlay';
  o.innerHTML = `<form class="modal" role="dialog" aria-modal="true">${html}<div class="mbtn"><button type="button" data-x>Annuler</button><button class="primary">OK</button></div></form>`;
  const prev = document.activeElement, close = () => { o.remove(); prev?.focus?.(); };
  o.addEventListener('click', e => { if (e.target === o || e.target.hasAttribute('data-x')) close(); });
  o.addEventListener('keydown', e => { if (e.key === 'Escape') close(); });
  o.firstChild.addEventListener('submit', e => { e.preventDefault(); onSubmit(new FormData(e.target)); close(); });
  document.body.append(o); (o.querySelector('input:checked, input, button.primary')).focus();
}
function pickDesk(ids) {
  const ds = st.desks;
  modal(`<h2>${ids.length > 1 ? ids.length + ' documents' : 'Document'} → bureau</h2><fieldset><legend>Bureau de lecture</legend>
    ${ds.map(d => `<label class="rd"><input type="radio" name="desk" value="${d.id}" ${d.id === st.active ? 'checked' : ''}> ${esc(d.name)} <small>(${d.books.length} livres)</small></label>`).join('')}
    <label class="rd"><input type="radio" name="desk" value="__new" ${ds.length ? '' : 'checked'}> Nouveau bureau : <input name="nn" placeholder="Nom du bureau"></label></fieldset>`,
  f => { let id = f.get('desk'); if (id === '__new') id = store.newDesk(f.get('nn')).id; ids.forEach(i => store.addBook(id, i, false)); toast(`Ajouté à « ${store.desk(id).name} »`); });
}
function toast(t) { const el = $('#toast'); el.textContent = t; el.hidden = false; clearTimeout(toast.t); toast.t = setTimeout(() => (el.hidden = true), 2600); }
function openDoc(id) {
  const d = store.desk() || store.newDesk();
  store.addBook(d.id, id, true); store.selectBook(d.id, id); location.hash = '#/desk/' + d.id;
}

/* ---------- composants communs ---------- */
const badges = d => `${store.state.cart.includes(d.id) ? '<span class="bd c" title="Dans le panier">panier</span>' : ''}${deskNames(d.id).map(n => `<span class="bd d" title="Dans le bureau">${esc(n)}</span>`).join('')}${st.favs.includes(d.id) ? '<span class="bd f">★</span>' : ''}`;
const btns = d => `<button data-act="cart" data-id="${d.id}" aria-pressed="${st.cart.includes(d.id)}">${st.cart.includes(d.id) ? '− Panier' : '+ Panier'}</button>
  <button data-act="todesk" data-id="${d.id}">+ Bureau</button><button data-act="fav" data-id="${d.id}" aria-pressed="${st.favs.includes(d.id)}" aria-label="Favori">${st.favs.includes(d.id) ? '★' : '☆'}</button>`;
const row = (d, extra = '') => `<li class="row"><div class="rt"><button class="lk" data-act="open" data-id="${d.id}">${esc(d.title)}</button><span class="ext">${esc(d.ext)}</span>${badges(d)}</div>
  <div class="rm">${esc(d.author.join(', '))}${d.author.length ? ' · ' : ''}${esc(d.dir.join(' › '))}${d.category.length ? ' · ' + esc(d.category.join(', ')) : ''}</div>
  <div class="ra"><button class="primary" data-act="open" data-id="${d.id}">${readable(d.ext) ? 'Lire' : 'Ouvrir'}</button>${btns(d)}<a class="btn" href="${esc(url(d))}" target="_blank" rel="noopener" aria-label="Ouvrir l’original dans un nouvel onglet">↗</a>${extra}</div></li>`;
const list = (ds, more = true) => ds.length ? `<ul class="rows">${ds.slice(0, S.cap).map(d => row(d)).join('')}</ul>${more && ds.length > S.cap ? `<button class="more" data-act="more">Afficher plus (${ds.length - S.cap} restants)</button>` : ''}` : empty('Aucun document ne correspond.', 'Essayez d’élargir les filtres, ou cochez « Tous formats ».');

function filterHtml() {
  return `<div class="filter"><div class="box"><span id="chips"></span><input id="q" type="search" placeholder="Titre, auteur:…, categorie:…, « expression exacte »" autocomplete="off" aria-label="Ajouter un filtre (Entrée)" aria-controls="sug"></div><ul id="sug" role="listbox" hidden></ul>
  <div class="opts"><span role="group" aria-label="Combinaison des filtres"><button data-act="mode" data-v="union">Union</button><button data-act="mode" data-v="intersection">Intersection</button></span>
  <label>Tri <select id="sort"><option value="relevance">Pertinence / dossier</option><option value="title">Titre</option><option value="author">Auteur</option><option value="folder">Dossier</option><option value="ext">Format</option></select></label>
  <label><input type="checkbox" id="all"> Tous formats</label><button data-act="reset">Réinitialiser</button></div><p id="count" class="count" aria-live="polite"></p></div>`;
}
const TL = { keyword: 'mot-clé', author: 'auteur', category: 'catégorie', name: 'nom', folder: 'dossier', type: 'format', text: 'texte' };
function paintFilter(n, total) {
  $('#chips').innerHTML = (S.scope ? `<span class="tag folder">dossier : ${esc(S.scope)}<button data-act="unscope" aria-label="Retirer la limite au dossier">×</button></span>` : '') +
    S.tags.map((t, i) => `<span class="tag ${t.type}">${TL[t.type]} : ${esc(t.value)}<button data-act="tagrm" data-i="${i}" aria-label="Retirer le filtre ${esc(t.value)}">×</button></span>`).join('');
  $$('[data-act=mode]').forEach(b => b.setAttribute('aria-pressed', b.dataset.v === S.mode));
  $('#sort').value = S.sort; $('#all').checked = S.all;
  $('#count').textContent = `${n} document${n > 1 ? 's' : ''}${S.tags.length || S.scope ? ' correspondant aux filtres' : ''} (sur ${total} dans le catalogue${S.all ? ', tous formats' : ''})`;
}
function mountFilter(refresh) {
  const q = $('#q'), sug = $('#sug');
  const add = txt => { C.parseQuery(txt).forEach(t => { if (!S.tags.some(x => x.type === t.type && x.value === t.value)) S.tags.push(t); }); q.value = ''; sug.hidden = true; S.cap = 150; refresh(); };
  q.addEventListener('input', () => {
    const s = C.suggest(docs, q.value); sug.hidden = !s.length;
    sug.innerHTML = s.map(x => `<li role="option" tabindex="-1" data-act="sugpick" data-t="${x.type}" data-v="${esc(x.value)}"><span class="tag ${x.type}">${TL[x.type]}</span> ${esc(x.value)}</li>`).join('');
  });
  q.addEventListener('keydown', e => {
    if (e.key === 'Enter' && q.value.trim()) { e.preventDefault(); add(q.value); }
    else if (e.key === 'Backspace' && !q.value && S.tags.length) { S.tags.pop(); refresh(); }
    else if (e.key === 'Escape') sug.hidden = true;
  });
  $('#sort').addEventListener('change', e => { S.sort = e.target.value; refresh(); });
  $('#all').addEventListener('change', e => { S.all = e.target.checked; tree = null; refresh(); });
}

/* ---------- Bibliothèque ---------- */
let pinned = null, hideT = 0;
function spine(d, s) { return `<button class="spine" data-id="${d.id}" style="--w:${s.w}px;--h:${s.h}px;--c:hsl(${s.hue} ${s.sat}% ${s.light}%)" aria-label="${esc(d.title)}" aria-haspopup="dialog"><span class="lbl">${esc(C.abbreviate(d.title, Math.floor(s.h / 7.4)))}</span></button>`; }
function paintMarks() {
  const inDesk = new Set(st.desks.flatMap(d => d.books.map(b => b.id)));
  $$('.spine').forEach(el => { const id = el.dataset.id; el.classList.toggle('indesk', inDesk.has(id)); el.classList.toggle('incart', st.cart.includes(id)); el.classList.toggle('fav', st.favs.includes(id)); });
}
function libraryView() {
  main.innerHTML = `<section class="lib"><h1>Bibliothèque</h1><p class="legend"><span class="k d"></span> dans un bureau <span class="k c"></span> dans le panier <span class="k f">★</span> favori · survolez, touchez ou focalisez une tranche pour sortir le livre</p>${filterHtml()}
  <label class="jump">Aller à l’étagère <select id="jump" aria-label="Aller à un dossier"></select></label><div id="shelves" class="case"></div></section>`;
  let lastW = 0;
  const draw = () => {
    const ds = results(), host = $('#shelves'), W = host.clientWidth - 36 || 900;
    paintFilter(ds.length, docs.filter(d => kinds().includes(d.kind)).length);
    if (!ds.length) { host.innerHTML = empty('Aucun livre sur ces étagères.', 'Réinitialisez les filtres.'); return; }
    const byFolder = !unsorted() && (S.sort === 'folder' || S.sort === 'relevance'), rows = []; let r = null, used = 0;
    for (const d of ds) {
      const s = C.spineStyle(d, raw.folders);
      if (!r || used + s.w + 3 > W || (byFolder && r.f !== d.folder)) { r = { f: d.folder, it: [] }; rows.push(r); used = 0; }
      r.it.push(spine(d, s)); used += s.w + 3;
    }
    host.innerHTML = rows.map((x, i) => `<div class="shelf" data-folder="${esc(x.f)}"><div class="slabel">Étagère ${i + 1} · ${esc(x.f)}</div><div class="books">${x.it.join('')}</div><div class="plank"></div></div>`).join('');
    const fs = [...new Set(rows.map(x => x.f))]; $('#jump').innerHTML = '<option value="">—</option>' + fs.map(f => `<option>${esc(f)}</option>`).join('');
    paintMarks();
  };
  mountFilter(draw); draw(); window.__refreshView = draw;
  $('#jump').addEventListener('change', e => e.target.value && $$('.shelf').find(s => s.dataset.folder === e.target.value)?.scrollIntoView({ behavior: 'smooth', block: 'start' }));
  const ro = new ResizeObserver(() => { const w = $('#shelves').clientWidth; if (Math.abs(w - lastW) > 40) { lastW = w; clearTimeout(libraryView.t); libraryView.t = setTimeout(draw, 150); } }); ro.observe($('#shelves'));
  dispose = () => { ro.disconnect(); hideCard(true); };
}
const card = $('#card');
function cardHtml(d) {
  const s = C.spineStyle(d, raw.folders), rel = d.meta ? C.related(d, docs, 3) : [], ds = deskNames(d.id);
  return `<div class="cover" style="--c:hsl(${s.hue} ${s.sat}% ${s.light}%)"><span class="cv-f">${esc(d.folder)}</span><span class="cv-t">${esc(d.title)}</span><span class="cv-a">${esc(d.author.join(' · '))}</span><span class="cv-e">${esc(d.ext.toUpperCase())}</span></div>
  <div class="cinfo"><h2>${esc(d.title)}</h2>${d.author.length ? `<p>${esc(d.author.join(', '))}</p>` : ''}<p class="sm">${esc(d.dir.join(' › '))}${d.category.length ? ' · ' + esc(d.category.join(', ')) : ''}</p>
  ${d.meta ? `<p class="sm">${esc(d.keywords.filter(k => !d.dir.includes(k)).slice(0, 6).join(' · '))}</p>` : '<p class="sm">Pas de métadonnées détaillées (auteur, catégorie, mots-clés).</p>'}
  ${ds.length ? `<p class="sm">Dans : ${esc(ds.join(', '))}</p>` : ''}${rel.length ? `<p class="sm">Proches : ${rel.map(r => `<button class="lk" data-act="focus" data-id="${r.doc.id}" title="${esc(r.why.join(', '))}">${esc(C.abbreviate(r.doc.title, 28))}</button>`).join(' ')}</p>` : ''}
  <div class="ra"><button class="primary" data-act="open" data-id="${d.id}">${readable(d.ext) ? 'Lire' : 'Ouvrir'}</button>${btns(d)}<a class="btn" href="${esc(url(d))}" target="_blank" rel="noopener">↗</a></div></div>`;
}
function showCard(id, el, pin) {
  clearTimeout(hideT); const d = byId.get(id); if (!d) return; pinned = pin ? id : (pinned && pinned !== id ? null : pinned);
  $$('.spine.sel').forEach(x => x.classList.remove('sel')); el.classList.add('sel');
  card.innerHTML = cardHtml(d); card.dataset.id = id; card.hidden = false; card.classList.toggle('pin', !!pin);
  const r = el.getBoundingClientRect(), cw = card.offsetWidth, ch = card.offsetHeight;
  if (matchMedia('(pointer:coarse), (max-width:700px)').matches) { card.style.left = card.style.top = ''; return; }
  let x = r.right + 10; if (x + cw > innerWidth - 8) x = Math.max(8, r.left - cw - 10);
  card.style.left = x + 'px'; card.style.top = Math.max(8, Math.min(r.top - 20, innerHeight - ch - 8)) + 'px';
}
function hideCard(force) { if (pinned && !force) return; pinned = null; card.hidden = true; $$('.spine.sel').forEach(x => x.classList.remove('sel')); }

/* ---------- Dossiers ---------- */
function buildTree() {
  const root = { name: '', path: '', kids: new Map(), n: 0, docs: [] };
  for (const d of docs) { if (!kinds().includes(d.kind)) continue; let n = root; n.n++;
    d.dir.forEach((seg, i) => { let k = n.kids.get(seg); if (!k) n.kids.set(seg, k = { name: seg, path: d.dir.slice(0, i + 1).join('/'), kids: new Map(), n: 0, docs: [] }); k.n++; n = k; });
    n.docs.push(d); }
  return root;
}
const nodeAt = (root, p) => p ? p.split('/').reduce((n, s) => n?.kids.get(s), root) : root;
const treeHtml = (n, cur) => `<ul>${[...n.kids.values()].sort((a, b) => a.name.localeCompare(b.name, 'fr')).map(k => `<li><details ${cur === k.path || cur.startsWith(k.path + '/') ? 'open' : ''}><summary><a href="#/folders/${encodeURIComponent(k.path)}" ${cur === k.path ? 'aria-current="page"' : ''}>${esc(k.name)} <span class="n">${k.n}</span></a></summary>${treeHtml(k, cur)}</details></li>`).join('')}</ul>`;
function foldersView(cur) {
  tree = tree || buildTree();
  const draw = () => {
    tree = buildTree(); const n = nodeAt(tree, cur); $('#ftree').innerHTML = treeHtml(tree, cur);
    if (!n) { $('#fbody').innerHTML = empty('Dossier introuvable.', '<a href="#/folders">Retour à la racine</a>'); return; }
    const parts = cur ? cur.split('/') : [], searching = S.tags.length > 0;
    const ds = searching ? results(cur) : n.docs.slice().sort(C.SORTS[S.sort === 'relevance' ? 'title' : S.sort]);
    paintFilter(ds.length, n.n);
    $('#fbody').innerHTML = `<nav class="crumbs" aria-label="Chemin"><a href="#/folders">Racine</a>${parts.map((p, i) => ` › <a href="#/folders/${encodeURIComponent(parts.slice(0, i + 1).join('/'))}">${esc(p)}</a>`).join('')}</nav>
      <p class="fact">${cur ? `<a class="btn" href="#/folders/${encodeURIComponent(parts.slice(0, -1).join('/'))}">↑ Dossier parent</a> ` : ''}<button data-act="scope-search" data-p="${esc(cur)}">Rechercher dans ce dossier</button> <button data-act="scope-lib" data-p="${esc(cur)}">Voir sur les étagères</button> <a class="btn" href="#/cart">Panier (${st.cart.length})</a></p>
      ${!searching && n.kids.size ? `<ul class="subs">${[...n.kids.values()].sort((a, b) => a.name.localeCompare(b.name, 'fr')).map(k => `<li><a href="#/folders/${encodeURIComponent(k.path)}">${esc(k.name)}<span class="n">${k.n}</span></a></li>`).join('')}</ul>` : ''}
      <h2>${searching ? 'Résultats dans ce dossier' : 'Documents de ce dossier'} <span class="n">${ds.length}</span></h2>${list(ds)}`;
  };
  main.innerHTML = `<section class="fold"><h1>Dossiers</h1>${filterHtml()}<div class="fwrap"><nav id="ftree" aria-label="Arborescence"></nav><div id="fbody"></div></div></section>`;
  mountFilter(draw); draw(); dispose = () => { tree = null; };
  window.__refreshView = draw;
}

/* ---------- Recherche + découverte ---------- */
function discoveryHtml() {
  const lastBooks = st.desks.flatMap(d => d.books.filter(b => b.page > 1 && b.t).map(b => ({ d, b }))).sort((a, b) => b.b.t - a.b.t).slice(0, 6);
  const pick = ids => ids.map(i => byId.get(i)).filter(Boolean);
  const cats = {}, kws = {}; docs.forEach(d => { if (!d.meta) return; d.category.forEach(c => cats[c] = (cats[c] || 0) + 1); d.keywords.filter(k => !d.dir.includes(k)).forEach(k => kws[k] = (kws[k] || 0) + 1); });
  const chip = (t, v, n) => `<button class="chip" data-act="chip" data-t="${t}" data-v="${esc(v)}">${esc(v)} <span class="n">${n}</span></button>`;
  const seedId = st.recent[0]?.id || st.favs[0], seed = byId.get(seedId), rel = seed ? C.related(seed, docs, 5) : [];
  const sec = (h, body) => body ? `<section class="disc"><h2>${h}</h2>${body}</section>` : '';
  const mini = ds => `<ul class="mini">${ds.map(d => `<li><button class="lk" data-act="open" data-id="${d.id}">${esc(C.abbreviate(d.title, 60))}</button></li>`).join('')}</ul>`;
  return sec('Reprendre la lecture', lastBooks.length ? `<ul class="mini">${lastBooks.map(({ d, b }) => { const doc = byId.get(b.id); return doc ? `<li><button class="lk" data-act="resume" data-d="${d.id}" data-id="${b.id}">${esc(C.abbreviate(doc.title, 50))}</button> <small>p. ${b.page}${b.pages ? '/' + b.pages : ''} · ${esc(d.name)}</small></li>` : ''; }).join('')}</ul>` : '')
    + sec('Consultés récemment', pick(st.recent.map(r => r.id)).length ? mini(pick(st.recent.map(r => r.id)).slice(0, 8)) : '')
    + sec('Favoris', st.favs.length ? mini(pick(st.favs).slice(0, 10)) : '')
    + sec('Par catégorie (documents annotés)', Object.entries(cats).sort((a, b) => b[1] - a[1]).map(([c, n]) => chip('category', c, n)).join(' '))
    + sec('Thèmes fréquents (mots-clés)', Object.entries(kws).sort((a, b) => b[1] - a[1]).slice(0, 24).map(([k, n]) => chip('keyword', k, n)).join(' '))
    + sec(`Thèmes proches de « ${esc(seed?.title || '')} »`, rel.length ? `<ul class="mini">${rel.map(r => `<li><button class="lk" data-act="open" data-id="${r.doc.id}">${esc(C.abbreviate(r.doc.title, 50))}</button> <small>car ${esc(r.why.slice(0, 3).join(', '))}</small></li>`).join('')}</ul>` : '')
    + `<p class="note">Les suggestions reposent uniquement sur les métadonnées du catalogue (${docs.filter(d => d.meta).length} documents annotés sur ${docs.filter(d => d.kind === 'doc').length}) : mots-clés, auteur, catégorie, dossier. « Récemment ajoutés » n’est pas proposé : <code>docs.json</code> ne contient aucune date. La recherche ne porte pas sur le texte des PDF (aucun index de contenu).</p>`;
}
function searchView() {
  main.innerHTML = `<section class="srch"><h1>Recherche</h1>${filterHtml()}<div id="res"></div></section>`;
  const draw = () => {
    const ds = results(); paintFilter(ds.length, docs.filter(d => kinds().includes(d.kind)).length);
    $('#res').innerHTML = S.tags.length || S.scope ? list(ds) : discoveryHtml();
  };
  mountFilter(draw); draw(); window.__refreshView = draw;
}

/* ---------- Panier ---------- */
function cartView() {
  const ds = st.cart.map(i => byId.get(i)).filter(Boolean), free = ds.filter(d => !store.desksHaving(d.id).length);
  main.innerHTML = `<section class="cart"><h1>Panier <span class="n">${ds.length}</span></h1>
  ${ds.length ? `<p class="fact"><button class="primary" data-act="cartdesk">Tout ajouter à un bureau…</button> ${free.length && free.length < ds.length ? `<button data-act="cartdesk-free">Ajouter les ${free.length} non affectés…</button>` : ''} <button data-act="cartclear">Vider le panier</button></p>
  <ol class="rows num">${ds.map((d, i) => row(d, `<button data-act="cartup" data-id="${d.id}" aria-label="Monter" ${i ? '' : 'disabled'}>↑</button><button data-act="cartdown" data-id="${d.id}" aria-label="Descendre" ${i < ds.length - 1 ? '' : 'disabled'}>↓</button>`).replace(/\+ Panier|− Panier/, 'Retirer')).join('')}</ol>` : empty('Votre panier est vide.', 'Ajoutez des livres depuis <a href="#/library">la bibliothèque</a>, <a href="#/folders">les dossiers</a> ou <a href="#/search">la recherche</a>. Le panier est une sélection temporaire, conservée dans ce navigateur.')}</section>`;
}

/* ---------- Bureaux + lecteur ---------- */
function disposeReader() { reader?.destroy(); reader = null; mounted = null; }
function deskView(id) {
  const d0 = store.desk(id);
  if (!d0) { main.innerHTML = `<section class="deskempty">${empty('Aucun bureau de lecture.', 'Un bureau regroupe plusieurs livres et mémorise la page de chacun.')}<p class="fact"><button class="primary" data-act="deskNew">Créer un bureau</button> <label class="btn">Importer une sauvegarde<input type="file" id="imp" accept="application/json" hidden></label></p></section>`; return; }
  if (st.active !== d0.id) { st.active = d0.id; store.flush(); }
  main.innerHTML = `<section class="deskwrap"><div class="deskhead"><label>Bureau <select id="deskSel"></select></label>
    <button data-act="deskNew">+ Nouveau</button><button data-act="deskRename">Renommer</button><button data-act="deskDup">Dupliquer</button><button data-act="deskDel">Supprimer</button>
    <details class="more"><summary>Sauvegarde</summary><button data-act="export">Exporter (JSON)</button> <label class="btn">Importer<input type="file" id="imp" accept="application/json" hidden></label></details></div>
  <div class="desk"><aside id="books" aria-label="Livres du bureau"></aside><section class="stage"><div id="tabs" role="tablist" aria-label="Livres ouverts"></div>
  <div id="bar" class="bar"><button data-act="prev" aria-label="Page précédente">‹</button><label>Page <input id="pn" type="number" min="1" inputmode="numeric" aria-label="Numéro de page"> / <span id="pt">–</span></label><button data-act="next" aria-label="Page suivante">›</button>
  <span class="sep"></span><button data-act="zoomout" aria-label="Zoom arrière">−</button><span id="zv">100 %</span><button data-act="zoomin" aria-label="Zoom avant">+</button><button data-act="zoom1">Ajuster</button><button data-act="modecycle" id="mb" title="Affichage : auto / double page / une page">Auto</button>
  <a id="orig" class="btn" target="_blank" rel="noopener">Original ↗</a><progress id="prog" max="100" value="0" aria-label="Progression de lecture"></progress></div>
  <div id="err" role="alert" hidden></div><div id="host" class="host" tabindex="0" aria-label="Zone de lecture"></div></section></div></section>`;
  paintDesk(); dispose = () => { disposeReader(); };
}
function paintDesk() {
  const d = store.desk(); if (!d || !$('#deskSel')) return;
  $('#deskSel').innerHTML = st.desks.map(x => `<option value="${x.id}" ${x.id === d.id ? 'selected' : ''}>${esc(x.name)} (${x.books.length})</option>`).join('');
  $('#books').innerHTML = d.books.length ? `<h2>Livres (${d.books.length})</h2><ul>${d.books.map((b, i) => { const doc = byId.get(b.id); if (!doc) return `<li class="bk">Document introuvable <button data-act="bookRm" data-id="${b.id}">Retirer</button></li>`;
    return `<li class="bk ${b.id === d.current ? 'cur' : ''} ${b.open ? 'open' : ''}" id="bk-${b.id}"><button class="bt" data-act="bookSel" data-id="${b.id}" title="${esc(doc.title)}">${esc(C.abbreviate(doc.title, 42))}</button>
    <small class="bp">${b.pages ? `p. ${b.page}/${b.pages}` : b.page > 1 ? `p. ${b.page}` : 'non commencé'}</small><span class="ba"><button data-act="bookUp" data-id="${b.id}" aria-label="Monter" ${i ? '' : 'disabled'}>↑</button><button data-act="bookDown" data-id="${b.id}" aria-label="Descendre" ${i < d.books.length - 1 ? '' : 'disabled'}>↓</button>${b.open ? `<button data-act="bookClose" data-id="${b.id}">Fermer</button>` : ''}<button data-act="bookRm" data-id="${b.id}">Retirer</button></span></li>`; }).join('')}</ul><p class="sm">« Fermer » garde la page de reprise ; « Retirer » enlève le livre du bureau (jamais le fichier).</p>` : empty('Bureau vide.', 'Ajoutez des livres depuis <a href="#/cart">le panier</a> ou <a href="#/library">la bibliothèque</a>.');
  const open = d.books.filter(b => b.open).sort((a, b) => (b.t || 0) - (a.t || 0));
  $('#tabs').innerHTML = open.map(b => { const doc = byId.get(b.id); return doc ? `<button role="tab" aria-selected="${b.id === d.current}" data-act="bookSel" data-id="${b.id}" title="${esc(doc.title)}">${esc(C.abbreviate(doc.title, 22))}</button>` : ''; }).join('');
  ensureReader(d);
}
function paintBar(p, t) {
  const d = store.desk(), b = d?.books.find(x => x.id === d.current); if (!b) return;
  $('#pn').value = p; $('#pn').max = t; $('#pt').textContent = t; $('#prog').value = t > 1 ? Math.round((p - 1) / (t - 1) * 100) : 100;
  $('#zv').textContent = Math.round((reader?.zoom ?? b.zoom) * 100) + ' %';
  const el = $(`#bk-${b.id} .bp`); if (el) el.textContent = `p. ${p}/${t}`;
}
function ensureReader(d) {
  const b = d.books.find(x => x.id === d.current), doc = b && byId.get(b.id), host = $('#host'), bar = $('#bar'), err = $('#err');
  if (mounted && b && mounted.deskId === d.id && mounted.bookId === b.id) return;
  disposeReader(); err.hidden = true;
  bar.hidden = !doc; host.innerHTML = '';
  if (!doc) { host.innerHTML = empty('Aucun livre ouvert.', 'Choisissez un livre dans la liste, ou ajoutez-en depuis la bibliothèque.'); return; }
  $('#orig').href = url(doc);
  if (!readable(doc.ext)) { bar.hidden = true; host.innerHTML = empty(`Le format .${doc.ext} ne peut pas être lu dans le lecteur intégré.`, `Seuls les PDF et les images sont affichables ici. <a class="btn" href="${esc(url(doc))}" target="_blank" rel="noopener" download>Ouvrir / télécharger l’original</a>`); mounted = { deskId: d.id, bookId: b.id }; return; }
  mounted = { deskId: d.id, bookId: b.id };
  reader = new Reader(host, {
    onPage: (p, t) => { err.hidden = true; store.progress(d.id, b.id, { page: p, pages: t }); paintBar(p, t); },
    onZoom: z => store.progress(d.id, b.id, { zoom: z }),
    onMode: dual => { $('#mb').textContent = { auto: 'Auto', 2: 'Double page', 1: 'Une page' }[st.prefs.mode] + (st.prefs.mode === 'auto' ? (dual ? ' (2 p.)' : ' (1 p.)') : ''); },
    onError: (msg, retry) => { err.hidden = false; err.innerHTML = `<p>${esc(msg).replace(/\n/g, '<br>')}</p><button id="retry">Réessayer</button> <a class="btn" href="${esc(url(doc))}" target="_blank" rel="noopener">Ouvrir l’original ↗</a>`; $('#retry').onclick = () => { err.hidden = true; retry(); }; },
  });
  reader.open(url(doc), { page: b.page, zoom: b.zoom, mode: st.prefs.mode, ext: doc.ext });
}

/* ---------- actions (délégation) ---------- */
const A = {
  open: id => openDoc(id), cart: id => store.toggleList('cart', id), fav: id => store.toggleList('favs', id), todesk: id => pickDesk([id]),
  focus: id => { const el = $(`.spine[data-id="${id}"]`); el ? (el.scrollIntoView({ block: 'center' }), showCard(id, el, true)) : openDoc(id); },
  cartup: id => store.move('cart', id, -1), cartdown: id => store.move('cart', id, 1), cartclear: () => confirm('Vider le panier ? (les fichiers ne sont pas touchés)') && store.clearCart(),
  cartdesk: () => pickDesk(st.cart.slice()), 'cartdesk-free': () => pickDesk(st.cart.filter(i => !store.desksHaving(i).length)),
  more: () => { S.cap += 150; window.__refreshView?.(); }, mode: (_, el) => { S.mode = el.dataset.v; refreshAll(); }, unscope: () => { S.scope = ''; refreshAll(); },
  tagrm: (_, el) => { S.tags.splice(+el.dataset.i, 1); refreshAll(); }, reset: () => { S.tags = []; S.scope = ''; S.all = false; S.sort = 'relevance'; S.mode = 'union'; refreshAll(); },
  sugpick: (_, el) => { S.tags.push({ type: el.dataset.t, value: el.dataset.v, exact: false }); refreshAll(); },
  chip: (_, el) => { S.tags.push({ type: el.dataset.t, value: el.dataset.v, exact: false }); refreshAll(); },
  'scope-search': (_, el) => { S.scope = el.dataset.p; location.hash = '#/search'; }, 'scope-lib': (_, el) => { S.scope = el.dataset.p; location.hash = '#/library'; },
  resume: (_, el) => { store.setActive(el.dataset.d); store.selectBook(el.dataset.d, el.dataset.id); location.hash = '#/desk/' + el.dataset.d; },
  deskNew: () => modal('<h2>Nouveau bureau</h2><label>Nom <input name="n" placeholder="Mécanique quantique" required></label>', f => { const d = store.newDesk(f.get('n')); location.hash = '#/desk/' + d.id; }),
  deskRename: () => modal(`<h2>Renommer le bureau</h2><label>Nom <input name="n" value="${esc(store.desk().name)}" required></label>`, f => store.renameDesk(store.desk().id, f.get('n'))),
  deskDup: () => { const c = store.dupDesk(store.desk().id); location.hash = '#/desk/' + c.id; },
  deskDel: () => confirm(`Supprimer le bureau « ${store.desk().name} » ? Les documents originaux ne sont pas supprimés.`) && (store.deleteDesk(store.desk().id), location.hash = '#/desk/' + (st.active || '')),
  bookSel: id => store.selectBook(st.active, id), bookClose: id => store.closeBook(st.active, id), bookRm: id => store.removeBook(st.active, id),
  bookUp: id => store.moveBook(st.active, id, -1), bookDown: id => store.moveBook(st.active, id, 1),
  prev: () => reader?.prev(), next: () => reader?.next(), zoomin: () => reader?.setZoom(reader.zoom * 1.2), zoomout: () => reader?.setZoom(reader.zoom / 1.2), zoom1: () => reader?.setZoom(1),
  modecycle: () => { const m = { auto: '2', 2: '1', 1: 'auto' }[st.prefs.mode]; store.pref('mode', m); reader?.setMode(m); },
  export: () => { const a = document.createElement('a'); a.href = URL.createObjectURL(new Blob([store.exportJSON()], { type: 'application/json' })); a.download = 'bibliotheque-sauvegarde.json'; a.click(); setTimeout(() => URL.revokeObjectURL(a.href), 1000); },
};
function refreshAll() { if (window.__refreshView) window.__refreshView(); else route(); }
document.addEventListener('click', e => {
  const t = e.target.closest('[data-act]');
  if (t && A[t.dataset.act]) { e.preventDefault(); A[t.dataset.act](t.dataset.id, t); if (t.dataset.act === 'sugpick') $('#sug').hidden = true; return; }
  const sp = e.target.closest('.spine'); if (sp) { showCard(sp.dataset.id, sp, true); return; }
  if (!e.target.closest('#card') && !e.target.closest('#sug')) { hideCard(true); const s = $('#sug'); if (s) s.hidden = true; }
});
document.addEventListener('change', e => {
  if (e.target.id === 'deskSel') { location.hash = '#/desk/' + e.target.value; }
  if (e.target.id === 'deskNav') { if (e.target.value === '__new') A.deskNew(); else location.hash = '#/desk/' + e.target.value; e.target.value = st.active || ''; }
  if (e.target.id === 'pn') reader?.goto(e.target.value);
  if (e.target.id === 'imp' && e.target.files[0]) e.target.files[0].text().then(t => { try { store.importJSON(t); toast('Sauvegarde restaurée'); route(); } catch (x) { toast('Import impossible : ' + x.message); } });
});
document.addEventListener('pointerover', e => {   // survol souris uniquement ; le toucher passe par le clic
  if (e.pointerType !== 'mouse' || pinned) return; const sp = e.target.closest('.spine');
  if (e.target.closest('#card')) clearTimeout(hideT);
  else if (sp) showCard(sp.dataset.id, sp, false); else { clearTimeout(hideT); hideT = setTimeout(() => hideCard(), 160); }
});
document.addEventListener('focusin', e => { const sp = e.target.closest?.('.spine'); if (sp && !pinned) showCard(sp.dataset.id, sp, false); });
document.addEventListener('keydown', e => {
  if (e.key === 'Escape') { hideCard(true); return; }
  if (!reader || /^(INPUT|SELECT|TEXTAREA)$/.test(e.target.tagName) || e.ctrlKey || e.metaKey || e.altKey) return;
  const k = e.key; const m = { ArrowRight: 'next', PageDown: 'next', ArrowLeft: 'prev', PageUp: 'prev', '+': 'zoomin', '=': 'zoomin', '-': 'zoomout', '0': 'zoom1' }[k];
  if (m) { e.preventDefault(); A[m](); } else if (k === 'Home') reader.goto(1); else if (k === 'End') reader.goto(reader.total);
});
addEventListener('pagehide', () => store.flush()); document.addEventListener('visibilitychange', () => document.hidden && store.flush());

/* ---------- routage & rendu ---------- */
function paintNav(r) {
  $$('#nav a').forEach(a => a.setAttribute('aria-current', a.dataset.r === r ? 'page' : 'false'));
  $('#cartn').textContent = st.cart.length;
  $('#deskNav').innerHTML = (st.desks.length ? '' : '<option value="">Aucun bureau</option>') + st.desks.map(d => `<option value="${d.id}" ${d.id === st.active ? 'selected' : ''}>${esc(d.name)} (${d.books.length})</option>`).join('') + '<option value="__new">＋ Nouveau bureau…</option>';
  $('#warn').hidden = store.ok && !memOnly; $('#warn').textContent = memOnly ? 'Stockage navigateur indisponible : vos bureaux ne seront pas conservés. Utilisez « Sauvegarde > Exporter ».' : 'Enregistrement impossible (stockage plein ou bloqué).';
}
let cur = '';
function route() {
  dispose?.(); dispose = null; window.__refreshView = null; hideCard(true);
  const [, r = 'library', ...rest] = (location.hash || '#/library').split('/'), arg = decodeURIComponent(rest.join('/'));
  cur = r; paintNav(r === 'desk' ? 'desk' : r);
  ({ library: libraryView, folders: () => foldersView(arg), search: searchView, cart: cartView, desk: () => deskView(arg) }[r] || libraryView)();
  main.focus({ preventScroll: true }); if (r !== 'desk') scrollTo(0, 0);
}
let pending = false;
store.subscribe(() => {   // changements structurels : mise à jour ciblée, jamais de rechargement du lecteur inutile
  if (pending) return; pending = true;
  queueMicrotask(() => { pending = false; paintNav(cur);
    if (cur === 'library') { paintMarks(); if (!card.hidden) { const el = $(`.spine[data-id="${card.dataset.id}"]`); if (el) showCard(card.dataset.id, el, card.classList.contains('pin')); } }
    else if (cur === 'desk') { st.desks.length && store.desk() ? ($('#deskSel') ? paintDesk() : route()) : route(); }
    else if (window.__refreshView) window.__refreshView(); else route(); });
});
addEventListener('hashchange', route);

(async () => {
  try {
    const res = await fetch(new URL('catalog.json', document.baseURI)); if (!res.ok) throw new Error('HTTP ' + res.status);
    raw = await res.json(); docs = C.prepare(raw); byId = new Map(docs.map(d => [d.id, d])); BASE = raw.base || '../';
    $('#boot')?.remove(); route();
  } catch (e) {
    main.innerHTML = empty('Catalogue introuvable.', `Impossible de charger <code>catalog.json</code> (${esc(e.message)}). Exécutez <code>python3 build_catalog.py</code> dans ce dossier et servez le site via HTTP (pas en <code>file://</code>).`);
  }
})();
export { docs };
