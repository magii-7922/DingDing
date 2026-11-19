# DingDing AI

Web prototype of a 7-day “desktop companion” cat — ported from the GroupHomework Jupyter notebook.

The cat lives on a **simulated desktop** in the browser (form 1). Core game/LLM logic lives in `backend/cat_core/` so a later real desktop overlay (form 3) can reuse it.

## Features

- Create a companion (name, personality, volume, chonk, fav treat, optional photo → sprite)
- Advance days with an optional note to your cat
- Day 1–6 visits, Day 7 farewell, Day 8+ random spirit visits (~40%)
- Quiet keywords in your note (`quiet`, `shh`, `noisy`, …) soften loud meows
- Debug: **Reset** / **Jump Day 7**

## Setup

### 1. API key

```bash
cd backend
copy .env.example .env
```

Edit `backend/.env` and set `ZAI_API_KEY` (Z.ai / GLM).

### 2. Backend

```bash
cd backend
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app:app --reload --port 8000
```

API docs: http://127.0.0.1:8000/docs

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://127.0.0.1:5173 — Vite proxies `/api` and `/sprites` to the backend.

## Demo flow

1. Create a companion (upload a cat photo optional).
2. Click **Advance Day** a few times (optional notes).
3. Click **Jump Day 7**, then **Advance Day** for the farewell.
4. Advance again for post–Day-7 spirit / quiet days.
5. **Reset** to restart from Day 1.

## Project layout

```
remembrance-cat/
  backend/
    app.py              # FastAPI routes
    cat_core/           # UI-agnostic logic (ready for a future desktop shell)
    data/               # save_state.json + profile.json (local)
    .env.example
  frontend/
    public/sprites/     # cat PNGs + wallpaper
    src/                # desktop UI + step animation
```

## Deploy on Render (public website)

GitHub Pages cannot run the Python backend. Use **Render** connected to this GitHub repo:

1. Open [https://dashboard.render.com](https://dashboard.render.com) and sign in with GitHub.
2. **New → Blueprint** → select `magii-7922/DingDing` (uses `render.yaml`).
3. Set the secret env var **`ZAI_API_KEY`** when prompted.
4. Deploy. When it finishes, open the `*.onrender.com` URL — that is the live site.

Notes:
- Free tier may sleep after idle; the first request can take ~30–60s to wake.
- Never commit `.env` or real API keys.
- Without `ZAI_API_KEY`, profile creation still works (vision falls back to orange); **Advance Day** returns `503` until a key is set.
