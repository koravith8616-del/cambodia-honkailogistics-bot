import html
from typing import Dict, List, Any

def format_intelligence_post(item: Dict[str, Any], language_mode: str = "bilingual") -> str:
    """
    Formats a Cambodia logistics market intelligence report into an executive Telegram HTML message.
    Strictly bilingual: Khmer summary alongside English summary, focused entirely on helpful
    operational intelligence for Freight Forwarders, Shipping Lines, and Logistics Operators in Cambodia.
    """
    category = html.escape(item.get("category", "Cambodia Logistics"))
    title_km = html.escape(item.get("title_km", ""))
    title_en = html.escape(item.get("title_en", ""))
    summary_km = html.escape(item.get("summary_km", ""))
    summary_en = html.escape(item.get("summary_en", ""))
    
    impact_km = html.escape(item.get("cambodia_impact", item.get("impact_km", "")))
    impact_en = html.escape(item.get("cambodia_impact_en", item.get("impact_en", "")))
    
    action_km = html.escape(item.get("action_recommendation", item.get("action_km", "")))
    action_en = html.escape(item.get("action_recommendation_en", item.get("action_en", "")))
    
    photo_title = html.escape(item.get("photo_title", ""))
    photo_loc = html.escape(item.get("photo_location", ""))
    photo_credit = html.escape(item.get("photo_credit", ""))
    source = html.escape(item.get("source", "Cambodia Logistics Intelligence"))
    timestamp = html.escape(item.get("timestamp", ""))

    tags = " ".join([f"<b>{html.escape(t)}</b>" for t in item.get("tags", [])])

    lines = []
    
    # 1. Header Banner
    lines.append("🇰🇭 <b>ព័ត៌មានទីផ្សារភស្តុភារកម្មកម្ពុជា | CAMBODIA LOGISTICS INTEL</b>")
    lines.append(f"⚡ <b>Freight Forwarder & Carrier Advisory</b> | 📌 <b>{category}</b>")
    lines.append(f"🕒 <i>{timestamp}</i>")
    lines.append("────────────────────────────")

    # 2. Main Bilingual Headlines (Khmer first, followed by English)
    if title_km:
        lines.append(f"🇰🇭 <b>{title_km}</b>")
    if title_en:
        lines.append(f"🇬🇧 <b>{title_en}</b>")
    lines.append("")

    # 3. Action Photo Operational Context
    if photo_title:
        lines.append(f"📸 <b>ទិដ្ឋភាពជាក់ស្តែង / Operations:</b> <i>{photo_title}</i>")
        if photo_loc:
            lines.append(f"📍 <i>{photo_loc}</i>")
        lines.append("")

    # 4. Bilingual Operational Executive Summary
    lines.append("📢 <b>សេចក្តីសង្ខេបប្រតិបត្តិការ / EXECUTIVE SUMMARY:</b>")
    if summary_km:
        lines.append(f"🇰🇭 • {summary_km}")
    if summary_en:
        lines.append(f"🇬🇧 • {summary_en}")
    lines.append("")

    # 5. Key Operational Data Points
    key_data = item.get("key_data", [])
    if key_data:
        lines.append("📊 <b>សូចនាករសំខាន់ៗ / KEY OPERATIONAL METRICS:</b>")
        for dp in key_data:
            lines.append(f"  ▪️ <code>{html.escape(str(dp))}</code>")
        lines.append("")

    # 6. Supply Chain & Trade Impact
    if impact_km or impact_en:
        lines.append("🏭 <b>ផលប៉ះពាល់ខ្សែច្រវាក់ផ្គត់ផ្គង់ / SUPPLY CHAIN IMPACT:</b>")
        if impact_km:
            lines.append(f"🇰🇭 {impact_km}")
        if impact_en:
            lines.append(f"🇬🇧 {impact_en}")
        lines.append("")

    # 7. Forwarder & Shipper Action Plan
    if action_km or action_en:
        lines.append("💡 <b>អនុសាសន៍សម្រាប់ក្រុមហ៊ុនដឹកជញ្ជូន / FORWARDER ACTION PLAN:</b>")
        if action_km:
            lines.append(f"🇰🇭 🎯 {action_km}")
        if action_en:
            lines.append(f"🇬🇧 🎯 {action_en}")
        lines.append("")

    # 8. Footer & Authoritative Source
    lines.append("────────────────────────────")
    lines.append(f"🏛️ <b>ប្រភពផ្ទៀងផ្ទាត់ / Verified Source:</b> <i>{source}</i>")
    lines.append("💬 <i>ព័ត៌មានទាន់ហេតុការណ៍សម្រាប់សមាគមភស្តុភារកម្ម (CAMFFA) ភ្នាក់ងារនាវាចរណ៍ និងក្រុមហ៊ុនដឹកជញ្ជូននៅកម្ពុជា។</i>")
    if tags:
        lines.append(tags)

    return "\n".join(lines)


