import html
from typing import Dict, List, Any

def format_intelligence_post(item: Dict[str, Any], language_mode: str = "en") -> str:
    """
    Formats an intelligence report into a high-impact, professional Telegram HTML message in English.
    Specifically designed to promote Honkai Logistics services, reassure existing customers,
    and attract new clients by demonstrating operational excellence and reliability.
    """
    category = html.escape(item.get("category", "Market Logistics"))
    title_en = html.escape(item.get("title_en", ""))
    service_highlight = html.escape(item.get("service_highlight", "Honkai Logistics Dedicated Services"))
    summary_en = html.escape(item.get("summary_en", ""))
    market_intelligence = html.escape(item.get("market_intelligence", ""))
    honkai_advantage = html.escape(item.get("honkai_advantage", ""))
    action_rec = html.escape(item.get("action_recommendation", ""))
    
    photo_title = html.escape(item.get("photo_title", ""))
    photo_loc = html.escape(item.get("photo_location", ""))
    photo_credit = html.escape(item.get("photo_credit", ""))
    source = html.escape(item.get("source", "Honkai Logistics Intelligence Desk"))
    timestamp = html.escape(item.get("timestamp", ""))

    tags = " ".join([f"<b>{html.escape(t)}</b>" for t in item.get("tags", [])])

    lines = []
    
    # 1. Header Banner
    lines.append("🇰🇭 <b>HONKAI LOGISTICS | CAMBODIA MARKET DISPATCH</b>")
    lines.append(f"⚡ <b>Executive Freight Briefing</b> | 📌 <b>{category}</b>")
    lines.append(f"🕒 <i>{timestamp}</i>")
    lines.append("────────────────────────────")

    # 2. Main English Headline
    if title_en:
        lines.append(f"🚢 <b>{title_en}</b>")
        lines.append("")

    # 3. Action Photo Operational Context
    if photo_title:
        lines.append(f"📸 <b>Verified Operations:</b> <i>{photo_title}</i>")
        if photo_loc:
            lines.append(f"📍 <i>{photo_loc}</i>")
        lines.append("")

    # 4. Market Summary
    if summary_en:
        lines.append("📢 <b>MARKET OVERVIEW & OPERATIONAL REALITY:</b>")
        lines.append(f"• {summary_en}")
        if market_intelligence:
            lines.append(f"• <i>{market_intelligence}</i>")
        lines.append("")

    # 5. Key Operational Data Points
    key_data = item.get("key_data", [])
    if key_data:
        lines.append("📊 <b>KEY METRICS & ROUTE BENCHMARKS:</b>")
        for dp in key_data:
            lines.append(f"  ▪️ <code>{html.escape(str(dp))}</code>")
        lines.append("")

    # 6. Honkai Logistics Advantage & Service Spotlight (Promoting Trust & Quality)
    if honkai_advantage:
        lines.append("🛡️ <b>THE HONKAI LOGISTICS ADVANTAGE:</b>")
        lines.append(f"⭐ <b>{service_highlight}</b>")
        lines.append(f"{honkai_advantage}")
        lines.append("")

    # 7. Action Recommendation & Client Call to Action
    if action_rec:
        lines.append("💡 <b>EXECUTIVE RECOMMENDATION & NEXT STEPS:</b>")
        lines.append(f"🎯 {action_rec}")
        lines.append("")

    # 8. Footer & Trust-Building Company Callout
    lines.append("────────────────────────────")
    lines.append("🤝 <b>HONKAI LOGISTICS (CAMBODIA) CO., LTD.</b>")
    lines.append("🚀 <i>Your Reliable Partner for Ocean, Air, Cross-Border Trucking & Customs</i>")
    lines.append("📞 <b>Inquiries & Bookings:</b> <i>Contact our 24/7 Logistics Desk</i>")
    lines.append(f"🏛️ <b>Verified Source:</b> <i>{source}</i>")
    if tags:
        lines.append(tags)

    return "\n".join(lines)


