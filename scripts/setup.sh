#!/usr/bin/env bash

# Set-up the development environment

# Stop on errors
set -e

cd "$(dirname "$0")/.."

env_name=${1:-".venv"}

if [ -d "$env_name" ]; then
  echo "Virtual environment '$env_name' already exists."
else
  echo "Creating Virtual environment..."
  ${PYTHON:-python} -m venv "$env_name"
fi
echo "Activating virtual environment..."
source "$env_name"/bin/activate

echo "Installing development dependencies..."

pip install --upgrade pip
pip install --upgrade uv
uv pip install -e "."
uv pip install -e ".[test]"
pre-commit install
