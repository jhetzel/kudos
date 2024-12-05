from typing import List, Dict
import logging
from kudos_blockchain.chain.core.block_validation_service import ValidationService

class ProofOfKudos:
    def __init__(self, blockchain):
        self.votes = {}  # Speichert Stimmen pro Block
        self.validators = {}  # Validatoren mit deren Kudos-Token
        self.block_validator = ValidationService(blockchain)  # Blockchain übergeben

    def register_validator(self, validator_id, kudos_tokens):
        self.validators[validator_id] = kudos_tokens

    def cast_vote(self, validator_id, block_hash, vote):
        if validator_id not in self.validators:
            raise ValueError("Validator ist nicht registriert.")
        if block_hash not in self.votes:
            self.votes[block_hash] = {"yes": 0, "no": 0}
        weight = self.validators[validator_id]
        if vote == "yes":
            self.votes[block_hash]["yes"] += weight
        elif vote == "no":
            self.votes[block_hash]["no"] += weight
        else:
            raise ValueError("Ungültige Stimme. Nur 'yes' oder 'no' erlaubt.")

    def finalize_vote(self, block_hash):
        if block_hash not in self.votes:
            raise ValueError("Block nicht im Abstimmungsprozess.")
        result = self.votes[block_hash]
        return "accepted" if result["yes"] > result["no"] else "rejected"

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
        Delegates block validation to the ValidationService.
        """
        return self.block_validator.validate_block(block_data)

    def conduct_vote(self, block_hash: str) -> str:
        """
        Führt eine Abstimmung für einen Block durch und entscheidet, ob er akzeptiert oder abgelehnt wird.
        :param block_hash: Der Hash des Blocks, der abgestimmt wird.
        :return: "accepted" oder "rejected", basierend auf der Stimmenmehrheit.
        """
        if block_hash not in self.votes:
            raise ValueError("Keine Stimmen für diesen Block vorhanden.")

        vote_result = self.votes[block_hash]
        yes_weight = vote_result["yes"]
        no_weight = vote_result["no"]

        if yes_weight > no_weight:
            return "accepted"
        return "rejected"