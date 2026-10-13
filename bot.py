import asyncio
import logging
import sys
from typing import Optional

# Reconfigure stdout/stderr for Unicode (Khmer & emojis) on Windows consoles
if sys.platform == "win32":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")


from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    constants
)
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    ChatMemberHandler,
    filters
)

from config import (
    TELEGRAM_BOT_TOKEN,
    TELEGRAM_CHANNEL_ID,
    ADMIN_USER_IDS,
    DEFAULT_LANGUAGE
)
from database import (
    init_db,
    add_subscriber,
    remove_subscriber,
    set_subscriber_language,
    get_subscribers,
    get_all_indicators,
    log_post,
    is_post_duplicate
)
from research_engine import LogisticsResearchEngine
from photo_curator import get_action_photo_for_topic
from formatter import (
    format_intelligence_post,
    format_rate_index,
    format_port_status,
    format_customs_guide,
    format_factory_supply_chain
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

research_engine = LogisticsResearchEngine()


def get_main_keyboard() -> InlineKeyboardMarkup:
    """Builds interactive inline keyboard for logistics portal."""
    keyboard = [
        [
            InlineKeyboardButton("🚨 Latest Market Briefing", callback_data="btn_latest"),
            InlineKeyboardButton("📈 Freight Rate Index", callback_data="btn_rates")
        ],
        [
            InlineKeyboardButton("⚓ Ports (PAS & PPAP)", callback_data="btn_ports"),
            InlineKeyboardButton("✈️ Air Cargo (TIA/PNH)", callback_data="btn_aircargo")
        ],
        [
            InlineKeyboardButton("🚛 Highway & Trucking", callback_data="btn_trucking"),
            InlineKeyboardButton("🏭 Factory Supply Chain", callback_data="btn_factories")
        ],
        [
            InlineKeyboardButton("📋 Customs & GDCE", callback_data="btn_customs"),
            InlineKeyboardButton("🌐 Switch Language", callback_data="btn_lang")
        ],
        [
            InlineKeyboardButton("🔔 Toggle Auto-Digest", callback_data="btn_subscribe")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


# ==============================================================================
# COMMAND HANDLERS
# ==============================================================================

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles /start command with interactive welcome and role selection."""
    user = update.effective_user
    chat = update.effective_chat
    
    # Save subscriber in database
    is_channel = chat.type in (constants.ChatType.CHANNEL, constants.ChatType.SUPERGROUP)
    add_subscriber(
        chat_id=chat.id,
        username=user.username if user else None,
        first_name=user.first_name if user else chat.title,
        is_channel=is_channel,
        language=DEFAULT_LANGUAGE
    )

    welcome_text = (
        f"🇰🇭 <b>CAMBODIA LOGISTICS MARKET INTELLIGENCE BOT</b>\n"
        f"<i>ព័ត៌មានភស្តុភារកម្ម ការដឹកជញ្ជូន និងទីផ្សារផ្គត់ផ្គង់កម្ពុជា</i>\n\n"
        f"Hello <b>{user.first_name if user else 'Logistics Professional'}</b>! Welcome to your automated logistics intelligence assistant.\n\n"
        f"<b>🎯 Designed for Cambodian Supply Chain Stakeholders:</b>\n"
        f"• 🏭 <b>Garment & Footwear Factories:</b> Export schedules, container cut-offs & fabric imports\n"
        f"• 📦 <b>Freight Forwarders & Brokers:</b> Feeder slot availability, carrier rates & GDCE customs\n"
        f"• 🚢 <b>Carriers & Shipping Lines:</b> Sihanoukville (PAS) & Phnom Penh (PPAP) berth updates\n"
        f"• ✈️ <b>Airlines & Air Freight GSAs:</b> Belly capacity, freighter flights & express rates\n"
        f"• 🚛 <b>Trucking Companies:</b> PP-Sihanoukville Expressway tolls, Bavet & Poipet border status\n\n"
        f"<i>Select an option below or type <code>/help</code> for quick commands:</i>"
    )

    await update.message.reply_html(
        welcome_text,
        reply_markup=get_main_keyboard(),
        disable_web_page_preview=True
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Provides help documentation on all bot features."""
    help_text = (
        "📚 <b>BOT COMMAND DIRECTORY / ការណែនាំពាក្យបញ្ជា</b>\n\n"
        "• <code>/latest</code> - Fresh market intelligence briefing with verified action photo\n"
        "• <code>/rates</code> - Ocean container, air cargo & diesel rate indices\n"
        "• <code>/ports</code> - Sihanoukville PAS & Phnom Penh PPAP operational status\n"
        "• <code>/aircargo</code> - Air freight rates, capacity & airport terminal status\n"
        "• <code>/trucking</code> - Expressway, Bavet-Moc Bai & Poipet trucking corridor\n"
        "• <code>/factories</code> - GFT manufacturing, raw material flows & SEZ dry ports\n"
        "• <code>/customs</code> - GDCE customs, ASYCUDA, CamDX & RCEP/GSP regulations\n"
        "• <code>/research [topic]</code> - On-demand AI deep research on any logistics question\n"
        "• <code>/subscribe</code> - Enable daily morning intelligence broadcast (08:00 AM ICT)\n"
        "• <code>/unsubscribe</code> - Stop automated scheduled broadcasts\n"
        "• <code>/lang</code> - Toggle language (Bilingual, English, Khmer)\n"
    )
    if update.effective_user and update.effective_user.id in ADMIN_USER_IDS:
        help_text += "\n<b>👑 Admin Commands:</b>\n• <code>/broadcast [text]</code> - Broadcast urgent alert\n"

    await update.message.reply_html(help_text)


async def send_briefing_response(bot, chat_id: int, briefing: dict, caption: str):
    """Safely sends briefing with photo handling Telegram's 1024-character caption limit."""
    photo_url = briefing.get("photo_url", "")
    if len(caption) <= 1024:
        try:
            await bot.send_photo(
                chat_id=chat_id,
                photo=photo_url,
                caption=caption,
                parse_mode=constants.ParseMode.HTML
            )
            return
        except Exception as e:
            logger.warning(f"send_photo failed ({e}), falling back to split delivery.")

    # When caption exceeds 1024 chars (common for Trilingual posts)
    short_header = (
        f"🇰🇭 <b>HONKAI CAMBODIA LOGISTICS DISPATCH</b>\n"
        f"📌 <b>{briefing.get('category', 'Market Update')}</b>\n"
        f"📸 <i>{briefing.get('photo_title', '')} ({briefing.get('photo_location', '')})</i>"
    )
    try:
        await bot.send_photo(
            chat_id=chat_id,
            photo=photo_url,
            caption=short_header,
            parse_mode=constants.ParseMode.HTML
        )
    except Exception:
        pass

    await bot.send_message(
        chat_id=chat_id,
        text=caption,
        parse_mode=constants.ParseMode.HTML,
        disable_web_page_preview=True
    )


async def latest_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sends the latest logistics intelligence update with a real action photo."""
    chat_id = update.effective_chat.id
    await context.bot.send_chat_action(chat_id=chat_id, action=constants.ChatAction.UPLOAD_PHOTO)

    briefing = await research_engine.get_latest_market_briefing()
    caption = format_intelligence_post(briefing, language_mode=DEFAULT_LANGUAGE)

    # Log to database
    log_post(
        hash_key=briefing["hash_key"],
        title=briefing["title_en"],
        category=briefing["category"],
        summary=briefing["summary_en"],
        content=caption,
        photo_url=briefing["photo_url"],
        source_url="",
        tags=",".join(briefing.get("tags", [])),
        language=DEFAULT_LANGUAGE
    )

    await send_briefing_response(context.bot, chat_id, briefing, caption)


async def rates_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Displays latest freight rate benchmarks."""
    indicators = get_all_indicators()
    message = format_rate_index(indicators)
    await update.message.reply_html(message)


async def ports_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Displays Sihanoukville (PAS) and Phnom Penh (PPAP) port conditions with action photo."""
    chat_id = update.effective_chat.id
    photo_info = get_action_photo_for_topic("ocean_port", "PAS PPAP container port")
    text = format_port_status()

    try:
        await context.bot.send_photo(
            chat_id=chat_id,
            photo=photo_info["url"],
            caption=text,
            parse_mode=constants.ParseMode.HTML
        )
    except Exception:
        await update.message.reply_html(text)


async def aircargo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Displays Air cargo freight intelligence with action photo."""
    chat_id = update.effective_chat.id
    briefing = await research_engine.get_latest_market_briefing(category_filter="air")
    photo_info = get_action_photo_for_topic("air_cargo", "air freight")
    caption = format_intelligence_post(briefing, language_mode=DEFAULT_LANGUAGE)

    try:
        await context.bot.send_photo(
            chat_id=chat_id,
            photo=photo_info["url"],
            caption=caption,
            parse_mode=constants.ParseMode.HTML
        )
    except Exception:
        await update.message.reply_html(caption)


async def trucking_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Displays Highway, border gates and trucking corridor updates."""
    chat_id = update.effective_chat.id
    briefing = await research_engine.get_latest_market_briefing(category_filter="trucking")
    photo_info = get_action_photo_for_topic("trucking_highway", "expressway border")
    caption = format_intelligence_post(briefing, language_mode=DEFAULT_LANGUAGE)

    try:
        await context.bot.send_photo(
            chat_id=chat_id,
            photo=photo_info["url"],
            caption=caption,
            parse_mode=constants.ParseMode.HTML
        )
    except Exception:
        await update.message.reply_html(caption)


async def customs_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Displays Customs GDCE procedures and trade compliance."""
    chat_id = update.effective_chat.id
    photo_info = get_action_photo_for_topic("customs_inspection", "customs scanner")
    text = format_customs_guide()

    try:
        await context.bot.send_photo(
            chat_id=chat_id,
            photo=photo_info["url"],
            caption=text,
            parse_mode=constants.ParseMode.HTML
        )
    except Exception:
        await update.message.reply_html(text)


async def factories_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Displays Factory supply chain & GFT manufacturing intelligence."""
    chat_id = update.effective_chat.id
    photo_info = get_action_photo_for_topic("factory_logistics", "factory garment stuffing")
    text = format_factory_supply_chain()

    try:
        await context.bot.send_photo(
            chat_id=chat_id,
            photo=photo_info["url"],
            caption=text,
            parse_mode=constants.ParseMode.HTML
        )
    except Exception:
        await update.message.reply_html(text)


async def research_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles /research [query] on-demand deep market research."""
    chat_id = update.effective_chat.id
    query = " ".join(context.args).strip() if context.args else ""
    if not query:
        await update.message.reply_html(
            "⚠️ <b>Please provide a research query:</b>\n"
            "<i>Example:</i> <code>/research Funan Techo Canal impact on barge costs</code>\n"
            "<i>Example:</i> <code>/research Sihanoukville port 14.5m draft deep berth completion date</code>\n"
            "<i>Example:</i> <code>/research Air cargo rate forecast for garment export Q4</code>"
        )
        return

    wait_msg = await update.message.reply_html(f"🔍 <b>Conducting deep research on:</b> <i>'{query}'</i>\n<i>Analyzing maritime, air, and customs data...</i>")
    await context.bot.send_chat_action(chat_id=chat_id, action=constants.ChatAction.TYPING)

    research_res = await research_engine.deep_research_topic(query)
    caption = format_intelligence_post(research_res, language_mode=DEFAULT_LANGUAGE)

    try:
        await wait_msg.delete()
    except Exception:
        pass

    try:
        await context.bot.send_photo(
            chat_id=chat_id,
            photo=research_res["photo_url"],
            caption=caption,
            parse_mode=constants.ParseMode.HTML
        )
    except Exception as e:
        logger.warning(f"Could not send research photo: {e}")
        await update.message.reply_html(caption)


async def subscribe_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Subscribes chat to daily logistics digests."""
    chat = update.effective_chat
    user = update.effective_user
    add_subscriber(chat.id, user.username if user else None, user.first_name if user else chat.title)
    await update.message.reply_html(
        "✅ <b>Subscribed to Cambodia Logistics Daily Intelligence!</b>\n"
        "You will automatically receive daily morning market briefings (08:00 AM ICT) and urgent operational alerts."
    )


async def unsubscribe_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Unsubscribes chat from automated broadcasts."""
    remove_subscriber(update.effective_chat.id)
    await update.message.reply_html("🔕 <b>You have unsubscribed from automated digests.</b> You can still use on-demand commands anytime!")


async def lang_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Allows user to select language preference."""
    keyboard = [
        [
            InlineKeyboardButton("🌐 🇰🇭+🇬🇧+🇨🇳 Trilingual (Khmer, English & Chinese)", callback_data="lang_trilingual"),
        ],
        [
            InlineKeyboardButton("🇬🇧 English Only", callback_data="lang_en"),
            InlineKeyboardButton("🇰🇭 ភាសាខ្មែរ (Khmer)", callback_data="lang_km")
        ],
        [
            InlineKeyboardButton("🇨🇳 简体中文 (Chinese Only)", callback_data="lang_zh")
        ]
    ]
    await update.message.reply_html(
        "🌐 <b>Select Preferred Content Language / ជ្រើសរើសភាសា / 语言偏好设置：</b>",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# ==============================================================================
# INLINE CALLBACK HANDLERS
# ==============================================================================

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles button callbacks from interactive menus."""
    query = update.callback_query
    await query.answer()

    data = query.data
    chat_id = update.effective_chat.id

    if data == "btn_latest":
        briefing = await research_engine.get_latest_market_briefing()
        caption = format_intelligence_post(briefing, language_mode=DEFAULT_LANGUAGE)
        await send_briefing_response(context.bot, chat_id, briefing, caption)

    elif data == "btn_rates":
        indicators = get_all_indicators()
        await query.message.reply_html(format_rate_index(indicators))

    elif data == "btn_ports":
        photo_info = get_action_photo_for_topic("ocean_port", "port")
        text = format_port_status()
        try:
            await context.bot.send_photo(chat_id=chat_id, photo=photo_info["url"], caption=text, parse_mode=constants.ParseMode.HTML)
        except Exception:
            await query.message.reply_html(text)

    elif data == "btn_aircargo":
        briefing = await research_engine.get_latest_market_briefing(category_filter="air")
        caption = format_intelligence_post(briefing, language_mode=DEFAULT_LANGUAGE)
        await send_briefing_response(context.bot, chat_id, briefing, caption)

    elif data == "btn_trucking":
        briefing = await research_engine.get_latest_market_briefing(category_filter="trucking")
        caption = format_intelligence_post(briefing, language_mode=DEFAULT_LANGUAGE)
        await send_briefing_response(context.bot, chat_id, briefing, caption)

    elif data == "btn_factories":
        photo_info = get_action_photo_for_topic("factory_logistics", "factory")
        text = format_factory_supply_chain()
        try:
            await context.bot.send_photo(chat_id=chat_id, photo=photo_info["url"], caption=text, parse_mode=constants.ParseMode.HTML)
        except Exception:
            await query.message.reply_html(text)

    elif data == "btn_customs":
        photo_info = get_action_photo_for_topic("customs_inspection", "customs")
        text = format_customs_guide()
        try:
            await context.bot.send_photo(chat_id=chat_id, photo=photo_info["url"], caption=text, parse_mode=constants.ParseMode.HTML)
        except Exception:
            await query.message.reply_html(text)

    elif data == "btn_lang":
        keyboard = [
            [
                InlineKeyboardButton("🌐 🇰🇭+🇬🇧+🇨🇳 Trilingual (Khmer, English & Chinese)", callback_data="lang_trilingual"),
            ],
            [
                InlineKeyboardButton("🇬🇧 English Only", callback_data="lang_en"),
                InlineKeyboardButton("🇰🇭 ភាសាខ្មែរ (Khmer)", callback_data="lang_km")
            ],
            [
                InlineKeyboardButton("🇨🇳 简体中文 (Chinese Only)", callback_data="lang_zh")
            ]
        ]
        await query.message.reply_html(
            "🌐 <b>Select Preferred Content Language / ជ្រើសរើសភាសា / 语言偏好设置：</b>",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif data == "btn_subscribe":
        add_subscriber(chat_id, None, None)
        await query.message.reply_html("🔔 <b>Notification preference updated:</b> You are actively subscribed to automated market intelligence digests!")

    elif data.startswith("lang_"):
        chosen_lang = data.split("_")[1]
        set_subscriber_language(chat_id, chosen_lang)
        await query.edit_message_text(f"✅ Language updated to <b>{chosen_lang.upper()}</b>.", parse_mode=constants.ParseMode.HTML)


# ==============================================================================
# ==============================================================================
# CHANNEL & GROUP AUTO-DISCOVERY HANDLERS
# ==============================================================================

async def my_chat_member_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Automatically registers the channel or group when the bot is added/promoted as admin."""
    chat = update.effective_chat
    if not update.my_chat_member:
        return
    new_member = update.my_chat_member.new_chat_member
    if new_member.status in (constants.ChatMemberStatus.ADMINISTRATOR, constants.ChatMemberStatus.MEMBER):
        logger.info(f"Bot joined {chat.type} '{chat.title}' (ID: {chat.id})! Auto-registering for dispatches...")
        add_subscriber(
            chat_id=chat.id,
            username=chat.username,
            first_name=chat.title,
            is_channel=True,
            language=DEFAULT_LANGUAGE
        )
        try:
            welcome_dispatch = (
                f"🇰🇭 <b>HONKAI CAMBODIA LOGISTICS DISPATCH LINKED</b>\n"
                f"✅ This {chat.type} is now connected! It will receive <b>3x Daily Automated Logistics Briefings</b> with real action photos (08:00 Sea, 13:30 Trucking, 18:00 Air/Customs ICT) in Khmer, English & Chinese."
            )
            await context.bot.send_message(chat_id=chat.id, text=welcome_dispatch, parse_mode=constants.ParseMode.HTML)
        except Exception as e:
            logger.warning(f"Could not send welcome post to {chat.id}: {e}")

async def channel_post_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Auto-detects channel ID whenever any message appears in the channel."""
    chat = update.effective_chat
    if chat and chat.type == constants.ChatType.CHANNEL:
        add_subscriber(
            chat_id=chat.id,
            username=chat.username,
            first_name=chat.title,
            is_channel=True,
            language=DEFAULT_LANGUAGE
        )

async def post_now_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Instantly triggers an automated market intelligence dispatch with real action photo."""
    chat_id = update.effective_chat.id
    briefing = await research_engine.get_latest_market_briefing()
    caption = format_intelligence_post(briefing, language_mode=DEFAULT_LANGUAGE)
    await send_briefing_response(context.bot, chat_id, briefing, caption)

async def forward_link_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Detects forwarded messages from channels or groups and links them automatically."""
    msg = update.effective_message
    if not msg:
        return
    
    target_chat = None
    if getattr(msg, "forward_from_chat", None):
        target_chat = msg.forward_from_chat
    elif getattr(msg, "forward_origin", None) and hasattr(msg.forward_origin, "chat"):
        target_chat = msg.forward_origin.chat
        
    if target_chat:
        chat_id = target_chat.id
        title = target_chat.title or "Linked Channel/Group"
        username = target_chat.username
        logger.info(f"Forwarded from {target_chat.type} '{title}' (ID: {chat_id})! Linking...")
        add_subscriber(
            chat_id=chat_id,
            username=username,
            first_name=title,
            is_channel=True,
            language=DEFAULT_LANGUAGE
        )
        await msg.reply_html(
            f"🎉 <b>SUCCESS! Connected:</b> <i>{title}</i> (ID: <code>{chat_id}</code>)\n\n"
            f"🚀 <b>Now posting the live market dispatch with real action photo directly into {title}...</b>"
        )
        briefing = await research_engine.get_latest_market_briefing()
        caption = format_intelligence_post(briefing, language_mode=DEFAULT_LANGUAGE)
        try:
            await send_briefing_response(context.bot, chat_id, briefing, caption)
            await msg.reply_html(f"✅ <b>Successfully posted live dispatch to {title}!</b> Check your channel/group now!")
        except Exception as e:
            await msg.reply_html(
                f"⚠️ Could not post to {title}: <code>{e}</code>\n"
                f"<i>Please ensure @Honkai_Cambodia_Logistics_bot is an Administrator in {title} with 'Post Messages' enabled!</i>"
            )

async def link_channel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Manual link command: /link @channel_name or /link -100xxxx"""
    msg = update.effective_message
    args = context.args
    if not args:
        await msg.reply_html(
            "ℹ️ <b>How to link your Channel or Group:</b>\n\n"
            "<b>Method 1 (Easiest):</b> Just <b>Forward any message</b> from your channel/group into this chat!\n"
            "<b>Method 2:</b> Type <code>/link @YourChannelUsername</code>"
        )
        return
    
    target = args[0].strip()
    try:
        chat = await context.bot.get_chat(target)
        add_subscriber(
            chat_id=chat.id,
            username=chat.username,
            first_name=chat.title,
            is_channel=True,
            language=DEFAULT_LANGUAGE
        )
        await msg.reply_html(f"✅ <b>Connected:</b> <i>{chat.title}</i> (ID: <code>{chat.id}</code>)\nPublishing test dispatch...")
        briefing = await research_engine.get_latest_market_briefing()
        caption = format_intelligence_post(briefing, language_mode=DEFAULT_LANGUAGE)
        await send_briefing_response(context.bot, chat.id, briefing, caption)
        await msg.reply_html(f"🎉 <b>Successfully posted into {chat.title}!</b>")
    except Exception as e:
        await msg.reply_html(f"⚠️ Error connecting {target}: <code>{e}</code>\nEnsure the bot is added as Administrator first!")


# ==============================================================================
# BOT FACTORY / INITIALIZATION
# ==============================================================================

def create_bot_app() -> Application:
    """Builds and configures the Telegram Application instance."""
    init_db()

    if not TELEGRAM_BOT_TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN is not configured! Please provide it in .env or environment variable.")

    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Register command handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("latest", latest_command))
    app.add_handler(CommandHandler("rates", rates_command))
    app.add_handler(CommandHandler("ports", ports_command))
    app.add_handler(CommandHandler("aircargo", aircargo_command))
    app.add_handler(CommandHandler("trucking", trucking_command))
    app.add_handler(CommandHandler("customs", customs_command))
    app.add_handler(CommandHandler("factories", factories_command))
    app.add_handler(CommandHandler("research", research_command))
    app.add_handler(CommandHandler("subscribe", subscribe_command))
    app.add_handler(CommandHandler("unsubscribe", unsubscribe_command))
    app.add_handler(CommandHandler("lang", lang_command))
    app.add_handler(CommandHandler("post_now", post_now_command))
    app.add_handler(CommandHandler("link", link_channel_command))

    # Auto-link channels and groups (via ChatMember update, channel posts, or forwarded messages)
    app.add_handler(ChatMemberHandler(my_chat_member_handler, ChatMemberHandler.MY_CHAT_MEMBER))
    app.add_handler(MessageHandler(filters.ChatType.CHANNEL, channel_post_handler))
    app.add_handler(MessageHandler(filters.FORWARDED, forward_link_handler))

    # Register inline callbacks
    app.add_handler(CallbackQueryHandler(callback_handler))

    return app

if __name__ == "__main__":
    init_db()
    if not TELEGRAM_BOT_TOKEN:
        print("[!] TELEGRAM_BOT_TOKEN is not set. Please set it in .env before running the live polling bot.")
        print("[!] You can test all research, photo selection, and post formatting by running: python test_runner.py")
    else:
        print("[*] Starting Cambodia Logistics Telegram Bot in Polling Mode...")
        app = create_bot_app()
        app.run_polling()
