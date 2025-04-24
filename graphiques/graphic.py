import sqlite3
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import os
import json
from datetime import datetime


class GenerateurGraphiques:
    def __init__(self, db_path='../table_sondes.sqlite', cert_db_path='../parseur/parseur.sqlite'):
        """
        Initialise le générateur de graphiques avec les chemins des bases de données
        """
        self.db_path = db_path
        self.cert_db_path = cert_db_path

        # Save directly to the Flask static folder with absolute path
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(script_dir)
        self.output_dir = os.path.join(project_root, 'website', 'static')

        print(f"Output directory for graphs: {self.output_dir}")

        # Créer le dossier de sortie s'il n'existe pas
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def _get_sondes_data(self):
        """Récupère les données des sondes depuis la base de données"""
        try:
            print(f"Opening database: {self.db_path}")
            conn = sqlite3.connect(self.db_path)
            
            # Ajouter cette ligne pour voir le contenu brut
            print("Contenu de la base de données:")
            test_query = "SELECT timestamp_complet, valeur, nom_sonde FROM sondes LIMIT 5"
            test_df = pd.read_sql_query(test_query, conn)
            print(test_df)

            # Use correct column names based on the schema
            cpu_query = "SELECT timestamp_complet as timestamp, valeur FROM sondes WHERE nom_sonde='cpu' ORDER BY timestamp_complet"
            ram_query = "SELECT timestamp_complet as timestamp, valeur FROM sondes WHERE nom_sonde='ram' ORDER BY timestamp_complet"
            disk_query = "SELECT timestamp_complet as timestamp, valeur FROM sondes WHERE nom_sonde='disk' ORDER BY timestamp_complet"

            cpu_df = pd.read_sql_query(cpu_query, conn)
            ram_df = pd.read_sql_query(ram_query, conn)
            disk_df = pd.read_sql_query(disk_query, conn)

            # Conversion plus robuste des timestamps
            for df in [cpu_df, ram_df, disk_df]:
                if not df.empty:
                    # Conversion explicite et robuste
                    df['timestamp'] = pd.to_datetime(df['timestamp'], format='%Y-%m-%d %H:%M:%S', errors='coerce')
                    df['valeur'] = pd.to_numeric(df['valeur'], errors='coerce')
                    print(f"Premier timestamp dans DataFrame: {df['timestamp'].iloc[0] if len(df) > 0 else 'aucun'}")

            conn.close()
            return cpu_df, ram_df, disk_df
        except Exception as e:
            print(f"Erreur lors de la récupération des données: {str(e)}")
            import traceback
            traceback.print_exc()
            return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    def _get_alertes_data(self):
        """Récupère les données des alertes CERT"""
        try:
            if not os.path.exists(self.cert_db_path):
                print(f"La base de données {self.cert_db_path} n'existe pas")
                return None

            conn = sqlite3.connect(self.cert_db_path)
            alertes_df = pd.read_sql_query("SELECT date, reference, titre, derniere_verification FROM alertes", conn)
            conn.close()

            # Convertir les dates
            alertes_df['derniere_verification'] = pd.to_datetime(alertes_df['derniere_verification'])

            return alertes_df
        except Exception as e:
            print(f"Erreur lors de la récupération des alertes: {e}")
            return None

    def cleanup_old_graphs(self):
        """Supprime les anciennes images de graphiques"""
        try:
            if not os.path.exists(self.output_dir):
                print(f"Le dossier {self.output_dir} n'existe pas encore")
                return

            for filename in os.listdir(self.output_dir):
                if filename.endswith('.png'):
                    filepath = os.path.join(self.output_dir, filename)
                    os.remove(filepath)
                    print(f"Ancien graphique supprimé: {filepath}")
        except Exception as e:
            print(f"Erreur lors de la suppression des anciens graphiques: {e}")

    def generer_graphique_ram(self):
        """Génère un graphique pour l'utilisation de la RAM"""
        try:
            _, ram_df, _ = self._get_sondes_data()

            if ram_df.empty:
                print("Aucune donnée RAM à afficher")
                return

            plt.figure(figsize=(12, 6))
            plt.plot(ram_df['timestamp'], ram_df['valeur'], 'g-', linewidth=2)
            plt.title('Utilisation RAM')
            plt.ylabel('Pourcentage (%)')
            plt.xlabel('Heure')
            plt.grid(True)
            plt.ylim(0, 100)

            # Format de date sur l'axe X
            plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
            plt.gcf().autofmt_xdate()

            # Enregistrer le graphique
            plt.tight_layout()
            plt.savefig(f'{self.output_dir}/ram_usage.png')
            plt.close()
            print(f"Graphique RAM enregistré dans {self.output_dir}/ram_usage.png")
        except Exception as e:
            print(f"Erreur lors de la génération du graphique RAM: {str(e)}")

    def generer_graphique_cpu(self):
        """Génère un graphique pour l'utilisation du CPU"""
        try:
            cpu_df, _, _ = self._get_sondes_data()

            if cpu_df.empty:
                print("Aucune donnée CPU à afficher")
                return

            plt.figure(figsize=(12, 6))
            plt.plot(cpu_df['timestamp'], cpu_df['valeur'], 'b-', linewidth=2)
            plt.title('Utilisation CPU')
            plt.ylabel('Pourcentage (%)')
            plt.xlabel('Heure')
            plt.grid(True)
            plt.ylim(0, 100)

            # Format de date sur l'axe X - version simplifiée et robuste
            plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
            # Plus d'options pour l'affichage de l'axe X
            plt.gcf().autofmt_xdate()
            
            # Forcer la localisation
            import locale
            try:
                locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')
            except:
                try:
                    locale.setlocale(locale.LC_TIME, 'fr_FR')
                except:
                    pass

            # Enregistrer le graphique
            plt.tight_layout()
            plt.savefig(f'{self.output_dir}/cpu_usage.png')
            plt.close()
            print(f"Graphique CPU enregistré dans {self.output_dir}/cpu_usage.png")
        except Exception as e:
            print(f"Erreur lors de la génération du graphique CPU: {str(e)}")

    def generer_graphique_disque(self):
        """Génère un graphique pour l'utilisation du disque"""
        try:
            _, _, disk_df = self._get_sondes_data()

            if disk_df.empty:
                print("Aucune donnée disque à afficher")
                return

            plt.figure(figsize=(12, 6))
            plt.plot(disk_df['timestamp'], disk_df['valeur'], 'r-', linewidth=2)
            plt.title('Utilisation Disque')
            plt.ylabel('Pourcentage (%)')
            plt.xlabel('Heure')
            plt.grid(True)
            plt.ylim(0, 100)

            # Format de date sur l'axe X , affiche seulement l'heure et commence a 00H toutes les 15 minutes ap
            plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
            plt.gcf().autofmt_xdate()

            # Enregistrer le graphique
            plt.savefig(f'{self.output_dir}/disk_usage.png')
            plt.close()
            print(f"Graphique disque enregistré dans {self.output_dir}/disk_usage.png")
        except Exception as e:
            print(f"Erreur lors de la génération du graphique disque: {str(e)}")

    def generer_tous_graphiques(self):
        """Génère tous les graphiques disponibles"""
        # Nettoyer les anciens graphiques avant d'en générer de nouveaux
        self.cleanup_old_graphs()

        self.generer_graphique_cpu()
        self.generer_graphique_ram()
        self.generer_graphique_disque()
        print("Génération de tous les graphiques terminée.")


if __name__ == "__main__":
    generateur = GenerateurGraphiques()
    generateur.generer_tous_graphiques()