def format_rate_index(indicators: List[Dict[str, Any]]) -> str:
    """Formats freight rate indices and fuel costs into an executive English table."""
    lines = []
    lines.append("📈 <b>HONKAI LOGISTICS | CAMBODIA FREIGHT RATE BENCHMARK</b>")
    lines.append("📊 <i>Live Spot Rates, Feeder Tariffs & Commercial Energy Index</i>")
    lines.append("────────────────────────────")

    categories = {}
    for ind in indicators:
        cat = ind.get("category", "General")
        categories.setdefault(cat, []).append(ind)

    cat_icons = {
        "Sea Freight": "🚢 <b>OCEAN CONTAINER FREIGHT (FCL / LCL)</b>",
        "Feeder / Sea": "⚓ <b>FEEDER SERVICES (PAS & REGIONAL HUBS)</b>",
        "Barge / Feeder": "🛳️ <b>INLAND WATERWAY & MEKONG BARGE</b>",
        "Air Freight": "✈️ <b>AIR CARGO EXPRESS (PNH / TIA)</b>",
        "Trucking": "🚛 <b>DOMESTIC & CROSS-BORDER TRUCKING</b>",
        "Fuel / Energy": "⛽ <b>COMMERCIAL DIESEL & FUEL SURCHARGE</b>"
    }

    for cat, items in categories.items():
        title = cat_icons.get(cat, f"📦 <b>{cat.upper()}</b>")
        lines.append(f"\n{title}")
        for it in items:
            name = html.escape(it.get("indicator_name", ""))
            curr = html.escape(str(it.get("current_value", "")))
            pct = it.get("change_pct", 0.0)
            
            trend_icon = "➖"
            if pct > 0:
                trend_icon = f"🔺 +{pct:.1f}%"
            elif pct < 0:
                trend_icon = f"🔻 {pct:.1f}%"
            else:
                trend_icon = "🟢 Stable"

            lines.append(f"  ▪️ <b>{name}</b>\n     ↳ Rate: <code>{curr}</code> ({trend_icon})")

    lines.append("\n────────────────────────────")
    lines.append("💡 <i>Honkai Logistics offers secured space contracts and volume discounts for regular shippers.</i>")
    lines.append("📞 Contact Honkai Logistics for customized spot or quarterly contract rate quotes.")
    lines.append("#HonkaiLogistics #FreightRates #OceanFreight #AirCargo #CambodiaSupplyChain")
    return "\n".join(lines)


def format_port_status() -> str:
    """Formats operational status for Sihanoukville (PAS) and Phnom Penh (PPAP) in clean English."""
    return """
⚓ <b>HONKAI LOGISTICS | CAMBODIA PORTS OPERATIONAL DASHBOARD</b>
🚢 <i>Live Operational Intelligence: Sihanoukville (PAS) & Phnom Penh (PPAP)</i>
────────────────────────────

🚢 <b>1. Sihanoukville Autonomous Port (PAS) Deep-Water Terminal:</b>
• <b>Berth Waiting Time:</b> 🟢 0.5 - 1.0 Day (Fluid Berthing)
• <b>Vessel Turnaround:</b> ⏱️ 12 - 16 Hours per feeder vessel
• <b>Yard Utilization:</b> 📦 76% (Normal fluid capacity)
• <b>Gantry Cranes:</b> ⚙️ 5 STS Cranes + 2 MHC Active
• <b>Deep-Water Expansion:</b> 🚧 Phase 1 (14.5m draft) on schedule for completion
• <b>Direct Feeder Loops:</b> Singapore, Port Klang, Cai Mep, Bangkok, Shekou

🛳️ <b>2. Phnom Penh Autonomous Port (PPAP LM17) River Terminal:</b>
• <b>Barge Berthing:</b> 🟢 0 Hours Waiting (Immediate Berthing)
• <b>Transit to Cai Mep Hub:</b> ⏱️ 24 - 30 Hours downriver
• <b>Reefer Plugs Available:</b> 🔌 95% Active & Monitored
• <b>Customs Green Channel:</b> ✅ Fast-track paperless clearance via CamDX

────────────────────────────
💡 <b>THE HONKAI ADVANTAGE:</b>
<i>Routing heavy 40ft containers via Honkai's PPAP LM17 river barge saves $80-$120 per box compared to road transport while guaranteeing seamless transshipment onto US/EU mother vessels.</i>

📞 Contact Honkai Logistics for guaranteed port allocations and express feeder bookings.
#HonkaiLogistics #PAS #PPAP #CambodiaPorts #MaritimeLogistics
"""


