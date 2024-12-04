import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

from blockchain.core.main import main

if __name__ == "__main__":
    """
    Startpunkt für den Blockchain-Service.
    """
    try:
        main()
    except Exception as e:
        print(f"500 Internal Server Error - Unerwarteter Fehler beim Starten der Anwendung: {e}")