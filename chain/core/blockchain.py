from datetime import datetime
from typing import Dict, List, Optional, Union
import hashlib
import json
import logging
from dataclasses import dataclass, asdict
import psycopg2
from psycopg2.extras import DictCursor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class Transaction:
    sender: str
    receiver: str
    amount: float
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()

    def to_dict(self) -> dict:
        return {
            'sender': self.sender,
            'receiver': self.receiver,
            'amount': self.amount,
            'timestamp': self.timestamp.isoformat()
        }


class Block:
    def __init__(
            self,
            index: int,
            timestamp: Union[int, float, datetime],
            data: dict,
            previous_hash: str,
            sender: str,
            thread: str,
            subject: str,
            message: str,
            transactions: List[Transaction] = None
    ):
        self.index = index
        self.timestamp = (
            datetime.fromtimestamp(timestamp)
            if isinstance(timestamp, (int, float))
            else timestamp
        )
        self.data = data
        self.previous_hash = previous_hash
        self.sender = sender
        self.thread = thread
        self.subject = subject
        self.message = message
        self.transactions = transactions or []
        self.hash = self.calculate_hash()
        self._frozen_state = self._to_dict()

    def _to_dict(self, include_hash: bool = False) -> dict:
        block_dict = {
            "index": self.index,
            "timestamp": self.timestamp.isoformat(),
            "data": self.data,
            "transactions": [t.to_dict() for t in self.transactions],
            "previous_hash": self.previous_hash,
            "sender": self.sender,
            "thread": self.thread,
            "subject": self.subject,
            "message": self.message
        }
        if include_hash:
            block_dict["hash"] = self.hash
        return block_dict

    def calculate_hash(self) -> str:
        block_string = json.dumps(self._to_dict(), sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def is_unchanged(self) -> bool:
        return self._to_dict() == self._frozen_state


class TransactionValidator:
    """Validates blockchain transactions."""

    @staticmethod
    def validate_transaction(transaction: Transaction) -> bool:
        """Validate a single transaction."""
        try:
            if not isinstance(transaction, Transaction):
                logger.error("Transaction must be a Transaction instance")
                return False

            if transaction.sender == transaction.receiver:
                logger.error("Sender and receiver cannot be the same")
                return False

            if not isinstance(transaction.amount, (int, float)) or transaction.amount <= 0:
                logger.error("Invalid transaction amount")
                return False

            if not TransactionValidator._is_valid_address(transaction.sender):
                logger.error(f"Invalid sender address: {transaction.sender}")
                return False

            if not TransactionValidator._is_valid_address(transaction.receiver):
                logger.error(f"Invalid receiver address: {transaction.receiver}")
                return False

            return True

        except Exception as e:
            logger.error(f"Transaction validation error: {str(e)}")
            return False

    @staticmethod
    def _is_valid_address(address: str) -> bool:
        """Validate address format."""
        return isinstance(address, str) and len(address) > 0


class ValidatorManager:
    """Manages blockchain validators."""

    def __init__(self):
        self.validators: Dict[str, int] = {}

    def register_validator(self, validator_id: str, kudos_tokens: int) -> None:
        """Register a new validator."""
        if validator_id in self.validators:
            raise ValueError(f"Validator {validator_id} already registered")
        if kudos_tokens <= 0:
            raise ValueError("Kudos tokens must be greater than 0")
        self.validators[validator_id] = kudos_tokens

    def is_validator(self, validator_id: str) -> bool:
        """Check if validator is registered."""
        return validator_id in self.validators

    def get_validator_kudos(self, validator_id: str) -> int:
        """Get validator's kudos balance."""
        return self.validators.get(validator_id, 0)

    def get_all_validators(self) -> List[str]:
        """Get list of all validator IDs."""
        return list(self.validators.keys())


class BlockService:
    def __init__(self, db_url: str):
        try:
            self.connection = psycopg2.connect(db_url, cursor_factory=DictCursor)
            self.cursor = self.connection.cursor()
            self.initialize_db()
        except Exception as e:
            logger.error(f"Database connection error: {str(e)}")
            raise

    def initialize_db(self) -> None:
        create_table_query = """
        CREATE TABLE IF NOT EXISTS blocks (
            block_index SERIAL PRIMARY KEY,
            timestamp TIMESTAMP NOT NULL,
            data JSONB NOT NULL,
            previous_hash VARCHAR(64) NOT NULL,
            sender VARCHAR(255) NOT NULL,
            thread VARCHAR(255) NOT NULL,
            subject VARCHAR(255) NOT NULL,
            message TEXT NOT NULL,
            hash VARCHAR(64) NOT NULL
        );
        """
        try:
            self.cursor.execute(create_table_query)
            self.connection.commit()
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Database initialization error: {str(e)}")
            raise

    def save_block(self, block: Block) -> None:
        try:
            block_dict = block._to_dict(include_hash=True)
            self.cursor.execute(
                """
                INSERT INTO blocks (
                    timestamp, data, previous_hash, sender,
                    thread, subject, message, hash
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    block_dict["timestamp"],
                    json.dumps(block_dict["data"]),
                    block_dict["previous_hash"],
                    block_dict["sender"],
                    block_dict["thread"],
                    block_dict["subject"],
                    block_dict["message"],
                    block_dict["hash"],
                )
            )
            self.connection.commit()
            logger.info(f"Block saved: {block_dict['hash']}")
        except Exception as e:
            logger.error(f"Error saving block: {str(e)}")
            raise

    def load_chain(self) -> List[dict]:
        try:
            self.cursor.execute("SELECT * FROM blocks ORDER BY block_index ASC")
            rows = self.cursor.fetchall()
            chain_data = []
            for row in rows:
                data = row["data"]
                if isinstance(data, str):
                    data = json.loads(data)
                row["data"] = data
                chain_data.append(dict(row))
            logger.debug(f"Loaded chain data: {chain_data}")
            return chain_data
        except Exception as e:
            logger.error(f"Error loading chain: {str(e)}")
            raise


class Blockchain:
    def __init__(self, db_url: str):
        self.block_service = BlockService(db_url)
        self.chain = self._load_chain_from_db()
        self.mempool: List[Transaction] = []

        if not self.chain:
            genesis_block = self._create_genesis_block()
            self.chain.append(genesis_block)
            self.block_service.save_block(genesis_block)
            logger.info("Genesis block created and saved.")

    def _create_genesis_block(self) -> Block:
        genesis_block = Block(
            index=0,
            timestamp=datetime.utcnow(),
            data={"type": "genesis"},
            previous_hash="0" * 64,
            sender="system",
            thread="genesis",
            subject="Genesis Block",
            message="Initial block of the chain",
            transactions=[]
        )
        logger.debug(f"Genesis block details: {genesis_block._to_dict(include_hash=True)}")
        return genesis_block

    def _load_chain_from_db(self) -> List[Block]:
        try:
            chain_data = self.block_service.load_chain()
            chain = []
            for block_data in chain_data:
                block = Block(
                    index=block_data["block_index"],
                    timestamp=block_data["timestamp"],
                    data=block_data["data"],
                    previous_hash=block_data["previous_hash"],
                    sender=block_data["sender"],
                    thread=block_data["thread"],
                    subject=block_data["subject"],
                    message=block_data["message"],
                    transactions=[]
                )
                chain.append(block)
            logger.info(f"Loaded chain with {len(chain)} blocks.")
            return chain
        except Exception as e:
            logger.error(f"Error loading chain: {str(e)}")
            return []

    def add_block(self, data: dict, sender: str, thread: str, subject: str, message: str, transactions: List[Transaction] = None) -> Block:
        last_block = self.chain[-1]
        new_block = Block(
            index=last_block.index + 1,
            timestamp=datetime.utcnow(),
            data=data,
            previous_hash=last_block.hash,
            sender=sender,
            thread=thread,
            subject=subject,
            message=message,
            transactions=transactions or []
        )
        logger.info(f"Adding block with index {new_block.index}")
        logger.debug(f"Block details: {new_block._to_dict(include_hash=True)}")

        self.chain.append(new_block)
        self.block_service.save_block(new_block)
        return new_block
