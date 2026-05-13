"""
Vessel Rating System - Scoring Engine Package
"""

from scoring_engine.engine import (
    ScoringEngine,
    get_scoring_engine
)

from scoring_engine.modules import (
    Module1_GeneralInformation,
    Module2_OwnershipInformation,
    Module3_AISInformation,
    Module4_RiskCompliance,
    Module5_Environmental,
    MODULES
)

__all__ = [
    "ScoringEngine",
    "get_scoring_engine",
    "Module1_GeneralInformation",
    "Module2_OwnershipInformation",
    "Module3_AISInformation",
    "Module4_RiskCompliance",
    "Module5_Environmental",
    "MODULES",
]
