import html
from typing import Dict, List, Any

def format_intelligence_post(item: Dict[str, Any], language_mode: str = "trilingual") -> str:
    """
    Formats an intelligence report into an executive Telegram HTML message.
    Supports trilingual (English + Khmer + Chinese), English only, Khmer only, or Chinese only.
    """
    category = html.escape(item.get("category", "Market Logistics"))
    title_en = html.escape(item.get("title_en", ""))
    title_km = html.escape(item.get("title_km", ""))
    title_zh = html.escape(item.get("title_zh", ""))
    
    summary_en = html.escape(item.get("summary_en", ""))
    summary_km = html.escape(item.get("summary_km", ""))
    summary_zh = html.escape(item.get("summary_zh", ""))
    
    cambodia_impact = html.escape(item.get("cambodia_impact", ""))
    cambodia_impact_zh = html.escape(item.get("cambodia_impact_zh", ""))
    
    action_rec = html.escape(item.get("action_recommendation", ""))
    action_rec_zh = html.escape(item.get("action_recommendation_zh", ""))
    
    photo_title = html.escape(item.get("photo_title", ""))
    photo_loc = html.escape(item.get("photo_location", ""))
    photo_credit = html.escape(item.get("photo_credit", ""))
    source = html.escape(item.get("source", "Cambodia Logistics Intelligence"))
    timestamp = html.escape(item.get("timestamp", ""))

    tags = " ".join([f"<b>{t}</b>" for t in item.get("tags", [])])

    lines = []
    
    # Category Banner & Header
    lines.append(f"🇰🇭 <b>CAMBODIA LOGISTICS MARKET INTELLIGENCE</b>")
    lines.append(f"⚡ <b>Executive Briefing</b> | 📌 <b>{category}</b> | 🕒 <i>{timestamp}</i>")
    lines.append("────────────────────────────")

    # Titles based on language mode
    if language_mode in ("trilingual", "bilingual", "en") and title_en:
        lines.append(f"🇬🇧 <b>{title_en}</b>")
    if language_mode in ("trilingual", "bilingual", "km") and title_km:
        lines.append(f"🇰🇭 <b>{title_km}</b>")
    if language_mode in ("trilingual", "zh") and title_zh:
        lines.append(f"🇨🇳 <b>{title_zh}</b>")
    lines.append("")

    # Action Photo Context
    if photo_title:
        lines.append(f"📸 <b>Verified Operations:</b> <i>{photo_title}</i>")
        if photo_loc:
            lines.append(f"📍 <i>{photo_loc} ({photo_credit})</i>")
        lines.append("")

    # Executive Summary
    lines.append("📢 <b>KEY TAKEAWAYS / សេចក្តីសង្ខេប / 核心要闻:</b>")
    if language_mode in ("trilingual", "bilingual", "en") and summary_en:
        lines.append(f"🇬🇧 • {summary_en}")
    if language_mode in ("trilingual", "bilingual", "km") and summary_km:
        lines.append(f"🇰🇭 • {summary_km}")
    if language_mode in ("trilingual", "zh") and summary_zh:
        lines.append(f"🇨🇳 • {summary_zh}")
    lines.append("")

    # Key Data Points
    key_data = item.get("key_data", [])
    if key_data:
        lines.append("📊 <b>LIVE FREIGHT & PORT METRICS / សូចនាករសំខាន់ៗ / 核心指标:</b>")
        for dp in key_data:
            lines.append(f"  ▪️ <code>{html.escape(str(dp))}</code>")
        lines.append("")

    # Cambodia Factory & Trade Impact
    if cambodia_impact or cambodia_impact_zh:
        lines.append("🏭 <b>SUPPLY CHAIN IMPACT / ផលប៉ះពាល់ខ្សែច្រវាក់ផ្គត់ផ្គង់ / 产业影响:</b>")
        if language_mode in ("trilingual", "bilingual", "en") and cambodia_impact:
            lines.append(f"🇬🇧 {cambodia_impact}")
        if language_mode in ("trilingual", "zh") and cambodia_impact_zh:
            lines.append(f"🇨🇳 {cambodia_impact_zh}")
        lines.append("")

    # Forwarder & Shipper Action Plan
    if action_rec or action_rec_zh:
        lines.append("💡 <b>EXECUTIVE ACTION PLAN / អនុសាសន៍ប្រតិបត្តិការ / 应对建议:</b>")
        if language_mode in ("trilingual", "bilingual", "en") and action_rec:
            lines.append(f"🇬🇧 🎯 {action_rec}")
        if language_mode in ("trilingual", "zh") and action_rec_zh:
            lines.append(f"🇨🇳 🎯 {action_rec_zh}")
        lines.append("")

    # Footer & Tags
    lines.append("────────────────────────────")
    lines.append(f"🏛️ <b>Verified Source:</b> {source}")
    lines.append("💬 <i>Stay ahead in Cambodia's supply chain — daily briefings at 08:00, 13:30, 18:00 ICT.</i>")
    if tags:
        lines.append(tags)

    return "\n".join(lines)


