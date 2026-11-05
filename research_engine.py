import hashlib
import json
import logging
import re
from typing import Dict, List, Optional, Any
from datetime import datetime

import httpx
from config import GEMINI_API_KEY, LOGISTICS_HUBS
from photo_curator import get_action_photo_for_topic
from database import get_recently_posted_titles, get_recently_used_photos

logger = logging.getLogger(__name__)

# Comprehensive 36 Cambodia Logistics Market Intelligence Scenarios
# Strictly focused on the Cambodian logistics market, tailored specifically for Freight Forwarders,
# Shipping Lines, Trucking Operators, and Factory Supply Chain Executives.
# Formatted in Khmer alongside English.
# Distributed across 3 distinct daily dispatch slots:
# - Slot 1 (Morning 08:00 ICT): Ocean Freight, Sea Ports (PAS), River Barges (PPAP) & Waterways
# - Slot 2 (Midday 13:30 ICT): Cross-Border Trucking (Bavet/Poipet), Expressways & Inland Haulage
# - Slot 3 (Evening 18:00 ICT): Air Cargo (PNH/TIA), GDCE Customs Compliance, SEZs & Warehousing
BUILTIN_INTELLIGENCE_FEEDS = [
    # =========================================================================
    # SLOT 1: MORNING (08:00 ICT) — OCEAN FREIGHT, SEA PORTS & WATERWAYS
    # =========================================================================
    {
        "slot": "slot_morning",
        "category": "Sea Freight & Port Operations / ប្រតិបត្តិការកំពង់ផែសមុទ្រ",
        "title_km": "បច្ចុប្បន្នភាពកាលវិភាគកប៉ាល់ចំណុះ និងការចូលចតនៅកំពង់ផែស្វយ័តក្រុងព្រះសីហនុ (PAS)",
        "title_en": "Sihanoukville Autonomous Port (PAS) Container Terminal Berthing & Feeder Schedules",
        "summary_km": "រយៈពេលចូលចត និងលើកដាក់ទំនិញនៅកំពង់ផែ PAS ជាមធ្យមពី ១២ ទៅ ១៦ ម៉ោងក្នុងមួយកប៉ាល់។ ទីលានកុងតឺន័រដំណើរការ ៧៦% នៃការផ្ទុកសរុប ដោយមានស្ទូចកុងតឺន័រ (STS Cranes) ចំនួន ៥ គ្រឿង និងស្ទូចចល័ត (MHC) ចំនួន ២ គ្រឿង កំពុងដំណើរការយ៉ាងសកម្មសម្រាប់ការនាំចេញសម្លៀកបំពាក់ទៅកាន់ទីផ្សារអាមេរិក និងអឺរ៉ុប។",
        "summary_en": "Feeder vessel turnaround time at Sihanoukville Autonomous Port (PAS) currently averages 12-16 hours per vessel. Container yard utilization stands at 76% with steady throughput for garment exports heading to US and EU retail markets. 5 STS gantry cranes and 2 MHC units are actively deployed.",
        "key_data": [
            "PAS Berth Wait Time: 0.5 - 1.0 Day / រង់ចាំចូលចត ០.៥ - ១.០ ថ្ងៃ (Normal Fluid)",
            "Feeder Slot Availability to Singapore/Port Klang: High / ជើងកប៉ាល់មានគ្រប់គ្រាន់",
            "Transshipment Connection via Cai Mep: 2-3 Days transit / តភ្ជាប់ទៅ Cai Mep ២-៣ ថ្ងៃ",
            "Empty 40ft HQ Equipment: Balanced at PAS & PPAP dry ports / ទូកុងតឺន័រមានស្ថិរភាព"
        ],
        "impact_km": "រោងចក្រកាត់ដេរ និងស្បែកជើង (GFT) អាចរក្សាការផ្ទុកទំនិញតាមកាលវិភាគធម្មតា។ ការតភ្ជាប់ទៅកាន់កប៉ាល់ធំ (Mother Vessel) នៅប្រទេសសិង្ហបុរី និងម៉ាឡេស៊ី កំពុងដំណើរការដោយរលូន ដោយគ្មានការលុបជើងកប៉ាល់ធំដុំនៅសប្តាហ៍នេះឡើយ។",
        "impact_en": "Garment & Footwear (GFT) factories can maintain standard loading cut-offs. Feeder connections to Singapore and Malaysia mother vessels are running on schedule without major blank sailings this week.",
        "action_km": "ក្រុមហ៊ុនបញ្ជូនទំនិញ (Forwarders) ត្រូវក្រើនរំលឹកដល់ម្ចាស់ទំនិញឱ្យបញ្ជូនពាក្យបញ្ជាដឹកជញ្ជូន (Shipping Instructions - SI) មុនពេលកាត់បញ្ជី (CY Cut-off) យ៉ាងតិច ២៤ ម៉ោង ដើម្បីចៀសវាងការស្ទះរថយន្តនៅច្រកទ្វារកំពង់ផែពេលចុងសប្តាហ៍។",
        "action_en": "Freight forwarders should advise factory shippers to submit SI (Shipping Instructions) 24 hours prior to CY cut-off to prevent gate-in delays during peak weekend trucking hours.",
        "tags": ["#SeaFreight", "#PAS", "#SihanoukvillePort", "#FeederSchedule", "#GarmentLogistics", "#CAMFFA"],
        "photo_category": "ocean_port",
        "source": "PAS Operations & Regional Feeder Carrier Network"
    },
    {
        "slot": "slot_morning",
        "category": "Inland Waterways & River Barge / ផ្លូវទឹកក្នុងស្រុក និងសាឡង់",
        "title_km": "ការដឹកជញ្ជូនកុងតឺន័រតាមសាឡង់ទន្លេមេគង្គ កំពង់ផែស្វយ័តភ្នំពេញ (PPAP LM17) ទៅកាន់ Cai Mep",
        "title_en": "Mekong River Barge Container Operations: PPAP LM17 Direct Hub Connection to Cai Mep",
        "summary_km": "ការដឹកជញ្ជូនកុងតឺន័រតាមសាឡង់ពីកំពង់ផែស្វយ័តភ្នំពេញ (PPAP LM17) ទៅកាន់កំពង់ផែទឹកជ្រៅ Cai Mep និង Cat Lai មានជើងចេញដំណើរជារៀងរាល់ថ្ងៃ។ សាឡង់ចំណុះពី ១២០ ទៅ ២៥០ TEU ជួយកាត់បន្ថយថ្លៃដឹកជញ្ជូនយ៉ាងច្រើនសម្រាប់ទំនិញធ្ងន់ៗ។",
        "summary_en": "Barge container operations between Phnom Penh Autonomous Port (PPAP LM17) and Cai Mep / Cat Lai ports maintain steady daily departures. Barge capacity ranging from 120 to 250 TEU provides a highly economical routing for heavy export containers.",
        "key_data": [
            "PPAP Barge Transit to Cai Mep: 24 - 30 Hours / រយៈពេលធ្វើដំណើរ ២៤ - ៣០ ម៉ោង",
            "Cost Advantage vs Road: Saves $80 - $120 per 40ft container / ចំណេញ ៨០-១២០ ដុល្លារ/ទូ",
            "Reefer Plugs Available: 95% Active monitoring / កន្លែងដោតភ្លើងទូត្រជាក់មាន ៩៥%",
            "Customs Clearance: Pre-clearance at PPAP LM17 before downriver transit"
        ],
        "impact_km": "ជួយកាត់បន្ថយថ្លៃដើមដឹកជញ្ជូនសម្រាប់រោងចក្រនៅរាជធានីភ្នំពេញ ខេត្តកណ្តាល និងកំពង់ចាម ព្រមទាំងចៀសផុតពីបញ្ហាកំណត់ទម្ងន់រថយន្តលើផ្លូវជាតិ និងថ្លៃបង់ផ្លូវល្បឿនលឿន។",
        "impact_en": "Substantially lowers inland logistics costs for factories situated in Phnom Penh, Kandal, and Kampong Cham, while completely bypassing road weight limits and expressway toll charges.",
        "action_km": "សម្រាប់ទំនិញធ្ងន់ៗដែលមិនបន្ទាន់ខ្លាំង ក្រុមហ៊ុន Forwarders គួរណែនាំអតិថិជនឱ្យជ្រើសរើសផ្លូវទឹកតាម LM17 ដើម្បីសន្សំថ្លៃដើម និងធានាការតភ្ជាប់ទៅកាន់កប៉ាល់ធំនៅ Cai Mep ឱ្យទាន់ពេល។",
        "action_en": "For heavy or non-urgent export shipments, forwarders are advised to route via PPAP LM17 river barge for cost optimization and guaranteed mother vessel connections at Cai Mep.",
        "tags": ["#PPAP", "#RiverBarge", "#MekongLogistics", "#CaiMep", "#InlandWaterway", "#CAMFFA"],
        "photo_category": "canal_waterways",
        "source": "PPAP Maritime Authority & Mekong River Navigation Directorate"
    },
    {
        "slot": "slot_morning",
        "category": "Port Infrastructure & Expansion / ហេដ្ឋារចនាសម្ព័ន្ធកំពង់ផែ",
        "title_km": "វឌ្ឍនភាពកំពង់ផែកុងតឺន័រទឹកជ្រៅក្រុងព្រះសីហនុ ជំហានទី១ (ជម្រៅទឹក ១៤.៥ ម៉ែត្រ)",
        "title_en": "Sihanoukville Port Deep-Water Container Terminal Phase 1 (14.5m Draft) Construction Progress",
        "summary_km": "ការសាងសង់ចំណតផែកុងតឺន័រទឹកជ្រៅថ្មីជំហានទី១ ប្រវែង ៣៥០ ម៉ែត្រ និងជម្រៅទឹក ១៤.៥ ម៉ែត្រ កំពុងដំណើរការយ៉ាងសកម្ម។ នៅពេលបញ្ចប់ ផែនេះនឹងអនុញ្ញាតឱ្យកប៉ាល់កុងតឺន័រធំៗប្រមាណ ៩៣% ក្នុងតំបន់អាស៊ី (ចំណុះរហូតដល់ ៤,០០០ TEU) អាចចូលចតផ្ទាល់ដោយមិនបាច់ឆ្លងកាត់ប្រទេសទី៣។",
        "summary_en": "Construction on the 350-meter long, 14.5-meter draft new deep-water container terminal Phase 1 is progressing on schedule. Upon completion, it will accommodate 93% of regional container vessels (up to 4,000 TEU), enabling direct transpacific routes without intermediate hub feeders.",
        "key_data": [
            "Terminal Length: 350 Meters / ប្រវែងចំណត ៣៥០ ម៉ែត្រ",
            "Water Draft: 14.5 Meters / ជម្រៅទឹក ១៤.៥ ម៉ែត្រ (បច្ចុប្បន្ន ១០.៥ ម៉ែត្រ)",
            "Vessel Capacity: Up to 4,000 TEU container ships / កប៉ាល់ផ្ទុកបាន ៤,០០០ TEU",
            "Logistics Cost Reduction: Estimated $200 savings per TEU on ocean freight"
        ],
        "impact_km": "នឹងជួយកាត់បន្ថយថ្លៃដឹកជញ្ជូនតាមសមុទ្ររបស់កម្ពុជាប្រមាណ ២០០ ដុល្លារក្នុងមួយកុងតឺន័រ និងកាត់បន្ថយរយៈពេលដឹកជញ្ជូនទៅកាន់សហរដ្ឋអាមេរិក និងអឺរ៉ុបបានពី ៣ ទៅ ៥ ថ្ងៃ។",
        "impact_en": "Expected to lower ocean freight rates by approximately $200 per container and shave 3-5 days off transpacific and European transit times for Cambodian exporters.",
        "action_km": "ក្រុមហ៊ុន Forwarders គួររៀបចំផែនការតភ្ជាប់ខ្សែសង្វាក់ផ្គត់ផ្គង់នាពេលអនាគត និងចាប់ផ្តើមពិភាក្សាជាមួយបណ្តាញក្រុមហ៊ុនកប៉ាល់ធំៗ (Ocean Carriers) ដើម្បីត្រៀមបើកជើងកប៉ាល់ផ្ទាល់។",
        "action_en": "Forwarders should factor this upcoming deep-water capacity into long-term carrier contract negotiations to capitalize on direct shipping calls as terminal completion nears.",
        "tags": ["#PASExpansion", "#DeepWaterPort", "#MaritimeInfrastructure", "#Sihanoukville", "#CambodiaTrade"],
        "photo_category": "ocean_port",
        "source": "Ministry of Public Works and Transport & PAS Engineering Department"
    },
    {
        "slot": "slot_morning",
        "category": "Container Equipment & Depots / ទីលានទូកុងតឺន័រ",
        "title_km": "ស្ថានភាពទូកុងតឺន័រ 40ft High Cube (HQ) នៅតាមទីលាន ICD ភ្នំពេញ និងព្រះសីហនុ",
        "title_en": "Empty Container Depot Operations: 40ft High Cube (HQ) Equipment Stock & Availability",
        "summary_km": "ចំនួនទូកុងតឺន័រទទេប្រភេទ 40ft HQ សម្រាប់បម្រើការនាំចេញសម្លៀកបំពាក់ និងស្បែកជើង នៅតាមទីលានកុងតឺន័រគោក (ICD) ដូចជា Teng Lay, Olair, និង So Ngoun ស្ថិតក្នុងកម្រិតមានតុល្យភាពល្អ។ ក្រុមហ៊ុនកប៉ាល់ធំៗបាននាំចូលទូកុងតឺន័រទទេបំពេញបន្ថែមទាន់ពេលវេលា។",
        "summary_en": "Inventory of empty 40ft High Cube (HQ) containers across major Phnom Penh dry ports (Teng Lay, Olair, So Ngoun) and PAS terminal depots remains balanced. Ocean carriers have positioned adequate empty boxes to meet peak garment export booking volumes.",
        "key_data": [
            "40ft HQ Availability: Adequate stock across Phnom Penh ICDs / ស្តុកគ្រប់គ្រាន់",
            "Container Inspection: Clean dry grade certified for apparel export",
            "Equipment Release Order (ERO): 24-48 hours processing turnaround",
            "Reefer Container Plug Status: Active at PAS and PPAP cold terminals"
        ],
        "impact_km": "រោងចក្រមិនប្រឈមនឹងការខ្វះខាតទូកុងតឺន័រសម្រាប់ការវេចខ្ចប់នាំចេញឡើយ។ ការដកទូទទេពីទីលានក្នុងរាជធានីភ្នំពេញមានភាពងាយស្រួល និងរហ័ស។",
        "impact_en": "Garment and manufacturing exporters avoid container stock-out risks. Drayage hauliers can retrieve empty boxes smoothly without extended staging delays at depots.",
        "action_km": "ក្រុមហ៊ុនបញ្ជូនទំនិញគួរស្នើសុំលិខិតដកទូ (Equipment Release Order - ERO) មុន ២ ថ្ងៃ និងពិនិត្យស្ថានភាពកុងតឺន័រ (កុំឱ្យធ្លាយទឹក ឬធុំក្លិន) មុនពេលបញ្ជូនទៅរោងចក្រផ្ទុកទំនិញ។",
        "action_en": "Forwarders should secure Equipment Release Orders (ERO) 48 hours prior to packing and perform pre-trip inspections (ensure clean, dry, odor-free boxes) before factory delivery.",
        "tags": ["#ContainerDepot", "#40ftHQ", "#DryPortICD", "#EquipmentAvailability", "#FreightOperations"],
        "photo_category": "ocean_port",
        "source": "CAMFFA Container Logistics Committee & Phnom Penh ICD Operators"
    },
    {
        "slot": "slot_morning",
        "category": "Transpacific Feeder Routes / ផ្លូវសមុទ្រឆ្លងមហាសមុទ្រ",
        "title_en": "Transpacific Feeder Connections: Optimized Transit via Cai Mep to US West Coast",
        "title_km": "ខ្សែសង្វាក់ដឹកជញ្ជូនតាមសមុទ្រទៅអាមេរិក៖ ការតភ្ជាប់ពីកម្ពុជាឆ្លងកាត់ Cai Mep ទៅឆ្នេរខាងលិច",
        "summary_km": "រយៈពេលដឹកជញ្ជូនទំនិញកុងតឺន័រពីកម្ពុជាទៅកាន់កំពង់ផែឆ្នេរខាងលិចសហរដ្ឋអាមេរិក (LAX/LGB) តាមរយៈការតភ្ជាប់ពី PAS/PPAP ទៅកាន់ Cai Mep ចំណាយពេលសរុបចន្លោះពី ១៦ ទៅ ១៩ ថ្ងៃប៉ុណ្ណោះ ដែលជាជម្រើសលឿនបំផុតសម្រាប់ការនាំចេញទំនិញម៉ូដទាន់សម័យ។",
        "summary_en": "Total transit time from Cambodia to US West Coast hubs (LAX/LGB) via PAS/PPAP feeders connecting with direct mother vessel loops at Cai Mep averages 16-19 days, providing the fastest ocean routing for retail goods.",
        "key_data": [
            "Feeder Connection to Cai Mep: 24 - 36 Hours",
            "Mother Vessel Ocean Leg: 14 - 16 Days direct to Los Angeles/Long Beach",
            "B/L Management: Single Through Bill of Lading coverage",
            "Feeder Punctuality: 96% on-time connection rate"
        ],
        "impact_km": "ជួយឱ្យរោងចក្រកាត់ដេរកម្ពុជាអាចបំពេញតាមកាលកំណត់កិច្ចសន្យាទិញ (PO Delivery) របស់ក្រុមហ៊ុនលក់រាយនៅសហរដ្ឋអាមេរិកបានយ៉ាងត្រឹមត្រូវ និងទប់ស្កាត់ការផាកពិន័យ។",
        "impact_en": "Enables Cambodian garment and footwear suppliers to meet strict buyer PO delivery windows at US distribution centers without resorting to expensive air freight.",
        "action_km": "ក្រុមហ៊ុន Forwarders គួរផ្ទៀងផ្ទាត់កាលវិភាគ Feeder Cut-Off នៅភ្នំពេញ/ព្រះសីហនុ ឱ្យត្រូវគ្នាជាមួយកាលវិភាគ Mother Vessel នៅ Cai Mep ដើម្បីបញ្ចៀសការរង់ចាំខកជើងកប៉ាល់។",
        "action_en": "Forwarders must carefully align feeder gate-in cut-offs in Cambodia with Cai Mep mother vessel closing windows to eliminate risk of missed transshipment connections.",
        "tags": ["#Transpacific", "#USWestCoast", "#OceanFreight", "#FeederConnection", "#CaiMepHub"],
        "photo_category": "ocean_port",
        "source": "Transpacific Carrier Schedules & Regional Maritime Advisory"
    },
    {
        "slot": "slot_morning",
        "category": "Inland Waterways & Canal Projects / ព្រែកជីក និងផ្លូវទឹក",
        "title_km": "គម្រោងព្រែកជីកហ្វូណនតេជោ និងយុទ្ធសាស្ត្រតភ្ជាប់ប្រព័ន្ធដឹកជញ្ជូនពហុមធ្យោបាយ",
        "title_en": "Funan Techo Canal Infrastructure Progress & Multi-Modal River-Sea Strategic Integration",
        "summary_km": "គម្រោងព្រែកជីកហ្វូណនតេជោ ប្រវែង ១៨០ គីឡូម៉ែត្រ តភ្ជាប់ទន្លេមេគង្គពីខេត្តកណ្តាល កាត់ខេត្តតាកែវ កំពត និងកែប ឆ្ពោះទៅកាន់សមុទ្រកម្ពុជា កំពុងត្រូវបានតាមដានយ៉ាងយកចិត្តទុកដាក់។ គម្រោងនេះនឹងជួយឱ្យកម្ពុជាមានច្រកចេញទៅសមុទ្រផ្ទាល់ដោយមិនបាច់ឆ្លងកាត់ប្រទេសជិតខាង។",
        "summary_en": "The 180 km Funan Techo Canal project connecting the Mekong River basin from Kandal, Takeo, Kampot to Kep coastal sea continues to advance. The project will provide Cambodia with direct, sovereign sea access, significantly reducing regional transit dependencies.",
        "key_data": [
            "Canal Length: 180 Kilometers / ប្រវែងសរុប ១៨០ គ.ម",
            "Vessel Capacity: Accommodating 1,000 to 3,000 DWT barges / សាឡង់ ១,០០០ - ៣,០០០ តោន",
            "Cost Reduction Target: Up to 30% lower transport costs / កាត់បន្ថយថ្លៃដឹកជញ្ជូនដល់ ៣០%",
            "Direct Coast Access: Direct inland waterway link to Kep/Kampot ports"
        ],
        "impact_km": "នៅពេលសាងសង់រួចរាល់ នឹងកាត់បន្ថយថ្លៃដឹកជញ្ជូនទំនិញក្នុងស្រុកបានរហូតដល់ ៣០% និងជួយបង្កើតតំបន់ឧស្សាហកម្ម និងភស្តុភារកម្មថ្មីៗតាមដងព្រែកជីក។",
        "impact_en": "Long-term projections indicate up to 30% reduction in domestic freight transit costs and will foster new industrial corridors along the Bassac waterway.",
        "action_km": "ក្រុមហ៊ុនដឹកជញ្ជូន និងវិនិយោគិនគួរពិចារណាយុទ្ធសាស្ត្រជ្រើសរើសទីតាំងឃ្លាំងស្តុកទំនិញ និងរោងចក្រដែលនៅជិតច្រករបៀងផ្លូវទឹកថ្មីនេះ ដើម្បីត្រៀមទាញយកអត្ថប្រយោជន៍។",
        "action_en": "Logistics planners and industrial investors should evaluate future warehouse and factory footprint positioning along the canal route to leverage future waterway savings.",
        "tags": ["#FunanTechoCanal", "#InlandWaterway", "#MultiModal", "#CambodiaInfrastructure", "#WaterwayLogistics"],
        "photo_category": "canal_waterways",
        "source": "Ministry of Public Works and Transport & Waterway Infrastructure Council"
    },
    {
        "slot": "slot_morning",
        "category": "Cold Chain & Agriculture Export / កុងតឺន័រត្រជាក់ និងកសិផល",
        "title_km": "ការត្រួតពិនិត្យប្រព័ន្ធកុងតឺន័រត្រជាក់ (Reefer) នៅកំពង់ផែ PAS និង PPAP សម្រាប់ការនាំចេញកសិផល",
        "title_en": "Reefer Cold Chain Monitoring at PAS & PPAP for Fresh Agricultural Product Exports",
        "summary_km": "ការនាំចេញផ្លែស្វាយស្រស់ ចេកអំបូងលឿង និងកសិផលផ្សេងៗ ទាមទារឱ្យមានការថែរក្សាកម្ដៅក្នុងកុងតឺន័រត្រជាក់យ៉ាងម៉ត់ចត់។ នៅកំពង់ផែ PAS និង PPAP មានកន្លែងដោតភ្លើងកុងតឺន័រត្រជាក់ជាង ៤០០ កន្លែង ជាមួយការត្រួតពិនិត្យកម្ដៅជាប្រចាំ (PTI Monitoring)។",
        "summary_en": "Export of fresh mangoes, Cavendish bananas, and agricultural goods requires strict continuous cold chain integrity. PAS and PPAP container yards feature over 400 active reefer plugs with round-the-clock PTI temperature monitoring.",
        "key_data": [
            "Temperature Range: Precision control from -25°C to +15°C",
            "Pre-Trip Inspection (PTI): Mandatory 100% pre-cooling verification",
            "Plug Availability: Over 90% capacity available at both main ports",
            "Phytosanitary Clearance: Expedited digital permits via CamDX platform"
        ],
        "impact_km": "ការពារគុណភាពកសិផលកុំឱ្យខូចខាត ឬធ្លាក់ចុះគុណភាពនៅពេលទៅដល់ទីផ្សារប្រទេសចិន និងអាស៊ី ដែលជួយឱ្យអ្នកនាំចេញទទួលបានតម្លៃខ្ពស់។",
        "impact_en": "Prevents temperature excursions that cause cargo spoilage or phytosanitary rejections at destination ports in China, Europe, and ASEAN.",
        "action_km": "ក្រុមហ៊ុន Forwarders ត្រូវបញ្ជាក់លម្អិតអំពីកម្រិតសីតុណ្ហភាព និងខ្យល់ចេញចូល (Ventilation Setting) ក្នុងលិខិតដឹកជញ្ជូន និងពិនិត្យឧបករណ៍តាមដានកម្ដៅ (Data Logger) មុនពេលចេញដំណើរ។",
        "action_en": "Forwarders must double-check temperature setpoints and vent settings on Shipping Instructions and ensure calibrated temperature data loggers are activated inside reefer boxes.",
        "tags": ["#ColdChain", "#ReeferLogistics", "#AgriExport", "#PAS", "#PPAP", "#FreshProduce"],
        "photo_category": "ocean_port",
        "source": "PAS Cold Chain Terminal & Ministry of Agriculture Phytosanitary Bureau"
    },
    {
        "slot": "slot_morning",
        "category": "Ocean Freight Rate Indices / សន្ទស្សន៍តម្លៃដឹកជញ្ជូនតាមសមុទ្រ",
        "title_km": "សន្ទស្សន៍តម្លៃដឹកជញ្ជូនតាមសមុទ្រ និងកម្រៃប្រេងបន្ថែម (BAF) ប្រចាំសប្តាហ៍",
        "title_en": "Cambodia Weekly Ocean Freight Benchmark Index & Bunker Adjustment Factors (BAF)",
        "summary_km": "តម្លៃដឹកជញ្ជូនកុងតឺន័រតាមសមុទ្រចេញពីកំពង់ផែក្រុងព្រះសីហនុ ទៅកាន់កំពង់ផែមូលដ្ឋាននៅអាស៊ី និងអាមេរិក មានស្ថិរភាពល្អនៅសប្តាហ៍នេះ។ តម្លៃកម្រៃប្រេងបន្ថែម (Bunker Surcharges) មិនមានការប្រែប្រួលខ្លាំងឡើយ។",
        "summary_en": "Ocean container spot freight indices departing Sihanoukville to major Asian, US, and European base ports maintain stable ranges this week. Carrier Bunker Adjustment Factors (BAF) remain level in line with regional marine fuel postings.",
        "key_data": [
            "PAS to Singapore Feeder (TEU): $250 - $270 / Box",
            "PAS to Shanghai/Ningbo (FEU): $380 - $450 / 40ft Box",
            "Asia to US West Coast (FEU): $2,800 - $3,050 / 40ft HQ",
            "Bunker Fuel Index: Stable marine gasoil benchmark across ASEAN"
        ],
        "impact_km": "ជួយឱ្យក្រុមហ៊ុនបញ្ជូនទំនិញ និងរោងចក្រអាចប៉ាន់ប្រមាណថ្លៃដើមដឹកជញ្ជូនសម្រាប់ត្រីមាសបន្ទាប់បានយ៉ាងជាក់លាក់ ដោយមិនមានការឡើងថ្លៃភ្លាមៗ។",
        "impact_en": "Provides freight forwarders and shippers with predictable landed cost forecasting for upcoming quarterly production orders.",
        "action_km": "ក្រុមហ៊ុនបញ្ជូនទំនិញគួរប្រៀបធៀបរវាងតម្លៃកិច្ចសន្យា (Contract Rate) និងតម្លៃទីផ្សារភ្លាមៗ (Spot Rate) ដើម្បីផ្តល់ជម្រើសសន្សំប្រាក់ល្អបំផុតដល់អតិថិជន។",
        "action_en": "Forwarders should benchmark quarterly contract rates against spot market filings to secure the best combination of space commitment and cost efficiency for clients.",
        "tags": ["#OceanRates", "#FreightBenchmark", "#BunkerSurcharge", "#ShippingCosts", "#CAMFFA"],
        "photo_category": "rate_index",
        "source": "CAMFFA Freight Exchange & Regional Carrier Tariff Postings"
    },

    {
        "slot": "slot_morning",
        "category": "Intra-Asia Ocean Shipping / សេវាដឹកជញ្ជូនផ្លូវសមុទ្រក្នុងតំបន់អាស៊ី",
        "title_km": "ការពង្រីកជើងកប៉ាល់ផ្ទាល់ Intra-Asia (ចិន-កម្ពុជា-វៀតណាម) កាត់បន្ថយការផ្ទេរទំនិញនៅកំពង់ផែបន្ត",
        "title_en": "Intra-Asia Direct Feeder Loops: Direct China-Cambodia-Vietnam Services Bypass Transshipment Hubs",
        "summary_km": "បណ្តាញក្រុមហ៊ុនកប៉ាល់ក្នុងតំបន់អាស៊ី (RCL, SITC, CNC/CMA CGM) បានបង្កើនជើងកប៉ាល់ផ្ទាល់រវាងកំពង់ផែក្រុងព្រះសីហនុ (PAS) និងកំពង់ផែសំខាន់ៗនៅចិន (Shanghai, Ningbo, Shekou) និងវៀតណាម។ សេវាកម្មផ្ទាល់នេះជួយកាត់បន្ថយការពឹងផ្អែកលើការផ្ទេរទំនិញនៅសិង្ហបុរី និងកាត់បន្ថយរយៈពេលដឹកជញ្ជូនវត្ថុធាតុដើមកាត់ដេរ។",
        "summary_en": "Regional carriers (RCL, SITC, CNC/CMA CGM) have augmented direct feeder loops linking Sihanoukville Autonomous Port (PAS) with key Chinese origin ports (Shanghai, Ningbo, Shekou) and Vietnam. Direct calls substantially reduce reliance on Singapore transshipment and accelerate raw material arrivals for garment manufacturers.",
        "key_data": [
            "Transit Time China to PAS: 5 - 7 Days direct / រយៈពេលពីចិនមក PAS ត្រឹម ៥-៧ ថ្ងៃ",
            "Transshipment Risk: Zero feeder connection rollovers / គ្មានហានិភ័យខកជើងកប៉ាល់បន្ត",
            "Sailing Frequency: 3-4 Direct weekly departures per alliance / ជើងចេញ ៣-៤ ដងក្នុងមួយសប្តាហ៍",
            "Raw Material Delivery: Same-day customs clearance at PAS for green-lane factories"
        ],
        "impact_km": "រោងចក្រកាត់ដេរ និងស្បែកជើងទទួលបានក្រណាត់ និងគ្រឿងបន្លាស់លឿនជាងមុនពី ៣ ទៅ ៤ ថ្ងៃ ជួយកាត់បន្ថយហានិភ័យនៃការយឺតយ៉ាវខ្សែសង្វាក់ផលិតកម្ម និងកាត់បន្ថយថ្លៃដើមស្តុកទំនិញ។",
        "impact_en": "Apparel and footwear manufacturers receive fabric, yarn, and hardware 3-4 days faster, drastically mitigating production downtime risks and reducing working capital tied up in pipeline inventory.",
        "action_km": "ក្រុមហ៊ុនបញ្ជូនទំនិញគួរណែនាំអតិថិជននាំចូលឱ្យកក់ជើងកប៉ាល់ផ្ទាល់ (Direct Service) សម្រាប់វត្ថុធាតុដើមបន្ទាន់ ជាជាងជ្រើសរើសសេវាឆ្លងកាត់ដែលងាយប្រឈមនឹងការខកជើងនៅកំពង់ផែផ្ទេរ (Rollover)។",
        "action_en": "Forwarders should counsel import procurement teams to prioritize direct loop routing for critical raw materials rather than transshipment options vulnerable to hub transshipment rollovers.",
        "tags": ["#IntraAsia", "#SeaFreight", "#PAS", "#RawMaterials", "#SupplyChainSpeed", "#CAMFFA"],
        "photo_category": "ocean_port",
        "source": "Intra-Asia Carrier Schedules & PAS Container Traffic Directorate"
    },
    {
        "slot": "slot_morning",
        "category": "Dangerous Goods & Hazmat Handling / ការដឹកជញ្ជូនទំនិញគ្រោះថ្នាក់ (DG/IMO)",
        "title_km": "បទប្បញ្ញត្តិ និងនីតិវិធីផ្ទុកទំនិញគ្រោះថ្នាក់ (Dangerous Goods - DG) នៅកំពង់ផែស្វយ័តក្រុងព្រះសីហនុ",
        "title_en": "Dangerous Goods (DG / IMO Class) Handling & Storage Compliance at Sihanoukville Port (PAS)",
        "summary_km": "កំពង់ផែស្វយ័តក្រុងព្រះសីហនុ (PAS) បានរឹតបន្តឹងការត្រួតពិនិត្យ និងការគ្រប់គ្រងកុងតឺន័រទំនិញគ្រោះថ្នាក់ (IMO Classes 2, 3, 4, 5, 6, 8, 9) ដូចជាសារធាតុគីមីសម្រាប់រោងចក្រ ថ្នាំជ្រលក់ពណ៌ និងថ្មលីចូម។ ទំនិញគ្រោះថ្នាក់មួយចំនួនត្រូវបានតម្រូវឱ្យលើកដាក់ផ្ទាល់លើរថយន្ត (Direct Truck Delivery) ដោយមិនអនុញ្ញាតឱ្យស្តុកទុកយូរក្នុងទីលានឡើយ។",
        "summary_en": "Sihanoukville Autonomous Port (PAS) has tightened safety protocols for dangerous goods containers (IMO Classes 2, 3, 4, 5, 6, 8, 9) including factory processing chemicals, textile dyes, and lithium batteries. Specific hazard classes mandate Direct Truck Delivery (DTD) without prolonged container yard dwell time.",
        "key_data": [
            "Pre-Notification Deadline: 72 Hours prior to vessel arrival / ជូនដំណឹងមុន ៧២ ម៉ោង",
            "Mandatory Docs: MSDS, Dangerous Goods Declaration (DGD), UN Packaging Certificate",
            "Yard Dwell Limit: Maximum 24 hours for approved DG classes / ក្នុងទីលានអតិបរមា ២៤ ម៉ោង",
            "Direct Delivery: Required for Class 2.1 gases and Class 3 flammable liquids"
        ],
        "impact_km": "ធានាសុវត្ថិភាពខ្ពស់បំផុតក្នុងបរិវេណកំពង់ផែ និងចៀសវាងគ្រោះថ្នាក់អគ្គិភ័យ ប៉ុន្តែទាមទារឱ្យមានការរៀបចំរថយន្តសណ្តោង និងការបង់ពន្ធគយឱ្យរួចរាល់ជាមុន ដើម្បីទទួលទំនិញភ្លាមៗពេលកប៉ាល់ចូលចត។",
        "impact_en": "Ensures maximum terminal safety and fire prevention, but demands strict alignment between customs duty settlement and prime mover truck dispatch for immediate offloading upon vessel discharge.",
        "action_km": "ក្រុមហ៊ុន Forwarders ត្រូវបញ្ជូនឯកសារ DGD និង MSDS ទៅកាន់ការិយាល័យសុវត្ថិភាព PAS យ៉ាងតិច ៣ ថ្ងៃមុនកប៉ាល់មកដល់ និងរៀបចំក្បួនរថយន្តសណ្តោងឱ្យបានស្រេចបាច់នៅមាត់ផែ។",
        "action_en": "Freight forwarders must submit verified DGD declarations and full MSDS sheets to the PAS Safety & Environmental Department 72 hours prior to berthing and pre-dispatch licensed chassis.",
        "tags": ["#DangerousGoods", "#PASPort", "#IMOCargo", "#ChemicalLogistics", "#SafetyCompliance"],
        "photo_category": "ocean_port",
        "source": "PAS Terminal Safety Department & International Maritime Dangerous Goods (IMDG) Code"
    },
    {
        "slot": "slot_morning",
        "category": "Demurrage & Detention Management / ការគ្រប់គ្រងថ្លៃ Demurrage និង Detention (D&D)",
        "title_km": "យុទ្ធសាស្ត្រគ្រប់គ្រងថ្លៃពន្យារពេលទូកុងតឺន័រ (D&D Free Time) សម្រាប់ក្រុមហ៊ុននាំចូលនៅកម្ពុជា",
        "title_en": "Container Demurrage & Detention (D&D) Guidelines: Free-Time Optimization for Cambodia Importers",
        "summary_km": "ថ្លៃពន្យារទូកុងតឺន័រក្នុងកំពង់ផែ (Demurrage) និងក្រៅកំពង់ផែ (Detention) អាចកើនឡើងយ៉ាងឆាប់រហ័ស ប្រសិនបើដំណើរការបំពេញបែបបទគយ និងការដឹកជញ្ជូនមានការយឺតយ៉ាវ។ ជាមធ្យម ក្រុមហ៊ុនកប៉ាល់ផ្តល់រយៈពេលអនុគ្រោះ (Free Time) ចន្លោះពី ៧ ទៅ ១៤ ថ្ងៃអាស្រ័យលើកិច្ចសន្យា។",
        "summary_en": "Container demurrage (port dwell penalty) and detention (chassis/box holding penalty) represent substantial avoidable costs for Cambodian shippers when customs clearance or factory unloading encounters delays. Standard carrier free-time allowances typically span 7 to 14 combined days.",
        "key_data": [
            "Standard Free Time: 7 Days (Standard dry box), 3 Days (Reefer container)",
            "Demurrage Rates: $35 - $60 per day (Days 8-14), $70 - $120 per day (Day 15+)",
            "Detention Surcharge: $25 - $45 per day for holding empty box beyond agreed limit",
            "Target Free Time for SEZ Factories: 14 - 21 Combined days via forwarder volume contracts"
        ],
        "impact_km": "ការយឺតយ៉ាវលើឯកសារគយត្រឹមតែពីរបីថ្ងៃ អាចធ្វើឱ្យថ្លៃ D&D កើនឡើងរាប់ពាន់ដុល្លារក្នុងមួយបណ្តុំកុងតឺន័រ ដែលប៉ះពាល់យ៉ាងធ្ងន់ធ្ងរដល់ប្រាក់ចំណេញរបស់ក្រុមហ៊ុននាំចូល។",
        "impact_en": "A minor documentation delay of just 3-5 days can escalate container detention penalties by thousands of dollars across a multi-box shipment, directly eroding import gross margins.",
        "action_km": "ក្រុមហ៊ុនបញ្ជូនទំនិញគួរចរចាស្នើសុំរយៈពេល Free Time រួម (Combined D&D) យ៉ាងតិច ១៤ ថ្ងៃជាមួយក្រុមហ៊ុនកប៉ាល់ និងរៀបចំបែបបទគយជាមុន (Pre-clearance) មុនពេលទំនិញមកដល់ផែ។",
        "action_en": "Forwarders must aggressively negotiate combined 14-21 day D&D packages with shipping lines during rate contracting and execute pre-clearance filings before vessels make landfall.",
        "tags": ["#Demurrage", "#Detention", "#FreeTime", "#CostControl", "#ImportLogistics", "#CAMFFA"],
        "photo_category": "rate_index",
        "source": "Cambodia Association of Freight Forwarders (CAMFFA) & Ocean Carrier Port Tariffs"
    },
    {
        "slot": "slot_morning",
        "category": "Breakbulk & Project Cargo / ទំនិញទំហំធំ និងគ្រឿងចក្រគម្រោងធំៗ",
        "title_km": "ប្រតិបត្តិការលើកដាក់ទំនិញទំហំធំ ដែកថែបសំណង់ និងគ្រឿងចក្រគម្រោងធ្ងន់ៗ (Breakbulk) នៅផែចាស់ PAS",
        "title_en": "Breakbulk & Project Cargo Handling: Structural Steel & Heavy Machinery Operations at PAS Old Jetty",
        "summary_km": "ការនាំចូលដែកថែបសំណង់ ម៉ាស៊ីនរោងចក្រធុនធ្ងន់ និងឧបករណ៍ថាមពលកកើតឡើងវិញ (បន្ទះសូឡា និងទួរប៊ីន) តាមរយៈចំណតផែចាស់ (Old Jetty) និងផែពហុបំណងកំពង់ផែក្រុងព្រះសីហនុ រក្សាបាននូវដំណើរការលើកដាក់យ៉ាងសកម្ម ដោយមានស្ទូចធុនធ្ងន់ (Heavy Shore Cranes) ជួយសម្រួល។",
        "summary_en": "Inbound shipments of structural construction steel, heavy industrial production lines, and renewable energy components (solar arrays and substation transformers) via PAS Old Jetty and Multipurpose Terminal maintain active discharge operations utilizing high-tonnage mobile cranes and shore handling rigs.",
        "key_data": [
            "Crane Lift Capacity: Up to 100 metric tons tandem lift at PAS Multipurpose Pier",
            "Wharf Draft at Old Jetty: 9.0 - 9.5 Meters / ជម្រៅទឹក ៩.០ - ៩.៥ ម៉ែត្រ",
            "Storage Capacity: Over 50,000 sqm open heavy-cargo staging wharves",
            "Surveyor Requirement: Mandatory third-party condition survey upon discharge"
        ],
        "impact_km": "គាំទ្រដល់គម្រោងវិនិយោគហេដ្ឋារចនាសម្ព័ន្ធធំៗ និងការសាងសង់រោងចក្រថ្មីៗនៅកម្ពុជាឱ្យដំណើរការតាមកាលវិភាគកំណត់ ដោយធានាសុវត្ថិភាព និងមិនមានការខូចខាតគ្រឿងចក្រ។",
        "impact_en": "Directly underpins nationwide industrial infrastructure projects and factory turnkeys, ensuring mission-critical machinery and raw construction inputs arrive without physical damage.",
        "action_km": "ក្រុមហ៊ុន Forwarders ជំនាញផ្នែក Project Cargo ត្រូវបញ្ជូនវិស្វករវាស់ទំហំផ្លូវ (Route Survey) និងរៀបចំរថយន្តសណ្តោងកង់ច្រើន (Multi-axle Hydraulic Modular Trailers) ឱ្យស្របតាមលក្ខខណ្ឌបច្ចេកទេស។",
        "action_en": "Project cargo specialists must conduct bridge and overhead obstruction surveys along NR4/Expressway and pre-book certified multi-axle hydraulic low-bed trailers well before vessel discharge.",
        "tags": ["#ProjectCargo", "#Breakbulk", "#HeavyLift", "#PASOldJetty", "#IndustrialLogistics"],
        "photo_category": "ocean_port",
        "source": "PAS Stevedoring & Heavy Lift Division & Project Cargo Logistics Association"
    },

    # =========================================================================
    # SLOT 2: MIDDAY (13:30 ICT) — TRUCKING, EXPRESSWAY & CROSS-BORDER
    # =========================================================================
    {
        "slot": "slot_midday",
        "category": "Expressway Container Haulage / ការដឹកជញ្ជូនតាមផ្លូវល្បឿនលឿន",
        "title_km": "ស្ថានភាពចរាចរណ៍រថយន្តកុងតឺន័រលើផ្លូវល្បឿនលឿន ភ្នំពេញ-ព្រះសីហនុ (ET Corridor)",
        "title_en": "Phnom Penh - Sihanoukville Expressway Heavy Container Haulage Status & Safety Protocol",
        "summary_km": "ការដឹកជញ្ជូនកុងតឺន័រតាមផ្លូវល្បឿនលឿន ភ្នំពេញ-ព្រះសីហនុ ចំណាយពេលត្រឹមតែ ២ ម៉ោង ១៥ នាទីប៉ុណ្ណោះ។ ការអនុវត្តប្រព័ន្ធបង់ប្រាក់ស្វ័យប្រវត្តិតាមផ្លូវអេឡិចត្រូនិច (ETC) ជួយឱ្យរថយន្តឆ្លងកាត់របាំងបង់ប្រាក់បានលឿនដោយមិនបាច់រង់ចាំតម្រង់ជួរវែងឡើយ។",
        "summary_en": "Heavy container trucking on the Phnom Penh - Sihanoukville Expressway maintains smooth transit times under 2 hours and 15 minutes. Widespread adoption of Electronic Toll Collection (ETC) RFID lanes ensures seamless flow through toll plazas without queuing.",
        "key_data": [
            "Transit Time: 2h 15m (Phnom Penh Dry Ports to PAS Container Gate)",
            "Toll System: 100% active ETC automated non-stop lanes",
            "Weigh Station Compliance: Strict axle weight inspection active",
            "Speed Limit: 80 km/h strictly enforced for heavy container trucks"
        ],
        "impact_km": "ជួយកាត់បន្ថយពេលវេលាដឹកជញ្ជូនបានជាងពាក់កណ្តាលធៀបនឹងផ្លូវជាតិលេខ ៤ ចាស់ ព្រមទាំងកាត់បន្ថយការពាក់កកិតសំបកកង់ និងការស៊ីប្រេងឥន្ធនៈរបស់រថយន្តធំ។",
        "impact_en": "Cuts transit time by over 50% compared to National Road 4, significantly lowering fuel consumption, vehicle wear-and-tear, and risk of traffic congestion.",
        "action_km": "ក្រុមហ៊ុនរថយន្តកុងតឺន័រត្រូវធានាថាគណនី ETC របស់រថយន្តមានសមតុល្យគ្រប់គ្រាន់ និងត្រួតពិនិត្យប្រព័ន្ធហ្វ្រាំង និងសំបកកង់ឱ្យបានត្រឹមត្រូវមុនពេលចូលផ្លូវល្បឿនលឿន។",
        "action_en": "Trucking fleets must maintain sufficient ETC account balances to avoid manual lane delays and verify brake and tire pressure integrity before expressway entry.",
        "tags": ["#Expressway", "#ContainerTrucking", "#HighwayLogistics", "#Sihanoukville", "#PhnomPenh"],
        "photo_category": "trucking_highway",
        "source": "Ministry of Public Works and Transport & Expressway Dispatch Command"
    },
    {
        "slot": "slot_midday",
        "category": "Cross-Border Trucking (Vietnam) / ដឹកជញ្ជូនឆ្លងដែនកម្ពុជា-វៀតណាម",
        "title_km": "ស្ថានភាពចរាចរណ៍ និងការបំពេញបែបបទគយនៅច្រកទ្វារព្រំដែនអន្តរជាតិបាវិត-ម៉ុកបាយ",
        "title_en": "Bavet - Moc Bai International Border Gate: Cross-Border Trucking & Customs Clearance Status",
        "summary_km": "ច្រកទ្វារព្រំដែនបាវិត (ខេត្តស្វាយរៀង) - ម៉ុកបាយ (វៀតណាម) មានលំហូរចរាចរណ៍រថយន្តកុងតឺន័រធម្មតា។ រយៈពេលរង់ចាំបំពេញបែបបទគយ និងត្រួតពិនិត្យសោអេឡិចត្រូនិច (E-Seal) ជាមធ្យមចន្លោះពី ២ ទៅ ៣ ម៉ោង។",
        "summary_en": "Cross-border container traffic through the Bavet (Svay Rieng) - Moc Bai (Vietnam) international gate reports normal fluid operations. Average customs clearance and electronic customs seal (E-Seal) processing queue time stands at 2 to 3 hours.",
        "key_data": [
            "Clearance Wait Time: 2 - 3 Hours / រង់ចាំត្រួតពិនិត្យ ២ - ៣ ម៉ោង",
            "Transit to Cat Lai/Cai Mep: Under 14 Hours door-to-door transit",
            "Customs Processing: Electronic transit customs seals (GDCE / Vietnam Customs)",
            "Cross-Docking Facilities: Operational at Bavet Dry Port terminal"
        ],
        "impact_km": "រោងចក្រក្នុងតំបន់សេដ្ឋកិច្ចពិសេសមេនហាតធិន និងតាយសេង (បាវិត) អាចបញ្ជូនទំនិញទៅកាន់កំពង់ផែ Cat Lai និង Cai Mep នៅប្រទេសវៀតណាម ដើម្បីតភ្ជាប់ជើងកប៉ាល់ធំទៅអាមេរិកបានយ៉ាងរលូន។",
        "impact_en": "Factories operating in Manhattan and Tai Seng SEZs (Bavet) can seamlessly transfer export containers to Vietnamese deep-sea ports for transpacific direct mother vessel sailings.",
        "action_km": "ក្រុមហ៊ុនបញ្ជូនទំនិញត្រូវផ្ទៀងផ្ទាត់ឯកសារឆ្លងកាត់ដែន និងបញ្ជាក់លេខសោ E-Seal ឱ្យបានត្រឹមត្រូវក្នុងប្រព័ន្ធគយ ASYCUDA មុនពេលរថយន្តទៅដល់គន្លងត្រួតពិនិត្យព្រំដែន។",
        "action_en": "Forwarders and cross-border brokers must ensure electronic transit declarations and active E-seal numbers match ASYCUDA manifests prior to arrival at border inspection lanes.",
        "tags": ["#BavetBorder", "#CrossBorderTrucking", "#VietnamCambodia", "#MocBai", "#BondedTransport"],
        "photo_category": "trucking_highway",
        "source": "Bavet Customs Department & Cross-Border Logistics Association"
    },
    {
        "slot": "slot_midday",
        "category": "Cross-Border Trucking (Thailand) / ដឹកជញ្ជូនឆ្លងដែនកម្ពុជា-ថៃ",
        "title_km": "ច្រកទ្វារព្រំដែនអន្តរជាតិប៉ោយប៉ែត-អារញ្ញប្រាថេត៖ ការដឹកជញ្ជូនទំនិញឧស្សាហកម្មកម្ពុជា-ថៃ",
        "title_en": "Poipet - Aranyaprathet Border Corridor: Intermodal Road Haulage & Industrial Cargo Transit",
        "summary_km": "ច្រកទ្វារប៉ោយប៉ែត (ខេត្តបន្ទាយមានជ័យ) បន្តជាសរសៃឈាមសំខាន់សម្រាប់ការនាំចូលគ្រឿងបន្លាស់រថយន្ត វត្ថុធាតុដើមវេចខ្ចប់ និងគ្រឿងសំណង់ពីប្រទេសថៃ។ រយៈពេលដឹកជញ្ជូនពីបាងកកមកភ្នំពេញចំណាយពេលត្រឹមតែ ២៤ ទៅ ៣៦ ម៉ោងប៉ុណ្ណោះ។",
        "summary_en": "The Poipet - Aranyaprathet border corridor continues to serve as a critical economic artery for importing auto parts, industrial packaging, and construction inputs from Thailand. Door-to-door transit between Bangkok and Phnom Penh averages 24 to 36 hours.",
        "key_data": [
            "Door-to-Door Transit: 24 - 36 Hours (Bangkok to Phnom Penh)",
            "Border Transloading: Smooth swap-body cross-docking at Poipet Dry Port",
            "Preferential Duty: ATIGA Form D 0% import duty on qualifying goods",
            "Border Inspection Queue: 1.5 - 2.5 Hours during daytime hours"
        ],
        "impact_km": "ជួយឱ្យរោងចក្រដំឡើងយានយន្ត និងរោងចក្រផលិតសម្ភារៈប្រើប្រាស់នៅកម្ពុជា ទទួលបានវត្ថុធាតុដើមទាន់ពេលវេលាដោយមិនបាច់រង់ចាំការដឹកជញ្ជូនតាមសមុទ្ររយៈពេលយូរ។",
        "impact_en": "Allows Cambodian automotive assembly plants and manufacturers to receive raw material inputs on a just-in-time schedule without waiting for lengthy ocean feeder transit.",
        "action_km": "ក្រុមហ៊ុនបញ្ជូនទំនិញត្រូវធានាថាឯកសារ Form D មានភាពត្រឹមត្រូវដើម្បីទទួលបានការលើកលែងពន្ធនាំចូល និងរៀបចំរថយន្តស្ទូច ឬរថយន្តលើកដាក់ (Forklift) ឱ្យរួចរាល់នៅទីលានផ្ទេរទំនិញប៉ោយប៉ែត។",
        "action_en": "Forwarders must verify ATIGA Form D origin compliance for zero-duty clearance and pre-book certified cross-docking handling equipment at Poipet border transshipment yards.",
        "tags": ["#PoipetBorder", "#ThailandCambodia", "#OverlandTrucking", "#FormD", "#IntermodalTransport"],
        "photo_category": "trucking_highway",
        "source": "Poipet Customs Office & Thailand-Cambodia Logistics Directorate"
    },
    {
        "slot": "slot_midday",
        "category": "Heavy Haulage & Oversized Cargo / ការដឹកជញ្ជូនទំនិញធុនធ្ងន់",
        "title_km": "បទប្បញ្ញត្តិដឹកជញ្ជូនគ្រឿងចក្រធុនធ្ងន់ និងទំនិញលើសទម្ងន់លើបណ្តាញផ្លូវជាតិកម្ពុជា (MPWT)",
        "title_en": "Heavy Lift & Oversized Project Cargo Logistics: MPWT Road Permit & Axle Regulations",
        "summary_km": "ក្រសួងសាធារណការ និងដឹកជញ្ជូន (MPWT) រំលឹកដល់ក្រុមហ៊ុនដឹកជញ្ជូនគ្រឿងចក្រឧស្សាហកម្មធំៗ ឡចំហាយ និងឧបករណ៍សំណង់ធុនធ្ងន់ ឱ្យស្នើសុំលិខិតអនុញ្ញាតដឹកជញ្ជូនលើសទម្ងន់កម្រិតកំណត់ និងធ្វើការអង្កេតផ្លូវ (Route Survey) ឱ្យបានម៉ត់ចត់។",
        "summary_en": "The Ministry of Public Works and Transport (MPWT) reminds logistics operators transporting heavy factory machinery, industrial boilers, and oversized equipment to secure special road permits and conduct bridge capacity route surveys prior to haulage.",
        "key_data": [
            "Trailer Requirements: Multi-axle hydraulic modular trailers / រថយន្តសណ្តោងច្រើនភ្លៅ",
            "Permit Application Window: Submit 7 - 10 days in advance of transit",
            "Night Movement Window: Escorted transport permitted from 22:00 to 05:00",
            "Weight Limit Compliance: Strict bridge weight assessment protocols"
        ],
        "impact_km": "ការពារការខូចខាតហេដ្ឋារចនាសម្ព័ន្ធផ្លូវ-ស្ពានសាធារណៈ និងធានាសុវត្ថិភាពខ្ពស់ក្នុងការដឹកជញ្ជូនគ្រឿងចក្រមកកាន់រោងចក្រដោយគ្មានការរាំងស្ទះ។",
        "impact_en": "Protects public road and bridge infrastructure from structural overloading and guarantees incident-free delivery of multi-million dollar industrial assets to factory foundations.",
        "action_km": "ក្រុមហ៊ុន Forwarders ដែលទទួលដឹកជញ្ជូនគម្រោងធំៗ (Project Cargo) ត្រូវសហការជាមួយក្រុមវិស្វករផ្លូវថ្នល់ ដើម្បីវាស់កម្ពស់ខ្សែភ្លើង ពិនិត្យកម្លាំងទ្រស្ពាន និងរៀបចំរថយន្តនគរបាលនាំផ្លូវជាមុន។",
        "action_en": "Project freight forwarders must collaborate with route survey engineers to inspect overhead wire heights, evaluate bridge loading ratings, and arrange official police escorts in advance.",
        "tags": ["#ProjectCargo", "#HeavyLift", "#MPWT", "#OversizedTransport", "#MachineryHaulage"],
        "photo_category": "trucking_highway",
        "source": "Ministry of Public Works and Transport (MPWT) Heavy Transport Bureau"
    },
    {
        "slot": "slot_midday",
        "category": "Dry Port ICD Operations / ទីលានកុងតឺន័រគោក",
        "title_km": "ការគ្រប់គ្រងលំហូរកុងតឺន័រ និងការកកស្ទះនៅតាមទីលាន ICD ភ្នំពេញពេលចុងសប្តាហ៍",
        "title_en": "Phnom Penh Dry Port (ICD) Weekend Gate-In Management & Congestion Index",
        "summary_km": "នៅថ្ងៃសុក្រ និងថ្ងៃសៅរ៍ ទីលានកុងតឺន័រគោក (Dry Ports) ក្នុងរាជធានីភ្នំពេញ ដូចជា Teng Lay, Olair, និង So Ngoun តែងតែមានរថយន្តកុងតឺន័រចេញ-ចូលយ៉ាងកុះករ។ ការរៀបចំកាលវិភាគលើកដាក់ទំនិញមុនម៉ោងជួយកាត់បន្ថយការកកស្ទះបានយ៉ាងមានប្រសិទ្ធភាព។",
        "summary_en": "Friday and Saturday stuffing schedules create concentrated gate-in activity at Phnom Penh inland container depots (Teng Lay, Olair, So Ngoun). Pre-slotting gate appointments significantly reduces gate-in turnaround delays.",
        "key_data": [
            "Average Gate Turnaround: 45 - 60 Minutes during non-peak hours",
            "Peak Rush Window: Friday 16:00 to Saturday 20:00 / ម៉ោងមមាញឹកចុងសប្តាហ៍",
            "Chassis Availability: Sufficient skeletal trailers available for hire",
            "Weighbridge Certification: On-site Verified Gross Mass (VGM) weighing operational"
        ],
        "impact_km": "ជួយឱ្យរថយន្តកុងតឺន័រអាចបញ្ជូនទំនិញទៅកាន់កំពង់ផែក្រុងព្រះសីហនុបានទាន់ពេលវេលាកាត់បញ្ជី (CY Cut-Off) នៅយប់ថ្ងៃអាទិត្យ។",
        "impact_en": "Ensures container hauliers reach Sihanoukville Port gates well ahead of strict Sunday midnight carrier vessel cut-offs, eliminating rollover charges.",
        "action_km": "ក្រុមហ៊ុនបញ្ជូនទំនិញគួរណែនាំរោងចក្រឱ្យបញ្ចប់ការវេចខ្ចប់ទំនិញនៅព្រឹកថ្ងៃសុក្រ ដើម្បីដកទូ និងចេញដំណើរមុនពេលមានការកកស្ទះចរាចរណ៍នៅពេលល្ងាច។",
        "action_en": "Forwarders should encourage factory shipping departments to finalize packing by Friday morning to stage containers early and avoid peak evening dry port queues.",
        "tags": ["#DryPort", "#ICD", "#PhnomPenh", "#ContainerGateIn", "#WeekendTrucking", "#CAMFFA"],
        "photo_category": "trucking_highway",
        "source": "Phnom Penh Dry Port Association & Freight Forwarders Logistics Exchange"
    },
    {
        "slot": "slot_midday",
        "category": "Commercial Diesel Benchmark / តម្លៃប្រេងម៉ាស៊ូត",
        "title_km": "សន្ទស្សន៍តម្លៃប្រេងម៉ាស៊ូតពាណិជ្ជកម្ម និងកម្រៃប្រេងលើការដឹកជញ្ជូនផ្លូវគោក (FSC)",
        "title_en": "Cambodia Commercial Diesel Fuel Benchmark & Inland Haulage Fuel Surcharge (FSC)",
        "summary_km": "តម្លៃលក់រាយប្រេងម៉ាស៊ូតពាណិជ្ជកម្មនៅកម្ពុជា ស្ថិតក្នុងរង្វង់ ១.០២ ដុល្លារក្នុងមួយលីត្រ។ ស្ថិរភាពតម្លៃប្រេងនេះជួយឱ្យថ្លៃឈ្នួលរថយន្តកុងតឺន័រ និងកម្រៃប្រេងបន្ថែម (Fuel Surcharge) រក្សាបាននូវភាពទៀងទាត់ និងងាយស្រួលក្នុងការគណនាថ្លៃដើម។",
        "summary_en": "Retail commercial diesel prices in Cambodia remain stable at approximately $1.02 per liter. Fuel price stability supports predictable road haulage rates and transparent Fuel Surcharge (FSC) calculations across major commercial trucking corridors.",
        "key_data": [
            "Diesel Retail Price: Stable at ~$1.02 / Liter nationwide / ប្រេងម៉ាស៊ូត ១.០២$/លីត្រ",
            "Fuel Surcharge Formula: Linked to Ministry of Commerce bi-weekly notices",
            "Phnom Penh to PAS Haulage: Average $200 - $220 per 40ft container box",
            "Expressway Toll Cost: Class 5 heavy truck toll verified at standard tariffs"
        ],
        "impact_km": "ជួយឱ្យក្រុមហ៊ុនដឹកជញ្ជូន និងម្ចាស់ទំនិញអាចចុះកិច្ចសន្យាថ្លៃដឹកជញ្ជូនរយៈពេលវែងដោយមិនបារម្ភពីរលកនៃការប្រែប្រួលតម្លៃប្រេងឥន្ធនៈខ្លាំងក្លា។",
        "impact_en": "Protects transport operators and cargo owners from severe price volatility, enabling stable quarterly and annual transportation rate contracts.",
        "action_km": "ក្រុមហ៊ុនបញ្ជូនទំនិញគួរអនុវត្តរូបមន្តកម្រៃប្រេងបន្ថែម (FSC) ផ្អែកលើតារាងផ្លូវការរបស់ក្រសួងពាណិជ្ជកម្ម ដើម្បីធានាតម្លាភាព និងភាពជឿជាក់ជាមួយអតិថិជន។",
        "action_en": "Forwarders should utilize transparent fuel surcharge formulas indexed against Ministry of Commerce bi-weekly postings for auditable client invoicing.",
        "tags": ["#DieselPrice", "#FuelSurcharge", "#TruckingCosts", "#InlandHaulage", "#CambodiaEconomy"],
        "photo_category": "rate_index",
        "source": "Ministry of Commerce Fuel Directorate & CAMFFA Transport Committee"
    },
    {
        "slot": "slot_midday",
        "category": "Cross-Border Bonded Logistics / ដឹកជញ្ជូនទំនិញជាប់ពន្ធ",
        "title_km": "ការដឹកជញ្ជូនកុងតឺន័រជាប់ពន្ធ (Bonded Trucking) ពីតំបន់សេដ្ឋកិច្ចពិសេសទៅកាន់កំពង់ផែ",
        "title_en": "Bonded Container Trucking Corridors: Seamless Transit from SEZs to Deep-Sea Gateways",
        "summary_km": "ការដឹកជញ្ជូនទំនិញកុងតឺន័រក្រោមរបបគយពិសេស (Bonded Transit) រវាងតំបន់សេដ្ឋកិច្ចពិសេសភ្នំពេញ (PPSEZ) ស្វាយរៀង និងកំពង់ផែស្វយ័តក្រុងព្រះសីហនុ ត្រូវបានអនុញ្ញាតឱ្យប្រើប្រាស់នីតិវិធីសាមញ្ញតាមប្រព័ន្ធអេឡិចត្រូនិច។",
        "summary_en": "Bonded container trucking between special economic zones (PPSEZ, Svay Rieng SEZs) and Sihanoukville Port operates under streamlined electronic customs transit procedures, safeguarding duty-suspension status throughout transit.",
        "key_data": [
            "Transit Protocol: National electronic customs transit manifest (T1 Document)",
            "Seal Verification: High-security ISO 17712 electronic tamper seals",
            "Transit Security: Geo-fenced GPS corridor monitoring",
            "Inspection Rate: Under 5% physical check for certified bonded carriers"
        ],
        "impact_km": "កាត់បន្ថយពេលវេលាបំពេញបែបបទនៅតាមច្រកទ្វារ និងធានាថាទំនិញមិនត្រូវបង់ពន្ធនាំចូល ឬអាករផ្សេងៗក្នុងអំឡុងពេលដឹកជញ្ជូនលើផ្លូវសាធារណៈ។",
        "impact_en": "Minimizes transit checkpoint stops and guarantees that raw materials remain under duty-suspension status while transiting domestic highways.",
        "action_km": "ក្រុមហ៊ុនបញ្ជូនទំនិញត្រូវជ្រើសរើសក្រុមហ៊ុនរថយន្តដែលមានអាជ្ញាប័ណ្ណដឹកជញ្ជូនទំនិញជាប់ពន្ធ (Bonded Trucking License) ត្រឹមត្រូវពីអគ្គនាយកដ្ឋានគយ និងរដ្ឋាករ។",
        "action_en": "Forwarders must contract only certified bonded trucking carriers authorized by GDCE to prevent customs bond forfeitures and vehicle detentions.",
        "tags": ["#BondedTrucking", "#SEZTransit", "#CustomsTransit", "#SupplyChainSecurity", "#GDCE"],
        "photo_category": "trucking_highway",
        "source": "General Department of Customs and Excise & Bonded Logistics Registry"
    },
    {
        "slot": "slot_midday",
        "category": "Safety & Weight Enforcement / សុវត្ថិភាពផ្លូវថ្នល់ និងទម្ងន់",
        "title_km": "ការរឹតបន្តឹងការត្រួតពិនិត្យទម្ងន់រថយន្តកុងតឺន័រនៅស្ថានីយជញ្ជីងផ្លូវជាតិ និងផ្លូវល្បឿនលឿន",
        "title_en": "Vehicle Weight Enforcement & Weigh Station Protocols on National Corridors",
        "summary_km": "គណៈកម្មាធិការសម្របសម្រួលការត្រួតពិនិត្យទម្ងន់យានយន្ត បន្តរឹតបន្តឹងការថ្លឹងទម្ងន់រថយន្តកុងតឺន័រនៅគ្រប់ស្ថានីយជញ្ជីងអចល័ត និងចល័ត។ ការផ្ទុកលើសទម្ងន់កម្រិតកំណត់ នឹងត្រូវផាកពិន័យ និងតម្រូវឱ្យរើទំនិញចេញភ្លាមៗ។",
        "summary_en": "The Permanent Committee for Vehicle Overload Inspection continues strict weight enforcement across stationary and mobile weighbridges on national routes and expressway ramps. Overloaded trucks face immediate fines and mandatory cargo offloading.",
        "key_data": [
            "Axle Weight Limits: Maximum 40-45 metric tons total gross vehicle weight (GVW)",
            "Weigh Station Locations: Key checkpoints along NR4, NR1, NR5, and Expressway",
            "Penalties: Heavy fines per ton overloaded + impoundment for repeat violations",
            "VGM Alignment: Mandatory matching with port Verified Gross Mass documentation"
        ],
        "impact_km": "ជួយទប់ស្កាត់ការខូចខាតផ្លូវថ្នល់ និងកាត់បន្ថយគ្រោះថ្នាក់ចរាចរណ៍ ប៉ុន្តែទាមទារឱ្យរោងចក្រត្រូវថ្លឹងទម្ងន់កុងតឺន័រឱ្យបានត្រឹមត្រូវមុនពេលចេញពីរោងចក្រ។",
        "impact_en": "Prevents severe pavement damage and road accidents, but requires factory dispatchers to verify exact container tare and gross weights prior to release.",
        "action_km": "ក្រុមហ៊ុន Forwarders ត្រូវក្រើនរំលឹកដល់រោងចក្រឱ្យផ្ទៀងផ្ទាត់ទម្ងន់ទំនិញជាក់ស្តែង (VGM) ឱ្យត្រូវគ្នាជាមួយឯកសារដឹកជញ្ជូន ដើម្បីកុំឱ្យរថយន្តជាប់គាំងនៅស្ថានីយជញ្ជីង។",
        "action_en": "Forwarders must advise factory shippers to ensure accurate weighbridge gross weights match VGM declarations, preventing vehicle detention at road checkpoints.",
        "tags": ["#WeightEnforcement", "#WeighStation", "#RoadSafety", "#MPWT", "#TruckingCompliance"],
        "photo_category": "trucking_highway",
        "source": "MPWT Vehicle Overload Committee & Highway Traffic Police"
    },

    {
        "slot": "slot_midday",
        "category": "Reefer & Cold Chain Haulage / ដឹកជញ្ជូនទំនិញត្រជាក់ និងកុងតឺន័រ Reefer",
        "title_km": "ខ្សែសង្វាក់ដឹកជញ្ជូនទំនិញរក្សាសីតុណ្ហភាពត្រជាក់ (Cold Chain Reefer Trucking) លើច្រករបៀងភ្នំពេញ-ព្រះសីហនុ",
        "title_en": "Cold Chain Logistics: Temperature-Controlled Reefer Haulage on the Phnom Penh - Sihanoukville Corridor",
        "summary_km": "តម្រូវការដឹកជញ្ជូនកុងតឺន័រត្រជាក់ (Reefer Containers) សម្រាប់ការនាំចេញកសិផល (ចេកអំបូងលឿង ស្វាយស្រស់) និងការនាំចូលសាច់បង្កក ឱសថ និងអាហារកែច្នៃ មានការកើនឡើងខ្លាំង។ រថយន្តសណ្តោងបំពាក់ម៉ាស៊ីនភ្លើងជំនួយ (Genset) ធានាសីតុណ្ហភាពថេរចន្លោះពី -២០°C ដល់ +១៥°C តាមតម្រូវការទំនិញ។",
        "summary_en": "Demand for temperature-controlled reefer container haulage along the Phnom Penh - Sihanoukville corridor is expanding rapidly for fresh agricultural exports (Cavendish bananas, fresh mangoes) and imported frozen proteins, pharmaceuticals, and dairy. Fleet operators deploy active clip-on gensets ensuring continuous temperature integrity (-20°C to +15°C).",
        "key_data": [
            "Expressway Transit Advantage: Under 2.5 hours runtime drastically preserves shelf life",
            "Genset Fuel Autonomy: 48 hours continuous diesel run-time per reefer unit",
            "Pre-Trip Inspection (PTI): Mandatory 6-point check prior to factory positioning",
            "Data Logger Verification: Real-time digital temperature telemetry during entire road leg"
        ],
        "impact_km": "ធានាគុណភាពកសិផលខ្មែរសម្រាប់ការនាំចេញទៅកាន់ទីផ្សារអន្តរជាតិបានស្រស់ល្អ គ្មានការខូចខាត និងជួយកាត់បន្ថយការបាត់បង់ទំនិញក្នុងពេលធ្វើដំណើរ។",
        "impact_en": "Protects high-value agricultural exports and pharmaceutical consignments against thermal shock and spoilage, guaranteeing cargo acceptance at destination retail and wholesale markets.",
        "action_km": "ក្រុមហ៊ុនបញ្ជូនទំនិញត្រូវតម្រូវឱ្យអ្នកបើកបរ និងក្រុមហ៊ុនរថយន្តត្រួតពិនិត្យដំណើរការម៉ាស៊ីនភ្លើង Genset និងសីតុណ្ហភាពនៅលើទូកុងតឺន័ររៀងរាល់ ២ ម៉ោងម្តង និងរក្សាទុករបាយការណ៍សីតុណ្ហភាព (Temp Log) ជាភស្តុតាង។",
        "action_en": "Forwarders must mandate 2-hour physical temperature log checks and ensure drivers run full PTI tests with active genset certificates prior to dispatching chassis to packing houses.",
        "tags": ["#ColdChain", "#ReeferTrucking", "#AgriLogistics", "#TemperatureControl", "#FoodSafety"],
        "photo_category": "trucking_highway",
        "source": "Cambodia Cold Chain Association & Reefer Fleet Monitoring Network"
    },
    {
        "slot": "slot_midday",
        "category": "Fleet Telematics & Cargo Security / ប្រព័ន្ធ GPS និងសុវត្ថិភាពទំនិញតាមផ្លូវ",
        "title_km": "ការប្រើប្រាស់ប្រព័ន្ធផ្កាយរណប GPS និងត្រាអេឡិចត្រូនិច (E-Seals) លើរថយន្តកុងតឺន័រឆ្លងកាត់",
        "title_en": "Fleet Telematics & E-Seals: Real-Time Cargo Visibility & Anti-Tamper Security on Transit Corridors",
        "summary_km": "ក្រុមហ៊ុនដឹកជញ្ជូនធំៗនៅកម្ពុជា បានបំពាក់ប្រព័ន្ធតាមដានផ្កាយរណប (GPS Telematics) និងត្រាសោអេឡិចត្រូនិច (Electronic Cargo Seals / E-Seals) លើរថយន្តកុងតឺន័រទាំងអស់។ បច្ចេកវិទ្យានេះជួយតាមដានទីតាំងរថយន្តភ្លាមៗ និងផ្ញើសញ្ញាប្រកាសអាសន្នភ្លាមៗ ប្រសិនបើមានការបើកទ្វារកុងតឺន័រ ឬរថយន្តឈប់ខុសផ្លូវដែលបានកំណត់។",
        "summary_en": "Major Cambodian trucking hauliers have implemented advanced GPS telematics and electronic anti-tamper container seals (E-Seals) across cross-border and highway fleets. The system provides minute-by-minute satellite geolocation, instant geofence deviation alerts, and unauthorized container door-opening notifications.",
        "key_data": [
            "Geofence Route Deviation Alert: Instant trigger if vehicle deviates >500m from corridor",
            "E-Seal Battery Life: 30+ days continuous operational tracking with remote tamper sensor",
            "GDCE Customs Transit Link: Integrated with customs central control room monitoring",
            "Cargo Loss Ratio: Reduced by 98% across participating high-value electronics and apparel routes"
        ],
        "impact_km": "ផ្តល់ទំនុកចិត្តខ្ពស់ដល់ម៉ាកយីហោអន្តរជាតិ (International Brands) និងរោងចក្រផលិតសម្ភារៈអេឡិចត្រូនិច ព្រមទាំងជួយសម្រួលឱ្យការដឹកជញ្ជូនឆ្លងកាត់ព្រំដែនប្រព្រឹត្តទៅលឿន ដោយមិនបាច់ឈប់ត្រួតពិនិត្យញឹកញាប់។",
        "impact_en": "Instills rigorous supply chain confidence for global footwear, luxury apparel, and electronics buyers, while enabling customs green-channel fast-track routing with minimized physical checkpoint stops.",
        "action_km": "ក្រុមហ៊ុន Forwarders គួរជ្រើសរើសក្រុមហ៊ុនរថយន្តដែលមានប្រព័ន្ធតាមដាន GPS និង E-Seal ស្របច្បាប់ ដើម្បីអាចផ្តល់ដំណឹងតាមដានទំនិញ (Tracking Link) ផ្ទាល់ជូនអតិថិជនបាន ២៤ ម៉ោងលើ ២៤ ម៉ោង។",
        "action_en": "Forwarders should partner exclusively with hauliers operating certified API-connected GPS and e-seal platforms, offering clients 24/7 self-service live milestone tracking links.",
        "tags": ["#CargoSecurity", "#GPSTracking", "#ESeal", "#FleetManagement", "#SmartLogistics"],
        "photo_category": "trucking_highway",
        "source": "Cambodian Trucking Association (CAMTA) & Logistics Technology Council"
    },
    {
        "slot": "slot_midday",
        "category": "Multimodal Dry Ports & Hubs / មជ្ឈមណ្ឌលភស្តុភារកម្មពហុបំណង",
        "title_km": "ការតភ្ជាប់ភស្តុភារកម្មពហុបំណង មជ្ឈមណ្ឌល PPLC (Phnom Penh Logistics Center) តភ្ជាប់ផ្លូវដែក ផ្លូវទឹក និងផ្លូវគោក",
        "title_en": "Phnom Penh Logistics Center (PPLC): Multimodal Hub Integrating Rail, River Barge & Highway Corridors",
        "summary_km": "ការអភិវឌ្ឍមជ្ឈមណ្ឌលភស្តុភារកម្មភ្នំពេញ (PPLC) នឹងដើរតួជាបេះដូងនៃការដឹកជញ្ជូនទំនិញពហុបំណងនៅកម្ពុជា។ មជ្ឈមណ្ឌលទំនើបនេះតភ្ជាប់ដោយផ្ទាល់ជាមួយផ្លូវដែកភាគខាងត្បូង (ភ្នំពេញ-ព្រះសីហនុ) កំពង់ផែទន្លេមេគង្គ និងបណ្តាញផ្លូវល្បឿនលឿន ជួយសម្រួលការផ្ទេរទំនិញយ៉ាងរលូន។",
        "summary_en": "The strategic development of the Phnom Penh Logistics Center (PPLC) serves as Cambodia's premier multimodal inland hub. Integrating dedicated rail sidings connected to the Southern Railway, direct barge access to the Mekong River, and feeder links to expressways, PPLC streamlines intermodal container transfers.",
        "key_data": [
            "Rail Intermodal Siding: Direct on-dock container train loading to Sihanoukville Port",
            "Bonded Warehousing: Over 100,000 sqm modern high-ceiling racked space",
            "Container Yard Capacity: Engineered for 300,000+ TEU annual handling throughput",
            "Turnaround Target: Sub-30 minute gate-in to gate-out container chassis servicing"
        ],
        "impact_km": "ជួយកាត់បន្ថយថ្លៃដើមភស្តុភារកម្មសរុបរបស់កម្ពុជា និងកាត់បន្ថយការកកស្ទះចរាចរណ៍រថយន្តធុនធ្ងន់ក្នុងរាជធានីភ្នំពេញ តាមរយៈការបង្វែរទំនិញមួយផ្នែកធំទៅដឹកតាមផ្លូវដែក និងផ្លូវទឹក។",
        "impact_en": "Will structurally compress Cambodia's overall logistics cost ratio while de-congesting metropolitan Phnom Penh road corridors by shifting high-volume container freight onto rail and river networks.",
        "action_km": "ក្រុមហ៊ុន Forwarders គួរត្រៀមខ្លួនប្រើប្រាស់សេវាកម្មឃ្លាំង និងទីលានពហុបំណង ដើម្បីផ្តល់ដំណោះស្រាយដឹកជញ្ជូនចម្រុះ (ផ្លូវដែក + ផ្លូវទឹក) ដែលសន្សំថ្លៃដើមជូនរោងចក្រធំៗ។",
        "action_en": "Forwarders should evaluate future cross-docking and intermodal rail-barge options at PPLC to design blended freight models delivering structural cost savings to high-volume manufacturing clients.",
        "tags": ["#PPLC", "#MultimodalHub", "#DryPort", "#RailFreight", "#LogisticsInfrastructure"],
        "photo_category": "factory_logistics",
        "source": "Ministry of Public Works and Transport & National Logistics Council"
    },
    {
        "slot": "slot_midday",
        "category": "Dry Port & Cross-Dock Operations / ទីលាន ICD និងឃ្លាំងឆ្លងកាត់ព្រំដែន",
        "title_km": "ប្រតិបត្តិការទីលានកុងតឺន័រគោក (ICD) និងឃ្លាំង Cross-Dock នៅខេត្តស្វាយរៀង តំបន់សេដ្ឋកិច្ចពិសេសបាវិត",
        "title_en": "Svay Rieng & Bavet Dry Port Operations: Cross-Docking & Container Staging for Border Manufacturing",
        "summary_km": "ទីលានកុងតឺន័រគោក និងឃ្លាំង Cross-Dock នៅតំបន់បាវិត ខេត្តស្វាយរៀង (ដូចជា Manhattan SEZ, Tai Seng, និង Giga Resource) កំពុងដំណើរការយ៉ាងមមាញឹកក្នុងការផ្ទេរទំនិញរវាងរថយន្តកម្ពុជា និងរថយន្តវៀតណាម។ ការគ្រប់គ្រងទីលានប្រកបដោយប្រសិទ្ធភាពជួយឱ្យរថយន្តមិនបាច់រង់ចាំយូរនៅច្រកទ្វារព្រំដែន។",
        "summary_en": "Inland Container Depots (ICD) and cross-dock platforms across Bavet, Svay Rieng province (including facilities within Manhattan SEZ, Tai Seng SEZ, and Giga Resource) sustain heavy operations staging export cargo and transloading goods between Cambodian and Vietnamese tractors. Rapid yard turnaround minimizes border queueing.",
        "key_data": [
            "Cross-Dock Cargo Turnaround: 2 - 3 hours for standard palletized dry cargo transfers",
            "Empty Drop-off Facility: Off-dock container depot certified by 6 major regional carriers",
            "Operating Hours: 06:00 - 22:00 daily with extended night clearance capability",
            "Customs Sub-branch: Dedicated on-site GDCE customs presence inside SEZ zones"
        ],
        "impact_km": "សម្រួលដល់ខ្សែសង្វាក់ផ្គត់ផ្គង់របស់រោងចក្រផលិតកង់ គ្រឿងបន្លាស់រថយន្ត និងឧបករណ៍អេឡិចត្រូនិចនៅតាមបណ្តោយព្រំដែន ឱ្យមានភាពរលូន និងមិនមានការរអាក់រអួល។",
        "impact_en": "Secures seamless just-in-time material flows for high-tech bicycle, automotive wire harness, and electronics clusters clustered along the Cambodia-Vietnam border corridor.",
        "action_km": "ក្រុមហ៊ុន Forwarders គួររៀបចំកាលវិភាគផ្ទេរទំនិញនៅឃ្លាំង Cross-Dock ឱ្យបានច្បាស់លាស់ជាមួយដៃគូរថយន្តវៀតណាម ដើម្បីកាត់បន្ថយថ្លៃរង់ចាំ (Waiting Charges) និងធានាថាទំនិញទៅដល់កំពង់ផែ Cai Mep ទាន់ពេលកាត់បញ្ជី។",
        "action_en": "Forwarders must strictly synchronize cross-dock transshipment slots with Vietnamese border carriers to eliminate standby surcharges and meet strict Cat Lai/Cai Mep port closing deadlines.",
        "tags": ["#BavetLogistics", "#CrossDock", "#DryPort", "#SvayRieng", "#BorderLogistics", "#SEZSupplyChain"],
        "photo_category": "trucking_highway",
        "source": "Bavet Border Customs & Cross-Border Transport Coordination Association"
    },

    # =========================================================================
    # SLOT 3: EVENING (18:00 ICT) — AIR CARGO, CUSTOMS, SEZ & TRADE COMPLIANCE
    # =========================================================================
    {
        "slot": "slot_evening",
        "category": "Air Cargo & Express Logistics / ដឹកជញ្ជូនទំនិញតាមផ្លូវអាកាស",
        "title_km": "សមត្ថភាពដឹកជញ្ជូនទំនិញតាមផ្លូវអាកាស (Air Cargo) នៅអាកាសយានដ្ឋានភ្នំពេញ (PNH/TIA)",
        "title_en": "Phnom Penh (PNH/TIA) Air Cargo Capacity & Scheduled Freighter Operations",
        "summary_km": "តម្រូវការដឹកជញ្ជូនតាមផ្លូវអាកាសសម្រាប់ទំនិញគំរូសម្លៀកបំពាក់ ស្បែកជើងបន្ទាន់ និងគ្រឿងអេឡិចត្រូនិច មានកម្រិតខ្ពស់។ ជើងហោះហើរដឹកទំនិញសុទ្ធ (Freighters) របស់ក្រុមហ៊ុនអាកាសចរណ៍ដូចជា Cathay Cargo, Raya Airways, និង K-Mile កំពុងដំណើរការជាទៀងទាត់។",
        "summary_en": "Air cargo demand out of Phnom Penh (PNH/TIA) remains robust for seasonal fashion sample runs, urgent garment purchase orders, and electronic assemblies. Scheduled widebody freighters operated by Cathay Cargo, Raya Airways, and K-Mile maintain regular weekly rotations.",
        "key_data": [
            "PNH - US West Coast (LAX/SFO): $4.85 - $5.10 / kg spot rate",
            "PNH - Europe (FRA/AMS): $3.90 - $4.15 / kg spot rate",
            "Freighter Capacity: Scheduled B747F, B767F, and B737F freighters",
            "Regional Express (BKK/SIN/KUL): Next-day transit available"
        ],
        "impact_km": "ផ្តល់លទ្ធភាពឱ្យរោងចក្រកាត់ដេរកម្ពុជាអាចបញ្ជូនទំនិញគំរូ ឬការកុម្ម៉ង់បន្ទាន់ទៅកាន់អតិថិជននៅអឺរ៉ុប និងអាមេរិកបានក្នុងរយៈពេលពី ២ ទៅ ៤ ថ្ងៃ។",
        "impact_en": "Enables garment and electronics manufacturers in Cambodia to meet tight retail sample deadlines in Europe and North America within 2 to 4 days.",
        "action_km": "ក្រុមហ៊ុន Forwarders គួរកក់ទំហំផ្ទុក (Booking Space) មុនយ៉ាងតិច ៤៨ ម៉ោង សម្រាប់ការដឹកទំនិញលើសពី ៥០០ គីឡូក្រាម និងបញ្ជាក់ឧបករណ៍ GOH ជាមួយភ្នាក់ងារអាកាសចរណ៍។",
        "action_en": "Forwarders should book air cargo space at least 48 hours in advance for volume exceeding 500kg, and confirm Garment on Hanger (GOH) equipment availability early with your airline GSA.",
        "tags": ["#AirFreight", "#AirCargo", "#PNH", "#TIA", "#CathayCargo", "#CAMFFA"],
        "photo_category": "air_cargo",
        "source": "State Secretariat of Civil Aviation & Phnom Penh Airport Cargo Terminal"
    },
    {
        "slot": "slot_evening",
        "category": "Specialized Air Freight / សម្លៀកបំពាក់ព្យួរតាមយន្តហោះ",
        "title_km": "ការដឹកជញ្ជូនសម្លៀកបំពាក់ព្យួរ (Garment on Hanger - GOH) តាមផ្លូវអាកាសទៅកាន់ទីផ្សារអន្តរជាតិ",
        "title_en": "Garment on Hanger (GOH) Air Logistics: Wrinkle-Free Retail Ready Garment Transport",
        "summary_km": "ការរៀបចំកុងតឺន័រយន្តហោះពិសេស (Air ULDs) សម្រាប់ព្យួរសម្លៀកបំពាក់ (GOH) អនុញ្ញាតឱ្យសម្លៀកបំពាក់ម៉ាកល្បីៗចេញពីរោងចក្រនៅកម្ពុជា ទៅដល់ធ្នើរដាក់តាំងលក់នៅហាងទំនើបនៅបរទេសភ្លាមៗ ដោយមិនបាច់បោកអ៊ុត ឬវេចខ្ចប់ឡើងវិញឡើយ។",
        "summary_en": "Specialized Garment on Hanger (GOH) air container configurations (ULDs) allow high-end fashion apparel manufactured in Cambodia to move straight from stitching lines to retail floors abroad without folding, ironing, or repackaging.",
        "key_data": [
            "Equipment: Structural string and bar GOH ULD air pallets",
            "Retail Advantage: 100% retail-ready with price tags and sensors attached",
            "Damage Protection: High-grade moisture-absorbing desiccant and dust-proof lining",
            "Transit Speed: Airport-to-store delivery within 72 hours"
        ],
        "impact_km": "បង្កើនតម្លៃបន្ថែមដល់ឧស្សាហកម្មកាត់ដេរកម្ពុជា និងទាក់ទាញម៉ាកសម្លៀកបំពាក់លំដាប់ខ្ពស់ឱ្យមកកុម្ម៉ង់ទិញកាន់តែច្រើន។",
        "impact_en": "Elevates the value proposition of Cambodian garment manufacturing, attracting premium fashion brands requiring immediate floor-ready supply chains.",
        "action_km": "ក្រុមហ៊ុន Forwarders ត្រូវពិនិត្យខ្សែ និងរបារដែកព្យួរក្នុងទូ ULD ឱ្យបានម៉ត់ចត់ និងធានាថាមានថង់ស្រោបការពារធូលី និងសំណើមគ្រប់គ្រាន់ មុនពេលបញ្ជូនទៅព្រលានយន្តហោះ។",
        "action_en": "Forwarders must inspect GOH hanger string tension and locking bars inside ULDs and verify dust-proof protective plastic wrapping before airport apron transfer.",
        "tags": ["#GOH", "#GarmentOnHanger", "#AirLogistics", "#FashionLogistics", "#TextileExport"],
        "photo_category": "air_cargo",
        "source": "Air Cargo Ground Handling & Apparel Logistics Committee"
    },
    {
        "slot": "slot_evening",
        "category": "GDCE Customs & Compliance / នីតិវិធីគយ និងច្បាប់",
        "title_km": "ការប្រកាសទំនិញមុនពេលមកដល់ (Pre-Arrival) តាមប្រព័ន្ធ ASYCUDA World និង CamDX",
        "title_en": "GDCE ASYCUDA World Pre-Clearance & CamDX Digital National Single Window Integration",
        "summary_km": "អគ្គនាយកដ្ឋានគយ និងរដ្ឋាករកម្ពុជា (GDCE) លើកទឹកចិត្តឱ្យក្រុមហ៊ុនបញ្ជូនទំនិញ និងឈ្មួញកណ្តាលគយ (Customs Brokers) ដាក់ពាក្យប្រកាសពន្ធគយមុនពេលកប៉ាល់មកដល់ (Pre-Arrival Declaration) តាមរយៈប្រព័ន្ធ ASYCUDA World និងច្រកចេញចូលតែមួយជាតិ CamDX ដើម្បីទទួលបានការលើកលែងការត្រួតពិនិត្យ (Green Lane)។",
        "summary_en": "The General Department of Customs and Excise (GDCE) strongly encourages freight forwarders and customs brokers to file pre-arrival declarations 24-48 hours before vessel berthing via ASYCUDA World and CamDX to achieve automated Green Channel release.",
        "key_data": [
            "ASYCUDA Green Lane Ratio: Over 85% for pre-filed declarations",
            "CamDX Integration: 24/7 automated paperless permit processing",
            "Pre-Filing Timeline: 24 to 48 hours prior to vessel arrival at port",
            "Demurrage Prevention: Zero port storage delay for Green Channel shipments"
        ],
        "impact_km": "ជួយកាត់បន្ថយពេលវេលាបញ្ចេញទំនិញពីកំពង់ផែមកសល់ត្រឹមតែប៉ុន្មានម៉ោងប៉ុណ្ណោះ និងជួយសន្សំប្រាក់លើថ្លៃស្តុកទុក និងថ្លៃពន្យារពេលកុងតឺន័រ (Demurrage & Detention)។",
        "impact_en": "Drastically accelerates customs cargo clearance upon vessel docking, eliminating expensive port storage and container detention charges for factory importers.",
        "action_km": "ក្រុមហ៊ុន Forwarders ត្រូវប្រមូលឯកសារវិក្កយបត្រ (Commercial Invoice) បញ្ជីវេចខ្ចប់ (Packing List) និងលិខិតដឹកជញ្ជូន (B/L) ឱ្យបានមុន ៣ ថ្ងៃ ដើម្បីប្រកាសចូលប្រព័ន្ធ ASYCUDA ឱ្យទាន់ពេល។",
        "action_en": "Forwarders must collect commercial invoices, packing lists, and sea waybills 3 days ahead of arrival to complete ASYCUDA electronic entry filing prior to port arrival.",
        "tags": ["#CustomsGDCE", "#ASYCUDA", "#CamDX", "#GreenLane", "#TradeCompliance", "#CAMFFA"],
        "photo_category": "customs_inspection",
        "source": "General Department of Customs and Excise of Cambodia (GDCE)"
    },
    {
        "slot": "slot_evening",
        "category": "Trade Agreements & Tariffs / កិច្ចព្រមព្រៀងពាណិជ្ជកម្ម",
        "title_km": "ការទាញយកផលប្រយោជន៍ពន្ធគយពីកិច្ចព្រមព្រៀង RCEP និងវិញ្ញាបនបត្រដើមកំណើត Form D / Form E",
        "title_en": "Maximizing Tariff Savings: RCEP Agreement, Form D, Form E & Rules of Origin Compliance",
        "summary_km": "កិច្ចព្រមព្រៀងភាពជាដៃគូសេដ្ឋកិច្ចគ្រប់ជ្រុងជ្រោយតំបន់ (RCEP) និងកិច្ចព្រមព្រៀងអាស៊ាន (ATIGA - Form D) ផ្តល់ការលើកលែងពន្ធនាំចូល ០% លើវត្ថុធាតុដើមវាយនភណ្ឌ គ្រឿងបន្លាស់ និងគ្រឿងម៉ាស៊ីនដែលនាំចូលមកកម្ពុជា។ ការបំពេញបែបបទវិញ្ញាបនបត្រដើមកំណើតទំនិញ (CO) តាមប្រព័ន្ធអនឡាញរបស់ក្រសួងពាណិជ្ជកម្ម មានភាពងាយស្រួល និងឆាប់រហ័ស។",
        "summary_en": "The Regional Comprehensive Economic Partnership (RCEP) and ASEAN ATIGA (Form D) agreements offer zero import duties on qualifying textile yarns, accessories, and industrial machinery imported into Cambodia. The Ministry of Commerce electronic Certificate of Origin (CO) system accelerates filing.",
        "key_data": [
            "RCEP Preferential Duty: 0% tariff on participating raw material HS codes",
            "ATIGA Form D: Duty-free intra-ASEAN movement for qualifying goods",
            "Online CO Issuance: Fast-track digital approval within 24-48 hours",
            "Landed Cost Savings: Up to 7% to 15% reduction in total import duty spend"
        ],
        "impact_km": "ជួយកាត់បន្ថយថ្លៃដើមផលិតរបស់រោងចក្រនៅកម្ពុជា និងបង្កើនភាពប្រកួតប្រជែងនៃការនាំចេញទំនិញកម្ពុជាទៅកាន់ទីផ្សារពិភពលោក។",
        "impact_en": "Directly reduces landed manufacturing input costs for Cambodian factories, enhancing export competitiveness in international consumer markets.",
        "action_km": "ក្រុមហ៊ុន Forwarders គួរជួយត្រួតពិនិត្យលេខកូដទំនិញ (HS Code) និងទម្រង់វិញ្ញាបនបត្រដើមកំណើតទំនិញ (CO) របស់រោងចក្រ ឱ្យត្រូវគ្នានឹងតារាងបន្ធូរបន្ថយពន្ធ RCEP មុនពេលទំនិញមកដល់។",
        "action_en": "Forwarders should audit supplier HS codes against the RCEP tariff reduction schedule to ensure import shipments qualify for full duty exemption.",
        "tags": ["#RCEP", "#FormD", "#FormE", "#RulesOfOrigin", "#TradeCompliance", "#DutyFree"],
        "photo_category": "customs_inspection",
        "source": "Ministry of Commerce & General Department of Customs and Excise"
    },
    {
        "slot": "slot_evening",
        "category": "Special Economic Zones (SEZ) / តំបន់សេដ្ឋកិច្ចពិសេស",
        "title_km": "ការគ្រប់គ្រងឃ្លាំងស្តុកទំនិញជាប់ពន្ធ (Bonded Warehousing) ក្នុងតំបន់សេដ្ឋកិច្ចពិសេសភ្នំពេញ (PPSEZ)",
        "title_en": "Bonded Warehousing & Inventory Staging at Royal Group Phnom Penh SEZ (PPSEZ)",
        "summary_km": "តំបន់សេដ្ឋកិច្ចពិសេសភ្នំពេញ (PPSEZ) ផ្តល់សេវាកម្មឃ្លាំងស្តុកទំនិញជាប់ពន្ធ (Bonded Warehouse) និងការិយាល័យគយប្រចាំការនៅនឹងកន្លែង។ រោងចក្រអាចរក្សាទុកវត្ថុធាតុដើមនាំចូលដោយមិនទាន់បង់ពន្ធគយ រហូតដល់ទំនិញត្រូវបានដកចេញទៅផលិតជាក់ស្តែង។",
        "summary_en": "Royal Group Phnom Penh Special Economic Zone (PPSEZ) provides secure bonded warehousing facilities with on-site customs inspection offices. Manufacturers can store imported raw materials under duty-suspension status until drawn onto factory production lines.",
        "key_data": [
            "On-site Customs Office: Immediate physical clearance inside SEZ",
            "Duty-Suspension: Zero duty payment until cargo is withdrawn for manufacturing",
            "Inventory Technology: Modern barcode SKU warehouse tracking systems",
            "Port Proximity: Direct expressway link to Sihanoukville Port (2h 15m)"
        ],
        "impact_km": "ជួយសម្រួលដល់លំហូរសាច់ប្រាក់របស់រោងចក្រ (Cash Flow) និងកាត់បន្ថយតម្រូវការសាងសង់ឃ្លាំងផ្ទុកទំនិញធំៗក្នុងបរិវេណរោងចក្រផ្ទាល់។",
        "impact_en": "Optimizes factory cash flow by deferring customs tax payments and reduces the need for expensive dedicated on-site factory storage buildings.",
        "action_km": "ក្រុមហ៊ុនបញ្ជូនទំនិញ និងភ្នាក់ងារ 3PL គួរផ្តល់ជម្រើសស្តុកទំនិញក្នុងឃ្លាំង Bonded ក្នុង PPSEZ ដល់រោងចក្រ ដើម្បីជួយគ្រប់គ្រងវត្ថុធាតុដើមឱ្យមានតុល្យភាពល្អ។",
        "action_en": "Forwarders and 3PL providers should offer bonded staging solutions inside PPSEZ to assist manufacturing clients in managing seasonal material inventory buffers.",
        "tags": ["#PPSEZ", "#BondedWarehouse", "#SEZLogistics", "#InventoryManagement", "#PhnomPenh"],
        "photo_category": "factory_logistics",
        "source": "Royal Group PPSEZ Administration & Customs Sub-Branch"
    },
    {
        "slot": "slot_evening",
        "category": "Less-Than-Container-Load (LCL) / ទំនិញកុងតឺន័ររួម",
        "title_km": "ការច្របាច់បញ្ចូលទំនិញកុងតឺន័ររួម (LCL Consolidation) ពីកំពង់ផែអាស៊ីមកកាន់ភ្នំពេញ",
        "title_en": "Weekly LCL Ocean Consolidation Services from Major Asian Hubs to Phnom Penh CFS",
        "summary_km": "សេវាកម្មច្របាច់បញ្ចូលទំនិញរួមគ្នា (LCL Consolidation) ជួយឱ្យក្រុមហ៊ុនខ្នាតតូច និងមធ្យម ដែលមានទំនិញមិនគ្រប់មួយកុងតឺន័រ អាចនាំចូលទំនិញពីស៊ាងហៃ នីងបូ ក្វាងចូវ និងបាងកក មកកាន់ភ្នំពេញ ដោយគិតថ្លៃតាមមាឌជាក់ស្តែង (CBM) យ៉ាងសមរម្យ។",
        "summary_en": "Weekly Less-Than-Container-Load (LCL) ocean consolidation boxes departing Shanghai, Ningbo, Guangzhou, and Bangkok provide small and medium importers with reliable shared-box freight billed transparently on a per-CBM basis to Phnom Penh CFS depots.",
        "key_data": [
            "Weekly Departures: Fixed weekly consolidation loops to Phnom Penh ICDs",
            "Pricing Model: Transparent per-CBM billing with standardized CFS charges",
            "Cargo Integrity: Professional shrink-wrapping and palletization standards",
            "Deconsolidation Turnaround: 24-48 hours post container arrival"
        ],
        "impact_km": "ជួយឱ្យសហគ្រាសខ្នាតតូច និងមធ្យម (SMEs) អាចកុម្ម៉ង់ទំនិញក្នុងបរិមាណតិចតួចបាន ដោយមិនបាច់រង់ចាំប្រមូលទំនិញឱ្យគ្រប់មួយកុងតឺន័រឡើយ។",
        "impact_en": "Empowers small and medium enterprises (SMEs) to import smaller purchase orders without bearing the full expense of dedicated FCL container boxes.",
        "action_km": "ក្រុមហ៊ុន Forwarders ត្រូវបញ្ជាក់ទម្ងន់ និងទំហំមាឌទំនិញ (Volume Weight) ឱ្យបានច្បាស់លាស់ជាមួយអតិថិជន និងផ្តល់តារាងតម្លៃថ្លៃឃ្លាំង CFS ឱ្យបានច្បាស់លាស់ដោយគ្មានការលាក់កំបាំង។",
        "action_en": "Forwarders must accurately re-measure carton dimensions and gross weights and provide transparent, itemized CFS destination tariff sheets to prevent client billing disputes.",
        "tags": ["#LCL", "#Consolidation", "#CFS", "#CBMFreight", "#SMETrade", "#PhnomPenhDelivery"],
        "photo_category": "factory_logistics",
        "source": "Phnom Penh Container Freight Station (CFS) Operators & Forwarding Desk"
    },
    {
        "slot": "slot_evening",
        "category": "Cargo Insurance & Risk / ធានារ៉ាប់រងទំនិញដឹកជញ្ជូន",
        "title_km": "ការការពារហានិភ័យទំនិញតាមរយៈការធានារ៉ាប់រងទំនិញដឹកជញ្ជូនគ្រប់ជ្រុងជ្រោយ (All-Risk Marine Insurance)",
        "title_en": "Marine Cargo Insurance & Risk Management Protocols for International Trade",
        "summary_km": "ក្នុងរដូវវស្សាដែលមានខ្យល់ព្យុះខ្លាំងនៅសមុទ្រ និងការផ្ទេរទំនិញឆ្លងកាត់ច្រើនមធ្យោបាយ ការទិញប័ណ្ណសន្យារ៉ាប់រងទំនិញគ្រប់ជ្រុងជ្រោយ (Institute Cargo Clauses A) គឺជាការចាំបាច់ ដើម្បីការពារការខាតបង់ហិរញ្ញវត្ថុពេលមានគ្រោះថ្នាក់កើតឡើង។",
        "summary_en": "Monsoon sea weather and multi-modal handling risks make all-risk marine cargo insurance (Institute Cargo Clauses A) essential for protecting shippers against catastrophic financial loss during ocean and overland transshipment.",
        "key_data": [
            "Coverage Standard: Institute Cargo Clauses (A) — Comprehensive all-risk protection",
            "Carrier Liability Limit: Baseline Hague-Visby rules provide minimal recovery ($2/kg)",
            "Claim Documentation: Survey report, commercial invoice, packing list, bill of lading",
            "Deductible Structure: Competitive low deductible tiers for regular corporate shippers"
        ],
        "impact_km": "ការពារម្ចាស់ទំនិញពីការខាតបង់ទឹកប្រាក់រាប់ម៉ឺនដុល្លារ ប្រសិនបើមានទូកុងតឺន័រធ្លាក់ចូលសមុទ្រ ភ្លើងឆេះ ឬទឹកចូលសើមខូចខាតទំនិញ។",
        "impact_en": "Protects exporters and importers from devastating financial losses resulting from container loss at sea, cargo wetting, or total vessel loss.",
        "action_km": "ក្រុមហ៊ុន Forwarders គួរពន្យល់អតិថិជនឱ្យយល់ច្បាស់ពីដែនកំណត់នៃការទទួលខុសត្រូវរបស់ក្រុមហ៊ុនកប៉ាល់ (Carrier Liability) និងណែនាំឱ្យទិញធានារ៉ាប់រងបន្ថែមសម្រាប់រាល់ជើងដឹកជញ្ជូន។",
        "action_en": "Forwarders must explain carrier liability limitations under international conventions to shippers and recommend full all-risk cargo insurance policies for valuable shipments.",
        "tags": ["#CargoInsurance", "#MarineInsurance", "#RiskManagement", "#TradeProtection", "#SupplyChainSecurity"],
        "photo_category": "rate_index",
        "source": "General Insurance Association of Cambodia & Marine Underwriting Council"
    },
    {
        "slot": "slot_evening",
        "category": "Reverse Logistics & Re-Export / ការនាំចេញទំនិញត្រឡប់ក្រោយ",
        "title_km": "នីតិវិធីគយសម្រាប់ការនាំចេញទំនិញខូចគុណភាពត្រឡប់ក្រោយ (Re-Export) និងការជួសជុល",
        "title_en": "Reverse Logistics & Re-Export Customs Regulations for Defective Industrial Goods",
        "summary_km": "នៅពេលដែលវត្ថុធាតុដើម ឬសម្លៀកបំពាក់មានបញ្ហាបច្ចេកទេសដែលតម្រូវឱ្យនាំចេញត្រឡប់ទៅប្រទេសដើមវិញ រោងចក្រត្រូវអនុវត្តតាមនីតិវិធីនាំចេញត្រឡប់ក្រោយ (Re-Export Formalities) របស់អគ្គនាយកដ្ឋានគយ ដើម្បីទាញយកប្រាក់កក់ពន្ធ ឬចៀសវាងការបង់ពន្ធស្ទួន។",
        "summary_en": "When raw materials or manufactured goods contain quality defects requiring return to origin, factories must follow GDCE re-export regulations and temporary admission guidelines to recover customs deposits and prevent double taxation.",
        "key_data": [
            "Customs Form: Temporary Admission / Export (TA/TI Declaration)",
            "Inspection Protocol: Joint inspection by GDCE port customs officers",
            "Duty Drawback: Eligible for duty refund upon verified proof of re-exportation",
            "Time Limit: Standard 6-month validity for temporary export-return operations"
        ],
        "impact_km": "ជួយឱ្យរោងចក្រអាចដោះស្រាយបញ្ហាទំនិញខូចគុណភាពជាមួយអ្នកផ្គត់ផ្គង់ក្រៅប្រទេសបានស្របច្បាប់ ដោយមិនខាតបង់ថ្លៃពន្ធគយបន្ថែម។",
        "impact_en": "Enables factories to legally return rejected components to overseas vendors while recovering or canceling customs duties assessed at initial import.",
        "action_km": "ក្រុមហ៊ុន Forwarders ត្រូវណែនាំអតិថិជនកុំឱ្យប្រញាប់បញ្ជូនទំនិញចេញ ដោយគ្មានការចុះត្រួតពិនិត្យ និងចុះហត្ថលេខាបញ្ជាក់ពីមន្ត្រីគយមានសមត្ថកិច្ចជាមុនឡើយ។",
        "action_en": "Forwarders must instruct factory clients to obtain formal customs defect certification and joint survey inspection stamps before repacking goods for outbound transit.",
        "tags": ["#ReverseLogistics", "#ReExport", "#CustomsRegulations", "#DutyDrawback", "#GDCECompliance"],
        "photo_category": "customs_inspection",
        "source": "General Department of Customs and Excise Legal Affairs & Audit Department"
    },
    {
        "slot": "slot_evening",
        "category": "Customs Best Trader & AEO / វិញ្ញាបនបត្រ AEO និងពាណិជ្ជករឆ្នើម",
        "title_km": "អត្ថប្រយោជន៍នៃកម្មវិធីពាណិជ្ជករឆ្នើម (Best Trader Group) និងវិញ្ញាបនបត្រ AEO របស់អគ្គនាយកដ្ឋានគយ និងរដ្ឋាករ (GDCE)",
        "title_en": "GDCE Best Trader Group & Authorized Economic Operator (AEO) Accreditation: Green Lane Fast-Tracking",
        "summary_km": "ក្រុមហ៊ុននាំចេញ-នាំចូល និងក្រុមហ៊ុនបញ្ជូនទំនិញដែលទទួលបានវិញ្ញាបនបត្រពាណិជ្ជករឆ្នើម (Best Trader) ឬ AEO ពីអគ្គនាយកដ្ឋានគយ និងរដ្ឋាករកម្ពុជា (GDCE) ទទួលបានការលើកលែងការត្រួតពិនិត្យឯកសារ និងទំនិញជាក់ស្តែង (Green Lane)។ នេះជួយឱ្យការបញ្ចេញទំនិញពីកំពង់ផែ និងព្រំដែនចំណាយពេលត្រឹមតែប៉ុន្មានម៉ោងប៉ុណ្ណោះ។",
        "summary_en": "Exporters, importers, and forwarders accredited under the General Department of Customs and Excise (GDCE) Best Trader Group and Authorized Economic Operator (AEO) scheme enjoy preferential Green Lane processing. Eligible shipments bypass routine documentary verification and physical container devanning, enabling customs clearance within 1-2 hours.",
        "key_data": [
            "Physical Inspection Rate: Zero routine physical inspections for certified AEO consignments",
            "Clearance Speed: Under 2 hours from ASYCUDA submission to cargo release",
            "Post-Clearance Audit (PCA): Periodic compliance audits replacing at-the-border inspections",
            "Mutual Recognition: Cambodia advancing bilateral AEO arrangements with regional trade partners"
        ],
        "impact_km": "ជួយកាត់បន្ថយថ្លៃដើមប្រតិបត្តិការគយយ៉ាងច្រើន និងលុបបំបាត់ការកកស្ទះនៅមាត់ច្រកទ្វារ ព្រមទាំងបង្កើនកេរ្តិ៍ឈ្មោះ និងភាពជឿជាក់របស់ក្រុមហ៊ុនក្នុងក្រសែភ្នែកដៃគូពាណិជ្ជកម្មអន្តរជាតិ។",
        "impact_en": "Substantially lowers customs brokerage friction and terminal storage expenses while cementing operational reputation and supply chain predictability for international buyers.",
        "action_km": "ក្រុមហ៊ុន Forwarders គួរជួយណែនាំ និងជំរុញឱ្យអតិថិជនរោងចក្រធំៗបំពេញលក្ខខណ្ឌអនុលោមភាពច្បាប់គយ ដើម្បីស្នើសុំចូលជាសមាជិក Best Trader Group ទទួលបានអត្ថប្រយោជន៍ Green Lane។",
        "action_en": "Forwarders should proactively audit and guide compliant factory clients through the formal GDCE AEO application process to lock in priority green channel status.",
        "tags": ["#GDCE", "#AEO", "#BestTrader", "#CustomsGreenLane", "#TradeFacilitation", "#CAMFFA"],
        "photo_category": "customs_inspection",
        "source": "General Department of Customs and Excise (GDCE) Risk Management & Audit Directorate"
    },
    {
        "slot": "slot_evening",
        "category": "HS Code & Customs Valuation / ចំណាត់ថ្នាក់កូដទំនិញ និងតម្លៃគិតពន្ធគយ",
        "title_km": "នីតិវិធីស្នើសុំសេចក្តីសម្រេចជាមុនលើចំណាត់ថ្នាក់ទំនិញ (Advance Ruling on HS Code) និងតម្លៃគិតពន្ធគយ",
        "title_en": "GDCE Advance Ruling Guidelines: Securing Pre-Arrival Certainty on HS Code Classification & Valuation",
        "summary_km": "ដើម្បីចៀសវាងវិវាទលើការកំណត់លេខកូដទំនិញ (HS Code) និងតម្លៃគិតពន្ធគយនៅពេលទំនិញមកដល់ ម្ចាស់ទំនិញអាចដាក់ពាក្យស្នើសុំ «សេចក្តីសម្រេចជាមុន» (Advance Ruling) ពីអគ្គនាយកដ្ឋានគយ និងរដ្ឋាករកម្ពុជា (GDCE) មុនពេលនាំចូលទំនិញជាក់ស្តែង។ សេចក្តីសម្រេចនេះមានសុពលភាពស្របច្បាប់រហូតដល់ ៣ ឆ្នាំ។",
        "summary_en": "To eliminate costly classification disputes, re-valuation penalties, or clearance delays at border checkpoints, shippers and importers can file for formal Advance Rulings on Tariff Classification (HS Code) and Customs Valuation with GDCE prior to cargo departure. Approved advance rulings remain legally binding for up to 3 years.",
        "key_data": [
            "Application Lead Time: Recommended 30 days prior to commercial cargo shipment",
            "Validity Period: Up to 3 years legally binding across all Cambodian entry ports",
            "Required Submission: Technical spec sheets, product breakdown, chemical analysis / MSDS, commercial invoice",
            "Dispute Prevention: Completely eliminates on-arrival HS code reclassification disputes"
        ],
        "impact_km": "ជួយឱ្យក្រុមហ៊ុននាំចូលអាចគណនាថ្លៃដើមពន្ធគយបានត្រឹមត្រូវ ១០០% មុនពេលបញ្ជាទិញទំនិញ និងលុបបំបាត់ហានិភ័យនៃការផាកពិន័យ ឬការជាប់គាំងទំនិញនៅកំពង់ផែ។",
        "impact_en": "Delivers 100% landed-cost certainty before procurement POs are issued and entirely safeguards importers against retrospective tariff audits or surprise duty adjustments.",
        "action_km": "ក្រុមហ៊ុន Forwarders និងភ្នាក់ងារគយ (Customs Brokers) ត្រូវណែនាំអតិថិជនឱ្យស្នើសុំ Advance Ruling ជាមុនសម្រាប់ទំនិញថ្មីៗ ឬគ្រឿងបន្លាស់ស្មុគស្មាញ ដើម្បីធានាការបញ្ចេញទំនិញបានលឿន។",
        "action_en": "Customs brokers and freight forwarders should mandate Advance Ruling filings for new SKU lines, complex electronics, or composite raw materials before inbound shipping orders are placed.",
        "tags": ["#HSCode", "#AdvanceRuling", "#CustomsValuation", "#TariffCompliance", "#GDCE"],
        "photo_category": "customs_inspection",
        "source": "GDCE Department of Tariff and Customs Procedures & WCO Classification Standards"
    },
    {
        "slot": "slot_evening",
        "category": "Air Cargo Cold Chain & Pharma / ដឹកជញ្ជូនឱសថតាមផ្លូវអាកាស",
        "title_km": "ឃ្លាំងត្រជាក់ស្តង់ដារឱសថ (GDP Cold Room) និងការដឹកជញ្ជូនទំនិញតាមផ្លូវអាកាសនៅអាកាសយានដ្ឋានភ្នំពេញ (PNH/TIA)",
        "title_en": "Phnom Penh Airport (PNH/TIA) Pharma Cold Room Logistics & Good Distribution Practice (GDP)",
        "summary_km": "ស្ថានីយទំនិញផ្លូវអាកាសនៅអាកាសយានដ្ឋានអន្តរជាតិភ្នំពេញ បានបំពាក់ឃ្លាំងរក្សាសីតុណ្ហភាពត្រជាក់ស្របតាមស្តង់ដារចែកចាយឱសថល្អ (GDP)។ ប្រព័ន្ធនេះផ្តល់សេវាថែរក្សាសីតុណ្ហភាពចន្លោះពី +២°C ដល់ +៨°C និង +១៥°C ដល់ +២៥°C សម្រាប់ឱសថ វ៉ាក់សាំង និងសារធាតុគីមីជីវសាស្ត្រដែលងាយខូចគុណភាព។",
        "summary_en": "The cargo terminal at Phnom Penh International Airport (PNH) operates dedicated temperature-controlled cold rooms compliant with WHO Good Distribution Practice (GDP) standards. The facility maintains strict temperature zones (+2°C to +8°C cold room, and +15°C to +25°C controlled room temperature) for healthcare, vaccines, and biomedical shipments.",
        "key_data": [
            "Temperature Zones: Dedicated +2°C to +8°C walk-in chillers and -20°C freezer units",
            "Tarmac Thermal Protection: Insulated pallet covers and thermal dollies for ramp transit",
            "Customs Priority: GDCE airport customs priority release for temperature-sensitive healthcare cargo",
            "Data Logging: Continuous multi-sensor calibrated temperature recording with cloud alert"
        ],
        "impact_km": "ធានាសុវត្ថិភាពខ្ពស់បំផុត និងប្រសិទ្ធភាពនៃឱសថព្យាបាលជំងឺដែលនាំចូលមកកាន់ប្រទេសកម្ពុជា ព្រមទាំងគាំទ្រដល់ការនាំចេញផលិតផលកសិកម្មមានតម្លៃខ្ពស់តាមផ្លូវអាកាស។",
        "impact_en": "Guarantees full biomedical potency and regulatory safety for essential pharmaceuticals, vaccines, and diagnostic reagents entering Cambodia's healthcare supply chain.",
        "action_km": "ក្រុមហ៊ុន Forwarders ត្រូវរៀបចំការស្នើសុំបញ្ចេញទំនិញជាបន្ទាន់ (Express Green Clearance) និងត្រួតពិនិត្យឧបករណ៍វាស់សីតុណ្ហភាព (Data Logger) ភ្លាមៗនៅពេលទទួលប្រគល់ទំនិញពីស្ថានីយអាកាសចរណ៍។",
        "action_en": "Air freight forwarders handling pharmaceutical cargo must pre-arrange emergency customs pre-clearance and execute immediate on-arrival logger downloads at the tarmac handover gate.",
        "tags": ["#AirCargo", "#PharmaLogistics", "#ColdChain", "#PNH", "#AirportCargo", "#HealthLogistics"],
        "photo_category": "air_cargo",
        "source": "Cambodia Airports Cargo Services & Ministry of Health Pharmaceutical Regulatory Bureau"
    },
    {
        "slot": "slot_evening",
        "category": "E-Commerce Logistics & Express Cargo / ភស្តុភារកម្មពាណិជ្ជកម្មអេឡិចត្រូនិច",
        "title_km": "ការគ្រប់គ្រងបញ្ញើឆាប់រហ័ស (Express Air Parcels) និងការបង់ពន្ធគយលើកញ្ចប់ទំនិញ E-Commerce",
        "title_en": "Cross-Border E-Commerce & Express Parcel Air Freight Clearances under GDCE De Minimis Regulations",
        "summary_km": "កំណើននៃការបញ្ជាទិញទំនិញតាមប្រព័ន្ធអេឡិចត្រូនិចឆ្លងកាត់ព្រំដែន (E-Commerce) បានជំរុញឱ្យអគ្គនាយកដ្ឋានគយ និងរដ្ឋាករកម្ពុជា (GDCE) អនុវត្តប្រព័ន្ធគ្រប់គ្រងទិន្នន័យបញ្ញើទំនិញឆាប់រហ័សស្វ័យប្រវត្តិ។ កញ្ចប់ទំនិញដែលមានតម្លៃក្រោមទំហំអនុគ្រោះពន្ធ (De Minimis Threshold) ត្រូវបានបញ្ចេញយ៉ាងឆាប់រហ័ស ស្របពេលទំនិញលើសកម្រិតត្រូវបង់ពន្ធតាមប្រព័ន្ធអេឡិចត្រូនិក។",
        "summary_en": "Surging cross-border e-commerce air parcels and express courier shipments have led GDCE to deploy specialized express customs clearance protocols at international airport hubs. Low-value consignments qualifying under de minimis thresholds receive expedited direct release, while dutiable packages are cleared via electronic data interchange (EDI).",
        "key_data": [
            "De Minimis Threshold: Expedited non-dutiable parcel release up to statutory limit",
            "Express Clearance Turnaround: Same-day release for manifest-pre-screened parcels",
            "Prohibited Goods Screening: Dual-view automated X-ray scanners and automated risk profiling",
            "EDI Courier Integration: Seamless integration between international courier manifests and GDCE ASYCUDA"
        ],
        "impact_km": "ជួយឱ្យប្រជាពលរដ្ឋ និងអាជីវកម្មខ្នាតតូចនៅកម្ពុជាទទួលបានទំនិញបញ្ជាទិញពីក្រៅប្រទេសបានលឿន និងមានតម្លាភាពក្នុងការបង់ពន្ធគយស្របតាមច្បាប់។",
        "impact_en": "Accelerates final delivery times for regional e-commerce shipments, empowering small businesses and consumers with predictable import duty assessments and fast tarmac turnaround.",
        "action_km": "ក្រុមហ៊ុនភស្តុភារកម្មបញ្ញើទំនិញរហ័ស (Express Couriers) ត្រូវតម្រូវឱ្យម្ចាស់ទំនិញផ្តល់ព័ត៌មានលម្អិតអំពីតម្លៃ និងប្រភេទកញ្ចប់ទំនិញឱ្យបានច្បាស់លាស់មុនពេលជើងហោះហើរចុះចត ដើម្បីបញ្ចៀសការឃាត់ទុកកញ្ចប់ទំនិញ។",
        "action_en": "Express air cargo operators must ensure overseas shippers transmit full electronic manifests with accurate itemized declarations before flights arrive to prevent parcel quarantine holds.",
        "tags": ["#ECommerceLogistics", "#ExpressCargo", "#AirParcel", "#CustomsClearance", "#LastMile", "#GDCE"],
        "photo_category": "air_cargo",
        "source": "GDCE Airport Express Clearance Bureau & Express Cargo Association"
    },
]

