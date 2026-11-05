"""Parser checks for the solar-system seed. No database required."""

from pathlib import Path

from sannetic_explorer.services.seed_planets import load_records, planet_files

ROOT = Path(__file__).resolve().parents[2]


def test_planet_files_cover_the_eight_planets():
    names = {path.stem for path in planet_files(ROOT / "Data")}
    assert names == {
        "mercury",
        "venus",
        "earth",
        "mars",
        "jupiter",
        "saturn",
        "uranus",
        "neptune",
    }


def test_load_records_includes_sun_and_eight_planets():
    records = load_records(ROOT / "Data")
    by_name = {record["name"]: record for record in records}
    assert set(by_name) == {
        "Sun",
        "Mercury",
        "Venus",
        "Earth",
        "Mars",
        "Jupiter",
        "Saturn",
        "Uranus",
        "Neptune",
    }
    assert by_name["Sun"]["kind"] == "star"
    assert by_name["Sun"]["radius_km"] == 696340
    earth = by_name["Earth"]
    assert earth["kind"] == "planet"
    assert earth["mean_distance_au"] == 1
    assert earth["radius_km"] == 6371
    assert earth["orbital_period_days"] == 365.25
    assert earth["orbital_speed_kms"] == 29.78
    assert by_name["Mercury"]["orbital_speed_kms"] == 47.36
    assert by_name["Saturn"]["has_rings"] is True
    assert by_name["Mercury"]["has_rings"] is False
    for record in records:
        if record["kind"] != "planet":
            continue
        assert record["mean_distance_au"] and record["mean_distance_au"] > 0
        assert record["radius_km"] and record["radius_km"] > 0
        eccentricity = record["eccentricity"]
        assert eccentricity is None or 0 <= eccentricity < 1
