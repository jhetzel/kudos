import sys
from pathlib import Path

# Projektverzeichnis zum PYTHONPATH hinzufügen
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))

import hashlib
import json
import logging
import time
from datetime import datetime
from blockchain.core.block_service import BlockService
from blockchain.core.block_validation_service import ValidationService


class Block:
    def __init__(self, index, timestamp, data, previous_hash, sender, thread, subject, message):
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
        self.hash = self.calculate_hash()
        self._frozen_state = self._to_dict()

    def _to_dict(self, include_hash=False):
        """
        Converts the block to a dictionary format, excluding the hash if specified.
        """
        block_dict = {key: value for key, value in self.__dict__.items() if not key.startswith("_")}
        if not include_hash:
            block_dict.pop("hash", None)
        if isinstance(block_dict["timestamp"], datetime):
            block_dict["timestamp"] = block_dict["timestamp"].isoformat()
        return block_dict

    def calculate_hash(self):
        """
        Calculates the hash of the block based on its content.
        """
        block_string = json.dumps(self._to_dict(include_hash=False), sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()

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
        self.validation_service = ValidationService()
        self.mempool = []

        if not self.chain:
            genesis_block = self.create_genesis_block()
            self.chain.append(genesis_block)
            self.block_service.save_block(genesis_block)

    def _load_chain_from_db(self):
        """
        Loads the blockchain from the database.
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
        Creates the genesis block for the blockchain.
        """
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

    def add_block(self, data, sender, thread, subject, message):
        """
        Adds a new block to the blockchain after validation.
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
        upvotes = votes.count(True)
        downvotes = votes.count(False)
        total_votes = upvotes + downvotes

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