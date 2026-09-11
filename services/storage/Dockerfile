FROM python:3.14-slim

WORKDIR /app

COPY . .

RUN pip install uv && \
    uv sync --frozen --package kv-store-storage --no-dev

ENV PORT=50051
ENV DATA_DIR=/data
ENV PYTHONUNBUFFERED=1

EXPOSE 50051

VOLUME ["/data"]

CMD ["uv", "run", "--package", "kv-store-storage", "storage-node"]