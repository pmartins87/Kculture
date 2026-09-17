#!/usr/bin/env bash
set -euo pipefail

ROOT="${HOME}/Kculture"
PY="${ROOT}/.venv-ps2/bin/python"
OUT_REL="runs/l2_vec_gate_v0/L2_VEC_GATE.json"
OUT="${ROOT}/${OUT_REL}"

cd "${ROOT}"

if [[ ! -x "${PY}" ]]; then
  echo "L2_BOOTSTRAP_FAIL missing_venv_python=${PY}" >&2
  exit 3
fi

if [[ ! -f external/kaggriculture-cppsim/sim/sim.hpp ]]; then
  echo "L2_BOOTSTRAP_FAIL missing_kagsim_checkout=external/kaggriculture-cppsim" >&2
  exit 4
fi

"${PY}" -m pip install -U setuptools wheel pybind11

(
  cd native/l2
  "${PY}" setup.py build_ext --inplace
)

cd "${ROOT}"
set +e
"${PY}" tools/prize_solver_l2_vec_gate.py \
  --batches 256,1024,4096 \
  --steps 720 \
  --threads 0 \
  --out "${OUT_REL}"
rc=$?
set -e

if [[ -f "${OUT}" && -d /mnt/c/Users/Rz9/Downloads ]]; then
  cp "${OUT}" /mnt/c/Users/Rz9/Downloads/L2_VEC_GATE.json
fi

echo "L2_RC=${rc}"
echo "L2_RESULT=${OUT}"
exit "${rc}"
