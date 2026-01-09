"""
Blockchain Service for Portfolio Staking Platform.

Provides Web3 integration for:
- Contract deployment and interaction
- Staking operations (stake, withdraw, claim)
- Event monitoring and indexing
- Transaction management
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from decimal import Decimal
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from web3 import Web3
from web3.contract import Contract
from web3.types import TxReceipt, Wei
from eth_account import Account
from eth_account.signers.local import LocalAccount

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class StakeInfo:
    """Stake information for a user."""
    balance: int
    reward_debt: int
    last_updated: int
    pending_rewards: int


@dataclass
class TransactionResult:
    """Result of a blockchain transaction."""
    tx_hash: str
    block_number: int
    gas_used: int
    status: bool
    events: List[Dict]


class BlockchainService:
    """
    Service for interacting with Portfolio Staking smart contracts.

    Provides high-level methods for:
    - Contract deployment
    - Staking operations
    - Reward management
    - Event indexing
    """

    def __init__(
        self,
        rpc_url: str,
        private_key: Optional[str] = None,
        chain_id: int = 31337
    ):
        """
        Initialize blockchain service.

        Args:
            rpc_url: Ethereum RPC endpoint URL
            private_key: Private key for signing transactions
            chain_id: Network chain ID (default: 31337 for Hardhat)
        """
        self.web3 = Web3(Web3.HTTPProvider(rpc_url))
        self.chain_id = chain_id

        # Setup account if private key provided
        self.account: Optional[LocalAccount] = None
        if private_key:
            self.account = Account.from_key(private_key)
            logger.info(f"Account loaded: {self.account.address}")

        # Contract instances
        self.staking_contract: Optional[Contract] = None
        self.staking_token: Optional[Contract] = None
        self.reward_token: Optional[Contract] = None

        # Contract ABIs (loaded from artifacts)
        self._abis = {}

    @property
    def is_connected(self) -> bool:
        """Check if connected to blockchain."""
        return self.web3.is_connected()

    @property
    def block_number(self) -> int:
        """Get current block number."""
        return self.web3.eth.block_number

    def load_contract_abi(self, contract_name: str) -> Dict:
        """
        Load contract ABI from artifacts.

        Args:
            contract_name: Name of the contract

        Returns:
            Contract ABI as dict
        """
        if contract_name in self._abis:
            return self._abis[contract_name]

        # Look for artifact in common locations
        artifact_paths = [
            Path(f"artifacts/contracts/{contract_name}.sol/{contract_name}.json"),
            Path(f"artifacts/{contract_name}.json"),
            Path(f"build/contracts/{contract_name}.json"),
        ]

        for path in artifact_paths:
            if path.exists():
                with open(path) as f:
                    artifact = json.load(f)
                    self._abis[contract_name] = artifact.get('abi', artifact)
                    return self._abis[contract_name]

        raise FileNotFoundError(f"Contract artifact not found for {contract_name}")

    def get_contract(self, address: str, abi: List[Dict]) -> Contract:
        """
        Get contract instance.

        Args:
            address: Contract address
            abi: Contract ABI

        Returns:
            Web3 Contract instance
        """
        return self.web3.eth.contract(
            address=Web3.to_checksum_address(address),
            abi=abi
        )

    def setup_staking_contract(
        self,
        staking_address: str,
        staking_token_address: str,
        reward_token_address: str
    ):
        """
        Setup staking contract and token contracts.

        Args:
            staking_address: PortfolioStaking contract address
            staking_token_address: Staking token (ERC20) address
            reward_token_address: Reward token (ERC20) address
        """
        # Load ABIs
        staking_abi = self.load_contract_abi("PortfolioStaking")
        erc20_abi = self._get_erc20_abi()

        # Create contract instances
        self.staking_contract = self.get_contract(staking_address, staking_abi)
        self.staking_token = self.get_contract(staking_token_address, erc20_abi)
        self.reward_token = self.get_contract(reward_token_address, erc20_abi)

        logger.info(f"Staking contract setup at {staking_address}")

    def _get_erc20_abi(self) -> List[Dict]:
        """Get standard ERC20 ABI."""
        return [
            {
                "inputs": [{"name": "account", "type": "address"}],
                "name": "balanceOf",
                "outputs": [{"name": "", "type": "uint256"}],
                "stateMutability": "view",
                "type": "function"
            },
            {
                "inputs": [
                    {"name": "spender", "type": "address"},
                    {"name": "amount", "type": "uint256"}
                ],
                "name": "approve",
                "outputs": [{"name": "", "type": "bool"}],
                "stateMutability": "nonpayable",
                "type": "function"
            },
            {
                "inputs": [
                    {"name": "owner", "type": "address"},
                    {"name": "spender", "type": "address"}
                ],
                "name": "allowance",
                "outputs": [{"name": "", "type": "uint256"}],
                "stateMutability": "view",
                "type": "function"
            },
            {
                "inputs": [
                    {"name": "to", "type": "address"},
                    {"name": "amount", "type": "uint256"}
                ],
                "name": "transfer",
                "outputs": [{"name": "", "type": "bool"}],
                "stateMutability": "nonpayable",
                "type": "function"
            }
        ]

    def _send_transaction(self, tx_func, value: int = 0) -> TransactionResult:
        """
        Build, sign, and send a transaction.

        Args:
            tx_func: Contract function to call
            value: ETH value to send (in wei)

        Returns:
            TransactionResult with tx details
        """
        if not self.account:
            raise ValueError("No account configured for signing transactions")

        # Build transaction
        tx = tx_func.build_transaction({
            'from': self.account.address,
            'nonce': self.web3.eth.get_transaction_count(self.account.address),
            'gas': 500000,
            'gasPrice': self.web3.eth.gas_price,
            'chainId': self.chain_id,
            'value': value
        })

        # Sign and send
        signed_tx = self.account.sign_transaction(tx)
        tx_hash = self.web3.eth.send_raw_transaction(signed_tx.raw_transaction)

        # Wait for receipt
        receipt: TxReceipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)

        # Parse events
        events = []
        if self.staking_contract:
            for event_name in ['Staked', 'Withdrawn', 'RewardClaimed']:
                try:
                    event = getattr(self.staking_contract.events, event_name)
                    parsed = event().process_receipt(receipt)
                    events.extend([dict(e['args']) for e in parsed])
                except Exception:
                    pass

        return TransactionResult(
            tx_hash=tx_hash.hex(),
            block_number=receipt['blockNumber'],
            gas_used=receipt['gasUsed'],
            status=receipt['status'] == 1,
            events=events
        )

    # ==================== Staking Operations ====================

    def approve_staking(self, amount: int) -> TransactionResult:
        """
        Approve staking contract to spend tokens.

        Args:
            amount: Amount to approve (in token units)

        Returns:
            TransactionResult
        """
        if not self.staking_token or not self.staking_contract:
            raise ValueError("Contracts not setup")

        tx_func = self.staking_token.functions.approve(
            self.staking_contract.address,
            amount
        )
        return self._send_transaction(tx_func)

    def stake(self, amount: int) -> TransactionResult:
        """
        Stake tokens in the contract.

        Args:
            amount: Amount to stake (in token units)

        Returns:
            TransactionResult
        """
        if not self.staking_contract:
            raise ValueError("Staking contract not setup")

        tx_func = self.staking_contract.functions.stake(amount)
        return self._send_transaction(tx_func)

    def withdraw(self, amount: int) -> TransactionResult:
        """
        Withdraw staked tokens.

        Args:
            amount: Amount to withdraw (in token units)

        Returns:
            TransactionResult
        """
        if not self.staking_contract:
            raise ValueError("Staking contract not setup")

        tx_func = self.staking_contract.functions.withdraw(amount)
        return self._send_transaction(tx_func)

    def claim_rewards(self) -> TransactionResult:
        """
        Claim pending rewards.

        Returns:
            TransactionResult
        """
        if not self.staking_contract:
            raise ValueError("Staking contract not setup")

        tx_func = self.staking_contract.functions.claim()
        return self._send_transaction(tx_func)

    # ==================== View Functions ====================

    def get_stake_info(self, address: str) -> StakeInfo:
        """
        Get staking information for an address.

        Args:
            address: User address

        Returns:
            StakeInfo with balance and rewards
        """
        if not self.staking_contract:
            raise ValueError("Staking contract not setup")

        address = Web3.to_checksum_address(address)

        # Get pending rewards
        pending = self.staking_contract.functions.pendingRewards(address).call()

        # Note: In a real scenario, we'd have a getter for stakes mapping
        # For now, return with pending rewards
        return StakeInfo(
            balance=0,  # Would need stakes mapping getter
            reward_debt=0,
            last_updated=0,
            pending_rewards=pending
        )

    def get_total_staked(self) -> int:
        """Get total staked amount."""
        if not self.staking_contract:
            raise ValueError("Staking contract not setup")

        return self.staking_contract.functions.totalStaked().call()

    def get_reward_rate(self) -> int:
        """Get current reward rate per second."""
        if not self.staking_contract:
            raise ValueError("Staking contract not setup")

        return self.staking_contract.functions.rewardRatePerSecond().call()

    def get_token_balance(self, token: str, address: str) -> int:
        """
        Get token balance for an address.

        Args:
            token: 'staking' or 'reward'
            address: User address

        Returns:
            Token balance
        """
        contract = self.staking_token if token == 'staking' else self.reward_token
        if not contract:
            raise ValueError(f"{token} token contract not setup")

        return contract.functions.balanceOf(
            Web3.to_checksum_address(address)
        ).call()

    # ==================== Admin Functions ====================

    def set_reward_rate(self, rate: int) -> TransactionResult:
        """
        Set new reward rate (owner only).

        Args:
            rate: New reward rate per second

        Returns:
            TransactionResult
        """
        if not self.staking_contract:
            raise ValueError("Staking contract not setup")

        tx_func = self.staking_contract.functions.setRewardRate(rate)
        return self._send_transaction(tx_func)

    # ==================== Event Indexing ====================

    def get_staking_events(
        self,
        from_block: int = 0,
        to_block: str = 'latest',
        event_type: Optional[str] = None
    ) -> List[Dict]:
        """
        Get staking events from the contract.

        Args:
            from_block: Starting block number
            to_block: Ending block number or 'latest'
            event_type: Optional filter for event type (Staked, Withdrawn, RewardClaimed)

        Returns:
            List of event dictionaries
        """
        if not self.staking_contract:
            raise ValueError("Staking contract not setup")

        events = []
        event_types = [event_type] if event_type else ['Staked', 'Withdrawn', 'RewardClaimed']

        for et in event_types:
            try:
                event_filter = getattr(self.staking_contract.events, et)
                logs = event_filter().get_logs(
                    fromBlock=from_block,
                    toBlock=to_block
                )

                for log in logs:
                    events.append({
                        'event': et,
                        'block_number': log['blockNumber'],
                        'tx_hash': log['transactionHash'].hex(),
                        'args': dict(log['args'])
                    })
            except Exception as e:
                logger.warning(f"Error fetching {et} events: {e}")

        return sorted(events, key=lambda x: x['block_number'])


class EventIndexer:
    """
    Indexes blockchain events for efficient querying.

    Tracks staking history, user positions, and protocol statistics.
    """

    def __init__(self, blockchain_service: BlockchainService):
        """
        Initialize event indexer.

        Args:
            blockchain_service: BlockchainService instance
        """
        self.blockchain = blockchain_service
        self.last_indexed_block = 0

        # In-memory indexes (would use a database in production)
        self.user_stakes: Dict[str, int] = {}
        self.user_rewards: Dict[str, int] = {}
        self.total_staked_history: List[Tuple[int, int]] = []

    def index_events(self, from_block: Optional[int] = None):
        """
        Index new events from the blockchain.

        Args:
            from_block: Starting block (default: last indexed + 1)
        """
        start_block = from_block or (self.last_indexed_block + 1)

        events = self.blockchain.get_staking_events(from_block=start_block)

        for event in events:
            self._process_event(event)
            self.last_indexed_block = max(
                self.last_indexed_block,
                event['block_number']
            )

        logger.info(f"Indexed {len(events)} events up to block {self.last_indexed_block}")

    def _process_event(self, event: Dict):
        """Process a single event."""
        args = event['args']
        user = args.get('user', '').lower()

        if event['event'] == 'Staked':
            amount = args.get('amount', 0)
            self.user_stakes[user] = self.user_stakes.get(user, 0) + amount

        elif event['event'] == 'Withdrawn':
            amount = args.get('amount', 0)
            self.user_stakes[user] = max(0, self.user_stakes.get(user, 0) - amount)

        elif event['event'] == 'RewardClaimed':
            amount = args.get('amount', 0)
            self.user_rewards[user] = self.user_rewards.get(user, 0) + amount

    def get_user_position(self, address: str) -> Dict:
        """Get indexed position for a user."""
        address = address.lower()
        return {
            'staked': self.user_stakes.get(address, 0),
            'total_rewards_claimed': self.user_rewards.get(address, 0)
        }

    def get_protocol_stats(self) -> Dict:
        """Get protocol-wide statistics."""
        return {
            'total_users': len(self.user_stakes),
            'total_staked': sum(self.user_stakes.values()),
            'total_rewards_distributed': sum(self.user_rewards.values()),
            'last_indexed_block': self.last_indexed_block
        }
