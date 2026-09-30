"""
Sovereign Demographic, Infrastructure Deficit, and Public Investment Datasets.
Canonical Local Government Directory (LGD) Codes, Census Indicators,
Authoritative Village Gazetteer (Maharashtra Pilot Focus) + BRICS Benchmarks.
"""

from typing import Dict, List, Any, Optional

# Canonical LGD State Codes
LGD_STATES = {
    "27": {"code": "27", "name_en": "Maharashtra", "name_local": "महाराष्ट्र", "iso": "IN-MH"},
    "09": {"code": "09", "name_en": "Uttar Pradesh", "name_local": "उत्तर प्रदेश", "iso": "IN-UP"},
    "22": {"code": "22", "name_en": "Chhattisgarh", "name_local": "छत्तीसगढ़", "iso": "IN-CT"},
    "29": {"code": "29", "name_en": "Karnataka", "name_local": "ಕರ್ನಾಟಕ", "iso": "IN-KA"},
    "06": {"code": "06", "name_en": "Haryana", "name_local": "हरियाणा", "iso": "IN-HR"},
    "33": {"code": "33", "name_en": "Tamil Nadu", "name_local": "தமிழ்நாடு", "iso": "IN-TN"},
    "10": {"code": "10", "name_en": "Bihar", "name_local": "बिहार", "iso": "IN-BR"}
}

