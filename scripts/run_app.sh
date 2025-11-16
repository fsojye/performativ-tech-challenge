#!/bin/bash
set -euo pipefail

APP_DIR="src"

SKIP_BUILD=${SKIP_BUILD:-false}

POSITIONS_FILE=${1:-}
TARGET_CURRENCY=${2:-USD}
START_DATE=${3:-2023-01-01}
END_DATE=${4:-2024-11-10}

if [ -z "$POSITIONS_FILE" ]; then
    echo "Error: missing POSITIONS_FILE" >&2
    exit 1
fi
# Create venv and build unless SKIP_BUILD is set
if [ "$SKIP_BUILD" != "true" ]; then
    uv venv --python python3.14
    ./scripts/build_app.sh
fi

args=()

[ -n "$POSITIONS_FILE" ] && args+=(--positions-file="$POSITIONS_FILE")
[ -n "$TARGET_CURRENCY" ] && args+=(--target-currency="$TARGET_CURRENCY")
[ -n "$START_DATE" ] && args+=(--start-date="$START_DATE")
[ -n "$END_DATE" ] && args+=(--end-date="$END_DATE")

echo "Calculating metrics..."
echo "Positions data source: $POSITIONS_FILE"
echo "Target currency: $TARGET_CURRENCY"
echo "Start date: $START_DATE"
echo "End date: $END_DATE"

PYTHONPATH=$APP_DIR .venv/bin/python -m src.main "${args[@]}"