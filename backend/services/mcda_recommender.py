"""
Multi-Criteria Decision Analysis (MCDA) Project Prioritization & Recommendation Engine.
Formulates discrete, bankable capital project dossiers mapped to national budgets & schemes.
"""

from typing import List, Dict, Any
from backend.data.sovereign_data import DISTRICT_PROFILES, NATIONAL_SCHEMES_CATALOG

PROJECT_NAME_TEMPLATES = {
    "water": [
        "Project Jal-Suraksha: Decentralized Deep-Aquifer & Solar RO Purification Grid",
        "Project Har Ghar Jal-Vikas: Gravity-Fed Piped Drinking Water Network",
        "Coastal Aquifer Protection & Solar Desalination Project"
    ],
    "power": [
        "Project Surya-Shakti: Dedicated Solar Agri-Feeder & Resilient Transformer Network",
        "Project Urja-Drishti: Off-Grid Renewable Microgrid & Storage for Tribal Clusters",
        "Grid Modernization & 11kV Substation Hardening"
    ],
    "roads": [
        "Project Sadak-Setu: All-Weather Concrete Arterial & High-Level Culverts",
        "Gramin Lifeline Connectivity: Flood-Resilient Raised Embankment Corridors",
        "Critical Healthcare & Farm Access Corridors"
    ],
    "health": [
        "Project Arogya-Kavach: Ayushman Health & Wellness Hub with 24x7 Emergency Care",
        "Mobile Diagnostic & Maternal Health Telemedicine Network",
        "Integrated Maternal, Child & Dialysis Care Center"
    ],
    "telecom": [
        "Project Digital-Gati: Fiber-to-Panchayat & Resilient 4G/5G Micro-Tower Grid",
        "Broadband Lifeline for Rural Schools, PHCs & Biometric PDS Outlets"
    ],
    "sanitation": [
        "Project Nirmal-Grama: High-School Gender-Segregated Bio-Toilets & Drainage",
        "Decentralized Faecal Sludge & Greywater Treatment Complex"
    ]
}

class MCDAProjectRecommender:
    """Ranks and generates actionable infrastructure project dossiers."""

    @classmethod
    def generate_recommendations(cls, hotspots: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Takes prioritized hotspots and generates bankable project dossiers.
        """
        recommendations = []
        project_counter = 1

        for hs in hotspots:
            sector = hs["sector"]
            dist_id = hs["district_id"]
            dist_profile = DISTRICT_PROFILES.get(dist_id, {})
            scheme_info = NATIONAL_SCHEMES_CATALOG.get(sector, {})

            # Calculate estimated project capex and beneficiaries
            beneficiaries = hs["estimated_affected_population"]
            unit_cost_inr = scheme_info.get("typical_capex_per_beneficiary_inr", 4000)
            
            # Base Capex in INR Crores (1 Crore = 10 Million INR)
            base_capex_cr = round((beneficiaries * unit_cost_inr) / 10000000.0, 2)
            # Bound capex to realistic district package sizes (₹ 4.5 Cr to ₹ 85 Cr)
            capex_cr = round(max(4.5, min(85.0, base_capex_cr)), 2)
            capex_usd_mn = round(capex_cr * 0.12, 2)  # Approx conversion

            timeline_months = scheme_info.get("typical_timeline_months", 12)
            sdg_multiplier = scheme_info.get("sdg_impact_multiplier", 1.30)
            disparity = hs["disparity_score"]
            vulnerability = hs["vulnerability_index"]

            # Multi-Criteria Priority Score (0 - 100)
            # Factors: Disparity Score (40%), Vulnerability (25%), SDG Impact (20%), Capex Efficiency (15%)
            capex_efficiency = max(10.0, min(100.0, 100.0 - (capex_cr / beneficiaries * 5000)))
            mcda_priority_score = round(
                (0.40 * disparity) +
                (0.25 * vulnerability) +
                (0.20 * (sdg_multiplier * 50)) +
                (0.15 * capex_efficiency),
                1
            )

            # Pick contextual project title
            template_list = PROJECT_NAME_TEMPLATES.get(sector, ["Critical Infrastructure Modernization"])
            project_title = f"{template_list[project_counter % len(template_list)]} - {hs['district_name']}"

            # Scheme mapping
            if hs.get("country_code") == "IN":
                funding_scheme = scheme_info.get("india_scheme", "Special Central Assistance")
            else:
                funding_scheme = scheme_info.get("brics_framework", "BRICS Sovereign Co-Financing Facility")

            # Evidence synthesis
            primary_evidence = hs["sample_testimonies"][0] if hs["sample_testimonies"] else "Multiple corroborated community requests."

            recommendations.append({
                "project_id": f"PRJ-{hs['country_code']}-{project_counter:03d}",
                "project_title": project_title,
                "sector": sector,
                "district_id": dist_id,
                "district_name": hs["district_name"],
                "state_or_province": hs["state_or_province"],
                "country": hs["country"],
                "country_code": hs["country_code"],
                "lat": hs["lat"],
                "lon": hs["lon"],
                "mcda_priority_score": mcda_priority_score,
                "urgency_grade": "TIER-1 (CRITICAL)" if mcda_priority_score >= 80 else "TIER-2 (HIGH)" if mcda_priority_score >= 65 else "TIER-3 (MODERATE)",
                "estimated_capex_cr_inr": capex_cr,
                "estimated_capex_usd_mn": capex_usd_mn,
                "projected_beneficiaries": beneficiaries,
                "execution_timeline_months": timeline_months,
                "funding_scheme": funding_scheme,
                "primary_sdg": scheme_info.get("primary_sdg", "SDG 9: Infrastructure"),
                "sdg_impact_multiplier": sdg_multiplier,
                "citizen_corroborations": hs["total_corroborations"],
                "ground_evidence_sample": primary_evidence,
                "hotspot_ref_id": hs["hotspot_id"],
                "policy_impact_rationale": (
                    f"Directly resolves verified infrastructure deficit of {hs['sector_deficit_index']}% in {hs['district_name']}. "
                    f"Prioritized due to socioeconomic vulnerability index of {hs['vulnerability_index']}/100 and "
                    f"{hs['total_corroborations']} corroborated citizen voice distress signals."
                )
            })
            project_counter += 1

        recommendations.sort(key=lambda x: x["mcda_priority_score"], reverse=True)
        return recommendations
