#!/bin/bash

set -e

# 📅 Date + heure
DATE=$(date +"%Y-%m-%d %H:%M:%S")

# 🌿 Branche actuelle
BRANCH=$(git branch --show-current)

# 💻 Machine
HOST=$(hostname)

# 👤 User git
USER=$(git config user.name)

# 🎲 Tag aléatoire
TAGS=("quantum" "relativity" "entropy" "wavefunction" "tensor" "symmetry")
RAND_TAG=${TAGS[$RANDOM % ${#TAGS[@]}]}

COMMIT_MSG="[$DATE][$BRANCH][$HOST] update by $USER | tag:$RAND_TAG"

echo "🔍 Vérification des PDF..."

# Trouve tous les PDF
PDFS=$(find . -type f -name "*.pdf")

BLOCK=false

for file in $PDFS; do
    SIZE_MB=$(du -m "$file" | cut -f1)

    if [ "$SIZE_MB" -gt 100 ]; then
        echo "❌ BLOQUANT (>100MB): $file (${SIZE_MB} MB)"
        BLOCK=true
    elif [ "$SIZE_MB" -gt 50 ]; then
        echo "⚠️  Warning (>50MB): $file (${SIZE_MB} MB)"
    fi
done

if [ "$BLOCK" = true ]; then
    echo ""
    echo "🚫 Push annulé : fichiers > 100MB détectés"
    echo "👉 Utilise compress_pdf.py ou Git LFS"
    exit 1
fi

echo "📦 Ajout des fichiers..."
git add .

if git diff --cached --quiet; then
    echo "⚠️ Aucun changement à commit"
    exit 0
fi

echo "📝 Commit : $COMMIT_MSG"
git commit -m "$COMMIT_MSG"

echo "🚀 Push vers origin/$BRANCH"
git push origin "$BRANCH"

echo "✅ Terminé"