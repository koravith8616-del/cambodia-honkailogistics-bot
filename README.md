# 🇰🇭 Cambodia Logistics & Supply Chain Automated Telegram Bot
> **Trilingual Market Logistics Information & Real Action Photo Engine (Khmer | English | 中文)**  
> *Dedicated to Cambodian Factory Industries (GFT), Freight Forwarders, Logistics Providers, Airlines, Ocean Carriers, and Inland Transportation Fleets.*

---

## 🌐 Trilingual Support (Khmer, English & Chinese)

The bot generates and formats intelligence across three key languages in Cambodia's supply chain:
* 🇰🇭 **ភាសាខ្មែរ (Khmer):** For local Cambodian warehouse operators, port clearing staff, logistics coordinators, and drivers.
* 🇬🇧 **English:** For international freight forwarders, ocean carriers, airline GSAs, and foreign buyers.
* 🇨🇳 **中文 (Simplified Chinese):** For Chinese factory owners, GFT production managers, merchandisers, and procurement teams operating in Special Economic Zones (PPSEZ, Manhattan SEZ Bavet, Sihanoukville SEZ).

---

## ⏰ Automated 3x Daily Dispatches (3 Distinct Information Domains)

The bot automatically dispatches **three completely distinct intelligence reports per day** (Cambodia Time ICT / UTC+7), each paired with a verified real action photo:

| Slot & Time (ICT) | Domain Focus | Key Topics |
| :--- | :--- | :--- |
| **08:00 AM (Morning)** | 🚢 **Ocean Freight & Port Operations** | Sihanoukville Autonomous Port (**PAS**) and Phnom Penh Autonomous Port (**PPAP LM17**) berth wait times, feeder container ship turnaround, yard utilization, and Singapore/Cai Mep transshipment connections. |
| **13:30 PM (Midday)** | 🚛 **Cross-Border Trucking & Highways** | Phnom Penh–Sihanoukville Expressway container transit times, Bavet–Moc Bai (Vietnam) & Poipet (Thailand) border queue conditions, diesel fuel prices, and e-seal customs inspection lanes. |
| **18:00 PM (Evening)** | ✈️ **Air Cargo, Customs & Factory Logistics** | Phnom Penh Techo Airport (**TIA**) cargo flights & air rates ($/kg), GFT factory container stuffing cut-offs, GDCE ASYCUDA pre-clearance, and RCEP/Form D compliance. |

---

## 🖥️ Running 24/7 Without Stopping (Even When Your Computer Is Closed)

To ensure the bot and automated scheduler broadcast continuously even when your laptop or personal computer is turned off or closed:

### Method 1: Cloud Server / VPS with Docker (Recommended)
You can deploy the bot on a cheap cloud VPS (e.g. Google Cloud Compute Engine e2-micro Free Tier, DigitalOcean, Hetzner, or Linode):

1. **Clone or transfer the project folder to your VPS:**
   ```bash
   git clone <your-repo> cambodia-logistics-bot
   cd cambodia-logistics-bot
   ```
2. **Create your `.env` file:**
   ```bash
   cp .env.example .env
   nano .env  # Enter your TELEGRAM_BOT_TOKEN and TELEGRAM_CHANNEL_ID
   ```
3. **Start the bot with Docker Compose:**
   ```bash
   docker compose up -d --build
   ```
   > 🚀 The bot will run continuously in the background (`restart: always`), automatically recovering from server reboots.

### Method 2: Free Cloud Container Hosting (Render / Railway / Fly.io)
1. Push this repository to GitHub.
2. In **Render.com** or **Railway.app**, select **New Web Service / Background Worker**.
3. Connect your GitHub repository.
4. Add your Environment Variables:
   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_CHANNEL_ID`
   - `DEFAULT_LANGUAGE=trilingual`
5. The container will automatically build using the included `Dockerfile` and execute `python run_all.py` 24/7.

### Method 3: Local 24/7 Runner on Windows (If running on a dedicated office server)
Use the included unified runner `run_all.py` via Python:
```powershell
.\.venv\Scripts\python run_all.py
```

---

## 📂 Project Structure

```
cambodia-logistics-bot/
├── config.py              # Environment configuration & 3 daily dispatch slots
├── database.py            # SQLite database (subscribers, logs, rate indicators)
├── photo_curator.py       # Real action photo curation & URL validation
├── research_engine.py     # Trilingual intelligence aggregator + Google Gemini
├── formatter.py           # Trilingual HTML post formatter (Khmer, English & Chinese)
├── bot.py                 # Interactive Telegram Bot (PTB v22) & command handlers
├── scheduler.py           # Automated background broadcaster for 3x daily dispatches
├── run_all.py             # Unified 24/7 runner executing both Bot & Scheduler
├── test_runner.py         # Full integration test suite (Trilingual & 3x daily tests)
├── Dockerfile             # Production container definition for 24/7 cloud hosting
├── docker-compose.yml     # Docker Compose orchestration
├── requirements.txt       # Python dependencies
├── .env.example           # Configuration template
└── README.md              # Project documentation
```

---

## 📱 Bot Commands Directory

| Command | Description |
| :--- | :--- |
| `/start` | Interactive welcome menu with quick-access inline buttons |
| `/latest` | Instant trilingual market dispatch with verified real action photo |
| `/rates` | Ocean container rates, air freight index & diesel fuel benchmark |
| `/ports` | Sihanoukville (PAS) and Phnom Penh (PPAP) berth & container yard status |
| `/aircargo` | Phnom Penh airport freighter capacity, flights, and spot rates |
| `/trucking` | Expressway conditions, Bavet-Moc Bai & Poipet border queue updates |
| `/factories` | Garment/Footwear supply chain, container stuffing & SEZ dry ports |
| `/customs` | GDCE customs notices, ASYCUDA, CamDX, and RCEP/GSP trade rules |
| `/research <query>` | AI deep research on any specific logistics topic in Khmer, English & Chinese |
| `/subscribe` | Subscribe to automated 3x/day intelligence broadcasts |
| `/unsubscribe` | Opt out of automated broadcasts |
| `/lang` | Select preferred language (Trilingual, English, Khmer, or Chinese) |
