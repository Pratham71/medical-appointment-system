# syntax=docker/dockerfile:1
# ── Frontend — Next.js 14 / TypeScript ───────────────────────────────────────
# Build context: app/frontend/  (package.json lives here)

FROM node:20-alpine

WORKDIR /app

# ── Install dependencies ──────────────────────────────────────────────────────
# Copy manifests first for layer-cache efficiency.
# package-lock.json exists in the repo (setup.py uses `npm ci`), so we use ci.
COPY package*.json ./
RUN npm ci

# ── Copy source ───────────────────────────────────────────────────────────────
COPY . .

EXPOSE 3000

# README confirms the -H 0.0.0.0 flag is required to bind inside the container
CMD ["npm", "run", "dev", "--", "-H", "0.0.0.0"]
