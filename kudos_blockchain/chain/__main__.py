from kudos_blockchain.chain.core.main import main

if __name__ == "__main__":
    """
    Startpunkt für den Blockchain-Service.
    """
    try:
        main()
    except Exception as e:
        print(f"500 Internal Server Error - Unerwarteter Fehler beim Starten der Anwendung: {e}")