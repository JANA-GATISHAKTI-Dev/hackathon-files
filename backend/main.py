"""
FastAPI Sovereign REST API Server for JANA-GATISHAKTI / CIVIC-PULSE BRICS.
Provides high-performance, DPG-compliant endpoints for citizen voice ingestion,
spatial demand hotspot analytics, AI project recommendations, and policy simulation.
"""

from fastapi import FastAPI, Query, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
import os

from backend.services.store import STORE
from backend.services.impact_tracker import ImpactTrackerEngine

app = FastAPI(
    title="JANA-GATISHAKTI / CIVIC-PULSE BRICS DPI Platform",
    description="A Digital Public Good for Multilingual Citizen Voice Aggregation, Spatial Need Hotspot Discovery & Evidence-Based Capital Infrastructure Allocation.",
    version="2.0.0"
)

# Enable CORS for sovereign cross-departmental integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Input Models
class CitizenFeedbackSubmission(BaseModel):
    raw_text: str = Field(..., description="Raw citizen voice transcript or message text")
    district_id: str = Field(..., description="District code e.g. IN-DIST-01, IN-DIST-02, etc.")
    channel: str = Field(default="voice_ivr", description="voice_ivr, whatsapp, sms, gp_kiosk, portal")
    corroboration_count: int = Field(default=1, description="Number of community members co-signing")

class BudgetSimulationRequest(BaseModel):
    total_budget_cr: float = Field(default=100.0, description="Total capital expenditure budget in INR Crores")
    allocations: Dict[str, float] = Field(
        default={
            "water": 30.0,
            "roads": 25.0,
            "power": 15.0,
            "health": 20.0,
            "telecom": 5.0,
            "sanitation": 5.0
        },
        description="Sector allocation percentages summing to 100"
    )

# --- API ENDPOINTS ---

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "JANA-GATISHAKTI DPI",
        "dpg_standard_aligned": True,
        "active_records_count": len(STORE.requests)
    }

@app.get("/api/districts")
async def get_districts(country: Optional[str] = Query(None, description="Country filter: IN, BR, ZA")):
    return STORE.get_districts(country_code=country)

@app.get("/api/feedback")
async def get_feedback(
    country: Optional[str] = Query(None, description="Country filter: IN, BR, ZA"),
    sector: Optional[str] = Query(None, description="Sector: water, power, roads, health, telecom, sanitation, all")
):
    return STORE.get_requests(country_code=country, sector=sector)

@app.post("/api/feedback/submit")
async def submit_citizen_feedback(submission: CitizenFeedbackSubmission):
    if not submission.raw_text.strip():
        raise HTTPException(status_code=400, detail="Feedback text cannot be empty.")
    
    record = STORE.add_citizen_request(
        raw_text=submission.raw_text,
        district_id=submission.district_id,
        channel=submission.channel,
        corroborations=submission.corroboration_count
    )
    return {
        "message": "Citizen request successfully ingested, PII scrubbed, and geolocated into DPI grid.",
        "processed_record": record,
        "hotspots_updated_count": len(STORE.get_hotspots())
    }

@app.get("/api/hotspots")
async def get_hotspots(country: Optional[str] = Query(None, description="Country filter: IN, BR, ZA")):
    return STORE.get_hotspots(country_code=country)

@app.get("/api/recommendations")
async def get_recommendations(country: Optional[str] = Query(None, description="Country filter: IN, BR, ZA")):
    return STORE.get_recommendations(country_code=country)

@app.post("/api/simulate-budget")
async def simulate_budget(req: BudgetSimulationRequest):
    hotspots = STORE.get_hotspots()
    result = ImpactTrackerEngine.simulate_budget_allocation(
        total_budget_cr=req.total_budget_cr,
        allocations=req.allocations,
        hotspots=hotspots
    )
    return result

@app.get("/api/audits")
async def get_citizen_audits():
    return {
        "citizen_audits": STORE.audit_records,
        "ghost_asset_sentinel_status": "ACTIVE",
        "critical_alerts_count": sum(1 for a in STORE.audit_records if a.get("investigation_flag"))
    }

# --- DPG ALLIANCE & OPEN STANDARDS ENDPOINTS ---

@app.get("/api/dpg/compliance")
async def dpg_compliance():
    return STORE.get_dpg_compliance_report()

@app.get("/api/dpg/geojson")
async def export_geojson():
    return STORE.export_geojson()

@app.get("/api/dpg/ocds")
async def export_ocds():
    return STORE.export_ocds()

# --- SERVE FRONTEND STATIC FILES ---
frontend_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend")
static_path = os.path.join(frontend_path, "static")

if os.path.exists(static_path):
    app.mount("/static", StaticFiles(directory=static_path), name="static")

@app.get("/")
async def serve_index():
    index_file = os.path.join(frontend_path, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"message": "Jana-GatiShakti API is running. Frontend index.html not yet initialized."}
