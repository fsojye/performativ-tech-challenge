#!/bin/bash
set -euo pipefail

ACTION=${1:-}

if [ -z "$ACTION" ] || [[ ! "$ACTION" =~ ^(check|fix)$ ]]; then
  echo "Usage: $0 <check|fix>"
  exit 1
fi

APP_DIR="src"

echo "Type checking python code"
.venv/bin/mypy $APP_DIR

if [[ "$ACTION" == "check" ]]; then
  echo "Format checking python code"
  .venv/bin/ruff check $APP_DIR
fi

if [[ "$ACTION" == "fix" ]]; then
  echo "Formatting python code"
  .venv/bin/ruff format $APP_DIR
  .venv/bin/ruff check $APP_DIR --fix
fi

if [[ $? -ne 0 ]]; then
  echo "Formatting issues found"
  exit $?
fi