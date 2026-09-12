"""Build CR081 v3: faithful runtime-aligned UMG market overlay.

This is a mechanical fidelity correction to the already-frozen CR081 hypothesis.
No H2H result from v1/v2 is used. v3 keeps all frozen strategic choices:
- same-step CR071M physical/runtime backbone;
- runtime steps 0..287 use the development-only UMG modal market learned from
  replay action indices 1..288;
- legal/capacity protections (room_guard and clamp_sells) remain;
- inherited strategic market transforms (CR053 counterplay and dead_stock) are
  disabled only inside the frozen CR081 prefix and resume after step 287.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import cr081_build_current3056_bridge as v2

PREFIX = v2.PREFIX


def patch_source_v3(source: str, policy: list[list]) -> str:
    source = v2.patch_source(source, policy)

    counter_old = "        market = self._cr053_counter_market(step, market, proj)\n"
    counter_new = (
        "        # CR081 v3 fidelity: inside the frozen UMG prefix, do not apply the\n"
        "        # inherited CR053 strategic market transform. It is not a safety repair.\n"
        "        if step >= CR081_PREFIX:\n"
        "            market = self._cr053_counter_market(step, market, proj)\n"
    )
    if source.count(counter_old) != 1:
        raise RuntimeError("CR053 counter anchor mismatch")
    source = source.replace(counter_old, counter_new, 1)

    dead_cond_old = "            if surplus > 0 and prices.get(it, 0) > 1:\n"
    dead_cond_new = (
        "            # CR081 v3 fidelity: dead_stock is inherited economic strategy,\n"
        "            # not a legality/capacity repair, so it is disabled in the prefix.\n"
        "            if step >= CR081_PREFIX and surplus > 0 and prices.get(it, 0) > 1:\n"
    )
    if source.count(dead_cond_old) != 1:
        raise RuntimeError("dead_stock condition anchor mismatch")
    source = source.replace(dead_cond_old, dead_cond_new, 1)

    header_old = "Single frozen candidate: unchanged same-step CR071M physical backbone plus\n"
    header_new = "Single frozen candidate: unchanged same-step CR071M physical backbone plus\n"
    if header_old not in source:
        raise RuntimeError("CR081 provenance header missing")

    return source


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--umg-root", type=Path, required=True)
    ap.add_argument("--cr071m", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--manifest", type=Path, required=True)
    a = ap.parse_args()

    rows, dev, hold, policy, support, blocks = v2.modal_market(a.umg_root)
    source = v2.extract_main(a.cr071m)
    base_hash = v2.sha256_bytes(a.cr071m.read_bytes())
    patched = patch_source_v3(source, policy)
    compile(patched, "main.py", "exec")
    v2.write_tar(a.output, patched)
    out_hash = v2.sha256_bytes(a.output.read_bytes())

    manifest = {
        "schema_version": "cr081-current3056-bridge-v3-fidelity",
        "candidate": "CR081",
        "architecture": "same-step CR071M physical backbone + runtime-aligned UMG dev-only market prefix",
        "prefix_steps": PREFIX,
        "replay_action_index_offset": v2.REPLAY_ACTION_OFFSET,
        "runtime_market_window": [0, PREFIX - 1],
        "physical_backbone_delayed": False,
        "development_episodes": len(dev),
        "sealed_holdout_episodes_not_used_in_build": len(hold),
        "development_market_support_blocks": blocks,
        "base_cr071m_sha256": base_hash,
        "candidate_sha256": out_hash,
        "same_turn_buy_product_funds_later_sell_in_prefix": True,
        "room_guard_retained_in_prefix": True,
        "clamp_sells_retained_in_prefix": True,
        "cr053_counter_disabled_in_prefix": True,
        "dead_stock_disabled_in_prefix": True,
        "inherited_strategic_market_transforms_resume_after_prefix": True,
        "replay_stitching": False,
        "identity_features": False,
        "holdout_used_for_policy_construction": False,
        "v1_run_invalid": 34671122716,
        "v2_run_invalid": 34671446692,
        "invalidity_reason_v2": "post-overlay inherited strategic market transforms were still active inside prefix; discovered before reading scores",
    }
    a.manifest.parent.mkdir(parents=True, exist_ok=True)
    a.manifest.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
