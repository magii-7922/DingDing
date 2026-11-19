import base64
import io
import json

from langchain_core.messages import HumanMessage
from PIL import Image

from .constants import SPRITE_CATALOG
from .llm import MissingApiKeyError, get_vision_llm


def scan_cat_photo(profile: dict) -> dict:
    """Pick a sprite from an optional PIL image; mutate and return profile."""
    if "image" not in profile or profile["image"] is None:
        profile.setdefault("sprite", "orange")
        profile.setdefault(
            "ai_notes",
            "No photo provided; defaulted to chaotic orange tabby.",
        )
        return profile

    image: Image.Image = profile["image"]
    buf = io.BytesIO()
    image.convert("RGB").save(buf, format="JPEG")
    b64_img = base64.b64encode(buf.getvalue()).decode("utf-8")

    try:
        vision_llm = get_vision_llm()
        msg = HumanMessage(
            content=[
                {
                    "type": "text",
                    "text": (
                        "Analyze this cat photo. Reply ONLY with valid JSON containing two keys: "
                        f"'sprite' (must be one of: {list(SPRITE_CATALOG.keys())}) and "
                        "'ai_notes' (a 1-sentence description of their breed/look)."
                    ),
                },
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{b64_img}"},
                },
            ]
        )
        res = vision_llm.invoke([msg]).content
        clean_json = res.strip().removeprefix("```json").removesuffix("```").strip()
        parsed = json.loads(clean_json)
        sprite = parsed.get("sprite", "orange")
        if sprite not in SPRITE_CATALOG:
            sprite = "orange"
        profile["sprite"] = sprite
        profile["ai_notes"] = parsed.get("ai_notes", "A very good kitty.")
    except MissingApiKeyError:
        profile["sprite"] = "orange"
        profile["ai_notes"] = "No API key; defaulted to orange tabby."
    except Exception as exc:
        profile["sprite"] = "orange"
        profile["ai_notes"] = f"Fallback sprite selected ({exc})"

    return profile
