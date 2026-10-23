import asyncio
import logging
import sys
from datetime import datetime, timezone, timedelta
from typing import List

# Reconfigure stdout/stderr for Unicode on Windows consoles
if sys.platform == "win32":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")

from telegram import Bot, constants
from config import (
    TELEGRAM_BOT_TOKEN,
    TELEGRAM_CHANNEL_ID,
    SCHEDULE_SLOT_1,
    SCHEDULE_SLOT_2,
    SCHEDULE_SLOT_3,
    DEFAULT_LANGUAGE
)
from database import (
    init_db,
    get_subscribers,
    log_post,
    is_post_duplicate
)
from research_engine import LogisticsResearchEngine
from formatter import format_intelligence_post

logging.basicConfig(
    format="%(asctime)s - [SCHEDULER] - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Daily slots configured for 3 distinct market intelligence domains in English:
# 1. Morning (08:00 ICT): Ocean Freight & Port Operations (PAS / PPAP / Feeder Allocation)
# 2. Midday (13:30 ICT): Cross-Border Trucking, Expressway Haulage & Borders (Bavet / Poipet)
# 3. Evening (18:00 ICT): Air Cargo Express, Customs (GDCE), SEZ & Factory Logistics
DAILY_SLOTS_CONFIG = {
    SCHEDULE_SLOT_1: {"filter": "ocean", "label": "Morning Ocean & Port Dispatch"},
    SCHEDULE_SLOT_2: {"filter": "trucking", "label": "Midday Trucking & Expressway Dispatch"},
    SCHEDULE_SLOT_3: {"filter": "air", "label": "Evening Air Cargo & Customs Dispatch"}
}

ICT_TIMEZONE = timezone(timedelta(hours=7))

async def broadcast_market_update(bot: Bot, research_engine: LogisticsResearchEngine, category_filter: str = None):
    """
    Synthesizes the freshest intelligence briefing in English, promoting Honkai Logistics services,
    and broadcasts it with a verified action photo to the configured channel and active subscribers.
    Deduplicates recipients strictly to prevent sending duplicate posts.
    """
    logger.info(f"Generating scheduled market intelligence briefing (filter: {category_filter})...")
    briefing = await research_engine.get_latest_market_briefing(category_filter=category_filter)

    caption = format_intelligence_post(briefing, language_mode=DEFAULT_LANGUAGE)
    photo_url = briefing["photo_url"]

    # Target recipients: channel + active subscriber chats
    # Normalize to int (or str) so that string channel IDs and integer chat IDs merge in the set
    target_recipients = set()
    if TELEGRAM_CHANNEL_ID:
        try:
            target_recipients.add(int(TELEGRAM_CHANNEL_ID))
        except (ValueError, TypeError):
            target_recipients.add(str(TELEGRAM_CHANNEL_ID))

    subscribers = get_subscribers(only_active=True)
    for sub in subscribers:
        try:
            target_recipients.add(int(sub["chat_id"]))
        except (ValueError, TypeError):
            target_recipients.add(str(sub["chat_id"]))

    if not target_recipients:
        logger.warning("No subscribers or TELEGRAM_CHANNEL_ID configured for broadcast.")
        return

    logger.info(f"Broadcasting '{briefing['title_en']}' to {len(target_recipients)} distinct destination(s)...")
    success_count = 0

    for dest in target_recipients:
        try:
            if len(caption) <= 1024:
                await bot.send_photo(
                    chat_id=dest,
                    photo=photo_url,
                    caption=caption,
                    parse_mode=constants.ParseMode.HTML
                )
            else:
                short_header = (
                    f"🇰🇭 <b>HONKAI LOGISTICS | CAMBODIA FREIGHT DISPATCH</b>\n"
                    f"📌 <b>{briefing.get('category', 'Market Update')}</b>\n"
                    f"📸 <i>{briefing.get('photo_title', '')} ({briefing.get('photo_location', '')})</i>"
                )
                await bot.send_photo(
                    chat_id=dest,
                    photo=photo_url,
                    caption=short_header,
                    parse_mode=constants.ParseMode.HTML
                )
                await bot.send_message(
                    chat_id=dest,
                    text=caption,
                    parse_mode=constants.ParseMode.HTML,
                    disable_web_page_preview=True
                )
            success_count += 1
            await asyncio.sleep(0.5)
        except Exception as e:
            logger.error(f"Failed to broadcast photo to {dest}: {e}")
            # Fallback to pure text message if photo fails
            try:
                await bot.send_message(chat_id=dest, text=caption, parse_mode=constants.ParseMode.HTML, disable_web_page_preview=True)
                success_count += 1
            except Exception as e2:
                logger.error(f"Fallback text also failed for {dest}: {e2}")

    logger.info(f"Broadcast complete! Successfully sent to {success_count}/{len(target_recipients)} destinations.")

    # Record post in database
    log_post(
        hash_key=briefing["hash_key"],
        title=briefing["title_en"],
        category=briefing["category"],
        summary=briefing["summary_en"],
        content=caption,
        photo_url=photo_url,
        source_url="",
        tags=",".join(briefing.get("tags", [])),
        language=DEFAULT_LANGUAGE
    )

async def run_scheduler_loop():
    """Continuous scheduler loop running in background."""
    init_db()
    if not TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN is missing in .env! Cannot start scheduler.")
        return

    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    research_engine = LogisticsResearchEngine()
    logger.info("Cambodia Logistics Automated 3x/Day Scheduler initiated.")
    logger.info(f"• Slot 1 ({SCHEDULE_SLOT_1} ICT): Ocean Freight & Port Operations")
    logger.info(f"• Slot 2 ({SCHEDULE_SLOT_2} ICT): Cross-Border Trucking & Expressway")
    logger.info(f"• Slot 3 ({SCHEDULE_SLOT_3} ICT): Air Cargo & Customs/Factory Logistics")

    last_broadcast_date = ""

    while True:
        try:
            now_ict = datetime.now(ICT_TIMEZONE)
            now_str = now_ict.strftime("%H:%M")
            today_str = now_ict.strftime("%Y-%m-%d")

            # Check if current time matches any of the 3 daily slots
            if now_str in DAILY_SLOTS_CONFIG and last_broadcast_date != f"{today_str}_{now_str}":
                slot_info = DAILY_SLOTS_CONFIG[now_str]
                logger.info(f"Triggering {slot_info['label']} at {now_str} ICT!")
                await broadcast_market_update(bot, research_engine, category_filter=slot_info["filter"])
                last_broadcast_date = f"{today_str}_{now_str}"

            # Sleep 20 seconds between checks
            await asyncio.sleep(20)
        except Exception as e:
            logger.error(f"Error in scheduler loop: {e}")
            await asyncio.sleep(30)

if __name__ == "__main__":
    asyncio.run(run_scheduler_loop())
