from telethon import TelegramClient, events, Button
from telethon.errors import SessionPasswordNeededError
from config import Config
from database import Database
import asyncio
import json

# Import wallet classes
from wallets.ethereum import EthereumWallet, BSCWallet, PolygonWallet
from wallets.bitcoin import BitcoinWallet, LitecoinWallet
from wallets.tron import TronWallet

class WalletBot:
    def __init__(self):
        self.client = TelegramClient('wallet_bot', Config.API_ID, Config.API_HASH)
        self.db = Database()
        
        # Initialize wallet managers
        self.wallets = {
            'ETH': EthereumWallet(Config.ETH_RPC),
            'BSC': BSCWallet(Config.BSC_RPC),
            'MATIC': PolygonWallet(Config.POLYGON_RPC),
            'BTC': BitcoinWallet(),
            'LTC': LitecoinWallet(),
            'TRX': TronWallet(Config.TRON_RPC)
        }
        
        self.setup_handlers()
    
    def setup_handlers(self):
        @self.client.on(events.NewMessage(pattern='/start'))
        async def start_handler(event):
            user_id = event.sender_id
            username = event.sender.username
            self.db.add_user(user_id, username)
            
            await event.reply(
                "💰 **Crypto Wallet Bot**\n\n"
                "Available commands:\n"
                "/create - Create new wallet\n"
                "/wallets - View your wallets\n"
                "/balance - Check wallet balance\n"
                "/send - Send cryptocurrency\n"
                "/receive - Get deposit address\n"
                "/help - Show help message",
                buttons=[
                    [Button.inline("📱 Create Wallet", b"create_wallet"),
                     Button.inline("👛 My Wallets", b"view_wallets")],
                    [Button.inline("📤 Send Funds", b"send_funds"),
                     Button.inline("📥 Receive Funds", b"receive_funds")]
                ]
            )
        
        @self.client.on(events.CallbackQuery(pattern=b'create_wallet'))
        async def create_wallet_handler(event):
            await event.edit(
                "Select network:",
                buttons=[
                    [Button.inline("🟡 Bitcoin (BTC)", b"create_btc"),
                     Button.inline("🔶 Litecoin (LTC)", b"create_ltc")],
                    [Button.inline("🔷 Ethereum (ETH)", b"create_eth"),
                     Button.inline("🟡 BSC (BEP20)", b"create_bsc")],
                    [Button.inline("🟣 Polygon (MATIC)", b"create_matic"),
                     Button.inline("🔴 Tron (TRC20)", b"create_trx")],
                    [Button.inline("🔙 Back", b"main_menu")]
                ]
            )
        
        @self.client.on(events.CallbackQuery(pattern=b'create_(.*)'))
        async def create_specific_wallet(event):
            network = event.pattern_match.group(1).decode()
            user_id = event.sender_id
            username = event.sender.username
            
            network_map = {
                'btc': ('BTC', 'Bitcoin'),
                'ltc': ('LTC', 'Litecoin'),
                'eth': ('ETH', 'Ethereum'),
                'bsc': ('BSC', 'Binance Smart Chain'),
                'matic': ('MATIC', 'Polygon'),
                'trx': ('TRX', 'Tron')
            }
            
            currency, network_name = network_map.get(network, (network.upper(), network))
            
            # Create wallet
            wallet_manager = self.wallets.get(currency)
            if wallet_manager:
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
                
                # Send wallet info (careful with private key!)
                message = f"""
**✅ {network_name} Wallet Created!**

**Address:** `{wallet_data['address']}`
**Network:** {network_name} ({currency})

**⚠️ IMPORTANT SECURITY WARNING ⚠️**
- Keep your private key secret!
- Never share it with anyone
- Store it securely offline

**Private Key:** `{wallet_data['private_key']}`

Use /wallets to see all your wallets.
"""
                await event.edit(message)
            else:
                await event.edit("❌ Network not supported!")
        
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
        
        @self.client.on(events.NewMessage(pattern='/send'))
        async def send_handler(event):
            # This would be a multi-step process
            # For security, handle private keys carefully
            await event.reply(
                "Send cryptocurrency:\n\n"
                "1. Use /wallets to see your addresses\n"
                "2. PM me with format:\n"
                "`/sendfrom ADDRESS TO_ADDRESS AMOUNT CURRENCY`\n\n"
                "Example: `/sendfrom 0x... 0x... 0.1 ETH`\n\n"
                "⚠️ Make sure you have the private key for the sending address!"
            )
        
        @self.client.on(events.NewMessage(pattern=r'/sendfrom (.+) (.+) (.+) (.+)'))
        async def send_from_handler(event):
            try:
                _, from_address, to_address, amount_str, currency = event.pattern_match.groups()
                amount = float(amount_str)
                user_id = event.sender_id
                
                # Get private key from database
                private_key = self.db.get_wallet_private_key(user_id, from_address)
                
                if not private_key:
                    await event.reply("❌ Wallet not found or not owned by you!")
                    return
                
                # Send transaction
                wallet_manager = self.wallets.get(currency.upper())
                if wallet_manager:
                    tx_hash = wallet_manager.send_transaction(
                        private_key=private_key,
                        to_address=to_address,
                        amount=amount
                    )
                    
                    # Save transaction to database
                    self.db.add_transaction(
                        user_id=user_id,
                        tx_hash=tx_hash,
                        from_address=from_address,
                        to_address=to_address,
                        amount=amount,
                        currency=currency.upper(),
                        network=currency.upper()
                    )
                    
                    await event.reply(f"""
✅ **Transaction Sent!**

**Tx Hash:** `{tx_hash}`
**From:** `{from_address}`
**To:** `{to_address}`
**Amount:** {amount} {currency.upper()}

Track on block explorer.
""")
                else:
                    await event.reply("❌ Unsupported currency!")
            
            except Exception as e:
                await event.reply(f"❌ Error: {str(e)}")
        
        @self.client.on(events.NewMessage(pattern='/balance'))
        async def balance_handler(event):
            user_id = event.sender_id
            wallets = self.db.get_user_wallets(user_id)
            
            if not wallets:
                await event.reply("You don't have any wallets yet!")
                return
            
            message = "**💰 Wallet Balances:**\n\n"
            for wallet in wallets:
                wallet_id, network, currency, address, _ = wallet
                wallet_manager = self.wallets.get(currency)
                if wallet_manager:
                    try:
                        balance = wallet_manager.get_balance(address)
                        message += f"**{network} ({currency})**\n"
                        message += f"Address: `{address}`\n"
                        message += f"Balance: {balance:.6f} {currency}\n"
                        message += "─" * 30 + "\n"
                    except Exception as e:
                        message += f"**{network} ({currency})** - Error: {str(e)}\n"
            
            await event.reply(message)
    
    async def start(self):
        await self.client.start(bot_token=Config.BOT_TOKEN)
        print("Bot started!")
        await self.client.run_until_disconnected()

if __name__ == "__main__":
    bot = WalletBot()
    asyncio.run(bot.start())
