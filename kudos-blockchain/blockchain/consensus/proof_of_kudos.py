from typing import List, Dict


class ProofOfKudos:
    """
    Implements the Proof-of-Kudos (PoK) consensus mechanism.
    """

    def __init__(self):
        self.validators = set()

    def register_validator(self, validator_id: str):
        """
        Registers a new validator for PoK.
        :param validator_id: Unique ID of the validator.
        """
        if not isinstance(validator_id, str) or not validator_id.strip():
            raise ValueError("Validator ID must be a non-empty string.")
        self.validators.add(validator_id)

    def select_validator(self, kudos_scores: Dict[str, int]) -> str:
        """
        Selects a validator based on their Kudos score.
        :param kudos_scores: A dictionary mapping validator IDs to Kudos scores.
        :return: Selected validator ID.
        """
        if not isinstance(kudos_scores, dict) or not kudos_scores:
            raise ValueError("Kudos scores must be a non-empty dictionary.")

        valid_scores = {v: kudos_scores[v] for v in self.validators if v in kudos_scores}
        if not valid_scores:
            raise ValueError("No eligible validators with Kudos scores.")

        return max(valid_scores, key=valid_scores.get)

    def validate_block(self, block_data: Dict) -> bool:
        """
        Validates a block using PoK logic.
        :param block_data: The block to be validated.
        :return: True if the block is valid, False otherwise.
        """
        if not isinstance(block_data, dict):
            raise ValueError("Block data must be a dictionary.")

        required_fields = {"transactions", "timestamp", "previous_hash", "hash"}
        if not required_fields.issubset(block_data.keys()):
            return False

        transactions = block_data.get("transactions")
        return isinstance(transactions, list) and len(transactions) > 0