def format_rate_index(indicators: List[Dict[str, Any]]) -> str:
    """Formats freight rate indices and fuel costs into an executive table."""
    lines = []
    lines.append("📈 <b>CAMBODIA FREIGHT & LOGISTICS RATE INDEX</b>")
    lines.append("📊 <i>សន្ទស្សន៍តម្លៃដឹកជញ្ជូន និងថ្លៃប្រេងឥន្ធនៈ | 柬埔寨运价与物流基准指数</i>")
    lines.append("────────────────────────────")

    # Group by category
    categories = {}
    for ind in indicators:
        cat = ind.get("category", "General")
        categories.setdefault(cat, []).append(ind)

    cat_icons = {
        "Sea Freight": "🚢 <b>SEA CONTAINER FREIGHT (海运集装箱)</b>",
        "Feeder / Sea": "⚓ <b>FEEDER SERVICES (支线驳船)</b>",
        "Barge / Feeder": "🛳️ <b>INLAND WATERWAY & MEKONG (内河水运)</b>",
        "Air Freight": "✈️ <b>AIR CARGO FREIGHT (航空货运)</b>",
        "Trucking": "🚛 <b>DOMESTIC & CROSS-BORDER TRUCKING (公路拖卡)</b>",
        "Fuel / Energy": "⛽ <b>COMMERCIAL DIESEL & FUEL (燃油价格)</b>"
    }

    for cat, items in categories.items():
        title = cat_icons.get(cat, f"📦 <b>{cat.upper()}</b>")
        lines.append(f"\n{title}")
        for it in items:
            name = html.escape(it.get("indicator_name", ""))
            curr = html.escape(str(it.get("current_value", "")))
            pct = it.get("change_pct", 0.0)
            trend = it.get("status_trend", "STABLE")
            
            trend_icon = "➖"
            if pct > 0:
                trend_icon = f"🔺 +{pct:.1f}%"
            elif pct < 0:
                trend_icon = f"🔻 {pct:.1f}%"
            else:
                trend_icon = "🟢 0.0%"

            lines.append(f"  ▪️ <b>{name}</b>\n     ↳ Rate: <code>{curr}</code> ({trend_icon})")

    lines.append("\n────────────────────────────")
    lines.append("💡 <i>Source: Spot freight indices, carrier fuel surcharges, CAMFFA & GDCE declarations.</i>")
    lines.append("#FreightRates #OceanFreight #AirCargo #CambodiaLogistics #运价指数")
    return "\n".join(lines)


def format_port_status() -> str:
    """Formats operational status for Sihanoukville (PAS) and Phnom Penh (PPAP) in Trilingual format."""
    return """
⚓ <b>CAMBODIA PORTS OPERATIONAL DASHBOARD</b>
🚢 <i>ស្ថានភាពកំពង់ផែស្វយ័តកម្ពុជា | 柬埔寨港口运营实时看板</i>
────────────────────────────

🚢 <b>1. Sihanoukville Autonomous Port (PAS) / កំពង់ផែក្រុងព្រះសីហនុ / 西哈努克自治港:</b>
• <b>Berth Wait Time:</b> 🟢 0.5 - 1.0 Day / រង់ចាំ ០.៥ - ១ ថ្ងៃ / 靠泊等待正常 (0.5-1天)
• <b>Vessel Turnaround:</b> ⏱️ 12 - 16 Hours / ពេលលើកដាក់ ១២-១៦ ម៉ោង / 周转高效
• <b>Yard Utilization:</b> 📦 76% Fluid Operations / ទីលានដំណើរការល្អ / 堆场利用率 76%
• <b>STS Gantry Cranes:</b> ⚙️ 5 STS Cranes + 2 MHC Active / ស្ទូចកុងតឺន័រដំណើរការពេញលេញ
• <b>Deep-Water Terminal:</b> 🚧 Phase 1 (14.5m draft) on track / 14.5米深水码头建设中
• <b>Direct Feeder Loops:</b> Singapore, Port Klang, Cai Mep, Bangkok, Shekou

🛳️ <b>2. Phnom Penh Autonomous Port (PPAP LM17) / កំពង់ផែស្វយ័តភ្នំពេញ / 金边自治港:</b>
• <b>River Barge Berthing:</b> 🟢 0 Hours Wait (Immediate) / ចូលចតភ្លាមៗ / 即到即靠
• <b>Transit to Cai Mep Hub:</b> ⏱️ 24 - 30 Hours downriver / ២៤-៣០ ម៉ោង ទៅដល់ Cai Mep
• <b>Reefer Plugs Available:</b> 🔌 95% Available (Mango/Banana/Cassava exports / 农产品冷链冷插)
• <b>Customs Green Channel:</b> ✅ 85% fast-track clearance via CamDX / 绿通快速验放

────────────────────────────
💡 <b>PRO TIP / គន្លឹះសំខាន់ / 物流锦囊:</b>
<i>Routing heavy 40ft containers via PPAP LM17 river barge saves $80-$120 per box compared to road haulage!</i>
<i>ដឹកជញ្ជូនទំនិញធ្ងន់តាមសាឡង់ LM17 ចំណេញ ៨០ - ១២០ ដុល្លារក្នុងមួយកុងតឺន័រធៀបនឹងផ្លូវគោក!</i>
#PAS #PPAP #CambodiaPorts #MaritimeLogistics #港口动态
"""