# Authoritative Village Gazetteer for Pilot Regions (with local names, transliteration, H3 cells, pop)
VILLAGE_GAZETTEER: List[Dict[str, Any]] = [
    # GADCHIROLI (State: 27, District: 990001 / LGD: 499)
    {
        "village_code": "990000101",
        "name_en": "Kasansur",
        "name_local": "कासनसूर",
        "name_translit": "kasanasur",
        "gp_code": "990001",
        "gp_name": "Kasansur GP",
        "block_code": "9901",
        "block_name": "Etapalli",
        "district_code": "990001",
        "district_name": "Gadchiroli",
        "state_code": "27",
        "population": 1842,
        "lat": 19.6845,
        "lon": 80.2451,
        "h3_r8": "8860a2a1b3fffff",
        "h3_r7": "8760a2a1bffffff"
    },
    {
        "village_code": "990000102",
        "name_en": "Arewada",
        "name_local": "आरेवाडा",
        "name_translit": "arewada",
        "gp_code": "990002",
        "gp_name": "Arewada GP",
        "block_code": "9902",
        "block_name": "Bhamragad",
        "district_code": "990001",
        "district_name": "Gadchiroli",
        "state_code": "27",
        "population": 1420,
        "lat": 19.3871,
        "lon": 80.3541,
        "h3_r8": "8860a2b4c7fffff",
        "h3_r7": "8760a2b4cffffff"
    },
    {
        "village_code": "990000103",
        "name_en": "Nanhi",
        "name_local": "नान्ही",
        "name_translit": "nanhi",
        "gp_code": "990003",
        "gp_name": "Nanhi GP",
        "block_code": "9904",
        "block_name": "Kurkheda",
        "district_code": "990001",
        "district_name": "Gadchiroli",
        "state_code": "27",
        "population": 2190,
        "lat": 20.3500,
        "lon": 80.1800,
        "h3_r8": "8860a28355fffff",
        "h3_r7": "8760a2835ffffff"
    },
    {
        "village_code": "990002210",
        "name_en": "Jimalgatta",
        "name_local": "जिमलगट्टा",
        "name_translit": "jimalgatta",
        "gp_code": "990114",
        "gp_name": "Jimalgatta GP",
        "block_code": "9903",
        "block_name": "Aheri",
        "district_code": "990001",
        "district_name": "Gadchiroli",
        "state_code": "27",
        "population": 3120,
        "lat": 19.3871,
        "lon": 80.4412,
        "h3_r8": "8860a2b4c7fffff",
        "h3_r7": "8760a2b4cffffff"
    },
    {
        "village_code": "990000104",
        "name_en": "Sironcha",
        "name_local": "सिरोंचा",
        "name_translit": "sironcha",
        "gp_code": "990005",
        "gp_name": "Sironcha GP",
        "block_code": "9905",
        "block_name": "Sironcha",
        "district_code": "990001",
        "district_name": "Gadchiroli",
        "state_code": "27",
        "population": 7890,
        "lat": 18.8354,
        "lon": 79.9612,
        "h3_r8": "8860a21643fffff",
        "h3_r7": "8760a2164ffffff"
    },

    # NANDURBAR (State: 27, District: 990002 / LGD: 479) - Tribal Bhil Belt
    {
        "village_code": "990000201",
        "name_en": "Dhadgaon (Akrani)",
        "name_local": "धडगाव",
        "name_translit": "dhadgaon",
        "gp_code": "990011",
        "gp_name": "Dhadgaon GP",
        "block_code": "9911",
        "block_name": "Dhadgaon",
        "district_code": "990002",
        "district_name": "Nandurbar",
        "state_code": "27",
        "population": 4560,
        "lat": 21.8341,
        "lon": 74.2215,
        "h3_r8": "8860956b43fffff",
        "h3_r7": "8760956b4ffffff"
    },
    {
        "village_code": "990000202",
        "name_en": "Molgi",
        "name_local": "मोलगी",
        "name_translit": "molgi",
        "gp_code": "990012",
        "gp_name": "Molgi GP",
        "block_code": "9911",
        "block_name": "Dhadgaon",
        "district_code": "990002",
        "district_name": "Nandurbar",
        "state_code": "27",
        "population": 2980,
        "lat": 21.7214,
        "lon": 74.0512,
        "h3_r8": "8860956891fffff",
        "h3_r7": "876095689ffffff"
    },

    # WASHIM (State: 27, District: 990003 / LGD: 482) - Agrarian Vidarbha
    {
        "village_code": "990000301",
        "name_en": "Manora",
        "name_local": "मानोरा",
        "name_translit": "manora",
        "gp_code": "990021",
        "gp_name": "Manora GP",
        "block_code": "9922",
        "block_name": "Manora",
        "district_code": "990003",
        "district_name": "Washim",
        "state_code": "27",
        "population": 8420,
        "lat": 20.2185,
        "lon": 77.5512,
        "h3_r8": "8860b45723fffff",
        "h3_r7": "8760b4572ffffff"
    },

    # CHITRAKOOT (State: 09, District: 164)
    {
        "village_code": "090000101",
        "name_en": "Ranipur",
        "name_local": "रानीपुर",
        "name_translit": "ranipur",
        "gp_code": "090001",
        "gp_name": "Ranipur GP",
        "block_code": "0901",
        "block_name": "Manikpur",
        "district_code": "164",
        "district_name": "Chitrakoot",
        "state_code": "09",
        "population": 2340,
        "lat": 25.0450,
        "lon": 81.1200,
        "h3_r8": "883cf305d3fffff",
        "h3_r7": "873cf305dffffff"
    },

    # BASTAR (State: 22, District: 374)
    {
        "village_code": "220000101",
        "name_en": "Bade Kilepal",
        "name_local": "बडेकिलेपाल",
        "name_translit": "badekilepal",
        "gp_code": "220001",
        "gp_name": "Bade Kilepal GP",
        "block_code": "2201",
        "block_name": "Tokapal",
        "district_code": "374",
        "district_name": "Bastar",
        "state_code": "22",
        "population": 1950,
        "lat": 18.9100,
        "lon": 81.8200,
        "h3_r8": "886196230bfffff",
        "h3_r7": "876196230ffffff"
    },

    # RAICHUR (State: 29, District: 547)
    {
        "village_code": "290000101",
        "name_en": "Potnal",
        "name_local": "ಪೊಟ್ನಲ್",
        "name_translit": "potnal",
        "gp_code": "290001",
        "gp_name": "Potnal GP",
        "block_code": "2901",
        "block_name": "Manvi",
        "district_code": "547",
        "district_name": "Raichur",
        "state_code": "29",
        "population": 3610,
        "lat": 16.0100,
        "lon": 77.0600,
        "h3_r8": "8860163351fffff",
        "h3_r7": "876016335ffffff"
    },

    # NUH (State: 06, District: 85)
    {
        "village_code": "060000101",
        "name_en": "Jamun Khera",
        "name_local": "जामुन खेड़ा",
        "name_translit": "jamunkhera",
        "gp_code": "060001",
        "gp_name": "Jamun Khera GP",
        "block_code": "0601",
        "block_name": "Punhana",
        "district_code": "85",
        "district_name": "Nuh",
        "state_code": "06",
        "population": 2840,
        "lat": 27.8700,
        "lon": 77.2000,
        "h3_r8": "883e8b0b53fffff",
        "h3_r7": "873e8b0b5ffffff"
    }
]

