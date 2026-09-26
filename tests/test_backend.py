"""
Automated Verification Suite for JANA-GATISHAKTI / CIVIC-PULSE BRICS.
Tests NLP PII redaction, spatial hotspot generation, MCDA project prioritization, and budget simulation.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.services.nlp_engine import MultilingualNLPEngine
from backend.services.store import STORE
from backend.services.impact_tracker import ImpactTrackerEngine

def test_nlp_pii_redaction():
    text_with_pii = "मेरा नाम रमेश कुमार है, मोबाइल 9876543210 और आधार 4521 8901 2345 है। हमारे गांव में जल जीवन मिशन का पानी नहीं आ रहा है।"
    result = MultilingualNLPEngine.process_incoming_request(text_with_pii, "IN-DIST-02", "voice_ivr", 25)
    
    assert "[REDACTED_AADHAAR]" in result["sanitized_text"], "Aadhaar number was not redacted!"
    assert "[REDACTED_PHONE]" in result["sanitized_text"], "Phone number was not redacted!"
    assert result["classified_sector"] == "water", f"Expected 'water', got {result['classified_sector']}"
    assert result["severity_level"] >= 2, "Expected severity >= 2"
    print("PASS: NLP PII Redaction and Sector Classification test passed.")

def test_hotspot_generation():
    hotspots = STORE.get_hotspots()
    assert len(hotspots) > 0, "No hotspots generated!"
    top_hs = hotspots[0]
    assert "disparity_score" in top_hs, "Missing disparity score!"
    assert "estimated_affected_population" in top_hs, "Missing affected population!"
    print(f"PASS: Generated {len(hotspots)} hotspots. Top hotspot in {top_hs['district_name']} with disparity {top_hs['disparity_score']}.")

def test_mcda_recommendations():
    recs = STORE.get_recommendations()
    assert len(recs) > 0, "No recommendations generated!"
    top_rec = recs[0]
    assert "estimated_capex_cr_inr" in top_rec, "Missing Capex estimate!"
    assert "mcda_priority_score" in top_rec, "Missing MCDA score!"
    print(f"PASS: Generated {len(recs)} prioritized projects. Top: '{top_rec['project_title']}' with score {top_rec['mcda_priority_score']} and Capex INR {top_rec['estimated_capex_cr_inr']} Cr.")

def test_budget_simulator():
    hotspots = STORE.get_hotspots()
    sim = ImpactTrackerEngine.simulate_budget_allocation(
        total_budget_cr=120.0,
        allocations={"water": 35.0, "roads": 25.0, "power": 15.0, "health": 15.0, "telecom": 5.0, "sanitation": 5.0},
        hotspots=hotspots
    )
    assert sim["hotspots_resolved_count"] > 0, "Expected resolved hotspots!"
    assert sim["total_beneficiaries_reached"] > 0, "Expected reached beneficiaries!"
    print(f"PASS: Budget simulation passed. Resolved {sim['hotspots_resolved_count']} hotspots, reaching {sim['total_beneficiaries_reached']} citizens.")

def test_dpg_compliance():
    rep = STORE.get_dpg_compliance_report()
    assert len(rep["standards_audit"]) == 9, "Expected 9 DPGA indicators!"
    geojson = STORE.export_geojson()
    assert geojson["type"] == "FeatureCollection", "Expected GeoJSON FeatureCollection!"
    ocds = STORE.export_ocds()
    assert "releases" in ocds, "Expected OCDS releases!"
    print("PASS: DPG Compliance & Open Standards export verified.")

if __name__ == "__main__":
    test_nlp_pii_redaction()
    test_hotspot_generation()
    test_mcda_recommendations()
    test_budget_simulator()
    test_dpg_compliance()
    print("\nALL 5 CORE TESTS PASSED SUCCESSFULLY!")
