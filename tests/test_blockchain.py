import unittest
from datetime import datetime
from unittest.mock import MagicMock, patch
import json
import hashlib
import logging
import sys
from typing import Any, Dict

# Configure detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('blockchain_tests.log')
    ]
)

logger = logging.getLogger(__name__)


class BlockchainJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder for blockchain objects."""

    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


def json_serialize(obj):
    """Helper function for JSON serialization."""
    return json.dumps(obj, cls=BlockchainJSONEncoder, indent=2)


def log_test_step(step_name: str, details: Dict[str, Any] = None) -> None:
    """Utility function for structured test logging."""
    logger.info(f"TEST STEP: {step_name}")
    if details:
        for key, value in details.items():
            logger.debug(f"  {key}: {json_serialize(value)}")


from chain.core.blockchain import (
    Block, Blockchain, Transaction, TransactionValidator,
    ValidatorManager, BlockService
)


def get_db_url():
    """Get production database URL."""
    url = "postgresql://kudos_user:kudos_pass@localhost:5432/kudos"
    logger.info(f"Database URL configured: {url}")
    return url


class BlockchainTestCase(unittest.TestCase):
    """Base test class for blockchain tests."""

    @classmethod
    def setUpClass(cls):
        """Initialize test environment."""
        logger.info("=== Initializing BlockchainTestCase ===")
        cls.db_url = get_db_url()
        logger.info(f"Test class initialized with DB URL: {cls.db_url}")

    def setUp(self):
        """Set up individual test."""
        logger.info(f"\n=== Setting up test: {self._testMethodName} ===")
        self.blockchain = Blockchain(get_db_url())
        logger.info("Blockchain instance created")

    def tearDown(self):
        """Test cleanup."""
        logger.info(f"=== Completing test: {self._testMethodName} ===\n")


import time
import functools
from typing import Any, Callable, Dict


def log_performance(func: Callable) -> Callable:
    """Performance logging decorator."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        logger.debug(f"Starting {func.__name__}")

        try:
            result = func(*args, **kwargs)
            execution_time = (time.perf_counter() - start_time) * 1000
            logger.info(f"Performance - {func.__name__}: {execution_time:.2f}ms")
            return result
        except Exception as e:
            execution_time = (time.perf_counter() - start_time) * 1000
            logger.error(f"Error in {func.__name__} after {execution_time:.2f}ms: {str(e)}")
            raise

    return wrapper


class TransactionLogger:
    """Transaction logging utility."""

    @staticmethod
    def log_transaction_details(transaction: Transaction, prefix: str = "") -> None:
        """Log detailed transaction information."""
        logger.debug(f"{prefix} Transaction Details:")
        logger.debug(f"  - Sender: {transaction.sender}")
        logger.debug(f"  - Receiver: {transaction.receiver}")
        logger.debug(f"  - Amount: {transaction.amount}")
        logger.debug(f"  - Timestamp: {transaction.timestamp}")

    @staticmethod
    def log_transaction_validation(transaction: Transaction, is_valid: bool) -> None:
        """Log transaction validation results."""
        logger.info(f"Transaction Validation Result:")
        logger.info(f"  - Valid: {is_valid}")
        if not is_valid:
            logger.warning("  - Validation failed for transaction:")
            TransactionLogger.log_transaction_details(transaction, "    ")


class TestTransaction(BlockchainTestCase):
    """Enhanced test suite for Transaction class with performance metrics."""

    @log_performance
    def setUp(self):
        logger.info(f"\n=== Setting up Transaction test: {self._testMethodName} ===")
        self.transaction = Transaction(
            sender="sender123",
            receiver="receiver456",
            amount=100.0
        )
        TransactionLogger.log_transaction_details(self.transaction, "New")

    @log_performance
    def test_transaction_initialization(self):
        """Test transaction initialization with performance metrics."""
        logger.info("Testing transaction initialization")
        start_time = time.perf_counter()

        # Core test logic
        self.assertEqual(self.transaction.sender, "sender123")
        self.assertEqual(self.transaction.receiver, "receiver456")
        self.assertEqual(self.transaction.amount, 100.0)
        self.assertIsInstance(self.transaction.timestamp, datetime)

        execution_time = (time.perf_counter() - start_time) * 1000
        logger.info(f"Transaction initialization completed in {execution_time:.2f}ms")


