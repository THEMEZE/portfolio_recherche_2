#!/usr/bin/env python3
"""Fusionne ../docs.json (arborescence) + ../search.json (métadonnées) -> catalog.json.
Lecture seule sur les originaux. Relancer après chaque mise à jour de docs.json/search.json."""
import json, hashlib, unicodedata, urllib.parse, difflib, collections, datetime
from pathlib import Path
HERE = Path(__file__).resolve().parent; DOCS = HERE.parent
nfc = lambda s: unicodedata.normalize('NFC', s)
def norm(p):  # clé de rapprochement : %xx décodés, sans diacritiques, sans casse (search.json mélange NFC/NFD, %20, ė/é)
    return ''.join(c for c in unicodedata.normalize('NFD', urllib.parse.unquote(p)) if not unicodedata.combining(c)).lower()
KIND = {k: v for v, ks in {
 'doc': 'pdf pptx ppt pptm docx doc odt xlsx djvu epub nb md',
 'media': 'jpg jpeg png mp4 swf', 'code': 'py css js html htm json gitignore txt ipynb'}.items() for k in ks.split()}

files = []
def walk(nodes):
    for n in nodes:
        walk(n['children']) if n['type'] == 'folder' else files.append(n)
walk(json.load(open(DOCS / 'docs.json', encoding='utf-8')))
meta = json.load(open(DOCS / 'search.json', encoding='utf-8'))

byk = {norm(f['path']): f['path'] for f in files}
bybase = collections.defaultdict(list)
for f in files: bybase[norm(f['path']).rsplit('/', 1)[-1]].append(f['path'])
merged, unresolved, fixed = {}, [], []
for m in meta:
    k = norm(m['path']); p = byk.get(k)
    if not p:  # repli : même nom de fichier, unique -> sinon ressemblance forte
        c = bybase.get(k.rsplit('/', 1)[-1], [])
        p = c[0] if len(c) == 1 else (lambda r: byk[r[0]] if r else None)(difflib.get_close_matches(k, byk, 1, 0.93))
    if not p: unresolved.append(m['path']); continue
    if p != m['path']: fixed.append((m['path'], p))
    e = merged.setdefault(p, {'author': [], 'category': [], 'keywords': [], 'link': None})
    for f in ('author', 'category', 'keywords'):
        e[f] += [x for x in m.get(f, []) if x not in e[f]]   # fusion des doublons
    e['link'] = m.get('link') or e['link']

docs = []
for f in files:
    ext = f['name'].rsplit('.', 1)[-1].lower() if '.' in f['name'] else ''
    m = merged.get(f['path'])
    d = {'id': 'd' + hashlib.sha1(nfc(f['path']).encode()).hexdigest()[:10], 'name': f['name'],
         'path': f['path'], 'ext': ext, 'kind': KIND.get(ext, 'other'), 'meta': bool(m)}
    if m: d.update({k: v for k, v in m.items() if v})
    docs.append(d)
ids = collections.Counter(d['id'] for d in docs); assert max(ids.values()) == 1, 'collision d\'id'
stats = collections.Counter(d['kind'] for d in docs)
out = {'generated': datetime.date.today().isoformat(), 'base': '../',
       'folders': sorted({d['path'].split('/')[0] for d in docs if '/' in d['path']}), 'docs': docs}
(HERE / 'catalog.json').write_text(json.dumps(out, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
print(f"{len(docs)} fichiers | {dict(stats)} | dossiers racine: {len(out['folders'])}")
print(f"métadonnées: {len(meta)} entrées -> {len(merged)} documents ({len(meta)-len(merged)-len(unresolved)} doublons fusionnés), "
      f"{len(fixed)} chemins corrigés, {len(unresolved)} non résolus")
for a, b in fixed:  # on ne signale que les vraies déductions (répertoire différent), pas les simples %20 / NFD
    if nfc(urllib.parse.unquote(a)).rsplit('/', 1)[0] != nfc(b).rsplit('/', 1)[0]:
        print('  À VÉRIFIER (rapproché par nom de fichier):', a, '->', b)
for u in unresolved: print('  NON RÉSOLU:', u)
