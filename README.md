# AdminMonitoring System (AMS)

![Version](https://img.shields.io/badge/version-1.0-blue.svg)
![Python](https://img.shields.io/badge/Python-3.6+-green.svg)
![License](https://img.shields.io/badge/license-MIT-lightgrey.svg)

## 📑 Table des matières

- [Introduction](#introduction)
- [Fonctionnalités](#fonctionnalités)
- [Installation](#installation)
- [Architecture du projet](#architecture-du-projet)
- [Interface utilisateur](#interface-utilisateur)
- [Modules principaux](#modules-principaux)
- [Configuration avancée](#configuration-avancée)
- [Dépannage](#dépannage)
- [Documentation technique](#documentation-technique)
- [Crédits](#crédits)

## 📋 Introduction

AdminMonitoring System (AMS) est une solution complète de surveillance système développée dans le cadre du cours de Système et Réseau. Cette application permet le suivi en temps réel des métriques essentielles d'un serveur, génère des visualisations graphiques et alerte en cas de dépassement de seuils critiques.

**Objectifs pédagogiques:**

- Application pratique des concepts de programmation système
- Utilisation de Python pour la surveillance de ressources
- Implémentation d'une base de données pour le stockage de métriques
- Création d'une interface web avec Flask
- Automatisation des alertes et notifications

## ✨ Fonctionnalités

### Surveillance système
- **Monitoring CPU**: Suivi du pourcentage d'utilisation processeur
- **Monitoring RAM**: Suivi du pourcentage d'utilisation mémoire
- **Monitoring Disque**: Suivi du pourcentage d'espace disque utilisé

### Visualisation des données
- **Graphiques historiques**: Visualisation des tendances d'utilisation
- **Interface web**: Tableau de bord ergonomique et responsive
- **Actualisation en temps réel**: Rafraîchissement sur demande des données

### Système d'alertes
- **Alertes par email**: Notifications automatiques
- **Seuils configurables**: Personnalisation des niveaux d'alerte
- **Anti-spam**: Intervalle minimal entre les alertes similaires

### Sécurité
- **Veille CERT**: Intégration des alertes de sécurité du CERT-FR
- **Affichage centralisé**: Toutes les informations critiques au même endroit

## 🔧 Installation

### Prérequis
- Système Linux/macOS
- Python 3.6+
- pip (gestionnaire de paquets Python)
- Connexion Internet (pour les mises à jour et alertes CERT)

### Méthode rapide (recommandée)
```bash
git clone https://github.com/username/ams.git
cd ams
chmod +x install.sh
./install.sh
```

### Installation manuelle des dépendances
Si le script automatique échoue, vous pouvez installer manuellement les dépendances:

```bash
pip install -r requirements.txt
```

## 🏗 Architecture du projet

### Structure des répertoires
```
ams/
├── sondes/            # Scripts de collecte des métriques
├── stockage/          # Gestion de la base de données
├── graphiques/        # Génération des visualisations
├── alertes/           # Système de notification
├── website/           # Interface web Flask
├── parseur/           # Module de surveillance CERT
└── mail/              # Gestion des emails
```

### Flux de données
1. Les sondes collectent les données brutes du système
2. Le module de stockage enregistre ces données dans une base SQLite
3. Le module graphiques génère des visualisations à partir de ces données
4. Le module alertes vérifie les dépassements de seuils
5. L'interface web affiche toutes ces informations de façon centralisée

## 🖥 Interface utilisateur

### Démarrage de l'application
```bash
python3 website/app.py
```

Accédez ensuite à votre tableau de bord via: http://localhost:4000

### Éléments de l'interface
- **Cards de métriques**: Affichent les valeurs actuelles CPU, RAM, disque
- **Graphiques historiques**: Visualisation temporelle des métriques
- **Tableau des alertes CERT**: Affiche les alertes de sécurité récentes
- **Bouton "Rafraîchir"**: Met à jour les données et graphiques manuellement

### Utilisation quotidienne recommandée
- Consultez régulièrement le tableau de bord pour surveiller l'état du système
- Configurez le système pour démarrer automatiquement au boot (voir ci-dessous)
- Configurez les alertes email avec vos paramètres SMTP personnels

### Configuration de démarrage automatique (systemd)
Créez un fichier service systemd:

```bash
sudo nano /etc/systemd/system/ams.service
```

Contenu du fichier:
```
[Unit]
Description=AdminMonitoring System
After=network.target

[Service]
User=votre_utilisateur
WorkingDirectory=/chemin/vers/ams
ExecStart=/usr/bin/python3 website/app.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Activez le service:
```bash
sudo systemctl enable ams.service
sudo systemctl start ams.service
```

## 📦 Modules principaux

### Système de sondes (sondes/)
Les sondes sont des scripts légers qui collectent les métriques systèmes:

- **cpu.py**: Utilise psutil pour mesurer l'utilisation CPU
- **ram.py**: Analyse la mémoire via psutil
- **disk.sh**: Script bash qui utilise df pour l'espace disque

Chaque sonde renvoie un objet JSON standardisé pour faciliter l'interopérabilité.

### Gestion des données (stockage/)
Module central qui gère la persistance des données:

- **gerer_stockage.py**:
  - `GestionnaireBDD`: Interface avec la base SQLite
  - `GestionnaireSondes`: Exécute les sondes et enregistre les données
- **main.py**: Orchestration de la collecte périodique
- **back_up.py**: Création de sauvegardes
- **back_up_restore.py**: Restauration de données

### Visualisation (graphiques/)
Module responsable de la création des graphiques:

- **graphic.py**: Utilise Matplotlib pour créer des visualisations temporelles
- `GenerateurGraphiques`: Classe principale qui gère la création des graphiques

### Système d'alertes (alertes/)
Module qui détecte et notifie les situations critiques:

- **alertes.py**:
  - Vérifie si les métriques dépassent les seuils configurés
  - Envoie des emails d'alerte via le module mail
  - Maintient un journal des alertes pour référence

### Interface web (website/)
Application web Flask qui centralise toutes les informations:

- **app.py**: Serveur Flask avec routes `/` et `/refresh`
- **index.html**: Template Bootstrap responsive

### Surveillance CERT (parseur/)
Module qui surveille les alertes de sécurité officielles:

- **parseur.py**:
  - Analyse les alertes du CERT-FR
  - Stocke les alertes dans une base de données
  - Met à jour les informations périodiquement

## ⚙ Configuration avancée

### Modification des seuils d'alerte
Le système permet de configurer les seuils d'alerte facilement via un fichier JSON sans avoir à modifier le code source.

#### Utilisation du fichier seuils.json
Éditez le fichier `alertes/seuils.json` pour personnaliser vos seuils d'alertes:

```json
{
  "cpu": 90,     // Pourcentage d'utilisation CPU
  "ram": 80,     // Pourcentage d'utilisation RAM
  "disk": 85,    // Pourcentage d'espace disque utilisé
  "intervalle_alertes": 30  // Minutes entre deux alertes du même type
}
```

### Configuration de l'envoi d'emails
Créez le fichier `mail/config.py` s'il n'existe pas:
```python
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
SMTP_USERNAME = 'votre.email@gmail.com'
SMTP_PASSWORD = 'votre_mot_de_passe'
DEST_EMAIL = 'destinataire@example.com'
```

Modifiez `mail.py` pour configurer votre serveur SMTP:
```python
def envoyer_alerte(sujet, message):
    # Configuration du serveur SMTP
    server = smtplib.SMTP(config.SMTP_SERVER, config.SMTP_PORT)
    server.starttls()
    server.login(config.SMTP_USERNAME, config.SMTP_PASSWORD)
    
    # Construction du message
    msg = MIMEText(message)
    msg['Subject'] = sujet
    msg['From'] = config.SMTP_USERNAME
    msg['To'] = config.DEST_EMAIL
    
    # Envoi
    server.send_message(msg)
    server.quit()
```

### Paramétrage de l'interface web
Pour modifier le port ou activer le mode debug, éditez `app.py`:
```python
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4000, debug=True)
```

### Configuration de la rétention de données
Pour modifier la politique de conservation des données, éditez `gerer_stockage.py`:
```python
# Conserver les données pendant 30 jours
RETENTION_JOURS = 30

def nettoyer_donnees_anciennes():
    date_limite = datetime.now() - timedelta(days=RETENTION_JOURS)
    # SQL pour supprimer les données plus anciennes que date_limite
```

### Fréquence de collecte
Modifiez l'intervalle de collecte dans `main.py`:
```python
# Collecter les données toutes les 5 minutes
INTERVALLE_MINUTES = 5
```

## 🛠 Dépannage

### Problèmes courants et solutions
1. **Base de données inaccessible ou corrompue**
   - Sauvegardez vos données
   - Supprimez la base courante
   - Restaurez à partir d'une sauvegarde ou créez une nouvelle base

2. **Erreurs de permission sur les scripts**
   - Vérifiez les permissions: `ls -la sondes/`
   - Ajoutez les permissions d'exécution: `chmod +x sondes/*.py sondes/*.sh`

3. **Problèmes d'envoi d'emails**
   - Vérifiez la configuration SMTP dans `mail/config.py`
   - Pour Gmail, activez "Autoriser les applications moins sécurisées"
   - Testez avec `python -m mail.test_mail`

4. **Interface web inaccessible**
   - Vérifiez que Flask est en cours d'exécution
   - Confirmez le port utilisé (par défaut: 4000)
   - Vérifiez les règles de pare-feu

5. **Aucune donnée affichée**
   - Vérifiez que les sondes fonctionnent correctement
   - Consultez les logs pour détecter d'éventuelles erreurs

### Journal des erreurs
Le système maintient plusieurs fichiers de log:
- `alertes/alertes.log`: Journal des alertes envoyées
- `cron.log`: Si configuré avec cron, journal des exécutions périodiques

## 📖 Documentation technique

### Structure de la base de données
- **Table sondes** (`table_sondes.sqlite`)
  ```
  id INTEGER PRIMARY KEY
  timestamp DATETIME
  type TEXT
  valeur REAL
  ```

- **Table alertes** (`parseur.sqlite`)
  ```
  id INTEGER PRIMARY KEY
  date DATETIME
  titre TEXT
  description TEXT
  niveau TEXT
  url TEXT
  ```

### Format des données des sondes
Chaque sonde retourne un objet JSON avec une clé unique:
```json
{
  "cpu": 45.2,
  "timestamp": "2023-04-01 14:30:25"
}
```

### Algorithme de détection des alertes
1. Récupération de la dernière valeur de chaque métrique
2. Comparaison avec les seuils configurés
3. Si dépassement, vérification de l'historique récent
4. Si aucune alerte similaire récente, envoi d'un email
5. Mise à jour du journal des alertes

### Cycle de vie des données
1. **Collecte**: Exécution des sondes à intervalles réguliers
2. **Stockage**: Insertion dans la base SQLite
3. **Traitement**: Génération des graphiques, vérification des seuils
4. **Purge**: Suppression des données anciennes (limite configurable)
5. **Sauvegarde**: Création périodique de backups

## 📝 Crédits

- **Développeur**: Alexi Miaille
- **Contexte**: Cours de Système et Réseau (L2 Informatique)
- **Année**: 2025

### Licence
Ce projet est distribué sous licence MIT à des fins éducatives uniquement.

> "La simplicité est la sophistication suprême." - Leonardo da Vinci