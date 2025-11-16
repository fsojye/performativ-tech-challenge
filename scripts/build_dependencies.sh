#!/bin/bash
set -euo pipefail

ACTION=${1:-}

if [ -z "$ACTION" ] || [[ ! "$ACTION" =~ ^(update|install)$ ]]; then
  echo "Usage: $0 <update|install>"
  exit 1
fi

APP_DIR="src"

if [ ! -d ".venv" ]; then
  echo "Virtual environment not found. Creating one with 'uv venv'..."
  uv venv
fi

if [[ "$ACTION" == "update" ]]; then
  echo "Updating application dependencies"
  uv pip compile $APP_DIR/requirements.in -o $APP_DIR/requirements.txt \
    --generate-hashes \
    --no-cache-dir \
    --no-header \
    --no-emit-index-url \
    --emit-build-options \
    --strip-extras
fi

if [[ "$ACTION" == "install" ]]; then
  echo "Installing application dependencies"
  uv pip install -r $APP_DIR/requirements.txt \
    --require-hashes
fi
