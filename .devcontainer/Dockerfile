# Dev container for GapTrace
FROM mcr.microsoft.com/devcontainers/python:3.11-bullseye

# Install system dependencies for libclang and development
RUN apt-get update && apt-get install -y --no-install-recommends \
    llvm-11-dev \
    libclang-11-dev \
    build-essential \
    cmake \
    git \
    curl \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables for libclang
ENV LLVM_CONFIG_PATH=/usr/lib/llvm-11/bin/llvm-config
ENV LD_LIBRARY_PATH=/usr/lib/llvm-11/lib:$LD_LIBRARY_PATH

# Create workspace directory
WORKDIR /workspace

# Copy post-create script
COPY post-create.sh /tmp/post-create.sh
RUN chmod +x /tmp/post-create.sh

# Install Python packages (will be done by post-create script)
# This ensures they're installed in the venv created during container initialization
