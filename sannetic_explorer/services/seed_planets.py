"""Seed the Sun and the eight planets from Data/ JSON into Postgres.

Idempotent: bodies that already exist (matched by name) are left unchanged.
`make up` calls this on backend startup. `make db-seed` runs it again.
"""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from ..models.celestial_bodies import CelestialBody
from ..models.orbital_parameters import OrbitalParameters
from ..models.physical_characteristics import PhysicalCharacteristics
from .database import SessionLocal, init_database

logger = logging.getLogger(__name__)

AU_KM = 149_597_870.7

# JSON files do not carry a display color. These match the previous demo palette.
COLORS = {
    "Sun": "#FDB813",
    "Mercury": "#8c7853",
    "Venus": "#e7cdcd",
    "Earth": "#6b93d6",
    "Mars": "#c1440e",
    "Jupiter": "#d8ca9d",
    "Saturn": "#fad5a5",
    "Uranus": "#4fd0e7",
    "Neptune": "#4b70dd",
}

# Mercury's JSON has no orbital speed. The other planets read it from the file.
SPEED_FALLBACK_KMS = {
    "Mercury": 47.36,
    "Venus": 35.02,
    "Earth": 29.78,
    "Mars": 24.07,
    "Jupiter": 13.07,
    "Saturn": 9.68,
    "Uranus": 6.80,
    "Neptune": 5.43,
}

SKIP_FILES = {"index.json", "template.json", ".template.json"}


def data_root() -> Path:
    """Directory that contains Planets/ and Stars/."""
    configured = os.getenv("DATA_DIR")
    if configured:
        return Path(configured)
    packaged = Path(__file__).resolve().parents[2] / "Data"
    if packaged.is_dir():
        return packaged
    return Path("/app/Data")


def _num(node: Any, default: Optional[float] = None) -> Optional[float]:
    if isinstance(node, dict):
        return _num(node.get("value"), default)
    if node in (None, "", "noValue", "none"):
        return default
    try:
        return float(node)
    except (TypeError, ValueError):
        return default


def _unit(node: Any) -> str:
    if isinstance(node, dict) and isinstance(node.get("unit"), str):
        return node["unit"].strip().lower()
    return ""


def _au(node: Any, default: Optional[float] = None) -> Optional[float]:
    value = _num(node)
    if value is None:
        return default
    unit = _unit(node)
    if unit in {"km", "kilometer", "kilometers"}:
        return value / AU_KM
    return value


def _km_from_au_node(node: Any) -> Optional[float]:
    au = _au(node)
    if au is None:
        return None
    return au * AU_KM


def _atmosphere(data: Dict[str, Any]) -> tuple[bool, Optional[dict]]:
    atmosphere = data.get("atmosphere") or {}
    composition = atmosphere.get("composition")
    if composition in (None, "", "noValue", "none"):
        return False, None
    if isinstance(composition, dict):
        return True, composition
    if isinstance(composition, str):
        return True, {"composition": composition}
    return False, None


def parse_planet(data: Dict[str, Any]) -> Dict[str, Any]:
    """Map a Data/Planets/*.json document onto model fields."""
    name = data["name"]
    orbit = data.get("orbit") or {}
    diameter_km = _num(data.get("diameter"))
    radius_km = diameter_km / 2 if diameter_km else None
    distance_au = _au(data.get("distanceFromSun"))
    if distance_au is None:
        distance_au = _au((orbit.get("semiMajorAxis")))
    has_atmosphere, composition = _atmosphere(data)
    rings = data.get("rings") or {}
    speed = _num((orbit.get("orbitalSpeed")))
    if speed is None:
        speed = SPEED_FALLBACK_KMS.get(name)
    temp = data.get("surfaceTemperature") or {}
    temp_min_c = _num(temp.get("min")) if isinstance(temp, dict) else None
    temp_max_c = _num(temp.get("max")) if isinstance(temp, dict) else None
    surface_k = None
    if temp_min_c is not None and temp_max_c is not None:
        surface_k = ((temp_min_c + temp_max_c) / 2) + 273.15
    rotation_days = _num(data.get("rotationPeriod"))
    return {
        "name": name,
        "kind": "planet",
        "subtype": data.get("type"),
        "mass_kg": _num(data.get("mass")),
        "radius_km": radius_km,
        "mean_distance_au": distance_au,
        "orbital_speed_kms": speed,
        "surface_gravity_ms2": _num(data.get("gravity")),
        "color_hex": COLORS.get(name, "#aaaaaa"),
        "orbital_period_days": _num(data.get("orbitalPeriod")),
        "semi_major_axis_km": _km_from_au_node(orbit.get("semiMajorAxis"))
        or (distance_au * AU_KM if distance_au is not None else None),
        "eccentricity": _num(orbit.get("eccentricity")),
        "inclination_degrees": _num(orbit.get("inclination")),
        "longitude_ascending_node_degrees": _num(orbit.get("longitudeOfAscendingNode")),
        "argument_periapsis_degrees": _num(orbit.get("argumentOfPeriapsis")),
        "mean_anomaly_degrees": _num(orbit.get("meanAnomaly")),
        "epoch": orbit.get("epoch") if isinstance(orbit.get("epoch"), str) else "J2000",
        "rotation_period_hours": rotation_days * 24 if rotation_days is not None else None,
        "has_atmosphere": has_atmosphere,
        "atmospheric_composition": composition,
        "has_rings": bool(rings.get("hasRings")),
        "surface_temperature_k": surface_k,
        "surface_type": "rocky" if "terrestrial" in str(data.get("type", "")).lower() else "gaseous",
        "mutual_perturbations": orbit.get("mutualPerturbations")
        if isinstance(orbit.get("mutualPerturbations"), list)
        else None,
    }


