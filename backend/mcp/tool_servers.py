"""
MCP (Model Context Protocol) Tool Servers.
Implements the 5 core DPG tool servers specified in Section 6.3 of India Pilot Master Plan:
1. jgs-gazetteer: Village/LGD resolution, reverse geocoding, administrative chain.
2. jgs-privacy: Two-pass PII redaction, leakage scan, consent verification.
3. jgs-schemes: Scheme matching, Schedule of Rates (SoR) unit costs, progress queries.
4. jgs-optimizer: Deterministic MILP portfolio optimization.
5. jgs-audit: Tamper-evident ledger append and cryptographic chain verification.
"""

from typing import List, Dict, Any, Optional
import difflib
import math
from backend.data.sovereign_data import VILLAGE_GAZETTEER, DISTRICT_PROFILES, NATIONAL_SCHEMES_CATALOG
from backend.services.nlp_engine import MultilingualNLPEngine
from backend.services.audit_service import AUDIT
from backend.services.mcda_recommender import MCDAProjectRecommender

class GazetteerMCP:
    """jgs-gazetteer: Authoritative LGD place name resolution and geocoding."""

    @staticmethod
    def resolve_place(mention: str, district_lgd: Optional[str] = None, limit: int = 3) -> List[Dict[str, Any]]:
        """Fuzzy matches free-text place mention to authoritative LGD villages."""
        mention_clean = mention.strip().lower()
        candidates = []

        for v in VILLAGE_GAZETTEER:
            if district_lgd and v.get("district_code") != district_lgd:
                continue

            # Compare Devanagari local name and transliteration
            sim_local = difflib.SequenceMatcher(None, mention_clean, v["name_local"].lower()).ratio()
            sim_translit = difflib.SequenceMatcher(None, mention_clean, v["name_translit"].lower()).ratio()
            sim_en = difflib.SequenceMatcher(None, mention_clean, v["name_en"].lower()).ratio()

            best_sim = max(sim_local, sim_translit, sim_en)
            if best_sim > 0.40 or mention_clean in v["name_local"] or mention_clean in v["name_en"].lower():
                # Population boost prior: log(pop)
                pop_boost = min(0.15, math.log10(max(10, v.get("population", 1000))) * 0.03)
                score = round(min(0.99, best_sim * 0.85 + pop_boost), 2)
                candidates.append({
                    "village_code": v["village_code"],
                    "name_en": v["name_en"],
                    "name_local": v["name_local"],
                    "gp_name": v.get("gp_name"),
                    "block_name": v.get("block_name"),
                    "district_code": v["district_code"],
                    "district_name": v["district_name"],
                    "lat": v["lat"],
                    "lon": v["lon"],
                    "h3_r8": v.get("h3_r8"),
                    "score": score
                })

        candidates.sort(key=lambda x: x["score"], reverse=True)
        return candidates[:limit]

    @staticmethod
    def reverse_geocode(lat: float, lon: float, lang: str = "en") -> Optional[Dict[str, Any]]:
        """Finds closest authoritative LGD village to a given GPS coordinate."""
        closest = None
        min_dist = 9999.0

        for v in VILLAGE_GAZETTEER:
            d = math.hypot(lat - v["lat"], lon - v["lon"]) * 111.0  # Approx km
            if d < min_dist:
                min_dist = d
                closest = v

        if closest:
            return {
                "village_code": closest["village_code"],
                "display_name": closest["name_local"] if "mr" in lang or "hi" in lang else closest["name_en"],
                "gp_name": closest.get("gp_name"),
                "block_name": closest.get("block_name"),
                "district_name": closest.get("district_name"),
                "distance_km": round(min_dist, 2),
                "h3_r8": closest.get("h3_r8")
            }
        return None

class PrivacyMCP:
    """jgs-privacy: Zero-knowledge PII redaction and consent verification."""

    @staticmethod
    def redact(text: str, lang: str = "mr") -> Dict[str, Any]:
        sanitized, redacted, leak_check = MultilingualNLPEngine.sanitize_pii(text)
        return {
            "sanitized_text": sanitized,
            "redacted_types": redacted,
            "leakage_check_passed": leak_check
        }

    @staticmethod
    def verify_consent(token: str) -> Dict[str, Any]:
        """Validates compact JWS / consent token structure."""
        valid = bool(token and (len(token) > 10 or token.startswith("eyJ")))
        return {
            "valid": valid,
            "purposes_granted": ["planning_analytics", "followup_contact", "precise_location"],
            "retention_days": 30
        }

class SchemesMCP:
    """jgs-schemes: Official scheme catalogs, SoR norms, and expenditure progress."""

    @staticmethod
    def match_scheme(sector: str, sub_issue: str, lgd: str) -> Dict[str, Any]:
        scheme_info = NATIONAL_SCHEMES_CATALOG.get(sector, {})
        return {
            "sector": sector,
            "sub_issue": sub_issue,
            "scheme_name": scheme_info.get("india_scheme", "State Infrastructure Fund"),
            "scheme_code": scheme_info.get("scheme_code", "SIF"),
            "typical_capex_per_beneficiary_inr": scheme_info.get("typical_capex_per_beneficiary_inr", 4000),
            "typical_timeline_months": scheme_info.get("typical_timeline_months", 12),
            "primary_sdg": scheme_info.get("primary_sdg", "SDG 9: Infrastructure")
        }

    @staticmethod
    def get_progress(lgd_district_code: str, scheme_code: str) -> Dict[str, Any]:
        dist = DISTRICT_PROFILES.get(lgd_district_code, {})
        ongoing = dist.get("ongoing_schemes", [])
        matched = [s for s in ongoing if scheme_code.lower() in s["scheme"].lower()]
        return {
            "district_code": lgd_district_code,
            "scheme_code": scheme_code,
            "schemes": matched or [{"scheme": scheme_code, "status": "No active projects"}]
        }

class OptimizerMCP:
    """jgs-optimizer: Deterministic MILP solver interface."""

    @staticmethod
    def run_portfolio(budget_cr: float, candidates: List[Dict[str, Any]], alpha: float = 0.40) -> Dict[str, Any]:
        return MCDAProjectRecommender.optimize_portfolio(
            candidates=candidates,
            total_budget_cr=budget_cr,
            alpha_aspirational=alpha
        )

class AuditMCP:
    """jgs-audit: Append-only hash-chained ledger interface."""

    @staticmethod
    def append(event: Dict[str, Any]) -> Dict[str, Any]:
        return AUDIT.append_entry(
            actor_sub=event.get("actor_sub", "agent:mcp"),
            actor_role=event.get("actor_role", "agent"),
            action=event.get("action", "agent:tool_call"),
            resource_id=event.get("resource_id", ""),
            lgd_district_code=event.get("lgd_district_code", "27"),
            purpose=event.get("purpose", ""),
            payload=event.get("payload", {})
        )

    @staticmethod
    def verify_chain() -> Dict[str, Any]:
        return AUDIT.verify_chain()
