"""
Empirical-Bayes Demand Scoring & Additive Explainability Engine.
Implements the exact mathematical formulation from Sections 6.6 & 6.7 of India Pilot Master Plan.
Computes deterministic, reproducible scores with full signal attribution.
"""

from typing import List, Dict, Any, Optional
import math
from datetime import datetime, timezone
from backend.data.sovereign_data import DISTRICT_PROFILES

class ScoringEngine:
    # Tunable, versioned policy parameters (governed by 4-eyes approval)
    PARAMS = {
        "version": "dds-1.2",
        "w_c": 0.35,      # Weight: citizen demand density
        "w_s": 0.25,      # Weight: average severity
        "w_d": 0.20,      # Weight: socioeconomic vulnerability
        "w_i": 0.20,      # Weight: official infrastructure gap
        "tau_days": 30.0, # Temporal decay half-life in days
        "c_cap": 50.0,    # Saturation cap per 10k population
        "k_shrink": 10.0, # Empirical-Bayes shrinkage prior weight
        "k_anon_min": 5   # Minimum unique citizens for public aggregation
    }

    @classmethod
    def compute_district_demand(
        cls,
        district_id: str,
        sector: str,
        reports: List[Dict[str, Any]],
        state_mean_ds: float = 50.0
    ) -> Dict[str, Any]:
        """
        Computes the Demand Score (DS) for a given district and sector using empirical-Bayes shrinkage.
        Provides full linear additive decomposition for the explainability drawer.
        """
        dist = DISTRICT_PROFILES.get(district_id, {})
        pop = dist.get("population", 500000)
        p = cls.PARAMS

        # 1. Unique citizen filtering and temporal decay
        now = datetime.now(timezone.utc)
        unique_reporters: Dict[str, Dict[str, Any]] = {}

        for r in reports:
            if r.get("sector") != sector:
                continue
            r_dist = r.get("lgd_district_code") or r.get("district_id")
            if r_dist != district_id and dist.get("legacy_id") != r_dist:
                continue

            hid = r.get("hashed_id") or r.get("id")
            created_at_str = r.get("timestamp") or r.get("created_at") or now.isoformat()
            try:
                dt = datetime.fromisoformat(created_at_str.replace("Z", "+00:00"))
            except Exception:
                dt = now

            days_ago = max(0.0, (now - dt).total_seconds() / 86400.0)
            weight = math.exp(-days_ago / p["tau_days"])
            severity = r.get("severity", 3)

            if hid not in unique_reporters or dt > unique_reporters[hid]["dt"]:
                unique_reporters[hid] = {
                    "weight": weight,
                    "severity": severity,
                    "dt": dt
                }

        n_unique = len(unique_reporters)
        eff_citizens = sum(rep["weight"] for rep in unique_reporters.values())
        avg_sev = (sum(rep["severity"] for rep in unique_reporters.values()) / max(1, n_unique)) if n_unique else 3.0

        # 2. Normalized feature components
        # c_rate = effective unique citizens per 10,000 population
        c_rate = (eff_citizens * 10000.0) / max(1, pop)
        c_hat = min(1.0, math.log(1.0 + c_rate) / math.log(1.0 + p["c_cap"]))
        s_hat = (avg_sev - 1.0) / 4.0

        # Demographic vulnerability weight (D_r = 0.5 * poverty + 0.3 * sc_st + 0.2 * rural)
        poverty_rate = dist.get("poverty_rate", 0.40)
        sc_st_share = dist.get("sc_st_share", 0.35)
        rural_share = dist.get("rural_share", 0.80)
        demo_w = (0.5 * poverty_rate) + (0.3 * sc_st_share) + (0.2 * rural_share)

        # Infrastructure gap index (0 - 100) -> [0.0, 1.0]
        infra_deficits = dist.get("infrastructure_deficits", {})
        gap = infra_deficits.get(sector, 50.0) / 100.0

        # 3. Raw Demand Score (0 - 100)
        ds_raw = 100.0 * (
            p["w_c"] * c_hat +
            p["w_s"] * s_hat +
            p["w_d"] * demo_w +
            p["w_i"] * gap
        )

        # 4. Empirical-Bayes Shrinkage (guards against small-n noise)
        k = p["k_shrink"]
        shrinkage_weight = n_unique / (n_unique + k)
        final_ds = round((shrinkage_weight * ds_raw) + ((1.0 - shrinkage_weight) * state_mean_ds), 1)

        # 5. Additive Signal Contributions (Exact points attribution)
        contrib_citizen = round(100.0 * p["w_c"] * c_hat, 1)
        contrib_severity = round(100.0 * p["w_s"] * s_hat, 1)
        contrib_demographic = round(100.0 * p["w_d"] * demo_w, 1)
        contrib_infra_gap = round(100.0 * p["w_i"] * gap, 1)

        signal_list = [
            {"signal": "citizen_demand", "label": f"Citizen Demand ({n_unique} citizens, {c_rate:.1f}/10k)", "contribution": contrib_citizen},
            {"signal": "severity", "label": f"Severity Index (Avg {avg_sev:.1f}/5)", "contribution": contrib_severity},
            {"signal": "demographic", "label": f"Vulnerability (Poverty/ST {demo_w*100:.0f}%)", "contribution": contrib_demographic},
            {"signal": "infra_gap", "label": f"Infrastructure Deficit ({gap*100:.0f}%)", "contribution": contrib_infra_gap}
        ]
        signal_list.sort(key=lambda s: s["contribution"], reverse=True)

        return {
            "district_id": district_id,
            "lgd_district_code": dist.get("lgd_district_code", district_id),
            "district_name": dist.get("district", "Unknown"),
            "state": dist.get("state", "Maharashtra"),
            "sector": sector,
            "demand_score": final_ds,
            "raw_demand_score": round(ds_raw, 1),
            "unique_citizens": n_unique,
            "effective_citizens": round(eff_citizens, 1),
            "avg_severity": round(avg_sev, 2),
            "infra_gap_pct": round(gap * 100.0, 1),
            "demographic_weight": round(demo_w, 2),
            "top_signals": signal_list[:3],
            "all_signals": signal_list,
            "confidence": "high" if n_unique >= 30 else "medium" if n_unique >= 10 else "low",
            "k_anonymity_passed": n_unique >= p["k_anon_min"],
            "score_version": p["version"]
        }
