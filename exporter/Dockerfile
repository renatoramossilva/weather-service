FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

# Install Git (required for git+ dependencies)
RUN apt-get update && apt-get install -y git && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy project to workdir
COPY . ./

# Install project dependencies
RUN uv sync --locked

EXPOSE 8082

CMD ["uv", "run", "uvicorn", "exporter.metrics_exporter:app_metrics", "--host", "0.0.0.0", "--port", "8082"]
