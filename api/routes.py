"""
FastAPI Routes - Vessel Rating System API Endpoints
"""

from fastapi import APIRouter, HTTPException, Query, Path
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from sqlalchemy import text
import json

from api_integration.providers import (
    AISProvider, SanctionsProvider, WeatherProvider, MaritimeDBProvider
)
from scoring_engine.engine import ScoringEngine
from db.models import Session, Vessel, ModuleScore
from storage.sources import SOURCE_CLOUD, SOURCE_LOCAL, get_storage_manager
from utils.helpers import format_json_report

router = APIRouter()

# ==================== Pydantic Models ====================

class VesselInput(BaseModel):
    """Input model for vessel analysis"""
    vessel_name: str = Field(..., min_length=1, max_length=100, example="Ever Given")
    imo_number: str = Field(..., min_length=5, max_length=10, example="9860910")
    storage_source: str = Field(
        SOURCE_LOCAL,
        pattern="^(local_storage|cloud)$",
        example="local_storage",
        description="Storage source to pull vessel data from: local_storage or cloud"
    )
    cloud_location: Optional[str] = Field(
        None,
        example="https://storage.example.com/vessels.json",
        description="Cloud JSON/CSV URL or synced cloud folder path when storage_source is cloud"
    )

class ModuleScoreModel(BaseModel):
    """Model for individual module scores"""
    module_name: str
    score: float
    weight: float
    weighted_score: float
    details: Optional[Dict[str, Any]] = None

class AnalysisResult(BaseModel):
    """Model for final analysis result"""
    vessel_name: str
    imo_number: str
    analysis_date: str
    final_rating: float
    band_rating: int
    risk_level: str
    module_scores: list[ModuleScoreModel]
    critical_alerts: list[str]
    recommendation: str
    processing_time_seconds: float

class BulkAnalysisRequest(BaseModel):
    """Model for bulk analysis"""
    vessels: list[VesselInput] = Field(..., min_items=1, max_items=100)

class HistoryResponse(BaseModel):
    """Model for analysis history"""
    vessel_name: str
    imo_number: str
    total_analyses: int
    latest_analysis_date: str
    latest_rating: float
    ratings_history: list[Dict[str, Any]]

# ==================== API Endpoints ====================

@router.get("/", tags=["Info"])
async def root():
    """API Root - System Information"""
    return {
        "system": "Vessel Rating System API",
        "version": "1.0.0",
        "status": "operational",
        "endpoints": {
            "health": "/health",
            "analyze": "/analyze",
            "batch-analyze": "/batch-analyze",
            "history": "/history",
            "modules": "/modules",
            "docs": "/docs"
        }
    }

@router.get("/health", tags=["Info"])
async def health_check():
    """Health Check - System Status"""
    try:
        session = Session()
        # Test database connection
        session.execute(text("SELECT 1"))
        session.close()
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "components": {
                "database": "connected",
                "api": "operational",
                "scoring_engine": "ready"
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Service Unavailable: {str(e)}"
        )

