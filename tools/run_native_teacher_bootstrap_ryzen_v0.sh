#!/usr/bin/env bash
set -euo pipefail

ROOT="${HOME}/Kculture"
PY="${ROOT}/.venv-ps2/bin/python"
OUT_REL="runs/native_teacher_bootstrap_v0/TEACHER_BOOTSTRAP.json"
OUT="${ROOT}/${OUT_REL}"

cd "${ROOT}"

if [[ ! -x "${PY}" ]]; then
  echo "TEACHER_BOOTSTRAP_FAIL missing_venv_python=${PY}" >&2
  exit 3
fi
if [[ ! -f external/kaggriculture-cppsim/sim/sim.hpp ]]; then
  echo "TEACHER_BOOTSTRAP_FAIL missing_kagsim_checkout" >&2
  exit 4
fi

"${PY}" -m pip install -U setuptools wheel pybind11 numpy

(
  cd native/teacher
  rm -rf build kagteacher*.so
  "${PY}" setup.py build_ext --inplace
)

cd "${ROOT}"
set +e
"${PY}" tools/prize_solver_native_teacher_cem_v0.py \
  --generations 4 \
  --population 96 \
  --train-seeds 4 \
  --holdout-seeds 12 \
  --threads 0 \
  --out "${OUT_REL}"
rc=$?
set -e

if [[ -f "${OUT}" && -d /mnt/c/Users/Rz9/Downloads ]]; then
  cp "${OUT}" /mnt/c/Users/Rz9/Downloads/TEACHER_BOOTSTRAP.json
fi
DATA="${ROOT}/runs/native_teacher_bootstrap_v0/TEACHER_SEARCH_DATA.npz"
if [[ -f "${DATA}" && -d /mnt/c/Users/Rz9/Downloads ]]; then
  cp "${DATA}" /mnt/c/Users/Rz9/Downloads/TEACHER_SEARCH_DATA.npz
fi

echo "TEACHER_RC=${rc}"
echo "TEACHER_RESULT=${OUT}"
exit "${rc}"
