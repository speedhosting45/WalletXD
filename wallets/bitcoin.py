from bitcoinlib.wallets import Wallet as BTCWallet
from bitcoinlib.services.services import Service
from .base import BaseWallet

class BitcoinWallet(BaseWallet):
    def create_wallet(self, network='bitcoin') -> Dict[str, Any]:
        wallet = BTCWallet.create(network=network)
        
        return {
            'address': wallet.get_key().address,
            'private_key': wallet.get_key().key_private,
            'public_key': wallet.get_key().key_public,
            'wif': wallet.get_key().wif,
            'mnemonic': wallet.mnemonic
        }
    
    def get_balance(self, address: str, network='bitcoin') -> float:
        service = Service(network=network)
        balance = service.getbalance(address)
        return balance / 100000000  # Convert satoshis to BTC
    
    def send_transaction(self, private_key: str, to_address: str, amount: float, network='bitcoin') -> str:
        # Note: bitcoinlib requires more complex transaction building
        # This is a simplified version
        wallet = BTCWallet.from_key(private_key, network=network)
        tx = wallet.send_to(to_address, amount)
        return tx.txid

class LitecoinWallet(BitcoinWallet):
    def create_wallet(self) -> Dict[str, Any]:
        return super().create_wallet(network='litecoin')
    
    def get_balance(self, address: str) -> float:
        return super().get_balance(address, network='litecoin')
    
    def send_transaction(self, private_key: str, to_address: str, amount: float) -> str:
        return super().send_transaction(private_key, to_address, amount, network='litecoin')
