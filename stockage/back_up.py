import os
import shutil
from datetime import datetime


def main():
    """Fonction principale qui crée une sauvegarde de la base de données table_sondes.sqlite"""
    # Obtenir le chemin du projet
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Définir les chemins
    db_path = os.path.join(project_root, 'table_sondes.sqlite')
    backup_dir = os.path.join(project_root, 'stockage/backups')

    # Créer le répertoire de backup s'il n'existe pas
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
        print(f"Répertoire de backup créé: {backup_dir}")

    # Vérifier que la base existe
    if not os.path.exists(db_path):
        print(f"Erreur: La base de données {db_path} n'existe pas")
        return False

    # Créer un nom de fichier avec timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = os.path.join(backup_dir, f'backup_{timestamp}.sqlite')

    try:
        # Copier le fichier de la base de données
        shutil.copy2(db_path, backup_file)
        print(f"Backup créé avec succès: {backup_file}")
        return True
    except Exception as e:
        print(f"Erreur lors de la création du backup: {e}")
        return False


if __name__ == "__main__":
    main()