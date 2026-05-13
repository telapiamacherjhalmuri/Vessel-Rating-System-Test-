"""
Configuration for Vessel Rating System
"""

import os
from datetime import datetime

# System Configuration
PROJECT_NAME = "Vessel Rating System"
VERSION = "1.0.0"
DATABASE_URL = "sqlite:///./db/vessel_ratings.db"

# Storage Configuration
STORAGE_CONFIG = {
    "local_storage_path": os.getenv("VRS_LOCAL_STORAGE_PATH", "./local_storage"),
    "device_import_path": os.getenv("VRS_DEVICE_IMPORT_PATH", "./local_storage/device_imports"),
    "cloud_storage_path": os.getenv("VRS_CLOUD_STORAGE_PATH", ""),
    "allowed_extensions": [".json", ".csv"],
}

# API Keys and Endpoints
API_CONFIG = {
    "AIS_API": {
        "provider": "marinetraffic",  # or "spire"
        "endpoint": "https://www.marinetraffic.com/api/",
        "key": os.getenv("AIS_API_KEY", "demo"),
        "timeout": 10,
    },
    "SANCTIONS_API": {
        "provider": "ofac",
        "endpoint": "https://www.treasury.gov/",
        "timeout": 10,
    },
    "WEATHER_API": {
        "provider": "open-meteo",
        "endpoint": "https://api.open-meteo.com/v1/forecast",
        "key": None,  # Open-Meteo is free, no API key required
        "timeout": 10,
    },
    "MARITIME_DB": {
        "provider": "equasis",
        "endpoint": "https://www.equasis.org/",
        "timeout": 10,
    },
}

# Scoring Weights (must sum to 100)
SCORING_WEIGHTS = {
    "general_info": 11,       # 11%
    "ownership": 22,          # 22%
    "ais": 17,                # 17%
    "risk_compliance": 33,    # 33%
    "environmental": 17,      # 17%
}

# Band Rating Thresholds (0-9)
BAND_THRESHOLDS = {
    "excellent": (8.5, 9.0, "Very Low Risk", "🟢"),
    "very_strong": (8.0, 8.4, "Low Risk", "🟢"),
    "strong": (7.0, 7.9, "Low-Moderate Risk", "🟡"),
    "good": (6.0, 6.9, "Moderate Risk", "🟡"),
    "acceptable": (5.0, 5.9, "Medium Risk", "🟠"),
    "weak": (4.0, 4.9, "Elevated Risk", "🟠"),
    "poor": (3.0, 3.9, "High Risk", "🔴"),
    "very_poor": (2.0, 2.9, "Very High Risk", "🔴"),
    "critical": (1.0, 1.9, "Severe Risk", "🔴"),
    "blacklisted": (0.0, 0.9, "Extreme Risk", "⛔"),
}

# Risk Thresholds
RISK_THRESHOLDS = {
    "AIS_GAP_HOURS": 24,          # Flag if AIS data missing > 24 hours
    "FREQUENT_NAME_CHANGES": 3,   # Flag if name changed > 3 times in 5 years
    "FREQUENT_STS": 5,            # Flag if STS transfers > 5 in 2 years
    "HIGH_RISK_PORT_RATIO": 0.3,  # Flag if > 30% port calls are high-risk
    "SANCTIONED_OWNER_CRITICAL": True,  # Critical override for sanctioned entities
}

# High Risk Flags
HIGH_RISK_FLAGS = [
    "DPRK", "IRN", "SYR", "CUB", "VEN",  # Sanctioned countries
]

# High Risk Jurisdictions
HIGH_RISK_JURISDICTIONS = [
    "DPRK", "Iran", "Syria", "North Korea", "Panama", "Belize",
]

# Database Settings
DB_CONFIG = {
    "echo": False,
    "pool_size": 10,
    "max_overflow": 20,
}

# Logging Configuration
LOG_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        },
    },
    "handlers": {
        "default": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "standard",
        },
    },
    "loggers": {
        "": {
            "handlers": ["default"],
            "level": "INFO",
            "propagate": True,
        },
    },
}

# Feature Flags
FEATURES = {
    "AI_ANOMALY_DETECTION": False,  # Future feature
    "PREDICTIVE_SCORING": False,    # Future feature
    "BEHAVIOR_ANALYSIS": False,     # Future feature
    "CACHE_RESULTS": True,          # Cache API responses
}

print(f"[{datetime.now()}] Configuration loaded: {PROJECT_NAME} v{VERSION}")
