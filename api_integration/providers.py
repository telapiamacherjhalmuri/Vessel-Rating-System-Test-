"""
API Integration Layer for Vessel Rating System
Handles all external data fetching
"""

import requests
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from config import API_CONFIG, RISK_THRESHOLDS

logger = logging.getLogger(__name__)


class APIIntegration:
    """Central API Integration Manager"""
    
    def __init__(self):
        self.ais_provider = AISProvider()
        self.sanctions_provider = SanctionsProvider()
        self.weather_provider = WeatherProvider()
        self.maritime_db_provider = MaritimeDBProvider()
    
    def fetch_all_vessel_data(self, vessel_name: str, imo_number: str) -> Dict[str, Any]:
        """Fetch all vessel data from all sources"""
        logger.info(f"Fetching data for vessel: {vessel_name} (IMO: {imo_number})")
        
        result = {
            "vessel_info": self.maritime_db_provider.get_vessel_info(vessel_name, imo_number),
            "ais_data": self.ais_provider.get_ais_data(vessel_name, imo_number),
            "ownership": self.maritime_db_provider.get_ownership_data(imo_number),
            "sanctions": self.sanctions_provider.check_sanctions(vessel_name, imo_number),
            "weather": self.weather_provider.get_vessel_weather(imo_number),
            "compliance": self.maritime_db_provider.get_compliance_data(imo_number),
            "risk_events": self.maritime_db_provider.get_risk_events(imo_number),
        }
        
        logger.info(f"Data fetch completed for IMO: {imo_number}")
        return result


class AISProvider:
    """AIS (Automatic Identification System) Data Provider"""
    
    def get_ais_data(self, vessel_name: str, imo_number: str) -> Dict[str, Any]:
        """Fetch real-time AIS data"""
        # Demo implementation - returns sample data
        # In production, connect to MarineTraffic or Spire APIs
        
        return {
            "position": {
                "latitude": 22.5431,
                "longitude": 88.3660,
                "timestamp": datetime.utcnow().isoformat()
            },
            "movement": {
                "speed": 15.2,  # Knots
                "course": 125.5,  # Degrees
                "heading": 126.0
            },
            "status": "Underway using Engine",
            "ais_gaps": {
                "detected": False,
                "gap_hours": 0,
                "last_signal": datetime.utcnow().isoformat()
            },
            "anomalies": {
                "spoofing_detected": False,
                "dark_activity": False,
                "unusual_speed": False,
                "unusual_route": False
            }
        }
    
    def detect_ais_gaps(self, imo_number: str) -> Dict[str, Any]:
        """Detect AIS transmission gaps"""
        return {
            "has_gaps": False,
            "largest_gap_hours": 2,
            "total_gaps": 0,
            "last_transmission": datetime.utcnow().isoformat()
        }


class SanctionsProvider:
    """Sanctions List Checker (OFAC, UN, EU)"""
    
    def check_sanctions(self, vessel_name: str, imo_number: str) -> Dict[str, Any]:
        """Check vessel against sanctions lists"""
        # Demo implementation
        # In production, connect to actual OFAC/UN/EU APIs
        
        return {
            "ofac_hit": False,
            "un_hit": False,
            "eu_hit": False,
            "sanctioned_entities": [],
            "risk_level": "LOW",
            "last_checked": datetime.utcnow().isoformat()
        }
    
    def check_owner_sanctions(self, owner_name: str) -> Dict[str, Any]:
        """Check owner against sanctions lists"""
        return {
            "sanctioned": False,
            "lists": [],
            "confidence": 0.0
        }


