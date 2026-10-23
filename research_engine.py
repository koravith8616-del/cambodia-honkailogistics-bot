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

# Comprehensive 23 Cambodian Logistics Intelligence & Honkai Logistics Service Scenarios
# All in English, organized into 3 distinct daily dispatch slots:
# Slot 1 (Morning 08:00 ICT): Ocean Freight, Sea Ports & Inland Waterways
# Slot 2 (Midday 13:30 ICT): Cross-Border Trucking, Expressway & Road Haulage
# Slot 3 (Evening 18:00 ICT): Air Cargo, GDCE Customs, SEZ Warehousing & Trade Compliance
BUILTIN_INTELLIGENCE_FEEDS = [
    # =========================================================================
    # SLOT 1: MORNING (08:00 ICT) — OCEAN FREIGHT, PORTS & WATERWAYS
    # =========================================================================
    {
        "slot": "slot_morning",
        "category": "Ocean Freight & Port Operations",
        "title_en": "Sihanoukville Autonomous Port (PAS) Container Terminal Operations & Guaranteed Feeder Space",
        "service_highlight": "Honkai Logistics Priority Ocean Feeder Allocations",
        "summary_en": "Feeder vessel turnaround times at Sihanoukville Autonomous Port (PAS) currently average 12-16 hours with steady container yard fluid operations. Container yard utilization stands at 76%, with active STS gantry crane deployments ensuring rapid vessel loading.",
        "key_data": [
            "PAS Berth Wait Time: 0.5 - 1.0 Day (Normal Operations)",
            "Feeder Slot Availability to Singapore/Port Klang: High / Secured",
            "Transshipment Connection via Cai Mep: 2-3 Days transit",
            "Empty 40ft HQ Equipment: Balanced stock across PAS & Phnom Penh depots"
        ],
        "market_intelligence": "With global shipping carriers maintaining strict cut-offs, exporters must ensure accurate shipping instructions to avoid container rollovers. Capacity on direct feeder services connecting Sihanoukville to Singapore and Port Klang mother vessels remains stable.",
        "honkai_advantage": "Honkai Logistics holds direct service contracts with major regional ocean carriers. We guarantee container space allocations, secure 40ft HQ equipment even during peak shipping cycles, and provide end-to-end milestone tracking from factory floor to overseas discharge port.",
        "action_recommendation": "Shippers are advised to place bookings 5 to 7 days ahead of CY cut-off. Contact Honkai Logistics' ocean operations team to lock in competitive contract rates and secure guaranteed vessel space.",
        "tags": ["#HonkaiLogistics", "#OceanFreight", "#SihanoukvillePort", "#PAS", "#ContainerShipping", "#CambodiaTrade"],
        "photo_category": "ocean_port",
        "source": "Honkai Ocean Freight Operations & PAS Maritime Network"
    },
    {
        "slot": "slot_morning",
        "category": "Ocean Freight & Transpacific Routes",
        "title_en": "Transpacific Ocean Freight: Rapid Feeder Connections to US West Coast via Cai Mep Hub",
        "service_highlight": "Honkai Express Transpacific & Europe Ocean Solutions",
        "summary_en": "Transpacific container transit times out of Cambodia have optimized significantly. Combining Sihanoukville feeder routes with direct mother vessel loops at Cai Mep deep-water port allows Cambodian exporters to reach Los Angeles and Long Beach in 16 to 19 days.",
        "key_data": [
            "Transit to US West Coast (LAX/LGB): 16 - 19 Days via Cai Mep connection",
            "Transit to Northern Europe (Rotterdam/Hamburg): 26 - 30 Days",
            "Ocean Spot Rates: Competitive index with stable bunker adjustment factors (BAF)",
            "Container Equipment: 40ft High Cube & 20ft Standard available with pre-trip inspection"
        ],
        "market_intelligence": "US retail inventory restocking continues to drive steady demand for Cambodian apparel, footwear, and travel goods. Securing reliable transshipment loops through regional deep-sea hubs is vital to avoid congestion delays.",
        "honkai_advantage": "Honkai Logistics offers streamlined, single-bill-of-lading (B/L) services directly connecting Cambodian manufacturing hubs to North America and Europe. We eliminate double handling risks, manage destination customs clearance, and ensure guaranteed carrier space on tier-1 vessel alliances.",
        "action_recommendation": "Book your US and Europe export shipments with Honkai Logistics to take advantage of priority mother vessel boarding passes and dedicated overseas customs support.",
        "tags": ["#HonkaiLogistics", "#Transpacific", "#USWestCoast", "#EuropeShipping", "#ContainerLogistics", "#GarmentExport"],
        "photo_category": "ocean_port",
        "source": "Honkai Global Forwarding Division & Shipping Line Alliance"
    },
    {
        "slot": "slot_morning",
        "category": "Inbound Ocean Freight & Raw Materials",
        "title_en": "Intra-Asia Inbound Ocean Express: Fast-Track Raw Material Deliveries from China to Sihanoukville",
        "service_highlight": "Honkai Inbound Factory Supply Chain & Raw Material Logistics",
        "summary_en": "Direct container services from Shanghai, Ningbo, Qingdao, and Shekou to Sihanoukville Port maintain regular weekly sailings with average ocean transit of 6 to 9 days. Rapid discharge protocols at PAS ensure prompt transfer to Phnom Penh industrial zones.",
        "key_data": [
            "Transit from Ningbo/Shanghai to PAS: 7 - 9 Days direct",
            "Transit from Shekou/Guangzhou to PAS: 5 - 7 Days direct",
            "Port Free Demurrage Package: 14 - 21 Days available for contracted accounts",
            "Container Gate-Out Speed: Under 4 hours post customs release"
        ],
        "market_intelligence": "Textile, footwear raw materials, and machinery components represent over 60% of inbound container volumes through Sihanoukville. Timely raw material arrival is crucial for garment factories to maintain strict buyer delivery schedules.",
        "honkai_advantage": "Honkai Logistics provides comprehensive inbound supply chain management. We coordinate directly with your overseas suppliers in China, track container manufacturing milestones, and expedite port gate-out upon arrival to keep your assembly lines running without interruption.",
        "action_recommendation": "Partner with Honkai Logistics for your inbound material shipments from China and ASEAN. Enjoy generous detention-free time and transparent all-inclusive freight pricing.",
        "tags": ["#HonkaiLogistics", "#InboundLogistics", "#RawMaterials", "#ChinaToCambodia", "#GarmentManufacturing"],
        "photo_category": "ocean_port",
        "source": "Honkai Asian Freight Network & Port Authority Data"
    },
    {
        "slot": "slot_morning",
        "category": "Inland Waterways & River Barge",
        "title_en": "Phnom Penh Autonomous Port (PPAP LM17) River Barge Logistics: Sustainable & Cost-Effective Transport",
        "service_highlight": "Honkai Mekong River Barge & Inland Feeder Service",
        "summary_en": "Inland container barge traffic between Phnom Penh Autonomous Port (PPAP LM17) and Cai Mep / Cat Lai ports operates on daily scheduled departures. River transport provides a low-carbon, highly economical alternative for heavy container cargo.",
        "key_data": [
            "Barge Transit Time (PPAP to Cai Mep): 24 - 30 Hours downriver",
            "Cost Advantage: Up to $80 - $120 savings per 40ft container vs. road haulage",
            "Barge Fleet Capacity: 120 - 250 TEU per vessel with high frequency",
            "Reefer Container Support: Active monitoring with continuous generator power"
        ],
        "market_intelligence": "For factories situated along the Mekong and Tonle Sap rivers or southern Phnom Penh, river barge logistics eliminates highway toll expenses and bypasses road weight restrictions for heavy commodity cargo.",
        "honkai_advantage": "Honkai Logistics operates integrated barge-to-mother-vessel connections via PPAP LM17. We handle customs bonded river transit, container lifting, terminal handling, and smooth transshipment at Cai Mep deep sea terminals under one unified bill of lading.",
        "action_recommendation": "Evaluate your heavy freight routes today. Switching suitable container volumes to Honkai's river barge service will directly reduce your logistics overhead by up to 25%.",
        "tags": ["#HonkaiLogistics", "#PPAP", "#RiverBarge", "#MekongLogistics", "#CostSavingFreight", "#GreenLogistics"],
        "photo_category": "canal_waterways",
        "source": "Honkai Waterway Operations & PPAP Terminal Management"
    },
    {
        "slot": "slot_morning",
        "category": "Equipment & Container Depots",
        "title_en": "Container Depot Operations: Guaranteed 40ft High Cube & 20ft GP Equipment Availability",
        "service_highlight": "Honkai Container Equipment Guarantee & Pre-Trip Inspection",
        "summary_en": "Maintaining balanced empty container equipment at Phnom Penh dry ports and Sihanoukville terminal depots is essential for uninterrupted manufacturing export schedules. Honkai Logistics actively positions shipping line equipment to prevent loading bottlenecks.",
        "key_data": [
            "40ft HQ Availability: High stock across Teng Lay, Olair & So Ngoun depots",
            "Container Quality Grade: Food-grade and textile-grade dry clean certified",
            "Gate-In Cut-Off Flexibility: Extended late-gate acceptance for Honkai clients",
            "Equipment Turnaround: Streamlined empty return with zero administrative hold-up"
        ],
        "market_intelligence": "During peak quarter export cycles, equipment imbalances can stall factory stuffing lines. Securing equipment release orders (ERO) in advance protects exporters from costly production hold-ups.",
        "honkai_advantage": "Honkai Logistics holds dedicated container depot release allocations with leading carriers. We guarantee clean, watertight, odor-free 40ft High Cube containers positioned at your loading bay exactly when you need them.",
        "action_recommendation": "Avoid equipment shortages before month-end rushes. Pre-allocate your 40ft HQ export containers through Honkai Logistics' depot management team.",
        "tags": ["#HonkaiLogistics", "#ContainerDepot", "#40ftHQ", "#EquipmentGuarantee", "#ExportLogistics"],
        "photo_category": "ocean_port",
        "source": "Honkai Equipment Desk & Dry Port Terminal Network"
    },
    {
        "slot": "slot_morning",
        "category": "Funan Techo Canal & Multi-Modal",
        "title_en": "Funan Techo Canal Strategic Integration: Future-Proofing Cambodia's Multi-Modal Logistics Network",
        "service_highlight": "Honkai Multi-Modal Route Planning & Strategic Infrastructure Advisory",
        "summary_en": "The groundbreaking Funan Techo Canal project (180 km) represents a transformative leap for Cambodia's transport autonomy, linking the inland Mekong River network directly to the deep-water coastal sea at Kep province.",
        "key_data": [
            "Project Scope: 180 km waterway connecting Kandal, Takeo, Kampot, and Kep provinces",
            "Vessel Capacity: Accommodating 1,000 to 3,000 DWT inland cargo vessels and barges",
            "Logistics Impact: Projected 25% - 30% reduction in long-term domestic cargo transit costs",
            "Strategic Advantage: Autonomous direct sea access eliminating third-party transit dependencies"
        ],
        "market_intelligence": "Industrial developers and forward-thinking manufacturing investors are actively evaluating land and factory positioning along the planned canal corridor to capture future logistics cost savings.",
        "honkai_advantage": "Honkai Logistics is at the forefront of Cambodia's infrastructure evolution. We help industrial clients future-proof their supply chain network, designing multimodal routing that integrates road, river barge, and deep-sea shipping for optimal long-term efficiency.",
        "action_recommendation": "Consult Honkai Logistics' strategic advisory team to understand how emerging infrastructure like the Funan Techo Canal and new expressways can optimize your long-term logistics footprint in Cambodia.",
        "tags": ["#HonkaiLogistics", "#FunanTechoCanal", "#CambodiaInfrastructure", "#FutureLogistics", "#MultiModalTransport"],
        "photo_category": "canal_waterways",
        "source": "Honkai Strategic Planning & Cambodia Infrastructure Development Watch"
    },
    {
        "slot": "slot_morning",
        "category": "Ocean Freight Rate Benchmarks",
        "title_en": "Cambodia Ocean Freight Rate Benchmark: Strategic Spot vs Contract Optimization",
        "service_highlight": "Honkai Long-Term Contract Rate Stability & Spot Optimization",
        "summary_en": "Ocean container spot freight indices across transpacific and intra-Asia routes continue to adjust following global carrier capacity realignments. Shippers in Cambodia benefit from locking in balanced quarterly contracts that combine price stability with space protection.",
        "key_data": [
            "Asia - US West Coast (FEU): Stable bracket with competitive bunker clauses",
            "Asia - Europe (TEU): Balanced feeder rates through Singapore hubs",
            "Intra-Asia Feeder (PAS to China base ports): Highly competitive per-box pricing",
            "Contract Flexibility: Custom volume tiers with locked-in peak season surcharges (PSS)"
        ],
        "market_intelligence": "Spot market volatility can dramatically inflate per-unit export costs. Corporate shippers with predictable monthly volumes achieve greater margin security through indexed freight contracts.",
        "honkai_advantage": "Honkai Logistics delivers transparent, predictable ocean freight pricing. We benchmark global indexes weekly to offer clients optimal contract and spot rate combinations with zero hidden destination fees.",
        "action_recommendation": "Review your quarterly freight expenditure with Honkai Logistics. Request a customized rate card comparison to discover where your supply chain can capture immediate savings.",
        "tags": ["#HonkaiLogistics", "#FreightRates", "#OceanBenchmark", "#CostOptimization", "#GlobalTrade"],
        "photo_category": "rate_index",
        "source": "Honkai Freight Analytics & Shipping Line Tariff Bureau"
    },

    # =========================================================================
    # SLOT 2: MIDDAY (13:30 ICT) — TRUCKING, EXPRESSWAY & CROSS-BORDER
    # =========================================================================
    {
        "slot": "slot_midday",
        "category": "Expressway Container Haulage",
        "title_en": "Phnom Penh - Sihanoukville Expressway Container Haulage: 2.5-Hour Transit Guarantee",
        "service_highlight": "Honkai Dedicated Trucking Fleet & GPS Live Telematics",
        "summary_en": "The Phnom Penh - Sihanoukville Expressway continues to provide the fastest freight corridor in Cambodia, reducing heavy truck transit times to just 2 hours and 15 minutes. Road safety, electronic toll management, and modern rest stops ensure uninterrupted container flow.",
        "key_data": [
            "Transit Time: 2h 15m (Phnom Penh Dry Ports to PAS Container Terminal)",
            "Fleet Availability: Dedicated Prime Movers & 40ft/45ft skeletal chassis",
            "On-Time Delivery Performance: 99.4% on-schedule record",
            "Security: 24/7 Real-Time GPS Tracking & electronic cargo door seals"
        ],
        "market_intelligence": "Speed-to-port is the single biggest factor for factories meeting Friday and weekend ocean vessel cut-offs. Reliable trucking partners with modern prime movers eliminate the risk of vehicle breakdowns and missed sailings.",
        "honkai_advantage": "Honkai Logistics operates its own dedicated fleet of modern heavy container trucks equipped with live GPS telematics and speed monitoring. We guarantee prompt container positioning at your factory loading dock and round-the-clock weekend dispatch to Sihanoukville.",
        "action_recommendation": "Never worry about missed vessel cut-offs again. Trust Honkai Logistics for guaranteed expressway haulage and transparent live truck location updates sent directly to your dispatch team.",
        "tags": ["#HonkaiLogistics", "#ExpresswayHaulage", "#ContainerTrucking", "#OnTimeDelivery", "#CambodiaSupplyChain"],
        "photo_category": "trucking_highway",
        "source": "Honkai Fleet Operations & Expressway Dispatch Command"
    },
    {
        "slot": "slot_midday",
        "category": "Cross-Border Trucking (Vietnam)",
        "title_en": "Bavet - Moc Bai Border Corridor: Fast-Track Bonded Trucking Between Cambodia & Vietnam",
        "service_highlight": "Honkai Cross-Border Bonded Trucking & Dual-Plate Transit",
        "summary_en": "Cross-border container traffic through the Bavet (Cambodia) - Moc Bai (Vietnam) international border gate maintains smooth customs operations with an average clearance turnaround of 2 to 3 hours. Electronic customs e-seals ensure high-speed processing.",
        "key_data": [
            "Border Clearance Time: 2 - 3 Hours with pre-filed e-manifests",
            "Transit Time (Phnom Penh to Ho Chi Minh City/Cai Mep): Under 14 Hours door-to-door",
            "Service Frequency: Daily scheduled bonded truck departures in both directions",
            "Customs Processing: Electronic transit customs seals (GDCE / Vietnam Customs)"
        ],
        "market_intelligence": "Manufacturing enterprises in Svay Rieng SEZs (Manhattan, Tai Seng) and Phnom Penh utilize the Bavet overland corridor for rapid access to Vietnam's ocean ports and for importing time-critical Vietnamese components.",
        "honkai_advantage": "Honkai Logistics provides comprehensive cross-border logistics solutions with licensed customs clearance teams on both sides of the border. We operate seamless transit trucks, manage cross-border transshipment, and eliminate border hold-ups with pre-vetted customs documentation.",
        "action_recommendation": "Accelerate your regional supply chain. Contact Honkai Logistics for scheduled daily trucking between Phnom Penh, Bavet, Ho Chi Minh City, and Cai Mep ports.",
        "tags": ["#HonkaiLogistics", "#CrossBorderTrucking", "#BavetBorder", "#VietnamCambodia", "#BondedTransport"],
        "photo_category": "trucking_highway",
        "source": "Honkai Cross-Border Department & Border Customs Bureau"
    },
    {
        "slot": "slot_midday",
        "category": "Cross-Border Trucking (Thailand)",
        "title_en": "Poipet - Aranyaprathet Overland Corridor: Direct Intermodal Haulage Connecting Thailand & Cambodia",
        "service_highlight": "Honkai Thailand - Cambodia Door-to-Door Overland Transport",
        "summary_en": "The Poipet - Aranyaprathet commercial border checkpoint provides a vital economic link for automotive parts, industrial machinery, food packaging, and construction materials moving between Bangkok and Phnom Penh.",
        "key_data": [
            "Door-to-Door Transit (Bangkok to Phnom Penh): 24 - 36 Hours",
            "Border Clearance: Seamless intermodal cross-docking at Poipet Dry Port",
            "Cargo Safety: Full cargo insurance and secure lashing verification",
            "Customs Documentation: Form D compliance for zero tariff duty benefits"
        ],
        "market_intelligence": "Overland trade with Thailand represents an essential corridor for Cambodian manufacturing plants seeking short lead times for packaging, electronic harnesses, and construction inputs without waiting for ocean feeder sailings.",
        "honkai_advantage": "Honkai Logistics manages end-to-end Thailand-Cambodia road freight. Our specialized team coordinates factory pick-up in Bangkok, seamless border transit at Poipet, GDCE customs import declaration, and direct final-mile delivery across all Cambodian provinces.",
        "action_recommendation": "Switch urgent regional freight from ocean to Honkai's express overland route from Thailand. Gain up to 5 days on transit time with competitive door-to-door pricing.",
        "tags": ["#HonkaiLogistics", "#PoipetBorder", "#ThailandCambodia", "#OverlandFreight", "#IntermodalLogistics"],
        "photo_category": "trucking_highway",
        "source": "Honkai Overland Freight Division & Border Logistics Authority"
    },
    {
        "slot": "slot_midday",
        "category": "Heavy Haulage & Project Cargo",
        "title_en": "Heavy Lift & Project Cargo Logistics: Specialized Transport for Machinery & Factory Infrastructure",
        "service_highlight": "Honkai Heavy Equipment & Turnkey Factory Relocation",
        "summary_en": "Cambodia's ongoing industrial expansion demands robust project cargo handling capabilities. Moving oversized industrial boilers, textile weaving looms, solar energy structures, and heavy machinery requires engineering precision and legal road escorts.",
        "key_data": [
            "Chassis Capability: Multi-axle hydraulic trailers, low-bed and extendable flatbeds",
            "Cargo Capacity: Up to 120 Metric Tons per individual transport unit",
            "Safety Standards: Full route survey, bridge load assessments & Ministry permits",
            "On-Site Support: Certified mobile cranes & heavy rigging teams at destination"
        ],
        "market_intelligence": "Importing complex industrial equipment demands detailed planning to comply with Ministry of Public Works and Transport (MPWT) road regulations and ensure safe delivery without infrastructure damage.",
        "honkai_advantage": "Honkai Logistics is Cambodia's trusted specialist for project cargo. From vessel hook at Sihanoukville Port to foundation placement inside your factory, our dedicated project engineers manage road permits, police escorts, and safe heavy-lift offloading.",
        "action_recommendation": "Planning new factory setup or machinery imports? Consult Honkai Logistics' project cargo engineering team for a turnkey feasibility study and route survey.",
        "tags": ["#HonkaiLogistics", "#ProjectCargo", "#HeavyLift", "#FactoryRelocation", "#MachineryTransport"],
        "photo_category": "trucking_highway",
        "source": "Honkai Engineering & Project Logistics Division"
    },
    {
        "slot": "slot_midday",
        "category": "Cross-Border Bonded Shuttles",
        "title_en": "Same-Day Bonded Shuttle: Connecting Southern Vietnam Industrial Hubs to Phnom Penh Factories",
        "service_highlight": "Honkai Scheduled Daily Cross-Border Bonded Express",
        "summary_en": "For just-in-time manufacturing assembly lines, Honkai Logistics operates scheduled daily bonded trucking shuttles between Binh Duong/Dong Nai industrial hubs in Vietnam and Special Economic Zones in Phnom Penh and Kandal.",
        "key_data": [
            "Departure Frequency: 2 Daily scheduled convoys (Morning & Night runs)",
            "Door-to-Door Turnaround: Under 12 hours from supplier dock to receiving bay",
            "Security Protocol: GPS geo-fenced route monitoring and electronic tamper alerts",
            "Cargo Types: Precision electronics, carton packaging, haberdashery, and trim inputs"
        ],
        "market_intelligence": "Relying on fragmented local trucking for regional cross-border supply chains leads to unpredictable border transloading delays and damaged cargo.",
        "honkai_advantage": "Honkai Logistics operates its own fleet of dual-licensed cross-border vehicles with certified bonded transport licenses. Your goods remain untouched in secure locked containers from initial origin loading straight to final destination.",
        "action_recommendation": "Eliminate regional assembly line downtime. Contact Honkai Logistics to establish scheduled cross-border bonded shuttles tailored to your production takt time.",
        "tags": ["#HonkaiLogistics", "#BondedShuttle", "#CrossBorderExpress", "#JustInTime", "#ManufacturingLogistics"],
        "photo_category": "trucking_highway",
        "source": "Honkai Cross-Border Dispatch & Regional Transport Office"
    },
    {
        "slot": "slot_midday",
        "category": "Expressway Weekend Gate-In",
        "title_en": "Weekend & Night Drayage: Beating Port Cut-Offs with Honkai 24/7 Expressway Dispatch",
        "service_highlight": "Honkai 24/7 Emergency Drayage & Weekend Port Gate-In Assurance",
        "summary_en": "Weekend port congestion and Sunday midnight vessel cut-offs create immense pressure on factory shipping managers. Honkai Logistics operates round-the-clock weekend drayage teams on the Phnom Penh - Sihanoukville Expressway to ensure zero missed sailings.",
        "key_data": [
            "Operations Window: Continuous 24/7 dispatch including public holidays and Sundays",
            "Cut-off Buffer: Safe terminal gate-in guaranteed 4 hours before carrier SI cut-off",
            "Chassis Availability: Over 60 heavy chassis stationed across Phnom Penh industrial corridors",
            "Driver Team: Dual-driver certified teams for night-shift expressway transport"
        ],
        "market_intelligence": "Over 45% of Cambodian apparel shipments are loaded between Friday evening and Saturday afternoon. Having an active 24/7 drayage partner is essential for meeting carrier CY closing times.",
        "honkai_advantage": "When other transport providers shut down for the weekend, Honkai Logistics' dispatch tower remains fully staffed. Our trucks roll non-stop, our port coordinators stand by at PAS terminal gates, and your cargo safely catches its booked vessel.",
        "action_recommendation": "Have urgent weekend container stuffing scheduled? Book your weekend drayage with Honkai Logistics and relax knowing your export cut-off is 100% secured.",
        "tags": ["#HonkaiLogistics", "#WeekendDrayage", "#PortGateIn", "#ExpresswayTrucking", "#ReliableLogistics"],
        "photo_category": "trucking_highway",
        "source": "Honkai Drayage Command & PAS Terminal Gate Registry"
    },
    {
        "slot": "slot_midday",
        "category": "Commercial Fuel & Fleet Benchmarks",
        "title_en": "Cambodia Commercial Diesel & Transport Benchmark: Managing Fleet Fuel Surcharges Efficiently",
        "service_highlight": "Honkai Transparent Fuel Surcharge (FSC) Policy & Rate Predictability",
        "summary_en": "Retail diesel prices in Cambodia remain stable at approximately $1.02 per liter, supporting predictable inland transportation budgeting. Honkai Logistics implements a transparent, government-indexed Fuel Surcharge (FSC) mechanism that protects clients from arbitrary price hikes.",
        "key_data": [
            "Commercial Diesel Benchmark: Stable at ~$1.02 / Liter nationwide",
            "Fuel Efficiency Optimization: Modern aerodynamic prime movers saving up to 8% fuel",
            "FSC Formula: Open, auditable monthly index linked to Ministry of Commerce postings",
            "Cost Savings: Zero hidden fees, all toll and terminal gate fees fully itemized"
        ],
        "market_intelligence": "Opaque fuel surcharges from unregulated trucking operators frequently create unexpected budget variances on commercial logistics invoices.",
        "honkai_advantage": "Honkai Logistics believes in complete financial transparency. We provide clear, itemized rate cards with predictable fuel indexing so your finance and procurement teams can audit costs with 100% confidence.",
        "action_recommendation": "Review your current road haulage contract. Switch to Honkai Logistics for fair, auditable transportation rates backed by professional corporate invoicing.",
        "tags": ["#HonkaiLogistics", "#FuelSurcharge", "#TruckingBenchmark", "#TransparentLogistics", "#CambodiaTransport"],
        "photo_category": "rate_index",
        "source": "Honkai Fleet Economics Desk & Ministry of Commerce Price Postings"
    },

    # =========================================================================
    # SLOT 3: EVENING (18:00 ICT) — AIR CARGO, CUSTOMS, SEZ & FACTORY LOGISTICS
    # =========================================================================
    {
        "slot": "slot_evening",
        "category": "Air Cargo & Express Logistics",
        "title_en": "Phnom Penh Air Cargo Capacity & Express Solutions for Urgent Fashion & Electronics",
        "service_highlight": "Honkai Air Freight Express & Priority Airport Apron Handling",
        "summary_en": "Air cargo operations out of Phnom Penh (PNH/TIA) provide critical speed for seasonal garment samples, high-end footwear collections, and time-sensitive electronic components. Scheduled freighter connections via regional air hubs ensure rapid global connectivity.",
        "key_data": [
            "PNH - US West Coast (LAX/SFO/ORD): 3 - 4 Days transit via express hub",
            "PNH - Europe (FRA/AMS/CDG): 2 - 3 Days transit via Middle East/Asia hubs",
            "Freighter Capacity: Blocked space on scheduled widebody flights",
            "Airport Handling: Priority export screening and customs pre-clearance"
        ],
        "market_intelligence": "When production delays threaten purchase order cancellation penalties, air freight becomes an indispensable safety net for factory executives needing guaranteed arrival at global retail distribution centers.",
        "honkai_advantage": "Honkai Logistics maintains priority allocation agreements with premier international air carriers. We secure air space during peak periods, offer charter flight arrangements for heavy emergency volumes, and handle door-to-airport express delivery in record time.",
        "action_recommendation": "For critical PO deadlines, leverage Honkai Logistics' Air Freight Express. Contact our air desk 24/7 for instant flight routing, confirmed space, and door-to-door courier options.",
        "tags": ["#HonkaiLogistics", "#AirFreight", "#AirCargo", "#ExpressLogistics", "#FashionSupplyChain", "#AirportLogistics"],
        "photo_category": "air_cargo",
        "source": "Honkai Aviation Logistics Department & IATA Cargo Network"
    },
    {
        "slot": "slot_evening",
        "category": "Specialized Air Freight",
        "title_en": "Garment on Hanger (GOH) Air Logistics: Wrinkle-Free Direct-to-Retail Garment Solutions",
        "service_highlight": "Honkai Specialized GOH Air & Ocean Container Solutions",
        "summary_en": "Specialized Garment on Hanger (GOH) transport allows high-value fashion apparel to travel directly from Cambodian stitching floors to European and American department store racks without folding, ironing, or repackaging.",
        "key_data": [
            "Equipment: Structural bar and string GOH configurations for 20ft/40ft & ULDs",
            "Retail Ready: Direct-to-floor delivery with price tags and security sensors attached",
            "Cost Efficiency: Eliminates secondary retail pressing and packaging expenses",
            "Protection: High-grade moisture-absorbing desiccant and dust-proof interior lining"
        ],
        "market_intelligence": "International fashion retailers increasingly demand GOH shipping to accelerate stock replenishment cycles and minimize carbon-intensive packaging waste.",
        "honkai_advantage": "Honkai Logistics possesses dedicated GOH conversion expertise in Cambodia. Our skilled ground teams professionally outfit containers and air cargo pallets, ensuring your premium garments arrive in pristine, showroom condition.",
        "action_recommendation": "Upgrade your export packaging with Honkai's GOH solutions. Contact our apparel logistics specialists to review equipment specifications and sample load layouts.",
        "tags": ["#HonkaiLogistics", "#GOH", "#GarmentOnHanger", "#TextileLogistics", "#FashionExport", "#GarmentSupplyChain"],
        "photo_category": "air_cargo",
        "source": "Honkai Textile Logistics Division & Airline Cargo Partners"
    },
    {
        "slot": "slot_evening",
        "category": "Customs Brokerage & GDCE Compliance",
        "title_en": "GDCE ASYCUDA World Pre-Clearance & CamDX Digital Integration: Fast-Track Green Lane Release",
        "service_highlight": "Honkai Licensed Customs Brokerage & Zero-Demurrage Guarantee",
        "summary_en": "The General Department of Customs and Excise (GDCE) continues to modernize customs operations through ASYCUDA World and the CamDX National Single Window. Proper electronic declaration filing 24 to 48 hours prior to vessel arrival ensures seamless green channel release.",
        "key_data": [
            "ASYCUDA Green Channel Rate: Over 92% for Honkai-cleared shipments",
            "Pre-Arrival Declaration: Electronic manifest filing 48 hours prior to berthing",
            "Paperless Processing: Fully digitalized duty tax payment and clearance slips",
            "Compliance Record: 100% audit-approved regulatory clearance standards"
        ],
        "market_intelligence": "Incorrect HS codes, invoice discrepancies, or late paperwork filing lead to customs red/yellow channel holds, triggering expensive port storage and container demurrage fines that eat into factory profit margins.",
        "honkai_advantage": "Honkai Logistics employs certified, highly experienced customs brokers stationed at Sihanoukville Port, Phnom Penh Dry Ports, and international borders. We conduct pre-shipment document audits, verify HS codes, and guarantee expedited clearance with zero unnecessary delays.",
        "action_recommendation": "Protect your bottom line against demurrage charges. Hand your customs brokerage over to Honkai Logistics for guaranteed compliance, speed, and peace of mind.",
        "tags": ["#HonkaiLogistics", "#CustomsBrokerage", "#GDCE", "#ASYCUDA", "#CamDX", "#TradeCompliance"],
        "photo_category": "customs_inspection",
        "source": "Honkai Customs Brokerage Division & GDCE Public Directives"
    },
    {
        "slot": "slot_evening",
        "category": "Trade Agreements & Tariff Advisory",
        "title_en": "Maximizing Tariff Savings: RCEP, Form D, Form E & Rules of Origin for Cambodian Manufacturers",
        "service_highlight": "Honkai Free Trade Agreement & Tariff Optimization Advisory",
        "summary_en": "Cambodia's strategic participation in the Regional Comprehensive Economic Partnership (RCEP), ASEAN ATIGA (Form D), and bilateral trade agreements offers zero or reduced import duties on thousands of industrial raw materials and capital machinery.",
        "key_data": [
            "RCEP Benefits: Zero tariffs on participating textile yarn, dyes, and machinery",
            "ATIGA Form D: Duty-free intra-ASEAN movement for qualifying manufactured goods",
            "Certificate of Origin (CO): Accelerated online issuance via Ministry of Commerce",
            "Duty Savings Potential: Up to 7% to 15% reduction in total landed import cost"
        ],
        "market_intelligence": "Understanding the specific origin criterion (value-added content vs. change in tariff classification) is the key to unlocking millions of dollars in duty exemptions for Cambodian industrial operators.",
        "honkai_advantage": "Honkai Logistics provides expert trade compliance advisory. We assist manufacturing clients in reviewing bill of materials, obtaining valid Certificates of Origin (CO), and navigating complex tariff regulations to ensure maximum legal duty savings.",
        "action_recommendation": "Schedule a complimentary tariff review with Honkai Logistics' trade advisory team to identify untapped duty savings across your current supply chain routes.",
        "tags": ["#HonkaiLogistics", "#RCEP", "#RulesOfOrigin", "#TradeAgreements", "#DutyFreeImport", "#CambodiaEconomy"],
        "photo_category": "customs_inspection",
        "source": "Honkai Trade Advisory Team & Ministry of Commerce Guidelines"
    },
    {
        "slot": "slot_evening",
        "category": "Special Economic Zone (SEZ) Logistics",
        "title_en": "Special Economic Zone (SEZ) Bonded Warehousing & Factory Distribution Solutions",
        "service_highlight": "Honkai SEZ Logistics & Vendor-Managed Inventory (VMI)",
        "summary_en": "Special Economic Zones including Royal Group Phnom Penh SEZ, Manhattan SEZ in Bavet, and Sihanoukville Special Economic Zone (SSEZ) host modern bonded logistics warehouses that support just-in-time raw material staging and container consolidation.",
        "key_data": [
            "Warehouse Facilities: High-bay bonded and non-bonded secure facilities",
            "On-Site Customs: Immediate duty-suspension status inside bonded zones",
            "Inventory Control: Cloud-based WMS with real-time barcode SKU tracking",
            "Value-Added Services: Kitting, palletizing, labeling, and export quality inspection"
        ],
        "market_intelligence": "Operating factory warehouses at full capacity creates operational bottlenecks. Forward-thinking manufacturers utilize external bonded warehouses to manage buffer inventory and optimize floor space for manufacturing lines.",
        "honkai_advantage": "Honkai Logistics provides comprehensive 3PL warehousing and vendor-managed inventory (VMI) services across Cambodia's major industrial zones. We store your raw materials, pick and pack upon order, and deliver directly to your assembly line within hours.",
        "action_recommendation": "Optimize your factory floor space. Speak with Honkai Logistics today about flexible bonded warehousing contracts tailored to your seasonal inventory fluctuations.",
        "tags": ["#HonkaiLogistics", "#SEZLogistics", "#BondedWarehouse", "#InventoryManagement", "#PhnomPenhSEZ", "#3PL"],
        "photo_category": "factory_logistics",
        "source": "Honkai Contract Logistics & SEZ Industrial Zone Reports"
    },
    {
        "slot": "slot_evening",
        "category": "Cold Chain & Reefer Logistics",
        "title_en": "Reefer & Cold Chain Solutions: Safeguarding Temperature-Sensitive Food, Agriculture & Pharma",
        "service_highlight": "Honkai Active Reefer Fleet & Continuous Temperature Telematics",
        "summary_en": "The growth of Cambodia's fresh agricultural exports (fresh mangoes, Cavendish bananas, bird's nest) and imports of pharmaceuticals requires stringent cold chain integrity from harvesting packhouses to overseas consumers.",
        "key_data": [
            "Temperature Range: Precise control from -25°C deep freeze to +15°C chilled",
            "Reefer Fleet: Modern Carrier and Thermo King refrigerated container chassis",
            "Live Telematics: Real-time temperature, humidity, and power monitoring alarms",
            "Port Integration: Priority reefer plug-in at PAS and PPAP cold terminals"
        ],
        "market_intelligence": "A single temperature excursion during inland transit can result in the total rejection of agricultural or medical cargo by overseas health and phytosanitary authorities.",
        "honkai_advantage": "Honkai Logistics operates an advanced cold chain logistics division. Our refrigerated trucks and reefer containers undergo rigorous pre-trip inspection (PTI), feature backup generator sets, and provide automated temperature logging reports for every shipment.",
        "action_recommendation": "Protect your perishable assets with Honkai's certified cold chain services. Contact our cold chain desk for customized temperature protocols and dedicated reefer equipment.",
        "tags": ["#HonkaiLogistics", "#ColdChain", "#ReeferLogistics", "#AgriExport", "#PharmaLogistics", "#TemperatureControlled"],
        "photo_category": "factory_logistics",
        "source": "Honkai Cold Chain Operations & Agri-Trade Association"
    },
    {
        "slot": "slot_evening",
        "category": "LCL Consolidation & Small Cargo",
        "title_en": "Weekly LCL Ocean & Air Consolidation: Cost-Effective Logistics for Growing Businesses",
        "service_highlight": "Honkai Less-Than-Container-Load (LCL) Dedicated Consolidation",
        "summary_en": "For businesses importing or exporting volumes that do not fill an entire 20ft or 40ft container, weekly Less-Than-Container-Load (LCL) consolidation offers significant cost savings without sacrificing transit reliability.",
        "key_data": [
            "Weekly Departures: Shanghai, Ningbo, Shenzhen, Guangzhou, and Bangkok to Phnom Penh",
            "Pricing Model: Transparent per-CBM billing with zero hidden destination terminal fees",
            "Cargo Safety: Professional palletizing, shrink-wrapping, and barcode cargo tracking",
            "Customs Clearance: Comprehensive consolidated import clearance handled by Honkai"
        ],
        "market_intelligence": "Small and medium enterprises frequently suffer from inflated destination delivery fees when utilizing non-transparent freight forwarders for small consolidation cargo.",
        "honkai_advantage": "Honkai Logistics runs direct, company-managed LCL consolidation boxes. We provide honest, upfront CBM quotes, eliminate surprise destination charges, and deliver your cargo straight to your warehouse door in Phnom Penh or the provinces.",
        "action_recommendation": "Stop overpaying for small cargo. Switch to Honkai Logistics' weekly LCL consolidation service for fair per-CBM rates and reliable weekly schedules.",
        "tags": ["#HonkaiLogistics", "#LCLConsolidation", "#SmallCargo", "#CBMFreight", "#SMETrade", "#PhnomPenhDelivery"],
        "photo_category": "factory_logistics",
        "source": "Honkai Consolidation Services & Freight Forwarding Desk"
    },
    {
        "slot": "slot_evening",
        "category": "Strategic Supply Chain Management",
        "title_en": "Honkai Logistics 24/7 Control Tower: Complete Supply Chain Visibility & Milestone Tracking",
        "service_highlight": "Honkai Digital Logistics Control Tower & Dedicated Key Account Management",
        "summary_en": "In modern manufacturing, visibility is control. Honkai Logistics integrates digital shipment tracking, automated email/SMS status alerts, and dedicated 24/7 key account managers to give supply chain executives instant oversight of their global cargo movements.",
        "key_data": [
            "Milestone Updates: Real-time notification at container pickup, port gate-in, vessel departure, and arrival",
            "Dedicated Support: One-on-one key account manager for every corporate client",
            "Resolution Speed: Direct escalation hotline with resolution times under 30 minutes",
            "Documentation Archival: Secure digital portal for all shipping bills of lading, customs slips, and invoices"
        ],
        "market_intelligence": "Leading international brands require their manufacturing partners in Cambodia to maintain fully auditable, transparent logistics tracking systems with zero communication gaps.",
        "honkai_advantage": "At Honkai Logistics, we treat your business as our own. You never speak to automated answering bots — our dedicated logistics specialists monitor your shipments around the clock, proactively solving bottlenecks before they impact your schedule.",
        "action_recommendation": "Experience a higher standard of freight forwarding. Partner with Honkai Logistics and let our 24/7 dedicated control tower take your supply chain reliability to the next level.",
        "tags": ["#HonkaiLogistics", "#SupplyChainManagement", "#CustomerTrust", "#LogisticsVisibility", "#FreightForwarding"],
        "photo_category": "rate_index",
        "source": "Honkai Customer Service & Digital Operations Center"
    },
    {
        "slot": "slot_evening",
        "category": "Risk Management & Cargo Insurance",
        "title_en": "All-Risk Cargo Insurance & Comprehensive Asset Protection for Cambodian Exporters & Importers",
        "service_highlight": "Honkai Comprehensive Cargo Insurance & Secure Transport Protocols",
        "summary_en": "Maritime perils, heavy seasonal monsoon weather, and intermodal transshipment risks make comprehensive cargo insurance an indispensable component of sound corporate risk governance for all international shipments.",
        "key_data": [
            "Coverage Scope: Institute Cargo Clauses (A) — Complete all-risk door-to-door protection",
            "Claims Process: Fast-track local claims assessment and swift settlement processing",
            "Tamper-Proof Seals: High-security ISO 17712 compliant bolt seals on all container haulage",
            "Asset Security: Armed escort availability for high-value electronics and solar technology cargo"
        ],
        "market_intelligence": "Standard carrier liability limits under international maritime conventions (Hague-Visby Rules) are extremely low and provide virtually no financial recovery in cases of container loss or storm damage at sea.",
        "honkai_advantage": "Honkai Logistics provides comprehensive, low-deductible cargo insurance policies underwritten by world-class marine insurance institutions. We safeguard your full invoice value from the moment goods leave the factory floor until safe final delivery.",
        "action_recommendation": "Do not risk your company's valuable inventory. Ask Honkai Logistics to add door-to-door all-risk cargo insurance to your next freight booking at very affordable premium rates.",
        "tags": ["#HonkaiLogistics", "#CargoInsurance", "#RiskManagement", "#AssetProtection", "#MarineInsurance", "#SafeLogistics"],
        "photo_category": "rate_index",
        "source": "Honkai Risk Management Division & Marine Underwriting Partners"
    }
]

