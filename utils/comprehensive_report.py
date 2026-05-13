"""
Comprehensive Reporting Module - Detailed vessel data analysis with band scoring
"""

import json
from datetime import datetime
from typing import Dict, List, Any, Optional
import pandas as pd

class ComprehensiveReport:
    """Generate detailed vessel analysis reports with all data and band scoring"""
    
    def __init__(self):
        self.report_data = {}
        self.module_scores = {}
    
    def generate_complete_report(self, 
                                vessel_name: str,
                                imo_number: str,
                                vessel_data: Dict[str, Any],
                                module_scores: Dict[str, Any],
                                final_rating: float,
                                band_rating: int,
                                risk_level: str) -> Dict[str, Any]:
        """
        Generate comprehensive report with all vessel data and band scoring
        
        Args:
            vessel_name: Name of vessel
            imo_number: IMO number
            vessel_data: All fetched vessel data from providers
            module_scores: Individual module scores and data
            final_rating: Final overall rating (0-9)
            band_rating: Band rating (0-9)
            risk_level: Risk classification
            
        Returns:
            Complete report dictionary with all data and analysis
        """
        
        report = {
            "report_type": "Comprehensive Vessel Analysis",
            "generation_timestamp": datetime.now().isoformat(),
            "vessel_identification": self._build_vessel_identification(vessel_name, imo_number),
            "executive_summary": self._build_executive_summary(final_rating, band_rating, risk_level),
            "detailed_sections": {
                "general_information": self._analyze_general_info(vessel_data.get("vessel_info", {})),
                "ownership_analysis": self._analyze_ownership(vessel_data.get("ownership", {})),
                "ais_analysis": self._analyze_ais(vessel_data.get("ais_data", {})),
                "risk_compliance_analysis": self._analyze_risk_compliance(vessel_data.get("sanctions", {})),
                "environmental_analysis": self._analyze_environmental(vessel_data.get("weather", {})),
            },
            "scoring_breakdown": self._build_scoring_breakdown(module_scores),
            "data_quality_assessment": self._assess_data_quality(vessel_data),
            "recommendations": self._generate_recommendations(final_rating, risk_level, module_scores),
            "exportable_data": self._prepare_exportable_data(vessel_data, module_scores, final_rating)
        }
        
        return report
    
    def _build_vessel_identification(self, vessel_name: str, imo_number: str) -> Dict:
        """Build vessel identification section"""
        return {
            "vessel_name": vessel_name,
            "imo_number": imo_number,
            "report_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def _build_executive_summary(self, final_rating: float, band_rating: int, risk_level: str) -> Dict:
        """Build executive summary"""
        rating_interpretation = self._interpret_rating(band_rating)
        
        return {
            "overall_rating": final_rating,
            "band_rating": band_rating,
            "risk_classification": risk_level,
            "rating_interpretation": rating_interpretation,
            "assessment_date": datetime.now().isoformat()
        }
    
    def _interpret_rating(self, band: int) -> str:
        """Interpret band rating into human-readable format"""
        if band >= 8:
            return "Excellent - Very low risk profile, strong compliance"
        elif band >= 7:
            return "Good - Low to moderate risk, acceptable standards"
        elif band >= 6:
            return "Moderate - Moderate risk, some concerns"
        elif band >= 5:
            return "Fair - Elevated risk, significant issues"
        elif band >= 4:
            return "Weak - High risk, multiple concerns"
        else:
            return "Poor/Blacklisted - Extreme risk, immediate action required"
    
    def _analyze_general_info(self, vessel_info: Dict) -> Dict:
        """Analyze general information with detailed data"""
        
        age = (2024 - int(vessel_info.get('built_year', 2024))) if vessel_info.get('built_year') else None
        age_risk = self._calculate_age_risk(age) if age else "Unknown"
        
        return {
            "collected_data": {
                "vessel_type": vessel_info.get('vessel_type', 'Not Available'),
                "built_year": vessel_info.get('built_year', 'Not Available'),
                "vessel_age_years": age,
                "age_risk_classification": age_risk,
                "gross_tonnage": vessel_info.get('dimensions', {}).get('tonnage', {}).get('gross', 'Not Available'),
                "deadweight_tonnage": vessel_info.get('dimensions', {}).get('tonnage', {}).get('deadweight', 'Not Available'),
                "flag_state": vessel_info.get('flag_state', 'Not Available'),
                "port_of_registry": vessel_info.get('port_of_registry', 'Not Available'),
                "classification_society": vessel_info.get('classification_society', 'Not Available'),
                "vessel_status": vessel_info.get('status', 'Not Available'),
                "call_sign": vessel_info.get('call_sign', 'Not Available'),
                "mmsi": vessel_info.get('mmsi', 'Not Available'),
                "previous_names": vessel_info.get('previous_names', []),
                "engine_type": vessel_info.get('engine_type', 'Not Available'),
                "propulsion_power": vessel_info.get('propulsion_power', 'Not Available'),
            },
            "risk_assessment": {
                "age_concern": "High ⚠️" if age and age > 20 else "Low ✅",
                "flag_state_risk": self._assess_flag_risk(vessel_info.get('flag_state')),
                "maintenance_status": vessel_info.get('maintenance_status', 'Unknown'),
                "classification_status": "Active ✅" if vessel_info.get('class_active') else "Inactive ⚠️"
            }
        }
    
    def _calculate_age_risk(self, age: int) -> str:
        """Calculate risk based on vessel age"""
        if age < 5:
            return "Very Low - Modern vessel"
        elif age < 10:
            return "Low - Well-maintained period"
        elif age < 15:
            return "Moderate - Entering higher maintenance phase"
        elif age < 20:
            return "High - Aging vessel, increased maintenance needs"
        else:
            return "Very High - Old vessel, significant maintenance risk"
    
    def _assess_flag_risk(self, flag_state: str) -> str:
        """Assess flag state risk"""
        # List of high-risk flag states (simplified)
        high_risk_flags = ['Unknown', 'Stateless', 'Comoros', 'Cambodia', 'Belize', 'Liberia']
        
        if flag_state in high_risk_flags:
            return "High Risk ⚠️"
        elif flag_state in ['Panama', 'Marshall Islands', 'Cyprus']:
            return "Moderate ⚠️"
        else:
            return "Low Risk ✅"
    
    def _analyze_ownership(self, ownership_data: Dict) -> Dict:
        """Analyze ownership information"""
        return {
            "collected_data": {
                "current_owner": ownership_data.get('current_owner', 'Not Available'),
                "owner_country": ownership_data.get('owner_country', 'Not Available'),
                "manager": ownership_data.get('manager', 'Not Available'),
                "operator": ownership_data.get('operator', 'Not Available'),
                "beneficial_owner": ownership_data.get('beneficial_owner', 'Not Available'),
                "ownership_changes_count": ownership_data.get('ownership_changes', 0),
                "name_changes_count": ownership_data.get('name_changes', 0),
                "last_change_date": ownership_data.get('last_change_date', 'Not Available'),
                "ownership_history_years": ownership_data.get('ownership_history_years', 'Unknown'),
                "manager_reputation": ownership_data.get('manager_reputation', 'Unknown'),
            },
            "risk_assessment": {
                "owner_sanctioned": "Yes ⚠️" if ownership_data.get('owner_sanctioned') else "No ✅",
                "ownership_stability": "Unstable ⚠️" if ownership_data.get('ownership_changes', 0) > 5 else "Stable ✅",
                "manager_risk": "High ⚠️" if ownership_data.get('manager_reputation') == 'Poor' else "Low ✅",
                "ownership_chain_clarity": "Clear ✅" if ownership_data.get('beneficial_owner') else "Unclear ⚠️"
            }
        }
    
    def _analyze_ais(self, ais_data: Dict) -> Dict:
        """Analyze AIS tracking data"""
        return {
            "collected_data": {
                "position": {
                    "latitude": ais_data.get('position', {}).get('latitude', 'Not Available'),
                    "longitude": ais_data.get('position', {}).get('longitude', 'Not Available'),
                    "accuracy_meters": ais_data.get('position', {}).get('accuracy', 'Unknown')
                },
                "movement": {
                    "speed_knots": ais_data.get('movement', {}).get('speed', 'Not Available'),
                    "course_degrees": ais_data.get('movement', {}).get('course', 'Not Available'),
                    "rot_degrees_per_min": ais_data.get('movement', {}).get('rot', 'Not Available')
                },
                "ais_status": ais_data.get('ais_status', 'Unknown'),
                "last_update": ais_data.get('last_update', 'Unknown'),
                "signal_quality": ais_data.get('signal_quality', 'Unknown'),
                "messaging_frequency": ais_data.get('messaging_frequency', 'Unknown'),
                "destination": ais_data.get('destination', 'Not Available'),
                "eta": ais_data.get('eta', 'Not Available')
            },
            "anomaly_detection": {
                "spoofing_detected": "Yes ⚠️" if ais_data.get('spoofing_detected') else "No ✅",
                "dark_activity": "Yes ⚠️" if ais_data.get('dark_activity') else "No ✅",
                "unusual_routes": "Detected ⚠️" if ais_data.get('unusual_routes') else "Normal ✅",
                "speed_anomalies": "Yes ⚠️" if ais_data.get('speed_anomalies') else "No ✅",
                "course_changes": ais_data.get('course_changes_count', 0),
                "signal_gaps": "Yes ⚠️" if ais_data.get('signal_gaps') else "No ✅"
            }
        }
    
    def _analyze_risk_compliance(self, sanctions_data: Dict) -> Dict:
        """Analyze risk and compliance"""
        total_hits = (
            (1 if sanctions_data.get('ofac_hit') else 0) +
            (1 if sanctions_data.get('un_hit') else 0) +
            (1 if sanctions_data.get('eu_hit') else 0)
        )
        
        return {
            "sanctions_screening": {
                "ofac_listed": "Yes 🚨" if sanctions_data.get('ofac_hit') else "No ✅",
                "un_sanctions": "Yes 🚨" if sanctions_data.get('un_hit') else "No ✅",
                "eu_sanctions": "Yes 🚨" if sanctions_data.get('eu_hit') else "No ✅",
                "total_sanctions_hits": total_hits,
                "last_violation_date": sanctions_data.get('last_violation_date', 'None'),
                "violation_type": sanctions_data.get('violation_type', 'N/A')
            },
            "compliance_history": {
                "detention_count": sanctions_data.get('detention_count', 0),
                "detention_rate": sanctions_data.get('detention_rate', 'Not Available'),
                "psc_status": sanctions_data.get('psc_status', 'Unknown'),
                "deficiency_count": sanctions_data.get('deficiency_count', 0),
                "banned_status": "Banned 🚨" if sanctions_data.get('banned') else "Active ✅",
                "banning_period": sanctions_data.get('banning_period', 'N/A') if sanctions_data.get('banned') else 'N/A'
            },
            "trade_route_risk": {
                "route_risk_level": sanctions_data.get('route_risk_level', 'Unknown'),
                "restricted_areas": sanctions_data.get('restricted_areas', []),
                "sanctioned_trade_partners": sanctions_data.get('sanctioned_trade_partners', []),
                "illicit_cargo_risk": sanctions_data.get('illicit_cargo_risk', 'Unknown')
            }
        }
    
    def _analyze_environmental(self, weather_data: Dict) -> Dict:
        """Analyze environmental and voyage data"""
        return {
            "current_conditions": {
                "region": weather_data.get('region', 'Unknown'),
                "temperature_celsius": weather_data.get('temperature', 'Not Available'),
                "wind_speed_knots": weather_data.get('wind_speed', 'Not Available'),
                "wind_direction": weather_data.get('wind_direction', 'Not Available'),
                "wave_height_meters": weather_data.get('wave_height', 'Not Available'),
                "sea_state": weather_data.get('sea_state', 'Unknown'),
                "visibility": weather_data.get('visibility', 'Unknown'),
                "pressure_hpa": weather_data.get('pressure', 'Not Available')
            },
            "route_hazards": {
                "piracy_zone": "Yes ⚠️" if weather_data.get('piracy_zone') else "No ✅",
                "war_zone": "Yes 🚨" if weather_data.get('war_zone') else "No ✅",
                "storm_area": "Yes ⚠️" if weather_data.get('storm_area') else "No ✅",
                "ice_zone": "Yes ⚠️" if weather_data.get('ice_zone') else "No ✅",
                "heavy_traffic": "Yes ⚠️" if weather_data.get('heavy_traffic') else "No ✅"
            },
            "route_assessment": {
                "overall_risk": weather_data.get('route_risk_assessment', 'Unknown'),
                "weather_risk": weather_data.get('weather_risk', 'Unknown'),
                "geopolitical_risk": weather_data.get('geopolitical_risk', 'Unknown'),
                "maritime_risk": weather_data.get('maritime_risk', 'Unknown')
            }
        }
    
    def _build_scoring_breakdown(self, module_scores: Dict) -> Dict:
        """Build detailed scoring breakdown with band ratings"""
        breakdown = {
            "modules": [],
            "summary": {
                "total_weighted_score": 0,
                "average_band": 0,
                "highest_scoring_module": None,
                "lowest_scoring_module": None
            }
        }
        
        for module_name, scores in module_scores.items():
            module_info = {
                "module_name": module_name,
                "raw_score": scores.get('score', 0),
                "normalized_score": scores.get('normalized_score', 0),
                "band_rating": scores.get('band', 0),
                "weight_percentage": scores.get('weight_percent', 0),
                "weighted_contribution": (scores.get('score', 0) / 100) * scores.get('weight_percent', 0),
                "risk_factors": scores.get('risk_factors', []),
                "positive_factors": scores.get('positive_factors', []),
                "improvement_areas": scores.get('improvement_areas', [])
            }
            breakdown["modules"].append(module_info)
        
        if breakdown["modules"]:
            scores_only = [m["band_rating"] for m in breakdown["modules"]]
            breakdown["summary"]["average_band"] = sum(scores_only) / len(scores_only)
            breakdown["summary"]["highest_scoring_module"] = max(breakdown["modules"], key=lambda x: x["band_rating"])
            breakdown["summary"]["lowest_scoring_module"] = min(breakdown["modules"], key=lambda x: x["band_rating"])
        
        return breakdown
    
    def _assess_data_quality(self, vessel_data: Dict) -> Dict:
        """Assess quality and freshness of collected data"""
        sources = [
            "vessel_info",
            "ownership",
            "ais_data",
            "sanctions",
            "weather",
        ]

        available_sources = sum(1 for source in sources if vessel_data.get(source))
        completeness_score = (available_sources / len(sources)) * 100

        return {
            "data_sources": {
                "total_available": available_sources,
                "total_expected": len(sources),
                "completeness_percentage": completeness_score
            },
            "source_status": {
                "vessel_info": "✅" if vessel_data.get("vessel_info") else "❌",
                "ownership": "✅" if vessel_data.get("ownership") else "❌",
                "ais_data": "✅" if vessel_data.get("ais_data") else "❌",
                "sanctions": "✅" if vessel_data.get("sanctions") else "❌",
                "weather": "✅" if vessel_data.get("weather") else "❌",
            },
            "reliability": {
                "ais_reliability": "Real-time, High confidence ✅",
                "sanctions_reliability": "Daily updated, High confidence ✅",
                "vessel_info_reliability": "Updated on change, Medium-High confidence ⚠️",
                "weather_reliability": "Current conditions, High confidence ✅",
                "compliance_reliability": "Periodic updates, Medium confidence ⚠️"
            }
        }
    
    def _generate_recommendations(self, final_rating: float, risk_level: str, module_scores: Dict) -> Dict:
        """Generate actionable recommendations"""
        recommendations = {
            "overall": [],
            "by_module": []
        }
        
        # Overall recommendations
        if final_rating >= 8:
            recommendations["overall"].append("✅ Vessel meets excellent standards. Continue routine monitoring.")
        elif final_rating >= 6:
            recommendations["overall"].append("⚠️ Conduct enhanced risk monitoring.")
        else:
            recommendations["overall"].append("🚨 Immediate action required. Review vessel eligibility.")
        
        return recommendations
    
    def _prepare_exportable_data(self, vessel_data: Dict, module_scores: Dict, final_rating: float) -> Dict:
        """Prepare data for export to CSV, JSON, PDF"""
        return {
            "csv_compatible": {
                "module_scores": [
                    {
                        "module": name,
                        "score": scores.get('score', 0),
                        "band": scores.get('band', 0),
                        "weight": scores.get('weight_percent', 0)
                    }
                    for name, scores in module_scores.items()
                ]
            },
            "json_compatible": {
                "all_data": vessel_data,
                "scoring": module_scores,
                "final_rating": final_rating,
                "export_date": datetime.now().isoformat()
            }
        }


# Convenience function
def generate_comprehensive_report(vessel_name: str, 
                                 imo_number: str,
                                 vessel_data: Dict[str, Any],
                                 module_scores: Dict[str, Any],
                                 final_rating: float,
                                 band_rating: int,
                                 risk_level: str) -> Dict[str, Any]:
    """Generate comprehensive report"""
    reporter = ComprehensiveReport()
    return reporter.generate_complete_report(
        vessel_name, imo_number, vessel_data, module_scores,
        final_rating, band_rating, risk_level
    )

def _flatten_vessel_data(vessel_data: Dict[str, Any]) -> Dict[str, Any]:
    """Flatten nested vessel data for CSV export"""
    flattened = {}
    
    # Vessel Info
    vessel_info = vessel_data.get("vessel_info", {})
    flattened.update({
        "vessel_name": vessel_info.get("vessel_name", ""),
        "imo_number": vessel_info.get("imo_number", ""),
        "vessel_type": vessel_info.get("vessel_type", ""),
        "built_year": vessel_info.get("built_year", ""),
        "flag_state": vessel_info.get("flag_state", ""),
        "port_of_registry": vessel_info.get("port_of_registry", ""),
        "call_sign": vessel_info.get("call_sign", ""),
        "mmsi": vessel_info.get("mmsi", ""),
        "classification_society": vessel_info.get("classification_society", ""),
        "status": vessel_info.get("status", ""),
        "dimensions_length": vessel_info.get("dimensions", {}).get("length", ""),
        "dimensions_width": vessel_info.get("dimensions", {}).get("width", ""),
        "dimensions_draught": vessel_info.get("dimensions", {}).get("draught", ""),
        "tonnage_gross": vessel_info.get("dimensions", {}).get("tonnage", {}).get("gross", ""),
        "tonnage_net": vessel_info.get("dimensions", {}).get("tonnage", {}).get("net", ""),
        "tonnage_deadweight": vessel_info.get("dimensions", {}).get("tonnage", {}).get("deadweight", ""),
    })
    
    # Ownership
    ownership = vessel_data.get("ownership", {})
    flattened.update({
        "current_owner": ownership.get("current_owner", ""),
        "manager": ownership.get("manager", ""),
        "technical_manager": ownership.get("technical_manager", ""),
        "ownership_changes": ownership.get("ownership_changes", 0),
        "name_changes": ownership.get("name_changes", 0),
        "beneficial_owner": ownership.get("beneficial_owner", ""),
        "registered_owner": ownership.get("registered_owner", ""),
    })
    
    # AIS Data
    ais = vessel_data.get("ais_data", {})
    position = ais.get("position", {})
    movement = ais.get("movement", {})
    flattened.update({
        "ais_latitude": position.get("latitude", ""),
        "ais_longitude": position.get("longitude", ""),
        "ais_speed": movement.get("speed", ""),
        "ais_course": movement.get("course", ""),
        "ais_heading": movement.get("heading", ""),
        "ais_timestamp": ais.get("timestamp", ""),
        "ais_destination": ais.get("destination", ""),
        "ais_eta": ais.get("eta", ""),
    })
    
    # Sanctions
    sanctions = vessel_data.get("sanctions", {})
    flattened.update({
        "ofac_hit": sanctions.get("ofac_hit", False),
        "un_hit": sanctions.get("un_hit", False),
        "eu_hit": sanctions.get("eu_hit", False),
        "sanctions_details": json.dumps(sanctions.get("details", [])),
    })
    
    # Weather/Environmental
    weather = vessel_data.get("weather", {})
    flattened.update({
        "piracy_zone": weather.get("piracy_zone", False),
        "war_zone": weather.get("war_zone", False),
        "hurricane_zone": weather.get("hurricane_zone", False),
        "weather_conditions": weather.get("conditions", ""),
        "weather_temperature": weather.get("temperature", ""),
        "weather_wind_speed": weather.get("wind_speed", ""),
    })
    
    return flattened


def _get_vessel_metadata(vessel_data: Dict[str, Any]) -> Dict[str, Any]:
    """Extract vessel metadata including pictures"""
    metadata = {}
    
    # Try to get vessel picture URLs from various sources
    vessel_info = vessel_data.get("vessel_info", {})
    metadata["vessel_picture_url"] = vessel_info.get("picture_url", "")
    
    # Additional metadata
    metadata.update({
        "data_sources": list(vessel_data.keys()),
        "last_updated": datetime.now().isoformat(),
        "data_completeness": len([k for k, v in vessel_data.items() if v]),
    })
    
    return metadata