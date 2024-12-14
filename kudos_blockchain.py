import hashlib
import time
import random

class Transaktion:
    """
    Repräsentiert eine Transaktion in der Kudos-Blockchain.
    """
    def __init__(self, sender_wallet, empfaenger_wallet, thread, subject, message, amount):
        self.sender_wallet = sender_wallet
        self.empfaenger_wallet = empfaenger_wallet
        self.thread = thread
        self.subject = subject
        self.message = message
        self.amount = amount
        self.timestamp = time.time()
        self.fee = len(message) * 0.001 + 0.1 # Gebühr basierend auf Nachrichtenlänge + feste Gebühr

    def to_dict(self): #für Hashbildung
        return self.__dict__

class Block:
    """
    Repräsentiert einen Block in der Kudos-Blockchain.
    """
    def __init__(self, vorheriger_hash, transaktionen):
        self.timestamp = time.time()
        self.vorheriger_hash = vorheriger_hash
        self.transaktionen = transaktionen
        self.nonce = 0 # für späteres Proof-of-Work
        self.hash = self.berechne_hash()

    def berechne_hash(self):
        """
        Berechnet den Hash des Blocks.
        """
        block_string = str(self.timestamp) + str(self.vorheriger_hash) + str([t.to_dict() for t in self.transaktionen]) + str(self.nonce)
        return hashlib.sha256(block_string.encode()).hexdigest()

class Blockchain:
    """
    Repräsentiert die Kudos-Blockchain.
    """
    def __init__(self):
        self.kette = [self.generiere_genesis_block()]
        self.validatoren = ["Validator1", "Validator2", "Validator3", "Validator4", "Validator5"] #Beispielvalidatoren

    def generiere_genesis_block(self):
        """
        Erstellt den ersten Block (Genesis Block) der Blockchain.
        """
        return Block("0", [])

    def fuege_block_hinzu(self, block):
        """
        Fügt einen neuen Block zur Blockchain hinzu, nachdem die Validierung erfolgreich war.
        """
        block.vorheriger_hash = self.kette[-1].hash
        block.hash = block.berechne_hash()
        self.kette.append(block)

    def validiere_transaktionen(self, transaktionen):
        """
        Validiere Transaktionen mit zufällig ausgewählten Validatoren.
        """

        if not transaktionen:
            return False

        ausgewaehlte_validatoren = random.sample(self.validatoren, 3)
        upvotes = 0
        downvotes = 0

        for validator in ausgewaehlte_validatoren:
            #Hier müsste in echt eine Interaktion mit den Validatoren stattfinden
            #Für Demo simuliert mit Zufall:
            vote = random.choice(["upvote", "downvote"])
            if vote == "upvote":
                upvotes += 1
            else:
                downvotes += 1
            print(f"{validator} voted {vote}")


        print(f"Upvotes: {upvotes}, Downvotes: {downvotes}")
        return upvotes > downvotes

    @classmethod
    def from_json(cls, param):
        pass