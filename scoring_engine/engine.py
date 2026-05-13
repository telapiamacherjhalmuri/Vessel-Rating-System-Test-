"""
Scoring Engine - Aggregates module scores and calculates final ratings
Implements band rating system (0-9)
"""

import logging
from typing import Dict, Any, Tuple, List
from config import SCORING_WEIGHTS, BAND_THRESHOLDS, RISK_THRESHOLDS
from scoring_engine.modules import MODULES

logger = logging.getLogger(__name__)


class ScoringEngine:
    """Main Scoring Engine"""
    
    def __init__(self):
        self.weights = SCORING_WEIGHTS
        self.band_thresholds = BAND_THRESHOLDS
        self.risk_thresholds = RISK_THRESHOLDS
    
    def calculate_all_module_scores(self, vessel_data: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """Calculate scores for all registered modules"""
        module_results = {}
        
        for module_name, module in MODULES.items():
            score, details = module.calculate_score(vessel_data)
            
            module_results[module_name] = {
                "raw_score": score,
                "normalized_score": score,  # Already 0-100
                "weight": self.weights.get(module_name, 0) / 100.0,
                "weighted_score": score * (self.weights.get(module_name, 0) / 100.0),
                "details": details,
                "band_score": self._score_to_band(score)
            }
            
            logger.info(f"Module {module_name}: Score={score:.1f}, Band={module_results[module_name]['band_score']:.1f}")
        
        return module_results
    
    def calculate_final_score(self, module_results: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate weighted final score"""
        total_weighted_score = 0.0
        total_weight = 0.0
        
        for module_name, result in module_results.items():
            total_weighted_score += result["weighted_score"]
            total_weight += result["weight"]
        
        # Normalize if weights don't sum to 1
        if total_weight > 0:
            final_score = total_weighted_score / total_weight
        else:
            final_score = sum(r["raw_score"] for r in module_results.values()) / len(module_results)
        
        return {
            "final_score": final_score,
            "total_weight": total_weight,
            "total_weighted_score": total_weighted_score
        }
    
    def apply_critical_overrides(self, module_results: Dict[str, Dict[str, Any]],
                                vessel_data: Dict[str, Any]) -> float:
        """Return a band ceiling for critical conditions.

        The returned value is a CAP, not a forced band — the engine takes
        min(natural_band, cap_band), so vessels still differentiate within
        the capped range based on their full scoring profile.
        """
        cap_band = None
        cap_reason = None

        def _tighten(new_cap: float, reason: str) -> None:
            nonlocal cap_band, cap_reason
            if cap_band is None or new_cap < cap_band:
                cap_band = new_cap
                cap_reason = reason

        sanctions = vessel_data.get("sanctions", {})
        if sanctions.get("ofac_hit") or sanctions.get("un_hit") or sanctions.get("eu_hit"):
            _tighten(4.0, "SANCTIONED_ENTITY")
            logger.warning("CAP OVERRIDE: Sanctioned vessel — band capped at 4.0")

        ais_details = module_results.get("ais", {}).get("details", {})
        if ais_details.get("spoofing_detected") and ais_details.get("dark_activity"):
            _tighten(3.0, "AIS_SPOOFING_AND_DARK_ACTIVITY")
            logger.warning("CAP OVERRIDE: AIS spoofing + dark activity — band capped at 3.0")

        risk_details = module_results.get("risk_compliance", {}).get("details", {})
        if risk_details.get("flag_risk") == "HIGH":
            _tighten(4.0, "BLACKLISTED_FLAG")
            logger.warning("CAP OVERRIDE: High-risk flag — band capped at 4.0")

        return cap_band, cap_reason
    
    def _score_to_band(self, score: float) -> float:
        """Convert 0-100 score to 0-9 band rating"""
        # Remember: Higher score = Lower risk = Higher band
        # Band = (Score / 100) * 9
        band = (score / 100.0) * 9.0
        return round(band, 1)
    
    def _band_to_classification(self, band: float) -> Dict[str, Any]:
        """Convert band score to classification with color and risk level"""
        # Sort thresholds descending by min_band so the first match wins — eliminates gaps
        for classification, (min_band, max_band, risk_level, emoji) in sorted(
            self.band_thresholds.items(), key=lambda x: x[1][0], reverse=True
        ):
            if band >= min_band:
                return {
                    "classification": classification,
                    "band": band,
                    "risk_level": risk_level,
                    "emoji": emoji,
                    "min_band": min_band,
                    "max_band": max_band
                }

        return {
            "classification": "blacklisted",
            "band": band,
            "risk_level": "Extreme Risk",
            "emoji": "⛔",
            "min_band": 0,
            "max_band": 0.9
        }
    
    def generate_report(self, vessel_name: str, imo_number: str, 
                       vessel_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate complete vessel rating report"""
        logger.info(f"Generating report for {vessel_name} (IMO: {imo_number})")
        
        # Step 1: Calculate all module scores
        module_results = self.calculate_all_module_scores(vessel_data)
        
        # Step 2: Calculate final score
        final_score_data = self.calculate_final_score(module_results)
        final_score = final_score_data["final_score"]
        
        # Step 3: Convert to band rating
        final_band = self._score_to_band(final_score)
        
        # Step 4: Apply cap overrides (ceiling — does not force a value, only limits upside)
        override_band, override_reason = self.apply_critical_overrides(module_results, vessel_data)

        if override_band is not None:
            final_band = min(final_band, override_band)
            override_applied = True
        else:
            override_applied = False
        
        # Step 5: Get classification
        classification = self._band_to_classification(final_band)
        
        # Step 6: Extract alerts and anomalies
        alerts = self._extract_alerts(module_results, vessel_data)
        
        # Step 7: Module breakdown
        module_breakdown = self._create_module_breakdown(module_results)
        
        report = {
            "vessel_info": {
                "vessel_name": vessel_name,
                "imo_number": imo_number,
                "analysis_timestamp": self._get_timestamp(),
            },
            "scoring": {
                "final_score": round(final_score, 2),  # 0-100
                "final_band": final_band,  # 0-9
                "classification": classification["classification"],
                "risk_level": classification["risk_level"],
                "emoji_indicator": classification["emoji"],
                "override_applied": override_applied,
                "override_reason": override_reason,
            },
            "module_breakdown": module_breakdown,
            "alerts": alerts,
            "summary": self._generate_summary(final_band, classification, alerts),
        }
        
        return report
    
    def _extract_alerts(self, module_results: Dict[str, Dict[str, Any]], 
                       vessel_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract critical alerts and anomalies"""
        alerts = []
        
        # Sanctions alert
        sanctions = vessel_data.get("sanctions", {})
        if sanctions.get("ofac_hit") or sanctions.get("un_hit") or sanctions.get("eu_hit"):
            alerts.append({
                "severity": "CRITICAL",
                "type": "SANCTIONS_HIT",
                "message": "⚠️ Vessel or owner on international sanctions lists",
                "emoji": "🚫"
            })
        
        # AIS gaps alert
        ais_details = module_results.get("ais", {}).get("details", {})
        gap_hours = ais_details.get("ais_gap_hours", 0)
        if gap_hours > 24:
            alerts.append({
                "severity": "HIGH",
                "type": "AIS_GAP",
                "message": f"⚠️ AIS signal gap detected: {gap_hours:.1f} hours",
                "emoji": "📡"
            })
        
        # Spoofing alert
        if ais_details.get("spoofing_detected"):
            alerts.append({
                "severity": "CRITICAL",
                "type": "AIS_SPOOFING",
                "message": "⚠️ Potential AIS spoofing detected",
                "emoji": "🚨"
            })
        
        # Dark activity alert
        if ais_details.get("dark_activity"):
            alerts.append({
                "severity": "HIGH",
                "type": "DARK_ACTIVITY",
                "message": "⚠️ Suspicious dark activity detected",
                "emoji": "🌑"
            })
        
        # High-risk port calls
        risk_details = module_results.get("risk_compliance", {}).get("details", {})
        high_risk_ports = risk_details.get("high_risk_ports", 0)
        if high_risk_ports > 0:
            alerts.append({
                "severity": "MEDIUM",
                "type": "HIGH_RISK_PORT_CALLS",
                "message": f"⚠️ {high_risk_ports} high-risk port call(s) detected",
                "emoji": "🚢"
            })
        
        # STS transfers alert
        sts_transfers = risk_details.get("sts_transfers", 0)
        if sts_transfers > 2:
            alerts.append({
                "severity": "MEDIUM",
                "type": "FREQUENT_STS",
                "message": f"⚠️ Frequent Ship-to-Ship transfers: {sts_transfers}",
                "emoji": "⚓"
            })
        
        # War zone alert
        weather = vessel_data.get("weather", {})
        if weather.get("war_zone"):
            alerts.append({
                "severity": "HIGH",
                "type": "WAR_ZONE",
                "message": "⚠️ Vessel in or near war zone",
                "emoji": "💥"
            })
        
        # Piracy zone alert
        if weather.get("piracy_zone"):
            alerts.append({
                "severity": "MEDIUM",
                "type": "PIRACY_ZONE",
                "message": "⚠️ Vessel in piracy-prone area",
                "emoji": "🏴‍☠️"
            })
        
        return sorted(alerts, key=lambda x: {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}.get(x["severity"], 4))
    
    def _create_module_breakdown(self, module_results: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create module-by-module breakdown for display"""
        module_names = {
            "general_info": "General Information",
            "ownership": "Ownership Information",
            "ais": "AIS Information",
            "risk_compliance": "Risk & Compliance",
            "environmental": "Environmental & Voyage",
        }
        
        breakdown = []
        for module_key, module_data in module_results.items():
            breakdown.append({
                "module": module_names.get(module_key, module_key),
                "code": module_key,
                "score": round(module_data["raw_score"], 1),
                "band": module_data["band_score"],
                "weight_percent": self.weights.get(module_key, 0),
                "weighted_contribution": round(module_data["weighted_score"], 2),
                "details": module_data.get("details", {}),
                "emoji": self._get_emoji_for_band(module_data["band_score"]),
            })
        
        return sorted(breakdown, key=lambda x: x["weight_percent"], reverse=True)
    
    def _generate_summary(self, band: float, classification: Dict[str, Any], 
                         alerts: List[Dict[str, Any]]) -> str:
        """Generate human-readable summary"""
        critical_alerts = len([a for a in alerts if a["severity"] == "CRITICAL"])
        high_alerts = len([a for a in alerts if a["severity"] == "HIGH"])
        
        summary = f"{classification['emoji']} **{classification['classification'].upper()}** Vessel (Band: {band:.1f}/9.0)\n"
        summary += f"Risk Level: {classification['risk_level']}\n"
        
        if critical_alerts > 0:
            summary += f"⚠️ **{critical_alerts} Critical Alert(s)** - Immediate review recommended\n"
        if high_alerts > 0:
            summary += f"⚠️ **{high_alerts} High-Risk Alert(s)** - Close monitoring recommended\n"
        
        return summary
    
    def _get_emoji_for_band(self, band: float) -> str:
        """Get emoji indicator for band score"""
        if band >= 8:
            return "🟢"
        elif band >= 6:
            return "🟡"
        elif band >= 4:
            return "🟠"
        else:
            return "🔴"
    
    @staticmethod
    def _get_timestamp() -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.utcnow().isoformat()


def get_scoring_engine() -> ScoringEngine:
    """Factory function to get scoring engine instance"""
    return ScoringEngine()


if __name__ == "__main__":
    # Test scoring engine
    from api_integration.providers import get_api_integration
    
    api = get_api_integration()
    engine = get_scoring_engine()
    
    # Fetch data
    vessel_data = api.fetch_all_vessel_data("Test Vessel", "9999999")
    
    # Generate report
    report = engine.generate_report("Test Vessel", "9999999", vessel_data)
    
    # Pretty print
    import json
    print(json.dumps(report, indent=2, default=str))
