const ZONE_ICONS = {
  taskbar: "📁",
  browser_window: "🌐",
  coffee_mug: "☕",
  trash_bin: "🗑️",
};

const CHONK_WIDTHS = {
  Slender: 50,
  Standard: 85,
  "Absolute Chonk": 150,
};

const DESKTOP_W = 640;
const DESKTOP_H = 365;

const els = {
  statusPill: document.getElementById("status-pill"),
  createPanel: document.getElementById("create-panel"),
  playPanel: document.getElementById("play-panel"),
  profileForm: document.getElementById("profile-form"),
  createMsg: document.getElementById("create-msg"),
  playMsg: document.getElementById("play-msg"),
  catTitle: document.getElementById("cat-title"),
  catNotes: document.getElementById("cat-notes"),
  desktop: document.getElementById("desktop"),
  dayBadge: document.getElementById("day-badge"),
  zoneIcons: document.getElementById("zone-icons"),
  catSprite: document.getElementById("cat-sprite"),
  speechBubble: document.getElementById("speech-bubble"),
  quietCard: document.getElementById("quiet-card"),
  taskbarLabel: document.getElementById("taskbar-label"),
  advanceForm: document.getElementById("advance-form"),
  playerNote: document.getElementById("player-note"),
  btnAdvance: document.getElementById("btn-advance"),
  btnReset: document.getElementById("btn-reset"),
  btnJump7: document.getElementById("btn-jump7"),
  stepLog: document.getElementById("step-log"),
};

let meta = { zones: {} };
let state = {
  current_day: 1,
  profile: null,
};

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function api(path, options = {}) {
  const res = await fetch(path, options);
  let data = null;
  try {
    data = await res.json();
  } catch {
    data = null;
  }
  if (!res.ok) {
    const detail = data?.detail || res.statusText || "Request failed";
    throw new Error(typeof detail === "string" ? detail : JSON.stringify(detail));
  }
  return data;
}

function showMsg(el, text, kind = "ok") {
  el.hidden = !text;
  el.textContent = text || "";
  el.classList.remove("ok", "error");
  if (text) el.classList.add(kind);
}

function scalePoint(x, y) {
  const rect = els.desktop.getBoundingClientRect();
  return {
    x: (x / DESKTOP_W) * rect.width,
    y: (y / DESKTOP_H) * rect.height,
  };
}

function renderZones() {
  els.zoneIcons.innerHTML = "";
  for (const [zone, [zx, zy]] of Object.entries(meta.zones || {})) {
    const { x, y } = scalePoint(zx, zy);
    const div = document.createElement("div");
    div.className = "zone-icon";
    div.style.left = `${x}px`;
    div.style.top = `${y}px`;
    div.innerHTML = `<div class="emoji">${ZONE_ICONS[zone] || "📄"}</div>${zone}`;
    els.zoneIcons.appendChild(div);
  }
}

function setDayBadge(day, { isSpirit = false, isPresent = true } = {}) {
  els.dayBadge.classList.remove("spirit", "quiet");
  if (day <= 7) {
    const left = 7 - day;
    els.dayBadge.textContent = `Day ${day} / 7 (${left} days left together)`;
  } else if (isPresent) {
    els.dayBadge.textContent = `Day ${day} · Unscheduled Spirit Visit`;
    els.dayBadge.classList.add("spirit");
  } else {
    els.dayBadge.textContent = `Day ${day} · Quiet Desktop`;
    els.dayBadge.classList.add("quiet");
  }
}

function placeCat(zone, profile, { spirit = false } = {}) {
  const coords = meta.zones?.[zone] || [320, 180];
  const { x, y } = scalePoint(coords[0], coords[1]);
  const width = CHONK_WIDTHS[profile?.chonk] || 85;
  const height = 85;

  els.catSprite.hidden = false;
  els.catSprite.src = `/sprites/${profile?.sprite || "orange"}.png`;
  els.catSprite.style.width = `${(width / DESKTOP_W) * 100}%`;
  els.catSprite.style.height = `${(height / DESKTOP_H) * 100}%`;
  els.catSprite.style.left = `${x}px`;
  els.catSprite.style.top = `${y}px`;
  els.catSprite.classList.toggle("spirit", spirit);

  return { x, y };
}

function placeBubble(zone, speech, { spirit = false } = {}) {
  const coords = meta.zones?.[zone] || [320, 180];
  const { x, y } = scalePoint(coords[0], coords[1]);
  const rect = els.desktop.getBoundingClientRect();
  const left = Math.max(12, Math.min(x - 80, rect.width - 180));
  const top = Math.max(42, y - 70);

  els.speechBubble.hidden = false;
  els.speechBubble.textContent = speech || "*purrs softly*";
  els.speechBubble.style.left = `${left}px`;
  els.speechBubble.style.top = `${top}px`;
  els.speechBubble.classList.toggle("spirit", spirit);
}

function showQuietDesktop(profile, day) {
  els.catSprite.hidden = true;
  els.speechBubble.hidden = true;
  els.quietCard.hidden = false;
  els.quietCard.innerHTML = `
    <div>🐾 <i>${profile?.name || "Cat"} didn't visit the desktop today.</i></div>
    <div style="margin-top:6px;font-size:11px;color:#cbd5e1;">
      A warm sunbeam rests on the screen.
    </div>
  `;
  setDayBadge(day, { isSpirit: true, isPresent: false });
}

