#!/bin/bash
set -euo pipefail

ACTION=${1:-}

if [ -z "$ACTION" ] || [[ ! "$ACTION" =~ ^(unit_test|integration_test)$ ]]; then
  echo "Usage: $0 <unit_test|integration_test>"
  exit 1
fi

if [[ "$ACTION" == "unit_test" ]]; then
  echo "Running unit tests"
  .venv/bin/pytest
fi

if [[ "$ACTION" == "integration_test" ]]; then
  echo "Running integration tests"
fi