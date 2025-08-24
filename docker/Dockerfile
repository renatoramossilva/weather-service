# Docker image with uv pre-installed
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

# Install Git (required for git+ dependencies)
RUN apt-get update && apt-get install -y git && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Set workdir
WORKDIR /app

# Copy project to workdir
COPY . ./

# Install project dependencies
RUN uv sync --locked

# Expose port 8000
# This config should matches with the ports config on
# docker compose file
EXPOSE 8000

# Run app
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

