#!/usr/bin/env bash
set -euo pipefail

ROOT="${HOME}/Kculture"
PY="${ROOT}/.venv-ps2/bin/python"
PACK_WIN="/mnt/c/Users/Rz9/Downloads/cr089-frozen-population-packages-v1.zip"
OUT_REL="runs/native_teacher_hybrid_v1/HYBRID_TEACHER.json"
OUT="${ROOT}/${OUT_REL}"

cd "${ROOT}"

if [[ ! -x "${PY}" ]]; then
  echo "HYBRID_TEACHER_FAIL missing_venv_python=${PY}" >&2
  exit 3
fi
if [[ ! -f external/kaggriculture-cppsim/sim/sim.hpp ]]; then
  echo "HYBRID_TEACHER_FAIL missing_kagsim_checkout" >&2
  exit 4
fi
if [[ ! -f "${PACK_WIN}" && ! -f "${ROOT}/cr089-frozen-population-packages-v1.zip" && ! -f "${ROOT}/artifacts/cr089-frozen-population-packages-v1.zip" ]]; then
  echo "HYBRID_TEACHER_FAIL missing_frozen_pack" >&2
  echo "Expected: ${PACK_WIN}" >&2
  exit 5
fi
if [[ ! -f runs/native_teacher_bootstrap_v0/TEACHER_BOOTSTRAP.json ]]; then
  echo "HYBRID_TEACHER_FAIL missing_bootstrap_result" >&2
  exit 6
fi

"${PY}" -m pip install -U setuptools wheel pybind11 numpy

(
  cd native/teacher
  rm -rf build kagteacher*.so
  "${PY}" setup.py build_ext --inplace
)

cd "${ROOT}"
set +e
"${PY}" tools/prize_solver_native_teacher_hybrid_cem_v1.py \
  --generations 8 \
  --population 256 \
  --train-seeds 8 \
  --holdout-seeds 32 \
  --threads 0 \
  --out "${OUT_REL}"
rc=$?
set -e

if [[ -f "${OUT}" && -d /mnt/c/Users/Rz9/Downloads ]]; then
  cp "${OUT}" /mnt/c/Users/Rz9/Downloads/HYBRID_TEACHER.json
fi
DATA="${ROOT}/runs/native_teacher_hybrid_v1/HYBRID_SEARCH_DATA.npz"
if [[ -f "${DATA}" && -d /mnt/c/Users/Rz9/Downloads ]]; then
  cp "${DATA}" /mnt/c/Users/Rz9/Downloads/HYBRID_SEARCH_DATA.npz
fi

echo "HYBRID_RC=${rc}"
echo "HYBRID_RESULT=${OUT}"
exit "${rc}"