function showPresentDesktop(profile, day, step, { spirit = false } = {}) {
  els.quietCard.hidden = true;
  setDayBadge(day, { isSpirit: spirit, isPresent: true });
  placeCat(step.zone, profile, { spirit });
  placeBubble(step.zone, step.speech, { spirit });
}

function enterPlayMode(profile, day) {
  state.profile = profile;
  state.current_day = day;
  els.createPanel.hidden = true;
  els.playPanel.hidden = false;
  els.desktop.classList.add("has-wallpaper");
  els.catTitle.textContent = `${profile.name} · with ${profile.owner_name}`;
  els.catNotes.textContent = profile.ai_notes || `${profile.temperament} · ${profile.volume} · ${profile.chonk}`;
  els.taskbarLabel.textContent = `Remembering ${profile.name} (${profile.sprite})`;
  renderZones();
  setDayBadge(day);
  placeCat("taskbar", profile);
  placeBubble("taskbar", "*soft purr*");
  els.quietCard.hidden = true;
  els.stepLog.innerHTML = "";
}

async function refreshState() {
  const data = await api("/api/state");
  state.current_day = data.current_day;
  state.profile = data.profile;
  if (data.profile) {
    enterPlayMode(data.profile, data.current_day);
  }
  return data;
}

async function boot() {
  try {
    const [health, metaData] = await Promise.all([
      api("/api/health"),
      api("/api/meta"),
    ]);
    meta = metaData;
    if (health.has_api_key) {
      els.statusPill.textContent = "API ready";
      els.statusPill.className = "status-pill ok";
    } else {
      els.statusPill.textContent = "Missing ZAI_API_KEY";
      els.statusPill.className = "status-pill warn";
    }
    await refreshState();
    renderZones();
  } catch (err) {
    els.statusPill.textContent = "API offline — start backend";
    els.statusPill.className = "status-pill warn";
    console.error(err);
  }
}

els.profileForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  showMsg(els.createMsg, "");
  const form = e.currentTarget;
  const fd = new FormData(form);
  const submitBtn = form.querySelector('button[type="submit"]');
  submitBtn.disabled = true;
  try {
    const data = await api("/api/profile", { method: "POST", body: fd });
    showMsg(els.createMsg, `Created ${data.profile.name}!`, "ok");
    enterPlayMode(data.profile, data.current_day);
  } catch (err) {
    showMsg(els.createMsg, err.message, "error");
  } finally {
    submitBtn.disabled = false;
  }
});

els.advanceForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  showMsg(els.playMsg, "");
  els.btnAdvance.disabled = true;
  els.stepLog.innerHTML = "";
  try {
    const result = await api("/api/day/advance", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ player_note: els.playerNote.value || "" }),
    });

    state.current_day = result.next_day;
    showMsg(els.playMsg, result.message, "ok");

    if (!result.is_present) {
      showQuietDesktop(state.profile, result.day);
      const li = document.createElement("li");
      li.textContent = "No visit today.";
      els.stepLog.appendChild(li);
    } else if (!result.steps?.length) {
      showPresentDesktop(
        state.profile,
        result.day,
        { zone: "taskbar", speech: "*sits quietly*" },
        { spirit: result.is_spirit_visit },
      );
    } else {
      for (const step of result.steps) {
        showPresentDesktop(state.profile, result.day, step, {
          spirit: result.is_spirit_visit,
        });
        const li = document.createElement("li");
        const bit = step.interaction ? ` · ${step.interaction}` : "";
        li.textContent = `[${step.tool}] ${step.zone}${bit}: ${step.speech}`;
        els.stepLog.appendChild(li);
        await sleep(900);
      }
    }

    setDayBadge(result.next_day);
    els.playerNote.value = "";
  } catch (err) {
    showMsg(els.playMsg, err.message, "error");
  } finally {
    els.btnAdvance.disabled = false;
  }
});

els.btnReset.addEventListener("click", async () => {
  try {
    const data = await api("/api/day/reset", { method: "POST" });
    state.current_day = data.current_day;
    setDayBadge(data.current_day);
    showMsg(els.playMsg, data.message, "ok");
    if (state.profile) {
      placeCat("taskbar", state.profile);
      placeBubble("taskbar", "*soft purr*");
      els.quietCard.hidden = true;
      els.catSprite.hidden = false;
      els.speechBubble.hidden = false;
    }
    els.stepLog.innerHTML = "";
  } catch (err) {
    showMsg(els.playMsg, err.message, "error");
  }
});

els.btnJump7.addEventListener("click", async () => {
  try {
    const data = await api("/api/day/jump", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ day: 7 }),
    });
    state.current_day = data.current_day;
    setDayBadge(data.current_day);
    showMsg(els.playMsg, `${data.message} Press Advance Day for the farewell.`, "ok");
  } catch (err) {
    showMsg(els.playMsg, err.message, "error");
  }
});

window.addEventListener("resize", () => {
  if (!state.profile) return;
  renderZones();
});

boot();
