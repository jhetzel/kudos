import time
import logging
import os
from chain.core.blockchain import Blockchain
from logger_config import setup_logging
setup_logging()

def get_db_url():
    """
    Ermittelt die Datenbank-URL basierend auf der Umgebung.
    """
    is_docker = os.path.exists('/.dockerenv')
    host = "kudos-db" if is_docker else "localhost"
    return f"postgresql://kudos_user:kudos_pass@{host}:5432/kudos"


DB_URL = get_db_url()

# Logging-Konfiguration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler()  # Docker-kompatible Logs
    ]
)


def log_service_status(blockchain):
    """
    Loggt regelmäßig den Status des Services und der Blockchain.
    """
    try:
        all_blocks = blockchain.block_service.load_chain()
        block_count = len(all_blocks)
        logging.info(f"200 OK - Blockchain-Service läuft. Anzahl der Blöcke: {block_count}")
    except Exception as e:
        logging.error(f"500 Internal Server Error - Fehler beim Abrufen des Blockchain-Status: {e}")


def log_block_count(blockchain):
    """
    Loggt die Anzahl der Blöcke in der Blockchain.

    :param blockchain: Die Blockchain-Instanz, die die Kette enthält.
    """
    block_count = len(blockchain.chain)
    logging.info(f"200 OK - Die Blockchain enthält aktuell {block_count} Blöcke.")

def main():
    """
    Startet den Blockchain-Service.
    """
    try:
        # Initialisiere die Blockchain
        logging.info(f"200 OK - Initialisiere Blockchain mit DB_URL: {DB_URL}")
        blockchain = Blockchain(DB_URL)
        logging.info("200 OK - Blockchain-Service gestartet und mit der Datenbank verbunden.")
    except Exception as e:
        logging.error(f"500 Internal Server Error - Fehler beim Starten des Blockchain-Services: {e}")
        return  # Beende das Skript bei einem Fehler

    try:
        while True:
            log_block_count(blockchain)
            time.sleep(10)  # Statusmeldung alle 10 Sekunden
    except KeyboardInterrupt:
        logging.warning("503 Service Unavailable - Blockchain-Service wurde manuell beendet.")
    except Exception as e:
        logging.error(f"500 Internal Server Error - Unerwarteter Fehler: {e}")
    finally:
        logging.info("200 OK - Blockchain-Service sauber beendet.")


if __name__ == "__main__":
    main()