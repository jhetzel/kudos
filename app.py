import json

from flask import Flask, request, jsonify
from kudos_blockchain import Blockchain, Transaktion

app = Flask(__name__)
kudos_chain = Blockchain()

# Laden der Blockchain aus einer Datei beim Start (wenn vorhanden)
try:
    with open("blockchain_data.json", "r") as f:
        kudos_chain = Blockchain.from_json(f.read())
    print("Blockchain aus Datei geladen.")
except FileNotFoundError:
    print("Keine Blockchain-Datei gefunden. Neue Blockchain erstellt.")


@app.route('/transaction', methods=['POST'])
def neue_transaktion():
    data = request.get_json()
    try:
        transaktion = Transaktion(data['sender_wallet'], data['empfaenger_wallet'], data['thread'], data['subject'], data['message'], data['amount'])
        kudos_chain.add_transaction(transaktion)
        return jsonify({"message": "Transaktion zur Warteschlange hinzugefügt."}), 201
    except KeyError as e:
        return jsonify({"error": f"Fehlendes Feld: {e}"}), 400
    except TypeError as e:
        return jsonify({"error": f"Falscher Datentyp: {e}"}), 400
    except Exception as e:
        return jsonify({"error": f"Unerwarteter Fehler: {e}"}), 500

@app.route('/mine', methods=['POST'])
def mine_block():
    block = kudos_chain.mine_block()
    if block:
      # Speichern der Blockchain nach dem Minen
      with open("blockchain_data.json", "w") as f:
          f.write(kudos_chain.to_json())
      return jsonify({"message": "Block gemined!", "block_hash": block.hash}), 200
    else:
        return jsonify({"message": "Kein Block gemined (entweder keine Transaktionen oder Validierung fehlgeschlagen).",}), 200

@app.route('/chain', methods=['GET'])
def get_chain():
    return jsonify(json.loads(kudos_chain.to_json())), 200 # JSON wieder in ein Python-Dict umwandeln für die jsonify()-Funktion

if __name__ == '__main__':
    app.run(debug=True)