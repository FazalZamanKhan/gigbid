# syntax=docker/dockerfile:1.7
FROM node:20-alpine AS web
WORKDIR /web
COPY apps/web/package*.json ./
RUN npm ci --no-audit --no-fund
COPY apps/web ./
RUN npm run build

FROM python:3.12-slim
WORKDIR /app
ENV PYTHONUNBUFFERED=1 PYTHONPATH=/app
COPY pyproject.toml README.md ./
RUN --mount=type=cache,target=/root/.cache/pip \
    python -c "import subprocess,sys,tomllib; deps=tomllib.load(open('pyproject.toml','rb'))['project']['dependencies']; subprocess.check_call([sys.executable,'-m','pip','install','--timeout','180','--retries','10',*deps])"
COPY agent ./agent
COPY apps/api ./apps/api
COPY mcp_servers ./mcp_servers
COPY rag ./rag
COPY apps/__init__.py ./apps/__init__.py
COPY --from=web /web/dist /app/web_dist
ENV GIGBID_WEB_DIST=/app/web_dist
CMD ["sh", "-c", "uvicorn apps.api.public:app --host 0.0.0.0 --port ${PORT:-8000}"]
