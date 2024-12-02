import psycopg2
from psycopg2.extras import DictCursor
from datetime import datetime
import time
import logging


class BlockService:
    def __init__(self, db_url):
        self.db_url = db_url
        logging.info(f"200 OK - Verwende DB_URL: {self.db_url}")
        self._create_table()

    def _create_table(self):
        retries = 5
        while retries > 0:
            try:
                with psycopg2.connect(self.db_url) as conn:
                    with conn.cursor() as cursor:
                        cursor.execute("""
                        CREATE TABLE IF NOT EXISTS blockchain (
                            id SERIAL PRIMARY KEY,
                            index INTEGER NOT NULL,
                            timestamp TIMESTAMP NOT NULL,
                            data TEXT NOT NULL,
                            previous_hash TEXT NOT NULL,
                            hash TEXT NOT NULL,
                            sender TEXT NOT NULL,
                            thread TEXT NOT NULL,
                            subject TEXT NOT NULL,
                            message TEXT NOT NULL
                        );
                        """)
                        conn.commit()
                        logging.info("200 OK - Tabelle 'blockchain' erfolgreich erstellt oder bereits vorhanden.")
                        return
            except psycopg2.OperationalError as e:
                retries -= 1
                logging.warning(
                    f"503 Service Unavailable - Datenbankverbindung fehlgeschlagen: {e}. "
                    f"Erneuter Versuch in 5 Sekunden... ({retries} verbleibend)"
                )
                time.sleep(5)
        logging.error("500 Internal Server Error - Datenbank konnte nach mehreren Versuchen nicht erreicht werden.")
        raise Exception("Datenbank konnte nach mehreren Versuchen nicht erreicht werden.")

    def save_block(self, block):
        query = """
        INSERT INTO blockchain (index, timestamp, data, previous_hash, hash, sender, thread, subject, message)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        try:
            with psycopg2.connect(self.db_url) as conn:
                with conn.cursor() as cursor:
                    logging.info(f"DEBUG: Speichere Block {block.index} in der Datenbank...")
                    timestamp = (
                        block.timestamp
                        if isinstance(block.timestamp, datetime)
                        else datetime.fromtimestamp(block.timestamp)
                    )
                    cursor.execute(
                        query,
                        (
                            block.index,
                            timestamp,
                            block.data,
                            block.previous_hash,
                            block.hash,
                            block.sender,
                            block.thread,
                            block.subject,
                            block.message,
                        ),
                    )
                    conn.commit()
                    logging.info(f"201 Created - Block {block.index} erfolgreich in der Datenbank gespeichert.")
        except psycopg2.Error as e:
            logging.error(f"500 Internal Server Error - Fehler beim Speichern des Blocks {block.index}: {e}")
            raise

    def load_chain(self):
        """Lädt die gesamte Blockchain aus der Datenbank."""
        query = "SELECT * FROM blockchain ORDER BY index ASC"
        try:
            with psycopg2.connect(self.db_url, cursor_factory=DictCursor) as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query)
                    chain = cursor.fetchall()
                    logging.info(f"200 OK - Blockchain mit {len(chain)} Blöcken erfolgreich geladen.")
                    return chain
        except psycopg2.Error as e:
            logging.error(f"500 Internal Server Error - Fehler beim Laden der Blockchain: {e}")
            raise