import json
import logging

import psycopg2
from psycopg2.extras import DictCursor

from logger_config import render_dynamic_table


class BlockService:
    def __init__(self, db_url):
        """
        Initialisiert die Verbindung zur PostgreSQL-Datenbank.
        :param db_url: URL der Datenbank.
        """
        try:
            self.connection = psycopg2.connect(db_url, cursor_factory=DictCursor)
            self.cursor = self.connection.cursor()
            self._initialize_db()
        except Exception as e:
            logging.error(f"500 Internal Server Error - Fehler bei der Verbindung zur Datenbank: {e}")
            raise

    def _initialize_db(self):
        """
        Initialisiert die Datenbank und erstellt die Tabelle 'blocks', falls nicht vorhanden.
        """
        create_table_query = """
        CREATE TABLE IF NOT EXISTS blocks (
            block_index SERIAL PRIMARY KEY,
            timestamp TIMESTAMP NOT NULL,
            data JSONB NOT NULL,
            previous_hash VARCHAR(64) NOT NULL,
            sender VARCHAR(255),
            thread VARCHAR(255),
            subject VARCHAR(255),
            message TEXT,
            hash VARCHAR(64) NOT NULL
        );
        """
        try:
            self.cursor.execute(create_table_query)
            self.connection.commit()
            logging.info("Datenbank erfolgreich initialisiert.")
        except Exception as e:
            logging.error(f"500 Internal Server Error - Fehler bei der Initialisierung der Datenbank: {e}")
            raise

    def save_block(self, block):
        """
        Speichert einen Block in der Datenbank.
        """
        block_dict = block._to_dict(include_hash=True)
        self.cursor.execute(
            """
            INSERT INTO blocks (timestamp, data, previous_hash, sender, thread, subject, message, hash)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                block_dict["timestamp"],
                json.dumps(block_dict["data"]),
                block_dict["previous_hash"],
                block_dict["sender"],
                block_dict["thread"],
                block_dict["subject"],
                block_dict["message"],
                block_dict["hash"],
            )
        )
        self.connection.commit()
        logging.info(f"Block erfolgreich gespeichert: {block_dict['hash']}")

    def load_chain(self):
        """
        Lädt die gesamte Blockchain aus der PostgreSQL-Datenbank.
        :return: Liste aller Blöcke.
        """
        try:
            self.cursor.execute("SELECT * FROM blocks ORDER BY block_index ASC")
            rows = self.cursor.fetchall()
            data = [
    {
        "block_index": row["block_index"],
        "timestamp": row["timestamp"],
        "data": row["data"],
        "previous_hash": row["previous_hash"],
        "hash": row["hash"],
        "sender": row["sender"],
        "thread": row["thread"],
        "subject": row["subject"],
        "message": row["message"],
    }
    for row in rows
]
            # Dynamische Tabelle rendern
            render_dynamic_table(data)
            return data
        except Exception as e:
            logging.error(f"500 Internal Server Error - Fehler beim Laden der Blockchain: {e}")
            raise


class TokenHandler:
    BASE_COST = 0.25  # Token pro 100 Zeichen
    TRANSACTION_FEE = 0.2  # Fixe Gebühr

    @staticmethod
    def calculate_token_cost(message_length: int) -> float:
        """
        Berechnet die Tokenkosten und garantiert exakte Rundung.
        :param message_length: Anzahl der Zeichen in der Nachricht.
        :return: Gesamtkosten der Transaktion.
        """
        if message_length <= 0:
            return round(TokenHandler.TRANSACTION_FEE, 2)

        # Kostenberechnung
        full_blocks = message_length // 100
        total_cost = (full_blocks * TokenHandler.BASE_COST) + TokenHandler.TRANSACTION_FEE

        # Exakte Rundung auf zwei Dezimalstellen
        return round(total_cost, 2)