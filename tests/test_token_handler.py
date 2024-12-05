import unittest
from chain.core.block_service import TokenHandler

class TestTokenHandler(unittest.TestCase):
    def test_calculate_token_cost(self):
        """
        Testet die Berechnung der Tokenkosten.
        """
        self.assertEqual(TokenHandler.calculate_token_cost(0), 0.2)  # Nur Transaktionsgebühr
        self.assertEqual(TokenHandler.calculate_token_cost(50), 0.2)  # Unter 100 Zeichen
        self.assertEqual(TokenHandler.calculate_token_cost(100), 0.45)  # 100 Zeichen
        self.assertEqual(TokenHandler.calculate_token_cost(250), 0.7)  # Erwartetes Ergebnis: 0.7
        self.assertEqual(TokenHandler.calculate_token_cost(1000), 2.7)  # Erwartetes Ergebnis: 2.7

if __name__ == "__main__":
    unittest.main()