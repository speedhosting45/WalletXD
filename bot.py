from telethon import TelegramClient, events, Button
from config import Config
from database import Database
import asyncio
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import wallet classes with error handling
try:
    from wallets.ethereum import EthereumWallet, BSCWallet, PolygonWallet
    from wallets.bitcoin import BitcoinWallet, LitecoinWallet
    from wallets.tron import TronWallet
    WALLETS_LOADED = True
except ImportError as e:
    print(f"Warning: Could not load some wallet modules: {e}")
    WALLETS_LOADED = False

class WalletBot:
    def __init__(self):
        self.client = TelegramClient('wallet_bot', Config.API_ID, Config.API_HASH)
        self.db = Database()
        
        # Initialize wallet managers
        self.wallets = {}
        if WALLETS_LOADED:
            try:
                self.wallets = {
                    'ETH': EthereumWallet(Config.ETH_RPC),
                    'BSC': BSCWallet(Config.BSC_RPC),
                    'MATIC': PolygonWallet(Config.POLYGON_RPC),
                    'BTC': BitcoinWallet(),
                    'LTC': LitecoinWallet(),
                    'TRX': TronWallet(Config.TRON_RPC)
                }
            except Exception as e:
                print(f"Error initializing wallets: {e}")
        
        self.setup_handlers()
    
    def setup_handlers(self):
        @self.client.on(events.NewMessage(pattern='/start'))
        async def start_handler(event):
            user_id = event.sender_id
            username = event.sender.username if event.sender.username else "unknown"
            self.db.add_user(user_id, username)
            
            await event.reply(
                "💰 **Crypto Wallet Bot**\n\n"
                "Available commands:\n"
                "/create - Create new wallet\n"
                "/wallets - View your wallets\n"
                "/balance - Check wallet balance\n"
                "/send - Send cryptocurrency\n"
                "/help - Show help message"
            )
        
        @self.client.on(events.NewMessage(pattern='/create'))
        async def create_handler(event):
            if not self.wallets:
                await event.reply("❌ Wallet services are currently unavailable. Please try again later.")
                return
            
            await event.reply(
                "Select network to create wallet:",
                buttons=[
                    [Button.inline("🟡 Bitcoin (BTC)", b"create_btc"),
                     Button.inline("🔶 Litecoin (LTC)", b"create_ltc")],
                    [Button.inline("🔷 Ethereum (ETH)", b"create_eth"),
                     Button.inline("🟡 BSC (BEP20)", b"create_bsc")],
                    [Button.inline("🟣 Polygon (MATIC)", b"create_matic"),
                     Button.inline("🔴 Tron (TRC20)", b"create_trx")],
                    [Button.inline("❌ Cancel", b"cancel")]
                ]
            )
        
        @self.client.on(events.CallbackQuery(pattern=b'create_(.*)'))
        async def create_specific_wallet(event):
            network_code = event.pattern_match.group(1).decode()
            user_id = event.sender_id
            username = event.sender.username if event.sender.username else "unknown"
            
            network_map = {
                'btc': ('BTC', 'Bitcoin'),
                'ltc': ('LTC', 'Litecoin'),
                'eth': ('ETH', 'Ethereum'),
                'bsc': ('BSC', 'Binance Smart Chain'),
                'matic': ('MATIC', 'Polygon'),
                'trx': ('TRX', 'Tron')
            }
            
            if network_code not in network_map:
                await event.edit("❌ Invalid network selection!")
                return
            
            currency, network_name = network_map[network_code]
            
            # Show creating message
            await event.edit(f"⏳ Creating {network_name} wallet...")
            
            try:
                wallet_manager = self.wallets.get(currency)
                if not wallet_manager:
                    await event.edit(f"❌ {network_name} wallet service not available!")
                    return
                
                # Create wallet
                wallet_data = wallet_manager.create_wallet()
                
                # Save to database
                self.db.add_wallet(
                    user_id=user_id,
                    network=network_name,
                    currency=currency,
                    address=wallet_data['address'],
                    private_key=wallet_data['private_key'],
                    public_key=wallet_data.get('public_key', ''),
                    mnemonic=wallet_data.get('mnemonic')
                )
                
                # Send wallet info
                message = f"""
**✅ {network_name} Wallet Created!**

**Address:** `{wallet_data['address']}`
**Network:** {network_name} ({currency})

**⚠️ IMPORTANT SECURITY WARNING ⚠️**
- Keep your private key secret!
- Never share it with anyone
- Store it securely offline
- This bot is for testing only

**Private Key:** `{wallet_data['private_key'][:20]}...` (truncated for security)

Use /wallets to see all your wallets.
"""
                await event.edit(message)
                
            except Exception as e:
                await event.edit(f"❌ Error creating wallet: {str(e)}")
        
        @self.client.on(events.NewMessage(pattern='/wallets'))
        async def wallets_handler(event):
            user_id = event.sender_id
            wallets = self.db.get_user_wallets(user_id)
            
            if not wallets:
                await event.reply("You don't have any wallets yet. Use /create to make one!")
                return
            
            message = "**📋 Your Wallets:**\n\n"
            for wallet in wallets:
                wallet_id, network, currency, address, created_at = wallet
                message += f"**{network} ({currency})**\n"
                message += f"Address: `{address}`\n"
                message += f"Created: {created_at}\n"
                message += "─" * 30 + "\n"
            
            await event.reply(message)
        
        @self.client.on(events.NewMessage(pattern='/balance'))
        async def balance_handler(event):
            user_id = event.sender_id
            wallets = self.db.get_user_wallets(user_id)
            
            if not wallets:
                await event.reply("You don't have any wallets yet!")
                return
            
            message = "**💰 Wallet Balances:**\n\n"
            total_processed = 0
            
            for wallet in wallets:
                wallet_id, network, currency, address, _ = wallet
                wallet_manager = self.wallets.get(currency)
                if wallet_manager:
                    try:
                        balance = wallet_manager.get_balance(address)
                        message += f"**{network} ({currency})**\n"
                        message += f"Address: `{address[:10]}...{address[-8:]}`\n"
                        message += f"Balance: {balance:.6f} {currency}\n"
                        message += "─" * 30 + "\n"
                        total_processed += 1
                    except Exception as e:
                        message += f"**{network} ({currency})** - Error: Could not fetch balance\n"
            
            if total_processed == 0:
                message += "❌ Could not fetch any balances. Please try again later."
            
            await event.reply(message)
        
        @self.client.on(events.NewMessage(pattern='/send'))
        async def send_handler(event):
            await event.reply(
                "⚠️ **Send Functionality** ⚠️\n\n"
                "For security reasons, direct sending is disabled in this version.\n"
                "To send funds:\n"
                "1. Export your private key using /export\n"
                "2. Use a secure wallet app\n\n"
                "Example secure wallets:\n"
                "- MetaMask (for ETH/BSC/Polygon)\n"
                "- Trust Wallet\n"
                "- Ledger/Trezor (hardware)\n"
                "- Electrum (for BTC/LTC)"
            )
        
        @self.client.on(events.NewMessage(pattern='/help'))
        async def help_handler(event):
            await event.reply(
                "🤖 **Wallet Bot Help**\n\n"
                "**Commands:**\n"
                "/start - Start the bot\n"
                "/create - Create new wallet\n"
                "/wallets - List your wallets\n"
                "/balance - Check balances\n"
                "/help - This message\n\n"
                "**Supported Networks:**\n"
                "• Bitcoin (BTC)\n"
                "• Litecoin (LTC)\n"
                "• Ethereum (ETH)\n"
                "• BSC (BEP20)\n"
                "• Polygon (MATIC)\n"
                "• Tron (TRC20)\n\n"
                "⚠️ **Security Notice:**\n"
                "This is a demo bot. Do not store real funds in these wallets!"
            )
        
        @self.client.on(events.CallbackQuery(pattern=b'cancel'))
        async def cancel_handler(event):
            await event.delete()
    
    async def start(self):
        try:
            await self.client.start(bot_token=Config.BOT_TOKEN)
            print("✅ Bot started successfully!")
            
            # Get bot info
            me = await self.client.get_me()
            print(f"🤖 Bot username: @{me.username}")
            print(f"🆔 Bot ID: {me.id}")
            
            await self.client.run_until_disconnected()
        except Exception as e:
            print(f"❌ Error starting bot: {e}")

if __name__ == "__main__":
    print("🚀 Starting Wallet Bot...")
    
    # Check required environment variables
    required_vars = ['API_ID', 'API_HASH', 'BOT_TOKEN']
    missing_vars = [var for var in required_vars if not getattr(Config, var, None)]
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("Please check your .env file")
        exit(1)
    
    bot = WalletBot()
    
    try:
        asyncio.run(bot.start())
    except KeyboardInterrupt:
        print("\n👋 Bot stopped by user")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
