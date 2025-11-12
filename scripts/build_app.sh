#!/bin/bash
set -euo pipefail

ACTION=${1:-}

./scripts/build_dependencies.sh install

./scripts/format_code.sh check

./scripts/test_app.sh unit_test

./scripts/test_app.sh integration_test