from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
MODEL_DIR = ROOT / "models"
OUTPUT_DIR = ROOT / "outputs"
for directory in (DATA_DIR, MODEL_DIR, OUTPUT_DIR):
    directory.mkdir(parents=True, exist_ok=True)

RANDOM_STATE = 42
TARGET_COLUMN = "label"
