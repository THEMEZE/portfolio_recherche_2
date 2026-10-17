# Bibliothèque interactive de physique

Fusion de **A** (`documents/index.html` + `search.html`, catalogue) et **B** (`Outils/manipage.html`, lecteur PDF.js) en une application statique
(HTML/CSS/JS sans framework, sans serveur, sans compte). Aucun fichier original n'est modifié.

## Installation / lancement
1. Copier le dossier `biblio/` dans `physics/faculty/themeze/documents/` (à côté de `docs.json`, `search.json`).
2. Après tout ajout de documents : `python3 main.py && python3 search_keys_docs.py && python3 biblio/build_catalog.py` (régénère `catalog.json`).
3. Servir en HTTP (GitHub Pages convient ; `file://` ne marche pas à cause de `fetch`) : `python3 -m http.server` à la racine du site, puis ouvrir `/physics/faculty/themeze/documents/biblio/`.
4. Tests : `node --test tests/core.test.mjs` (Node ≥ 20).

Les chemins sont **relatifs** (`../` + chemin de `docs.json`) : aucune hypothèse sur la racine du domaine. Seule dépendance externe : PDF.js 2.10.377 (cdnjs), déjà utilisé par B.

## Architecture
| Fichier | Rôle |
|---|---|
| `build_catalog.py` | Fusionne `docs.json` + `search.json` → `catalog.json` (lecture seule sur les sources) |
| `js/core.js` | Logique pure : recherche (portée de `search.html`), parité des pages, abrégés, recommandations, persistance |
| `js/reader.js` | Lecteur PDF.js (double page / une page, rendu annulable, cache de 3 documents) |
| `js/app.js` | Vues Bibliothèque, Dossiers, Recherche, Panier, Bureaux ; un seul état partagé |
| `css/biblio.css`, `index.html` | Interface (palette bordeaux/crème du site d'origine) |

**Un seul catalogue** : `catalog.json` (2 318 fichiers, id stable `d`+sha1(chemin)[:10]). Les métadonnées ne sont jamais dupliquées ; le titre, le dossier et les mots-clés hérités des dossiers (comme `search.html`) sont dérivés au chargement.

## Données persistées (navigateur)
`localStorage['biblio.v1']` : `{cart[], favs[], recent[], prefs, active, desks:[{id,name,created,modified,current,books:[{id,page,pages,zoom,open,added,t}]}]}`.
Sauvegarde différée (350 ms) + forcée à la fermeture de la page. **Limites** : liée au navigateur, au profil et à l'appareil ; effacée si l'on vide les données du site ; pas de synchronisation. Contournement : *Bureaux › Sauvegarde › Exporter / Importer* (JSON).

## Fonctionnalités
- **Bibliothèque** : tranches de tailles/teintes variées (teinte = dossier), titre abrégé, étagères recalculées selon la largeur, saut par dossier, tri/filtres partagés. Survol souris = le livre sort + couverture générée à partir du titre/auteur/dossier ; **toucher/clavier** = même fiche, fixée. Marques : bureau (ruban), panier (liseré bleu), favori.
- **Dossiers** : arbre réel (16 dossiers racine), compteurs, fil d'Ariane, dossier parent, recherche limitée au dossier.
- **Recherche** : tags typés `author: keyword: category: name: folder: type:` + texte libre + « expression exacte », union/intersection, scores d'origine, suggestions, sans accents ni casse, tri, remise à zéro, découverte (reprise, récents, favoris, catégories, thèmes, « proches de… » avec la raison).
- **Panier** : ajout depuis tous les espaces, retrait, réordonnancement (↑↓, tactile), affectation à un bureau, distinction affecté / non affecté.
- **Bureaux** : nombre libre ; créer, renommer, dupliquer, supprimer (jamais les fichiers), page/zoom/ouverture par livre, reprise exacte.
- **Lecteur** : double page ≥ 880 px de large (**paires à gauche, impaires à droite ; page 1 à droite**), une page en dessous, bascule manuelle, saisie de page, clavier (← → PgUp/PgDn Home End + − 0), zoom, 2 canvas seulement, rendu annulé si l'on tourne vite la page.

## Constats sur les données (à connaître)
- **16 dossiers racine, pas 11** (le catalogue en reflète la réalité).
- `search.json` : **17 chemins ne correspondaient pas** à `docs.json` (%20, accents NFD/NFC, fautes) → leurs métadonnées étaient perdues par l'ancien moteur ; elles sont maintenant rattachées. 1 doublon fusionné. **2 rapprochements par nom de fichier à vérifier** : `Livres/Orale.pdf` → `Oraux/2021 Guillaume Themeze/Orale.pdf` ; `Oraux/LP/Avance du pėrihėlie…` → `Oraux/2025 Guillaume Themeze/LP/…`.
- Seuls **55 documents sur 1 961** ont auteur/catégorie/mots-clés ; les autres ne sont trouvables que par titre et dossier.
- Formats : PDF 1 487 ; **PPTX/DOCX/etc. ne sont pas lisibles dans le navigateur** (message explicite + lien vers l'original). Les images (301) et fichiers de code sont masqués sauf « Tous formats ».
- Dimensions des livres : aucune donnée physique → variation déterministe (hash de l'id), à but visuel uniquement.
- Le corpus de B (`docaranger/…`, thèse) n'est **pas** fusionné dans le catalogue (autre arborescence, pas de métadonnées).

## Vérifications réalisées
- `node --test` : 10/10 (catalogue réel, recherche, parité des pages, bureaux, persistance, stockage indisponible).
- Test d'intégration jsdom (exécute `app.js` sur le vrai catalogue, PDF.js simulé) : 32/32, 0 erreur JS.

## Non vérifié / limites
- **Aucun test dans un vrai navigateur** ni sur téléphone : rendu CSS, animations, fluidité, mise en page responsive et rendu PDF.js réel restent à valider visuellement.
- **Les PDF étaient exclus de l'archive** (1 795 fichiers) : l'ouverture de vrais documents n'a pas été testée.
- Pas de recherche dans le texte des PDF (aucun index). « Récemment ajoutés » absent : `docs.json` n'a pas de dates.
- Les ids dépendent du chemin : renommer un fichier crée un nouvel id (les bureaux qui le référencent afficheront « Document introuvable » et permettent de le retirer).
- Pas de glisser-déposer : le réordonnancement (panier, livres d’un bureau) se fait par boutons ↑↓.
