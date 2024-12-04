# tests/test_transaction_validator.py

import unittest
from blockchain.core.validation_service.transaction_validator import TransactionValidator

class TestTransactionValidator(unittest.TestCase):
    def setUp(self):
        self.validator = TransactionValidator()

    def test_validate_transaction(self):
        valid_transaction = {"sender": "Alice", "receiver": "Bob", "amount": 100}
        invalid_transaction = {"sender": "Alice", "receiver": "Bob"}
        self.assertTrue(self.validator.validate_transaction(valid_transaction))
        self.assertFalse(self.validator.validate_transaction(invalid_transaction))

    def test_validate_transactions(self):
        valid_transactions = [
            {"sender": "Alice", "receiver": "Bob", "amount": 100},
            {"sender": "Charlie", "receiver": "Dave", "amount": 50}
        ]
        invalid_transactions = [
            {"sender": "Alice", "receiver": "Bob", "amount": 100},
            {"sender": "Charlie", "receiver": "Dave"}
        ]
        self.assertTrue(self.validator.validate_transactions(valid_transactions))
        self.assertFalse(self.validator.validate_transactions(invalid_transactions))

if __name__ == "__main__":
    unittest.main()