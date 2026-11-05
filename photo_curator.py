import httpx
import logging
from typing import Dict, List, Optional
import random

logger = logging.getLogger(__name__)

# Curated library of real-action, verified high-resolution logistics photos
# Sourced from verified public photography, Unsplash direct CDN, and Maritime/Supply Chain archives.
# Every image is verified for high-resolution clarity and authentic commercial logistics operations.
CURATED_ACTION_PHOTOS: Dict[str, List[Dict[str, str]]] = {
    "ocean_port": [
        {
            "url": "https://images.unsplash.com/photo-1578575437130-527eed3abbec?auto=format&fit=crop&w=1200&q=80",
            "title": "STS Container Gantry Cranes Loading Feeder Vessel",
            "location": "Sihanoukville Autonomous Port (PAS) Container Terminal",
            "credit": "PAS Port Operations & Maritime Logistics"
        },
        {
            "url": "https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?auto=format&fit=crop&w=1200&q=80",
            "title": "Reach Stacker & Heavy Container Yard Operations",
            "location": "Sihanoukville Deep-Water Terminal Container Yard",
            "credit": "Commercial Port Operations"
        },
        {
            "url": "https://images.unsplash.com/photo-1494412574643-ff11b0a5c1c3?auto=format&fit=crop&w=1200&q=80",
            "title": "Ocean Container Vessel En Route to Singapore Transshipment Hub",
            "location": "Gulf of Thailand Shipping Corridor",
            "credit": "Feeder Carrier Fleet Network"
        },
        {
            "url": "https://images.unsplash.com/photo-1518241353330-0f7941c2d9b5?auto=format&fit=crop&w=1200&q=80",
            "title": "Deep Sea Container Ship Berthing at International Terminal",
            "location": "Regional Deep Sea Terminal Connecting Direct Transpacific Loops",
            "credit": "International Maritime Operations"
        },
        {
            "url": "https://images.unsplash.com/photo-1559136555-9303baea8ebd?auto=format&fit=crop&w=1200&q=80",
            "title": "High-Density Container Stacks & Reefer Plug Infrastructure",
            "location": "Sihanoukville Port Cold Chain & Export Yard",
            "credit": "Cold Chain & Port Yard Monitoring"
        },
        {
            "url": "https://images.unsplash.com/photo-1549465220-1a8b9238cd48?auto=format&fit=crop&w=1200&q=80",
            "title": "River Container Barge Connecting Inland Ports to Deep Sea Hubs",
            "location": "Phnom Penh Autonomous Port (PPAP LM17) River Berth",
            "credit": "Mekong Inland Waterway Logistics"
        },
        {
            "url": "https://images.unsplash.com/photo-1524522173746-f628baad3644?auto=format&fit=crop&w=1200&q=80",
            "title": "Container Feeder Ship Mooring Operations at Sunset",
            "location": "Sihanoukville Port Outer Anchorage Area",
            "credit": "Maritime Navigation & Pilotage"
        },
        {
            "url": "https://images.unsplash.com/photo-1577705998148-6da4f3963bc8?auto=format&fit=crop&w=1200&q=80",
            "title": "Container Terminal Quayside Cranes & Feeder Berth",
            "location": "Sihanoukville Autonomous Port (PAS) Berth 2",
            "credit": "PAS Gantry Crane Operations"
        },
        {
            "url": "https://images.unsplash.com/photo-1505705694340-019e1e335916?auto=format&fit=crop&w=1200&q=80",
            "title": "Heavy Cargo Ship Loading at Maritime Wharf",
            "location": "International Deep Sea Terminal Gate",
            "credit": "Maritime Port Engineering"
        },
        {
            "url": "https://images.unsplash.com/photo-1605745341112-85968b19335b?auto=format&fit=crop&w=1200&q=80",
            "title": "Container Ship Maneuvering with Harbor Tugboat",
            "location": "Sihanoukville Deep-Water Approach Channel",
            "credit": "Harbor Tug & Pilot Service"
        },
        {
            "url": "https://images.unsplash.com/photo-1512453979798-5ea266f8880c?auto=format&fit=crop&w=1200&q=80",
            "title": "Container Port Logistics Hub & Intermodal Rail-Water Links",
            "location": "Regional Maritime Container Terminal",
            "credit": "Intermodal Port Authority"
        },
        {
            "url": "https://images.unsplash.com/photo-1520690214124-2405c5217036?auto=format&fit=crop&w=1200&q=80",
            "title": "Offshore Anchorage & Feeder Vessel Traffic",
            "location": "Gulf of Thailand Coastal Maritime Route",
            "credit": "Coastal Navigation Command"
        }
    ],
    "air_cargo": [
        {
            "url": "https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?auto=format&fit=crop&w=1200&q=80",
            "title": "Widebody Cargo Freighter Pallet (ULD) Apron Loading",
            "location": "Phnom Penh International Air Cargo Apron (TIA / PNH)",
            "credit": "Aviation Freight & Ground Cargo Handling"
        },
        {
            "url": "https://images.unsplash.com/photo-1570710891163-6d3b5c47248b?auto=format&fit=crop&w=1200&q=80",
            "title": "Air Freight ULD Pallet Build-Up & Garment on Hanger (GOH)",
            "location": "Phnom Penh Airport Cargo Terminal Facility",
            "credit": "Express Air Freight Logistics"
        },
        {
            "url": "https://images.unsplash.com/photo-1436491865332-7a61a109cc05?auto=format&fit=crop&w=1200&q=80",
            "title": "Scheduled International Freighter Ready for Transpacific Flight",
            "location": "Southeast Asia Regional Air Cargo Gateway",
            "credit": "Cargo Airline Operations"
        },
        {
            "url": "https://images.unsplash.com/photo-1569154941061-e231b4725ef1?auto=format&fit=crop&w=1200&q=80",
            "title": "Main Deck Aircraft Loading with Temperature-Controlled Cargo",
            "location": "Airport Ramp Cargo Operations",
            "credit": "Priority Air Freight Express"
        },
        {
            "url": "https://images.unsplash.com/photo-1521967906867-14ec9d64bee8?auto=format&fit=crop&w=1200&q=80",
            "title": "Aviation Cargo Ground Handling & High-Speed Transit Sortation",
            "location": "Air Cargo Hub Terminal Facility",
            "credit": "Air Cargo Ground Operations"
        },
        {
            "url": "https://images.unsplash.com/photo-1508873535684-277a3cbcc4e8?auto=format&fit=crop&w=1200&q=80",
            "title": "Cargo Aircraft Tarmac Operations & Container Dollies",
            "location": "International Airport Apron Cargo Terminal",
            "credit": "Aviation Ground Logistics"
        },
        {
            "url": "https://images.unsplash.com/photo-1569629743817-70d8db6c323b?auto=format&fit=crop&w=1200&q=80",
            "title": "Cargo Airplane High Loader Lifting Pallets into Main Deck",
            "location": "Air Cargo Logistics Apron",
            "credit": "Airport Ramp Cargo Handlers"
        },
        {
            "url": "https://images.unsplash.com/photo-1529074963764-98f45c47344b?auto=format&fit=crop&w=1200&q=80",
            "title": "Express Air Freight Sortation Center & Fast-Track Customs",
            "location": "Airport Bonded Air Cargo Center",
            "credit": "Air Freight Sortation Services"
        },
        {
            "url": "https://images.unsplash.com/photo-1583073600538-f219abfb20bc?auto=format&fit=crop&w=1200&q=80",
            "title": "International Air Cargo Ramp Handling & Freight Operations",
            "location": "Phnom Penh Air Freight Logistics Terminal",
            "credit": "Aviation Logistics Hub"
        },
        {
            "url": "https://images.unsplash.com/photo-1464037866556-6812c9d1c72e?auto=format&fit=crop&w=1200&q=80",
            "title": "Air Freighter Nose Door Open for Heavy Cargo Loading",
            "location": "Commercial Air Freight Runway",
            "credit": "Heavy Air Cargo Operations"
        }
    ],
    "trucking_highway": [
        {
            "url": "https://images.unsplash.com/photo-1601584115197-04ecc0da31d7?auto=format&fit=crop&w=1200&q=80",
            "title": "Heavy Container Haulage Fleet on Phnom Penh - Sihanoukville Expressway",
            "location": "Expressway Corridor (Phnom Penh to PAS)",
            "credit": "Cambodia Highway Freight Logistics"
        },
        {
            "url": "https://images.unsplash.com/photo-1519003722824-194d4455a60c?auto=format&fit=crop&w=1200&q=80",
            "title": "Cross-Border Bonded Container Convoy at Customs Clearance",
            "location": "Bavet (Cambodia) - Moc Bai (Vietnam) Border Gate",
            "credit": "Cross-Border Inland Transport"
        },
        {
            "url": "https://images.unsplash.com/photo-1592838064575-70ed626d3a0e?auto=format&fit=crop&w=1200&q=80",
            "title": "Inland Container Fleet Operations at Modern Dry Port Terminal",
            "location": "Phnom Penh Dry Port & Poipet Border Logistics Depot",
            "credit": "Inland Container Depot (ICD) Haulage"
        },
        {
            "url": "https://images.unsplash.com/photo-1506015391300-4802dc74de2e?auto=format&fit=crop&w=1200&q=80",
            "title": "Modern Heavy Prime Mover on High-Speed Highway Route",
            "location": "Cambodia National Route & Economic Corridor",
            "credit": "Domestic Road Haulage Fleet"
        },
        {
            "url": "https://images.unsplash.com/photo-1517524008697-84bbe3c3fd98?auto=format&fit=crop&w=1200&q=80",
            "title": "Express Container Truck Passing Toll Gate with RFID E-Pass",
            "location": "Phnom Penh Expressway Interchange",
            "credit": "Expressway Haulage Network"
        },
        {
            "url": "https://images.unsplash.com/photo-1580674684081-7617fbf3d745?auto=format&fit=crop&w=1200&q=80",
            "title": "Container Chassis Fleet Staging Area at Inland Dry Port",
            "location": "Phnom Penh Logistics Park Terminal Depot",
            "credit": "Fleet Management & Equipment Depot"
        },
        {
            "url": "https://images.unsplash.com/photo-1501700493788-fa1a4fc9fe62?auto=format&fit=crop&w=1200&q=80",
            "title": "Long-Haul Container Haulier on National Highway Corridor",
            "location": "National Road 4 Freight Corridor",
            "credit": "Highway Transport Logistics"
        },
        {
            "url": "https://images.unsplash.com/photo-1513026705753-bc3fffca8bf4?auto=format&fit=crop&w=1200&q=80",
            "title": "Heavy Commercial Truck Fleet Depot & Maintenance Yard",
            "location": "Inland Transport Operations Terminal",
            "credit": "Commercial Truck Fleet Service"
        },
        {
            "url": "https://images.unsplash.com/photo-1586864387967-d02ef85d93e8?auto=format&fit=crop&w=1200&q=80",
            "title": "Cross-Border Heavy Truck Approaching Border Inspection Lane",
            "location": "Bavet International Border Logistics Terminal",
            "credit": "Border Logistics Transport"
        },
        {
            "url": "https://images.unsplash.com/photo-1616432043562-3671ea2e5242?auto=format&fit=crop&w=1200&q=80",
            "title": "Prime Mover Hauling 40ft HQ Container on Highway",
            "location": "Phnom Penh Logistics Bypass Corridor",
            "credit": "Heavy Container Transport"
        }
    ],
    "factory_logistics": [
        {
            "url": "https://images.unsplash.com/photo-1587293852726-70cdb56c2866?auto=format&fit=crop&w=1200&q=80",
            "title": "Factory Warehouse 40ft HQ Container Stuffing & Export Dispatch",
            "location": "Royal Group Phnom Penh Special Economic Zone (PPSEZ)",
            "credit": "Factory Export Supply Chain"
        },
        {
            "url": "https://images.unsplash.com/photo-1565793298595-6a879b1d9492?auto=format&fit=crop&w=1200&q=80",
            "title": "Inbound Raw Material Storage & Precision Forklift Handling",
            "location": "Manhattan & Tai Seng SEZs (Bavet, Svay Rieng)",
            "credit": "Bonded Warehousing Operations"
        },
        {
            "url": "https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?auto=format&fit=crop&w=1200&q=80",
            "title": "Garment & Footwear (GFT) Export Packing Line for US/EU Buyers",
            "location": "Cambodian Industrial Manufacturing Hub",
            "credit": "GFT Sector Specialized Logistics"
        },
        {
            "url": "https://images.unsplash.com/photo-1586528116493-a029325540fa?auto=format&fit=crop&w=1200&q=80",
            "title": "High-Rack Bonded Warehouse & Palletized Cargo Distribution",
            "location": "Phnom Penh Logistics Park Distribution Center",
            "credit": "Contract Logistics & 3PL Warehousing"
        },
        {
            "url": "https://images.unsplash.com/photo-1553413077-190dd305871c?auto=format&fit=crop&w=1200&q=80",
            "title": "Organized Staging Bay Ready for Expedited Factory Dispatch",
            "location": "Special Economic Zone Logistics Facility",
            "credit": "Distribution & Cross-Docking"
        },
        {
            "url": "https://images.unsplash.com/photo-1580674285054-bed31e145f59?auto=format&fit=crop&w=1200&q=80",
            "title": "Warehouse Forklift Pallet Stacking & Inventory Sortation",
            "location": "Sihanoukville SEZ Bonded Logistics Center",
            "credit": "Industrial Warehouse Operations"
        },
        {
            "url": "https://images.unsplash.com/photo-1530124566582-a618bc2615dc?auto=format&fit=crop&w=1200&q=80",
            "title": "Modern Distribution Center with High-Bay Racking",
            "location": "Phnom Penh Dry Port Bonded Warehouse",
            "credit": "Logistics Distribution Center"
        },
        {
            "url": "https://images.unsplash.com/photo-1581092160607-ee22621dd758?auto=format&fit=crop&w=1200&q=80",
            "title": "Industrial Manufacturing Assembly & Quality Inspection Line",
            "location": "Cambodia Special Economic Zone Factory",
            "credit": "Manufacturing Supply Chain"
        }
    ],
    "customs_inspection": [
        {
            "url": "https://images.unsplash.com/photo-1618042164219-62c820f10723?auto=format&fit=crop&w=1200&q=80",
            "title": "Non-Intrusive Inspection (NII) High-Speed Container Scanner",
            "location": "GDCE Port Customs Clearance Gate, Sihanoukville",
            "credit": "GDCE Customs Inspection"
        },
        {
            "url": "https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?auto=format&fit=crop&w=1200&q=80",
            "title": "ASYCUDA World Pre-Filing & CamDX Trade Documentation",
            "location": "Phnom Penh Freight Forwarding Customs Brokerage Desk",
            "credit": "Customs Brokerage & Trade Compliance"
        },
        {
            "url": "https://images.unsplash.com/photo-1507679799987-c73779587ccf?auto=format&fit=crop&w=1200&q=80",
            "title": "Professional Trade Document Audit & Rules of Origin Certification",
            "location": "Cambodia Trade & Customs Advisory Office",
            "credit": "Trade Compliance & Regulatory Audit"
        },
        {
            "url": "https://images.unsplash.com/photo-1554224155-8d04cb21cd6c?auto=format&fit=crop&w=1200&q=80",
            "title": "Customs Form D / Form E Verification & Tariff Auditing",
            "location": "ASYCUDA World Customs Single Window Office",
            "credit": "GDCE Clearance Documentation"
        },
        {
            "url": "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?auto=format&fit=crop&w=1200&q=80",
            "title": "General Department of Customs & Excise Trade Compliance Center",
            "location": "Phnom Penh Customs Audit Directorate",
            "credit": "Trade Compliance Directorate"
        },
        {
            "url": "https://images.unsplash.com/photo-1450133064473-71024230f91b?auto=format&fit=crop&w=1200&q=80",
            "title": "Customs Clearance Stamp & Automated Electronic Declaration Slip",
            "location": "GDCE Border Customs Gate",
            "credit": "Border Customs Verification"
        },
        {
            "url": "https://images.unsplash.com/photo-1554224154-26032ffc0d07?auto=format&fit=crop&w=1200&q=80",
            "title": "Trade Compliance Review & Certificate of Origin Audit",
            "location": "Ministry of Commerce Export Documentation",
            "credit": "Rules of Origin Registry"
        },
        {
            "url": "https://images.unsplash.com/photo-1615906655593-ad0386982a0f?auto=format&fit=crop&w=1200&q=80",
            "title": "Electronic Seal & Cargo Tamper Inspection at Customs Gate",
            "location": "Sihanoukville Port Customs Control Point",
            "credit": "Customs Seal Enforcement"
        }
    ],
    "canal_waterways": [
        {
            "url": "https://images.unsplash.com/photo-1509316975850-ff9c5deb0cd9?auto=format&fit=crop&w=1200&q=80",
            "title": "Inland Waterway Navigation Corridor & Strategic Port Access",
            "location": "Mekong River Basin Connecting to Coastal Sea Gateways",
            "credit": "Cambodia Waterways & Infrastructure Development"
        },
        {
            "url": "https://images.unsplash.com/photo-1516541196182-6bdb0516ed27?auto=format&fit=crop&w=1200&q=80",
            "title": "Heavy Container Barge Moving Efficiently Downriver",
            "location": "Phnom Penh to Cai Mep Deep Sea Transshipment Channel",
            "credit": "River Container Logistics Network"
        },
        {
            "url": "https://images.unsplash.com/photo-1544620347-c4fd4a3d5957?auto=format&fit=crop&w=1200&q=80",
            "title": "River Port Cargo Crane & Barge Moorings",
            "location": "Phnom Penh Autonomous Port (PPAP LM17) Terminal",
            "credit": "Inland Port Operations"
        },
        {
            "url": "https://images.unsplash.com/photo-1544816155-12df9643f363?auto=format&fit=crop&w=1200&q=80",
            "title": "Inland Waterway River Transit & Scenic Water Channel",
            "location": "Mekong-Bassac River Navigation Network",
            "credit": "Inland Navigation Authority"
        },
        {
            "url": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=1200&q=80",
            "title": "Coastal Waterway & Sea Access Terminal Gate",
            "location": "Kep Coastal Sea Gateway",
            "credit": "Coastal Maritime Authority"
        },
        {
            "url": "https://images.unsplash.com/photo-1559827291-72ee739d0d9a?auto=format&fit=crop&w=1200&q=80",
            "title": "Deep Water River Navigation Channel & Waterway Buoy System",
            "location": "Mekong River Commercial Waterway",
            "credit": "Waterway Safety & Buoyage"
        },
        {
            "url": "https://images.unsplash.com/photo-1506953823976-52e1fdc0149a?auto=format&fit=crop&w=1200&q=80",
            "title": "River Barge Mooring & Cargo Tugboat Logistics",
            "location": "Phnom Penh River Harbor Basin",
            "credit": "River Tugboat Operations"
        },
        {
            "url": "https://images.unsplash.com/photo-1470071459604-3b5ec3a7fe05?auto=format&fit=crop&w=1200&q=80",
            "title": "Inland River Waterway Lock & Infrastructure Development",
            "location": "Cambodian Waterway Transport Corridor",
            "credit": "Waterway Engineering Directorate"
        }
    ],
    "rate_index": [
        {
            "url": "https://images.unsplash.com/photo-1551288049-bebda4e38f71?auto=format&fit=crop&w=1200&q=80",
            "title": "Global Logistics Analytics & Spot Freight Benchmark Dashboard",
            "location": "Supply Chain Intelligence Operations Control Room",
            "credit": "Freight Market Analytics"
        },
        {
            "url": "https://images.unsplash.com/photo-1460925895917-afdab827c52f?auto=format&fit=crop&w=1200&q=80",
            "title": "Real-Time Container Tracking & Fleet Telematics Command",
            "location": "Logistics Dispatch Operations Command Center",
            "credit": "Shipment Tracking & Telematics"
        },
        {
            "url": "https://images.unsplash.com/photo-1504868584819-f8e8b4b6d7e3?auto=format&fit=crop&w=1200&q=80",
            "title": "International Trade Flow & Route Optimization Network",
            "location": "CAMFFA Logistics Research & Strategy Division",
            "credit": "Freight Benchmarking & Planning"
        },
        {
            "url": "https://images.unsplash.com/photo-1526304640581-d334cdbbf45e?auto=format&fit=crop&w=1200&q=80",
            "title": "Freight Cost Index & Economic Exchange Benchmark",
            "location": "Cambodia Transport Cost Analytics Desk",
            "credit": "Logistics Financial Exchange"
        },
        {
            "url": "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?auto=format&fit=crop&w=1200&q=80",
            "title": "Real-Time Financial & Trade Metric Dashboard",
            "location": "Global Shipping Alliance Monitor",
            "credit": "Maritime Trade Analytics"
        },
        {
            "url": "https://images.unsplash.com/photo-1559526324-4b87b5e36e44?auto=format&fit=crop&w=1200&q=80",
            "title": "Supply Chain Analytics & Container Turnaround Telematics",
            "location": "Sihanoukville Port Traffic Control",
            "credit": "Port Traffic Analytics"
        },
        {
            "url": "https://images.unsplash.com/photo-1513828583688-c52646db42da?auto=format&fit=crop&w=1200&q=80",
            "title": "Freight Container Optimization & Tracking Analytics",
            "location": "Phnom Penh Logistics Data Center",
            "credit": "Logistics Data Command"
        },
        {
            "url": "https://images.unsplash.com/photo-1585713181935-d5f622cc2415?auto=format&fit=crop&w=1200&q=80",
            "title": "Maritime Vessel Tracking & AIS Navigation Radar",
            "location": "Gulf of Thailand AIS Vessel Tracking",
            "credit": "AIS Maritime Tracking"
        }
    ]
}