@router.post("/analyze", response_model=AnalysisResult, tags=["Analysis"])
async def analyze_vessel(vessel_input: VesselInput):
    """
    Analyze a single vessel and get comprehensive risk rating
    
    **Parameters:**
    - `vessel_name`: Name of the vessel (e.g., "Ever Given")
    - `imo_number`: IMO number (e.g., "9860910")
    
    **Returns:**
    - Final rating (0-9 scale)
    - Risk level classification
    - Individual module scores
    - Critical alerts if any
    - Recommendation
    """
    import time
    start_time = time.time()
    
    try:
        storage_manager = get_storage_manager()
        vessel_data = storage_manager.fetch_vessel_data(
            vessel_input.vessel_name,
            vessel_input.imo_number,
            source=vessel_input.storage_source,
            cloud_location=vessel_input.cloud_location,
        )

        # Generate full report (calculates all module scores + final rating)
        scoring_engine = ScoringEngine()
        report = scoring_engine.generate_report(
            vessel_input.vessel_name,
            vessel_input.imo_number,
            vessel_data
        )

        scoring = report.get('scoring', {})
        final_rating = scoring.get('final_band', 0.0)

        # Store in database
        session = Session()
        vessel = Vessel(
            vessel_name=vessel_input.vessel_name,
            imo_number=vessel_input.imo_number,
            last_analyzed=datetime.now(),
            latest_rating=final_rating
        )
        session.add(vessel)
        session.commit()

        # Prepare module scores
        module_scores = []
        for mod in report.get('module_breakdown', []):
            module_scores.append(ModuleScoreModel(
                module_name=mod.get('code', mod.get('module', '')),
                score=mod.get('score', 0),
                weight=mod.get('weight_percent', 0),
                weighted_score=mod.get('weighted_contribution', 0),
                details={'band': mod.get('band', 0)}
            ))

        alerts = report.get('alerts', [])
        critical_alerts = [a['message'] for a in alerts if a.get('severity') == 'CRITICAL']

        processing_time = time.time() - start_time

        return AnalysisResult(
            vessel_name=vessel_input.vessel_name,
            imo_number=vessel_input.imo_number,
            analysis_date=datetime.now().isoformat(),
            final_rating=final_rating,
            band_rating=int(final_rating),
            risk_level=scoring.get('risk_level', 'Unknown'),
            module_scores=module_scores,
            critical_alerts=critical_alerts,
            recommendation=report.get('summary', 'No specific recommendation'),
            processing_time_seconds=round(processing_time, 2)
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Analysis failed: {str(e)}"
        )

@router.post("/batch-analyze", tags=["Analysis"])
async def batch_analyze(request: BulkAnalysisRequest):
    """
    Analyze multiple vessels in a single request
    
    **Parameters:**
    - `vessels`: List of vessel objects with vessel_name and imo_number
    
    **Returns:**
    - Array of analysis results
    - Summary statistics
    - Bulk processing time
    """
    import time
    start_time = time.time()
    
    results = []
    errors = []
    
    for vessel_input in request.vessels:
        try:
            # Reuse the analyze function
            result = await analyze_vessel(vessel_input)
            results.append(result)
        except Exception as e:
            errors.append({
                "vessel": vessel_input.vessel_name,
                "imo": vessel_input.imo_number,
                "error": str(e)
            })
    
    processing_time = time.time() - start_time
    
    return {
        "total_vessels": len(request.vessels),
        "successful": len(results),
        "failed": len(errors),
        "processing_time_seconds": round(processing_time, 2),
        "results": results,
        "errors": errors if errors else None,
        "summary": {
            "average_rating": round(sum(r.final_rating for r in results) / len(results), 2) if results else 0,
            "high_risk_count": len([r for r in results if r.risk_level == "Critical"]),
            "medium_risk_count": len([r for r in results if r.risk_level == "High"]),
            "low_risk_count": len([r for r in results if r.risk_level in ["Medium", "Low"]])
        }
    }

