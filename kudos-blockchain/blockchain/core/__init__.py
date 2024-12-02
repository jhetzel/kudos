import sys
print(sys.path)
# Option 1: Relative import
# /app/blockchain/core/__init__.py
from .blockchain import Blockchain
__all__ = ['Blockchain']