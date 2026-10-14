import asyncio
import logging
import sys
from datetime import datetime

# Reconfigure stdout/stderr for Unicode (Khmer & emojis) on Windows consoles
if sys.platform == "win32":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")

from config import (
    TELEGRAM_BOT_TOKEN,
    SCHEDULE_SLOT_1,
    SCHEDULE_SLOT_2,
    SCHEDULE_SLOT_3
)
from database import init_db
from bot import create_bot_app
from scheduler import DAILY_SLOTS_CONFIG, broadcast_market_update
from research_engine import LogisticsResearchEngine

logging.basicConfig(
    format="%(asctime)s - [%(name)s] - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger("RUN_ALL")

async def run_scheduler_task(bot, research_engine):
    """Background scheduler task checking for the 3 daily dispatch slots."""
    logger.info("Background 3x/Day Scheduler task started inside unified runner.")
    last_broadcast_date = ""

    while True:
        try:
            now_str = datetime.now().strftime("%H:%M")
            today_str = datetime.now().strftime("%Y-%m-%d")

            if now_str in DAILY_SLOTS_CONFIG and last_broadcast_date != f"{today_str}_{now_str}":
                slot_info = DAILY_SLOTS_CONFIG[now_str]
                logger.info(f"Triggering {slot_info['label']} at {now_str} ICT!")
                await broadcast_market_update(bot, research_engine, category_filter=slot_info["filter"])
                last_broadcast_date = f"{today_str}_{now_str}"

            await asyncio.sleep(30)
        except Exception as e:
            logger.error(f"Error in background scheduler: {e}")
            await asyncio.sleep(60)

import os
from aiohttp import web

async def health_check(request):
    """Health check endpoint for Render Web Service."""
    return web.Response(text="Cambodia Logistics Bot is running 24/7!", status=200)

async def start_health_server():
    """Starts minimal HTTP server on PORT required by Render Web Service."""
    port = int(os.getenv("PORT", "10000"))
    app = web.Application()
    app.router.add_get("/", health_check)
    app.router.add_get("/healthz", health_check)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    logger.info(f"Health check HTTP server listening on port {port} for Render.")

async def main():
    init_db()

    if not TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN is not set in .env! Please configure it before starting.")
        return

    logger.info("Initializing Cambodia Logistics Telegram Bot & 24/7 Engine...")
    app = create_bot_app()
    research_engine = LogisticsResearchEngine()

    # Start HTTP health server for Render
    await start_health_server()

    async with app:
        await app.start()
        await app.updater.start_polling()
        logger.info("Telegram Bot Polling started.")
        logger.info(f"Scheduler active for: {SCHEDULE_SLOT_1} (Sea), {SCHEDULE_SLOT_2} (Trucking), {SCHEDULE_SLOT_3} (Air/Customs) ICT.")

        # Run scheduler concurrently
        scheduler_task = asyncio.create_task(run_scheduler_task(app.bot, research_engine))

        try:
            await scheduler_task
        except asyncio.CancelledError:
            pass
        finally:
            await app.updater.stop()
            await app.stop()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot process terminated safely.")