# Canonical District Profiles with LGD Codes & Indicators
DISTRICT_PROFILES: Dict[str, Dict[str, Any]] = {
    # MAHARASHTRA PILOT 1: GADCHIROLI (LGD: 499 / 990001)
    "990001": {
        "id": "990001",
        "legacy_id": "IN-DIST-01",
        "lgd_district_code": "990001",
        "lgd_state_code": "27",
        "country": "India",
        "country_code": "IN",
        "state": "Maharashtra",
        "district": "Gadchiroli (Vidarbha)",
        "lat": 20.1809,
        "lon": 80.0000,
        "population": 1150000,
        "rural_percentage": 88.5,
        "tribal_percentage": 38.7,
        "poverty_rate": 0.412,
        "sc_st_share": 0.528,
        "rural_share": 0.885,
        "literacy_rate": 74.4,
        "aspirational_district": True,
        "primary_language": "Marathi",
        "secondary_languages": ["Hindi", "Gondi", "Madia"],
        "infrastructure_deficits": {
            "water": 78.4,
            "power": 64.2,
            "roads": 82.1,
            "health": 86.5,
            "telecom": 79.0,
            "sanitation": 61.3
        },
        "ongoing_schemes": [
            {"scheme": "Jal Jeevan Mission", "allocated_cr": 45.0, "spent_cr": 22.1, "status": "Delayed"},
            {"scheme": "PMGSY Roads", "allocated_cr": 68.0, "spent_cr": 54.0, "status": "In-Progress"},
            {"scheme": "Ayushman Arogya Mandir", "allocated_cr": 18.5, "spent_cr": 9.2, "status": "Critical Gap"}
        ]
    },

    # MAHARASHTRA PILOT 2: NANDURBAR (LGD: 479 / 990002) - Tribal Bhil Belt
    "990002": {
        "id": "990002",
        "legacy_id": "IN-DIST-MH2",
        "lgd_district_code": "990002",
        "lgd_state_code": "27",
        "country": "India",
        "country_code": "IN",
        "state": "Maharashtra",
        "district": "Nandurbar (Satpura)",
        "lat": 21.3667,
        "lon": 74.2333,
        "population": 1648295,
        "rural_percentage": 83.3,
        "tribal_percentage": 69.3,
        "poverty_rate": 0.472,
        "sc_st_share": 0.725,
        "rural_share": 0.833,
        "literacy_rate": 64.4,
        "aspirational_district": True,
        "primary_language": "Marathi",
        "secondary_languages": ["Bhili", "Hindi", "Ahirani"],
        "infrastructure_deficits": {
            "water": 84.2,
            "power": 68.5,
            "roads": 79.4,
            "health": 88.0,
            "telecom": 74.2,
            "sanitation": 66.5
        },
        "ongoing_schemes": [
            {"scheme": "Jal Jeevan Mission Solar Pumping", "allocated_cr": 52.0, "spent_cr": 24.0, "status": "Delayed"},
            {"scheme": "Satpura All-Weather Connectivity", "allocated_cr": 74.0, "spent_cr": 38.0, "status": "Behind Schedule"}
        ]
    },

    # MAHARASHTRA PILOT 3: WASHIM (LGD: 482 / 990003) - Agrarian Vidarbha
    "990003": {
        "id": "990003",
        "legacy_id": "IN-DIST-MH3",
        "lgd_district_code": "990003",
        "lgd_state_code": "27",
        "country": "India",
        "country_code": "IN",
        "state": "Maharashtra",
        "district": "Washim (Vidarbha)",
        "lat": 20.1084,
        "lon": 77.1352,
        "population": 1197160,
        "rural_percentage": 82.3,
        "tribal_percentage": 6.7,
        "poverty_rate": 0.384,
        "sc_st_share": 0.258,
        "rural_share": 0.823,
        "literacy_rate": 83.2,
        "aspirational_district": True,
        "primary_language": "Marathi",
        "secondary_languages": ["Hindi"],
        "infrastructure_deficits": {
            "water": 76.5,
            "power": 72.1,
            "roads": 58.0,
            "health": 65.4,
            "telecom": 49.0,
            "sanitation": 59.2
        },
        "ongoing_schemes": [
            {"scheme": "PM-KUSUM Agri Feeder Solarisation", "allocated_cr": 40.0, "spent_cr": 18.2, "status": "Under-utilized"}
        ]
    },

    # UTTAR PRADESH: CHITRAKOOT (LGD: 164)
    "164": {
        "id": "164",
        "legacy_id": "IN-DIST-02",
        "lgd_district_code": "164",
        "lgd_state_code": "09",
        "country": "India",
        "country_code": "IN",
        "state": "Uttar Pradesh",
        "district": "Chitrakoot (Bundelkhand)",
        "lat": 25.1764,
        "lon": 80.8667,
        "population": 991738,
        "rural_percentage": 90.3,
        "tribal_percentage": 26.8,
        "poverty_rate": 0.486,
        "sc_st_share": 0.320,
        "rural_share": 0.903,
        "literacy_rate": 65.0,
        "aspirational_district": True,
        "primary_language": "Hindi",
        "secondary_languages": ["Bundeli"],
        "infrastructure_deficits": {
            "water": 92.5,
            "power": 71.0,
            "roads": 65.4,
            "health": 74.8,
            "telecom": 58.2,
            "sanitation": 68.0
        },
        "ongoing_schemes": [
            {"scheme": "Bundelkhand Piped Water Pipeline", "allocated_cr": 120.0, "spent_cr": 88.0, "status": "In-Progress"}
        ]
    },

    # CHHATTISGARH: BASTAR (LGD: 374)
    "374": {
        "id": "374",
        "legacy_id": "IN-DIST-03",
        "lgd_district_code": "374",
        "lgd_state_code": "22",
        "country": "India",
        "country_code": "IN",
        "state": "Chhattisgarh",
        "district": "Bastar (Jagdalpur)",
        "lat": 19.0734,
        "lon": 82.0298,
        "population": 1412746,
        "rural_percentage": 86.2,
        "tribal_percentage": 66.4,
        "poverty_rate": 0.523,
        "sc_st_share": 0.685,
        "rural_share": 0.862,
        "literacy_rate": 54.4,
        "aspirational_district": True,
        "primary_language": "Hindi",
        "secondary_languages": ["Halbi", "Gondi", "Chhattisgarhi"],
        "infrastructure_deficits": {
            "water": 74.0,
            "power": 79.5,
            "roads": 88.6,
            "health": 89.2,
            "telecom": 84.1,
            "sanitation": 72.4
        },
        "ongoing_schemes": [
            {"scheme": "Special Central Assistance (SCA)", "allocated_cr": 85.0, "spent_cr": 41.0, "status": "In-Progress"}
        ]
    },

    # KARNATAKA: RAICHUR (LGD: 547)
    "547": {
        "id": "547",
        "legacy_id": "IN-DIST-04",
        "lgd_district_code": "547",
        "lgd_state_code": "29",
        "country": "India",
        "country_code": "IN",
        "state": "Karnataka",
        "district": "Raichur (Kalyana-Karnataka)",
        "lat": 16.2120,
        "lon": 77.3439,
        "population": 1928812,
        "rural_percentage": 74.5,
        "tribal_percentage": 19.0,
        "poverty_rate": 0.398,
        "sc_st_share": 0.380,
        "rural_share": 0.745,
        "literacy_rate": 59.5,
        "aspirational_district": True,
        "primary_language": "Kannada",
        "secondary_languages": ["Telugu", "Urdu", "Hindi"],
        "infrastructure_deficits": {
            "water": 81.2,
            "power": 55.0,
            "roads": 58.7,
            "health": 78.4,
            "telecom": 46.8,
            "sanitation": 63.5
        },
        "ongoing_schemes": [
            {"scheme": "JJM Rural Piped Water", "allocated_cr": 64.0, "spent_cr": 38.0, "status": "In-Progress"}
        ]
    },

    # HARYANA: NUH (LGD: 85)
    "85": {
        "id": "85",
        "legacy_id": "IN-DIST-05",
        "lgd_district_code": "85",
        "lgd_state_code": "06",
        "country": "India",
        "country_code": "IN",
        "state": "Haryana",
        "district": "Nuh (Mewat)",
        "lat": 28.1186,
        "lon": 77.0016,
        "population": 1089263,
        "rural_percentage": 88.6,
        "tribal_percentage": 0.5,
        "poverty_rate": 0.364,
        "sc_st_share": 0.180,
        "rural_share": 0.886,
        "literacy_rate": 54.1,
        "aspirational_district": True,
        "primary_language": "Hindi",
        "secondary_languages": ["Mewati", "Urdu"],
        "infrastructure_deficits": {
            "water": 89.0,
            "power": 62.8,
            "roads": 52.0,
            "health": 81.6,
            "telecom": 41.2,
            "sanitation": 75.3
        },
        "ongoing_schemes": [
            {"scheme": "Mewat Canal Water Feeder", "allocated_cr": 55.0, "spent_cr": 26.0, "status": "Behind Schedule"}
        ]
    },

    # BRICS BENCHMARK: BRAZIL (BAHIA SERTÃO)
    "BR-DIST-01": {
        "id": "BR-DIST-01",
        "legacy_id": "BR-DIST-01",
        "lgd_district_code": "BR-DIST-01",
        "lgd_state_code": "BR-BA",
        "country": "Brazil",
        "country_code": "BR",
        "state": "Bahia",
        "district": "Juazeiro / Sertão",
        "lat": -9.4167,
        "lon": -40.5000,
        "population": 218162,
        "rural_percentage": 42.1,
        "tribal_percentage": 8.4,
        "poverty_rate": 0.445,
        "sc_st_share": 0.520,
        "rural_share": 0.421,
        "literacy_rate": 78.2,
        "aspirational_district": True,
        "primary_language": "Portuguese",
        "secondary_languages": [],
        "infrastructure_deficits": {
            "water": 88.2,
            "power": 48.0,
            "roads": 69.5,
            "health": 72.0,
            "telecom": 57.3,
            "sanitation": 71.0
        },
        "ongoing_schemes": [
            {"scheme": "Novo PAC - Água para Todos", "allocated_cr": 60.0, "spent_cr": 28.0, "status": "In-Progress"}
        ]
    },

    # BRICS BENCHMARK: SOUTH AFRICA (EASTERN CAPE)
    "ZA-DIST-01": {
        "id": "ZA-DIST-01",
        "legacy_id": "ZA-DIST-01",
        "lgd_district_code": "ZA-DIST-01",
        "lgd_state_code": "ZA-EC",
        "country": "South Africa",
        "country_code": "ZA",
        "state": "Eastern Cape",
        "district": "OR Tambo District",
        "lat": -31.5833,
        "lon": 28.7833,
        "population": 1475000,
        "rural_percentage": 81.3,
        "tribal_percentage": 94.0,
        "poverty_rate": 0.582,
        "sc_st_share": 0.940,
        "rural_share": 0.813,
        "literacy_rate": 69.1,
        "aspirational_district": True,
        "primary_language": "isiXhosa",
        "secondary_languages": ["English", "isiZulu"],
        "infrastructure_deficits": {
            "water": 86.4,
            "power": 75.8,
            "roads": 81.0,
            "health": 79.5,
            "telecom": 62.1,
            "sanitation": 83.2
        },
        "ongoing_schemes": [
            {"scheme": "Municipal Infrastructure Grant (MIG)", "allocated_cr": 82.0, "spent_cr": 44.0, "status": "Delayed"}
        ]
    }
}

