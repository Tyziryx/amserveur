import smtplib
import ssl
import os
import certifi
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Configuration
port = 465
smtp_server = "partage.univ-avignon.fr"
login = "alexi.miaille@alumni.univ-avignon.fr"
try:
    from config import SMTP_PASSWORD

    password = SMTP_PASSWORD
except ImportError:
    password = input("Entrez votre mot de passe SMTP: ")

# Configuration des emails
sender_email = login
receiver_email = login  # Par défaut, envoyer à soi-même

# Contexte SSL
context = ssl.create_default_context(cafile=certifi.where())

# Variables globales pour le contenu du mail
mail_object = "Test email"
mail_text = "Contenu par défaut"


def send_email(objet, contenu):
    """Envoie un email avec l'objet et le contenu spécifiés"""
    global mail_object, mail_text

    # Mettre à jour les variables
    mail_object = objet
    mail_text = contenu

    # Créer le message
    message = MIMEMultipart()
    message["Subject"] = mail_object
    message["From"] = sender_email
    message["To"] = receiver_email

    # Ajouter le contenu
    part = MIMEText(mail_text, "plain")
    message.attach(part)

    try:
        with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
            server.login(login, password)
            server.sendmail(sender_email, receiver_email, message.as_string())
            print(f'Email envoyé avec succès: "{mail_object}"')
            return True
    except Exception as e:
        print(f"Erreur lors de l'envoi de l'email: {e}")
        return False


# Si le script est exécuté directement
if __name__ == "__main__":
    send_email("Test depuis mail.py", "Ceci est un test d'envoi d'email.")