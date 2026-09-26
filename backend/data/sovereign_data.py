"""
Sovereign Demographic, Infrastructure Deficit, and Public Investment Datasets
Focus on India (NITI Aayog Aspirational Districts & State Hubs) + BRICS Partner Benchmarks.
"""

from typing import Dict, List, Any

# Calibrated District Profiles: Demographics, Baseline Infrastructure Deficit Indices (0-100 scale, 100=extreme deficit)
DISTRICT_PROFILES: Dict[str, Dict[str, Any]] = {
    # INDIA - Aspirational & Critical Districts
    "IN-DIST-01": {
        "id": "IN-DIST-01",
        "country": "India",
        "country_code": "IN",
        "state": "Maharashtra",
        "district": "Gadchiroli (Vidarbha)",
        "lat": 20.1809,
        "lon": 80.0000,
        "population": 1150000,
        "rural_percentage": 88.5,
        "tribal_percentage": 38.7,
        "poverty_rate": 41.2,
        "literacy_rate": 74.4,
        "aspirational_district": True,
        "primary_language": "Marathi",
        "secondary_languages": ["Hindi", "Gondi"],
        "infrastructure_deficits": {
            "water": 78.4,       # Severe fluoride/iron water contamination, non-functional tap connections
            "power": 64.2,       # 10-14 hr power outages, lack of solar agricultural feeders
            "roads": 82.1,       # Dense forest river crossings washed away in monsoon
            "health": 86.5,      # Sub-district hospitals lack emergency obstetric & neonatal care
            "telecom": 79.0,     # BharatNet optical fiber cable snapped, zero cell signal in 120+ villages
            "sanitation": 61.3   # Incomplete school sanitation blocks
        },
        "ongoing_schemes": [
            {"scheme": "Jal Jeevan Mission", "allocated_cr": 45.0, "spent_cr": 22.1, "status": "Delayed"},
            {"scheme": "PMGSY Roads", "allocated_cr": 68.0, "spent_cr": 54.0, "status": "In-Progress"},
            {"scheme": "Ayushman Arogya Mandir", "allocated_cr": 18.5, "spent_cr": 9.2, "status": "Critical Gap"}
        ]
    },
    "IN-DIST-02": {
        "id": "IN-DIST-02",
        "country": "India",
        "country_code": "IN",
        "state": "Uttar Pradesh",
        "district": "Chitrakoot (Bundelkhand)",
        "lat": 25.1764,
        "lon": 80.8667,
        "population": 991738,
        "rural_percentage": 90.3,
        "tribal_percentage": 26.8,
        "poverty_rate": 48.6,
        "literacy_rate": 65.0,
        "aspirational_district": True,
        "primary_language": "Hindi",
        "secondary_languages": ["Bundeli"],
        "infrastructure_deficits": {
            "water": 92.5,       # Chronic drought, acute groundwater depletion in rocky terrain
            "power": 71.0,       # Unscheduled cuts tripping borewells and community RO plants
            "roads": 65.4,       # Unpaved approach tracks to remote Dalit hamlets
            "health": 74.8,      # Primary Health Centres (PHC) functioning without permanent doctors
            "telecom": 58.2,     # PDS ration shop POS machines offline 4 days a week
            "sanitation": 68.0   # Open defecation free (ODF) sustainability gaps
        },
        "ongoing_schemes": [
            {"scheme": "Bundelkhand Piped Water Pipeline", "allocated_cr": 120.0, "spent_cr": 88.0, "status": "In-Progress"},
            {"scheme": "PM-KUSUM Solar Pumps", "allocated_cr": 32.0, "spent_cr": 14.5, "status": "Under-utilized"}
        ]
    },
    "IN-DIST-03": {
        "id": "IN-DIST-03",
        "country": "India",
        "country_code": "IN",
        "state": "Chhattisgarh",
        "district": "Bastar (Jagdalpur)",
        "lat": 19.0734,
        "lon": 82.0298,
        "population": 1412746,
        "rural_percentage": 86.2,
        "tribal_percentage": 66.4,
        "poverty_rate": 52.3,
        "literacy_rate": 54.4,
        "aspirational_district": True,
        "primary_language": "Hindi",
        "secondary_languages": ["Halbi", "Gondi", "Chhattisgarhi"],
        "infrastructure_deficits": {
            "water": 74.0,       # Natural stream siltation, absence of overhead storage reservoirs
            "power": 79.5,       # Grid disconnected hamlets relying on malfunctioning mini-grids
            "roads": 88.6,       # Naxal-affected terrain, lack of culverts & all-weather bridges
            "health": 89.2,      # High sickle cell & malaria load, ambulance response > 3 hours
            "telecom": 84.1,     # Security-sensitive telecom shadow zones
            "sanitation": 72.4   # High community dependency on open water bodies
        },
        "ongoing_schemes": [
            {"scheme": "Special Central Assistance (SCA)", "allocated_cr": 85.0, "spent_cr": 41.0, "status": "In-Progress"},
            {"scheme": "PMGSY Phase-III", "allocated_cr": 110.0, "spent_cr": 72.0, "status": "Stalled"}
        ]
    },
    "IN-DIST-04": {
        "id": "IN-DIST-04",
        "country": "India",
        "country_code": "IN",
        "state": "Karnataka",
        "district": "Raichur (Kalyana-Karnataka)",
        "lat": 16.2120,
        "lon": 77.3439,
        "population": 1928812,
        "rural_percentage": 74.5,
        "tribal_percentage": 19.0,
        "poverty_rate": 39.8,
        "literacy_rate": 59.5,
        "aspirational_district": True,
        "primary_language": "Kannada",
        "secondary_languages": ["Telugu", "Urdu", "Hindi"],
        "infrastructure_deficits": {
            "water": 81.2,       # High arsenic & fluoride levels in Tungabhadra basin
            "power": 55.0,       # Thermal power plant neighbor but local farmers get erratic supply
            "roads": 58.7,       # Pothole-ridden farm-to-mandi links
            "health": 78.4,      # Severe child stunting & acute malnutrition (SAM) center deficit
            "telecom": 46.8,     # Moderate telecom in towns, patchy 4G in interior hoblis
            "sanitation": 63.5   # Inadequate drainage causing vector-borne outbreaks
        },
        "ongoing_schemes": [
            {"scheme": "JJM Rural Piped Water", "allocated_cr": 64.0, "spent_cr": 38.0, "status": "In-Progress"},
            {"scheme": "Kalyana Karnataka Development Board (KKRDB)", "allocated_cr": 95.0, "spent_cr": 60.5, "status": "In-Progress"}
        ]
    },
    "IN-DIST-05": {
        "id": "IN-DIST-05",
        "country": "India",
        "country_code": "IN",
        "state": "Haryana",
        "district": "Nuh (Mewat)",
        "lat": 28.1186,
        "lon": 77.0016,
        "population": 1089263,
        "rural_percentage": 88.6,
        "tribal_percentage": 0.5,
        "poverty_rate": 36.4,
        "literacy_rate": 54.1,
        "aspirational_district": True,
        "primary_language": "Hindi",
        "secondary_languages": ["Mewati", "Urdu"],
        "infrastructure_deficits": {
            "water": 89.0,       # Highly saline underground water, tankers cartel
            "power": 62.8,       # 11kV line fault rates 3x state average
            "roads": 52.0,       # Heavy transit truck damage on local feeder roads
            "health": 81.6,      # Infant Mortality Rate (IMR) double state average, no female gynecologist at CHC
            "telecom": 41.2,     # High mobile phone density but poor broadband for schools
            "sanitation": 75.3   # Lack of functional toilets in girls' primary schools leading to dropouts
        },
        "ongoing_schemes": [
            {"scheme": "Mewat Canal Water Feeder", "allocated_cr": 55.0, "spent_cr": 26.0, "status": "Behind Schedule"},
            {"scheme": "Beti Bachao Beti Padhao Infra Fund", "allocated_cr": 12.0, "spent_cr": 8.1, "status": "In-Progress"}
        ]
    },
    "IN-DIST-06": {
        "id": "IN-DIST-06",
        "country": "India",
        "country_code": "IN",
        "state": "Tamil Nadu",
        "district": "Ramanathapuram",
        "lat": 9.3639,
        "lon": 78.8395,
        "population": 1353445,
        "rural_percentage": 69.7,
        "tribal_percentage": 1.2,
        "poverty_rate": 28.5,
        "literacy_rate": 80.7,
        "aspirational_district": True,
        "primary_language": "Tamil",
        "secondary_languages": ["English"],
        "infrastructure_deficits": {
            "water": 84.6,       # Coastal salinity intrusion, extreme summer water crisis
            "power": 42.1,       # Solar potential high but lack of coastal evacuation feeders
            "roads": 46.3,       # Coastal fishing hamlets cut off during cyclonic tidal surges
            "health": 59.8,      # Dialysis and cancer diagnostic facilities 80 km away in Madurai
            "telecom": 38.5,     # Fishermen safety distress signaling beacon blind spots
            "sanitation": 48.0   # Coastal wastewater seepage into shallow aquifers
        },
        "ongoing_schemes": [
            {"scheme": "Desalination Plant Network", "allocated_cr": 78.0, "spent_cr": 45.0, "status": "In-Progress"},
            {"scheme": "Matsya Sampada Coastal Infra", "allocated_cr": 35.0, "spent_cr": 21.0, "status": "In-Progress"}
        ]
    },
    "IN-DIST-07": {
        "id": "IN-DIST-07",
        "country": "India",
        "country_code": "IN",
        "state": "Bihar",
        "district": "Katihar",
        "lat": 25.5411,
        "lon": 87.5689,
        "population": 3071029,
        "rural_percentage": 91.1,
        "tribal_percentage": 5.9,
        "poverty_rate": 53.8,
        "literacy_rate": 52.2,
        "aspirational_district": True,
        "primary_language": "Hindi",
        "secondary_languages": ["Maithili", "Surjapuri", "Urdu", "Bhojpuri"],
        "infrastructure_deficits": {
            "water": 76.5,       # Arsenic and flood siltation, submergence of tube-wells
            "power": 67.2,       # Flood inundation of sub-stations for 3 months annually
            "roads": 85.0,       # Kosi and Mahananda flood erosion severing road embankments
            "health": 83.1,      # Flood rescue boats and mobile fever clinic deficit
            "telecom": 63.4,     # Cell towers lose battery backup during monsoon floods
            "sanitation": 78.9   # Toilets submerged in annual inundations
        },
        "ongoing_schemes": [
            {"scheme": "Kosi River Basin Embankment & Paved Roads", "allocated_cr": 140.0, "spent_cr": 82.0, "status": "Stalled"},
            {"scheme": "Mukhya Mantri Gram Sampark Yojana", "allocated_cr": 58.0, "spent_cr": 39.0, "status": "In-Progress"}
        ]
    },

    # BRICS BENCHMARK: BRAZIL
    "BR-DIST-01": {
        "id": "BR-DIST-01",
        "country": "Brazil",
        "country_code": "BR",
        "state": "Bahia",
        "district": "Juazeiro / Sertão",
        "lat": -9.4167,
        "lon": -40.5000,
        "population": 218162,
        "rural_percentage": 42.1,
        "tribal_percentage": 8.4,
        "poverty_rate": 44.5,
        "literacy_rate": 78.2,
        "aspirational_district": True,
        "primary_language": "Portuguese",
        "secondary_languages": [],
        "infrastructure_deficits": {
            "water": 88.2,       # Semi-arid drought, Cisternas program capacity deficit
            "power": 48.0,       # Wind corridor exists but micro-distribution to quilombolas erratic
            "roads": 69.5,       # Unpaved unpaved dirt roads (estradas vicinais) cutting agricultural transport
            "health": 72.0,      # Specialized care concentrated 500 km away in Salvador
            "telecom": 57.3,     # 4G coverage gaps in quilombola communities
            "sanitation": 71.0   # Open sewage ditches in peripheral bairros
        },
        "ongoing_schemes": [
            {"scheme": "Novo PAC - Água para Todos", "allocated_cr": 60.0, "spent_cr": 28.0, "status": "In-Progress"}
        ]
    },

    # BRICS BENCHMARK: SOUTH AFRICA
    "ZA-DIST-01": {
        "id": "ZA-DIST-01",
        "country": "South Africa",
        "country_code": "ZA",
        "state": "Eastern Cape",
        "district": "OR Tambo District",
        "lat": -31.5833,
        "lon": 28.7833,
        "population": 1475000,
        "rural_percentage": 81.3,
        "tribal_percentage": 94.0,
        "poverty_rate": 58.2,
        "literacy_rate": 69.1,
        "aspirational_district": True,
        "primary_language": "isiXhosa",
        "secondary_languages": ["English", "isiZulu"],
        "infrastructure_deficits": {
            "water": 86.4,       # Unsafe communal standpipes, broken water booster pumps
            "power": 75.8,       # Rolling blackouts (load shedding) destroying cold chain in rural clinics
            "roads": 81.0,       # Potholed gravel roads preventing scholar transport
            "health": 79.5,      # Overburdened district hospital serving 300,000 people
            "telecom": 62.1,     # High data cost and network outages
            "sanitation": 83.2   # Dangerous pit latrines in rural schools (urgent national priority)
        },
        "ongoing_schemes": [
            {"scheme": "Municipal Infrastructure Grant (MIG)", "allocated_cr": 82.0, "spent_cr": 44.0, "status": "Delayed"}
        ]
    }
}

