import unittest
from unittest.mock import patch
from blockchain.core.blockchain import Blockchain
from blockchain.core.block_service import BlockService

class MockBlockService(BlockService):
    """Mock für die BlockService-Klasse, um die Datenbank-Interaktionen zu simulieren."""
    def __init__(self):
        self.blocks = []

    def load_chain(self):
        return self.blocks

    def save_block(self, block):
        self.blocks.append(block.__dict__)

class TestBlockchain(unittest.TestCase):
    def setUp(self):
        self.mock_service = MockBlockService()  # Mock für BlockService
        self.blockchain = Blockchain(self.mock_service)

        # Genesis-Block sicherstellen
        if not self.blockchain.chain:
            self.blockchain.chain.append(self.blockchain.create_genesis_block())

    def test_add_block_with_valid_and_invalid_transactions(self):
        """Testet, ob nur gültige Transaktionen in den Block aufgenommen werden."""
        valid_transaction = {"id": "tx1", "amount": 100}
        invalid_transaction = {"id": "tx2", "amount": -20}  # Negativer Betrag ist ungültig

        # Mock ValidationService
        self.blockchain.validation_service.validate_transaction = lambda tx: tx["amount"] > 0

        # Block hinzufügen mit gemischten Transaktionen
        data = [valid_transaction, invalid_transaction]
        block = self.blockchain.add_block(
            data=data,
            sender="Alice",
            thread="Test Thread",
            subject="Test Subject",
            message="Test Message"
        )

        # Überprüfen, dass nur die gültige Transaktion im Block gespeichert ist
        self.assertIsNotNone(block)
        self.assertIn(valid_transaction, block.data)
        self.assertNotIn(invalid_transaction, block.data)

    def test_add_invalid_block(self):
        """Testet, ob ein ungültiger Block abgelehnt wird."""
        invalid_block = self.blockchain.create_genesis_block()
        invalid_block.previous_hash = "tampered_hash"  # Manipulierter vorheriger Hash

        # Prüfen, ob der ungültige Block abgelehnt wird
        self.assertFalse(self.blockchain.is_block_valid(invalid_block))

    def test_finalize_block_with_pok_votes(self):
        block = self.blockchain.submit_block_for_validation(
            data=[{"amount": 10, "sender": "user1", "receiver": "user2"}],
            sender="user1",
            thread="thread1",
            subject="subject1",
            message="message1",
        )

        upvotes = 9
        downvotes = 3
        total_votes = upvotes + downvotes

        with patch("logging.info") as mock_logging_info:
            result = self.blockchain.finalize_block(block, votes=[True] * upvotes + [False] * downvotes)

            self.assertTrue(result)
            mock_logging_info.assert_called_with(
                f"200 OK - Block {block.index} wurde durch Konsens (Upvotes: {upvotes}/{total_votes}) zur Blockchain hinzugefügt."
            )

    def test_finalize_block_with_rejected_votes(self):
        """Testet, ob ein Block bei Ablehnung nicht zur Blockchain hinzugefügt wird."""
        block = self.blockchain.submit_block_for_validation(
            data="Test Data",
            sender="Alice",
            thread="Test Thread",
            subject="Test Subject",
            message="This is a test message."
        )

        # Mehrheit der Validatoren lehnt ab (Proof-of-Kudos)
        upvotes = 2
        downvotes = 5
        votes = [True] * upvotes + [False] * downvotes

        result = self.blockchain.finalize_block(block, votes)

        # Block sollte abgelehnt werden
        self.assertFalse(result)
        self.assertNotIn(block, self.blockchain.chain)
        self.assertNotIn(block, self.blockchain.mempool)

if __name__ == "__main__":
    unittest.main()