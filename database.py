import sqlite3
import json
from datetime import datetime

class Database:
    def __init__(self, db_path="wallets.db"):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.create_tables()
    
    def create_tables(self):
        cursor = self.conn.cursor()
        
        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Wallets table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS wallets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                network TEXT,
                currency TEXT,
                address TEXT UNIQUE,
                private_key TEXT,
                public_key TEXT,
                mnemonic TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        """)
        
        # Transactions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                tx_hash TEXT UNIQUE,
                from_address TEXT,
                to_address TEXT,
                amount REAL,
                currency TEXT,
                network TEXT,
                status TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        """)
        
        self.conn.commit()
    
    def add_user(self, user_id, username):
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)",
            (user_id, username)
        )
        self.conn.commit()
    
    def add_wallet(self, user_id, network, currency, address, private_key, public_key, mnemonic=None):
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO wallets (user_id, network, currency, address, private_key, public_key, mnemonic)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (user_id, network, currency, address, private_key, public_key, mnemonic))
        self.conn.commit()
        return cursor.lastrowid
    
    def get_user_wallets(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT id, network, currency, address, created_at 
            FROM wallets 
            WHERE user_id = ?
            ORDER BY created_at DESC
        """, (user_id,))
        return cursor.fetchall()
    
    def get_wallet_private_key(self, user_id, address):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT private_key FROM wallets 
            WHERE user_id = ? AND address = ?
        """, (user_id, address))
        result = cursor.fetchone()
        return result[0] if result else None
    
    def add_transaction(self, user_id, tx_hash, from_address, to_address, amount, currency, network, status="pending"):
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO transactions (user_id, tx_hash, from_address, to_address, amount, currency, network, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (user_id, tx_hash, from_address, to_address, amount, currency, network, status))
        self.conn.commit()
    
    def update_transaction_status(self, tx_hash, status):
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE transactions SET status = ? WHERE tx_hash = ?
        """, (status, tx_hash))
        self.conn.commit()
