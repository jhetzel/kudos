class TransactionValidator:
    """
    Validates transactions for the Kudos blockchain.
    """

    def validate_transaction(self, transaction):
        """
        Validates a single transaction.
        :param transaction: A dictionary representing a transaction.
        :return: True if the transaction is valid, False otherwise.
        """
        if not isinstance(transaction, dict):
            return False

        required_fields = {"amount", "sender", "receiver"}
        if not required_fields.issubset(transaction.keys()):
            return False

        amount = transaction.get("amount", 0)
        return isinstance(amount, (int, float)) and amount > 0

    def validate_transactions(self, transactions):
        """
        Validates a list of transactions.
        :param transactions: A list of transaction dictionaries.
        :return: True if all transactions are valid, False otherwise.
        """
        if not isinstance(transactions, list):
            return False

        return all(self.validate_transaction(tx) for tx in transactions)