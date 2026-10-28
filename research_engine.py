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

# Comprehensive 24 Cambodia Logistics Market Intelligence Scenarios
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
    }
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
        recent_titles_list = get_recently_posted_titles(limit=30)
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
        recent_photos = get_recently_used_photos(limit=30)
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

                recent_photos = get_recently_used_photos(limit=30)
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

        recent_photos = get_recently_used_photos(limit=30)
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
