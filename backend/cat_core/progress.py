import json
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
SAVE_FILE = DATA_DIR / "save_state.json"
PROFILE_FILE = DATA_DIR / "profile.json"


def load_day_progress() -> dict:
    if SAVE_FILE.exists():
        return json.loads(SAVE_FILE.read_text(encoding="utf-8"))
    return {"current_day": 1, "history_log": []}


def save_day_progress(data: dict) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    SAVE_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")


def reset_7_day_story() -> None:
    if SAVE_FILE.exists():
        SAVE_FILE.unlink()


def set_story_day(day: int) -> None:
    progress = load_day_progress()
    progress["current_day"] = day
    save_day_progress(progress)


def load_profile() -> dict | None:
    if not PROFILE_FILE.exists():
        return None
    return json.loads(PROFILE_FILE.read_text(encoding="utf-8"))


def save_profile(profile: dict) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    # Never persist binary image blobs in JSON.
    safe = {k: v for k, v in profile.items() if k != "image"}
    PROFILE_FILE.write_text(json.dumps(safe, indent=2), encoding="utf-8")
