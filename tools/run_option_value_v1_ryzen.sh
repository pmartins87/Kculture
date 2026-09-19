#!/usr/bin/env bash
set -euo pipefail

# Resumable Ryzen run for the first production option-value dataset.
# Safe to re-run: completed seeds are checkpointed as independent shards.

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

OUT="${OPTION_VALUE_OUT:-runs/option_value_v1_250}"
SEEDS="${OPTION_VALUE_SEEDS:-250}"
MASTER="${OPTION_VALUE_MASTER_SEED:-26091802}"

if [[ -n "${OPTION_VALUE_WORKERS:-}" ]]; then
  WORKERS="$OPTION_VALUE_WORKERS"
else
  CPU="$(python3 - <<'PY'
import os
print(os.cpu_count() or 8)
PY
)"
  if (( CPU > 4 )); then
    WORKERS=$((CPU-2))
  else
    WORKERS=$CPU
  fi
fi

echo "OPTION_VALUE_RYZEN_RUN root=$ROOT out=$OUT seeds=$SEEDS workers=$WORKERS"

python3 - <<'PY'
import importlib.metadata as m
v=m.version("kaggle-environments")
assert v=="1.32.7", f"kaggle-environments must be 1.32.7, got {v}"
print("runtime_ok kaggle-environments",v)
PY

python3 tools/option_value_dataset_ryzen_v1.py \
  --out "$OUT" \
  --seed-count "$SEEDS" \
  --master-seed "$MASTER" \
  --opponents v47_mirror,v48,tactical_memory \
  --seats 0,1 \
  --workers "$WORKERS"

echo
echo "DONE. Summary:"
cat "$OUT/SUMMARY.json"
