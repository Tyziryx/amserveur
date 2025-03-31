# website/app.py
from flask import Flask, render_template, jsonify, redirect, url_for
import sqlite3
import os
import subprocess
import sys
from datetime import datetime

app = Flask(__name__)


@app.route('/')
def index():
    # Récupérer les dernières données des sondes
    try:
        # Use correct path to database file (in project root)
        db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'table_sondes.sqlite')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Get latest stats
        latest_stats = {
            'cpu': 0,
            'ram': 0,
            'disk': 0
        }

        # Get CPU data - using correct column name "nom_sonde"
        cursor.execute("SELECT valeur FROM sondes WHERE nom_sonde='cpu' ORDER BY timestamp_complet DESC LIMIT 1")
        cpu_result = cursor.fetchone()
        if cpu_result:
            latest_stats['cpu'] = round(float(cpu_result[0]), 1)

        # Get RAM data
        cursor.execute("SELECT valeur FROM sondes WHERE nom_sonde='ram' ORDER BY timestamp_complet DESC LIMIT 1")
        ram_result = cursor.fetchone()
        if ram_result:
            latest_stats['ram'] = round(float(ram_result[0]), 1)

        # Get Disk data
        cursor.execute("SELECT valeur FROM sondes WHERE nom_sonde='disk' ORDER BY timestamp_complet DESC LIMIT 1")
        disk_result = cursor.fetchone()
        if disk_result:
            latest_stats['disk'] = round(float(disk_result[0]), 1)

        # Get CERT alerts
        cert_db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'parseur',
                                    'parseur.sqlite')
        cert_conn = sqlite3.connect(cert_db_path)
        cert_cursor = cert_conn.cursor()
        cert_cursor.execute("SELECT date, titre FROM alertes ORDER BY date DESC LIMIT 10")
        alertes = [{"date": row[0], "titre": row[1]} for row in cert_cursor.fetchall()]

        cert_conn.close()
        conn.close()

        print(f"Stats retrieved: CPU={latest_stats['cpu']}%, RAM={latest_stats['ram']}%, DISK={latest_stats['disk']}%")
    except Exception as e:
        print(f"Erreur lors de la récupération des données: {str(e)}")
        import traceback
        traceback.print_exc()
        latest_stats = {'cpu': 0, 'ram': 0, 'disk': 0}
        alertes = []

    return render_template('index.html',
                           stats=latest_stats,
                           alertes=alertes,
                           timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))


@app.route('/refresh')
def refresh_data():
    """Force une mise à jour des données sans quitter la page"""
    try:
        # Get absolute paths
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        stockage_main = os.path.join(project_root, "stockage", "main.py")

        print(f"Running stockage_main: {stockage_main}")

        # Use detached process on Windows
        startupinfo = None
        if os.name == 'nt':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = 0  # SW_HIDE

        # First run stockage/main.py to collect new data
        subprocess.Popen([sys.executable, stockage_main, "--once"],
                        startupinfo=startupinfo,
                        creationflags=subprocess.CREATE_NO_WINDOW)

        # Then run collector.py to generate graphs
        collector_path = os.path.join(project_root, 'collector.py')
        subprocess.Popen([sys.executable, collector_path],
                        startupinfo=startupinfo,
                        creationflags=subprocess.CREATE_NO_WINDOW)

        # Redirect back to index page
        return redirect(url_for('index'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"Erreur lors de la mise à jour: {str(e)}"


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')