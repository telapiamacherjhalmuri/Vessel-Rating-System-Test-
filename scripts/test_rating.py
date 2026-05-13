"""Quick smoke-test: score 5 vessels from the uploaded dataset."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scoring_engine.engine import ScoringEngine
from storage.sources import VesselStorageManager

engine  = ScoringEngine()
storage = VesselStorageManager()

TESTS = [
    ("HOOT",              "9267962"),
    ("ADENA",             "9254862"),
    ("AKADEMIK CHERSKIY", "8770261"),
    ("ALARA",             "9741724"),
    ("CLEAN OCEAN",       "9637492"),
]

print(f"{'Vessel':<25} {'IMO':<12} {'Band':>6}  {'Risk Level':<22} {'Alerts'}")
print("-" * 82)
for name, imo in TESTS:
    try:
        data   = storage.fetch_vessel_data(name, imo)
        report = engine.generate_report(name, imo, data)
        band   = report.get("scoring", {}).get("final_band", 0)
        lvl    = report.get("scoring", {}).get("risk_level", "?")
        alerts = len(report.get("alerts", []))
        print(f"{name:<25} {imo:<12} {band:>6.2f}  {lvl:<22} {alerts} alert(s)")
    except Exception as e:
        print(f"{name:<25} {imo:<12}  ERROR: {e}")
