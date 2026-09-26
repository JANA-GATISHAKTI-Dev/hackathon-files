"""
Spatial Hotspot & Demand-Deficit Disparity Engine.
Combines citizen feedback signals with sovereign demographics and infrastructure deficit indices.
Surfaces critical demand hotspots and infrastructure blind spots.
"""

from typing import List, Dict, Any
from backend.data.sovereign_data import DISTRICT_PROFILES

class SpatialHotspotEngine:
    """Surfaces acute infrastructure demand hotspots across districts and wards."""

    @staticmethod
    def calculate_hotspots(citizen_requests: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Groups requests by district and sector, calculates composite priority scores,
        and generates spatial demand hotspot polygons and metrics.
        """
        # Group requests by (district_id, sector)
        clusters: Dict[str, Dict[str, Any]] = {}

        for req in citizen_requests:
            dist_id = req.get("district_id")
            sector = req.get("sector", "roads")
            key = f"{dist_id}::{sector}"

            if key not in clusters:
                clusters[key] = {
                    "district_id": dist_id,
                    "sector": sector,
                    "requests": [],
                    "total_corroborations": 0,
                    "max_severity": 0,
                    "severity_sum": 0,
                    "lats": [],
                    "lons": [],
                    "sample_excerpts": []
                }

            c = clusters[key]
            c["requests"].append(req)
            corrob = req.get("corroboration_count", 1)
            severity = req.get("severity", 3)
            c["total_corroborations"] += corrob
            c["max_severity"] = max(c["max_severity"], severity)
            c["severity_sum"] += (severity * corrob)
            c["lats"].append(req.get("lat", 0.0))
            c["lons"].append(req.get("lon", 0.0))
            
            excerpt = req.get("english_translation") or req.get("raw_content", "")
            if len(excerpt) > 100:
                excerpt = excerpt[:97] + "..."
            c["sample_excerpts"].append(excerpt)

        hotspot_results = []
        hotspot_id_counter = 1

        for key, c in clusters.items():
            dist_id = c["district_id"]
            sector = c["sector"]
            dist_profile = DISTRICT_PROFILES.get(dist_id, {})

            if not dist_profile:
                continue

            # Compute centroid lat/lon
            avg_lat = sum(c["lats"]) / len(c["lats"]) if c["lats"] else dist_profile.get("lat", 0.0)
            avg_lon = sum(c["lons"]) / len(c["lons"]) if c["lons"] else dist_profile.get("lon", 0.0)

            # Retrieve infrastructure deficit for this sector
            sector_deficit = dist_profile.get("infrastructure_deficits", {}).get(sector, 50.0)
            
            # Demographic Vulnerability Index (0 to 100)
            poverty_rate = dist_profile.get("poverty_rate", 30.0)
            tribal_rate = dist_profile.get("tribal_percentage", 10.0)
            rural_rate = dist_profile.get("rural_percentage", 70.0)
            vulnerability_index = (poverty_rate * 0.5) + (tribal_rate * 0.3) + (rural_rate * 0.2)

            # Citizen demand signal weight
            request_count = len(c["requests"])
            total_corroborations = c["total_corroborations"]
            weighted_severity = c["severity_sum"] / max(1, total_corroborations)

            # Demand-Deficit Disparity Index (DDDI) (0 - 100 scale)
            # 40% citizen ground demand + 35% official infrastructure deficit + 25% socioeconomic vulnerability
            demand_score = min(100.0, (request_count * 15.0) + (total_corroborations * 0.4) * (weighted_severity / 5.0))
            dddi_score = round(
                (0.40 * demand_score) +
                (0.35 * sector_deficit) +
                (0.25 * vulnerability_index),
                1
            )

            # Check if active government schemes exist and if they are stalled/insufficient
            ongoing_schemes = dist_profile.get("ongoing_schemes", [])
            relevant_schemes = [s for s in ongoing_schemes if sector.lower() in s.get("scheme", "").lower()]
            is_blind_spot = False
            if dddi_score > 70 and (not relevant_schemes or any(s.get("status") in ["Critical Gap", "Stalled", "Delayed", "Behind Schedule"] for s in relevant_schemes)):
                is_blind_spot = True

            # Estimated affected population in proximity
            district_pop = dist_profile.get("population", 500000)
            estimated_affected_pop = int(min(district_pop * 0.4, max(5000, total_corroborations * 350)))

            hotspot_results.append({
                "hotspot_id": f"HOTSPOT-{dist_profile.get('country_code', 'IN')}-{hotspot_id_counter:03d}",
                "district_id": dist_id,
                "district_name": dist_profile.get("district", "Unknown"),
                "state_or_province": dist_profile.get("state", ""),
                "country": dist_profile.get("country", "India"),
                "country_code": dist_profile.get("country_code", "IN"),
                "sector": sector,
                "lat": round(avg_lat, 4),
                "lon": round(avg_lon, 4),
                "radius_km": round(max(3.0, min(25.0, request_count * 4.5)), 1),
                "disparity_score": dddi_score,
                "urgency_level": "CRITICAL" if dddi_score >= 78 else "HIGH" if dddi_score >= 60 else "MODERATE",
                "request_count": request_count,
                "total_corroborations": total_corroborations,
                "sector_deficit_index": sector_deficit,
                "vulnerability_index": round(vulnerability_index, 1),
                "estimated_affected_population": estimated_affected_pop,
                "is_government_blind_spot": is_blind_spot,
                "sample_testimonies": c["sample_excerpts"][:3]
            })
            hotspot_id_counter += 1

        # Sort hotspots by disparity score descending (most acute first)
        hotspot_results.sort(key=lambda x: x["disparity_score"], reverse=True)
        return hotspot_results
