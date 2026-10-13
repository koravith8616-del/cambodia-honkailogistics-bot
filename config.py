import os
from pathlib import Path
from dotenv import load_dotenv

# Base directory
BASE_DIR = Path(__file__).resolve().parent

# Load .env if present
load_dotenv(BASE_DIR / ".env")

# Telegram Bot Config
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
TELEGRAM_CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID", "").strip()

# Admin IDs (comma-separated integers)
_raw_admins = os.getenv("ADMIN_USER_IDS", "").strip()
ADMIN_USER_IDS = [int(uid.strip()) for uid in _raw_admins.split(",") if uid.strip().isdigit()]

# Gemini API Key for AI synthesis & deep research
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()

# Broadcast schedule & preferences (Cambodia Time ICT / UTC+7)
# 3 distinct times per day with 3 different intelligence domains:
# Slot 1 (08:00 AM ICT): Ocean & Port Operations (Sihanoukville PAS / PPAP)
# Slot 2 (13:30 PM ICT): Cross-Border Trucking, Expressway & Borders (Bavet / Poipet)
# Slot 3 (18:00 PM ICT): Air Cargo, Factory GFT Logistics & GDCE Customs Compliance
SCHEDULE_SLOT_1 = os.getenv("SCHEDULE_SLOT_1", "14:30").strip()
SCHEDULE_SLOT_2 = os.getenv("SCHEDULE_SLOT_2", "17:00").strip()
SCHEDULE_SLOT_3 = os.getenv("SCHEDULE_SLOT_3", "19:00").strip()

# Default language: "trilingual" (Khmer + English + Chinese), "en", "km", or "zh"
DEFAULT_LANGUAGE = os.getenv("DEFAULT_LANGUAGE", "trilingual").lower()


# Database Path
DB_PATH = BASE_DIR / os.getenv("DB_PATH", "cambodia_logistics.db")

# Cambodia Logistics Hubs & Topics
LOGISTICS_HUBS = {
    "PAS": "Sihanoukville Autonomous Port (កំពង់ផែស្វយ័តក្រុងព្រះសីហនុ)",
    "PPAP": "Phnom Penh Autonomous Port / LM17 (កំពង់ផែស្វយ័តភ្នំពេញ)",
    "TIA": "Techo International Airport Cargo Hub (អាកាសយានដ្ឋានអន្តរជាតិតេជោ)",
    "SAI": "Siem Reap-Angkor International Airport Cargo",
    "BAVET": "Bavet - Moc Bai Border Corridor (ច្រកទ្វារព្រំដែនបាវិត-ម៉ុកបាយ)",
    "POIPET": "Poipet - Aranyaprathet Border Corridor (ច្រកទ្វារប៉ោយប៉ែត)",
    "EXPRESSWAY": "Phnom Penh - Sihanoukville Expressway (ផ្លូវល្បឿនលឿន)",
    "FUNAN": "Funan Techo Canal Project (ព្រែកជីកហ្វូណនតេជោ)"
}

TARGET_SECTORS = [
    "Garment, Footwear & Travel Goods (GFT) Factories",
    "International & Local Freight Forwarders (CAMFFA)",
    "Ocean Container Shipping Lines & Feeder Operators",
    "Air Cargo Carriers & GSAs",
    "Cross-border & Inland Trucking Fleets",
    "Special Economic Zones (SEZs: Phnom Penh, Bavet, Sihanoukville)",
    "Customs Brokers & GDCE Regulatory Compliance"
]
