"""Validate synthetic fixture availability for local demos.

The app ships with committed synthetic JSON files, so seeding means verifying the
fixtures are present and parseable. No real PHI is generated or downloaded.
"""
import json
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[1] / "backend" / "app" / "data" / "synthetic"
FILES = ["patients.json", "encounters.json", "labs.json", "medications.json", "notes.json", "social_determinants.json"]


def main() -> None:
    for name in FILES:
        path = DATA_DIR / name
        rows = json.loads(path.read_text())
        print(f"{name}: {len(rows)} synthetic rows")


if __name__ == "__main__":
    main()