class TestTransactionValidator(unittest.TestCase):
    """Enhanced test suite for TransactionValidator with detailed logging."""

    @log_performance
    def setUp(self):
        self.validator = TransactionValidator()
        self.valid_transaction = Transaction(
            sender="valid_sender",
            receiver="valid_receiver",
            amount=100.0
        )
        TransactionLogger.log_transaction_details(self.valid_transaction, "Valid")

    @log_performance
    def test_valid_transaction(self):
        """Test validation of valid transaction with metrics."""
        logger.info("Testing valid transaction validation")
        start_time = time.perf_counter()

        result = self.validator.validate_transaction(self.valid_transaction)
        TransactionLogger.log_transaction_validation(self.valid_transaction, result)

        execution_time = (time.perf_counter() - start_time) * 1000
        logger.info(f"Validation completed in {execution_time:.2f}ms")
        self.assertTrue(result)


class TestBlockchain(BlockchainTestCase):
    """Enhanced test suite for Blockchain with performance tracking."""

    @log_performance
    def test_block_addition(self, _):
        """Test block addition with transaction and performance logging."""
        logger.info("Starting block addition test with performance tracking")

        # Initial state logging with timing
        start_time = time.perf_counter()
        initial_chain = [block._to_dict() for block in self.blockchain.chain]
        logger.info(f"Initial chain state loaded in {(time.perf_counter() - start_time) * 1000:.2f}ms")

        # Create test transaction
        test_transaction = Transaction(
            sender="test_sender",
            receiver="test_receiver",
            amount=50.0
        )
        TransactionLogger.log_transaction_details(test_transaction, "Test")

        # Add transaction to mempool
        mempool_start = time.perf_counter()
        self.blockchain.add_transaction_to_mempool(test_transaction)
        logger.info(f"Transaction added to mempool in {(time.perf_counter() - mempool_start) * 1000:.2f}ms")

        # Add new block with timing
        block_start = time.perf_counter()
        new_block = self.blockchain.add_block(
            data={"test": "data"},
            sender="test_sender",
            thread="test_thread",
            subject="Test Block",
            message="Test message",
            transactions=[test_transaction]
        )
        logger.info(f"Block addition completed in {(time.perf_counter() - block_start) * 1000:.2f}ms")

        # Verification with timing
        verify_start = time.perf_counter()
        self.assertEqual(len(self.blockchain.chain), self.initial_chain_length + 1)
        self.assertEqual(self.blockchain.chain[-1].hash, new_block.hash)
        logger.info(f"Verification completed in {(time.perf_counter() - verify_start) * 1000:.2f}ms")

    def setUp(self):
        logger.info(f"\n=== Setting up Transaction test: {self._testMethodName} ===")
        self.transaction = Transaction(
            sender="sender123",
            receiver="receiver456",
            amount=100.0
        )
        log_test_step("Transaction created", {
            "sender": self.transaction.sender,
            "receiver": self.transaction.receiver,
            "amount": self.transaction.amount
        })

    def test_transaction_initialization(self):
        """Test transaction initialization."""
        log_test_step("Testing transaction initialization")
        self.assertEqual(self.transaction.sender, "sender123")
        self.assertEqual(self.transaction.receiver, "receiver456")
        self.assertEqual(self.transaction.amount, 100.0)
        self.assertIsInstance(self.transaction.timestamp, datetime)
        logger.info("Transaction initialization test passed")

    def test_transaction_to_dict(self):
        """Test transaction dictionary conversion."""
        log_test_step("Testing transaction to dictionary conversion")
        tx_dict = self.transaction.to_dict()
        logger.debug(f"Generated dictionary: {tx_dict}")
        self.assertIsInstance(tx_dict, dict)
        self.assertEqual(tx_dict['sender'], "sender123")
        self.assertEqual(tx_dict['receiver'], "receiver456")
        self.assertEqual(tx_dict['amount'], 100.0)
        self.assertIsInstance(tx_dict['timestamp'], str)
        logger.info("Transaction to dictionary test passed")


