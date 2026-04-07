#!/bin/bash
set -e

echo "🔧 Setting up GapTrace development environment..."

# Install system dependencies for libclang
echo "📦 Installing system dependencies..."
# Fix apt cache permissions issues and GPG key issues
sudo rm -rf /var/lib/apt/lists/partial
sudo mkdir -p /var/lib/apt/lists/partial
sudo apt-get clean
# Skip GPG signature verification for problematic repos
sudo apt-get update --allow-insecure-repositories --allow-unauthenticated 2>&1 | grep -v "GPG\|WARNING" || true
sudo apt-get install -y \
    clang-11 \
    clang-tools-11 \
    llvm-11-dev \
    libclang-11-dev \
    build-essential \
    cmake \
    git

# Create and activate virtual environment
echo "🐍 Creating Python virtual environment..."
cd /workspaces/GapTrace
python3 -m venv .venv 2>&1

# Upgrade pip
echo "⬆️  Upgrading pip..."
.venv/bin/pip install --upgrade pip setuptools wheel

# Install project dependencies
echo "📚 Installing project dependencies..."
.venv/bin/pip install -e .

# Install development dependencies
echo "🛠️  Installing development tools..."
.venv/bin/pip install \
    pytest \
    pytest-cov \
    black \
    ruff \
    pylint \
    ipython

echo "✅ Development environment ready!"
echo ""
echo "📋 Quick start:"
echo "  • gaptrace parse --src <file.cpp>"
echo "  • gaptrace parse --src <file.cpp> --coverage <lcov.info>"
echo "  • gaptrace parse --src <file.cpp> --output results.json"
echo ""
echo "🧪 Run tests:"
echo "  • pytest"
echo ""
