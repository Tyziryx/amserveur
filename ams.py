# ams.py
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

            # Use detached process on Windows to run independently
            startupinfo = None
            if os.name == 'nt':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = 0  # SW_HIDE

            # Run with detached process
            subprocess.Popen([sys.executable, stockage_main, "--once"],
                             startupinfo=startupinfo,
                             creationflags=subprocess.CREATE_NO_WINDOW)

            # Wait a bit for data collection
            time.sleep(5)

            # Run collector to generate graphs
            collector_path = os.path.join(project_root, "collector.py")
            subprocess.Popen([sys.executable, collector_path],
                             startupinfo=startupinfo,
                             creationflags=subprocess.CREATE_NO_WINDOW)

        except Exception as e:
            print(f"Erreur lors de la mise à jour des données: {e}")

        # Sleep for 5 minutes
        time.sleep(300)


def run_web_server():
    """Démarre le serveur web"""
    os.environ["FLASK_APP"] = "website/app.py"
    os.environ["FLASK_DEBUG"] = "0"  # Disable debug mode for stability

    # Use CREATE_NEW_PROCESS_GROUP flag on Windows to make the process independent
    flags = 0
    if os.name == 'nt':
        flags = subprocess.CREATE_NEW_PROCESS_GROUP

    web_process = subprocess.Popen(
        [sys.executable, "-m", "flask", "run", "--host=0.0.0.0", "--no-reload"],
        creationflags=flags
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
    if os.name != 'nt':  # Unix-like systems
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