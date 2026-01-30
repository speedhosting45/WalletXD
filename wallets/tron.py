from tronpy import Tron
from tronpy.providers import HTTPProvider
from .base import BaseWallet

class TronWallet(BaseWallet):
    def __init__(self, rpc_url: str = "https://api.trongrid.io"):
        self.client = Tron(HTTPProvider(rpc_url))
    
    def create_wallet(self) -> Dict[str, Any]:
        wallet = self.client.generate_address()
        
        return {
            'address': wallet['base58check_address'],
            'private_key': wallet['private_key'],
            'public_key': wallet['public_key']
        }
    
    def get_balance(self, address: str) -> float:
        try:
            account = self.client.get_account(address)
            balance = account.get('balance', 0)
            return balance / 1000000  # Convert sun to TRX
        except:
            return 0.0
    
    def send_transaction(self, private_key: str, to_address: str, amount: float) -> str:
        sender = self.client.generate_address(private_key)
        
        txn = (
            self.client.trx.transfer(
                from_=sender['base58check_address'],
                to=to_address,
                amount=int(amount * 1000000)  # TRX to sun
            )
            .build()
            .sign(private_key)
        )
        
        result = txn.broadcast()
        return result['txid']
    
    def get_transaction(self, tx_hash: str) -> Dict[str, Any]:
        txn = self.client.get_transaction(tx_hash)
        return txn
