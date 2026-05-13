"""
Storage data adapters for the Vessel Rating System.

The scoring engine expects one vessel_data dictionary. This module lets the
application build that dictionary from local storage, an uploaded device file,
or a configured cloud storage path/URL.
"""

from __future__ import annotations

import csv
import io
import json
import logging
from pathlib import Path
from typing import Any, Dict, Iterable, Optional

import requests

from config import STORAGE_CONFIG

logger = logging.getLogger(__name__)

SOURCE_LOCAL = "local_storage"
SOURCE_DEVICE = "device"
SOURCE_CLOUD = "cloud"


class StorageError(Exception):
    """Raised when storage data cannot be loaded or matched."""


def _project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _resolve_path(value: str | Path) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return _project_root() / path


def _read_json_bytes(raw: bytes) -> Any:
    return json.loads(raw.decode("utf-8-sig"))


def _read_csv_bytes(raw: bytes) -> list[Dict[str, Any]]:
    text = raw.decode("utf-8-sig")
    return list(csv.DictReader(io.StringIO(text)))


def _load_file(path: Path) -> Any:
    suffix = path.suffix.lower()
    raw = path.read_bytes()
    if suffix == ".json":
        return _read_json_bytes(raw)
    if suffix == ".csv":
        return _read_csv_bytes(raw)
    raise StorageError(f"Unsupported storage file type: {path.suffix}")


def _iter_records(payload: Any) -> Iterable[Dict[str, Any]]:
    if isinstance(payload, list):
        for item in payload:
            if isinstance(item, dict):
                yield item
        return

    if not isinstance(payload, dict):
        return

    for key in ("vessels", "records", "data"):
        value = payload.get(key)
        if isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    yield item
            return

    yield payload


def _matches(record: Dict[str, Any], vessel_name: str, imo_number: str) -> bool:
    record_info = record.get("vessel_info", {}) if isinstance(record.get("vessel_info"), dict) else {}
    record_imo = str(record.get("imo_number") or record.get("imo") or record_info.get("imo_number") or "").strip()
    record_name = str(record.get("vessel_name") or record_info.get("vessel_name") or "").strip().lower()
    return record_imo == str(imo_number).strip() or record_name == vessel_name.strip().lower()


def normalize_vessel_data(record: Dict[str, Any], vessel_name: str, imo_number: str) -> Dict[str, Any]:
    """Normalize supported JSON/CSV shapes into the scoring-engine schema."""
    if all(key in record for key in ("vessel_info", "ais_data", "ownership", "sanctions", "weather", "compliance")):
        data = dict(record)
        data.setdefault("risk_events", {})
        data.setdefault("port_call_history", {})
        return data

    data = {
        "vessel_info": {
            "vessel_name": record.get("vessel_name", vessel_name),
            "imo_number": str(record.get("imo_number") or record.get("imo") or imo_number),
            "flag": record.get("flag", "Unknown"),
            "vessel_type": record.get("vessel_type", "Unknown"),
            "dimensions": {
                "length": _float(record.get("length"), 0),
                "width": _float(record.get("width"), 0),
                "depth": _float(record.get("depth"), 0),
                "tonnage": {
                    "gross": _float(record.get("gross_tonnage"), 0),
                    "dead_weight": _float(record.get("dead_weight_tonnage"), 0),
                },
            },
            "engine": {
                "type": record.get("engine_type", ""),
                "fuel_type": record.get("fuel_type", ""),
            },
            "capacity": _float(record.get("capacity"), 0),
            "builder": record.get("builder", ""),
            "built_year": _int(record.get("built_year"), 2015),
            "classification_society": record.get("classification_society", ""),
            "last_updated": record.get("last_updated", ""),
        },
        "ais_data": {
            "position": {
                "latitude": _float(record.get("latitude"), 0),
                "longitude": _float(record.get("longitude"), 0),
                "timestamp": record.get("ais_timestamp", ""),
            },
            "movement": {
                "speed": _float(record.get("speed"), 0),
                "course": _float(record.get("course"), 0),
                "heading": _float(record.get("heading"), 0),
            },
            "status": record.get("ais_status", "Unknown"),
            "ais_gaps": {"gap_hours": _float(record.get("ais_gap_hours"), 0)},
            "anomalies": {
                "spoofing_detected": _bool(record.get("spoofing_detected")),
                "dark_activity": _bool(record.get("dark_activity")),
                "unusual_speed": _bool(record.get("unusual_speed")),
                "unusual_route": _bool(record.get("unusual_route")),
            },
        },
        "ownership": {
            "current_owner": record.get("current_owner", ""),
            "registered_owner": record.get("registered_owner", ""),
            "beneficial_owner": record.get("beneficial_owner", ""),
            "ownership_changes": _int(record.get("ownership_changes"), 0),
            "name_changes": _int(record.get("name_changes"), 0),
            "manager": record.get("manager", ""),
            "classification_society": record.get("classification_society", ""),
            "p_and_i_club": record.get("p_and_i_club", ""),
            "reputation_score": _float(record.get("reputation_score"), 0.75),
        },
        "sanctions": {
            "ofac_hit": _bool(record.get("ofac_hit")),
            "un_hit": _bool(record.get("un_hit")),
            "eu_hit": _bool(record.get("eu_hit")),
            "sanctioned_entities": [],
            "risk_level": record.get("sanctions_risk_level", "LOW"),
            "last_checked": record.get("sanctions_last_checked", ""),
        },
        "weather": {
            "weather_conditions": {
                "temperature": _float(record.get("temperature"), 25),
                "wind_speed": _float(record.get("wind_speed"), 10),
                "sea_state": record.get("sea_state", "Moderate"),
                "visibility": record.get("visibility", "Good"),
                "wave_height": _float(record.get("wave_height"), 1.5),
            },
            "piracy_zone": _bool(record.get("piracy_zone")),
            "war_zone": _bool(record.get("war_zone")),
            "storm_warning": _bool(record.get("storm_warning")),
            "last_updated": record.get("weather_last_updated", ""),
        },
        "compliance": {
            "certificates": record.get("certificates", []) if isinstance(record.get("certificates"), list) else [],
            "insurance_valid": _bool(record.get("insurance_valid"), default=True),
            "inspection_status": record.get("inspection_status", "CLEAR"),
            "port_state_control": {
                "inspections": _int(record.get("psc_inspections"), 0),
                "deficiencies": _int(record.get("psc_deficiencies"), 0),
            },
        },
        "risk_events": {},
        "port_call_history": {
            "total_port_calls": _int(record.get("total_port_calls"), 0),
            "high_risk_ports": _int(record.get("high_risk_ports"), 0),
            "sts_transfers": _int(record.get("sts_transfers"), 0),
            "recent_ports": [],
        },
    }
    return data


