# syntax=docker/dockerfile:1.7
FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml README.md ./
RUN --mount=type=cache,target=/root/.cache/pip \
    python -c "import subprocess, sys, tomllib; deps = tomllib.load(open('pyproject.toml', 'rb'))['project']['dependencies']; subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--timeout', '180', '--retries', '10', *deps])"
COPY agent ./agent
COPY apps ./apps
COPY rag ./rag
COPY mcp_servers ./mcp_servers
EXPOSE 8000
CMD ["python", "-m", "uvicorn", "apps.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
