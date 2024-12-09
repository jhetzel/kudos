import unittest
from datetime import datetime
from unittest.mock import patch
import psycopg2
from chain.core.blockchain import (
    Block, Blockchain, Transaction, ValidatorManager,
    TransactionValidator, BlockService
)


class TestBlockchainIntegration(unittest.TestCase):
    """Integration tests for blockchain system components."""

    @patch('psycopg2.connect')
    def setUp(self, mock_connect):
        """Set up test environment with mocked database."""
        self.mock_db_url = "mock://db_url"
        self.blockchain = Blockchain(self.mock_db_url)

    def test_full_block_creation_flow(self):
        """Test complete flow of creating and adding a block."""
        # Create and validate transaction
        transaction = Transaction(
            sender="test_sender",
            receiver="test_receiver",
            amount=100.0
        )

        # Add transaction to mempool
        result = self.blockchain.add_transaction_to_mempool(transaction)
        self.assertTrue(result)
        self.assertEqual(len(self.blockchain.mempool), 1)

        # Create new block with transaction
        new_block = self.blockchain.add_block(
            data={"type": "test"},
            sender="test_sender",
            thread="test_thread",
            subject="Test Block",
            message="Test message",
            transactions=[transaction]
        )

        # Verify block was added correctly
        self.assertEqual(len(self.blockchain.chain), 2)
        self.assertEqual(new_block.index, 1)
        self.assertEqual(len(new_block.transactions), 1)
        self.assertEqual(new_block.transactions[0].sender, "test_sender")

    def test_chain_validation_flow(self):
        """Test blockchain validation with multiple blocks."""
        # Add multiple blocks
        blocks_data = [
            {
                "data": {"type": "test1"},
                "sender": "sender1",
                "thread": "thread1",
                "subject": "Block 1",
                "message": "Test message 1"
            },
            {
                "data": {"type": "test2"},
                "sender": "sender2",
                "thread": "thread2",
                "subject": "Block 2",
                "message": "Test message 2"
            }
        ]

        added_blocks = []
        for block_data in blocks_data:
            block = self.blockchain.add_block(**block_data)
            added_blocks.append(block)

        # Verify chain integrity
        self.assertEqual(len(self.blockchain.chain), 3)  # Including genesis
        self.assertTrue(self.blockchain._validate_chain(self.blockchain.chain))

        # Verify block relationships
        for i in range(1, len(self.blockchain.chain)):
            current_block = self.blockchain.chain[i]
            previous_block = self.blockchain.chain[i - 1]
            self.assertEqual(current_block.previous_hash, previous_block.hash)
            self.assertEqual(current_block.index, previous_block.index + 1)

    def test_validator_integration(self):
        """Test integration of validator system with blockchain."""
        # Set up validators
        self.blockchain.validator_manager.register_validator("validator1", 100)
        self.blockchain.validator_manager.register_validator("validator2", 150)

        # Create and add block
        new_block = self.blockchain.add_block(
            data={"type": "test"},
            sender="validator1",
            thread="test_thread",
            subject="Test Block",
            message="Test message"
        )

        # Verify validator can access block
        validator_id = "validator1"
        self.assertTrue(self.blockchain.validator_manager.is_validator(validator_id))
        self.assertEqual(
            self.blockchain.validator_manager.get_validator_kudos(validator_id),
            100
        )
        self.assertIn(new_block, self.blockchain.chain)

    def test_transaction_processing_flow(self):
        """Test complete transaction processing flow."""
        # Create multiple transactions
        transactions = [
            Transaction("sender1", "receiver1", 100.0),
            Transaction("sender2", "receiver2", 200.0),
            Transaction("sender3", "receiver3", 300.0)
        ]

        # Add transactions to mempool
        for tx in transactions:
            self.blockchain.add_transaction_to_mempool(tx)

        # Create block with transactions
        block = self.blockchain.add_block(
            data={"type": "transaction_block"},
            sender="test_sender",
            thread="test_thread",
            subject="Transaction Block",
            message="Block with multiple transactions",
            transactions=transactions
        )

        # Verify all transactions are included
        self.assertEqual(len(block.transactions), 3)
        self.assertEqual(
            sum(tx.amount for tx in block.transactions),
            600.0
        )


if __name__ == '__main__':
    unittest.main()