@patch('psycopg2.connect')
class TestBlockchain(BlockchainTestCase):
    """Test suite for Blockchain class."""

    def setUp(self):
        """Initialize test environment."""
        log_test_step("Setting up Blockchain test")
        self.blockchain = Blockchain(get_db_url())
        self.initial_chain_length = len(self.blockchain.chain)
        logger.info(f"Initial chain length: {self.initial_chain_length}")

    def test_blockchain_initialization(self, _):
        """Test blockchain initialization."""
        log_test_step("Testing blockchain initialization")

        chain_length = len(self.blockchain.chain)
        logger.info(f"Current chain length: {chain_length}")

        first_block = self.blockchain.chain[0]
        logger.debug(f"Genesis block details: {first_block._to_dict()}")

        self.assertGreaterEqual(chain_length, 1)
        self.assertEqual(first_block.index, 0)
        self.assertEqual(first_block.previous_hash, "0" * 64)
        logger.info("Blockchain initialization test passed")

    def test_block_addition(self, _):
        """Test block addition."""
        log_test_step("Starting block addition test")

        # Initial state logging
        initial_chain = [block._to_dict() for block in self.blockchain.chain]
        logger.debug(f"Initial chain state: {json_serialize(initial_chain)}")

        initial_length = len(self.blockchain.chain)
        logger.info(f"Initial chain length: {initial_length}")

        db_state = self.blockchain.block_service.load_chain()
        logger.info(f"Initial DB state (block count): {len(db_state)}")
        logger.debug(f"DB state details: {json_serialize(db_state)}")

        # Add new block
        log_test_step("Adding new block")
        new_block = self.blockchain.add_block(
            data={"test": "data"},
            sender="test_sender",
            thread="test_thread",
            subject="Test Block",
            message="Test message"
        )
        logger.debug(f"New block created: {new_block._to_dict()}")

        # Post-addition state logging
        final_chain = [block._to_dict() for block in self.blockchain.chain]
        logger.debug(f"Final chain state: {json.dumps(final_chain, indent=2)}")

        final_db_state = self.blockchain.block_service.load_chain()
        logger.info(f"Final chain length: {len(self.blockchain.chain)}")
        logger.info(f"Final DB state (block count): {len(final_db_state)}")

        # Verify chain state
        log_test_step("Verifying chain state")
        self.assertEqual(len(self.blockchain.chain), initial_length + 1)
        self.assertEqual(self.blockchain.chain[-1].hash, new_block.hash)
        self.assertEqual(new_block.index, initial_length)
        logger.info("Block addition test passed")


class TestBlockService(unittest.TestCase):
    """Test suite for BlockService."""

    @patch('psycopg2.connect')
    def setUp(self, mock_connect):
        """Set up test environment."""
        log_test_step("Setting up BlockService test")

        self.mock_connection = MagicMock()
        self.mock_cursor = MagicMock()
        self.mock_connection.cursor.return_value = self.mock_cursor
        mock_connect.return_value = self.mock_connection

        logger.info("Creating BlockService instance")
        self.block_service = BlockService("mock://db_url")
        logger.info("BlockService instance created")

        # Verify initialization
        logger.debug("Verifying initialization calls")
        self.mock_cursor.execute.assert_called()
        self.mock_connection.commit.assert_called()

    def test_save_block(self):
        """Test block saving."""
        log_test_step("Testing block save operation")

        # Reset mocks
        logger.debug("Resetting mocks for clean state")
        self.mock_cursor.reset_mock()
        self.mock_connection.reset_mock()

        # Create test block
        test_block = Block(
            index=1,
            timestamp=datetime.utcnow(),
            data={"test": "data"},
            previous_hash="0" * 64,
            sender="test_sender",
            thread="test_thread",
            subject="Test Block",
            message="Test message"
        )
        logger.debug(f"Test block created: {test_block._to_dict()}")

        # Save block
        logger.info("Saving block to database")
        self.block_service.save_block(test_block)

        # Verify database operations
        log_test_step("Verifying database operations")
        self.assertEqual(self.mock_cursor.execute.call_count, 1)
        self.assertEqual(self.mock_connection.commit.call_count, 1)

        # Verify SQL parameters
        call_args = self.mock_cursor.execute.call_args
        logger.debug(f"SQL Query: {call_args[0][0]}")
        logger.debug(f"SQL Parameters: {call_args[0][1]}")
        self.assertIn("INSERT INTO blocks", call_args[0][0])
        self.assertEqual(len(call_args[0][1]), 8)
        logger.info("Block save test passed")

    def test_load_chain(self):
        """Test chain loading."""
        log_test_step("Testing chain load operation")

        # Prepare mock data
        mock_data = [{
            "block_index": 0,
            "timestamp": datetime.utcnow(),
            "data": '{"type":"genesis"}',
            "previous_hash": "0" * 64,
            "hash": "test_hash",
            "sender": "system",
            "thread": "genesis",
            "subject": "Genesis",
            "message": "Genesis block"
        }]
        logger.debug(f"Prepared mock data: {mock_data}")

        self.mock_cursor.fetchall.return_value = mock_data

        # Load chain
        logger.info("Loading chain from database")
        chain_data = self.block_service.load_chain()
        logger.debug(f"Loaded chain data: {chain_data}")

        # Verify results
        log_test_step("Verifying loaded data")
        self.assertEqual(len(chain_data), 1)
        self.assertEqual(chain_data[0]["block_index"], 0)
        self.assertEqual(chain_data[0]["sender"], "system")
        logger.info("Chain load test passed")