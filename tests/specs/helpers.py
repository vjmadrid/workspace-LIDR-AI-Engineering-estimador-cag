import json
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
SPECS_DIR = ROOT_DIR / "specs"


def load_json(relative_path: str) -> dict:
    return json.loads((SPECS_DIR / relative_path).read_text(encoding="utf-8"))


def resolve_ref(schema: dict, ref: str) -> dict:
    parts = ref.removeprefix("#/").split("/")
    current = schema
    for part in parts:
        current = current[part]
    return current
