import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from blockchain.core.main import main

if __name__ == "__main__":
    main()