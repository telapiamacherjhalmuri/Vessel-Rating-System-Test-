"""
Scoring Modules for Vessel Rating System
5 Independent Modules for Risk Assessment
"""

import logging
from typing import Dict, Any, Tuple
from datetime import datetime, timedelta
from config import RISK_THRESHOLDS, HIGH_RISK_FLAGS

logger = logging.getLogger(__name__)


class Module1_GeneralInformation:
    """Module 1: General Information Scoring (10% weight)"""
    
    @staticmethod
    def calculate_score(vessel_data: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
        """
        Score based on: dimensions, age, tonnage, engine type, maintenance
        Higher score = Lower risk
        """
        score = 100.0
        details = {}
        
        try:
            vessel_info = vessel_data.get("vessel_info", {})
            
            # Vessel age assessment
            built_year = vessel_info.get("built_year", 2015)
            vessel_age = datetime.now().year - built_year
            details["vessel_age"] = vessel_age
            
            if vessel_age > 30:
                score -= 25  # Old vessel - higher maintenance risk
                details["age_risk"] = "HIGH"
            elif vessel_age > 20:
                score -= 15
                details["age_risk"] = "MEDIUM"
            else:
                details["age_risk"] = "LOW"
            
            # Tonnage assessment (larger = sometimes better maintained)
            tonnage = vessel_info.get("dimensions", {}).get("tonnage", {}).get("gross", 0)
            details["tonnage"] = tonnage
            
            if tonnage < 5000:
                score -= 10  # Small vessel - less regulated
            elif tonnage > 150000:
                score -= 5  # Very large - complex operations
            
            # Engine type assessment
            engine = vessel_info.get("engine", {}).get("type", "")
            fuel_type = vessel_info.get("engine", {}).get("fuel_type", "")
            details["engine"] = engine
            details["fuel_type"] = fuel_type
            
            # Modern engine types score better
            if "LNG" in fuel_type or "Electric" in engine:
                score += 10  # Environmentally friendly = better maintained
            elif "HFO" in fuel_type or "Heavy Fuel" in fuel_type:
                score -= 5  # Heavy fuel = potential environmental risk
            
            # Classification Society
            class_society = vessel_info.get("classification_society", "")
            details["classification_society"] = class_society
            
            # Top tier classification societies
            premium_societies = ["Lloyd's Register", "ClassNK", "DNV", "ABS", "Bureau Veritas", "BUREAU VERITAS", "BV", "RINA"]
            if any(s in class_society for s in premium_societies):
                score += 8
            elif class_society:
                score += 3
            
            # Ensure score stays within 0-100
            score = max(0, min(100, score))
            
        except Exception as e:
            logger.error(f"Error in Module 1 scoring: {e}")
            score = 50.0
        
        return score, details


class Module2_OwnershipInformation:
    """Module 2: Ownership Information Scoring (20% weight)"""
    
    @staticmethod
    def calculate_score(vessel_data: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
        """
        Score based on: ownership history, name changes, company reputation
        Higher score = Lower risk (stable ownership)
        """
        score = 100.0
        details = {}
        
        try:
            ownership = vessel_data.get("ownership", {})
            
            # Ownership change frequency
            ownership_changes = ownership.get("ownership_changes", 0)
            details["ownership_changes"] = ownership_changes
            
            if ownership_changes > 5:
                score -= 30  # Frequent ownership changes = suspicious
                details["ownership_risk"] = "CRITICAL"
            elif ownership_changes > 3:
                score -= 20
                details["ownership_risk"] = "HIGH"
            elif ownership_changes > 1:
                score -= 10
                details["ownership_risk"] = "MEDIUM"
            
            # Name change frequency
            name_changes = ownership.get("name_changes", 0)
            details["name_changes"] = name_changes
            
            if name_changes > 3:
                score -= 25  # Frequent name changes = suspicious
                details["name_change_risk"] = "CRITICAL"
            elif name_changes > 1:
                score -= 15
                details["name_change_risk"] = "HIGH"
            
            # Owner reputation (0-1 scale)
            reputation = ownership.get("reputation_score", 0.75)
            details["reputation_score"] = reputation

            reputation_penalty = (1.0 - reputation) * 40
            score -= reputation_penalty

            # Owner sanctions
            owner_sanctioned = ownership.get("owner_sanctioned", False)
            details["owner_sanctioned"] = owner_sanctioned
            if owner_sanctioned:
                score -= 40
                details["owner_sanction_risk"] = "CRITICAL"

            # Manager and Classification Society assessment
            manager = ownership.get("manager", "")
            class_society = ownership.get("classification_society", "")
            pi_club = ownership.get("p_and_i_club", "")
            
            details["manager"] = manager
            details["class_society"] = class_society
            details["pi_club"] = pi_club
            
            # Premium managers boost score
            premium_managers = ["Bernhard Schulte", "Wallem", "V.Group", "Columbia Shipmanagement"]
            if any(mgr in manager for mgr in premium_managers):
                score += 10
            
            # P&I Club presence is positive
            if pi_club:
                score += 5
            
            # Ensure score stays within 0-100
            score = max(0, min(100, score))
            
        except Exception as e:
            logger.error(f"Error in Module 2 scoring: {e}")
            score = 50.0
        
        return score, details


class Module3_AISInformation:
    """Module 3: AIS Information Scoring (15% weight)"""
    
    @staticmethod
    def calculate_score(vessel_data: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
        """
        Score based on: AIS continuity, spoofing detection, position accuracy
        Higher score = More transparent (lower risk)
        """
        score = 100.0
        details = {}
        
        try:
            ais_data = vessel_data.get("ais_data", {})
            
            # AIS gap detection
            ais_gaps = ais_data.get("ais_gaps", {})
            gap_hours = ais_gaps.get("gap_hours", 0)
            details["ais_gap_hours"] = gap_hours
            
            if gap_hours > 72:
                score -= 40  # Extended gap = suspicious
                details["ais_gap_risk"] = "CRITICAL"
            elif gap_hours > 24:
                score -= 25
                details["ais_gap_risk"] = "HIGH"
            elif gap_hours > 6:
                score -= 10
                details["ais_gap_risk"] = "MEDIUM"
            else:
                details["ais_gap_risk"] = "LOW"
            
            # AIS spoofing detection
            anomalies = ais_data.get("anomalies", {})
            spoofing = anomalies.get("spoofing_detected", False)
            dark_activity = anomalies.get("dark_activity", False)
            unusual_speed = anomalies.get("unusual_speed", False)
            unusual_route = anomalies.get("unusual_route", False)
            
            details["spoofing_detected"] = spoofing
            details["dark_activity"] = dark_activity
            
            if spoofing:
                score -= 50  # Spoofing = extreme risk
                details["spoofing_risk"] = "CRITICAL"
            
            if dark_activity:
                score -= 35
                details["dark_activity_risk"] = "CRITICAL"
            
            if unusual_speed:
                score -= 15
            
            if unusual_route:
                score -= 15
            
            # Signal quality/presence
            if ais_data.get("status") == "Underway using Engine":
                score += 5  # Normal operation is good
            
            # Ensure score stays within 0-100
            score = max(0, min(100, score))
            
        except Exception as e:
            logger.error(f"Error in Module 3 scoring: {e}")
            score = 50.0
        
        return score, details


class Module4_RiskCompliance:
    """Module 4: Risk & Compliance Scoring (30% weight) - CORE MODULE"""
    
    @staticmethod
    def calculate_score(vessel_data: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
        """
        Score based on: sanctions, flag risk, port history, STS transfers
        MOST IMPORTANT MODULE - determines critical risk levels
        Higher score = Lower risk
        """
        score = 100.0
        details = {}
        
        try:
            sanctions = vessel_data.get("sanctions", {})
            ownership = vessel_data.get("ownership", {})

            # SANCTIONS CHECK - Heavy penalty, but continue evaluating all factors
            # so each vessel is scored on its full profile, not just the sanctions hit
            ofac_hit = sanctions.get("ofac_hit", False)
            un_hit   = sanctions.get("un_hit",   False)
            eu_hit   = sanctions.get("eu_hit",   False)

            sanctions_penalty = 0
            if ofac_hit:
                sanctions_penalty = max(sanctions_penalty, 70)
            if un_hit:
                sanctions_penalty = max(sanctions_penalty, 65)
            if eu_hit:
                sanctions_penalty = max(sanctions_penalty, 60)

            if sanctions_penalty > 0:
                score -= sanctions_penalty
                details["sanctions_hit"] = True
                details["sanctions_risk"] = "CRITICAL"
            else:
                details["sanctions_hit"] = False

            # Owner sanctions (vessel not on a list but owner is sanctioned)
            owner_sanctioned = ownership.get("owner_sanctioned", False)
            if owner_sanctioned:
                score -= 35
                details["owner_sanctioned_risk"] = "HIGH"

            # Flag risk assessment
            flag = vessel_data.get("vessel_info", {}).get("flag", "Unknown")
            details["flag"] = flag

            # Check high-risk flags
            for risk_flag in HIGH_RISK_FLAGS:
                if risk_flag in flag:
                    score -= 40
                    details["flag_risk"] = "HIGH"
                    break

            # Port call analysis
            if "port_call_history" in vessel_data:
                port_data = vessel_data["port_call_history"]
                high_risk_ports = port_data.get("high_risk_ports", 0)
                sts_transfers = port_data.get("sts_transfers", 0)
                total_ports = port_data.get("total_port_calls", 1)
                
                details["high_risk_ports"] = high_risk_ports
                details["sts_transfers"] = sts_transfers
                
                # High-risk port ratio
                if total_ports > 0:
                    high_risk_ratio = high_risk_ports / total_ports
                    if high_risk_ratio > 0.5:
                        score -= 35
                    elif high_risk_ratio > 0.3:
                        score -= 20
                    elif high_risk_ratio > 0.1:
                        score -= 10
                
                # STS transfer frequency (red flag for smuggling)
                if sts_transfers > 5:
                    score -= 30
                    details["sts_risk"] = "CRITICAL"
                elif sts_transfers > 2:
                    score -= 15
                    details["sts_risk"] = "HIGH"
            
            # Trade route analysis
            # Add logic based on suspicious trade patterns

            # Ensure score stays within 0-100
            score = max(0, min(100, score))
            
        except Exception as e:
            logger.error(f"Error in Module 4 scoring: {e}")
            score = 50.0
        
        return score, details


class Module5_Environmental:
    """Module 5: Environmental & Voyage Data Scoring (15% weight)"""
    
    @staticmethod
    def calculate_score(vessel_data: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
        """
        Score based on: weather conditions, route safety, piracy/war zones
        Higher score = Safer voyage environment (lower risk)
        """
        score = 100.0
        details = {}
        
        try:
            weather = vessel_data.get("weather", {})
            
            # Weather conditions assessment
            weather_cond = weather.get("weather_conditions", {})
            sea_state = weather_cond.get("sea_state", "Moderate")
            visibility = weather_cond.get("visibility", "Good")
            wind_speed = weather_cond.get("wind_speed", 10.0)
            wave_height = weather_cond.get("wave_height", 1.5)
            
            details["sea_state"] = sea_state
            details["visibility"] = visibility
            details["wind_speed"] = wind_speed
            details["wave_height"] = wave_height
            
            # Enhanced sea state scoring based on wave height
            if wave_height > 4.0:
                score -= 20  # Very rough seas
            elif wave_height > 2.5:
                score -= 10  # Rough seas
            elif wave_height < 0.5:
                score += 5  # Calm seas = safer
            
            # Enhanced visibility scoring
            if visibility in ["Very Poor"]:
                score -= 20
            elif visibility in ["Poor"]:
                score -= 10
            elif visibility in ["Excellent"]:
                score += 3
            
            # Wind speed assessment
            if wind_speed > 30:
                score -= 15  # Gale force winds
            elif wind_speed > 20:
                score -= 8   # Strong winds
            
            # Piracy zone assessment
            piracy_zone = weather.get("piracy_zone", False)
            details["piracy_zone"] = piracy_zone
            
            if piracy_zone:
                score -= 25
            
            # War zone assessment
            war_zone = weather.get("war_zone", False)
            details["war_zone"] = war_zone
            
            if war_zone:
                score -= 50  # War zone = extreme risk
            
            # Storm warning
            storm_warning = weather.get("storm_warning", False)
            details["storm_warning"] = storm_warning
            
            if storm_warning:
                score -= 20
            
            # Port call risk analysis
            if "port_call_history" in vessel_data:
                port_data = vessel_data["port_call_history"]
                recent_ports = port_data.get("recent_ports", [])
                
                suspicious_routes = 0
                for port in recent_ports:
                    if port.get("risk_level") == "HIGH":
                        suspicious_routes += 1
                
                if suspicious_routes > 2:
                    score -= 20
                
                details["suspicious_routes"] = suspicious_routes
            
            # Maintenance patterns
            # Could analyze incident history for trends
            
            # Ensure score stays within 0-100
            score = max(0, min(100, score))
            
        except Exception as e:
            logger.error(f"Error in Module 5 scoring: {e}")
            score = 50.0
        
        return score, details


# Dictionary of all modules for easy access
MODULES = {
    "general_info": Module1_GeneralInformation(),
    "ownership": Module2_OwnershipInformation(),
    "ais": Module3_AISInformation(),
    "risk_compliance": Module4_RiskCompliance(),
    "environmental": Module5_Environmental(),
}