class WeatherProvider:
    """Weather and Environmental Data Provider"""

    def __init__(self):
        self.base_url = "https://api.open-meteo.com/v1/forecast"

    def get_vessel_weather(self, imo_number: str) -> Dict[str, Any]:
        """Get current weather at vessel location using Open-Meteo API"""
        try:
            # For demo purposes, we'll use a sample location (Bay of Bengal coordinates)
            # In production, you'd get the actual vessel position from AIS data
            latitude = 22.5431
            longitude = 88.3660

            # Get weather data from Open-Meteo (free API, no key required)
            params = {
                "latitude": latitude,
                "longitude": longitude,
                "current": ["temperature_2m", "wind_speed_10m", "wind_direction_10m", "precipitation"],
                "hourly": ["wave_height", "visibility"],
                "timezone": "auto"
            }

            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()

            # Extract current weather data
            current = data.get("current", {})
            hourly = data.get("hourly", {})

            # Get current conditions
            temperature = current.get("temperature_2m", 25.0)
            wind_speed = current.get("wind_speed_10m", 10.0)
            wind_direction_deg = current.get("wind_direction_10m", 90.0)
            precipitation = current.get("precipitation", 0.0)

            # Get hourly data (first hour for current conditions)
            wave_height = hourly.get("wave_height", [1.0])[0] if hourly.get("wave_height") else 1.0
            visibility = hourly.get("visibility", [10000])[0] if hourly.get("visibility") else 10000

            # Convert wind direction to cardinal direction
            wind_direction = self._degrees_to_cardinal(wind_direction_deg)

            # Determine sea state based on wave height
            sea_state = self._determine_sea_state(wave_height)

            # Determine visibility quality
            visibility_quality = self._determine_visibility(visibility)

            # Check for storm conditions (high winds + precipitation)
            storm_warning = wind_speed > 25 or precipitation > 5.0

            # Determine piracy/war zone risk (simplified geographic check)
            piracy_zone = self._check_geographic_risk(latitude, longitude, "piracy")
            war_zone = self._check_geographic_risk(latitude, longitude, "war")

            return {
                "location": f"{latitude:.4f}, {longitude:.4f}",
                "coordinates": {
                    "latitude": latitude,
                    "longitude": longitude
                },
                "weather_conditions": {
                    "temperature": temperature,
                    "wind_speed": wind_speed,
                    "wind_direction": wind_direction,
                    "sea_state": sea_state,
                    "visibility": visibility_quality,
                    "precipitation": precipitation > 0.1,
                    "wave_height": wave_height
                },
                "piracy_zone": piracy_zone,
                "war_zone": war_zone,
                "storm_warning": storm_warning,
                "last_updated": datetime.utcnow().isoformat(),
                "data_source": "Open-Meteo API"
            }

        except requests.RequestException as e:
            logger.warning(f"Failed to fetch weather data: {e}. Using fallback data.")
            return self._get_fallback_weather_data()
        except Exception as e:
            logger.error(f"Error processing weather data: {e}. Using fallback data.")
            return self._get_fallback_weather_data()

    def _degrees_to_cardinal(self, degrees: float) -> str:
        """Convert wind direction degrees to cardinal direction"""
        directions = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
                     "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
        index = round(degrees / 22.5) % 16
        return directions[index]

    def _determine_sea_state(self, wave_height: float) -> str:
        """Determine sea state based on wave height"""
        if wave_height < 0.5:
            return "Calm"
        elif wave_height < 1.25:
            return "Smooth"
        elif wave_height < 2.5:
            return "Slight"
        elif wave_height < 4.0:
            return "Moderate"
        elif wave_height < 6.0:
            return "Rough"
        elif wave_height < 9.0:
            return "Very Rough"
        else:
            return "Extreme"

    def _determine_visibility(self, visibility_meters: float) -> str:
        """Determine visibility quality based on meters"""
        if visibility_meters >= 10000:
            return "Excellent"
        elif visibility_meters >= 5000:
            return "Good"
        elif visibility_meters >= 2000:
            return "Moderate"
        elif visibility_meters >= 500:
            return "Poor"
        else:
            return "Very Poor"

    def _check_geographic_risk(self, lat: float, lng: float, risk_type: str) -> bool:
        """Simplified geographic risk assessment"""
        # This is a simplified implementation
        # In production, you'd use proper GIS databases for piracy/war zones

        if risk_type == "piracy":
            # Gulf of Guinea, Somali Basin, Sulu Sea, etc. are high-risk areas
            piracy_zones = [
                # Gulf of Guinea
                (0, 10, -5, 10),
                # Somali Basin
                (0, 15, 40, 55),
                # Sulu Sea
                (5, 10, 118, 125),
                # Singapore Strait
                (1, 2, 103, 104)
            ]

            for min_lat, max_lat, min_lng, max_lng in piracy_zones:
                if min_lat <= lat <= max_lat and min_lng <= lng <= max_lng:
                    return True

        elif risk_type == "war":
            # Simplified war/conflict zones
            war_zones = [
                # Red Sea/Gulf of Aden (Yemen conflict)
                (12, 18, 42, 45),
                # Black Sea (Ukraine conflict)
                (44, 47, 30, 37),
                # South China Sea disputes
                (10, 25, 110, 125)
            ]

            for min_lat, max_lat, min_lng, max_lng in war_zones:
                if min_lat <= lat <= max_lat and min_lng <= lng <= max_lng:
                    return True

        return False

    def _get_fallback_weather_data(self) -> Dict[str, Any]:
        """Fallback weather data when API fails"""
        return {
            "location": "Unknown",
            "coordinates": {"latitude": 0.0, "longitude": 0.0},
            "weather_conditions": {
                "temperature": 25.0,
                "wind_speed": 10.0,
                "wind_direction": "NE",
                "sea_state": "Moderate",
                "visibility": "Good",
                "precipitation": False,
                "wave_height": 1.5
            },
            "piracy_zone": False,
            "war_zone": False,
            "storm_warning": False,
            "last_updated": datetime.utcnow().isoformat(),
            "data_source": "Fallback Data"
        }


