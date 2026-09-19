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

OUT="${OPTION_VALUE_V2_OUT:-runs/option_value_v2_150}"
SEEDS="${OPTION_VALUE_V2_SEEDS:-150}"
MASTER="${OPTION_VALUE_V2_MASTER_SEED:-26091902}"
if [[ -n "${OPTION_VALUE_WORKERS:-}" ]]; then
  WORKERS="$OPTION_VALUE_WORKERS"
else
  CPU="$("$PY" - <<'PY'
import os
print(os.cpu_count() or 8)
PY
)"
  WORKERS=$(( CPU > 4 ? CPU-2 : CPU ))
fi

"$PY" - <<'PY'
import importlib.metadata as m
v=m.version("kaggle-environments")
assert v=="1.32.7", f"expected 1.32.7, got {v}"
print("runtime_ok kaggle-environments",v)
PY

echo "OPTION_VALUE_V2_RUN out=$OUT seeds=$SEEDS workers=$WORKERS"
"$PY" tools/option_value_dataset_ryzen_v2.py   --out "$OUT"   --seed-count "$SEEDS"   --master-seed "$MASTER"   --opponents v47_mirror,ready_stock,v48,router_2715,conditional_memory,tactical_memory,best_market   --seats 0,1   --workers "$WORKERS"

cat "$OUT/SUMMARY.json"
