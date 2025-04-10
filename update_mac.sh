#!/bin/bash

echo "=== Script d'installation pour macOS ==="
echo

# Vérification de Homebrew
if ! command -v brew &> /dev/null; then
    echo "Installation de Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

    # Ajouter Homebrew au PATH
    echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zshrc
    eval "$(/opt/homebrew/bin/brew shellenv)"
else
    echo "✅ Homebrew est déjà installé."
fi

# Installation des dépendances système via Homebrew
echo "Installation des dépendances via Homebrew..."
brew install python3 jq

# Création d'un environnement virtuel Python
echo "Création d'un environnement virtuel Python..."
python3 -m venv venv
source venv/bin/activate

# Installation des dépendances Python
echo "Installation des dépendances Python via pip..."
pip install flask matplotlib pandas psutil requests beautifulsoup4 lxml certifi

if [ $? -eq 0 ]; then
    echo "✅ Installation des dépendances Python réussie."
else
    echo "❌ Échec de l'installation des dépendances Python."
    exit 1
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
mkdir -p website/static alertes/alertes parseur stockage/backups

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

# Créer un wrapper pour cron qui active l'environnement virtuel
echo "Création d'un wrapper pour cron..."
cat > run_cron.sh << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate
python3 "$@"
EOF

chmod +x run_cron.sh

echo
echo "=== Installation terminée ==="
echo "Pour les tâches cron, utilisez le wrapper avec le chemin complet :"
echo "* * * * * $(pwd)/run_cron.sh run_check.py >> $(pwd)/cron.log 2>&1"
echo
echo "Vous pouvez maintenant exécuter votre application avec la commande:"
echo "source venv/bin/activate && python3 ams.py"
echo
echo "L'interface web sera disponible à l'adresse: http://localhost:4000"