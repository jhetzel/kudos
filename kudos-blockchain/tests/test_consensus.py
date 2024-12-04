# tests/test_consensus.py
import unittest
from typing import Dict
from blockchain.consensus.proof_of_kudos import ProofOfKudos

class TestProofOfKudos(unittest.TestCase):
    def setUp(self):
        self.pok = ProofOfKudos()

    def test_register_validator(self):
        self.pok.register_validator("validator1")
        self.assertIn("validator1", self.pok.validators)

    def test_select_validator(self):
        self.pok.register_validator("validator1")
        self.pok.register_validator("validator2")
        kudos_scores = {"validator1": 10, "validator2": 20}
        selected = self.pok.select_validator(kudos_scores)
        self.assertEqual(selected, "validator2")

    def test_validate_block(self):
        valid_block = {
            "transactions": [{"amount": 10, "sender": "user1", "receiver": "user2"}],
            "timestamp": "2024-12-04T01:00:00",
            "previous_hash": "abc123",
            "hash": "def456",
        }
        self.assertTrue(self.pok.validate_block(valid_block))

if __name__ == "__main__":
    unittest.main()