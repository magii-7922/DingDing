"""Remembrance Cat core — UI-agnostic game + LLM logic."""

from .constants import DESKTOP_ZONES, SPRITE_CATALOG
from .progress import load_day_progress, reset_7_day_story, save_day_progress, set_story_day
from .runner import advance_day
from .vision import scan_cat_photo

__all__ = [
    "DESKTOP_ZONES",
    "SPRITE_CATALOG",
    "advance_day",
    "load_day_progress",
    "reset_7_day_story",
    "save_day_progress",
    "scan_cat_photo",
    "set_story_day",
]
