FROM python:3.14-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1

COPY . .

RUN pip install uv && \
    uv sync --frozen --package kv-store-proxy --no-dev

CMD ["uv", "run", "--package", "kv-store-proxy", "proxy-node"]
