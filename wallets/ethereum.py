from web3 import Web3
from eth_account import Account
from .base import BaseWallet
import json

class EthereumWallet(BaseWallet):
    def __init__(self, rpc_url: str, chain_id: int = 1):
        self.web3 = Web3(Web3.HTTPProvider(rpc_url))
        self.chain_id = chain_id
        Account.enable_unaudited_hdwallet_features()
    
    def create_wallet(self, mnemonic: str = None) -> Dict[str, Any]:
        if mnemonic:
            account = Account.from_mnemonic(mnemonic)
        else:
            account = Account.create()
        
        return {
            'address': account.address,
            'private_key': account.key.hex(),
            'public_key': account.publickey.hex(),
            'mnemonic': mnemonic
        }
    
    def get_balance(self, address: str) -> float:
        balance_wei = self.web3.eth.get_balance(address)
        return self.web3.from_wei(balance_wei, 'ether')
    
    def send_transaction(self, private_key: str, to_address: str, amount: float, gas_price: int = None) -> str:
        account = Account.from_key(private_key)
        nonce = self.web3.eth.get_transaction_count(account.address)
        
        tx = {
            'nonce': nonce,
            'to': to_address,
            'value': self.web3.to_wei(amount, 'ether'),
            'gas': 21000,
            'chainId': self.chain_id
        }
        
        if gas_price:
            tx['gasPrice'] = gas_price
        else:
            tx['gasPrice'] = self.web3.eth.gas_price
        
        signed_tx = self.web3.eth.account.sign_transaction(tx, private_key)
        tx_hash = self.web3.eth.send_raw_transaction(signed_tx.rawTransaction)
        
        return tx_hash.hex()
    
    def get_transaction(self, tx_hash: str) -> Dict[str, Any]:
        tx = self.web3.eth.get_transaction(tx_hash)
        receipt = self.web3.eth.get_transaction_receipt(tx_hash)
        
        return {
            'hash': tx_hash,
            'from': tx['from'],
            'to': tx['to'],
            'value': self.web3.from_wei(tx['value'], 'ether'),
            'blockNumber': tx['blockNumber'],
            'status': receipt['status'] if receipt else None
        }

# BEP20 (Binance Smart Chain)
class BSCWallet(EthereumWallet):
    def __init__(self, rpc_url: str = "https://bsc-dataseed.binance.org/"):
        super().__init__(rpc_url, chain_id=56)
    
    def send_bep20_token(self, private_key: str, token_address: str, to_address: str, amount: float):
        # ERC20 token transfer
        pass

# Polygon
class PolygonWallet(EthereumWallet):
    def __init__(self, rpc_url: str = "https://polygon-rpc.com"):
        super().__init__(rpc_url, chain_id=137)
