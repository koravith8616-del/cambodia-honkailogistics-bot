import sqlite3
import datetime
from typing import List, Dict, Optional, Any
from config import DB_PATH

def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes the database schema if not already present."""
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # Subscribers table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS subscribers (
                chat_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                sector TEXT DEFAULT 'All Logistics',
                language TEXT DEFAULT 'bilingual',
                is_channel INTEGER DEFAULT 0,
                is_active INTEGER DEFAULT 1,
                joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Intelligence Posts log & deduplication
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS intelligence_posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                hash_key TEXT UNIQUE,
                title TEXT,
                category TEXT,
                summary TEXT,
                content TEXT,
                photo_url TEXT,
                source_url TEXT,
                tags TEXT,
                language TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Market Rates & Operational Indicators
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS market_indicators (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                indicator_key TEXT UNIQUE,
                indicator_name TEXT,
                category TEXT,
                current_value TEXT,
                previous_value TEXT,
                change_pct REAL,
                unit TEXT,
                status_trend TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Prepopulate baseline market indicators if empty
        cursor.execute("SELECT COUNT(*) as cnt FROM market_indicators")
        if cursor.fetchone()["cnt"] == 0:
            sample_indicators = [
                ("ocean_asia_uswc", "Ocean Freight (Asia - US West Coast / FEU)", "Sea Freight", "$2,850", "$3,100", -8.06, "USD/FEU", "DECREASING"),
                ("ocean_asia_usec", "Ocean Freight (Asia - US East Coast / FEU)", "Sea Freight", "$4,200", "$4,450", -5.61, "USD/FEU", "DECREASING"),
                ("ocean_asia_eu", "Ocean Freight (Asia - Northern Europe / TEU)", "Sea Freight", "$2,100", "$2,050", 2.44, "USD/TEU", "STABLE"),
                ("feeder_pas_sg", "Feeder Sihanoukville (PAS) - Singapore (TEU)", "Feeder / Sea", "$260", "$250", 4.0, "USD/TEU", "STABLE"),
                ("feeder_ppap_caimep", "Barge Phnom Penh (PPAP) - Cai Mep (TEU)", "Barge / Feeder", "$190", "$190", 0.0, "USD/TEU", "NORMAL"),
                ("air_pnh_us", "Air Cargo (Phnom Penh - US West Coast)", "Air Freight", "$4.85", "$5.10", -4.9, "USD/KG", "NORMAL"),
                ("air_pnh_eu", "Air Cargo (Phnom Penh - Europe Hubs)", "Air Freight", "$3.95", "$4.05", -2.47, "USD/KG", "NORMAL"),
                ("trucking_pp_sihanoukville", "Expressway Container Trucking (PP - PAS)", "Trucking", "$220", "$220", 0.0, "USD/40ft", "NORMAL"),
                ("diesel_cambodia", "Cambodia Commercial Diesel Retail Price", "Fuel / Energy", "$1.02", "$1.01", 0.99, "USD/Liter", "STABLE")
            ]
            cursor.executemany("""
                INSERT OR IGNORE INTO market_indicators 
                (indicator_key, indicator_name, category, current_value, previous_value, change_pct, unit, status_trend)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, sample_indicators)
            
        conn.commit()

# --- Subscriber Management ---
def add_subscriber(chat_id: int, username: Optional[str], first_name: Optional[str], is_channel: bool = False, sector: str = "All Logistics", language: str = "bilingual"):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO subscribers (chat_id, username, first_name, sector, language, is_channel, is_active, last_active)
            VALUES (?, ?, ?, ?, ?, ?, 1, CURRENT_TIMESTAMP)
            ON CONFLICT(chat_id) DO UPDATE SET
                username = excluded.username,
                first_name = excluded.first_name,
                is_active = 1,
                last_active = CURRENT_TIMESTAMP
        """, (chat_id, username, first_name, sector, language, 1 if is_channel else 0))
        conn.commit()

def remove_subscriber(chat_id: int):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE subscribers SET is_active = 0 WHERE chat_id = ?", (chat_id,))
        conn.commit()

def set_subscriber_language(chat_id: int, language: str):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE subscribers SET language = ? WHERE chat_id = ?", (language, chat_id))
        conn.commit()

def get_subscribers(only_active: bool = True) -> List[Dict[str, Any]]:
    with get_connection() as conn:
        cursor = conn.cursor()
        if only_active:
            cursor.execute("SELECT * FROM subscribers WHERE is_active = 1")
        else:
            cursor.execute("SELECT * FROM subscribers")
        return [dict(row) for row in cursor.fetchall()]

# --- Post Logging & Deduplication ---
def is_post_duplicate(hash_key: str) -> bool:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM intelligence_posts WHERE hash_key = ?", (hash_key,))
        return cursor.fetchone() is not None

def log_post(hash_key: str, title: str, category: str, summary: str, content: str, photo_url: str, source_url: str, tags: str, language: str):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR IGNORE INTO intelligence_posts 
            (hash_key, title, category, summary, content, photo_url, source_url, tags, language)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (hash_key, title, category, summary, content, photo_url, source_url, tags, language))
        conn.commit()

# --- Market Indicators ---
def get_all_indicators() -> List[Dict[str, Any]]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM market_indicators ORDER BY category, id")
        return [dict(row) for row in cursor.fetchall()]

def update_indicator(key: str, current_val: str, prev_val: str, change_pct: float, trend: str):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE market_indicators
            SET current_value = ?, previous_value = ?, change_pct = ?, status_trend = ?, updated_at = CURRENT_TIMESTAMP
            WHERE indicator_key = ?
        """, (current_val, prev_val, change_pct, trend, key))
        conn.commit()