# National Infrastructure Schemes Catalog for Automated Project Formulation
NATIONAL_SCHEMES_CATALOG: Dict[str, Dict[str, Any]] = {
    "water": {
        "india_scheme": "Jal Jeevan Mission (Har Ghar Jal) & AMRUT 2.0",
        "brics_framework": "BRICS Clean Water & Sanitation DPI Initiative",
        "typical_capex_per_beneficiary_inr": 4500,
        "typical_timeline_months": 12,
        "primary_sdg": "SDG 6: Clean Water and Sanitation",
        "sdg_impact_multiplier": 1.45
    },
    "power": {
        "india_scheme": "PM-KUSUM & RDSS (Revamped Distribution Sector Scheme)",
        "brics_framework": "BRICS Just Energy Transition & Solar Grid Accord",
        "typical_capex_per_beneficiary_inr": 3800,
        "typical_timeline_months": 9,
        "primary_sdg": "SDG 7: Affordable and Clean Energy",
        "sdg_impact_multiplier": 1.35
    },
    "roads": {
        "india_scheme": "PMGSY (Pradhan Mantri Gram Sadak Yojana - Phase IV)",
        "brics_framework": "BRICS Rural-Urban Connectivity Partnership",
        "typical_capex_per_beneficiary_inr": 6200,
        "typical_timeline_months": 15,
        "primary_sdg": "SDG 9: Industry, Innovation and Infrastructure",
        "sdg_impact_multiplier": 1.40
    },
    "health": {
        "india_scheme": "PM-ABHIM (Ayushman Bharat Health Infrastructure Mission)",
        "brics_framework": "BRICS Integrated Health Surveillance & Telemedicine Network",
        "typical_capex_per_beneficiary_inr": 5100,
        "typical_timeline_months": 14,
        "primary_sdg": "SDG 3: Good Health and Well-Being",
        "sdg_impact_multiplier": 1.50
    },
    "telecom": {
        "india_scheme": "BharatNet (USOF) & Digital India Gramin Telecom Mission",
        "brics_framework": "BRICS Digital Public Infrastructure Connectivity Rail",
        "typical_capex_per_beneficiary_inr": 2900,
        "typical_timeline_months": 8,
        "primary_sdg": "SDG 9 & SDG 10: Reduced Inequalities & Digital Inclusion",
        "sdg_impact_multiplier": 1.30
    },
    "sanitation": {
        "india_scheme": "Swachh Bharat Mission (Grameen Phase-II)",
        "brics_framework": "BRICS Public Health & Waste Management Cooperative",
        "typical_capex_per_beneficiary_inr": 2400,
        "typical_timeline_months": 6,
        "primary_sdg": "SDG 6 & SDG 11: Sustainable Cities & Communities",
        "sdg_impact_multiplier": 1.25
    }
}