@router.get("/history/{imo_number}", response_model=HistoryResponse, tags=["History"])
async def get_vessel_history(imo_number: str = Path(..., min_length=5, max_length=10)):
    """
    Get analysis history for a specific vessel by IMO number
    
    **Parameters:**
    - `imo_number`: IMO number of the vessel
    
    **Returns:**
    - Total analyses performed
    - Latest analysis date and rating
    - Historical ratings over time
    """
    try:
        session = Session()
        
        # Get vessel
        vessel = session.query(Vessel).filter(
            Vessel.imo_number == imo_number
        ).first()
        
        if not vessel:
            raise HTTPException(
                status_code=404,
                detail=f"No vessel found with IMO: {imo_number}"
            )
        
        # Get module scores history
        scores = session.query(ModuleScore).filter(
            ModuleScore.vessel_id == vessel.id
        ).all()
        
        ratings_history = [
            {
                "date": score.calculated_at.isoformat(),
                "module": score.module_name,
                "band_score": score.band_score,
                "raw_score": score.raw_score,
            }
            for score in sorted(scores, key=lambda x: x.calculated_at)
        ]
        
        session.close()
        
        return HistoryResponse(
            vessel_name=vessel.vessel_name,
            imo_number=vessel.imo_number,
            total_analyses=len(scores),
            latest_analysis_date=vessel.last_analyzed.isoformat() if vessel.last_analyzed else "Never",
            latest_rating=vessel.latest_rating or 0,
            ratings_history=ratings_history
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@router.get("/modules", tags=["Info"])
async def get_modules_info():
    """
    Get information about all scoring modules
    
    **Returns:**
    - Module names and descriptions
    - Weights and thresholds
    - Scoring criteria
    """
    return {
        "modules": [
            {
                "id": 1,
                "name": "General Information",
                "weight": 10,
                "description": "Vessel class, age, flag state, port state control history",
                "factors": ["vessel_class", "age", "flag_state", "psc_history"]
            },
            {
                "id": 2,
                "name": "Ownership Information",
                "weight": 20,
                "description": "Beneficial owners, company history, beneficial owner sanctions",
                "factors": ["owner_profile", "company_sanctions", "ownership_changes"]
            },
            {
                "id": 3,
                "name": "AIS Information",
                "weight": 15,
                "description": "Automatic Identification System signal patterns and anomalies",
                "factors": ["ais_signal_strength", "route_anomalies", "spoofing_detection"]
            },
            {
                "id": 4,
                "name": "Risk & Compliance",
                "weight": 30,
                "description": "Sanctions status, compliance violations, incident history (CRITICAL)",
                "factors": ["sanctions_status", "violations", "incident_history", "detention_history"]
            },
            {
                "id": 5,
                "name": "Environmental & Voyage",
                "weight": 15,
                "description": "Route information, environmental compliance, cargo type",
                "factors": ["route_risk", "environmental_violations", "cargo_hazard_level"]
            },
            {
                "id": 6,
                "name": "Legal & Documentation",
                "weight": 10,
                "description": "Certification status, insurance, documentation completeness",
                "factors": ["certification_status", "insurance_valid", "doc_completeness"]
            }
        ],
        "total_weight": 100,
        "rating_scale": {
            "min": 0,
            "max": 9,
            "type": "band rating",
            "risk_levels": ["Minimal (0)", "Low (1-2)", "Medium (3-5)", "High (6-7)", "Critical (8-9)"]
        }
    }

@router.get("/stats", tags=["Statistics"])
async def get_statistics():
    """
    Get system statistics
    
    **Returns:**
    - Total vessels analyzed
    - Average rating
    - Risk distribution
    """
    try:
        session = Session()
        
        vessels = session.query(Vessel).all()
        total_vessels = len(vessels)
        
        if total_vessels == 0:
            return {
                "total_vessels_analyzed": 0,
                "average_rating": 0,
                "risk_distribution": {},
                "last_analysis": None
            }
        
        avg_rating = sum(v.latest_rating for v in vessels if v.latest_rating) / total_vessels
        
        # Calculate risk distribution based on band_score thresholds
        risk_dist = {
            "critical": len([v for v in vessels if (v.latest_rating or 0) < 2]),
            "high": len([v for v in vessels if 2 <= (v.latest_rating or 0) < 4]),
            "medium": len([v for v in vessels if 4 <= (v.latest_rating or 0) < 6]),
            "low": len([v for v in vessels if 6 <= (v.latest_rating or 0) < 8]),
            "minimal": len([v for v in vessels if (v.latest_rating or 0) >= 8]),
        }

        dated = [v for v in vessels if v.last_analyzed]
        latest = max(dated, key=lambda v: v.last_analyzed).last_analyzed if dated else None
        
        session.close()
        
        return {
            "total_vessels_analyzed": total_vessels,
            "total_analyses": total_vessels,
            "average_rating": round(avg_rating, 2),
            "risk_distribution": risk_dist,
            "last_analysis": latest.isoformat() if latest else None
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
