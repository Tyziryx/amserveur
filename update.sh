#!/bin/bash

echo "=== Script d'installation des dépendances pour le projet AMS ==="
echo

# Mise à jour des paquets
echo "Mise à jour de la liste des paquets..."
sudo apt-get update

# Installation des paquets Python depuis les dépôts Debian
echo "Installation des paquets Python depuis les dépôts Debian..."
sudo apt-get install -y python3-flask python3-matplotlib python3-pandas python3-psutil python3-requests python3-bs4 python3-lxml

# Vérification si les installations ont réussi
if [ $? -eq 0 ]; then
    echo "✅ Installation des paquets Debian réussie."
else
    echo "⚠️ Problème lors de l'installation des paquets Debian."
    echo "Tentative d'installation via pip..."

    # Installation via pip en mode utilisateur
    pip3 install --user flask matplotlib pandas psutil requests beautifulsoup4 lxml

    if [ $? -eq 0 ]; then
        echo "✅ Installation via pip réussie."
    else
        echo "❌ L'installation a échoué. Veuillez installer manuellement les dépendances."
        exit 1
    fi
fi

# Rendre le script disk.sh exécutable
if [ -f "sondes/disk.sh" ]; then
    echo "Rendre disk.sh exécutable..."
    chmod +x sondes/disk.sh
    echo "✅ Le script disk.sh est maintenant exécutable."
else
    echo "⚠️ Le fichier sondes/disk.sh n'a pas été trouvé."
fi

echo
echo "=== Installation terminée ==="
echo "Vous pouvez maintenant exécuter votre application avec la commande:"
echo "python3 ams.py"