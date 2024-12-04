from blockchain.core.validation_service.transaction_validator import TransactionValidator
from blockchain.core.validation_service.validator_manager import ValidatorManager
import logging


class ValidationService:
    """
    Handles validation logic for blocks and transactions in the blockchain.
    """

    def __init__(self):
        self.transaction_validator = TransactionValidator()
        self.validator_manager = ValidatorManager()

    def validate_block(self, block):
        """
        Validates a block's structure and transactions.
        :param block: A dictionary representing the block to validate.
        :return: True if the block is valid, False otherwise.
        """
        if not isinstance(block, dict):
            logging.error("400 Bad Request - Block muss ein Dictionary sein.")
            return False

        required_fields = {"index", "transactions", "previous_hash", "hash", "timestamp", "sender"}
        missing_fields = required_fields - block.keys()
        if missing_fields:
            logging.error(f"400 Bad Request - Fehlende Felder im Block: {missing_fields}")
            return False

        if not self.transaction_validator.validate_transactions(block["transactions"]):
            logging.error("400 Bad Request - Ungültige Transaktionen im Block.")
            return False

        logging.info(f"200 OK - Block {block['index']} erfolgreich validiert.")
        return True

    def validate_transaction(self, transaction):
        """
        Validates a single transaction using TransactionValidator.
        :param transaction: A dictionary representing the transaction.
        :return: True if the transaction is valid, False otherwise.
        """
        if not isinstance(transaction, dict):
            logging.error("400 Bad Request - Transaktion muss ein Dictionary sein.")
            return False

        result = self.transaction_validator.validate_transaction(transaction)
        if not result:
            logging.warning(f"400 Bad Request - Transaktion ungültig: {transaction}")
        else:
            logging.info("200 OK - Transaktion erfolgreich validiert.")

        return result