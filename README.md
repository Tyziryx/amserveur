AdminMonitoring System (AMS)
<img alt="Version" src="https://img.shields.io/badge/version-1.0-blue.svg">
<img alt="Python" src="https://img.shields.io/badge/Python-3.6+-green.svg">
<img alt="License" src="https://img.shields.io/badge/license-MIT-lightgrey.svg">
📑 Table des matières
Introduction
Fonctionnalités
Installation
Architecture du projet
Interface utilisateur
Modules principaux
Configuration avancée
Dépannage
Documentation technique
Contributions
Crédits
📋 Introduction
AdminMonitoring System (AMS) est une solution complète de surveillance système développée dans le cadre du cours de Système et Réseau. Cette application permet le suivi en temps réel des métriques essentielles d'un serveur, génère des visualisations graphiques et alerte en cas de dépassement de seuils critiques.

Objectifs pédagogiques:

Application pratique des concepts de programmation système
Utilisation de Python pour la surveillance de ressources
Implémentation d'une base de données pour le stockage de métriques
Création d'une interface web avec Flask
Automatisation des alertes et notifications
✨ Fonctionnalités
Surveillance système
Monitoring CPU: Suivi du pourcentage d'utilisation processeur
Monitoring RAM: Suivi du pourcentage d'utilisation mémoire
Monitoring Disque: Suivi du pourcentage d'espace disque utilisé
Visualisation des données
Graphiques historiques: Visualisation des tendances d'utilisation
Interface web: Tableau de bord ergonomique et responsive
Actualisation en temps réel: Rafraîchissement sur demande des données
Système d'alertes
Alertes par email: Notifications automatiques
Seuils configurables: Personnalisation des niveaux d'alerte
Anti-spam: Intervalle minimal entre les alertes similaires
Sécurité
Veille CERT: Intégration des alertes de sécurité du CERT-FR
Affichage centralisé: Toutes les informations critiques au même endroit
🔧 Installation
Prérequis
Système Linux/macOS
Python 3.6+
pip (gestionnaire de paquets Python)
Connexion Internet (pour les mises à jour et alertes CERT)
Méthode rapide (recommandée)
Installation manuelle des dépendances
Si le script automatique échoue, vous pouvez installer manuellement les dépendances:

🏗 Architecture du projet
Structure des répertoires
Flux de données
Les sondes collectent les données brutes du système
Le module de stockage enregistre ces données dans une base SQLite
Le module graphiques génère des visualisations à partir de ces données
Le module alertes vérifie les dépassements de seuils
L'interface web affiche toutes ces informations de façon centralisée
🖥 Interface utilisateur
Démarrage de l'application
Accédez ensuite à votre tableau de bord via: http://localhost:4000

Éléments de l'interface
Cards de métriques: Affichent les valeurs actuelles CPU, RAM, disque
Graphiques historiques: Visualisation temporelle des métriques
Tableau des alertes CERT: Affiche les alertes de sécurité récentes
Bouton "Rafraîchir": Met à jour les données et graphiques manuellement
Utilisation quotidienne recommandée
Consultez régulièrement le tableau de bord pour surveiller l'état du système
Configurez le système pour démarrer automatiquement au boot (voir ci-dessous)
Configurez les alertes email avec vos paramètres SMTP personnels
Configuration de démarrage automatique (systemd)
Créez un fichier service systemd:

Contenu du fichier:

Activez le service:

📦 Modules principaux
Système de sondes (sondes/)
Les sondes sont des scripts légers qui collectent les métriques systèmes:

cpu.py: Utilise psutil pour mesurer l'utilisation CPU
ram.py: Analyse la mémoire via psutil
disk.sh: Script bash qui utilise df pour l'espace disque
Chaque sonde renvoie un objet JSON standardisé pour faciliter l'interopérabilité.

Gestion des données (stockage/)
Module central qui gère la persistance des données:

gerer_stockage.py:

GestionnaireBDD: Interface avec la base SQLite
GestionnaireSondes: Exécute les sondes et enregistre les données
main.py: Orchestration de la collecte périodique

back_up.py: Création de sauvegardes

back_up_restore.py: Restauration de données

Visualisation (graphiques/)
Module responsable de la création des graphiques:

graphic.py: Utilise Matplotlib pour créer des visualisations temporelles
GenerateurGraphiques: Classe principale qui gère la création des graphiques
Système d'alertes (alertes/)
Module qui détecte et notifie les situations critiques:

alertes.py:
Vérifie si les métriques dépassent les seuils configurés
Envoie des emails d'alerte via le module mail
Maintient un journal des alertes pour référence
Interface web (website/)
Application web Flask qui centralise toutes les informations:

app.py: Serveur Flask avec routes / et /refresh
index.html: Template Bootstrap responsive
Surveillance CERT (parseur/)
Module qui surveille les alertes de sécurité officielles:

parseur.py:
Analyse les alertes du CERT-FR
Stocke les alertes dans une base de données
Met à jour les informations périodiquement
⚙ Configuration avancée
Modification des seuils d'alerte
Éditez le fichier alertes.py:

Configuration de l'envoi d'emails
Créez le fichier mail/config.py s'il n'existe pas:
Modifiez mail.py pour configurer votre serveur SMTP:
Paramétrage de l'interface web
Pour modifier le port ou activer le mode debug, éditez app.py:

Configuration de la rétention de données
Pour modifier la politique de conservation des données, éditez gerer_stockage.py:

Fréquence de collecte
Modifiez l'intervalle de collecte dans main.py:

🛠 Dépannage
Problèmes courants et solutions
Base de données inaccessible ou corrompue
Erreurs de permission sur les scripts
Problèmes d'envoi d'emails
Interface web inaccessible
Aucune donnée affichée
Journal des erreurs
Le système maintient plusieurs fichiers de log:

alertes/alertes.log: Journal des alertes envoyées
cron.log: Si configuré avec cron, journal des exécutions périodiques
📖 Documentation technique
Structure de la base de données
Table sondes (table_sondes.sqlite)
Table alertes (parseur.sqlite)
Format des données des sondes
Chaque sonde retourne un objet JSON avec une clé unique:

Algorithme de détection des alertes
Récupération de la dernière valeur de chaque métrique
Comparaison avec les seuils configurés
Si dépassement, vérification de l'historique récent
Si aucune alerte similaire récente, envoi d'un email
Mise à jour du journal des alertes
Cycle de vie des données
Collecte: Exécution des sondes à intervalles réguliers
Stockage: Insertion dans la base SQLite
Traitement: Génération des graphiques, vérification des seuils
Purge: Suppression des données anciennes (limite configurable)
Sauvegarde: Création périodique de backups
👥 Contributions
Ce projet a été développé dans un contexte éducatif et peut être amélioré de plusieurs façons:

Améliorations possibles
Ajout de nouvelles sondes (température, charge système, etc.)
Support pour la surveillance de plusieurs machines
Authentification sur l'interface web
API REST pour l'intégration avec d'autres services
Tests unitaires et fonctionnels
Containerisation avec Docker
Bonnes pratiques pour contribuer
Forker le projet
Créer une branche pour votre fonctionnalité
Soumettre une Pull Request avec une description détaillée
Respecter les normes de codage existantes (PEP8 pour Python)
📝 Crédits
Développeur: Alexi Miaille
Contexte: Cours de Système et Réseau (L2 Informatique)
Année: 2023

Licence
Ce projet est distribué sous licence MIT à des fins éducatives uniquement.

"La simplicité est la sophistication suprême." - Leonardo da Vinci