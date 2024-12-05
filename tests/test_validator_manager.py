# tests/test_validator_manager.py

import unittest
from chain.core.validation_service.validator_manager import ValidatorManager

class TestValidatorManager(unittest.TestCase):
    def setUp(self):
        self.manager = ValidatorManager()

    def test_register_validator(self):
        self.manager.register_validator("validator_1")
        self.assertIn("validator_1", self.manager.validators)

    def test_is_validator(self):
        self.manager.register_validator("validator_2")
        self.assertTrue(self.manager.is_validator("validator_2"))
        self.assertFalse(self.manager.is_validator("validator_3"))

if __name__ == "__main__":
    unittest.main()