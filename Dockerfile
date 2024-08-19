
FROM python:3.12-slim-bookworm

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

ENV APP_PORT=${APP_PORT:-9898}

WORKDIR /app

COPY . .

RUN pip install uv --root-user-action=ignore && \
    uv pip install --system --no-cache-dir . && \
    playwright install chromium --with-deps

CMD ["/bin/sh", "-c", "fastapi run --port ${APP_PORT} src/attctrl/main.py"]
