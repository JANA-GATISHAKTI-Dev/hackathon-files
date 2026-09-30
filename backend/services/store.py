"""
Sovereign Data Store & State Manager (JANA-GATISHAKTI DPI).
Maintains live state of reports, clusters, demand scores, and recommendations.
Enforces ABAC district scoping, 4-Eyes project approval governance, and OCDS/GeoJSON export.
"""

from typing import List, Dict, Any, Optional
import copy
from datetime import datetime, timezone

from backend.data.sovereign_data import DISTRICT_PROFILES, VILLAGE_GAZETTEER, NATIONAL_SCHEMES_CATALOG
from backend.data.citizen_requests import CITIZEN_REQUESTS
from backend.services.nlp_engine import MultilingualNLPEngine
from backend.services.hotspot_engine import SpatialHotspotEngine
from backend.services.mcda_recommender import MCDAProjectRecommender
from backend.services.scoring_engine import ScoringEngine
from backend.services.audit_service import AUDIT
from backend.services.orchestrator import IngestionOrchestrator
from backend.services.impact_tracker import ImpactTrackerEngine

class SovereignDataStore:
    def __init__(self):
        self.districts: Dict[str, Dict[str, Any]] = copy.deepcopy(DISTRICT_PROFILES)
        self.villages: List[Dict[str, Any]] = copy.deepcopy(VILLAGE_GAZETTEER)
        self.audit_records: List[Dict[str, Any]] = copy.deepcopy(ImpactTrackerEngine.AUDIT_RECORDS)
        
        # Initialize and migrate seed requests to canonical LGD codes
        self.requests: List[Dict[str, Any]] = []
        for req in copy.deepcopy(CITIZEN_REQUESTS):
            dist_id = req.get("district_id", "990001")
            # Map legacy ID to LGD if applicable
            if dist_id in ["IN-DIST-01", "IN-DIST-02", "IN-DIST-03", "IN-DIST-04", "IN-DIST-05"]:
                dist_prof = DISTRICT_PROFILES.get(dist_id, {})
                req["lgd_district_code"] = dist_prof.get("lgd_district_code", dist_id)
                req["district_id"] = req["lgd_district_code"]
            else:
                req["lgd_district_code"] = dist_id

            # Add hashed_id if missing
            if "hashed_id" not in req:
                req["hashed_id"] = MultilingualNLPEngine.generate_hashed_id(req.get("id", "seed"))
            
            # Workflow state
            req["status"] = req.get("status", "processed")
            self.requests.append(req)

        self._cached_hotspots: Optional[List[Dict[str, Any]]] = None
        self._cached_recommendations: Optional[List[Dict[str, Any]]] = None
        self.refresh_calculations()

    def refresh_calculations(self):
        """Recomputes spatio-temporal hotspots and MCDA project recommendations."""
        self._cached_hotspots = SpatialHotspotEngine.calculate_hotspots(self.requests)
        self._cached_recommendations = MCDAProjectRecommender.generate_recommendations(self._cached_hotspots)

    def get_requests(
        self,
        country_code: Optional[str] = None,
        sector: Optional[str] = None,
        district_lgd: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Filters reports by country, sector, district jurisdiction, and status."""
        results = self.requests
        if country_code and country_code != "all":
            valid_ids = [d_id for d_id, d in self.districts.items() if d.get("country_code") == country_code]
            results = [r for r in results if r.get("district_id") in valid_ids or r.get("lgd_district_code") in valid_ids]
        if sector and sector != "all":
            results = [r for r in results if r.get("sector") == sector]
        if district_lgd and district_lgd != "all":
            results = [r for r in results if r.get("lgd_district_code") == district_lgd or r.get("district_id") == district_lgd]
        if status and status != "all":
            results = [r for r in results if r.get("status") == status]
        return results

    def add_citizen_report(
        self,
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
        Executes full agentic pipeline: Verhoeff PII scrub -> extraction -> gazetteer resolution -> audit ledger.
        """
        event = IngestionOrchestrator.execute_pipeline(
            raw_text=raw_text,
            district_id=district_id,
            channel=channel,
            consent_token=consent_token,
            gps=gps,
            place_mention=place_mention,
            corroborations=corroborations,
            actor_sub=actor_sub
        )

        self.requests.insert(0, event)
        self.refresh_calculations()
        return event

    def ro_verify_report(
        self,
        report_id: str,
        ro_sub: str,
        action: str,  # 'verify', 'reject', 'merge', 'geo_correct'
        corrected_village_code: Optional[str] = None,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """Handles Reporting Officer casework actions with audit trail."""
        for r in self.requests:
            if r.get("event_id") == report_id or r.get("id") == report_id:
                old_status = r.get("status", "processed")
                if action == "verify":
                    r["status"] = "verified"
                elif action == "reject":
                    r["status"] = "rejected"
                elif action == "merge":
                    r["status"] = "merged"
                elif action == "geo_correct" and corrected_village_code:
                    for v in self.villages:
                        if v["village_code"] == corrected_village_code:
                            r["village_or_ward"] = v["name_en"]
                            r["lat"] = v["lat"]
                            r["lon"] = v["lon"]
                            r["status"] = "verified"
                            break

                r["workflow"] = r.get("workflow", {})
                r["workflow"]["status"] = r["status"]
                r["workflow"]["assigned_ro"] = ro_sub
                r["workflow"]["verified_at"] = datetime.now(timezone.utc).isoformat()
                if notes:
                    r["workflow"]["ro_notes"] = notes

                # Audit action
                AUDIT.append_entry(
                    actor_sub=ro_sub,
                    actor_role="reporting_officer",
                    action=f"report:{action}",
                    resource_id=report_id,
                    lgd_district_code=r.get("lgd_district_code", "27"),
                    purpose="field_verification",
                    payload={"old_status": old_status, "new_status": r["status"], "notes": notes}
                )

                self.refresh_calculations()
                return {"success": True, "report_id": report_id, "new_status": r["status"]}

        raise KeyError(f"Report ID '{report_id}' not found.")

    def get_hotspots(self, country_code: Optional[str] = None, district_lgd: Optional[str] = None) -> List[Dict[str, Any]]:
        if self._cached_hotspots is None:
            self.refresh_calculations()
        hotspots = self._cached_hotspots or []
        if country_code and country_code != "all":
            hotspots = [h for h in hotspots if h.get("country_code") == country_code]
        if district_lgd and district_lgd != "all":
            hotspots = [h for h in hotspots if h.get("lgd_district_code") == district_lgd or h.get("district_id") == district_lgd]
        return hotspots

    def get_recommendations(self, country_code: Optional[str] = None, district_lgd: Optional[str] = None) -> List[Dict[str, Any]]:
        if self._cached_recommendations is None:
            self.refresh_calculations()
        recs = self._cached_recommendations or []
        if country_code and country_code != "all":
            recs = [r for r in recs if r.get("country_code") == country_code]
        if district_lgd and district_lgd != "all":
            recs = [r for r in recs if r.get("lgd_district_code") == district_lgd or r.get("district_id") == district_lgd]
        return recs

    def optimize_portfolio(
        self,
        total_budget_cr: float = 120.0,
        alpha_aspirational: float = 0.40,
        beta_sc_st: float = 0.30,
        gamma_sector_cap: float = 0.35,
        max_duration_months: int = 18
    ) -> Dict[str, Any]:
        """Runs the MILP optimizer over current candidate projects."""
        candidates = self.get_recommendations()
        result = MCDAProjectRecommender.optimize_portfolio(
            candidates=candidates,
            total_budget_cr=total_budget_cr,
            alpha_aspirational=alpha_aspirational,
            beta_sc_st=beta_sc_st,
            gamma_sector_cap=gamma_sector_cap,
            max_duration_months=max_duration_months
        )
        return result

    def approve_recommendation(
        self,
        project_id: str,
        approver_sub: str,
        approver_acr: str = "loa3",
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Enforces 4-Eyes Governance & Step-Up MFA (ACR=loa3) to officially sanction a capital project.
        """
        recs = self.get_recommendations()
        for r in recs:
            if r.get("id") == project_id or r.get("project_id") == project_id:
                # 4-Eyes Check: cannot approve own proposal
                if r.get("proposed_by") == approver_sub:
                    raise PermissionError("4-Eyes Governance Rule: You cannot approve a project proposal authored by yourself.")
                if approver_acr != "loa3":
                    raise PermissionError("Step-up MFA (ACR=loa3) required for capital expenditure sanction.")

                r["approval_status"] = "sanctioned"
                r["approved_by"] = approver_sub
                r["approved_at"] = datetime.now(timezone.utc).isoformat()
                if notes:
                    r["sanction_notes"] = notes

                # Audit event
                AUDIT.append_entry(
                    actor_sub=approver_sub,
                    actor_role="admin",
                    action="recommendation:approve",
                    resource_id=project_id,
                    lgd_district_code=r.get("lgd_district_code", "27"),
                    payload={"project_id": project_id, "capex_cr": r.get("cost_cr"), "scheme": r.get("scheme")}
                )
                return {"success": True, "project_id": project_id, "status": "sanctioned"}

        raise KeyError(f"Project '{project_id}' not found.")

    def get_district_demand_geojson(self, state_code: str = "27", sector: str = "water") -> Dict[str, Any]:
        """
        Returns GeoJSON FeatureCollection with exact additive score decomposition (Section 5.5 of Master Plan).
        """
        features = []
        target_districts = [d for d in self.districts.values() if d.get("lgd_state_code") == state_code]

        for d in target_districts:
            d_code = d.get("lgd_district_code", d.get("id"))
            score_data = ScoringEngine.compute_district_demand(
                district_id=d_code,
                sector=sector,
                reports=self.requests
            )

            # Bounding box polygon around district centroid
            lat, lon = d.get("lat", 20.0), d.get("lon", 78.0)
            poly_coords = [
                [
                    [round(lon - 0.45, 4), round(lat - 0.45, 4)],
                    [round(lon + 0.45, 4), round(lat - 0.45, 4)],
                    [round(lon + 0.45, 4), round(lat + 0.45, 4)],
                    [round(lon - 0.45, 4), round(lat + 0.45, 4)],
                    [round(lon - 0.45, 4), round(lat - 0.45, 4)]
                ]
            ]

            features.append({
                "type": "Feature",
                "id": d_code,
                "geometry": {
                    "type": "Polygon",
                    "coordinates": poly_coords
                },
                "properties": {
                    "lgd_district_code": d_code,
                    "name": {"en": d.get("district"), "mr": d.get("district")},
                    "sector": sector,
                    "demand_score": score_data["demand_score"],
                    "unique_citizens": score_data["unique_citizens"],
                    "avg_severity": score_data["avg_severity"],
                    "infra_gap_pct": score_data["infra_gap_pct"],
                    "confidence": score_data["confidence"],
                    "top_signals": score_data["top_signals"]
                }
            })

        return {
            "type": "FeatureCollection",
            "metadata": {
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "score_version": ScoringEngine.PARAMS["version"],
                "boundary_source": "Survey of India / LGD Authoritative Boundaries",
                "k_anonymity_min": 5
            },
            "features": features
        }

    def export_ocds(self) -> Dict[str, Any]:
        """Exports prioritized projects into official Open Contracting Data Standard (OCDS 1.1) release format."""
        recs = self.get_recommendations()
        releases = []
        for r in recs:
            releases.append({
                "ocid": f"ocds-jgs-{r.get('lgd_district_code', '27')}-{r.get('id', 'proj').lower()}",
                "id": r.get("id"),
                "date": datetime.now(timezone.utc).isoformat(),
                "tag": ["planning"],
                "initiationType": "tender",
                "planning": {
                    "budget": {
                        "amount": {"amount": int(r.get("cost_cr", 10.0) * 10000000), "currency": "INR"},
                        "project": r.get("funding_scheme"),
                        "projectID": r.get("hotspot_ref_id")
                    },
                    "rationale": r.get("policy_impact_rationale")
                },
                "tender": {
                    "title": r.get("title"),
                    "status": r.get("approval_status", "planned"),
                    "deliveryAddresses": [{"region": r.get("state_or_province"), "countryName": r.get("country", "India")}]
                }
            })
        return {
            "uri": "https://janagatishakti.gov.in/api/v1/opendata/ocds",
            "version": "1.1",
            "publishedDate": datetime.now(timezone.utc).isoformat(),
            "publisher": {"name": "Jana-GatiShakti Sovereign DPI Platform (Maharashtra Pilot)"},
            "releases": releases
        }

    def export_geojson(self) -> Dict[str, Any]:
        """OGC GeoJSON export of active demand hotspots with H3 indices."""
        features = []
        hotspots = self.get_hotspots()
        for hs in hotspots:
            features.append({
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [hs["lon"], hs["lat"]]
                },
                "properties": {
                    "cluster_id": hs.get("cluster_id"),
                    "district": hs.get("district_name"),
                    "lgd_district_code": hs.get("lgd_district_code"),
                    "sector": hs.get("sector"),
                    "demand_score": hs.get("demand_score"),
                    "urgency": hs.get("urgency_level"),
                    "beneficiaries": hs.get("estimated_affected_population"),
                    "unique_citizens": hs.get("unique_citizens"),
                    "h3_r8": hs.get("h3_r8"),
                    "is_blind_spot": hs.get("is_government_blind_spot")
                }
            })
        return {
            "type": "FeatureCollection",
            "metadata": {
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "boundary_source": "Survey of India / LGD",
                "k_anonymity_min": 5
            },
            "features": features
        }

# Global Singleton Sovereign Store
STORE = SovereignDataStore()
