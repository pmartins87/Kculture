#!/usr/bin/env bash
set -euo pipefail

ROOT="${HOME}/Kculture"
OUT="${ROOT}/external/public_frontier_20260917"
WIN="/mnt/c/Users/Rz9/Downloads/kaggriculture_public_frontier_20260917.tar.gz"

cd "${ROOT}"
source .venv-ps2/bin/activate

rm -rf "${OUT}"
mkdir -p "${OUT}/index"

kaggle kernels list \
  --competition kaggriculture \
  --sort-by scoreDescending \
  --page-size 100 \
  -v > "${OUT}/index/kernels_score_desc.csv"

echo "status,spec,tag" > "${OUT}/index/pull_status.csv"

pull_one () {
  local spec="$1"
  local tag="$2"
  mkdir -p "${OUT}/${tag}"
  echo "PUBLIC_FRONTIER_PULL ${spec}"
  if kaggle kernels pull "${spec}" -m -p "${OUT}/${tag}"; then
    echo "OK,${spec},${tag}" >> "${OUT}/index/pull_status.csv"
    return 0
  fi
  echo "FAIL,${spec},${tag}" >> "${OUT}/index/pull_status.csv"
  echo "PUBLIC_FRONTIER_WARN failed=${spec}" >&2
  return 0
}

# First pull CURRENT versions without a /version suffix.  Kaggle's website currently
# exposes these notebooks publicly, but GetKernel has returned 403 for version-qualified
# specs on this account.  Current-source pulls tell us whether the restriction is only on
# historical versions or on the notebook source endpoint itself.
pull_one "lynnsakurai/farming-score-v4-a-better-shop" "farming_score_v4_current"
pull_one "lynnsakurai/farming-score-v3-replay-revised" "farming_score_v3_current"
pull_one "lynnsakurai/farming-score-a-mathematical-approach" "farming_math_current"
pull_one "indarkarhana/shape-the-shop-work-the-pasture-top-10" "shape_shop_top10_current"
pull_one "tetsutani/shape-the-shop-work-the-pasture-kaggriculture" "shape_shop_tetsu_current"
pull_one "reyhanksatria/adaptive-route-agent-v2" "adaptive_route_v2_current"
pull_one "flexonafft/kaggriculture-multi-route-farming-agent" "multiroute_current"
pull_one "vijaikm/kaggriculture-bc-policy-inference-starter" "bc_policy_starter_current"

# Historical high-water mark for Multi-Route.  This may remain forbidden by GetKernel;
# keep it as an explicit provenance attempt rather than silently substituting a version.
pull_one "flexonafft/kaggriculture-multi-route-farming-agent/59" "multiroute_best_v59"

(
  cd "${OUT}"
  find . -type f -print0 | sort -z | xargs -0 sha256sum > SHA256SUMS.txt
)

tar -czf "${WIN}" -C "${ROOT}/external" public_frontier_20260917

ok_count=$(awk -F, 'NR>1 && $1=="OK"{n++} END{print n+0}' "${OUT}/index/pull_status.csv")
fail_count=$(awk -F, 'NR>1 && $1=="FAIL"{n++} END{print n+0}' "${OUT}/index/pull_status.csv")

echo "PUBLIC_FRONTIER_RESULT ok=${ok_count} fail=${fail_count}"
echo "PUBLIC_FRONTIER_DONE ${WIN}"
ls -lh "${WIN}"
echo "PUBLIC_FRONTIER_INDEX=${OUT}/index/kernels_score_desc.csv"

# Exit non-zero only when literally no source notebook could be pulled.  The CSV/index
# and tarball are still preserved for diagnosis.
if [[ "${ok_count}" -eq 0 ]]; then
  exit 7
fi
