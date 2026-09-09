FROM python:3.14-slim

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN pip install uv && \
    uv sync --frozen --no-dev

COPY src ./src

ENV PORT=50051
ENV DATA_DIR=/data

EXPOSE 50051

VOLUME ["/data"]

CMD ["uv", "run", "kv-store"]