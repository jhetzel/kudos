class ValidationService:
    """Service zur Validierung der Blockchain."""
    @staticmethod
    def is_chain_valid(chain):
        for i in range(1, len(chain)):
            current = chain[i]
            previous = chain[i - 1]
            if current.previous_hash != previous.hash:
                return False
            if current.hash != current.calculate_hash():
                return False
        return True