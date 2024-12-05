import logging

class TransactionValidator:
    """
    Validates transactions for the Kudos chain.
    """

    def validate_transaction(self, transaction):
        """
        Validates a single transaction.
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

        logging.info("200 OK - Transaktion erfolgreich validiert.")
        return True

    def validate_transactions(self, transactions):
        """
        Validates a list of transactions.
        :param transactions: A list of transaction dictionaries.
        :return: True if all transactions are valid, False otherwise.
        """
        if not isinstance(transactions, list):
            return False

        return all(self.validate_transaction(tx) for tx in transactions)