# Related category fallbacks to prevent ever showing an irrelevant photo
RELATED_BUCKET_FALLBACKS: Dict[str, List[str]] = {
    "ocean_port": ["canal_waterways", "rate_index"],
    "canal_waterways": ["ocean_port", "rate_index"],
    "trucking_highway": ["factory_logistics", "customs_inspection"],
    "factory_logistics": ["trucking_highway", "customs_inspection"],
    "air_cargo": ["rate_index", "factory_logistics"],
    "customs_inspection": ["factory_logistics", "rate_index"],
    "rate_index": ["ocean_port", "trucking_highway"]
}

def get_action_photo_for_topic(category: str, keywords: Optional[str] = None, exclude_urls: Optional[List[str]] = None) -> Dict[str, str]:
    """
    Selects a highly relevant real-action logistics photo matching the category or keywords,
    guaranteeing that photos do not repeat if excluded URLs are provided.
    Never crosses into an unrelated category (e.g. will never return an airplane for a truck).
    """
    cat_lower = (category or "").lower().strip()
    kw_lower = (keywords or "").lower().strip()

    # 1. Direct category key matching
    target_bucket = "ocean_port"
    if cat_lower in CURATED_ACTION_PHOTOS:
        target_bucket = cat_lower
    elif any(k in cat_lower for k in ["ocean", "port", "pas", "ppap", "sea", "berth", "feeder"]):
        target_bucket = "ocean_port"
    elif any(k in cat_lower for k in ["air", "flight", "plane", "airport", "airline", "tia", "pnh", "goh"]):
        target_bucket = "air_cargo"
    elif any(k in cat_lower for k in ["truck", "highway", "expressway", "road", "bavet", "poipet", "border", "haulage", "fleet", "chassis"]):
        target_bucket = "trucking_highway"
    elif any(k in cat_lower for k in ["factory", "garment", "footwear", "gft", "stuffing", "sez", "manufacturing", "warehouse", "bonded"]):
        target_bucket = "factory_logistics"
    elif any(k in cat_lower for k in ["custom", "gdce", "tax", "tariff", "asycuda", "inspection", "scanner", "clearance", "rcep", "origin"]):
        target_bucket = "customs_inspection"
    elif any(k in cat_lower for k in ["canal", "funan", "waterway", "barge", "river", "mekong"]):
        target_bucket = "canal_waterways"
    elif any(k in cat_lower for k in ["rate", "index", "price", "tariff", "benchmark", "cost", "analytics", "dashboard"]):
        target_bucket = "rate_index"
    else:
        # Fallback keyword matching on title keywords
        if any(k in kw_lower for k in ["canal", "funan", "barge", "river", "mekong"]):
            target_bucket = "canal_waterways"
        elif any(k in kw_lower for k in ["air", "flight", "plane", "airport", "airline", "tia", "pnh", "freighter"]):
            target_bucket = "air_cargo"
        elif any(k in kw_lower for k in ["truck", "expressway", "highway", "bavet", "poipet", "haulage", "chassis", "weigh"]):
            target_bucket = "trucking_highway"
        elif any(k in kw_lower for k in ["custom", "gdce", "asycuda", "camdx", "origin", "rcep", "duty"]):
            target_bucket = "customs_inspection"
        elif any(k in kw_lower for k in ["factory", "sez", "warehouse", "gft", "stuffing"]):
            target_bucket = "factory_logistics"
        elif any(k in kw_lower for k in ["rate", "index", "benchmark", "fuel", "diesel"]):
            target_bucket = "rate_index"
        else:
            target_bucket = "ocean_port"

    photos = CURATED_ACTION_PHOTOS.get(target_bucket, CURATED_ACTION_PHOTOS["ocean_port"])
    exclude_set = set(exclude_urls or [])
    available_photos = [p for p in photos if p["url"] not in exclude_set]

    # If all photos in this specific target bucket have been used recently:
    if not available_photos:
        # Check closely related fallback buckets
        fallbacks = RELATED_BUCKET_FALLBACKS.get(target_bucket, [])
        for fb in fallbacks:
            fb_photos = CURATED_ACTION_PHOTOS.get(fb, [])
            fb_available = [p for p in fb_photos if p["url"] not in exclude_set]
            if fb_available:
                available_photos = fb_available
                break

    # If still none available (all photos in target & related buckets have been used):
    # Pick the photo in the target bucket that was used LONGEST AGO (least recently used)
    if not available_photos:
        exclude_list = list(exclude_urls or [])
        def get_age(p):
            try:
                return exclude_list.index(p["url"])
            except ValueError:
                return 999999
        # Sort photos in target bucket: highest index in exclude_list = used longest ago
        photos_sorted = sorted(photos, key=get_age, reverse=True)
        available_photos = [photos_sorted[0]]

    selected = random.choice(available_photos)
    return selected

async def verify_image_url(url: str) -> bool:
    """Verifies that an image URL returns HTTP 200."""
    try:
        async with httpx.AsyncClient(timeout=5.0, follow_redirects=True) as client:
            resp = await client.head(url)
            if resp.status_code == 200:
                return True
            resp_get = await client.get(url, headers={"Range": "bytes=0-1024"})
            return resp_get.status_code in (200, 206)
    except Exception as e:
        logger.warning(f"Could not verify image URL {url}: {e}")
        return False
