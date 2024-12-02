import time
import logging
from blockchain import Blockchain
import os

def get_db_url():
    is_docker = os.path.exists('/.dockerenv')
    host = "kudos-db" if is_docker else "localhost"
    return f"postgresql://kudos_user:kudos_pass@{host}:5432/kudos"

DB_URL = get_db_url()

# Logging konfigurieren
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler()  # Ausgabe in Docker-Logs
    ]
)

def log_service_status():
    """Loggt regelmäßig eine Statusmeldung mit HTTP-Statuscode."""
    logging.info("200 OK - Blockchain-Service läuft.")

def main():
    blockchain = Blockchain(DB_URL)
    logging.info("200 OK - Blockchain-Service gestartet und mit Datenbank verbunden.")

    try:
        while True:
            log_service_status()
            time.sleep(10)  # Alle 10 Sekunden Statusmeldung
    except KeyboardInterrupt:
        logging.error("503 Service Unavailable - Blockchain-Service wird beendet.")

if __name__ == "__main__":
    main()