#!/usr/bin/env bash
set -euo pipefail

ROOT="\${HOME}/Kculture"
BRANCH="research/prize-solver-v0"
PY="\${ROOT}/.venv-ps2/bin/python"
TOPDIR="\${ROOT}/external/public_topscore_20260917"
TOPWIN="/mnt/c/Users/Rz9/Downloads/kaggriculture_public_topscore_20260917.tar.gz"

cd "\${ROOT}"

if [[ ! -x "\${PY}" ]]; then
  echo "PROGRAMME_TEACHER_FAIL missing_venv_python=\${PY}" >&2
  exit 3
fi
if [[ ! -f external/kaggriculture-cppsim/sim/sim.hpp ]]; then
  echo "PROGRAMME_TEACHER_FAIL missing_kagsim_checkout" >&2
  exit 4
fi

if [[ ! -d "\${TOPDIR}" ]]; then
  if [[ ! -f "\${TOPWIN}" ]]; then
    echo "PROGRAMME_TEACHER_FAIL missing_public_topscore_corpus=\${TOPWIN}" >&2
    exit 5
  fi
  mkdir -p "\${ROOT}/external"
  tar -xzf "\${TOPWIN}" -C "\${ROOT}/external"
fi

git fetch origin "\${BRANCH}"

mkdir -p tools native/programme
for path in \
  tools/build_public_programme_corpus_v1.py \
  tools/programme_suffix_teacher_v0.py \
  native/programme/kagprog.cpp \
  native/programme/setup.py \
  native/programme/pyproject.toml
do
  git show "origin/\${BRANCH}:\${path}" > "\${path}"
done

source .venv-ps2/bin/activate

"\${PY}" - <<'PY'
import numpy, pybind11, setuptools
print("PROGRAMME_BUILD_DEPS", {
    "numpy": numpy.__version__,
    "pybind11": pybind11.__version__,
    "setuptools": setuptools.__version__,
})
PY

rm -rf runs/public_programme_corpus_v1 runs/programme_suffix_teacher_v0

"\${PY}" tools/build_public_programme_corpus_v1.py \
  --root external/public_topscore_20260917 \
  --out runs/public_programme_corpus_v1

(
  cd native/programme
  rm -rf build kagprog*.so
  "\${PY}" setup.py build_ext --inplace
)

set +e
"\${PY}" tools/programme_suffix_teacher_v0.py \
  --checkpoints 144,168,192,216,240 \
  --train-seeds 6 \
  --holdout-seeds 6 \
  --max-depth 4 \
  --threads 0 \
  --out runs/programme_suffix_teacher_v0/PROGRAMME_SUFFIX_TEACHER.json
rc=$?
set -e

if [[ -d /mnt/c/Users/Rz9/Downloads ]]; then
  for f in \
    runs/public_programme_corpus_v1/PROGRAMME_CORPUS.json \
    runs/programme_suffix_teacher_v0/PROGRAMME_SUFFIX_TEACHER.json \
    runs/programme_suffix_teacher_v0/PROGRAMME_TEACHER_DATA.npz
  do
    [[ -f "\${f}" ]] && cp "\${f}" /mnt/c/Users/Rz9/Downloads/
  done
fi

echo "PROGRAMME_TEACHER_RC=\${rc}"
echo "PROGRAMME_TEACHER_RESULT=\${ROOT}/runs/programme_suffix_teacher_v0/PROGRAMME_SUFFIX_TEACHER.json"
exit "\${rc}"