# Alias map for backward-compatibility with legacy keys
LEGACY_DISTRICT_ALIASES = {
    "IN-DIST-01": "990001",
    "IN-DIST-02": "164",
    "IN-DIST-03": "374",
    "IN-DIST-04": "547",
    "IN-DIST-05": "85",
    "IN-DIST-06": "990001",  # map to gadchiroli or ramanathapuram
    "IN-DIST-07": "990001",
}
for leg_k, lgd_k in LEGACY_DISTRICT_ALIASES.items():
    if lgd_k in DISTRICT_PROFILES and leg_k not in DISTRICT_PROFILES:
        DISTRICT_PROFILES[leg_k] = DISTRICT_PROFILES[lgd_k]

# National Infrastructure Schemes Catalog with Standard Schedules of Rates (SoR)
NATIONAL_SCHEMES_CATALOG: Dict[str, Dict[str, Any]] = {
    "water": {
        "india_scheme": "Jal Jeevan Mission (Har Ghar Jal)",
        "scheme_code": "JJM",
        "brics_framework": "BRICS Clean Water & Sanitation DPI Initiative",
        "typical_capex_per_beneficiary_inr": 4800,
        "typical_timeline_months": 12,
        "primary_sdg": "SDG 6: Clean Water and Sanitation",
        "sdg_impact_multiplier": 1.45,
        "default_envelope_cr": 75.0
    },
    "power": {
        "india_scheme": "PM-KUSUM & RDSS Feeder Solarisation",
        "scheme_code": "PM-KUSUM",
        "brics_framework": "BRICS Just Energy Transition & Solar Grid Accord",
        "typical_capex_per_beneficiary_inr": 3800,
        "typical_timeline_months": 9,
        "primary_sdg": "SDG 7: Affordable and Clean Energy",
        "sdg_impact_multiplier": 1.35,
        "default_envelope_cr": 45.0
    },
    "roads": {
        "india_scheme": "PMGSY Phase-III & IV All-Weather Road Connectivity",
        "scheme_code": "PMGSY",
        "brics_framework": "BRICS Rural-Urban Connectivity Partnership",
        "typical_capex_per_beneficiary_inr": 6200,
        "typical_timeline_months": 15,
        "primary_sdg": "SDG 9: Industry, Innovation and Infrastructure",
        "sdg_impact_multiplier": 1.40,
        "default_envelope_cr": 90.0
    },
    "health": {
        "india_scheme": "PM-ABHIM & Ayushman Arogya Mandir (Health & Wellness)",
        "scheme_code": "AAM",
        "brics_framework": "BRICS Integrated Health Surveillance & Telemedicine Network",
        "typical_capex_per_beneficiary_inr": 5100,
        "typical_timeline_months": 14,
        "primary_sdg": "SDG 3: Good Health and Well-Being",
        "sdg_impact_multiplier": 1.50,
        "default_envelope_cr": 50.0
    },
    "telecom": {
        "india_scheme": "BharatNet (USOF) GP Last-Mile Broadband Rail",
        "scheme_code": "BharatNet",
        "brics_framework": "BRICS Digital Public Infrastructure Connectivity Rail",
        "typical_capex_per_beneficiary_inr": 2900,
        "typical_timeline_months": 8,
        "primary_sdg": "SDG 9 & SDG 10: Reduced Inequalities & Digital Inclusion",
        "sdg_impact_multiplier": 1.30,
        "default_envelope_cr": 30.0
    },
    "sanitation": {
        "india_scheme": "Swachh Bharat Mission (Grameen Phase-II ODF+)",
        "scheme_code": "SBM-G",
        "brics_framework": "BRICS Public Health & Waste Management Cooperative",
        "typical_capex_per_beneficiary_inr": 2400,
        "typical_timeline_months": 6,
        "primary_sdg": "SDG 6 & SDG 11: Sustainable Cities & Communities",
        "sdg_impact_multiplier": 1.25,
        "default_envelope_cr": 25.0
    }
}
