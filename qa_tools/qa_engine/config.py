from pathlib import Path
import os

ROOT = Path(__file__).resolve().parents[2]
QA_OUTPUT_DIR = ROOT / "qa_output"
SCREENSHOT_DIR = QA_OUTPUT_DIR / "screenshots"
REPORTS_DIR = QA_OUTPUT_DIR / "reports"
LOG_DIR = QA_OUTPUT_DIR / "logs"

RESOLUTIONS = [
    (3840, 2160),
    (2560, 1440),
    (1920, 1080),
    (1600, 900),
    (1366, 768),
    (1280, 720),
    (1024, 768),
    (800, 600),
]

DPI_SCALES = [100, 125, 150, 175, 200]

for directory in [QA_OUTPUT_DIR, SCREENSHOT_DIR, REPORTS_DIR, LOG_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

DEFAULT_TIMEOUT_MS = 5000


def ensure_env():
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    if os.name == "nt":
        windir = os.environ.get("WINDIR")
        if windir:
            font_dir = os.path.join(windir, "Fonts")
            if os.path.isdir(font_dir):
                os.environ.setdefault("QT_QPA_FONTDIR", font_dir)
    return os.environ["QT_QPA_PLATFORM"]
