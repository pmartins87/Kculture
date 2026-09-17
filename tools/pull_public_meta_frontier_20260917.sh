#!/usr/bin/env bash
set -euo pipefail

ROOT="${HOME}/Kculture"
OUT="${ROOT}/external/public_frontier_20260917"
WIN="/mnt/c/Users/Rz9/Downloads/kaggriculture_public_frontier_20260917.tar.gz"

cd "${ROOT}"
source .venv-ps2/bin/activate

rm -rf "${OUT}"
mkdir -p "${OUT}/index"

# Snapshot the live public notebook frontier so we do not depend on stale web indexing.
kaggle kernels list \
  --competition kaggriculture \
  --sort-by scoreDescending \
  --page-size 100 \
  -v > "${OUT}/index/kernels_score_desc.csv"

pull_one () {
  local spec="$1"
  local tag="$2"
  mkdir -p "${OUT}/${tag}"
  echo "PUBLIC_FRONTIER_PULL ${spec}"
  kaggle kernels pull "${spec}" -m -p "${OUT}/${tag}"
}

# Current/high-scoring public families and historically best versions.
pull_one "lynnsakurai/farming-score-v4-a-better-shop/7" "farming_score_v4_v7"
pull_one "indarkarhana/shape-the-shop-work-the-pasture-top-10/1" "shape_shop_top10_v1"
pull_one "reyhanksatria/adaptive-route-agent-v2/2" "adaptive_route_v2"
pull_one "flexonafft/kaggriculture-multi-route-farming-agent/59" "multiroute_best_v59"
pull_one "flexonafft/kaggriculture-multi-route-farming-agent/84" "multiroute_latest_v84"
pull_one "andrewsokolovsky/kaggriculture/10" "sokolovsky_best_v10"
pull_one "andrewsokolovsky/kaggriculture/11" "sokolovsky_latest_v11"

# Manifest for provenance/audit.
(
  cd "${OUT}"
  find . -type f -print0 | sort -z | xargs -0 sha256sum > SHA256SUMS.txt
)

tar -czf "${WIN}" -C "${ROOT}/external" public_frontier_20260917

echo "PUBLIC_FRONTIER_DONE ${WIN}"
ls -lh "${WIN}"
echo "PUBLIC_FRONTIER_INDEX=${OUT}/index/kernels_score_desc.csv"