def format_customs_guide() -> str:
    """Formats GDCE Customs compliance and paperwork guidance in clean English."""
    return """
📋 <b>HONKAI LOGISTICS | CAMBODIA CUSTOMS (GDCE) CLEARANCE GUIDE</b>
🏛️ <i>Regulatory Compliance, ASYCUDA Pre-Filing & Rules of Origin Advisory</i>
────────────────────────────

🏛️ <b>General Department of Customs and Excise (GDCE) Best Practices:</b>
• <b>ASYCUDA World Single Window:</b> Online manifest filing 24h to 48h prior to vessel berthing.
• <b>CamDX Digital Integration:</b> Automated electronic import/export licenses and permits.
• <b>Pre-Arrival Declaration:</b> Enables 92%+ Green Lane automated release without physical inspection.

📜 <b>Preferential Trade Agreements & Tariff Optimization:</b>
1. <b>RCEP (Regional Comprehensive Economic Partnership):</b>
   ▫️ 0% duty on raw fabrics, yarns, dyes, and manufacturing machinery from China & ASEAN.
2. <b>ASEAN Trade in Goods Agreement (ATIGA - Form D):</b>
   ▫️ Duty-free cross-border land transit via Bavet (Vietnam) & Poipet (Thailand).
3. <b>EU / UK Schemes:</b>
   ▫️ Registered Exporter (REX) system for duty-free garment & footwear exports.

⚠️ <b>COMPLIANCE PROTECTION:</b>
• Always verify HS Codes prior to factory stuffing to maintain Green Channel status and avoid demurrage costs.

────────────────────────────
🛡️ <b>WHY CHOOSE HONKAI CUSTOMS BROKERAGE?</b>
<i>Our in-house licensed customs brokers manage pre-audits, electronic filings, and on-site port coordination, ensuring 100% compliant, zero-demurrage clearance for your cargo.</i>

#HonkaiLogistics #CustomsBrokerage #GDCE #ASYCUDA #CamDX #RCEP #TradeCompliance
"""


def format_factory_supply_chain() -> str:
    """Formats Factory & Manufacturing logistics intelligence in clean English."""
    return """
🏭 <b>HONKAI LOGISTICS | CAMBODIA INDUSTRIAL & FACTORY SUPPLY CHAIN</b>
📦 <i>Garment, Footwear, Electronics & Special Economic Zone (SEZ) Solutions</i>
────────────────────────────

📦 <b>1. Inbound Raw Materials & Component Staging:</b>
• <b>Textile & Fabric Supply:</b> Steady weekly arrivals from Shanghai, Ningbo, and Guangzhou.
• <b>Transit Timelines:</b> 7-9 days ocean feeder to PAS; 3 days cross-border road from Vietnam.
• <b>Free Demurrage Packages:</b> Up to 14-21 days detention free-time for contracted Honkai clients.

📦 <b>2. Outbound Finished Goods & Retail Exports:</b>
• <b>40ft HQ Equipment:</b> Guaranteed pristine container equipment stock at Phnom Penh depots.
• <b>GOH Capabilities:</b> Specialized Garment on Hanger installation for wrinkle-free retail delivery.
• <b>Expressway Haulage:</b> Guaranteed 2.5-hour transit from Phnom Penh factories to PAS port gate.

📍 <b>Key SEZ Logistics Service Corridors:</b>
• <b>Royal Group Phnom Penh SEZ:</b> On-site bonded warehousing, vendor-managed inventory (VMI).
• <b>Manhattan & Tai Seng SEZs (Bavet):</b> Daily bonded cross-border shuttles to Vietnam deep-sea ports.
• <b>Sihanoukville SEZ (SSEZ):</b> Immediate port proximity for heavy container loading.

────────────────────────────
🤝 <b>PARTNER WITH HONKAI LOGISTICS:</b>
<i>From raw material import to global retail delivery, Honkai Logistics provides end-to-end supply chain reliability, live GPS tracking, and dedicated corporate account management.</i>

#HonkaiLogistics #FactoryLogistics #GarmentCambodia #GFT #SEZ #SupplyChainSolutions
"""
