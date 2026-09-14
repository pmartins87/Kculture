#!/usr/bin/env python3
"""FP001 E2D — rerun frozen E2B matrix with stochastic town shops disabled."""
from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE_TEST = ROOT / "tools" / "fp001_e2b_no_weed_causal_test.py"

spec = importlib.util.spec_from_file_location("e2b_base", BASE_TEST)
if spec is None or spec.loader is None:
    raise RuntimeError(BASE_TEST)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

# Preserve all E2B instrumentation/architectures. Only alter the evaluation
# environment and use fresh nominal seeds.
_original_make = mod.make


def deterministic_make(name, configuration=None, debug=False, **kwargs):
    cfg = dict(configuration or {})
    cfg["weedSpawnChance"] = 0
    cfg["townShopUnlockInterval"] = 999
    return _original_make(name, configuration=cfg, debug=debug, **kwargs)


mod.make = deterministic_make
mod.SEEDS = list(range(69401, 69405))

if __name__ == "__main__":
    print("E2D_DETERMINISTIC_TOWN_BEGIN")
    mod.main()
    print("E2D_DETERMINISTIC_TOWN_PASS")
