# syntax=docker/dockerfile:1
# Produção Railway: build Vue + Flask servindo API + SPA na porta $PORT

FROM python:3.11-slim

RUN apt-get update \
  && apt-get install -y --no-install-recommends curl ca-certificates \
  && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
  && apt-get install -y --no-install-recommends nodejs \
  && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:0.9.26 /uv /uvx /bin/

WORKDIR /app

COPY package.json package-lock.json ./
COPY frontend/package.json frontend/package-lock.json ./frontend/
COPY backend/pyproject.toml backend/uv.lock ./backend/

RUN npm ci \
  && npm ci --prefix frontend \
  && cd backend && uv sync --frozen

COPY . .

ENV VITE_API_BASE_URL=
# Invalida cache do frontend quando a integração Copa Bets muda
RUN echo "frontend-build-vip-session-fix-v1" && npm run build

ENV NODE_ENV=production
ENV FLASK_DEBUG=False
ENV PYTHONUNBUFFERED=1

EXPOSE 5001

CMD ["npm", "run", "start"]
