#!/bin/bash

echo "=== Script d'installation des dépendances pour le projet AMS ==="
echo

# Mise à jour des paquets
echo "Mise à jour de la liste des paquets..."
sudo apt-get update

# Installation des paquets système nécessaires
echo "Installation des dépendances système..."
sudo apt-get install -y python3 python3-pip python3-venv jq sqlite3

# Installation des paquets Python depuis les dépôts Debian
echo "Installation des paquets Python depuis les dépôts Debian..."
sudo apt-get install -y python3-flask python3-matplotlib python3-pandas python3-psutil python3-requests python3-bs4 python3-lxml

# Vérification si les installations ont réussi
if [ $? -eq 0 ]; then
    echo "✅ Installation des dépendances systèmes réussie."

    # Création d'un environnement virtuel Python
    echo "Création d'un environnement virtuel Python..."
    python3 -m venv venv
    source venv/bin/activate

    # Installation des dépendances Python manquantes via pip
    echo "Installation des dépendances Python via pip..."
    pip install flask matplotlib pandas psutil requests beautifulsoup4 lxml certifi

    if [ $? -eq 0 ]; then
        echo "✅ Installation des dépendances Python réussie."
    else
        echo "❌ Échec de l'installation des dépendances Python."
        exit 1
    fi
else
    echo "❌ Échec de l'installation des dépendances système."
    echo "Essai d'installation via pip uniquement..."

    # Création d'un environnement virtuel Python en cas d'échec
    python3 -m venv venv
    source venv/bin/activate

    # Installation de toutes les dépendances via pip
    pip install flask matplotlib pandas psutil requests beautifulsoup4 lxml certifi

    if [ $? -eq 0 ]; then
        echo "✅ Installation des dépendances via pip réussie."
    else
        echo "❌ Échec de l'installation. Veuillez vérifier votre connexion internet."
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

# Création des répertoires nécessaires
echo "Création des répertoires pour l'application..."
mkdir -p website/static alertes/alertes parseur

# Vérification de la configuration email
if [ ! -f "mail/config.py" ]; then
    echo "⚠️ Fichier de configuration email non trouvé."
    echo "Création d'un template de configuration email..."
    mkdir -p mail
    echo 'SMTP_PASSWORD = "votre_mot_de_passe_ici"' > mail/config.py
    echo "✅ Template de configuration email créé dans mail/config.py"
    echo "⚠️ Veuillez mettre à jour le mot de passe SMTP avant d'utiliser les alertes."
fi

# Test de l'application
echo "Test de la base de données et collecte initiale des données..."
python3 run_check.py

echo
echo "=== Installation terminée ==="
echo "Vous pouvez maintenant exécuter votre application avec la commande:"
echo "python3 ams.py"
echo
echo "L'interface web sera disponible à l'adresse: http://localhost:4000"