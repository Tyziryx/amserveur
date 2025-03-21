import time
from stockage.gerer_stockage import GestionnaireSondes, GestionnaireBDD

# Configuration des sondes - Modifier les chemins selon tes fichiers
SONDES_CONFIG = [
    {"path": "sondes/cpu.py", "id": "cpu"},
    {"path": "sondes/ram.py", "id": "ram"},
    {"path": "sondes/disk.sh", "id": "disk"}
]

db_name = 'identifier.sqlite'


def main():
    """Fonction principale qui exécute la collecte de données régulière"""
    # Initialisation du gestionnaire de sondes
    gestionnaire = GestionnaireSondes(SONDES_CONFIG)
    """
    gestionnaire_bdd = GestionnaireBDD(db_name=db_name)

    gestionnaire.bdd = gestionnaire_bdd

    # Récupérer et afficher les dernières données
    resultats = gestionnaire_bdd.afficher_dernieres_donnees(limit=99)

    print("Dernières données enregistrées:")
    for resultat in resultats:
        id, nom_sonde, valeur, annee, mois, jour, heure, minutes, secondes, timestamp = resultat
        print(f"ID: {id} | Capteur: {nom_sonde} | Valeur: {valeur} | Timestamp: {timestamp}")
        print("-" * 80)
"""
    print("\nDémarrage de la collecte de données...")
    try:
        while True:
            # Collecte et stockage des données
            gestionnaire.collecter_donnees()
            # Attendre 3 secondes avant la prochaine collecte
            time.sleep(3)
    except KeyboardInterrupt:
        print("Arrêt de la collecte de données.")


if __name__ == "__main__":
    main()