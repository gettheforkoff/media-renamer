# Build stage
FROM python:3.13-slim AS builder

# Install system dependencies for building
RUN apt-get update && apt-get install -y \
    libmediainfo0v5 \
    libmediainfo-dev \
    curl \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

WORKDIR /build

# Copy project files
COPY pyproject.toml ./
COPY README.md ./
COPY build_binary.py ./
COPY media_renamer/ ./media_renamer/

# Install dependencies and PyInstaller using uv
RUN uv venv && \
    . .venv/bin/activate && \
    uv pip install -e . && \
    uv pip install pyinstaller

# Build the binary using our improved build script
RUN . .venv/bin/activate && \
    python build_binary.py

# Runtime stage
FROM debian:13-slim AS runtime

# Install only runtime dependencies
RUN apt-get update && apt-get install -y \
    libmediainfo0v5 \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create a non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Copy the binary from build stage
COPY --from=builder /build/dist/media-renamer /usr/local/bin/media-renamer

# Make sure the binary is executable
RUN chmod +x /usr/local/bin/media-renamer

# Create volume for media files
VOLUME ["/media"]

# Switch to non-root user
USER appuser

# Default command
CMD ["/usr/local/bin/media-renamer", "/media", "--dry-run", "--verbose"]