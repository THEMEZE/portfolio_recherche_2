// reader.js — lecteur basé sur PDF.js 2.10.377 (même version/CDN que Outils/manipage.html)
import { slots, nextPage, prevPage, clamp, DUAL_MIN } from './core.js';
export const WORKER = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/2.10.377/pdf.worker.min.js';
export const IMG = ['png', 'jpg', 'jpeg', 'webp', 'gif'];
export const readable = ext => ext === 'pdf' || IMG.includes(ext);

const cache = new Map();   // url -> Promise<PDFDocumentProxy> ; 3 documents max, les plus anciens sont détruits (libère le worker)
function load(url) {
  if (cache.has(url)) { const p = cache.get(url); cache.delete(url); cache.set(url, p); return p; }
  const lib = window.pdfjsLib;
  if (!lib) return Promise.reject(new Error('PDF.js n’a pas pu être chargé (réseau / CDN cdnjs bloqué).'));
  lib.GlobalWorkerOptions.workerSrc = lib.GlobalWorkerOptions.workerSrc || WORKER;
  const task = lib.getDocument({ url }), p = task.promise.catch(e => { cache.delete(url); throw e; });
  cache.set(url, p);
  while (cache.size > 3) { const [k, old] = cache.entries().next().value; cache.delete(k); old.then(d => d.destroy()).catch(() => {}); }
  return p;
}

export class Reader {
  /** host: élément conteneur ; cb: { onPage(p,total), onMode(dual), onError(msg,retry) } */
  constructor(host, cb) {
    this.host = host; this.cb = cb; this.page = 1; this.total = 1; this.zoom = 1; this.mode = 'auto'; this.dual = false;
    this.tok = 0; this.tasks = []; this.dead = false; this.doc = null; this.img = null;
    host.innerHTML = '<div class="spread" role="group" aria-label="Pages du document"></div>';
    this.spread = host.firstChild;
    this.size = ''; this.ro = new ResizeObserver(() => { const z = host.clientWidth + 'x' + host.clientHeight; if (z === this.size) return; this.size = z; clearTimeout(this.rt); this.rt = setTimeout(() => this.layout(), 120); });
    this.ro.observe(host);
  }
  async open(url, { page = 1, zoom = 1, mode = 'auto', ext = 'pdf' } = {}) {
    this.url = url; this.ext = ext; this.zoom = zoom; this.mode = mode; this.doc = null; this.img = null;
    this.spread.innerHTML = '<p class="msg">Chargement…</p>';
    try {
      if (IMG.includes(ext)) { this.img = url; this.total = 1; }
      else { this.doc = await load(url); this.total = this.doc.numPages; }
      if (this.dead) return;
      this.page = clamp(page, 1, this.total); this.layout(); this.emit();
    } catch (e) {
      if (this.dead) return;
      this.spread.innerHTML = '';
      this.cb.onError?.(`Document introuvable ou inaccessible : ${decodeURI(url)}\n${e.message || e}`, () => this.open(url, { page, zoom, mode, ext }));
    }
  }
  get isDual() { return this.mode === '2' || (this.mode === 'auto' && this.host.clientWidth >= DUAL_MIN); }
  layout() { const d = this.isDual; this.dual = d; this.cb.onMode?.(d); this.render(); }
  emit() { this.cb.onPage?.(this.page, this.total); }
  goto(p) { p = clamp(Math.round(+p) || 1, 1, this.total); if (p === this.page) return; this.page = p; this.render(); this.emit(); }
  next() { this.goto(nextPage(this.page, this.total, this.dual)); }
  prev() { this.goto(prevPage(this.page, this.total, this.dual)); }
  setZoom(z) { this.zoom = clamp(z, 0.4, 3.5); this.render(); this.cb.onZoom?.(this.zoom); }
  setMode(m) { this.mode = m; this.layout(); }
  async render() {
    if (!this.doc && !this.img) return;
    const tok = ++this.tok, pages = slots(this.page, this.total, this.dual);
    this.tasks.forEach(t => t?.cancel?.()); this.tasks = [];
    const W = Math.max(120, this.host.clientWidth - 24), H = Math.max(160, this.host.clientHeight - 16);
    try {
      const first = pages.find(n => n);
      let vw = 600, vh = 800, pg = {};
      if (this.doc) { for (const n of pages) if (n) pg[n] = await this.doc.getPage(n); const v = pg[first].getViewport({ scale: 1 }); vw = v.width; vh = v.height; }
      if (tok !== this.tok) return;
      const fit = Math.min((W - (this.dual ? 12 : 0)) / pages.length / vw, H / vh), scale = fit * this.zoom;   // zoom 1 = page entière visible
      const frag = document.createDocumentFragment(), jobs = [];
      pages.forEach((n, i) => {
        if (!n) { const b = document.createElement('div'); b.className = 'blank'; b.style.cssText = `width:${vw * scale}px;height:${vh * scale}px`; b.setAttribute('aria-hidden', 'true'); frag.append(b); return; }
        if (this.img) { const im = new Image(); im.alt = 'Page ' + n; im.className = 'pg'; im.src = this.img; im.style.width = Math.round(vw * scale) + 'px'; frag.append(im); return; }
        const c = document.createElement('canvas'), v = pg[n].getViewport({ scale }), r = Math.min(window.devicePixelRatio || 1, 2);
        c.className = 'pg'; c.width = Math.floor(v.width * r); c.height = Math.floor(v.height * r);
        c.style.width = v.width + 'px'; c.style.height = v.height + 'px'; c.setAttribute('role', 'img'); c.setAttribute('aria-label', 'Page ' + n);
        frag.append(c);
        const t = pg[n].render({ canvasContext: c.getContext('2d'), viewport: pg[n].getViewport({ scale: scale * r }) }); this.tasks[i] = t;
        jobs.push(t.promise.then(() => pg[n].cleanup()).catch(e => { if (e?.name !== 'RenderingCancelledException') throw e; }));
      });
      this.spread.replaceChildren(frag); this.spread.classList.toggle('dual', this.dual);
      await Promise.all(jobs);
    } catch (e) { if (tok === this.tok) this.cb.onError?.('Erreur d’affichage de la page : ' + (e.message || e), () => this.render()); }
  }
  destroy() { this.dead = true; this.tok++; this.tasks.forEach(t => t?.cancel?.()); this.ro.disconnect(); clearTimeout(this.rt); this.host.innerHTML = ''; }
}
