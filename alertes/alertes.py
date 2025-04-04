import sys
import os
import time
import sqlite3
from datetime import datetime, timedelta

# Ajouter le répertoire parent au path pour pouvoir importer les modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configuration des seuils critiques (en pourcentage)
SEUILS = {
    "cpu": 80,  # CPU usage > 80%
    "ram": 80,  # RAM usage > 80%
    "disk": 85  # Disk usage > 85%
}

# Intervalle minimal entre deux alertes pour le même problème (en minutes)
INTERVALLE_ALERTES = 30


class GestionnaireAlertes:
    def __init__(self, db_path=None, log_path=None):
        """Initialise le gestionnaire d'alertes"""
        # Obtenir le chemin absolu du projet
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        # Définir les chemins par défaut en utilisant des chemins absolus
        if db_path is None:
            db_path = os.path.join(project_root,"table_sondes.sqlite")
        if log_path is None:
            log_path = os.path.join(project_root, "alertes", "alertes.log")

        self.db_path = db_path
        self.log_path = log_path
        self.dernieres_alertes = {
            "cpu": None,
            "ram": None,
            "disk": None
        }
        self.init_log()

    def init_log(self):
        """Initialise le fichier de log"""
        if not os.path.exists(os.path.dirname(self.log_path)):
            os.makedirs(os.path.dirname(self.log_path))

        # Créer le fichier s'il n'existe pas
        if not os.path.exists(self.log_path):
            with open(self.log_path, 'w') as f:
                f.write(f"# Journal des alertes - Créé le {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

    def log(self, message):
        """Ajoute un message au fichier de log"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open(self.log_path, 'a') as f:
            f.write(f"[{timestamp}] {message}\n")
        print(f"[{timestamp}] {message}")

    def get_derniere_valeur(self, sonde_id):
        """Récupère la dernière valeur pour une sonde spécifique"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Récupérer la dernière valeur
            cursor.execute("""
                SELECT valeur FROM sondes
                WHERE nom_sonde = ?
                ORDER BY id DESC LIMIT 1
            """, (sonde_id,))

            resultat = cursor.fetchone()
            conn.close()

            if resultat:
                return float(resultat[0])
            return None
        except Exception as e:
            self.log(f"Erreur lors de la lecture des données de {sonde_id}: {e}")
            return None

    def peut_envoyer_alerte(self, sonde_id):
        """Vérifie si on peut envoyer une alerte (pour éviter le spam)"""
        derniere_alerte = self.dernieres_alertes[sonde_id]
        if derniere_alerte is None:
            return True

        maintenant = datetime.now()
        temps_ecoule = maintenant - derniere_alerte

        return temps_ecoule.total_seconds() / 60 >= INTERVALLE_ALERTES

    def envoyer_alerte(self, sonde_id, valeur):
        """Envoie une alerte par email"""
        if not self.peut_envoyer_alerte(sonde_id):
            self.log(f"Alerte {sonde_id} ignorée (délai minimum non atteint)")
            return False

        # Mettre à jour le timestamp de la dernière alerte
        self.dernieres_alertes[sonde_id] = datetime.now()

        # Préparer l'objet et le contenu de l'email
        seuil = SEUILS[sonde_id]

        if sonde_id == "cpu":
            objet = f"ALERTE - Utilisation CPU critique: {valeur}%"
            contenu = f"""Alerte système critique détectée !

L'utilisation du CPU a atteint un niveau critique: {valeur}% (seuil: {seuil}%)

Cette surcharge peut entraîner des ralentissements significatifs ou des interruptions
de service. Une intervention peut être nécessaire.

Date et heure de l'alerte: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        elif sonde_id == "ram":
            objet = f"ALERTE - Mémoire RAM critique: {valeur}%"
            contenu = f"""Alerte système critique détectée !

L'utilisation de la mémoire RAM a atteint un niveau critique: {valeur}% (seuil: {seuil}%)

Une utilisation élevée de la mémoire peut provoquer des plantages du système ou des
performances dégradées. Veuillez vérifier les processus consommant beaucoup de mémoire.

Date et heure de l'alerte: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        elif sonde_id == "disk":
            objet = f"ALERTE - Espace disque critique: {valeur}%"
            contenu = f"""Alerte système critique détectée !

L'utilisation de l'espace disque a atteint un niveau critique: {valeur}% (seuil: {seuil}%)

Un espace disque insuffisant peut empêcher le bon fonctionnement des services et la
création de nouveaux fichiers. Veuillez libérer de l'espace rapidement.

Date et heure de l'alerte: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

        try:
            sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'mail'))
            import mail

            # Sauvegarde des valeurs originales si nécessaire
            mail.send_email(objet, contenu)

            self.log(f"Envoi d'alerte par email avec objet: {objet}")
            self.log(f"Alerte {sonde_id} envoyée: {valeur}% > {seuil}%")
            return True
        except Exception as e:
            self.log(f"Erreur lors de l'envoi de l'alerte {sonde_id}: {e}")
            return False

    def verifier_seuils(self):
        """Vérifie les valeurs des sondes par rapport aux seuils critiques"""
        for sonde_id, seuil in SEUILS.items():
            valeur = self.get_derniere_valeur(sonde_id)

            if valeur is not None:
                if valeur > seuil:
                    self.envoyer_alerte(sonde_id, valeur)
                else:
                    self.log(f"Sonde {sonde_id}: {valeur}% (normal)")


def main():
    """Fonction principale"""
    import argparse

    parser = argparse.ArgumentParser(description="Système de surveillance des alertes")
    parser.add_argument("--check", action="store_true", help="Vérifier les alertes une seule fois puis quitter")
    args = parser.parse_args()

    gestionnaire = GestionnaireAlertes()

    if args.check:
        print("Vérification unique des seuils d'alerte...")
        gestionnaire.log("Vérification unique des seuils d'alerte")
        gestionnaire.verifier_seuils()
        return

    print(f"Démarrage du système d'alertes...")
    gestionnaire.log("Système d'alertes démarré")

    try:
        while True:
            gestionnaire.verifier_seuils()
            # Vérifier toutes les 5 minutes
            time.sleep(300)
    except KeyboardInterrupt:
        gestionnaire.log("Arrêt du système d'alertes")
        print("Système d'alertes arrêté.")


if __name__ == "__main__":
    main()