"""
Closed-Loop DPI Impact Measurement, What-If Budget Simulator & Ghost Asset Sentinel.
Verifies whether completed infrastructure delivers ground-truth human impact.
"""

from typing import List, Dict, Any

class ImpactTrackerEngine:
    """Measures DPI rollout impact, runs policy budget simulations, and detects ghost asset discrepancies."""

    # Pre-recorded citizen verification audits on completed government works
    AUDIT_RECORDS: List[Dict[str, Any]] = [
        {
            "audit_id": "AUD-IN-801",
            "project_ref": "Bundelkhand Pipeline Phase-1 (Chitrakoot)",
            "official_status": "Officially Marked 100% Complete",
            "contractor_expenditure_cr": 42.0,
            "citizen_ivr_calls_attempted": 500,
            "citizen_responses_received": 342,
            "confirmed_functional_pct": 21.3,
            "reported_defective_pct": 78.7,
            "discrepancy_alert": "CRITICAL GHOST ASSET RISK: Taps dry despite contractor billing sign-off",
            "sentiment_score_delta": -28.4,
            "investigation_flag": True
        },
        {
            "audit_id": "AUD-IN-802",
            "project_ref": "PMGSY All-Weather Forest Link Road (Gadchiroli)",
            "official_status": "Officially Marked 100% Complete",
            "contractor_expenditure_cr": 28.5,
            "citizen_ivr_calls_attempted": 300,
            "citizen_responses_received": 218,
            "confirmed_functional_pct": 89.4,
            "reported_defective_pct": 10.6,
            "discrepancy_alert": "VERIFIED EXCELLENT DELIVERY: 89% positive citizen verification",
            "sentiment_score_delta": +64.2,
            "investigation_flag": False
        },
        {
            "audit_id": "AUD-IN-803",
            "project_ref": "Ayushman Arogya Mandir Solar Upgrade (Raichur)",
            "official_status": "Officially Marked 100% Complete",
            "contractor_expenditure_cr": 9.2,
            "citizen_ivr_calls_attempted": 250,
            "citizen_responses_received": 184,
            "confirmed_functional_pct": 45.1,
            "reported_defective_pct": 54.9,
            "discrepancy_alert": "PARTIAL FAILURE: Solar panels installed but inverter batteries dead",
            "sentiment_score_delta": -12.0,
            "investigation_flag": True
        }
    ]

    @classmethod
    def simulate_budget_allocation(cls, total_budget_cr: float, allocations: Dict[str, float], hotspots: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Simulates the human and infrastructural impact of allocating capital budget across sectors.
        Allocations is a dict mapping sector to percentage (summing to 100%).
        """
        sector_budgets = {}
        for sector, pct in allocations.items():
            sector_budgets[sector] = round(total_budget_cr * (pct / 100.0), 2)

        # Evaluate which hotspots would be funded and resolved
        resolved_hotspots = []
        unresolved_hotspots = []
        remaining_budget = sector_budgets.copy()
        total_beneficiaries_reached = 0

        # Typical capex required per hotspot by sector
        hotspot_costs = {
            "water": 18.0,
            "power": 14.0,
            "roads": 25.0,
            "health": 20.0,
            "telecom": 10.0,
            "sanitation": 8.0
        }

        for hs in hotspots:
            sec = hs["sector"]
            req_cost = hotspot_costs.get(sec, 15.0)
            avail = remaining_budget.get(sec, 0.0)

            if avail >= req_cost:
                remaining_budget[sec] = round(avail - req_cost, 2)
                resolved_hotspots.append(hs)
                total_beneficiaries_reached += hs["estimated_affected_population"]
            else:
                unresolved_hotspots.append(hs)

        total_hotspots = len(hotspots)
        resolved_count = len(resolved_hotspots)
        resolution_rate_pct = round((resolved_count / max(1, total_hotspots)) * 100, 1)

        # Projected impact metrics
        projected_deficit_reduction_pct = round(resolution_rate_pct * 0.42, 1)
        projected_satisfaction_surge_pct = round(resolution_rate_pct * 0.65, 1)

        return {
            "total_budget_simulated_cr": total_budget_cr,
            "sector_budgets_allocated_cr": sector_budgets,
            "total_hotspots_evaluated": total_hotspots,
            "hotspots_resolved_count": resolved_count,
            "hotspots_unresolved_count": len(unresolved_hotspots),
            "resolution_rate_pct": resolution_rate_pct,
            "total_beneficiaries_reached": total_beneficiaries_reached,
            "projected_deficit_reduction_pct": projected_deficit_reduction_pct,
            "projected_satisfaction_surge_pct": projected_satisfaction_surge_pct,
            "remaining_unallocated_budget_cr": round(sum(remaining_budget.values()), 2),
            "resolved_hotspot_ids": [h["hotspot_id"] for h in resolved_hotspots]
        }
