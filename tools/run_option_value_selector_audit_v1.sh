#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if [[ -x "$HOME/Kculture/.venv-ps2/bin/python" ]]; then
  PY="$HOME/Kculture/.venv-ps2/bin/python"
elif [[ -x "$ROOT/.venv-ps2/bin/python" ]]; then
  PY="$ROOT/.venv-ps2/bin/python"
else
  PY="${PYTHON:-python3}"
fi

INPUT="${OPTION_VALUE_INPUT:-runs/option_value_v1_250/TRAINING_ROWS.jsonl}"
OUT="${OPTION_VALUE_AUDIT_OUT:-runs/option_value_v1_250/SELECTOR_AUDIT_V1.json}"

"$PY" tools/option_value_selector_audit_v1.py   --input "$INPUT"   --out "$OUT"

echo
echo "Audit written to $OUT"
