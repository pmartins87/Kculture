#!/usr/bin/env bash
set -euo pipefail

ROOT="${HOME}/Kculture"
SRC_INDEX="${ROOT}/external/public_frontier_20260917/index/kernels_score_desc.csv"
OUT="${ROOT}/external/public_topscore_20260917"
WIN="/mnt/c/Users/Rz9/Downloads/kaggriculture_public_topscore_20260917.tar.gz"
N="${TOP_N:-30}"

cd "${ROOT}"
source .venv-ps2/bin/activate

if [[ ! -f "${SRC_INDEX}" ]]; then
  echo "PUBLIC_TOP_FAIL missing_index=${SRC_INDEX}" >&2
  exit 3
fi

rm -rf "${OUT}"
mkdir -p "${OUT}/index"
cp "${SRC_INDEX}" "${OUT}/index/kernels_score_desc.csv"
echo "rank,status,ref,tag" > "${OUT}/index/pull_status.csv"

rank=0
tail -n +2 "${SRC_INDEX}" | head -n "${N}" | cut -d, -f1 | while IFS= read -r ref; do
  [[ -z "${ref}" ]] && continue
  rank=$((rank+1))
  tag=$(printf "%02d_%s" "${rank}" "${ref}" | tr '/ ' '__' | tr -cd '[:alnum:]_.-')
  mkdir -p "${OUT}/${tag}"
  echo "PUBLIC_TOP_PULL rank=${rank} ref=${ref}"
  if kaggle kernels pull "${ref}" -m -p "${OUT}/${tag}"; then
    echo "${rank},OK,${ref},${tag}" >> "${OUT}/index/pull_status.csv"
  else
    echo "${rank},FAIL,${ref},${tag}" >> "${OUT}/index/pull_status.csv"
    echo "PUBLIC_TOP_WARN rank=${rank} ref=${ref}" >&2
  fi
done

(
  cd "${OUT}"
  find . -type f -print0 | sort -z | xargs -0 sha256sum > SHA256SUMS.txt
)

tar -czf "${WIN}" -C "${ROOT}/external" public_topscore_20260917

ok_count=$(awk -F, 'NR>1 && $2=="OK"{n++} END{print n+0}' "${OUT}/index/pull_status.csv")
fail_count=$(awk -F, 'NR>1 && $2=="FAIL"{n++} END{print n+0}' "${OUT}/index/pull_status.csv")

if [[ -d /mnt/c/Users/Rz9/Downloads ]]; then
  cp "${OUT}/index/pull_status.csv" /mnt/c/Users/Rz9/Downloads/PUBLIC_TOP_PULL_STATUS.csv
fi

echo "PUBLIC_TOP_RESULT requested=${N} ok=${ok_count} fail=${fail_count}"
echo "PUBLIC_TOP_DONE ${WIN}"
ls -lh "${WIN}"

if [[ "${ok_count}" -eq 0 ]]; then
  exit 7
fi
