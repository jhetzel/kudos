class ValidatorManager:
    """
    Manages validators in the Kudos chain network.
    """

    def __init__(self):
        self.validators = set()

    def register_validator(self, validator_id):
        """
        Adds a validator to the set of registered validators.
        :param validator_id: The unique ID of the validator.
        """
        if not isinstance(validator_id, str) or not validator_id.strip():
            raise ValueError("Validator ID must be a non-empty string.")
        self.validators.add(validator_id)

    def is_validator(self, validator_id):
        """
        Checks if a given ID is a registered validator.
        :param validator_id: The unique ID of the validator.
        :return: True if the ID is registered, False otherwise.
        """
        return validator_id in self.validators

    def get_all_validators(self):
        """
        Retrieves a list of all registered validators.
        :return: A list of all validator IDs.
        """
        return list(self.validators)