"""FastAPI backend for Remembrance Cat web prototype."""

from __future__ import annotations

import io
from pathlib import Path
from typing import Any

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from PIL import Image
from pydantic import BaseModel, Field

from cat_core.constants import DESKTOP_ZONES, SPRITE_CATALOG
from cat_core.llm import MissingApiKeyError, get_api_key
from cat_core.progress import (
    load_day_progress,
    load_profile,
    reset_7_day_story,
    save_profile,
    set_story_day,
)
from cat_core.runner import advance_day
from cat_core.vision import scan_cat_photo

ROOT = Path(__file__).resolve().parent.parent
FRONTEND_DIST = ROOT / "frontend" / "dist"
FRONTEND_PUBLIC = ROOT / "frontend" / "public"

app = FastAPI(title="Remembrance Cat", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if (FRONTEND_PUBLIC / "sprites").exists():
    app.mount(
        "/sprites",
        StaticFiles(directory=FRONTEND_PUBLIC / "sprites"),
        name="sprites",
    )


class AdvanceRequest(BaseModel):
    player_note: str = ""


class JumpRequest(BaseModel):
    day: int = Field(ge=1, le=99)


def _public_profile(profile: dict | None) -> dict | None:
    if not profile:
        return None
    return {
        "owner_name": profile.get("owner_name", "friend"),
        "name": profile.get("name", "Cat"),
        "temperament": profile.get("temperament", "Playful"),
        "volume": profile.get("volume", "Quiet"),
        "chonk": profile.get("chonk", "Standard"),
        "fav_treat": profile.get("fav_treat", "salmon treats"),
        "sprite": profile.get("sprite", "orange"),
        "ai_notes": profile.get("ai_notes", ""),
    }


@app.get("/api/health")
def health() -> dict[str, Any]:
    has_key = True
    try:
        get_api_key()
    except MissingApiKeyError:
        has_key = False
    return {"ok": True, "has_api_key": has_key}


@app.get("/api/meta")
def meta() -> dict[str, Any]:
    return {
        "zones": DESKTOP_ZONES,
        "sprites": list(SPRITE_CATALOG.keys()),
        "temperaments": ["Playful", "Bitey", "Lazy", "Affectionate"],
        "volumes": ["Loud", "Quiet"],
        "chonks": ["Slender", "Standard", "Absolute Chonk"],
    }


@app.get("/api/state")
def state() -> dict[str, Any]:
    progress = load_day_progress()
    return {
        "current_day": progress.get("current_day", 1),
        "history_log": progress.get("history_log", []),
        "profile": _public_profile(load_profile()),
    }


@app.post("/api/profile")
async def create_profile(
    owner_name: str = Form("friend"),
    name: str = Form("Kitty"),
    temperament: str = Form("Playful"),
    volume: str = Form("Quiet"),
    chonk: str = Form("Standard"),
    fav_treat: str = Form("salmon treats"),
    photo: UploadFile | None = File(None),
) -> dict[str, Any]:
    profile: dict[str, Any] = {
        "owner_name": (owner_name or "friend").strip() or "friend",
        "name": (name or "Kitty").strip() or "Kitty",
        "temperament": temperament,
        "volume": volume,
        "chonk": chonk,
        "fav_treat": (fav_treat or "salmon treats").strip() or "salmon treats",
    }

    if photo is not None and photo.filename:
        raw = await photo.read()
        try:
            img = Image.open(io.BytesIO(raw)).convert("RGB")
            img.thumbnail((512, 512))
            profile["image"] = img
        except Exception as exc:
            raise HTTPException(status_code=400, detail=f"Invalid image: {exc}") from exc

    scan_cat_photo(profile)
    save_profile(profile)
    reset_7_day_story()

    return {
        "profile": _public_profile(profile),
        "current_day": 1,
    }


@app.post("/api/day/advance")
def day_advance(body: AdvanceRequest) -> dict[str, Any]:
    profile = load_profile()
    if not profile:
        raise HTTPException(
            status_code=400,
            detail="No companion yet. Create a profile first.",
        )
    try:
        result = advance_day(profile, player_note=body.player_note or "")
    except MissingApiKeyError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"LLM error: {exc}") from exc

    result["profile"] = _public_profile(profile)
    return result


@app.post("/api/day/reset")
def day_reset() -> dict[str, Any]:
    reset_7_day_story()
    return {"current_day": 1, "message": "Story reset to Day 1."}


@app.post("/api/day/jump")
def day_jump(body: JumpRequest) -> dict[str, Any]:
    set_story_day(body.day)
    return {"current_day": body.day, "message": f"Jumped to Day {body.day}."}


@app.get("/api")
def api_root() -> dict[str, str]:
    return {
        "message": "Remembrance Cat API",
        "docs": "/docs",
        "health": "/api/health",
    }


if FRONTEND_DIST.exists():
    app.mount("/", StaticFiles(directory=FRONTEND_DIST, html=True), name="frontend")
