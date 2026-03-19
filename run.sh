#!/bin/bash

echo "🔧 Compression PDF..."
#./run.sh compress
python scripts/compress_pdf.py physics/faculty/themeze/documents/ --recursive --replace

echo "🌐 JSON..."
bash scripts/json.py

echo "📤 Push Git..."
# ./run.sh push
bash scripts/git_push.sh

echo "🌐 Lancement serveur..."
# ./run.sh serve
python scripts/serve.py &


