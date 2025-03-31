#!/bin/bash

# installation.sh - Admin Monitoring System installation script
# This script installs all dependencies for the monitoring application
# Run with: bash installation.sh

# Print colored messages
print_message() {
    echo -e "\e[1;34m>>> $1\e[0m"
}

print_success() {
    echo -e "\e[1;32m>>> $1\e[0m"
}

print_error() {
    echo -e "\e[1;31m>>> ERROR: $1\e[0m"
}

# Check if we're running as root or using sudo
if [ "$EUID" -ne 0 ]; then
    print_error "This script must be run as root or with sudo"
    exit 1
fi

# Update package lists
print_message "Updating package lists..."
apt-get update

# Install system packages
print_message "Installing system packages..."
apt-get install -y python3 python3-pip python3-dev \
    sqlite3 curl wget htop git screen tmux \
    build-essential libfreetype6-dev pkg-config

# Install Python packages
print_message "Installing Python packages..."
pip3 install --upgrade pip
pip3 install psutil pandas matplotlib flask requests beautifulsoup4 lxml python-daemon

# Create directory structure if it doesn't exist
if [ ! -d "website/static" ]; then
    print_message "Creating website directory structure..."
    mkdir -p website/static
    mkdir -p website/templates
fi

if [ ! -d "sondes" ]; then
    print_message "Creating sondes directory..."
    mkdir -p sondes
fi

if [ ! -d "parseur" ]; then
    print_message "Creating parseur directory..."
    mkdir -p parseur
fi

if [ ! -d "stockage" ]; then
    print_message "Creating stockage directory..."
    mkdir -p stockage
fi

if [ ! -d "graphiques" ]; then
    print_message "Creating graphiques directory..."
    mkdir -p graphiques
fi

# Fix any potential permissions issues
print_message "Setting correct permissions..."
current_user=$(who am i | awk '{print $1}')
chown -R $current_user:$current_user .
chmod +x sondes/*.sh 2>/dev/null || true

# Create empty database files if they don't exist
print_message "Creating database files if needed..."
if [ ! -f "table_sondes.sqlite" ]; then
    touch table_sondes.sqlite
    sqlite3 table_sondes.sqlite "CREATE TABLE IF NOT EXISTS sondes (id INTEGER PRIMARY KEY, nom_sonde TEXT, valeur REAL, timestamp_complet TEXT);"
    print_success "Created table_sondes.sqlite"
fi

if [ ! -f "parseur/parseur.sqlite" ]; then
    touch parseur/parseur.sqlite
    sqlite3 parseur/parseur.sqlite "CREATE TABLE IF NOT EXISTS alertes (id INTEGER PRIMARY KEY, date TEXT, titre TEXT, lien TEXT);"
    print_success "Created parseur/parseur.sqlite"
fi

# Fixed ams.py for Linux
print_message "Updating ams.py for Linux compatibility..."
cat > ams.py << 'EOL'
#!/usr/bin/env python3
# ams.py - Admin Monitoring System
import subprocess
import threading
import time
import sys
import os
import atexit
import signal

# Global process references to prevent garbage collection
processes = []

def cleanup():
    """Clean up all running processes on exit"""
    print("Cleaning up processes...")
    for proc in processes:
        if proc.poll() is None:  # If process is still running
            try:
                proc.terminate()
                proc.wait(timeout=2)
            except Exception:
                proc.kill()

def run_collector():
    """Exécute la collecte de données régulièrement"""
    while True:
        print("Mise à jour des données en arrière-plan...")
        try:
            # Run stockage/main.py with the --once flag to collect data just once
            project_root = os.path.dirname(os.path.abspath(__file__))
            stockage_main = os.path.join(project_root, "stockage", "main.py")

            # Run with detached process
            process = subprocess.Popen(
                [sys.executable, stockage_main, "--once"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            processes.append(process)

            # Wait a bit for data collection
            time.sleep(5)

            # Run collector to generate graphs
            collector_path = os.path.join(project_root, "collector.py")
            process = subprocess.Popen(
                [sys.executable, collector_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            processes.append(process)

        except Exception as e:
            print(f"Erreur lors de la mise à jour des données: {e}")

        # Sleep for 5 minutes
        time.sleep(300)

def run_web_server():
    """Démarre le serveur web"""
    os.environ["FLASK_APP"] = "website/app.py"
    os.environ["FLASK_DEBUG"] = "0"  # Disable debug mode for stability

    web_process = subprocess.Popen(
        [sys.executable, "-m", "flask", "run", "--host=0.0.0.0", "--no-reload"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    processes.append(web_process)

    try:
        # Wait for the web server to terminate
        web_process.wait()
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    # Register cleanup function
    atexit.register(cleanup)

    # Handle signals
    signal.signal(signal.SIGTERM, lambda *args: sys.exit(0))

    # Execute collector once on startup
    try:
        print("Initial data collection...")
        project_root = os.path.dirname(os.path.abspath(__file__))
        stockage_main = os.path.join(project_root, "stockage", "main.py")

        # Run data collection
        subprocess.run([sys.executable, stockage_main, "--once"], timeout=30)

        # Generate graphs
        collector_path = os.path.join(project_root, "collector.py")
        subprocess.run([sys.executable, collector_path], timeout=30)

    except Exception as e:
        print(f"Initial data collection error: {e}")

    # Démarrer la collecte de données en arrière-plan
    collector_thread = threading.Thread(target=run_collector)
    collector_thread.daemon = True
    collector_thread.start()

    # Démarrer le serveur web en premier plan
    run_web_server()
EOL

# Fix website/app.py for Linux
print_message "Updating website/app.py for Linux compatibility..."
mkdir -p website
cat > website/app.py << 'EOL'
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

        # First run stockage/main.py to collect new data
        subprocess.Popen([sys.executable, stockage_main, "--once"],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE)

        # Then run collector.py to generate graphs
        collector_path = os.path.join(project_root, 'collector.py')
        subprocess.Popen([sys.executable, collector_path],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE)

        # Redirect back to index page
        return redirect(url_for('index'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"Erreur lors de la mise à jour: {str(e)}"

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
EOL

# Make the script executable
print_message "Making files executable..."
chmod +x ams.py

print_success "Installation complete!"
print_success "You can now start the application by running: python3 ams.py"
print_success "Access the web interface at: http://[your-ip-address]:5000"