import os
import json

from pathlib import Path

def build_tree(path: str, ROOT: str):
    tree = []
    path = Path(path)
    ROOT = Path(ROOT)

    for name in sorted(path.iterdir()):
        if name.name not in ["docs.json", "index.html", "main.py", ".DS_Store"]:
            if name.is_dir():
                tree.append({
                    "type": "folder",
                    "name": name.name,
                    "children": build_tree(name, ROOT)
                })
            else:
                tree.append({
                    "type": "file",
                    "name": name.name,
                    "path": str(name.relative_to(ROOT))
                })
    return tree

def main_build_tree(root_path=None):
    if root_path is None:
        root_path = Path(__file__).resolve().parent
    root_path = Path(root_path)
    data = build_tree(str(root_path), str(root_path))

    with open(root_path / "docs.json", "w") as f:
        json.dump(data, f, indent=2)