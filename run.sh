#!/bin/bash

echo "🔧 split pdf"
#python scripts/split_pdf.py

echo "🔧 Compression PDF..."
echo "🧹 Compression automatique..."
#./run.sh compress
#python scripts/compress_pdf.py physics/faculty/themeze/documents/ --recursive --split --replace
#python scripts/compress_pdf.py physics/faculty/themeze/documents/ --recursive --compress --replace

#python scripts/compress_pdf.py physics/faculty/themeze/documents/ --recursive --compress --gitignore
#python scripts/compress_pdf.py physics/faculty/themeze/documents/ --recursive --split --gitignore


echo "🌐 JSON..."
python -m scripts.filjson

echo "📤 Push Git..."
#./run.sh push
bash scripts/git_push.sh

echo "🌐 Lancement serveur..."
# ./run.sh serve
#python scripts/server.py &


