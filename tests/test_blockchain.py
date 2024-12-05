import unittest
from unittest.mock import patch
from datetime import datetime
from chain.core.blockchain import Blockchain
from chain.core.blockchain import Block

class TestBlockchain(unittest.TestCase):
    def setUp(self):
        db_url = "postgresql://kudos_user:kudos_pass@localhost:5432/kudos"
        self.blockchain = Blockchain(db_url)

        # Sicherstellen, dass der Genesis-Block korrekt erstellt und gespeichert wird
        if not self.blockchain.chain:
            genesis_block = self.blockchain.create_genesis_block()
            self.blockchain.chain.append(genesis_block)
            self.blockchain.block_service.save_block(genesis_block)

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

    @patch('logging.info')
    def test_finalize_block_with_pok_votes(self, mock_logging_info):
        # Simuliere Votes
        votes = [True] * 9 + [False] * 3
        block = Block(6, datetime.now(), "data", "prev_hash", "sender", "thread", "subject", "message")
        self.blockchain.mempool.append(block)

        result = self.blockchain.finalize_block(block, votes)

        # Prüfen, ob der Block erfolgreich hinzugefügt wurde
        self.assertTrue(result)

        # Prüfen, ob die Konsens-Nachricht korrekt geloggt wurde
        mock_logging_info.assert_any_call(
            '200 OK - Block 6 wurde durch Konsens (Upvotes: 9/12) zur Blockchain hinzugefügt.')

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