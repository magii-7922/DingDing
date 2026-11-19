import random

from langchain_core.tools import tool

from .constants import DESKTOP_ZONES
from .speech import format_cat_speech


class RemembranceCatEnv:
    def __init__(
        self,
        profile: dict,
        day_num: int,
        is_spirit_visit: bool = False,
        quiet_requested: bool = False,
    ):
        self.profile = profile
        self.day_num = day_num
        self.is_spirit_visit = is_spirit_visit
        self.quiet_requested = quiet_requested
        self.state = {
            "zone": random.choice(list(DESKTOP_ZONES.keys())),
            "speech": "*soft purr*",
            "actions_taken": 0,
            "interaction": None,
        }
        self.ended = False
        self.steps: list[dict] = []

    def _record_step(self, tool_name: str) -> dict:
        step = {
            "tool": tool_name,
            "zone": self.state["zone"],
            "speech": self.state["speech"],
            "interaction": self.state.get("interaction"),
            "actions_taken": self.state["actions_taken"],
        }
        self.steps.append(step)
        return step

    def tools(self):
        env = self
        vol = env.profile.get("volume", "Quiet")
        shh = env.quiet_requested

        @tool
        def walk_to_spot(zone: str, thought: str) -> dict:
            """Walk to a desktop icon (taskbar, browser_window, coffee_mug, trash_bin) with a short cat thought."""
            if zone not in DESKTOP_ZONES:
                zone = random.choice(list(DESKTOP_ZONES.keys()))
            env.state["zone"] = zone
            env.state["speech"] = format_cat_speech(thought, vol, quiet_requested=shh)
            env.state["interaction"] = None
            env.state["actions_taken"] += 1
            env._record_step("walk_to_spot")
            return dict(env.state)

        @tool
        def interact_with_owner(action_type: str, message: str) -> dict:
            """Do a Desktop Goose prank (steal_cursor, nudge_mug) OR affectionate gesture (headbutt_hand, slow_blink) with a short message."""
            env.state["speech"] = format_cat_speech(message, vol, quiet_requested=shh)
            env.state["interaction"] = action_type
            env.state["actions_taken"] += 1
            if env.state["actions_taken"] >= 3:
                env.ended = True
            env._record_step("interact_with_owner")
            return {**env.state, "interaction": action_type}

        @tool
        def say_goodbye_for_today(farewell_message: str) -> dict:
            """End today's visit (on Day 7, this triggers the final goodbye)."""
            is_day_7 = env.day_num == 7
            env.state["speech"] = format_cat_speech(
                farewell_message,
                vol,
                is_final_bye=is_day_7,
                quiet_requested=shh,
            )
            env.state["interaction"] = "goodbye"
            env.ended = True
            env._record_step("say_goodbye_for_today")
            return dict(env.state)

        return [walk_to_spot, interact_with_owner, say_goodbye_for_today]
