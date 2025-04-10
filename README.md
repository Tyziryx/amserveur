# Documentation de AMS (Application Monitoring System)

## Présentation générale

AMS est une solution de surveillance système qui permet de :
- Surveiller l'utilisation CPU, RAM et stockage disque
- Visualiser les données historiques via des graphiques
- Recevoir des alertes par email en cas de dépassement de seuils
- Afficher les dernières alertes de sécurité du CERT

## Installation

### Prérequis
- Système Linux/macOS
- Python 3.6+
- pip (gestionnaire de paquets Python)

### Installation automatique

1. Clonez le dépôt :
```bash
git clone https://github.com/Tyziryx/amserveur.git
cd amserveur
```

2. Exécutez le script d'installation :
```bash
chmod +x update.sh
./update.sh
```

Ce script installe toutes les dépendances nécessaires :
- Python 3 et pip
- Bibliothèques système (jq, sqlite3)
- Modules Python (Flask, Matplotlib, Pandas, etc.)
- Configure l'environnement et vérifie les permissions

## Architecture du projet

### Structure des répertoires
```
amserveur/
├── alertes/            # Gestion des alertes système
├── graphiques/         # Génération des graphiques
├── mail/               # Configuration et envoi des emails
├── parseur/            # Surveillance des alertes CERT
├── sondes/             # Scripts de collecte des données système
├── stockage/           # Gestion de la base de données
├── website/            # Interface web Flask
├── ams.py              # Script principal
├── collector.py        # Génération des graphiques
├── run_check.py        # Mise à jour manuelle des données
└── update.sh           # Installation automatique
```

## Démarrage de l'application

1. Lancez l'application principale :
```bash
python3 ams.py
```

2. Accédez à l'interface web :
```
http://localhost:4000
```

## Modules principaux

### Sondes (sondes/)
Ces scripts collectent les données système :

- `cpu.py` : Mesure l'utilisation CPU (%)
- `ram.py` : Mesure l'utilisation mémoire (%)
- `disk.sh` : Mesure l'utilisation d'espace disque (%)

### Stockage des données (stockage/)
Gère l'enregistrement des données collectées :

- `gerer_stockage.py` : Contient deux classes :
  - `GestionnaireBDD` : Gère les opérations CRUD sur la base SQLite
  - `GestionnaireSondes` : Exécute les sondes et stocke leurs valeurs

- `main.py` : Script de collecte des données qui exécute les sondes à intervalles réguliers

### Graphiques (graphiques/)
Génère des graphiques historiques des données :

- `graphic.py` : Crée des graphiques pour CPU, RAM et disque

### Alertes (alertes/)
Surveille les dépassements de seuils et envoie des alertes :

- `alertes.py` : Vérifie les valeurs par rapport aux seuils configurés
  - Seuils par défaut : CPU (80%), RAM (80%), disque (85%)

### E-mail (mail/)
Configure et gère l'envoi d'emails :

- `mail.py` : Fonctions d'envoi d'emails
- `config.py` : Contient le mot de passe SMTP (à configurer)

### Interface Web (website/)
Interface utilisateur construite avec Flask :

- `app.py` : Serveur web Flask configuré sur le port 4000
- `templates/` : Templates HTML (interface utilisateur)
- `static/` : Fichiers statiques (graphiques, CSS)

### Parseur CERT (parseur/)
Surveille les alertes de sécurité du CERT :

- `parseur.py` : Récupère et analyse les alertes récentes du CERT-FR

## Scripts principaux

### ams.py
Script principal qui orchestre toutes les fonctionnalités :
- Lance la collecte de données
- Génère les graphiques
- Vérifie les alertes
- Démarre le serveur web Flask

### collector.py
Génère les graphiques pour l'interface web :
- Récupère les données dans la base SQLite
- Créé les graphiques avec Matplotlib
- Les sauvegarde dans `website/static/`

### run_check.py
Exécute une mise à jour manuelle des données :
- Collecte des nouvelles données
- Génère des graphiques actualisés
- Vérifie les alertes

## Configuration personnalisée

### Modifier les seuils d'alerte
Éditez `alertes/alertes.py` et modifiez le dictionnaire `SEUILS` :
```python
SEUILS = {
    "cpu": 80,  # CPU > 80%
    "ram": 80,  # RAM > 80%
    "disk": 85  # Disque > 85%
}
```

### Configurer l'envoi d'emails
1. Modifiez `mail/config.py` pour définir votre mot de passe
2. Modifiez `mail/mail.py` pour configurer vos paramètres SMTP

### Changer le port du serveur web
Modifiez la ligne dans `website/app.py` :
```python
app.run(debug=True, host='0.0.0.0', port=4000)
```

## Fonctionnalités clés

### Collecte automatique des données
Les données système sont collectées toutes les 5 minutes et stockées dans une base SQLite.

### Graphiques historiques
Des graphiques d'utilisation CPU, RAM et disque sont générés et accessibles via l'interface web.

### Alertes par email
Des alertes sont envoyées lorsque l'utilisation dépasse les seuils configurés, avec un délai minimal de 30 minutes entre deux alertes similaires.

### Interface web responsive
Une interface basée sur Bootstrap affiche les statistiques actuelles, les graphiques historiques et les alertes CERT.

### Bouton "Rafraîchir"
Le bouton sur l'interface permet de forcer une mise à jour des données sans redémarrer l'application.

## Dépannage

### Base de données corrompue
```bash
rm table_sondes.sqlite
python3 run_check.py
```

### Erreurs de permission
```bash
chmod +x sondes/disk.sh
chmod +x update.sh
```

### Problèmes d'envoi d'emails
Vérifiez `mail/config.py` et les logs dans `alertes/alertes/alertes.log`

### Redémarrage complet
```bash
pkill -f ams.py
python3 ams.py
```

## Maintenance

- La base de données est automatiquement purgée pour conserver les 500 entrées les plus récentes
- Les graphiques sont régulièrement mis à jour lors de la collecte de données

---

Développé par Alexi Miaille pour le cours de Système et Réseau.
