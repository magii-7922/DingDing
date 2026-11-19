FROM python:3.12-slim

# Node is needed to build the Vite frontend
RUN apt-get update \
  && apt-get install -y --no-install-recommends curl ca-certificates \
  && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
  && apt-get install -y --no-install-recommends nodejs \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Python deps
COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

# Frontend deps + build
COPY frontend/package.json frontend/package-lock.json /app/frontend/
WORKDIR /app/frontend
RUN npm ci
COPY frontend/ /app/frontend/
RUN npm run build

# Backend source (and keep sprites available under public/)
COPY backend/ /app/backend/

WORKDIR /app/backend
ENV PYTHONUNBUFFERED=1

CMD uvicorn app:app --host 0.0.0.0 --port ${PORT:-8000}
