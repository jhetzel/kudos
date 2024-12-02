import hashlib
import json
import time
from datetime import datetime
from .block_service import BlockService
import logging






class Block:
    def __init__(self, index, timestamp, data, previous_hash, sender, thread, subject, message):
        self.index = index
        # Konvertiere Unix-Timestamp in datetime, falls nötig
        self.timestamp = (
            datetime.fromtimestamp(timestamp)
            if isinstance(timestamp, (int, float))
            else timestamp
        )
        self.data = data
        self.previous_hash = previous_hash
        self.hash = self.calculate_hash()
        self.sender = sender
        self.thread = thread
        self.subject = subject
        self.message = message

    def calculate_hash(self):
        # Serialisierbare Version der Block-Daten erstellen
        block_dict = self.__dict__.copy()
        if isinstance(block_dict["timestamp"], datetime):
            # Konvertiere datetime zu einem ISO 8601-String
            block_dict["timestamp"] = block_dict["timestamp"].isoformat()

        # Erstelle den Hash
        block_string = json.dumps(block_dict, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()



class Blockchain:
    def __init__(self, db_url):
        self.block_service = BlockService(db_url)
        self.chain = self._load_chain_from_db()

    def _load_chain_from_db(self):
        """Lädt die Blockchain aus der Datenbank."""
        chain = self.block_service.load_chain()
        if not chain:
            return [self.create_genesis_block()]
        return [
            Block(
                block["index"],
                block["timestamp"],
                block["data"],
                block["previous_hash"],
                block["sender"],
                block["thread"],
                block["subject"],
                block["message"],
            )
            for block in chain
        ]

    def add_block(self, data, sender, thread, subject, message):
        try:
            # Hole den vorherigen Block
            previous_block = self.get_last_block()

            # Erstelle einen neuen Block
            new_block = Block(
                index=len(self.chain),
                timestamp=time.time(),
                data=data,
                previous_hash=previous_block.hash,
                sender=sender,
                thread=thread,
                subject=subject,
                message=message,
            )

            # Füge den Block zur Blockchain hinzu
            self.chain.append(new_block)
            logging.info(
                f"201 Created - Block zur Blockchain hinzugefügt: Index={new_block.index}, Hash={new_block.hash}"
            )

            # Block in der Datenbank speichern
            try:
                self.block_service.save_block(new_block)
                logging.info(
                    f"201 Created - Block {new_block.index} erfolgreich in der Datenbank gespeichert."
                )
            except Exception as e:
                logging.error(
                    f"500 Internal Server Error - Fehler beim Speichern des Blocks {new_block.index}: {e}"
                )
                raise

            # Debug-Log für zusätzlichen Kontext
            logging.debug(
                f"DEBUG: Block {new_block.index} mit Daten: {new_block.data} erfolgreich erstellt."
            )

            return new_block

        except Exception as e:
            # Fehler beim Erstellen oder Hinzufügen des Blocks
            logging.error(f"500 Internal Server Error - Fehler beim Hinzufügen eines Blocks: {e}")
            raise

    def get_last_block(self):
        return self.chain[-1]

    def create_genesis_block(self):
        """Erstellt den Genesis-Block."""
        return Block(
            index=0,
            timestamp=time.time(),
            data="Genesis Block",
            previous_hash="0",
            sender="system",
            thread="none",
            subject="Genesis Block",
            message="This is the genesis block.",
        )