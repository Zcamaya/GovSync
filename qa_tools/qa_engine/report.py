from __future__ import annotations

from pathlib import Path
import json
from datetime import datetime

from qa_tools.qa_engine.config import REPORTS_DIR, QA_OUTPUT_DIR


class ReportWriter:
    def __init__(self, base_dir: Path | None = None):
        self.base_dir = base_dir or REPORTS_DIR
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def write_json(self, name: str, payload: object) -> Path:
        path = self.base_dir / f"{name}.json"
        path.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
        return path

    def write_markdown(self, name: str, content: str) -> Path:
        path = self.base_dir / f"{name}.md"
        path.write_text(content, encoding="utf-8")
        return path