def _float(value: Any, default: float) -> float:
    try:
        if value in (None, ""):
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def _int(value: Any, default: int) -> int:
    try:
        if value in (None, ""):
            return default
        return int(float(value))
    except (TypeError, ValueError):
        return default


def _bool(value: Any, default: bool = False) -> bool:
    if value in (None, ""):
        return default
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes", "y", "on"}


class VesselStorageManager:
    """Finds vessel data in local, device-imported, or cloud storage."""

    def __init__(self, local_root: str | Path | None = None):
        self.local_root = _resolve_path(local_root or STORAGE_CONFIG["local_storage_path"])
        self.device_import_root = _resolve_path(STORAGE_CONFIG["device_import_path"])

    def ensure_storage(self) -> None:
        self.local_root.mkdir(parents=True, exist_ok=True)
        self.device_import_root.mkdir(parents=True, exist_ok=True)

    def fetch_vessel_data(
        self,
        vessel_name: str,
        imo_number: str,
        source: str = SOURCE_LOCAL,
        uploaded_file: Any | None = None,
        cloud_location: str | None = None,
    ) -> Dict[str, Any]:
        self.ensure_storage()

        if source == SOURCE_DEVICE:
            if uploaded_file is None:
                raise StorageError("Please choose a device file before analyzing.")
            payload = self._load_uploaded_file(uploaded_file)
            return self._find_match(payload, vessel_name, imo_number)

        if source == SOURCE_CLOUD:
            payload = self._load_cloud_payload(cloud_location)
            return self._find_match(payload, vessel_name, imo_number)

        payloads = [self._load_local_file(path) for path in self._data_files(self.local_root)]
        for payload in payloads:
            try:
                return self._find_match(payload, vessel_name, imo_number)
            except StorageError:
                continue
        raise StorageError(f"No local storage record found for {vessel_name} / IMO {imo_number}.")

    def _data_files(self, root: Path) -> Iterable[Path]:
        allowed = set(STORAGE_CONFIG["allowed_extensions"])
        return sorted(path for path in root.rglob("*") if path.is_file() and path.suffix.lower() in allowed)

    def _load_local_file(self, path: Path) -> Any:
        logger.info("Loading vessel storage file: %s", path)
        return _load_file(path)

    def _load_uploaded_file(self, uploaded_file: Any) -> Any:
        name = Path(uploaded_file.name).name
        suffix = Path(name).suffix.lower()
        if suffix not in STORAGE_CONFIG["allowed_extensions"]:
            raise StorageError(f"Unsupported device file type: {suffix}")

        raw = uploaded_file.getvalue()
        target = self.device_import_root / name
        target.write_bytes(raw)
        if suffix == ".json":
            return _read_json_bytes(raw)
        if suffix == ".csv":
            return _read_csv_bytes(raw)
        raise StorageError(f"Unsupported device file type: {suffix}")

    def _load_cloud_payload(self, cloud_location: str | None) -> Any:
        location = (cloud_location or STORAGE_CONFIG.get("cloud_storage_path") or "").strip()
        if not location:
            raise StorageError("Provide a cloud storage URL or set VRS_CLOUD_STORAGE_PATH.")

        if location.startswith(("http://", "https://")):
            response = requests.get(location, timeout=20)
            response.raise_for_status()
            suffix = Path(location.split("?", 1)[0]).suffix.lower()
            if suffix == ".csv":
                return _read_csv_bytes(response.content)
            return _read_json_bytes(response.content)

        path = _resolve_path(location)
        if path.is_dir():
            payloads = [_load_file(file_path) for file_path in self._data_files(path)]
            return {"vessels": [record for payload in payloads for record in _iter_records(payload)]}
        if path.is_file():
            return _load_file(path)
        raise StorageError(f"Cloud storage location not found: {location}")

    def _find_match(self, payload: Any, vessel_name: str, imo_number: str) -> Dict[str, Any]:
        for record in _iter_records(payload):
            if _matches(record, vessel_name, imo_number):
                return normalize_vessel_data(record, vessel_name, imo_number)
        raise StorageError(f"No storage record found for {vessel_name} / IMO {imo_number}.")


def get_storage_manager() -> VesselStorageManager:
    return VesselStorageManager()
