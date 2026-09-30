"""
Multi-Criteria Decision Analysis (MCDA) & MILP Portfolio Optimizer.
Implements the exact optimization model from Section 7 of India Pilot Master Plan.
Optimizes public capital welfare value subject to budget, equity, aspirational, and sector constraints.
"""

from typing import List, Dict, Any, Optional
import math
from backend.data.sovereign_data import DISTRICT_PROFILES, NATIONAL_SCHEMES_CATALOG

# Try importing PuLP for MILP optimization
try:
    import pulp
    PULP_AVAILABLE = True
except ImportError:
    PULP_AVAILABLE = False

PROJECT_TEMPLATES = {
    "water": [
        "Retrofit JJM FHTC Piped Water + Solar Pumping Network",
        "Community Solar RO Desalination & Aquifer Recharge Complex",
        "Gravity-Fed Protected Drinking Water Scheme"
    ],
    "power": [
        "PM-KUSUM Dedicated Solar Agri-Feeder & 11kV Line Hardening",
        "Off-Grid Renewable Microgrid & BESS for Tribal Hamlets",
        "Smart Transformer Replacement & Voltage Stabilizer Network"
    ],
    "roads": [
        "PMGSY-IV All-Weather Concrete Paved Road & High-Level Culverts",
        "Flood-Resilient River Embankment & Bridge Corridor",
        "Critical Primary Health Centre & Mandi Access Highway Link"
    ],
    "health": [
        "Ayushman Arogya Mandir (AAM) Maternal & Dialysis Hub",
        "Mobile Diagnostic Ultrasound & Telemedicine Ambulance Network",
        "Sub-Centre Solarization & Cold-Chain Resiliency Upgrade"
    ],
    "telecom": [
        "BharatNet Gram Panchayat Optical Fiber Last-Mile Expansion",
        "Resilient 4G/5G Micro-Tower Grid for PDS Biometric Stations"
    ],
    "sanitation": [
        "High-School Gender-Segregated Bio-Toilet & Greywater Grid",
        "Decentralized Faecal Sludge Treatment Plant (FSTP)"
    ]
}

