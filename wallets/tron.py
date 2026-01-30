from tronpy import Tron
from tronpy.providers import HTTPProvider
from .base import BaseWallet
from typing import Dict, Any, Optional

class TronWallet(BaseWallet):
    def __init__(self, rpc_url: str = "https://api.trongrid.io"):
        self.client = Tron(HTTPProvider(rpc_url))
    
    def create_wallet(self, mnemonic: Optional[str] = None) -> Dict[str, Any]:
        try:
            wallet = self.client.generate_address()
            return {
                'address': wallet['base58check_address'],
                'private_key': wallet['private_key'],
                'public_key': wallet.get('public_key', ''),
                'mnemonic': mnemonic
            }
        except Exception as e:
            raise Exception(f"Tron wallet creation error: {e}")
    
    def get_balance(self, address: str) -> float:
        try:
            account = self.client.get_account(address)
            balance = account.get('balance', 0)
            return balance / 1000000  # Convert sun to TRX
        except Exception as e:
            print(f"Tron balance error: {e}")
            return 0.0
    
    def send_transaction(self, private_key: str, to_address: str, amount: float, **kwargs) -> str:
        try:
            # Create sender from private key
            sender = self.client.generate_address(private_key)
            
            # Build transaction
            txn = (
                self.client.trx.transfer(
                    from_=sender['base58check_address'],
                    to=to_address,
                    amount=int(amount * 1000000)  # TRX to sun
                )
                .build()
                .sign(private_key)
            )
            
            # Broadcast
            result = txn.broadcast()
            return result.get('txid', '')
        except Exception as e:
            raise Exception(f"Tron send error: {e}")
    
    def get_transaction(self, tx_hash: str) -> Dict[str, Any]:
        try:
            txn = self.client.get_transaction(tx_hash)
            return dict(txn)
        except Exception as e:
            return {'error': str(e)}