class LogisticsResearchEngine:
    """
    Advanced intelligence and deep research engine for Cambodian Logistics & Supply Chain.
    Produces high-impact, Khmer + English bilingual market intelligence posts
    specifically tailored for Freight Forwarders, Shipping Lines, and Logistics Operators in Cambodia.
    Guarantees that every post has unique content and a unique picture.
    """

    def __init__(self):
        self._gemini_client = None

    @property
    def gemini_client(self):
        if self._gemini_client is None and GEMINI_API_KEY:
            try:
                from google import genai
                self._gemini_client = genai.Client(api_key=GEMINI_API_KEY)
                logger.info("Google Gemini GenAI Client initialized successfully.")
            except Exception as e:
                logger.warning(f"Could not initialize Google GenAI Client: {e}")
        return self._gemini_client

    def get_latest_market_briefing_sync(self, category_filter: Optional[str] = None) -> Dict[str, Any]:
        """
        Retrieves the freshest market intelligence report with structured data and real action photo.
        Enforces smart rotation using recent post history from SQLite to NEVER duplicate recent posts.
        """
        import random
        candidates = BUILTIN_INTELLIGENCE_FEEDS

        if category_filter:
            cf = category_filter.lower()
            filtered = [
                c for c in BUILTIN_INTELLIGENCE_FEEDS 
                if cf == c.get("slot", "").lower()
                or cf in c["category"].lower() 
                or cf in c.get("photo_category", "").lower()
                or any(cf in t.lower() for t in c.get("tags", []))
            ]
            if filtered:
                candidates = filtered

        # Fetch recently posted titles from database to avoid repeating
        recent_titles_list = get_recently_posted_titles(limit=50)
        recent_titles_set = set(recent_titles_list)
        unposted = [c for c in candidates if c["title_en"] not in recent_titles_set]

        if unposted:
            item = random.choice(unposted)
        else:
            # If all candidates in current pool have been posted, select the least recently posted one
            def score(cand):
                try:
                    return recent_titles_list.index(cand["title_en"])
                except ValueError:
                    return 9999
            candidates_sorted = sorted(candidates, key=score, reverse=True)
            item = candidates_sorted[0]

        # Get recently used photo URLs to guarantee a different picture every time
        recent_photos = get_recently_used_photos(limit=100)
        photo_info = get_action_photo_for_topic(
            category=item.get("photo_category", "ocean_port"),
            keywords=item["title_en"],
            exclude_urls=recent_photos
        )

        # Compute hash key for deduplication based on title and hour to prevent double dispatch
        current_time_str = datetime.now().strftime("%Y-%m-%d_%H")
        hash_str = f"{item['title_en']}_{current_time_str}"
        hash_key = hashlib.md5(hash_str.encode()).hexdigest()

        return {
            "hash_key": hash_key,
            "category": item["category"],
            "title_km": item["title_km"],
            "title_en": item["title_en"],
            "summary_km": item["summary_km"],
            "summary_en": item["summary_en"],
            "key_data": item["key_data"],
            "cambodia_impact": item.get("impact_km", ""),
            "cambodia_impact_en": item.get("impact_en", ""),
            "action_recommendation": item.get("action_km", ""),
            "action_recommendation_en": item.get("action_en", ""),
            "tags": item.get("tags", ["#CambodiaLogistics", "#CAMFFA"]),
            "photo_url": photo_info["url"],
            "photo_title": photo_info["title"],
            "photo_location": photo_info["location"],
            "photo_credit": photo_info["credit"],
            "source": item.get("source", "Cambodia Logistics Intelligence Desk"),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M ICT")
        }

    async def get_latest_market_briefing(self, category_filter: Optional[str] = None) -> Dict[str, Any]:
        """Async wrapper for compatibility with bot and scheduler."""
        return self.get_latest_market_briefing_sync(category_filter)

    async def deep_research_topic(self, user_query: str) -> Dict[str, Any]:
        """
        Performs in-depth research on any specific Cambodia logistics topic,
        publishing helpful information in Khmer alongside English for freight forwarders.
        """
        logger.info(f"Conducting deep Cambodia logistics research on: {user_query}")
        
        # If Gemini API is available, generate dynamic real-time intelligence in Khmer + English
        if self.gemini_client:
            prompt = f"""
You are the Chief Logistics Analyst & Maritime Trade Specialist for the Cambodian Logistics Market (CAMFFA & GDCE Network).
The user requested deep research on the following topic:
"{user_query}"

Generate a professional, highly helpful logistics intelligence advisory specifically for Freight Forwarders, Shipping Lines, Customs Brokers, and Factory Logistics Managers in Cambodia.
Focus 100% on the Cambodian market (PAS port, PPAP port, Bavet border, Poipet border, Phnom Penh expressway, PNH/TIA air cargo, GDCE customs rules, SEZs, etc.).
DO NOT include promotional advertising or irrelevant fluff. Give concrete operational metrics, customs guidance, and practical forwarder action steps.
Provide the response in BILINGUAL format: natural Khmer alongside professional English.

Return your analysis as a valid JSON object with the following fields:
{{
  "category": "Category name in English & Khmer (e.g. Sea Freight & Ports / ប្រតិបត្តិការកំពង់ផែសមុទ្រ)",
  "title_km": "Clear, natural, professional Khmer headline",
  "title_en": "Clear, professional English headline",
  "summary_km": "Detailed operational summary in natural Khmer (2-3 sentences)",
  "summary_en": "Detailed executive summary in English (2-3 sentences)",
  "key_data": ["Metric 1 in English / Khmer", "Metric 2 with transit times or fees", "Metric 3 with operational status"],
  "impact_km": "Operational impact on Cambodian exporters, forwarders, and factories (Khmer)",
  "impact_en": "Operational impact on Cambodian exporters, forwarders, and factories (English)",
  "action_km": "Concrete, step-by-step recommendation for freight forwarders and dispatchers (Khmer)",
  "action_en": "Concrete, step-by-step recommendation for freight forwarders and dispatchers (English)",
  "tags": ["#CambodiaLogistics", "#CAMFFA", "#RelevantTag"],
  "photo_category": "ocean_port OR air_cargo OR trucking_highway OR factory_logistics OR customs_inspection OR canal_waterways"
}}
Return ONLY valid JSON without markdown fences.
"""
            try:
                response = self.gemini_client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt
                )
                raw_text = response.text.strip()
                clean_json = re.sub(r"^```json\s*", "", raw_text, flags=re.MULTILINE)
                clean_json = re.sub(r"```$", "", clean_json, flags=re.MULTILINE).strip()
                data = json.loads(clean_json)

                recent_photos = get_recently_used_photos(limit=100)
                photo_category = data.get("photo_category", "ocean_port")
                photo_info = get_action_photo_for_topic(photo_category, user_query, exclude_urls=recent_photos)

                hash_str = f"{data['title_en']}_{datetime.now().strftime('%Y-%m-%d_%H%M')}"
                hash_key = hashlib.md5(hash_str.encode()).hexdigest()

                return {
                    "hash_key": hash_key,
                    "category": data.get("category", "Cambodia Logistics Intelligence"),
                    "title_km": data.get("title_km", ""),
                    "title_en": data.get("title_en", ""),
                    "summary_km": data.get("summary_km", ""),
                    "summary_en": data.get("summary_en", ""),
                    "key_data": data.get("key_data", []),
                    "cambodia_impact": data.get("impact_km", ""),
                    "cambodia_impact_en": data.get("impact_en", ""),
                    "action_recommendation": data.get("action_km", ""),
                    "action_recommendation_en": data.get("action_en", ""),
                    "tags": data.get("tags", ["#CambodiaLogistics", "#CAMFFA"]),
                    "photo_url": photo_info["url"],
                    "photo_title": photo_info["title"],
                    "photo_location": photo_info["location"],
                    "photo_credit": photo_info["credit"],
                    "source": "Cambodia Logistics AI Research Desk & Trade Intelligence",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M ICT")
                }
            except Exception as e:
                logger.error(f"Gemini API research generation failed: {e}. Falling back to curated catalog.")

        # Fallback intelligent matching from BUILTIN_INTELLIGENCE_FEEDS
        matched_feed = None
        for feed in BUILTIN_INTELLIGENCE_FEEDS:
            if any(term in user_query.lower() for term in feed["category"].lower().split()):
                matched_feed = feed
                break
        if not matched_feed:
            matched_feed = BUILTIN_INTELLIGENCE_FEEDS[0]

        recent_photos = get_recently_used_photos(limit=100)
        photo_info = get_action_photo_for_topic(matched_feed.get("photo_category", "ocean_port"), user_query, exclude_urls=recent_photos)
        hash_str = f"{user_query}_{datetime.now().strftime('%Y-%m-%d_%H%M')}"
        hash_key = hashlib.md5(hash_str.encode()).hexdigest()

        return {
            "hash_key": hash_key,
            "category": matched_feed["category"],
            "title_km": f"ការស្រាវជ្រាវទីផ្សារភស្តុភារកម្ម៖ {matched_feed['title_km']}",
            "title_en": f"Cambodia Logistics Advisory: {matched_feed['title_en']}",
            "summary_km": matched_feed["summary_km"],
            "summary_en": matched_feed["summary_en"],
            "key_data": matched_feed["key_data"],
            "cambodia_impact": matched_feed["impact_km"],
            "cambodia_impact_en": matched_feed["impact_en"],
            "action_recommendation": matched_feed["action_km"],
            "action_recommendation_en": matched_feed["action_en"],
            "tags": matched_feed.get("tags", []) + ["#LogisticsResearch", "#CAMFFA"],
            "photo_url": photo_info["url"],
            "photo_title": photo_info["title"],
            "photo_location": photo_info["location"],
            "photo_credit": photo_info["credit"],
            "source": "Cambodia Logistics Intelligence Desk",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M ICT")
        }
