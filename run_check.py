# run_check.py
import subprocess
import sys
import os


def main():
    print("Exécution de la collecte de données...")
    try:
        project_root = os.path.dirname(os.path.abspath(__file__))

        # Collecte de données
        stockage_main = os.path.join(project_root, "stockage", "main.py")
        subprocess.run([sys.executable, stockage_main, "--once"], timeout=30)

        # Génération des graphiques
        collector_path = os.path.join(project_root, "collector.py")
        subprocess.run([sys.executable, collector_path], timeout=30)

        # Vérification des alertes
        alertes_path = os.path.join(project_root, "alertes", "alertes.py")
        subprocess.run([sys.executable, alertes_path, "--check"], timeout=30)

        print("Collecte de données terminée avec succès")
    except Exception as e:
        print(f"Erreur lors de la collecte de données: {e}")


if __name__ == "__main__":
    main()