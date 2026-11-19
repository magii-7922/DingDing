import random


def format_cat_speech(
    raw_text: str,
    volume: str,
    is_final_bye: bool = False,
    quiet_requested: bool = False,
) -> str:
    """Formats meows based on Loud/Quiet setting, unless the owner asked the cat to quiet down."""
    if is_final_bye:
        return "meow I need to go now bye."

    clean = raw_text.strip()

    if quiet_requested:
        return f"*quietly* meow... {clean.lower()}"

    if volume == "Loud":
        loud_meows = ["meowMeowMEOWMeow!", "MRROW! meow meow!", "MEOWmeowMEOW!"]
        if "meow" not in clean.lower():
            return f"{random.choice(loud_meows)} {clean}"
        return clean

    if "meow" not in clean.lower() and random.random() < 0.6:
        return f"meow. {clean}"
    return clean
