import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Telegram
    API_ID = int(os.getenv("API_ID"))
    API_HASH = os.getenv("API_HASH")
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    
    # Database
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///wallets.db")
    
    # RPC Endpoints
    ETH_RPC = os.getenv("ETH_RPC", "https://mainnet.infura.io/v3/YOUR_INFURA_KEY")
    BSC_RPC = os.getenv("BSC_RPC", "https://bsc-dataseed.binance.org/")
    POLYGON_RPC = os.getenv("POLYGON_RPC", "https://polygon-rpc.com")
    TRON_RPC = os.getenv("TRON_RPC", "https://api.trongrid.io")
    
    # Admin settings
    ADMIN_IDS = [int(id) for id in os.getenv("ADMIN_IDS", "").split(",") if id]
    
    # Transaction settings
    MIN_CONFIRMATIONS = int(os.getenv("MIN_CONFIRMATIONS", 3))
