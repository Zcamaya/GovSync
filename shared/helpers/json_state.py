import json
from pathlib import Path
from typing import Any


def load_json_dict(path: str | Path, default: dict[str, Any] | None = None) -> dict[str, Any]:
    fallback = default.copy() if isinstance(default, dict) else {}
    file_path = Path(path)
    if not file_path.exists():
        return fallback

    try:
        with open(file_path, "r", encoding="utf-8") as input_file:
            data = json.load(input_file)
    except (OSError, json.JSONDecodeError):
        return fallback

    return data if isinstance(data, dict) else fallback


def save_json_dict(path: str | Path, data: dict[str, Any]) -> None:
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as output_file:
        json.dump(data, output_file, indent=2)