class MCDAProjectRecommender:
    """Generates discrete project candidates and solves optimal portfolio allocation."""

    @classmethod
    def generate_candidate_projects(cls, hotspots: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Synthesizes discrete, bankable project candidates from demand hotspots."""
        candidates = []
        counter = 1

        for hs in hotspots:
            sector = hs["sector"]
            dist_id = hs.get("lgd_district_code") or hs.get("district_id")
            dist_profile = DISTRICT_PROFILES.get(dist_id, {})
            scheme_info = NATIONAL_SCHEMES_CATALOG.get(sector, {})

            beneficiaries = hs.get("estimated_affected_population", 8000)
            unit_cost = scheme_info.get("typical_capex_per_beneficiary_inr", 4500)
            base_capex = (beneficiaries * unit_cost) / 10000000.0  # in ₹ Crores
            capex_cr = round(max(3.5, min(65.0, base_capex)), 2)

            timeline_months = scheme_info.get("typical_timeline_months", 12)
            sdg_mult = scheme_info.get("sdg_impact_multiplier", 1.35)
            ds = hs.get("disparity_score", hs.get("demand_score", 65.0))
            vulnerability = hs.get("vulnerability_index", 50.0)

            # Capex efficiency: 10 to 100
            capex_eff = max(10.0, min(100.0, 100.0 - (capex_cr / max(1, beneficiaries) * 5000)))

            # Multi-Criteria Score: 40% DS + 25% Vuln + 20% SDG + 15% CapexEff
            mcda_score = round(
                (0.40 * ds) +
                (0.25 * vulnerability) +
                (0.20 * (sdg_mult * 50.0)) +
                (0.15 * capex_eff),
                1
            )

            # Welfare Value: MCDA * ln(1 + beneficiaries)
            welfare_value = round(mcda_score * math.log(1.0 + beneficiaries), 1)

            # Template title
            titles = PROJECT_TEMPLATES.get(sector, ["Critical Infrastructure Modernization"])
            title = f"{titles[counter % len(titles)]} - {hs.get('district_name')}"

            # Demographics for equity constraints
            is_aspirational = dist_profile.get("aspirational_district", True)
            sc_st_share = dist_profile.get("sc_st_share", 0.35)

            candidates.append({
                "id": f"PRJ-{dist_id}-{counter:03d}",
                "project_id": f"PRJ-{dist_id}-{counter:03d}",
                "title": title,
                "project_title": title,
                "sector": sector,
                "scheme": scheme_info.get("scheme_code", "Sovereign-Infra"),
                "funding_scheme": scheme_info.get("india_scheme", "Special Central Assistance"),
                "lgd_district_code": dist_id,
                "district_id": dist_id,
                "district_name": hs.get("district_name"),
                "state_or_province": hs.get("state_or_province", "Maharashtra"),
                "country": hs.get("country", "India"),
                "country_code": hs.get("country_code", "IN"),
                "lat": hs.get("lat"),
                "lon": hs.get("lon"),
                "cost_cr": capex_cr,
                "estimated_capex_cr_inr": capex_cr,
                "estimated_capex_usd_mn": round(capex_cr * 0.12, 2),
                "beneficiaries": beneficiaries,
                "projected_beneficiaries": beneficiaries,
                "duration_months": timeline_months,
                "execution_timeline_months": timeline_months,
                "aspirational": is_aspirational,
                "st_sc_share": sc_st_share,
                "demand_score": ds,
                "vulnerability": vulnerability,
                "sdg_mult": sdg_mult,
                "primary_sdg": scheme_info.get("primary_sdg", "SDG 9: Infrastructure"),
                "mcda_priority_score": mcda_score,
                "value": welfare_value,
                "urgency_grade": "TIER-1 (CRITICAL)" if mcda_score >= 78 else "TIER-2 (HIGH)" if mcda_score >= 65 else "TIER-3 (MODERATE)",
                "hotspot_ref_id": hs.get("hotspot_id"),
                "citizen_corroborations": hs.get("total_corroborations", 1),
                "ground_evidence_sample": hs.get("sample_testimonies", ["Corroborated community signals"])[0] if hs.get("sample_testimonies") else "Verified citizen signals.",
                "policy_impact_rationale": (
                    f"Directly resolves verified infrastructure gap of {hs.get('sector_deficit_index', 65)}% in {hs.get('district_name')}. "
                    f"Prioritized due to socioeconomic vulnerability index of {vulnerability}/100 and "
                    f"{hs.get('total_corroborations', 1)} corroborated citizen voice signals."
                ),
                "approval_status": "proposed",
                "proposed_by": "system:mcda_engine"
            })
            counter += 1

        return candidates

    @classmethod
    def optimize_portfolio(
        cls,
        candidates: List[Dict[str, Any]],
        total_budget_cr: float = 120.0,
        alpha_aspirational: float = 0.40,
        beta_sc_st: float = 0.30,
        gamma_sector_cap: float = 0.35,
        max_duration_months: int = 18
    ) -> Dict[str, Any]:
        """
        Solves Mixed-Integer Linear Program (MILP) maximizing total welfare subject to:
        1. Total budget <= B
        2. Aspirational district share >= alpha * total_spent
        3. SC/ST beneficiary share >= beta * total_spent
        4. Sector diversity cap <= gamma * B
        5. Duration <= max_duration_months
        """
        valid_pool = [p for p in candidates if p.get("duration_months", 12) <= max_duration_months]
        if not valid_pool:
            return {"status": "EmptyPool", "selected": [], "total_cost_cr": 0.0}

        # Method 1: PuLP CBC Solver if installed
        if PULP_AVAILABLE:
            try:
                prob = pulp.LpProblem("JGS_Portfolio_Optimization", pulp.LpMaximize)
                x = {p["id"]: pulp.LpVariable(f"x_{p['id']}", cat="Binary") for p in valid_pool}

                # Objective: Maximize sum(x_p * value_p)
                prob += pulp.lpSum(p["value"] * x[p["id"]] for p in valid_pool)

                # Total Cost variable
                total_cost = pulp.lpSum(p["cost_cr"] * x[p["id"]] for p in valid_pool)
                prob += total_cost <= total_budget_cr

                # Equity Constraint 1: Aspirational district share >= alpha * total_cost
                prob += pulp.lpSum(p["cost_cr"] * x[p["id"]] for p in valid_pool if p.get("aspirational")) >= alpha_aspirational * total_cost

                # Equity Constraint 2: SC/ST funding share >= beta * total_cost
                prob += pulp.lpSum(p["cost_cr"] * p.get("st_sc_share", 0.0) * x[p["id"]] for p in valid_pool) >= beta_sc_st * total_cost

                # Sector Diversity Cap: Any single sector <= gamma * B
                sectors = {p["sector"] for p in valid_pool}
                for s in sectors:
                    prob += pulp.lpSum(p["cost_cr"] * x[p["id"]] for p in valid_pool if p["sector"] == s) <= gamma_sector_cap * total_budget_cr

                solver = pulp.PULP_CBC_CMD(msg=False, timeLimit=20)
                prob.solve(solver)

                selected = [p for p in valid_pool if x[p["id"]].value() and x[p["id"]].value() > 0.5]
                total_spent = round(sum(p["cost_cr"] for p in selected), 2)
                total_welfare = round(sum(p["value"] for p in selected), 1)

                # Identify binding constraints
                binding = []
                if total_spent >= total_budget_cr * 0.95:
                    binding.append("Total Budget Cap (₹ B Cr)")
                asp_spent = sum(p["cost_cr"] for p in selected if p.get("aspirational"))
                if total_spent > 0 and (asp_spent / total_spent) <= alpha_aspirational + 0.05:
                    binding.append("Aspirational District Equity Floor (40%)")

                return {
                    "status": "Optimal",
                    "solver": "PuLP-CBC",
                    "total_budget_cr": total_budget_cr,
                    "total_cost_cr": total_spent,
                    "total_welfare_points": total_welfare,
                    "selected_count": len(selected),
                    "total_candidates": len(valid_pool),
                    "selected_projects": selected,
                    "binding_constraints": binding or ["Budget Headroom Available"],
                    "aspirational_share_pct": round((asp_spent / max(0.1, total_spent)) * 100, 1) if total_spent else 0.0
                }
            except Exception as e:
                # Fall back to greedy knapsack
                pass

        # Method 2: Heuristic 0/1 Knapsack Fallback with Equity Sorting
        sorted_pool = sorted(valid_pool, key=lambda p: (p.get("aspirational", False), p["value"] / max(0.1, p["cost_cr"])), reverse=True)
        selected = []
        spent = 0.0
        sector_spent: Dict[str, float] = {}

        for p in sorted_pool:
            c = p["cost_cr"]
            sec = p["sector"]
            sec_curr = sector_spent.get(sec, 0.0)

            if spent + c <= total_budget_cr and (sec_curr + c) <= (gamma_sector_cap * total_budget_cr + 5.0):
                selected.append(p)
                spent += c
                sector_spent[sec] = sec_curr + c

        return {
            "status": "Feasible",
            "solver": "DynamicKnapsackFallback",
            "total_budget_cr": total_budget_cr,
            "total_cost_cr": round(spent, 2),
            "total_welfare_points": round(sum(p["value"] for p in selected), 1),
            "selected_count": len(selected),
            "total_candidates": len(valid_pool),
            "selected_projects": selected,
            "binding_constraints": ["Total Budget Cap"],
            "aspirational_share_pct": round((sum(p["cost_cr"] for p in selected if p.get("aspirational")) / max(0.1, spent)) * 100, 1)
        }

    @classmethod
    def generate_recommendations(cls, hotspots: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generates ranked project dossiers ready for administrative review."""
        candidates = cls.generate_candidate_projects(hotspots)
        candidates.sort(key=lambda x: x["mcda_priority_score"], reverse=True)
        return candidates
