from bitcoinlib.wallets import Wallet as BTCWallet
from bitcoinlib.services.services import Service
from .base import BaseWallet
from typing import Dict, Any, Optional

class BitcoinWallet(BaseWallet):
    def create_wallet(self, mnemonic: Optional[str] = None) -> Dict[str, Any]:
        try:
            if mnemonic:
                wallet = BTCWallet.create(keys=mnemonic, network='bitcoin')
            else:
                wallet = BTCWallet.create(network='bitcoin')
            
            key = wallet.get_key()
            return {
                'address': key.address,
                'private_key': key.key_private,
                'public_key': key.key_public,
                'wif': key.wif,
                'mnemonic': wallet.mnemonic
            }
        except Exception as e:
            raise Exception(f"Bitcoin wallet creation error: {e}")
    
    def get_balance(self, address: str) -> float:
        try:
            service = Service(network='bitcoin')
            balance = service.getbalance(address)
            return balance / 100000000  # Convert satoshis to BTC
        except Exception as e:
            print(f"Bitcoin balance error: {e}")
            return 0.0
    
    def send_transaction(self, private_key: str, to_address: str, amount: float, **kwargs) -> str:
        try:
            network = kwargs.get('network', 'bitcoin')
            wallet = BTCWallet.from_key(private_key, network=network)
            tx = wallet.send_to(to_address, amount)
            return tx.txid
        except Exception as e:
            raise Exception(f"Bitcoin send error: {e}")
    
    def get_transaction(self, tx_hash: str) -> Dict[str, Any]:
        return {'hash': tx_hash, 'note': 'Bitcoin transaction lookup not implemented'}

class LitecoinWallet(BitcoinWallet):
    def create_wallet(self, mnemonic: Optional[str] = None) -> Dict[str, Any]:
        if mnemonic:
            wallet = BTCWallet.create(keys=mnemonic, network='litecoin')
        else:
            wallet = BTCWallet.create(network='litecoin')
        
        key = wallet.get_key()
        return {
            'address': key.address,
            'private_key': key.key_private,
            'public_key': key.key_public,
            'wif': key.wif,
            'mnemonic': wallet.mnemonic
        }
    
    def get_balance(self, address: str) -> float:
        try:
            service = Service(network='litecoin')
            balance = service.getbalance(address)
            return balance / 100000000  # Convert litoshis to LTC
        except Exception as e:
            print(f"Litecoin balance error: {e}")
            return 0.0