class LogisticsResearchEngine:
    """
    Advanced intelligence and deep research engine for Cambodian Logistics & Supply Chain.
    Produces high-impact, English-only market intelligence posts tailored to promote Honkai Logistics.
    Guarantees rotation so that every post has unique content and a unique picture.
    """

    def __init__(self):
        self.gemini_client = None
        if GEMINI_API_KEY:
            try:
                from google import genai
                self.gemini_client = genai.Client(api_key=GEMINI_API_KEY)
                logger.info("Google Gemini GenAI Client initialized successfully.")
            except Exception as e:
                logger.warning(f"Could not initialize Google GenAI Client: {e}")

    async def get_latest_market_briefing(self, category_filter: Optional[str] = None) -> Dict[str, Any]:
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
        recent_titles_list = get_recently_posted_titles(limit=25)
        recent_titles_set = set(recent_titles_list)
        unposted = [c for c in candidates if c["title_en"] not in recent_titles_set]

        if unposted:
            item = random.choice(unposted)
        else:
            # If all candidates in current pool have been posted, select the least recently posted one (longest time ago)
            def score(cand):
                try:
                    return recent_titles_list.index(cand["title_en"])
                except ValueError:
                    return 999
            candidates_sorted = sorted(candidates, key=score, reverse=True)
            item = candidates_sorted[0]

        # Get recently used photo URLs to guarantee a different picture every time
        recent_photos = get_recently_used_photos(limit=25)
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
            "title_en": item["title_en"],
            "service_highlight": item.get("service_highlight", "Honkai Logistics Dedicated Services"),
            "summary_en": item["summary_en"],
            "key_data": item["key_data"],
            "market_intelligence": item.get("market_intelligence", ""),
            "honkai_advantage": item.get("honkai_advantage", ""),
            "action_recommendation": item["action_recommendation"],
            "tags": item.get("tags", ["#HonkaiLogistics", "#CambodiaLogistics"]),
            "photo_url": photo_info["url"],
            "photo_title": photo_info["title"],
            "photo_location": photo_info["location"],
            "photo_credit": photo_info["credit"],
            "source": item.get("source", "Honkai Logistics Intelligence Desk"),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M ICT")
        }

    async def deep_research_topic(self, user_query: str) -> Dict[str, Any]:
        """
        Performs in-depth research on any specific logistics topic in English,
        promoting Honkai Logistics services.
        """
        logger.info(f"Conducting deep logistics research on: {user_query}")
        
        # If Gemini API is available, generate dynamic real-time intelligence in English
        if self.gemini_client:
            prompt = f"""
You are the Chief Logistics Analyst & Marketing Strategist for Honkai Logistics (Cambodia) Co., Ltd.
The user requested deep research on the following topic:
"{user_query}"

Generate a professional, compelling, 100% English logistics intelligence briefing tailored to promote Honkai Logistics' services to manufacturing factory owners, freight forwarders, and corporate shippers. Remind existing clients and attract new clients by demonstrating Honkai's reliability, equipment capacity, customs expertise, on-time delivery record, and competitive pricing.

Return your analysis as a valid JSON object with the following fields:
{{
  "category": "One of: Ocean Freight & Port Operations, Cross-Border Trucking, Air Cargo Express, Customs Brokerage & Compliance, Factory & SEZ Logistics, Inland Waterways",
  "title_en": "Engaging, professional headline in English highlighting market insight and Honkai service",
  "service_highlight": "Specific Honkai Logistics service capability related to this topic",
  "summary_en": "Executive summary in English (2-3 sentences)",
  "key_data": ["Bullet point 1 with rates or operational transit times", "Bullet point 2 with equipment or schedule data", "Bullet point 3 with efficiency metric"],
  "market_intelligence": "Detailed market context and operational reality in Cambodia (English)",
  "honkai_advantage": "Why clients trust Honkai Logistics for this specific route or service (English)",
  "action_recommendation": "Clear, actionable recommendation for shippers with a direct call to action to book with Honkai Logistics (English)",
  "tags": ["#HonkaiLogistics", "#CambodiaLogistics", "#RelevantTag1", "#RelevantTag2"],
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

                recent_photos = get_recently_used_photos(limit=25)
                photo_category = data.get("photo_category", "ocean_port")
                photo_info = get_action_photo_for_topic(photo_category, user_query, exclude_urls=recent_photos)

                hash_str = f"{data['title_en']}_{datetime.now().strftime('%Y-%m-%d_%H%M')}"
                hash_key = hashlib.md5(hash_str.encode()).hexdigest()

                return {
                    "hash_key": hash_key,
                    "category": data.get("category", "Logistics Market Intelligence"),
                    "title_en": data["title_en"],
                    "service_highlight": data.get("service_highlight", "Honkai Logistics Dedicated Services"),
                    "summary_en": data["summary_en"],
                    "key_data": data.get("key_data", []),
                    "market_intelligence": data.get("market_intelligence", ""),
                    "honkai_advantage": data.get("honkai_advantage", ""),
                    "action_recommendation": data.get("action_recommendation", ""),
                    "tags": data.get("tags", ["#HonkaiLogistics", "#CambodiaLogistics"]),
                    "photo_url": photo_info["url"],
                    "photo_title": photo_info["title"],
                    "photo_location": photo_info["location"],
                    "photo_credit": photo_info["credit"],
                    "source": "Honkai AI Research & Global Logistics Intelligence",
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

        recent_photos = get_recently_used_photos(limit=25)
        photo_info = get_action_photo_for_topic(matched_feed.get("photo_category", "ocean_port"), user_query, exclude_urls=recent_photos)
        hash_str = f"{user_query}_{datetime.now().strftime('%Y-%m-%d_%H%M')}"
        hash_key = hashlib.md5(hash_str.encode()).hexdigest()

        return {
            "hash_key": hash_key,
            "category": f"{matched_feed['category']}",
            "title_en": f"Logistics Advisory: {user_query.capitalize()} — Honkai Operational Analysis",
            "service_highlight": matched_feed.get("service_highlight", "Honkai Logistics Services"),
            "summary_en": f"Special analysis for '{user_query}': {matched_feed['summary_en']}",
            "key_data": matched_feed["key_data"],
            "market_intelligence": matched_feed.get("market_intelligence", ""),
            "honkai_advantage": matched_feed.get("honkai_advantage", ""),
            "action_recommendation": matched_feed["action_recommendation"],
            "tags": matched_feed.get("tags", []) + ["#CustomAdvisory", "#HonkaiReliability"],
            "photo_url": photo_info["url"],
            "photo_title": photo_info["title"],
            "photo_location": photo_info["location"],
            "photo_credit": photo_info["credit"],
            "source": "Honkai Logistics Intelligence Desk",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M ICT")
        }
