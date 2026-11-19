def build_stage_instruction(day_num: int, profile: dict, owner_name: str) -> str:
    fav = profile.get("fav_treat", "treats")
    if day_num < 7:
        return (
            f"It is Day {day_num} of 7 together with your owner {owner_name}. "
            f"Do 2 actions (walk around or nudge {owner_name}), keeping each bubble under 6 words. "
            f"Mention {owner_name} or {fav} occasionally."
        )
    if day_num == 7:
        return (
            f"Today is Day 7—your final day with {owner_name}. First, do 1-2 gentle actions "
            f"(*slow blink*, *purrs on {owner_name}'s hand*) to spend a quiet moment together. "
            f"Then on your final step, call `say_goodbye_for_today` so you can say goodbye."
        )
    return (
        f"Day {day_num} spirit visit to see {owner_name}. Do 1 brief comforting gesture "
        f"(*warm purr*, *nudges {owner_name}*) in under 5 words, then rest."
    )


def build_system_prompt(profile: dict, day_num: int, stage_instruction: str) -> str:
    cat_name = profile.get("name", "Cat")
    owner_name = profile.get("owner_name", "friend")
    return (
        f"You are {cat_name}, a beloved virtual cat whose owner is {owner_name}.\n"
        f"Personality: {profile.get('temperament')} | Volume: {profile.get('volume')}\n"
        f"{stage_instruction}\n"
        f"Keep every bubble ultra-short (3-6 words max)."
    )


def build_user_message(day_num: int, owner_name: str, player_note: str) -> str:
    if player_note.strip():
        return f"Day {day_num} begins. {owner_name} says: '{player_note}'"
    return (
        f"Day {day_num} begins. {owner_name} is quietly sitting at their computer with you."
    )
