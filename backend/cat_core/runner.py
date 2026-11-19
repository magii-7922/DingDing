import json
import random

from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage

from .constants import QUIET_WORDS
from .env import RemembranceCatEnv
from .llm import get_chat_llm
from .progress import load_day_progress, save_day_progress
from .prompts import build_stage_instruction, build_system_prompt, build_user_message


def advance_day(profile: dict, player_note: str = "") -> dict:
    """Advance one day. Returns a structured result for the web UI."""
    progress = load_day_progress()
    day_num = progress["current_day"]
    cat_name = profile.get("name", "Cat")
    owner_name = profile.get("owner_name", "friend")

    if day_num > 7:
        is_spirit_visit = True
        if random.random() > 0.40:
            progress["current_day"] = day_num + 1
            save_day_progress(progress)
            return {
                "day": day_num,
                "next_day": day_num + 1,
                "is_spirit_visit": True,
                "is_present": False,
                "quiet_requested": False,
                "message": f"{cat_name} did not visit today. Check back another day.",
                "steps": [],
                "final_state": {},
            }
    else:
        is_spirit_visit = False

    quiet_requested = any(word in player_note.lower() for word in QUIET_WORDS)

    env = RemembranceCatEnv(
        profile,
        day_num,
        is_spirit_visit,
        quiet_requested=quiet_requested,
    )
    wrapped_tools = env.tools()
    tool_map = {t.name: t for t in wrapped_tools}
    model = get_chat_llm().bind_tools(wrapped_tools)

    stage_instruction = build_stage_instruction(day_num, profile, owner_name)
    system_prompt = build_system_prompt(profile, day_num, stage_instruction)
    user_msg = build_user_message(day_num, owner_name, player_note)

    history = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_msg),
    ]

    for _ in range(4):
        response = model.invoke(history)
        history.append(response)
        if not response.tool_calls:
            break
        for req in response.tool_calls:
            tool_name = req["name"]
            if tool_name not in tool_map:
                error_msg = (
                    f"Tool '{tool_name}' does not exist. "
                    f"Choose ONLY from: {list(tool_map.keys())}"
                )
                history.append(ToolMessage(content=error_msg, tool_call_id=req["id"]))
                continue

            res = tool_map[tool_name].invoke(req["args"])
            history.append(ToolMessage(content=json.dumps(res), tool_call_id=req["id"]))
            if env.ended:
                break
        if env.ended:
            break

    progress["current_day"] = day_num + 1
    save_day_progress(progress)

    stage_label = ""
    if day_num == 7:
        stage_label = "Final Day Together"
    elif is_spirit_visit:
        stage_label = "Spirit Visit"

    return {
        "day": day_num,
        "next_day": day_num + 1,
        "is_spirit_visit": is_spirit_visit,
        "is_present": True,
        "quiet_requested": quiet_requested,
        "message": f"Day {day_num}" + (f" ({stage_label})" if stage_label else ""),
        "steps": env.steps,
        "final_state": dict(env.state),
    }
