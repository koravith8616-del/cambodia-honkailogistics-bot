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
    
    # Category Banner
    lines.append(f"🇰🇭 <b>CAMBODIA LOGISTICS MARKET INTELLIGENCE</b>")
    lines.append(f"📌 <b>Category:</b> {category} | 🕒 <i>{timestamp}</i>")
    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

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
        lines.append(f"📸 <i>Action Photo: {photo_title}</i>")
        if photo_loc:
            lines.append(f"📍 <i>Location: {photo_loc} ({photo_credit})</i>")
        lines.append("")

    # Executive Summary
    lines.append("🚨 <b>Executive Summary / សេចក្តីសង្ខេប / 核心要闻:</b>")
    if language_mode in ("trilingual", "bilingual", "en") and summary_en:
        lines.append(f"🇬🇧 {summary_en}")
    if language_mode in ("trilingual", "bilingual", "km") and summary_km:
        lines.append(f"🇰🇭 {summary_km}")
    if language_mode in ("trilingual", "zh") and summary_zh:
        lines.append(f"🇨🇳 {summary_zh}")
    lines.append("")

    # Key Data Points
    key_data = item.get("key_data", [])
    if key_data:
        lines.append("📊 <b>Key Freight & Operational Metrics / 核心指标:</b>")
        for dp in key_data:
            lines.append(f"  ▫️ {html.escape(str(dp))}")
        lines.append("")

    # Cambodia Factory & Trade Impact
    if cambodia_impact or cambodia_impact_zh:
        lines.append("🏭 <b>Impact on Cambodia Factories & Shippers / 产业影响:</b>")
        if language_mode in ("trilingual", "bilingual", "en") and cambodia_impact:
            lines.append(f"🇬🇧 {cambodia_impact}")
        if language_mode in ("trilingual", "zh") and cambodia_impact_zh:
            lines.append(f"🇨🇳 {cambodia_impact_zh}")
        lines.append("")

    # Forwarder & Shipper Action Plan
    if action_rec or action_rec_zh:
        lines.append("💡 <b>Forwarder & Shipper Action Plan / 建议方案:</b>")
        if language_mode in ("trilingual", "bilingual", "en") and action_rec:
            lines.append(f"🇬🇧 {action_rec}")
        if language_mode in ("trilingual", "zh") and action_rec_zh:
            lines.append(f"🇨🇳 {action_rec_zh}")
        lines.append("")

    # Footer & Tags
    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    lines.append(f"ℹ️ <b>Source:</b> {source}")
    if tags:
        lines.append(tags)

    return "\n".join(lines)


