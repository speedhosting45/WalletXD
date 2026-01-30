from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class BaseWallet(ABC):
    @abstractmethod
    def create_wallet(self) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def get_balance(self, address: str) -> float:
        pass
    
    @abstractmethod
    def send_transaction(self, private_key: str, to_address: str, amount: float) -> str:
        pass
    
    @abstractmethod
    def get_transaction(self, tx_hash: str) -> Dict[str, Any]:
        pass
