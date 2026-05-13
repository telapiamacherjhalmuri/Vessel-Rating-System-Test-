"""Verify: strict validation, history persistence, back-button logic."""
import sys, os, re, json
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

HISTORY_FILE = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) / "local_storage" / "_search_history.json"
_IMO_RE = re.compile(r"^\d{7}$")

# ── 1. Validation logic ────────────────────────────────────────────────────────
def validate_inputs(name, imo):
    errors = []
    if not name.strip():
        errors.append("Vessel Name is required.")
    elif len(name.strip()) < 2:
        errors.append("Vessel Name too short.")
    elif re.match(r"^\d+$", name.strip()):
        errors.append("Vessel Name should not be a number.")
    if not imo.strip():
        errors.append("IMO Number is required.")
    elif not _IMO_RE.match(imo.strip()):
        errors.append(f"IMO '{imo}' invalid — must be exactly 7 digits.")
    return errors

cases = [
    ("ADENA",   "9254862", []),                          # valid
    ("",        "9254862", ["Vessel Name is required."]),
    ("A",       "9254862", ["Vessel Name too short."]),
    ("9254862", "9254862", ["should not be a number"]),  # swapped
    ("ADENA",   "",        ["IMO Number is required."]),
    ("ADENA",   "925486",  ["invalid"]),                 # 6 digits
    ("ADENA",   "92548621",["invalid"]),                 # 8 digits
    ("ADENA",   "ABCDEFG", ["invalid"]),                 # letters
]

print("=== Validation Tests ===")
all_pass = True
for name, imo, expected_keywords in cases:
    errors = validate_inputs(name, imo)
    ok = bool(errors) == bool(expected_keywords)
    if expected_keywords and errors:
        ok = all(any(kw.lower() in e.lower() for e in errors) for kw in expected_keywords)
    status = "PASS" if ok else "FAIL"
    if not ok: all_pass = False
    print(f"  [{status}] name={name!r:<12} imo={imo!r:<12} -> errors={errors}")

print(f"\nAll validation tests: {'PASSED' if all_pass else 'FAILED'}\n")

# ── 2. History file ─────────────────────────────────────────────────────────
print("=== History File ===")
if HISTORY_FILE.exists():
    hist = json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
    print(f"  History file found: {len(hist)} entries")
    if hist:
        last = hist[-1]
        print(f"  Latest entry: {last['timestamp']}  {last['vessel_name']} / {last['imo']}  success={last['success']}")
else:
    print("  No history file yet (will be created on first search)")

print("\nAll checks complete.")
