import json
import os
import time
import shutil
import threading
import subprocess
from datetime import datetime
import sqlite3


# Classe pour gérer les opérations sur la base de données
class GestionnaireBDD:
    def __init__(self, db_name=None):
        """Initialise le gestionnaire avec la base de données"""
        # Définir le chemin par défaut si non fourni
        if db_name is None:
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            db_name = os.path.join(project_root, 'table_sondes.sqlite')

        self.db_name = db_name
        self.initialiser_bdd()

    def initialiser_bdd(self):
        """Initialise la base de données et crée la table sondes si nécessaire"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        # Création de la table sondes si elle n'existe pas
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS sondes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom_sonde TEXT NOT NULL,
            valeur REAL NOT NULL,
            annee INTEGER,
            mois INTEGER,
            jour INTEGER,
            heure INTEGER,
            minutes INTEGER,
            secondes INTEGER,
            timestamp_complet TEXT
        )
        ''')

        conn.commit()
        conn.close()
        print(f"Base de données {self.db_name} initialisée avec succès.")

    def inserer_donnees(self, nom_sonde, valeur):
        """Insère les données d'une sonde dans la base de données"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        # Obtenir la date et l'heure actuelles
        now = datetime.now()
        annee = now.year
        mois = now.month
        jour = now.day
        heure = now.hour
        minutes = now.minute
        secondes = now.second
        timestamp_complet = now.strftime('%Y-%m-%d %H:%M:%S')

        cursor.execute('''
        INSERT INTO sondes (nom_sonde, valeur, annee, mois, jour, heure, minutes, secondes, timestamp_complet)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (nom_sonde, valeur, annee, mois, jour, heure, minutes, secondes, timestamp_complet))

        conn.commit()
        conn.close()
        print(f"Données de {nom_sonde}: {valeur} insérées à {timestamp_complet}")

        # Vérifier et purger si nécessaire après l'insertion (seulement pour une des sondes)
        if nom_sonde == "cpu":  # Ne purger qu'après l'insertion des données CPU pour éviter des opérations inutiles
            self.purger_anciennes_donnees()

    def afficher_dernieres_donnees(self, limit=9):
        """Affiche les dernières données de la base"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM sondes ORDER BY id DESC LIMIT {limit}")

        resultats = cursor.fetchall()
        conn.close()

        return resultats

    def compter_entrees(self):
        """Compte le nombre total d'entrées dans la table sondes"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM sondes")
        total = cursor.fetchone()[0]
        conn.close()
        return total

    def purger_anciennes_donnees(self, limite=500):
        """Supprime les entrées les plus anciennes pour maintenir la limite"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        # Compte le nombre actuel d'entrées
        nb_entrees = self.compter_entrees()

        # Si le nombre d'entrées dépasse la limite
        if nb_entrees > limite:
            # Calcule combien d'entrées à supprimer
            a_supprimer = nb_entrees - limite

            # Supprime les entrées les plus anciennes
            cursor.execute("""
            DELETE FROM sondes
            WHERE id IN (
                SELECT id FROM sondes
                ORDER BY id ASC
                LIMIT ?
            )
            """, (a_supprimer,))

            conn.commit()
            print(f"Purge de {a_supprimer} entrées les plus anciennes")

        conn.close()

    def create_backup(self):
        """Crée une sauvegarde de la base de données"""
        try:
            # S'assurer que la connexion à la base principale est fermée
            conn = sqlite3.connect(self.db_name)
            conn.close()

            # Obtenir un timestamp pour le nom du fichier
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = os.path.join(self.backup_dir, f'backup_{timestamp}.db')

            # Copier le fichier de la base de données
            shutil.copy2(self.db_name, backup_file)

            # Nettoyer les anciens backups (garder seulement les 3 plus récents)
            self.cleanup_old_backups()

            print(f"Backup créé avec succès: {backup_file}")
            return True
        except Exception as e:
            print(f"Erreur lors de la création du backup: {e}")
            return False

    def cleanup_old_backups(self, keep=3):
        """Nettoie les anciens backups en gardant seulement les 'keep' plus récents"""
        try:
            # Lister tous les fichiers de backup
            backup_files = [os.path.join(self.backup_dir, f) for f in os.listdir(self.backup_dir)
                            if f.startswith('backup_') and f.endswith('.db')]

            # Trier par date de modification (plus récent en premier)
            backup_files.sort(key=os.path.getmtime, reverse=True)

            # Supprimer les fichiers plus anciens
            for old_file in backup_files[keep:]:
                os.remove(old_file)
                print(f"Ancien backup supprimé: {old_file}")
        except Exception as e:
            print(f"Erreur lors du nettoyage des anciens backups: {e}")

    def backup_scheduler(self):
        """Planificateur qui exécute le backup à intervalle régulier"""
        while True:
            time.sleep(self.backup_interval)
            self.create_backup()


# Classe pour gérer les sondes
class GestionnaireSondes:
    def __init__(self, config_sondes, db_name=None):
        """
        Initialise le gestionnaire avec la configuration des sondes
        config_sondes: liste de dictionnaires avec path et id pour chaque sonde
        """
        self.sondes = config_sondes
        self.bdd = GestionnaireBDD(db_name=db_name)

    def executer_sonde(self, sonde_path, sonde_id):
        """Exécute une sonde et récupère les données JSON"""
        try:
            import os
            import sys

            # Get absolute path to the sonde file
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            absolute_sonde_path = os.path.join(base_dir, sonde_path)

            # Use sys.executable to get the correct Python interpreter
            if sonde_path.endswith('.sh'):
                resultat = subprocess.check_output(['bash', absolute_sonde_path], universal_newlines=True)
            else:
                resultat = subprocess.check_output([sys.executable, absolute_sonde_path], universal_newlines=True)

            donnees = json.loads(resultat)
            return donnees
        except Exception as e:
            print(f"Erreur avec la sonde {sonde_id}: {e}")
            return None

    def collecter_donnees(self):
        """Collecte les données de toutes les sondes et les insère dans la BDD"""
        for sonde in self.sondes:
            donnees = self.executer_sonde(sonde["path"], sonde["id"])
            if donnees:
                # Extraction de la valeur selon le type de sonde
                if sonde["id"] == "cpu":
                    valeur = donnees.get("cpu_usage", 0)
                elif sonde["id"] == "ram":
                    valeur = donnees.get("ram", 0)
                elif sonde["id"] == "disk":
                    valeur = donnees.get("disk_usage", 0)
                else:
                    # Fallback for unknown sensors
                    valeur = next(iter(donnees.values()), 0)

                self.bdd.inserer_donnees(sonde["id"], valeur)