def format_customs_guide() -> str:
    """Formats GDCE Customs compliance and paperwork guidance in Trilingual format."""
    return """
📋 <b>CAMBODIA CUSTOMS (GDCE) & TRADE CLEARANCE GUIDE</b>
🏛️ <i>ការណែនាំនីតិវិធីគយ និងការបំពេញបែបបទ | 柬埔寨海关清关与原产地证合规指引</i>
────────────────────────────

🏛️ <b>General Department of Customs and Excise (GDCE / គយ / 海关):</b>
• <b>ASYCUDA World Single Window:</b> Online manifest filing 24h prior to berthing.
  ↳ <i>ដាក់លិខិតឆ្លងកាត់តាមប្រព័ន្ធមុន ២៤ ម៉ោង | 靠港前24小时电子舱单申报</i>
• <b>CamDX National Platform:</b> Real-time digital licenses & phytosanitary permits.
  ↳ <i>ការតភ្ជាប់អាជ្ញាប័ណ្ណឌីជីថល | 数字化单一窗口许可证联网核放</i>

📜 <b>Preferential Trade Agreements / កិច្ចព្រមព្រៀងពាណិជ្ជកម្ម / 协定税率:</b>
1. <b>RCEP (Regional Comprehensive Economic Partnership):</b>
   ▫️ 0% duty on raw textiles, yarn, and manufacturing equipment from China & ASEAN.
   ▫️ <i>ពន្ធនាំចូល ០% លើវត្ថុធាតុដើមវាយនភណ្ឌ | 原产地证享原材料零关税</i>
2. <b>ASEAN Trade in Goods Agreement (ATIGA - Form D):</b>
   ▫️ Cross-border land transit via Bavet (VN) & Poipet (TH) with duty exemption.
3. <b>EU / UK Schemes:</b>
   ▫️ REX exporter system for duty-free garment & footwear apparel exports.

⚠️ <b>COMPLIANCE ALERT / បម្រាមគយ / 查验预警:</b>
• Always verify HS Codes before factory stuffing to stay in the <b>Green Channel</b> (Avoid physical inspection delays / 避免落入红道拆箱查验).

────────────────────────────
#CustomsGDCE #ASYCUDA #CamDX #RCEP #GarmentExport #海关清关
"""

def format_factory_supply_chain() -> str:
    """Formats Factory & Manufacturing logistics intelligence in Trilingual format."""
    return """
🏭 <b>CAMBODIA FACTORY & INDUSTRIAL SUPPLY CHAIN DISPATCH</b>
📦 <i>ខ្សែច្រវាក់ផ្គត់ផ្គង់រោងចក្រកាត់ដេរ និងតំបន់សេដ្ឋកិច្ចពិសេស | 工厂供应链与经济特区内陆港动态</i>
────────────────────────────

📦 <b>1. Inbound Raw Materials / វត្ថុធាតុដើមនាំចូល / 进口原材料:</b>
• <b>Fabric & Textile Inflow:</b> Steady volume from Ningbo, Shanghai & Guangzhou.
• <b>Transit Time:</b> 7-10 days feeder sea to PAS; 3 days cross-border road from Vietnam.
• <b>Demurrage Free Time:</b> 7 days at port; transfer to ICD dry port within 48h recommended.

📦 <b>2. Outbound Finished Apparel / នាំចេញសម្លៀកបំពាក់សម្រេច / 成品出口:</b>
• <b>40ft HQ Availability:</b> Healthy equipment stock at Teng Lay, Olair, So Ngoun dry ports.
• <b>Stuffing Cut-off:</b> 36 hours prior to feeder departure at PAS.
• <b>Expressway Haulage:</b> PP to Sihanoukville in 2h 15m.

📍 <b>SEZ Logistics Gateways / តំបន់សេដ្ឋកិច្ចពិសេស / 重点特区:</b>
• <b>Phnom Penh SEZ (Royal Group):</b> On-site customs inspection & bonded logistics.
• <b>Manhattan & Tai Seng SEZs (Bavet):</b> Direct cross-border trucking access to Cai Mep.
• <b>Sihanoukville SEZ (SSEZ):</b> Immediate proximity to PAS deep-water port.

────────────────────────────
#FactoryLogistics #GarmentCambodia #GFT #SEZ #SupplyChain #柬埔寨工厂
"""
