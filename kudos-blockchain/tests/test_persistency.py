from blockchain.core.blockchain import Blockchain
import os
import logging

def get_db_url():
    is_docker = os.path.exists('/.dockerenv')
    host = "kudos-db" if is_docker else "localhost"
    return f"postgresql://kudos_user:kudos_pass@{host}:5432/kudos"

# Globale Logging-Konfiguration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),  # Logs werden an die Standardausgabe weitergeleitet
    ],
)

DB_URL = get_db_url()

def test_persistence():
    try:
        # Initialisiere die Blockchain
        logging.info("200 OK - Initialisiere Blockchain mit DB_URL.")
        blockchain = Blockchain(DB_URL)

        # Füge einen neuen Block hinzu
        try:
            new_block = blockchain.add_block(
                data="Test block",
                sender="test_sender_hash",
                thread="test_thread",
                subject="Test Subject",
                message="This is a test message.",
            )
            logging.info(
                f"201 Created - Block hinzugefügt: Index={new_block.index}, Hash={new_block.hash}"
            )
        except Exception as e:
            logging.error(f"500 Internal Server Error - Fehler beim Hinzufügen eines Blocks: {e}")
            raise

        # Prüfe die gesamte Blockchain
        try:
            all_blocks = blockchain.block_service.load_chain()
            logging.info(f"200 OK - Gesamte Blockchain aus der Datenbank geladen: {len(all_blocks)} Blöcke.")
            for block in all_blocks:
                logging.debug(f"Block: {block}")
        except Exception as e:
            logging.error(f"500 Internal Server Error - Fehler beim Laden der Blockchain: {e}")
            raise

    except Exception as e:
        logging.error(f"500 Internal Server Error - Test fehlgeschlagen: {e}")
        raise

if __name__ == "__main__":
    test_persistence()