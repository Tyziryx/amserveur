import time
from gerer_stockage import GestionnaireBDD, GestionnaireSondes
import sys
import os

# Configuration des sondes - Modifier les chemins selon tes fichiers
SONDES_CONFIG = [
    {"path": "sondes/cpu.py", "id": "cpu"},
    {"path": "sondes/ram.py", "id": "ram"},
    {"path": "sondes/disk.sh", "id": "disk"}
]

# Database in root directory
db_name = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'table_sondes.sqlite')


def main():
    """Fonction principale qui exécute la collecte de données régulière"""
    # Initialisation du gestionnaire de sondes et de la BDD
    gestionnaire_bdd = GestionnaireBDD(db_name=db_name)
    gestionnaire = GestionnaireSondes(SONDES_CONFIG)
    gestionnaire.bdd = gestionnaire_bdd

    print("\nDémarrage de la collecte de données...")

    # Check if we should run once or continuously
    run_once = "--once" in sys.argv

    if run_once:
        # Just collect once and exit
        gestionnaire.collecter_donnees()
        print("Données collectées une fois.")
    else:
        # Run continuously
        try:
            while True:
                # Collecte et stockage des données
                gestionnaire.collecter_donnees()
                time.sleep(1)  # 1 second between collections for testing
        except KeyboardInterrupt:
            print("Arrêt de la collecte de données.")
            # Créer un backup final à l'arrêt
            gestionnaire_bdd.create_backup()


if __name__ == "__main__":
    main()