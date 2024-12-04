import psycopg2
from psycopg2.extras import DictCursor
from datetime import datetime
import logging
import json


class BlockService:
    def __init__(self, db_url):
        """
        Initialisiert den BlockService mit einer Datenbankverbindung.
        :param db_url: Die URL zur Datenbankverbindung
        """
        try:
            self.connection = psycopg2.connect(db_url, cursor_factory=DictCursor)
            self._initialize_database()
            logging.info("200 OK - Datenbankverbindung erfolgreich hergestellt.")
        except psycopg2.OperationalError as e:
            logging.error(f"500 Internal Server Error - Fehler beim Herstellen der DB-Verbindung: {e}")
            raise
        except Exception as e:
            logging.error(f"500 Internal Server Error - Unerwarteter Fehler: {e}")
            raise

    def _initialize_database(self):
        """
        Erstellt die notwendige Tabelle, falls sie nicht existiert.
        """
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS blockchain (
                        index SERIAL PRIMARY KEY,
                        timestamp TIMESTAMPTZ NOT NULL,
                        data JSONB NOT NULL,
                        previous_hash TEXT NOT NULL,
                        sender TEXT NOT NULL,
                        thread TEXT NOT NULL,
                        subject TEXT NOT NULL,
                        message TEXT NOT NULL,
                        hash TEXT NOT NULL
                    )
                """)
                self.connection.commit()
                logging.info("200 OK - Tabelle 'blockchain' erfolgreich erstellt oder bereits vorhanden.")
        except Exception as e:
            logging.error(f"500 Internal Server Error - Fehler beim Initialisieren der Tabelle: {e}")
            raise

    def save_block(self, block):
        """
        Speichert einen Block in der Datenbank.
        """
        try:
            with self.connection.cursor() as cursor:
                data_json = json.dumps(block.data)
                cursor.execute(
                    """
                    INSERT INTO blockchain (index, timestamp, data, previous_hash, sender, thread, subject, message, hash)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        block.index,
                        block.timestamp.isoformat(),
                        data_json,
                        block.previous_hash,
                        block.sender,
                        block.thread,
                        block.subject,
                        block.message,
                        block.hash,
                    ),
                )
                self.connection.commit()
                logging.info(f"201 Created - Block {block.index} erfolgreich in der Datenbank gespeichert.")
        except psycopg2.DatabaseError as e:
            logging.error(f"500 Internal Server Error - Fehler beim Speichern des Blocks {block.index}: {e}")
            self.connection.rollback()
            raise
        except Exception as e:
            logging.error(f"500 Internal Server Error - Unerwarteter Fehler: {e}")
            raise

    def load_chain(self):
        """
        Lädt die gesamte Blockchain aus der Datenbank.
        """
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("SELECT * FROM blockchain ORDER BY index ASC")
                rows = cursor.fetchall()

                chain = []
                for row in rows:
                    chain.append({
                        "index": row["index"],
                        "timestamp": datetime.fromisoformat(row["timestamp"])
                        if isinstance(row["timestamp"], str) else row["timestamp"],
                        "data": row["data"],
                        "previous_hash": row["previous_hash"],
                        "sender": row["sender"],
                        "thread": row["thread"],
                        "subject": row["subject"],
                        "message": row["message"],
                        "hash": row["hash"],
                    })

                logging.info(f"200 OK - Blockchain mit {len(chain)} Blöcken geladen.")
                return chain
        except psycopg2.DatabaseError as e:
            logging.error(f"500 Internal Server Error - Fehler beim Laden der Blockchain: {e}")
            raise
        except Exception as e:
            logging.error(f"500 Internal Server Error - Unerwarteter Fehler: {e}")
            raise