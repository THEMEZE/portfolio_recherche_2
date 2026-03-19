#!/bin/bash

# Stop si erreur
set -e

# 📅 Date + heure
DATE=$(date +"%Y-%m-%d %H:%M:%S")

# 🌿 Branche actuelle
BRANCH=$(git branch --show-current)

# 💻 Machine
HOST=$(hostname)

# 👤 User git
USER=$(git config user.name)

# 🎲 Petit tag aléatoire (optionnel fun)
TAGS=("quantum" "relativity" "entropy" "wavefunction" "tensor" "symmetry")
RAND_TAG=${TAGS[$RANDOM % ${#TAGS[@]}]}

# 🧠 Message de commit stylé
COMMIT_MSG="[$DATE][$BRANCH][$HOST] update by $USER | tag:$RAND_TAG"

echo "📦 Ajout des fichiers..."
git add .

# Vérifie s’il y a des changements
if git diff --cached --quiet; then
    echo "⚠️ Aucun changement à commit"
    exit 0
fi

echo "📝 Commit : $COMMIT_MSG"
git commit -m "$COMMIT_MSG"

echo "🚀 Push vers origin/$BRANCH"
git push origin "$BRANCH"

echo "✅ Terminé"