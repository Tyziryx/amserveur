import os
import shutil
import glob
from datetime import datetime


class RestoreManager:
    def __init__(self, db_path=None, backup_dir=None):
        """Initialise le gestionnaire de restauration avec les chemins"""
        # Obtenir le chemin du projet
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        # Définir le chemin par défaut de la BDD si non fourni
        if db_path is None:
            db_path = os.path.join(project_root, 'table_sondes.sqlite')

        # Définir le répertoire de backup par défaut si non fourni
        if backup_dir is None:
            backup_dir = os.path.join(project_root, 'stockage/backups')

        self.db_path = db_path
        self.backup_dir = backup_dir

        # Vérifier que le répertoire de backup existe
        if not os.path.exists(self.backup_dir):
            print(f"Erreur: Le répertoire de backup {self.backup_dir} n'existe pas")

    def restore_latest_backup(self):
        """Restaure la base de données à partir de la dernière sauvegarde disponible"""
        try:
            # Trouver le fichier de backup le plus récent
            backup_files = glob.glob(os.path.join(self.backup_dir, 'backup_*.sqlite'))

            if not backup_files:
                print(f"Erreur: Aucun fichier de backup trouvé dans {self.backup_dir}")
                return False

            # Trier par date de modification (plus récent en premier)
            latest_backup = max(backup_files, key=os.path.getmtime)

            # Vérifier que le backup existe
            if not os.path.exists(latest_backup):
                print(f"Erreur: Le fichier de backup {latest_backup} n'existe pas")
                return False

            print(f"Restauration à partir de: {latest_backup}")

            # Remplacer la base actuelle par la sauvegarde
            shutil.copy2(latest_backup, self.db_path)

            print(f"Base de données restaurée avec succès à partir de: {os.path.basename(latest_backup)}")
            return True

        except Exception as e:
            print(f"Erreur lors de la restauration: {e}")
            return False


def main():
    """Fonction principale"""
    manager = RestoreManager()
    manager.restore_latest_backup()


if __name__ == "__main__":
    main()