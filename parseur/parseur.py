import requests
from bs4 import BeautifulSoup
import json
import sqlite3
import time
import os


def get_html(url):
    response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
    return response.content


def get_last_alert(url):
    html = get_html(url)
    soup = BeautifulSoup(html, 'html.parser')

    # Recherche des alertes avec les bonnes classes
    alerts = soup.find_all("div", class_="item cert-alert open")

    if alerts:
        # Prendre la première alerte (généralement la plus récente)
        last_alert = alerts[0]

        # Extraire les informations structurées
        date_element = last_alert.find("span", class_="item-date")
        date = date_element.text.strip() if date_element else "Date inconnue"

        ref_element = last_alert.find("div", class_="item-ref")
        ref = ref_element.text.strip() if ref_element else "Référence inconnue"

        titre_element = last_alert.find("div", class_="item-title")
        titre = titre_element.text.strip() if titre_element else "Titre inconnu"

        return {
            "date": date,
            "reference": ref,
            "titre": titre,
        }
    else:
        return None


def init_database(db_path):
    """Initialise la base de données si elle n'existe pas déjà"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Création de la table alertes
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS alertes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        reference TEXT UNIQUE,
        date TEXT,
        titre TEXT,
        derniere_verification TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    conn.commit()
    conn.close()


def check_and_update_alerts(db_path, url):
    """Vérifie les alertes et met à jour la base de données si nécessaire"""
    # Récupérer la dernière alerte
    alerte = get_last_alert(url)

    if not alerte:
        print(json.dumps({"message": "Aucune alerte trouvée."}, ensure_ascii=False, indent=2))
        return None

    # Connexion à la base de données
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Vérifier si l'alerte existe déjà
    cursor.execute("SELECT reference FROM alertes WHERE reference = ?", (alerte["reference"],))
    existing_alert = cursor.fetchone()

    if not existing_alert:
        # Insertion de la nouvelle alerte
        cursor.execute('''
        INSERT INTO alertes (reference, date, titre, derniere_verification)
        VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        ''', (alerte["reference"], alerte["date"], alerte["titre"]))
        conn.commit()
        result = {
            "status": "nouvelle",
            "alerte": alerte
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        # Mise à jour du timestamp de dernière vérification
        cursor.execute('''
        UPDATE alertes SET derniere_verification = CURRENT_TIMESTAMP
        WHERE reference = ?
        ''', (alerte["reference"],))
        conn.commit()
        result = {
            "status": "existante",
            "alerte": alerte
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))

    conn.close()
    return alerte


def get_all_alerts(db_path):
    """Récupère toutes les alertes de la base de données"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT reference, date, titre FROM alertes ORDER BY id DESC")

    alerts = []
    for row in cursor.fetchall():
        alerts.append({
            "reference": row[0],
            "date": row[1],
            "titre": row[2]
        })

    conn.close()
    return alerts


def main():
    db_path = "parseur.sqlite"
    url = "https://www.cert.ssi.gouv.fr/"

    # Initialisation de la base de données
    init_database(db_path)

    print("Surveillance des alertes du CERT-FR démarrée...")

    # Exécuter une première fois pour s'assurer d'ajouter l'alerte initiale
    print("\nPremière vérification...")
    initial_alert = check_and_update_alerts(db_path, url)

    if initial_alert:
        # Afficher toutes les alertes en JSON
        all_alerts = get_all_alerts(db_path)
        print("\nToutes les alertes en base:")
        print(json.dumps(all_alerts, ensure_ascii=False, indent=2))

    try:
        while True:
            time.sleep(60)  # Attendre 1 minute
            print(f"\nVérification à {time.strftime('%H:%M:%S')}...")
            check_and_update_alerts(db_path, url)
    except KeyboardInterrupt:
        print("\nSurveillance arrêtée.")


if __name__ == "__main__":
    main()