class MaritimeDBProvider:
    """Maritime Database Provider (Equasis, IHS Markit data)"""
    
    def get_vessel_info(self, vessel_name: str, imo_number: str) -> Dict[str, Any]:
        """Get general vessel information"""
        return {
            "vessel_name": vessel_name,
            "imo_number": imo_number,
            "flag": "Panama",
            "vessel_type": "General Cargo Ship",
            "dimensions": {
                "length": 178.0,
                "width": 30.0,
                "depth": 18.5,
                "tonnage": {
                    "gross": 25000,
                    "dead_weight": 32500
                }
            },
            "engine": {
                "type": "Diesel-Electric",
                "power_kw": 6850,
                "fuel_type": "Marine Gas Oil"
            },
            "capacity": 32500,
            "builder": "China State Shipbuilding Corporation",
            "built_year": 2015,
            "classification_society": "ClassNK",
            "manager": "Bernhard Schulte Shipmanagement",
            "p_and_i_club": "Gard"
        }
    
    def get_ownership_data(self, imo_number: str) -> Dict[str, Any]:
        """Get ownership and management information"""
        return {
            "current_owner": "Global Maritime Holdings Ltd",
            "registered_owner": "Global Maritime Holdings Ltd",
            "beneficial_owner": "To be verified",
            "ownership_changes": 2,
            "name_changes": 1,
            "ownership_history": [
                {
                    "owner": "Global Maritime Holdings Ltd",
                    "from": "2020-01-15",
                    "to": None,
                    "location": "Panama"
                },
                {
                    "owner": "Asia Maritime Corp",
                    "from": "2015-09-20",
                    "to": "2020-01-14",
                    "location": "Singapore"
                }
            ],
            "manager": "Bernhard Schulte Shipmanagement",
            "classification_society": "ClassNK",
            "p_and_i_club": "Gard",
            "reputation_score": 0.75  # 0-1 scale
        }
    
    def get_compliance_data(self, imo_number: str) -> Dict[str, Any]:
        """Get compliance and certification data"""
        return {
            "certificates": [
                {
                    "type": "International Certificate of Fitness",
                    "number": "PAN-123456",
                    "issued_date": "2022-05-15",
                    "expiry_date": "2027-05-14",
                    "status": "VALID"
                },
                {
                    "type": "International Oil Pollution Prevention",
                    "number": "PAN-789012",
                    "issued_date": "2022-08-20",
                    "expiry_date": "2027-08-19",
                    "status": "VALID"
                },
                {
                    "type": "International Load Line Certificate",
                    "number": "PAN-345678",
                    "issued_date": "2021-03-10",
                    "expiry_date": "2026-03-09",
                    "status": "VALID"
                }
            ],
            "insurance_valid": True,
            "inspection_status": "CLEAR",
            "port_state_control": {
                "inspections": 2,
                "deficiencies": 0,
                "last_inspection": "2024-01-15"
            }
        }
    
    def get_risk_events(self, imo_number: str) -> Dict[str, Any]:
        """Get historical risk events"""
        return {
            "total_events": 2,
            "critical_events": 0,
            "high_risk_events": 1,
            "medium_risk_events": 1,
            "recent_events": [
                {
                    "type": "AIS_GAP",
                    "severity": "MEDIUM",
                    "date": (datetime.utcnow() - timedelta(days=15)).isoformat(),
                    "description": "AIS signal lost for 18 hours",
                    "resolved": True
                },
                {
                    "type": "PORT_DEVIATION",
                    "severity": "LOW",
                    "date": (datetime.utcnow() - timedelta(days=30)).isoformat(),
                    "description": "Unscheduled port call at Port of Santos",
                    "resolved": True
                }
            ]
        }
    
    def get_port_call_history(self, imo_number: str) -> Dict[str, Any]:
        """Get port call history and routes"""
        return {
            "total_port_calls": 24,
            "high_risk_ports": 2,
            "suspicious_routes": 0,
            "sts_transfers": 1,  # Ship-to-Ship transfers
            "recent_ports": [
                {"port": "Singapore", "date": "2024-02-10", "risk_level": "LOW"},
                {"port": "Port Said", "date": "2024-02-05", "risk_level": "MEDIUM"},
                {"port": "Hong Kong", "date": "2024-01-28", "risk_level": "LOW"},
            ]
        }


def get_api_integration() -> APIIntegration:
    """Factory function to get API Integration instance"""
    return APIIntegration()


if __name__ == "__main__":
    # Test API Integration
    api = get_api_integration()
    result = api.fetch_all_vessel_data("Meghna Pearl", "9894765")
    print(json.dumps(result, indent=2, default=str))
