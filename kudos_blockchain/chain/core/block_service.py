import sqlite3
import psycopg2
from psycopg2.extras import DictCursor
from datetime import datetime
import logging
import json


class BlockService:
    def __init__(self, db_url):
        if "sqlite" in db_url:
            # SQLite-Setup
            self.connection = sqlite3.connect(":memory:")  # Für Tests
            self.cursor = self.connection.cursor()
            self._initialize_db()
        else:
            # PostgreSQL-Setup
            self.connection = psycopg2.connect(db_url, cursor_factory=DictCursor)
            self.cursor = self.connection.cursor()

    def _initialize_db(self):
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
        block_dict = block._to_dict(include_hash=True)  # Sicherstellen, dass der Hash enthalten ist
        self.cursor.execute(
            """
            INSERT INTO blocks (block_index, timestamp, data, previous_hash, sender, thread, subject, message, hash)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                block_dict["index"],
                block_dict["timestamp"],
                block_dict["data"],
                block_dict["previous_hash"],
                block_dict["sender"],
                block_dict["thread"],
                block_dict["subject"],
                block_dict["message"],
                block_dict["hash"]
            )
        )
        self.connection.commit()
        logging.info(f"Block {block_dict['index']} erfolgreich gespeichert.")

    def load_chain(self):
        """
        Loads the entire chain from the database.
        """
        self.cursor.execute("SELECT * FROM blocks ORDER BY block_index ASC")
        rows = self.cursor.fetchall()
        return [
            {
                "block_index": row[1],
                "timestamp": datetime.fromisoformat(row[2]) if row[2] else None,
                "data": json.loads(row[3]) if row[3] else [],
                "previous_hash": row[4],
                "hash": row[5],
                "sender": row[6],
                "thread": row[7],
                "subject": row[8],
                "message": row[9],
            }
            for row in rows
        ]


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