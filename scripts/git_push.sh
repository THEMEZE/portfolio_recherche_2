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

BLOCK=false

#find . -type f -name "*.pdf" \
#    ! -path "./physics/faculty/themeze/documents/M-Theory/*" \
#    ! -path "./physics/faculty/themeze/documents/Gravitation/*" \
#    -print0

find . -type f -name "*.pdf" -print0 | while IFS= read -r -d '' file; do
    SIZE_MB=$(du -m "$file" 2>/dev/null | cut -f1)

    # sécurité si du échoue
    if ! [[ "$SIZE_MB" =~ ^[0-9]+$ ]]; then
        continue
    fi

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

# 📏 Taille réelle du repo (fichiers trackés uniquement)
echo "📊 Calcul taille des fichiers trackés..."
TOTAL_SIZE=$(du -sm . | cut -f1)
echo "📊 Totale taille fichiers ${TOTAL_SIZE} MB)"
TOTAL_SIZE=$(git ls-files -z | xargs -0 du -m | awk '{sum += $1} END {print sum}')
echo "📊 Totale taille des fichiers trackés ${TOTAL_SIZE} MB)"
if [ "$TOTAL_SIZE" -gt 2000 ]; then
    echo "❌ Repo trop lourd (>1.8GB)"
    echo "⚠️  Warning (>2.0GB): (${TOTAL_SIZE} MB)"
    echo "👉 Nettoie ou utilise Git LFS"
    echo "git lfs install"
    echo 'git lfs track "*.pdf"'
    echo "git add .gitattributes"
    echo "git add ."
    echo 'git commit -m "use git lfs"'
    echo "git push"
    exit 1
fi

echo "🚀 Push vers origin/$BRANCH"
git push origin "$BRANCH"

echo "✅ Terminé"
