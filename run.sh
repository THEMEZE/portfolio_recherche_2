#!/bin/bash

echo "🔧 Compression PDF..."
echo "🧹 Compression automatique..."
#./run.sh compress
python scripts/compress_pdf.py physics/faculty/themeze/documents/ --recursive --split --replace
python scripts/compress_pdf.py physics/faculty/themeze/documents/ --recursive --compress --replace

echo "🌐 JSON..."
python -m scripts.json

echo "📤 Push Git..."
# ./run.sh push
bash scripts/git_push.sh

echo "🌐 Lancement serveur..."
# ./run.sh serve
python scripts/server.py &


