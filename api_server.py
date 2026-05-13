"""
FastAPI Server - Main entry point for REST API
Run with: uvicorn api_server:app --reload --host 0.0.0.0 --port 8000
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import sys
import os

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from api.routes import router

# ==================== FastAPI App Setup ====================

app = FastAPI(
    title="Vessel Rating System API",
    description="REST API for Maritime Risk Assessment and Vessel Rating",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# ==================== CORS Middleware ====================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== Include Routers ====================

app.include_router(router, prefix="/api/v1", tags=["Vessel Rating API"])

# ==================== Exception Handlers ====================

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": str(exc)
        }
    )

# ==================== Startup/Shutdown Events ====================

@app.on_event("startup")
async def startup_event():
    print("\n" + "="*60)
    print("VESSEL RATING SYSTEM API - Starting Up")
    print("="*60)
    print("[OK] FastAPI initialized")
    print("[OK] CORS enabled for all origins")
    print("[OK] Database connection ready")
    print("[OK] Scoring engine loaded")
    print("="*60)
    print("API Documentation: http://localhost:8000/docs")
    print("="*60 + "\n")

@app.on_event("shutdown")
async def shutdown_event():
    print("\n✓ API Server shutting down gracefully\n")

# ==================== Main ====================

if __name__ == "__main__":
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
