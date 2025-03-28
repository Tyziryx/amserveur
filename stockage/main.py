import time
from gerer_stockage import GestionnaireBDD, GestionnaireSondes

# Configuration des sondes - Modifier les chemins selon tes fichiers
SONDES_CONFIG = [
    {"path": "sondes/cpu.py", "id": "cpu"},
    {"path": "sondes/ram.py", "id": "ram"},
    {"path": "sondes/disk.sh", "id": "disk"}
]

db_name = 'identifier.sqlite'


def main():
    """Fonction principale qui exécute la collecte de données régulière"""
    # Initialisation du gestionnaire de sondes et de la BDD
    gestionnaire_bdd = GestionnaireBDD(db_name=db_name)
    gestionnaire = GestionnaireSondes(SONDES_CONFIG)
    gestionnaire.bdd = gestionnaire_bdd

    # Créer un backup initial au démarrage
    gestionnaire_bdd.create_backup()

    print("\nDémarrage de la collecte de données...")
    try:
        while True:
            # Collecte et stockage des données
            gestionnaire.collecter_donnees()
            # Attendre 3 secondes avant la prochaine collecte
            time.sleep(3)
    except KeyboardInterrupt:
        print("Arrêt de la collecte de données.")
        # Créer un backup final à l'arrêt
        gestionnaire_bdd.create_backup()


if __name__ == "__main__":
    main()