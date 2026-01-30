from web3 import Web3
from eth_account import Account
from .base import BaseWallet
from typing import Dict, Any, Optional
import json

class EthereumWallet(BaseWallet):
    def __init__(self, rpc_url: str, chain_id: int = 1):
        self.web3 = Web3(Web3.HTTPProvider(rpc_url))
        self.chain_id = chain_id
        # For newer web3 versions, use different approach
        if hasattr(Account, 'enable_unaudited_hdwallet_features'):
            Account.enable_unaudited_hdwallet_features()
    
    def create_wallet(self, mnemonic: Optional[str] = None) -> Dict[str, Any]:
        try:
            if mnemonic:
                # Create account from mnemonic
                account = self.web3.eth.account.from_mnemonic(mnemonic)
            else:
                # Create new account
                account = self.web3.eth.account.create()
            
            return {
                'address': account.address,
                'private_key': account.key.hex() if hasattr(account.key, 'hex') else account.key.hex(),
                'public_key': '',
                'mnemonic': mnemonic
            }
        except Exception as e:
            # Fallback method
            if mnemonic:
                account = Account.from_mnemonic(mnemonic)
            else:
                account = Account.create()
            
            return {
                'address': account.address,
                'private_key': account.key.hex(),
                'public_key': account.key.public_key.hex() if hasattr(account.key, 'public_key') else '',
                'mnemonic': mnemonic
            }
    
    def get_balance(self, address: str) -> float:
        try:
            balance_wei = self.web3.eth.get_balance(address)
            return self.web3.from_wei(balance_wei, 'ether')
        except Exception as e:
            print(f"Balance error: {e}")
            return 0.0
    
    def send_transaction(self, private_key: str, to_address: str, amount: float, gas_price: Optional[int] = None) -> str:
        try:
            account = self.web3.eth.account.from_key(private_key)
            nonce = self.web3.eth.get_transaction_count(account.address)
            
            # Prepare transaction
            tx = {
                'nonce': nonce,
                'to': self.web3.to_checksum_address(to_address),
                'value': self.web3.to_wei(amount, 'ether'),
                'gas': 21000,  # Standard gas limit for simple transfers
                'chainId': self.chain_id,
                'gasPrice': gas_price if gas_price else self.web3.eth.gas_price
            }
            
            # Sign and send
            signed_tx = self.web3.eth.account.sign_transaction(tx, private_key)
            tx_hash = self.web3.eth.send_raw_transaction(signed_tx.rawTransaction)
            
            return tx_hash.hex()
        except Exception as e:
            raise Exception(f"Send transaction error: {e}")
    
    def get_transaction(self, tx_hash: str) -> Dict[str, Any]:
        try:
            tx = self.web3.eth.get_transaction(tx_hash)
            receipt = self.web3.eth.get_transaction_receipt(tx_hash)
            
            return {
                'hash': tx_hash,
                'from': tx['from'],
                'to': tx['to'],
                'value': self.web3.from_wei(tx['value'], 'ether'),
                'blockNumber': tx.get('blockNumber'),
                'status': receipt.get('status') if receipt else None,
                'confirmations': 0
            }
        except Exception as e:
            return {'error': str(e)}

# BEP20 (Binance Smart Chain)
class BSCWallet(EthereumWallet):
    def __init__(self, rpc_url: str = "https://bsc-dataseed.binance.org/"):
        super().__init__(rpc_url, chain_id=56)

# Polygon
class PolygonWallet(EthereumWallet):
    def __init__(self, rpc_url: str = "https://polygon-rpc.com"):
        super().__init__(rpc_url, chain_id=137)
