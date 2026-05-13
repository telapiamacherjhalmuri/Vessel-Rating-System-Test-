"""
Database Models for Vessel Rating System
Using SQLAlchemy ORM
"""

import json
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

Base = declarative_base()


class Vessel(Base):
    """Main Vessel Record"""
    __tablename__ = "vessels"
    
    id = Column(Integer, primary_key=True, index=True)
    vessel_name = Column(String(255), index=True, nullable=False)
    imo_number = Column(String(50), unique=True, index=True, nullable=False)
    flag = Column(String(100))
    vessel_type = Column(String(100))
    tonnage = Column(Float)
    gross_tonnage = Column(Float)
    dead_weight_tonnage = Column(Float)
    length = Column(Float)
    width = Column(Float)
    depth = Column(Float)
    engine_type = Column(String(100))
    fuel_type = Column(String(100))
    capacity = Column(Float)
    builder = Column(String(255))
    built_year = Column(Integer)
    
    # Rating Data
    overall_score = Column(Float, default=0.0)
    band_score = Column(Float, default=0.0)
    risk_level = Column(String(50))
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_analysis = Column(DateTime)
    last_analyzed = Column(DateTime)
    latest_rating = Column(Float, default=0.0)
    
    # Relationships
    ownership_records = relationship("OwnershipRecord", back_populates="vessel", cascade="all, delete-orphan")
    ais_logs = relationship("AISLog", back_populates="vessel", cascade="all, delete-orphan")
    risk_events = relationship("RiskEvent", back_populates="vessel", cascade="all, delete-orphan")
    compliance_records = relationship("ComplianceRecord", back_populates="vessel", cascade="all, delete-orphan")
    module_scores = relationship("ModuleScore", back_populates="vessel", cascade="all, delete-orphan")


class OwnershipRecord(Base):
    """Ownership History"""
    __tablename__ = "ownership_records"
    
    id = Column(Integer, primary_key=True, index=True)
    vessel_id = Column(Integer, ForeignKey("vessels.id"), nullable=False)
    
    beneficial_owner = Column(String(255))
    registered_owner = Column(String(255))
    manager = Column(String(255))
    classification_society = Column(String(255))
    pi_club = Column(String(255))
    
    ownership_history = Column(JSON)  # JSON array of ownership changes
    name_change_frequency = Column(Integer, default=0)
    reputation_score = Column(Float)
    
    effective_from = Column(DateTime, default=datetime.utcnow)
    effective_to = Column(DateTime)
    
    vessel = relationship("Vessel", back_populates="ownership_records")


class AISLog(Base):
    """AIS Tracking Data"""
    __tablename__ = "ais_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    vessel_id = Column(Integer, ForeignKey("vessels.id"), nullable=False)
    
    latitude = Column(Float)
    longitude = Column(Float)
    speed = Column(Float)  # Knots
    course = Column(Float)  # Degrees
    heading = Column(Float)
    
    ais_timestamp = Column(DateTime, index=True)
    received_timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Quality Metrics
    ais_gap_hours = Column(Float, default=0)  # Hours since last signal
    spoofing_detected = Column(Boolean, default=False)
    dark_activity = Column(Boolean, default=False)
    
    vessel = relationship("Vessel", back_populates="ais_logs")


class RiskEvent(Base):
    """Risk Events and Alerts"""
    __tablename__ = "risk_events"
    
    id = Column(Integer, primary_key=True, index=True)
    vessel_id = Column(Integer, ForeignKey("vessels.id"), nullable=False)
    
    event_type = Column(String(100), index=True)  # "sanction_hit", "ais_gap", "dark_activity", etc.
    severity = Column(String(50))  # "critical", "high", "medium", "low"
    description = Column(Text)
    details = Column(JSON)
    
    detected_at = Column(DateTime, default=datetime.utcnow)
    resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime)
    
    vessel = relationship("Vessel", back_populates="risk_events")


class ComplianceRecord(Base):
    """Compliance and Documentation"""
    __tablename__ = "compliance_records"
    
    id = Column(Integer, primary_key=True, index=True)
    vessel_id = Column(Integer, ForeignKey("vessels.id"), nullable=False)
    
    certificate_type = Column(String(100))
    certificate_number = Column(String(255))
    issued_date = Column(DateTime)
    expiry_date = Column(DateTime)
    issuing_authority = Column(String(255))
    
    is_valid = Column(Boolean, default=True)
    compliance_status = Column(String(50))  # "compliant", "expired", "missing"
    insurance_status = Column(String(50))
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    vessel = relationship("Vessel", back_populates="compliance_records")


class ModuleScore(Base):
    """Individual Module Scores"""
    __tablename__ = "module_scores"
    
    id = Column(Integer, primary_key=True, index=True)
    vessel_id = Column(Integer, ForeignKey("vessels.id"), nullable=False)
    
    module_name = Column(String(100), index=True)  # "general_info", "ownership", "ais", etc.
    raw_score = Column(Float)  # 0-100
    normalized_score = Column(Float)  # 0-100
    band_score = Column(Float)  # 0-9
    weight = Column(Float)  # Module weight percentage
    
    details = Column(JSON)  # Additional details about how score was calculated
    
    calculated_at = Column(DateTime, default=datetime.utcnow)
    
    vessel = relationship("Vessel", back_populates="module_scores")


# Database initialization
def init_db(database_url: str = "sqlite:///./db/vessel_ratings.db"):
    """Initialize database"""
    engine = create_engine(database_url, connect_args={"check_same_thread": False} if "sqlite" in database_url else {})
    Base.metadata.create_all(bind=engine)
    return engine


def get_session(engine):
    """Get database session"""
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()


# Module-level engine and session for direct import
_default_engine = init_db()
Session = sessionmaker(autocommit=False, autoflush=False, bind=_default_engine)
