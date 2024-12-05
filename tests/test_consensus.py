import unittest
from typing import Dict
from chain.core.blockchain import Blockchain, Block
from chain.consensus.proof_of_kudos import ProofOfKudos
import logging


class TestProofOfKudos(unittest.TestCase):
    def setUp(self):
        db_url = "postgresql://kudos_user:kudos_pass@localhost:5432/kudos"
        self.blockchain = Blockchain(db_url)  # In-Memory-DB für Tests
        self.pok = ProofOfKudos(self.blockchain)  # Blockchain übergeben

    def test_register_validator(self):
        """
        Testet die Registrierung eines Validators mit Kudos-Token.
        """
        self.pok.register_validator("validator1", 10)  # 10 Kudos-Token als Beispiel
        self.assertIn("validator1", self.pok.validators)
        self.assertEqual(self.pok.validators["validator1"], 10)

    def test_select_validator(self):
        """
        Testet die Auswahl eines Validators basierend auf Kudos-Token.
        """
        self.pok.register_validator("validator1", 10)
        self.pok.register_validator("validator2", 20)

        # Simulierte Kudos-Scores der Validatoren
        kudos_scores = {"validator1": 10, "validator2": 20}

        # Übergebe die Kudos-Scores an die Methode
        selected = self.pok.select_validator(kudos_scores)
        self.assertEqual(selected, "validator2")  # Validator mit höchstem Kudos wird erwartet

    def test_calculate_hash_consistency(self):
        """
        Testet, ob die Hash-Berechnung konsistent bleibt.
        """
        block = Block(
            index=1,
            timestamp="2024-12-05T10:00:00",
            data=[{"amount": 10, "sender": "user1", "receiver": "user2"}],
            previous_hash="abc123",
            sender="system",
            thread="Test Thread",
            subject="Test Subject",
            message="Test Message"
        )

        first_hash = block.calculate_hash()
        second_hash = block.calculate_hash()

        self.assertEqual(first_hash, second_hash, "Die Hash-Berechnung sollte konsistent bleiben.")
        logging.info(f"Hash 1: {first_hash}, Hash 2: {second_hash}")

    def test_validate_block(self):
        """
        Testet die Blockvalidierung durch den Proof-of-Kudos-Mechanismus.
        """
        valid_block = Block(
            index=1,
            timestamp="2024-12-05T10:00:00",
            data=[{"amount": 10, "sender": "user1", "receiver": "user2"}],  # Transaktionen
            previous_hash="abc123",
            sender="system",
            thread="Test Thread",
            subject="Test Subject",
            message="Test Message"
        )

        serialized_block = valid_block._to_dict(include_hash=True)
        logging.debug(f"Serialisierter Block: {serialized_block}")

        self.assertTrue(self.pok.validate_block(serialized_block))  # Erwartet: True

    def test_conduct_vote(self):
        """
        Testet die Abstimmungslogik basierend auf Gewichtungen der Kudos.
        """
        # Registriere Validatoren
        self.pok.register_validator("validator1", 10)
        self.pok.register_validator("validator2", 20)
        self.pok.register_validator("validator3", 15)

        # Simuliere Stimmen
        block_hash = "abc123"
        self.pok.cast_vote("validator1", block_hash, "yes")
        self.pok.cast_vote("validator2", block_hash, "no")
        self.pok.cast_vote("validator3", block_hash, "yes")

        # Führt die Abstimmung aus und überprüft das Ergebnis
        result = self.pok.conduct_vote(block_hash)
        self.assertEqual(result, "accepted")  # Stimmenmehrheit für "yes"

        # Ändere eine Stimme, um "no" zur Mehrheit zu machen
        self.pok.cast_vote("validator2", block_hash, "yes")  # Stimmen für "yes" erhöhen
        result = self.pok.conduct_vote(block_hash)
        self.assertEqual(result, "accepted")  # Mehrheit bleibt für "yes"

if __name__ == "__main__":
    unittest.main()