def format_rate_index(indicators: List[Dict[str, Any]]) -> str:
    """Formats freight rate indices and fuel costs into an executive table."""
    lines = []
    lines.append("📈 <b>CAMBODIA FREIGHT & LOGISTICS RATE INDEX</b>")
    lines.append("<i>Weekly Container, Air Cargo & Inland Transport Benchmark</i>")
    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    # Group by category
    categories = {}
    for ind in indicators:
        cat = ind.get("category", "General")
        categories.setdefault(cat, []).append(ind)

    for cat, items in categories.items():
        lines.append(f"\n📦 <b>{cat.upper()}</b>")
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

            lines.append(f"• <b>{name}:</b> <code>{curr}</code> ({trend_icon})")

    lines.append("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    lines.append("💡 <i>Rates compiled from spot market indices, carrier surcharges & GDCE freight declarations.</i>")
    lines.append("#FreightRates #OceanFreight #AirCargo #CambodiaLogistics")
    return "\n".join(lines)


def format_port_status() -> str:
    """Formats operational status for Sihanoukville (PAS) and Phnom Penh (PPAP)."""
    return """
⚓ <b>CAMBODIA PORTS OPERATIONAL DASHBOARD</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🚢 <b>1. Sihanoukville Autonomous Port (PAS) — កំពង់ផែក្រុងព្រះសីហនុ</b>
• <b>Berth Wait Time:</b> 🟢 0.5 - 1.0 Day (Normal)
• <b>Vessel Turnaround:</b> ⏱️ 12 - 16 Hours
• <b>Yard Utilization:</b> 📦 76% (Fluid operations)
• <b>STS Gantry Cranes:</b> ⚙️ 5 Cranes Active + 2 Mobile Harbor Cranes
• <b>Deep-Water Expansion:</b> 🚧 Terminal Phase 1 (14.5m draft) progressing
• <b>Feeder Direct Calls:</b> Singapore, Port Klang, Cai Mep, Bangkok, Shekou

🛳️ <b>2. Phnom Penh Autonomous Port (PPAP) — កំពង់ផែស្វយ័តភ្នំពេញ (LM17)</b>
• <b>River Barge Berthing:</b> 🟢 Immediate (0 Hours wait)
• <b>Barge Transit to Cai Mep:</b> ⏱️ 24 - 30 Hours downriver
• <b>Reefer Plugs Available:</b> 🔌 95% Available (Agricultural exports)
• <b>Customs Green Channel:</b> ✅ 85% fast-track clearance via CamDX

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💡 <i>Recommendation: Routing heavy 40ft containers via PPAP LM17 river barge saves up to $80-$120/box compared to road haulage to deep-sea hubs.</i>
#PAS #PPAP #CambodiaPorts #MaritimeLogistics
"""

def format_customs_guide() -> str:
    """Formats GDCE Customs compliance and paperwork guidance."""
    return """
📋 <b>CAMBODIA CUSTOMS (GDCE) & TRADE CLEARANCE GUIDE</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🏛️ <b>General Department of Customs and Excise (GDCE)</b>
• <b>ASYCUDA World Single Window:</b> Online manifest & declaration submission mandatory 24h prior to vessel berthing.
• <b>CamDX National Platform:</b> Real-time exchange of customs licenses, transport permits & Phytosanitary certificates.

📜 <b>Preferential Trade Agreements & Form Verification:</b>
1. <b>RCEP (Regional Comprehensive Economic Partnership):</b>
   ▫️ Covers imports from China, Vietnam, Thailand, Japan, Korea, Australia.
   ▫️ Requires verified RCEP Certificate of Origin for 0% duty on raw materials.
2. <b>ASEAN Trade in Goods Agreement (ATIGA):</b>
   ▫️ Form D for cross-border transit via Bavet (Vietnam) & Poipet (Thailand).
3. <b>EBA / GSP Schemes:</b>
   ▫️ EU Registered Exporter (REX) system for garment & footwear duty-free exports.

⚠️ <b>Compliance Alert:</b>
• Verify Fabric & Raw Material HS Codes prior to stuffing in origin ports to avoid "Yellow/Red Channel" physical stripping at PAS or dry ports.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#CustomsGDCE #ASYCUDA #CamDX #RCEP #GarmentExportCambodia
"""

def format_factory_supply_chain() -> str:
    """Formats Factory & Manufacturing logistics intelligence."""
    return """
🏭 <b>CAMBODIA FACTORY & INDUSTRIAL SECTOR DISPATCH</b>
<i>Focus: Garment, Footwear, Travel Goods (GFT) & Electronics SEZs</i>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📦 <b>1. Inbound Raw Material Flow:</b>
• <b>Fabric & Textile Inflow:</b> Steady volume from Ningbo, Shanghai & Guangzhou.
• <b>Transit Time:</b> 7-10 days feeder sea transit to Sihanoukville PAS; 3 days cross-border trucking from Vietnam.
• <b>Demurrage & Detention:</b> Free time averages 7 days at port; dry port transfer recommended within 48h.

📦 <b>2. Outbound Finished Goods (US/EU Buyers):</b>
• <b>Container Availability:</b> 40ft HQ container inventory is healthy across Phnom Penh dry ports (Olair, So Ngoun, Teng Lay, PPAP).
• <b>Stuffing cut-off:</b> 36 hours prior to feeder departure at PAS.
• <b>Expressway Haulage:</b> Container trucks running PP to PAS in 2h 15m.

📍 <b>SEZ Logistics Gateways:</b>
• <b>Phnom Penh SEZ (Royal Group):</b> On-site customs inspection & bonded logistics.
• <b>Manhattan & Tai Seng SEZs (Bavet):</b> Direct cross-border trucking access to Cai Mep.
• <b>Sihanoukville SEZ (SSEZ):</b> Immediate proximity to PAS deep-water port.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#FactoryLogistics #GarmentCambodia #GFT #SEZ #SupplyChain
"""
