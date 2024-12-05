# tests/test_transaction_validator.py

import unittest
from chain.core.validation_service.transaction_validator import TransactionValidator

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

    def test_validate_transaction_same_sender_receiver(self):
        transaction = {"sender": "user1", "receiver": "user1", "amount": 50}
        self.assertFalse(self.validator.validate_transaction(transaction))  # Erwartet: False

    def test_validate_transaction_negative_amount(self):
        transaction = {"sender": "user1", "receiver": "user2", "amount": -10}
        self.assertFalse(self.validator.validate_transaction(transaction))  # Erwartet: False

if __name__ == "__main__":
    unittest.main()