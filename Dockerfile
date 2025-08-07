FROM python:3.11-slim-bookworm

WORKDIR /app

# Install uv
RUN apt-get update && apt-get install -y curl && \
    curl -Ls https://astral.sh/uv/install.sh | sh

# Add uv to PATH
ENV PATH="/root/.cargo/bin:${PATH}"

# Copy pyproject.toml and uv.lock to leverage Docker cache
COPY pyproject.toml uv.lock ./

# Install dependencies using uv
RUN uv sync

# Copy the rest of the application code
COPY . .

# Expose the port for FastAPI
EXPOSE 8000
