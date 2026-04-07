#!/bin/bash
set -e

echo "🔧 Setting up GapTrace development environment..."

# Install system dependencies for libclang
echo "📦 Installing system dependencies..."
apt-get update
apt-get install -y \
    llvm-11-dev \
    libclang-11-dev \
    build-essential \
    cmake \
    git

# Create and activate virtual environment
echo "🐍 Creating Python virtual environment..."
python3 -m venv /workspace/venv
source /workspace/venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip setuptools wheel

# Install project dependencies
echo "📚 Installing project dependencies..."
cd /workspace/GapTrace
pip install -e .

# Install development dependencies
echo "🛠️  Installing development tools..."
pip install \
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