def format_rate_index(indicators: List[Dict[str, Any]]) -> str:
    """Formats freight rate indices and fuel costs into an executive bilingual table."""
    lines = []
    lines.append("📈 <b>សន្ទស្សន៍តម្លៃដឹកជញ្ជូនកម្ពុជា | CAMBODIA FREIGHT RATE INDEX</b>")
    lines.append("📊 <i>Live Spot Rates, Feeder Tariffs & Commercial Diesel Benchmark</i>")
    lines.append("────────────────────────────")

    categories = {}
    for ind in indicators:
        cat = ind.get("category", "General")
        categories.setdefault(cat, []).append(ind)

    cat_icons = {
        "Sea Freight": "🚢 <b>ថ្លៃដឹកជញ្ជូនតាមសមុទ្រ (Ocean Container FCL / LCL)</b>",
        "Feeder / Sea": "⚓ <b>កម្រៃសេវាកប៉ាល់ចំណុះ (Feeder to Hubs)</b>",
        "Barge / Feeder": "🛳️ <b>ការដឹកជញ្ជូនតាមសាឡង់ទន្លេ (Mekong River Barge)</b>",
        "Air Freight": "✈️ <b>ថ្លៃដឹកជញ្ជូនតាមផ្លូវអាកាស (Air Cargo Express)</b>",
        "Trucking": "🚛 <b>ថ្លៃរថយន្តកុងតឺន័រ និងដឹកឆ្លងដែន (Road Freight & Border)</b>",
        "Fuel / Energy": "⛽ <b>តម្លៃប្រេងម៉ាស៊ូតពាណិជ្ជកម្ម (Commercial Diesel Benchmark)</b>"
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
                trend_icon = "🟢 ថេរ (Stable)"

            lines.append(f"  ▪️ <b>{name}</b>\n     ↳ Rate: <code>{curr}</code> ({trend_icon})")

    lines.append("\n────────────────────────────")
    lines.append("💡 <i>ប្រភព៖ CAMFFA, តារាងតម្លៃកំពង់ផែស្វយ័តក្រុងព្រះសីហនុ (PAS), ភ្នំពេញ (PPAP) និងក្រសួងពាណិជ្ជកម្ម។</i>")
    lines.append("#CambodiaLogistics #FreightRates #CAMFFA #OceanFreight #AirCargo #TruckingRates")
    return "\n".join(lines)


def format_port_status() -> str:
    """Formats operational status for Sihanoukville (PAS) and Phnom Penh (PPAP) in Khmer and English."""
    return """
⚓ <b>ស្ថានភាពប្រតិបត្តិការកំពង់ផែកម្ពុជា | CAMBODIA PORTS STATUS</b>
🚢 <i>Sihanoukville Autonomous Port (PAS) & Phnom Penh Autonomous Port (PPAP)</i>
────────────────────────────

🚢 <b>1. កំពង់ផែស្វយ័តក្រុងព្រះសីហនុ / Sihanoukville Autonomous Port (PAS):</b>
• <b>Berth Waiting Time:</b> 🟢 0.5 - 1.0 Day / រង់ចាំចូលចត ០.៥ - ១.០ ថ្ងៃ (Normal Fluid)
• <b>Vessel Turnaround:</b> ⏱️ 12 - 16 Hours / រយៈពេលលើកដាក់ ១២ - ១៦ ម៉ោងក្នុងមួយកប៉ាល់
• <b>Yard Utilization:</b> 📦 76% Capacity / ទីលានដំណើរការ ៧៦% នៃសមត្ថភាពផ្ទុក
• <b>Gantry Cranes:</b> ⚙️ 5 STS Cranes + 2 MHC Active / ស្ទូចកុងតឺន័រដំណើរការពេញលេញ
• <b>Deep-Water Expansion:</b> 🚧 ដំណាក់កាលទី១ (ជម្រៅទឹក ១៤.៥ ម៉ែត្រ) កំពុងសាងសង់តាមផែនការ
• <b>Direct Feeder Loops:</b> Singapore, Port Klang, Cai Mep, Bangkok, Shekou

🛳️ <b>2. កំពង់ផែស្វយ័តភ្នំពេញ / Phnom Penh Autonomous Port (PPAP LM17):</b>
• <b>Barge Berthing:</b> 🟢 0 Hours Waiting / ចូលចតភ្លាមៗ (Immediate Berthing)
• <b>Transit to Cai Mep Hub:</b> ⏱️ 24 - 30 Hours downriver / ២៤-៣០ ម៉ោង តាមដងទន្លេមេគង្គ
• <b>Reefer Plugs Available:</b> 🔌 95% Active / កន្លែងដោតភ្លើងកុងតឺន័រត្រជាក់មានគ្រប់គ្រាន់
• <b>Customs Green Channel:</b> ✅ 88% Fast-Track via CamDX / បញ្ចេញទំនិញឆាប់រហ័ស

────────────────────────────
💡 <b>FORWARDER PRO TIP / គន្លឹះសម្រាប់ក្រុមហ៊ុនបញ្ជូនទំនិញ:</b>
<i>ដឹកជញ្ជូនទំនិញកុងតឺន័រធ្ងន់ (40ft Heavy) តាមសាឡង់ PPAP LM17 ចំណេញចន្លោះពី ៨០ ទៅ ១២០ ដុល្លារក្នុងមួយទូ ធៀបនឹងការដឹកតាមផ្លូវគោក ព្រមទាំងមិនបារម្ភរឿងកំណត់ទម្ងន់លើផ្លូវជាតិឡើយ!</i>

#PAS #PPAP #CambodiaPorts #MaritimeLogistics #កំពង់ផែស្វយ័ត #CAMFFA
"""


def format_customs_guide() -> str:
    """Formats GDCE Customs compliance and paperwork guidance in Khmer and English."""
    return """
📋 <b>ការណែនាំនីតិវិធីគយ និងច្បាប់ពាណិជ្ជកម្ម | GDCE CUSTOMS COMPLIANCE GUIDE</b>
🏛️ <i>ASYCUDA World Pre-Filing, CamDX Integration & Rules of Origin Advisory</i>
────────────────────────────

🏛️ <b>អគ្គនាយកដ្ឋានគយ និងរដ្ឋាករកម្ពុជា (GDCE):</b>
• <b>ASYCUDA World Single Window:</b> Online manifest filing 24h to 48h prior to vessel berthing.
  ↳ <i>ដាក់លិខិតឆ្លងកាត់ និងបញ្ជីទំនិញតាមប្រព័ន្ធអេឡិចត្រូនិចមុន ២៤ ទៅ ៤៨ ម៉ោង មុនកប៉ាល់ចូលចត។</i>
• <b>CamDX Digital Integration:</b> Automated electronic import/export licenses and phytosanitary permits.
  ↳ <i>ការតភ្ជាប់អាជ្ញាប័ណ្ណ និងលិខិតអនុញ្ញាតបែបឌីជីថលកាត់បន្ថយពេលវេលាត្រួតពិនិត្យ។</i>
• <b>Pre-Arrival Declaration:</b> Enables 92%+ Green Lane automated release without physical inspection.
  ↳ <i>ការប្រកាសព័ត៌មានមុនពេលទំនិញមកដល់ ជួយឱ្យទំនិញឆ្លងកាត់ផ្លូវបៃតង (Green Channel) លើសពី ៩២%។</i>

📜 <b>វិញ្ញាបនបត្រដើមកំណើតទំនិញ និងការលើកលែងពន្ធ (Rules of Origin):</b>
1. <b>RCEP (Regional Comprehensive Economic Partnership):</b>
   ▫️ 0% duty on raw textiles, yarns, accessories, and manufacturing machinery from China & ASEAN.
   ▫️ <i>ពន្ធនាំចូល ០% លើវត្ថុធាតុដើមវាយនភណ្ឌ និងគ្រឿងម៉ាស៊ីនពីរដ្ឋជាសមាជិក RCEP។</i>
2. <b>ATIGA (Form D):</b>
   ▫️ Duty-free cross-border land transit via Bavet (Vietnam) & Poipet (Thailand).
   ▫️ <i>ការលើកលែងពន្ធសម្រាប់ការដឹកជញ្ជូនឆ្លងដែនក្នុងតំបន់អាស៊ាន។</i>
3. <b>EU / UK GSP Schemes:</b>
   ▫️ Registered Exporter (REX) system for duty-free garment & footwear exports.
   ▫️ <i>ប្រព័ន្ធ REX សម្រាប់ការនាំចេញសម្លៀកបំពាក់ និងស្បែកជើងដោយរួចពន្ធ។</i>

⚠️ <b>COMPLIANCE ALERT / បម្រាមគយសំខាន់:</b>
• ផ្ទៀងផ្ទាត់លេខកូដទំនិញ (HS Code) និងតម្លៃប្រកាសឱ្យបានត្រឹមត្រូវ មុនពេលផ្ទុកកុងតឺន័រ ដើម្បីចៀសវាងការធ្លាក់ចូលផ្លូវក្រហម (Red Lane) ដែលនាំឱ្យខាតបង់ថ្លៃស្តុក (Demurrage & Detention) នៅកំពង់ផែ!

────────────────────────────
#CustomsGDCE #ASYCUDA #CamDX #RCEP #TradeCompliance #គយនិងរដ្ឋាករ #CAMFFA
"""


def format_factory_supply_chain() -> str:
    """Formats Factory & Manufacturing logistics intelligence in Khmer and English."""
    return """
🏭 <b>ខ្សែច្រវាក់ផ្គត់ផ្គង់រោងចក្រ និងតំបន់សេដ្ឋកិច្ចពិសេស | FACTORY & SEZ SUPPLY CHAIN</b>
📦 <i>Garment, Footwear, Travel Goods (GFT) & Industrial Logistics</i>
────────────────────────────

📦 <b>1. វត្ថុធាតុដើមនាំចូល / Inbound Raw Materials & Staging:</b>
• <b>Textile & Fabric Supply:</b> Steady weekly arrivals from Ningbo, Shanghai, and Guangzhou.
• <b>Transit Timelines:</b> 7-9 days ocean feeder to PAS; 3 days cross-border road from Vietnam.
• <b>Free Demurrage Packages:</b> 14-21 days detention free-time recommended for dry port transfer.
• <i>ការផ្ទេរកុងតឺន័រពីកំពង់ផែទៅកាន់ឃ្លាំងស្តុក (Dry Port ICD) ក្នុងរយៈពេល ៤៨ ម៉ោង កាត់បន្ថយថ្លៃស្តុកលើសកាលកំណត់។</i>

📦 <b>2. ការនាំចេញទំនិញសម្រេច / Outbound Finished Goods Exports:</b>
• <b>40ft HQ Availability:</b> Healthy equipment stock at Teng Lay, Olair, and So Ngoun dry ports.
• <b>GOH Capabilities:</b> Specialized Garment on Hanger installation for wrinkle-free retail delivery.
• <b>Expressway Haulage:</b> 2h 15m transit from Phnom Penh industrial parks to PAS port gate.
• <i>ការដឹកជញ្ជូនតាមផ្លូវល្បឿនលឿនធានាការទៅដល់ទាន់ពេលវេលាកាត់បញ្ជី (CY Cut-Off) ចុងសប្តាហ៍។</i>

📍 <b>ច្រករបៀងតំបន់សេដ្ឋកិច្ចពិសេសសំខាន់ៗ / Key SEZ Corridors:</b>
• <b>Royal Group Phnom Penh SEZ:</b> On-site customs inspection & bonded logistics warehousing.
• <b>Manhattan & Tai Seng SEZs (Bavet):</b> Daily bonded shuttles to Cat Lai & Cai Mep deep-sea ports.
• <b>Sihanoukville SEZ (SSEZ):</b> Immediate proximity to PAS deep-water port terminal.

────────────────────────────
#FactoryLogistics #GarmentCambodia #GFT #SEZ #SupplyChain #រោងចក្រកាត់ដេរ #CAMFFA
"""
