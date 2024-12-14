import unittest
from kudos_blockchain import Blockchain, Block, Transaktion

# Beispielverwendung
kudos_chain = Blockchain()

transaktion1 = Transaktion("WalletA", "WalletB", "Thread1", "Subject1", "Hallo Welt!", 10)
transaktion2 = Transaktion("WalletB", "WalletC", "Thread2", "Subject2", "Noch eine Nachricht.", 5)

if kudos_chain.validiere_transaktionen([transaktion1, transaktion2]):
  neuer_block = Block(kudos_chain.kette[-1].hash, [transaktion1, transaktion2])
  kudos_chain.fuege_block_hinzu(neuer_block)
  print("Block hinzugefügt!")

print("Blockchain:")
for block in kudos_chain.kette:
  print(f"Hash: {block.hash}")
  print(f"Vorheriger Hash: {block.vorheriger_hash}")
  print(f"Transaktionen: {[t.__dict__ for t in block.transaktionen]}")
  print("--------------------")

transaktion3 = Transaktion("WalletC", "WalletA", "Thread1", "Subject3", "Längere Nachricht, um die Gebühr zu testen.................................................", 2)
if kudos_chain.validiere_transaktionen([transaktion3]):
    neuer_block = Block(kudos_chain.kette[-1].hash, [transaktion3])
    kudos_chain.fuege_block_hinzu(neuer_block)
    print("Block hinzugefügt!")
else:
    print("Block nicht hinzugefügt (Validierung fehlgeschlagen).")

print("Blockchain:")
for block in kudos_chain.kette:
  print(f"Hash: {block.hash}")
  print(f"Vorheriger Hash: {block.vorheriger_hash}")
  print(f"Transaktionen: {[t.__dict__ for t in block.transaktionen]}")
  print("--------------------")

if __name__ == '__main__':
    unittest.main()
