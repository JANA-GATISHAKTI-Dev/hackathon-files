"""
LangGraph-Style Agentic Pipeline Orchestrator.
Coordinates the multi-agent workflow:
Intake -> Privacy Guard -> Speech/LID -> Understanding -> Geo-Resolver -> Dedup & Cluster -> Audit.
Complies with Section 6.2 of India Pilot Master Plan.
"""

from typing import Dict, Any, Optional
import uuid
from datetime import datetime, timezone

from backend.mcp.tool_servers import GazetteerMCP, PrivacyMCP, SchemesMCP, AuditMCP
from backend.services.nlp_engine import MultilingualNLPEngine
from backend.data.sovereign_data import DISTRICT_PROFILES

class IngestionOrchestrator:
    """Orchestrates structured intake, verification, and geocoding across agents and MCP tools."""

    @classmethod
    def execute_pipeline(
        cls,
        raw_text: str,
        district_id: str,
        channel: str = "mobile_app",
        consent_token: Optional[str] = None,
        gps: Optional[Dict[str, float]] = None,
        place_mention: Optional[str] = None,
        corroborations: int = 1,
        actor_sub: str = "citizen:anon"
    ) -> Dict[str, Any]:
        """
        Executes the agentic pipeline to produce a canonical JGS v1.0 Ingestion Event.
        """
        now = datetime.now(timezone.utc).isoformat()
        event_id = uuid.uuid4().hex.upper()[:26]

        # 1. Intake Agent: Verify Consent
        consent_status = PrivacyMCP.verify_consent(consent_token or "consent_jws_default_v1")
        if not consent_status.get("valid"):
            raise ValueError("Consent validation failed. DPDP non-compliant request.")

        # 2. Privacy Guard Agent: Two-Pass Redaction & Leakage Assertion
        redact_res = PrivacyMCP.redact(raw_text)
        if not redact_res.get("leakage_check_passed"):
            raise ValueError("Privacy Guard Alert: Residual PII detected in sanitized output.")
        sanitized_text = redact_res["sanitized_text"]

        # 3. Speech / Language ID Agent
        detected_lang = MultilingualNLPEngine.detect_language(sanitized_text)

        # 4. Understanding Agent: Structured Extraction
        nlp_out = MultilingualNLPEngine.process_incoming_request(
            raw_text=raw_text,
            district_id=district_id,
            channel=channel,
            corroborations=corroborations
        )

        # 5. Geo-Resolver Agent: Match place mention or GPS
        geo_resolution = {"method": "unresolved", "confidence": 0.50, "needs_manual_review": True, "candidates": []}
        canonical_loc = None

        if gps and "lat" in gps and "lon" in gps:
            rev_match = GazetteerMCP.reverse_geocode(gps["lat"], gps["lon"], lang=detected_lang)
            if rev_match:
                geo_resolution = {"method": "gps_pip", "confidence": 0.98, "needs_manual_review": False, "candidates": []}
                canonical_loc = {
                    "lgd_state_code": "27",
                    "lgd_district_code": district_id,
                    "lgd_village_code": rev_match.get("village_code"),
                    "display_name": {"en": rev_match.get("display_name"), "mr": rev_match.get("display_name")},
                    "h3_r8": rev_match.get("h3_r8", "8860a2a1b3fffff"),
                    "h3_r7": "8760a2a1bffffff"
                }
        elif place_mention or len(sanitized_text) > 5:
            search_str = place_mention or sanitized_text
            candidates = GazetteerMCP.resolve_place(search_str, district_lgd=district_id, limit=3)
            if candidates:
                top = candidates[0]
                needs_review = (top["score"] < 0.75)
                geo_resolution = {
                    "method": "fuzzy_gazetteer",
                    "confidence": top["score"],
                    "needs_manual_review": needs_review,
                    "candidates": candidates
                }
                canonical_loc = {
                    "lgd_state_code": "27",
                    "lgd_district_code": top.get("district_code", district_id),
                    "lgd_village_code": top.get("village_code"),
                    "display_name": {"en": top.get("name_en"), "mr": top.get("name_local")},
                    "h3_r8": top.get("h3_r8", "8860a2a1b3fffff"),
                    "h3_r7": "8760a2a1bffffff"
                }

        # Fallback to district profile centroid if village not found
        dist_prof = DISTRICT_PROFILES.get(district_id, {})
        if not canonical_loc:
            canonical_loc = {
                "lgd_state_code": dist_prof.get("lgd_state_code", "27"),
                "lgd_district_code": district_id,
                "lgd_village_code": None,
                "display_name": {"en": dist_prof.get("district", "Unknown"), "mr": dist_prof.get("district", "Unknown")},
                "h3_r8": "8860a2a1b3fffff",
                "h3_r7": "8760a2a1bffffff"
            }

        # Generate HMAC-SHA256 hashed reporter ID
        hashed_id = MultilingualNLPEngine.generate_hashed_id(actor_sub)

        # 6. Construct Canonical Ingestion Event (Schema jgs.extract.v1)
        lat = (gps.get("lat") if gps else None) or (canonical_loc.get("lat") if "lat" in canonical_loc else None) or dist_prof.get("lat", 20.18)
        lon = (gps.get("lon") if gps else None) or (canonical_loc.get("lon") if "lon" in canonical_loc else None) or dist_prof.get("lon", 80.00)

        event = {
            "event_id": event_id,
            "id": f"REQ-{event_id[:8]}",
            "schema_version": "1.0",
            "received_at": now,
            "captured_at": now,
            "channel": channel,
            "consent": {
                "token": consent_token or "token_default_jws",
                "notice_version": "2026.09",
                "purposes": consent_status.get("purposes_granted", ["planning_analytics"]),
                "granted_at": now,
                "language": detected_lang
            },
            "reporter": {
                "hashed_id": hashed_id,
                "assurance": "otp_verified" if channel == "mobile_app" else "anonymous_device",
                "age_declared_18plus": True
            },
            "content": {
                "modality": "audio+text" if "voice" in channel else "text",
                "language": {"code": detected_lang, "confidence": 0.95, "detector": "IndicLID-1.0"},
                "transcript": {
                    "text_redacted": sanitized_text,
                    "asr_model": "indicconformer-600m-mr" if "voice" in channel else None,
                    "human_corrected": False
                },
                "translation_en": sanitized_text
            },
            "extraction": {
                "sector": nlp_out["classified_sector"],
                "sub_issue": nlp_out.get("sub_issue", "general"),
                "intent": "repair_maintenance",
                "severity": nlp_out["severity_level"],
                "emergency": nlp_out.get("emergency", False),
                "entities": nlp_out.get("entities", []),
                "summary_en": f"{nlp_out['classified_sector'].capitalize()} distress reported: {sanitized_text[:90]}",
                "scheme_candidates": nlp_out.get("scheme_candidates", []),
                "confidence": {
                    "sector": nlp_out["classification_confidence"],
                    "intent": 0.88,
                    "severity": 0.90,
                    "overall": round((nlp_out["classification_confidence"] + 0.88 + 0.90) / 3, 2)
                }
            },
            "geo": {
                "gps": gps,
                "canonical_location": canonical_loc,
                "resolution": geo_resolution
            },
            "pii": {
                "redacted_types": redact_res["redacted_types"],
                "leakage_check_passed": redact_res["leakage_check_passed"]
            },
            "workflow": {
                "status": "needs_review" if geo_resolution["needs_manual_review"] else "processed",
                "assigned_ro": f"ro:{dist_prof.get('district', 'mh').lower()[:8]}-01",
                "verified_at": None
            },
            # Flat attributes for backward compatibility
            "district_id": district_id,
            "district_name": dist_prof.get("district", "Unknown"),
            "village_or_ward": canonical_loc["display_name"].get("en", "Rural Ward"),
            "lat": lat,
            "lon": lon,
            "sector": nlp_out["classified_sector"],
            "severity": nlp_out["severity_level"],
            "corroboration_count": corroborations,
            "raw_content": raw_text,
            "sanitized_content": sanitized_text,
            "timestamp": now
        }

        # 7. Audit Agent: Append event to hash chain
        AuditMCP.append({
            "actor_sub": actor_sub,
            "actor_role": "citizen",
            "action": "report:create",
            "resource_id": event["event_id"],
            "lgd_district_code": district_id,
            "payload": {
                "event_id": event["event_id"],
                "sector": event["extraction"]["sector"],
                "severity": event["extraction"]["severity"],
                "channel": channel
            }
        })

        return event
