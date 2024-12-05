import hashlib
import json
import logging
import time
from datetime import datetime
from kudos_blockchain.chain.core.block_service import BlockService
from kudos_blockchain.chain.core.block_validation_service import ValidationService


class Block:
    def __init__(self, index, timestamp, data, previous_hash, sender, thread, subject, message, transactions=None):
        self.index = index
        self.timestamp = (
            datetime.fromtimestamp(timestamp) if isinstance(timestamp, (int, float)) else timestamp
        )
        self.data = data
        self.previous_hash = previous_hash
        self.sender = sender
        self.thread = thread
        self.subject = subject
        self.message = message
        self.transactions = transactions or []
        self.hash = self.calculate_hash()
        self._frozen_state = self._to_dict()

    def _to_dict(self, include_hash=False):
        """
        Converts the block to a dictionary format, excluding the hash if specified.
        """
        block_dict = {
            "index": self.index,
            "timestamp": self.timestamp.isoformat() if isinstance(self.timestamp, datetime) else self.timestamp,
            "data": self.data,
            "transactions": self.data,  # Sicherstellen, dass `transactions` explizit enthalten sind
            "previous_hash": self.previous_hash,
            "sender": self.sender,
            "thread": self.thread,
            "subject": self.subject,
            "message": self.message
        }
        if include_hash:
            block_dict["hash"] = self.hash

        logging.debug(f"Block-Daten im _to_dict: {block_dict}")
        return block_dict

    def calculate_hash(self):
        """
        Calculates the hash of the block based on its content.
        """
        block_data = self._to_dict(include_hash=False)
        logging.debug(f"Blockdaten vor der Serialisierung: {block_data}")

        block_string = json.dumps(block_data, sort_keys=True)
        logging.debug(f"Blockdaten nach der Serialisierung (JSON): {block_string}")

        calculated_hash = hashlib.sha256(block_string.encode()).hexdigest()
        logging.debug(f"Berechneter Hash: {calculated_hash}")

        return calculated_hash

    def is_unchanged(self):
        """
        Checks if the block's state has been modified since creation.
        """
        return self._to_dict() == self._frozen_state


class Blockchain:
    def __init__(self, block_service_or_db_url):
        self.block_service = (
            block_service_or_db_url
            if isinstance(block_service_or_db_url, BlockService)
            else BlockService(block_service_or_db_url)
        )
        self.chain = self._load_chain_from_db()
        self.validation_service = ValidationService(self)
        self.mempool = []

        if not self.chain:
            genesis_block = self.create_genesis_block()
            self.chain.append(genesis_block)
            self.block_service.save_block(genesis_block)

    def _load_chain_from_db(self):
        """
        Loads the chain from the database.
        """
        chain = self.block_service.load_chain()
        if not chain:
            return []
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

    def create_genesis_block(self):
        """
        Erstellt den Genesis-Block.
        """
        genesis_data = {
            "index": 0,
            "timestamp": datetime.now().isoformat(),
            "data": "Genesis Block",
            "previous_hash": "0" * 64,
            "sender": "system",
            "thread": "genesis",
            "subject": "Initial Block",
            "message": "This is the genesis block.",
        }
        genesis_block = Block(**genesis_data)
        genesis_block.hash = genesis_block.calculate_hash()
        return genesis_block

    def add_block(self, data, sender, thread, subject, message):
        """
        Adds a new block to the chain after validation.
        """
        valid_transactions = self.validate_transactions(data)
        if not valid_transactions:
            logging.warning("400 Bad Request - Keine gültigen Transaktionen gefunden.")
            return None

        last_block = self.get_last_block()
        new_block = Block(
            index=len(self.chain),
            timestamp=time.time(),
            data=valid_transactions,
            previous_hash=last_block.hash,
            sender=sender,
            thread=thread,
            subject=subject,
            message=message,
        )

        if not self.is_block_valid(new_block):
            logging.error("500 Internal Server Error - Neuer Block ist ungültig.")
            return None

        self.chain.append(new_block)
        self.block_service.save_block(new_block)
        logging.info(f"201 Created - Block {new_block.index} erfolgreich hinzugefügt.")
        return new_block

    def get_last_block(self):
        """
        Retrieves the last block in the chain.
        """
        return self.chain[-1]

    def get_latest_block_index(self):
        """
        Retrieves the index of the latest block in the chain.
        :return: The index of the latest block, or -1 if the chain is empty.
        """
        if not self.chain:
            return -1  # Keine Blöcke in der Blockchain
        return self.chain[-1].index

    def get_latest_block_hash(self):
        """
        Retrieves the hash of the latest block in the chain.
        :return: The hash of the latest block, or None if the chain is empty.
        """
        if not self.chain:
            return None  # Keine Blöcke in der Blockchain
        return self.chain[-1].hash

    def submit_block_for_validation(self, data, sender, thread, subject, message):
        """
        Submits a block for validation and consensus voting.
        """
        last_block = self.get_last_block()
        new_block = Block(
            index=len(self.chain),
            timestamp=time.time(),
            data=data,
            previous_hash=last_block.hash,
            sender=sender,
            thread=thread,
            subject=subject,
            message=message,
        )
        self.mempool.append(new_block)
        logging.info(f"Block {new_block.index} wurde zur Validierung in den Mempool hinzugefügt.")
        return new_block

    def finalize_block(self, block, votes):
        """
        Finalizes a block based on votes and adds it to the chain if approved.
        """
        upvotes = votes.count(True)
        downvotes = votes.count(False)
        total_votes = upvotes + downvotes
        logging.debug(f"Votes für Block {block.index}: Upvotes={upvotes}, Downvotes={downvotes}")

        if upvotes > downvotes:
            self.chain.append(block)
            self.mempool.remove(block)
            logging.info(
                f"200 OK - Block {block.index} wurde durch Konsens (Upvotes: {upvotes}/{total_votes}) zur Blockchain hinzugefügt."
            )
            self.block_service.save_block(block)
            return True
        else:
            self.mempool.remove(block)
            logging.info(f"403 Forbidden - Block {block.index} durch Konsens abgelehnt.")
            return False

    def is_block_valid(self, block):
        """
        Validates a block's hash and previous hash integrity.
        """
        if not block.is_unchanged() or block.hash != block.calculate_hash():
            logging.error("400 Bad Request - Block wurde modifiziert oder hat einen ungültigen Hash.")
            return False
        if block.previous_hash != self.get_last_block().hash:
            logging.error("400 Bad Request - Block hat einen ungültigen vorherigen Hash.")
            return False
        return True

    def validate_transactions(self, transactions):
        """
        Validates transactions using the ValidationService.
        """
        return [
            tx for tx in transactions if self.validation_service.validate_transaction(tx)
        ]