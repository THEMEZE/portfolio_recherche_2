import json
from collections import defaultdict
import os
import sys

def main_build_search_tree():
    # répertoire du script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    search_json_path = os.path.join(script_dir, "search.json")

    if not os.path.isfile(search_json_path):
        print(f"❌ Fichier 'search.json' introuvable !")
        print(f"Répertoire du script : {script_dir}")
        print("Fichiers présents dans ce répertoire :")
        for f in os.listdir(script_dir):
            print(" -", f)
        sys.exit(1)

    # charger search.json
    with open(search_json_path, "r", encoding="utf-8") as f:
        docs = json.load(f)

    keyword_dict = defaultdict(list)

    # créer mapping mots-clés -> documents
    for doc in docs:
        for kw in doc.get("keywords", []):
            keyword_dict[kw].append({
                "type": "file",
                "name": doc["name"],
                "path": doc["path"]
            })

    # construire structure finale
    search_keys_docs = []
    for kw, files in sorted(keyword_dict.items()):
        search_keys_docs.append({
            "type": "folder",
            "name": kw,
            "children": files
        })

    # enregistrer le JSON dans le même dossier que le script
    output_path = os.path.join(script_dir, "search_keys_docs.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(search_keys_docs, f, indent=2, ensure_ascii=False)

    print(f"✅ '{output_path}' généré avec succès !")

if __name__ == "__main__":
    main_build_search_tree()