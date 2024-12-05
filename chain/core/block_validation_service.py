import logging
import hashlib
from chain.core.validation_service.transaction_validator import TransactionValidator


class ValidationService:
    """
    Handles validation logic for blocks and transactions in the chain.
    """

    def __init__(self, blockchain):
        """
        Initialisiert den ValidationService mit einer Blockchain-Referenz.
        :param blockchain: Die Blockchain, die validiert werden soll.
        """
        self.blockchain = blockchain
        self.transaction_validator = TransactionValidator()

    def validate_block(self, block):
        """
        Validates a block's structure and transactions.
        :param block: A dictionary representing the block to validate.
        :return: True if the block is valid, False otherwise.
        """
        required_fields = {"index", "transactions", "previous_hash", "hash", "timestamp", "sender"}
        missing_fields = required_fields - block.keys()

        if missing_fields:
            logging.error(f"400 Bad Request - Fehlende Felder im Block: {missing_fields}")
            return False

        logging.debug(f"Validierter Block: {block}")
        return True  # Temporär, um spezifische Validierungsprobleme zu isolieren

    def _validate_block_hash(self, block):
        """
        Validates the hash integrity of a block.
        :param block: The block to validate.
        :return: True if the block's hash is correct, False otherwise.
        """
        block_copy = block.copy()
        block_hash = block_copy.pop("hash", None)
        calculated_hash = self._calculate_hash(block_copy)
        logging.debug(f"Blockdaten zur Validierung: {block_copy}")
        logging.debug(f"Erwarteter Hash: {block_hash}")
        logging.debug(f"Berechneter Hash: {calculated_hash}")
        if block_hash != calculated_hash:
            logging.error(f"Hash-Abweichung: Erwartet {calculated_hash}, erhalten {block_hash}")
            return False
        return True

    @staticmethod
    def _calculate_hash(block_data):
        """
        Calculates the hash of the given block data.
        :param block_data: A dictionary containing block data without the hash field.
        :return: A string representing the SHA256 hash of the block data.
        """
        block_string = str(sorted(block_data.items())).encode()
        return hashlib.sha256(block_string).hexdigest()

    def validate_transaction(self, transaction):
        """
        Validates a single transaction using TransactionValidator.
        :param transaction: A dictionary representing the transaction.
        :return: True if the transaction is valid, False otherwise.
        """
        if not isinstance(transaction, dict):
            logging.error("400 Bad Request - Transaktion muss ein Dictionary sein.")
            return False

        required_fields = {"sender", "receiver", "amount"}
        if not all(field in transaction for field in required_fields):
            logging.error(f"400 Bad Request - Fehlende Felder in der Transaktion: {transaction}")
            return False

        if transaction["sender"] == transaction["receiver"]:
            logging.error(f"400 Bad Request - Sender und Empfänger dürfen nicht identisch sein: {transaction}")
            return False

        if not isinstance(transaction["amount"], (int, float)) or transaction["amount"] <= 0:
            logging.error(f"400 Bad Request - Ungültiger Betrag in der Transaktion: {transaction}")
            return False

        result = self.transaction_validator.validate_transaction(transaction)
        if not result:
            logging.warning(f"400 Bad Request - Transaktion ungültig: {transaction}")
        else:
            logging.info("200 OK - Transaktion erfolgreich validiert.")

        return result