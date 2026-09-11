FROM python:3.14-slim

WORKDIR /app

COPY pyproject.toml uv.lock README.md ./
COPY src ./src

RUN pip install uv && \
    uv sync --frozen --no-dev

ENV PORT=50051
ENV DATA_DIR=/data
ENV PYTHONUNBUFFERED=1

EXPOSE 50051

VOLUME ["/data"]

CMD ["uv", "run", "kv-store"]