def parse_sun(data: Dict[str, Any]) -> Dict[str, Any]:
    physical = data.get("physicalCharacteristics") or {}
    stellar = data.get("stellarParameters") or {}
    return {
        "name": data.get("name") or "Sun",
        "kind": "star",
        "subtype": data.get("type"),
        "mass_kg": _num(physical.get("mass")),
        "radius_km": _num(physical.get("radius")),
        "mean_distance_au": 0.0,
        "orbital_speed_kms": None,
        "surface_gravity_ms2": _num(physical.get("surfaceGravity")),
        "escape_velocity_kms": _num(physical.get("escapeVelocity")),
        "color_hex": COLORS["Sun"],
        "orbital_period_days": None,
        "semi_major_axis_km": None,
        "eccentricity": None,
        "inclination_degrees": None,
        "longitude_ascending_node_degrees": None,
        "argument_periapsis_degrees": None,
        "mean_anomaly_degrees": None,
        "epoch": None,
        "rotation_period_hours": None,
        "has_atmosphere": False,
        "atmospheric_composition": None,
        "has_rings": False,
        "surface_temperature_k": _num(stellar.get("effectiveTemperature")),
        "surface_type": "plasma",
        "mutual_perturbations": None,
    }


def planet_files(root: Optional[Path] = None) -> List[Path]:
    directory = (root or data_root()) / "Planets"
    if not directory.is_dir():
        return []
    files = []
    for path in sorted(directory.glob("*.json")):
        if path.name in SKIP_FILES or path.name.startswith("."):
            continue
        files.append(path)
    return files


def load_records(root: Optional[Path] = None) -> List[Dict[str, Any]]:
    root = root or data_root()
    records: List[Dict[str, Any]] = []
    sun_path = root / "Stars" / "sun.json"
    if sun_path.is_file():
        records.append(parse_sun(json.loads(sun_path.read_text(encoding="utf-8"))))
    for path in planet_files(root):
        records.append(parse_planet(json.loads(path.read_text(encoding="utf-8"))))
    return records


def _insert(session: Session, record: Dict[str, Any], parent_id: Any = None) -> CelestialBody:
    body = CelestialBody(
        name=record["name"],
        type=record["kind"],
        subtype=record.get("subtype"),
        parent_id=parent_id,
        mass_kg=record.get("mass_kg"),
        radius_km=record.get("radius_km"),
        mean_distance_au=record.get("mean_distance_au"),
        orbital_speed_kms=record.get("orbital_speed_kms"),
        surface_gravity_ms2=record.get("surface_gravity_ms2"),
        escape_velocity_kms=record.get("escape_velocity_kms"),
        color_hex=record.get("color_hex"),
        data_quality="good",
        data_sources={"source": "Data/ JSON", "path": "Data/Planets" if record["kind"] == "planet" else "Data/Stars/sun.json"},
    )
    session.add(body)
    session.flush()

    if record["kind"] == "planet":
        session.add(
            OrbitalParameters(
                celestial_body_id=body.id,
                semi_major_axis_km=record.get("semi_major_axis_km"),
                eccentricity=record.get("eccentricity"),
                inclination_degrees=record.get("inclination_degrees"),
                longitude_ascending_node_degrees=record.get("longitude_ascending_node_degrees"),
                argument_periapsis_degrees=record.get("argument_periapsis_degrees"),
                mean_anomaly_degrees=record.get("mean_anomaly_degrees"),
                orbital_period_days=record.get("orbital_period_days"),
                orbital_speed_kms=record.get("orbital_speed_kms"),
                rotation_period_hours=record.get("rotation_period_hours"),
                distance_from_parent_km=record.get("semi_major_axis_km"),
                epoch=record.get("epoch") or "J2000",
                mutual_perturbations=record.get("mutual_perturbations"),
            )
        )
    session.add(
        PhysicalCharacteristics(
            celestial_body_id=body.id,
            has_atmosphere=bool(record.get("has_atmosphere")),
            atmospheric_composition=record.get("atmospheric_composition"),
            has_rings=bool(record.get("has_rings")),
            surface_temperature_k=record.get("surface_temperature_k"),
            surface_type=record.get("surface_type"),
        )
    )
    return body


def seed_solar_system(session: Optional[Session] = None) -> int:
    """Insert any missing Sun/planet rows. Returns the number of new bodies."""
    own_session = session is None
    if own_session:
        init_database()
        session = SessionLocal()
    assert session is not None
    inserted = 0
    try:
        records = load_records()
        if not records:
            logger.warning("No planet JSON found under %s; nothing seeded", data_root())
            return 0
        sun = session.query(CelestialBody).filter(CelestialBody.name == "Sun").one_or_none()
        for record in records:
            existing = session.query(CelestialBody).filter(CelestialBody.name == record["name"]).one_or_none()
            if existing:
                if record["kind"] == "star":
                    sun = existing
                continue
            parent_id = None
            if record["kind"] == "planet" and sun is not None:
                parent_id = sun.id
            created = _insert(session, record, parent_id=parent_id)
            inserted += 1
            if record["kind"] == "star":
                sun = created
            logger.info("Seeded %s (%s)", record["name"], record["kind"])
        session.commit()
        return inserted
    except Exception:
        session.rollback()
        raise
    finally:
        if own_session:
            session.close()


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    added = seed_solar_system()
    session = SessionLocal()
    try:
        planets = session.query(CelestialBody).filter(CelestialBody.type == "planet").count()
        stars = session.query(CelestialBody).filter(CelestialBody.type == "star").count()
    finally:
        session.close()
    print(f"Seed complete. Inserted {added} bodies. Planets in database: {planets}. Stars: {stars}.")


if __name__ == "__main__":
    main()
