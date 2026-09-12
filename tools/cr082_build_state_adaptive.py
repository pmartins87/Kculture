"""Build the single frozen CR082 state-adaptive Majkel market candidate.

The executable reproduces the strict-forward Gate-A policy exactly:
- exact CR071M physical/runtime backbone, same-step and unchanged;
- runtime market override only on steps 0..287;
- teacher = oldest 48 episodes of the original fixed 64-episode Majkel corpus;
- current-state features and replay alignment exactly match cr082_fresh_gate_a_v2.py;
- same-step z-score Euclidean 1-NN; p95 leave-one-out OOD threshold;
- OOD fallback = same-step teacher modal market queue;
- only room_guard / SELL clamping / same-turn BUY_PRODUCT->SELL accounting remain;
- inherited CR053 counter-market and dead_stock are disabled in the prefix.
"""
from __future__ import annotations

import argparse
import base64
import gzip
import hashlib
import io
import json
import tarfile
import zlib
from collections import Counter
from pathlib import Path

import numpy as np

TEAM = "Majkel1337"
PREFIX = 288
TEACHER_TOTAL = 64
TEACHER_DEV = 48
PRODUCTS = ["WHEAT","CARROT","MELON","STRAWBERRY","TOMATO","EGG","MILK","WOOL","FERTILIZER"]
SEEDS = ["WHEAT","CARROT","MELON","STRAWBERRY","TOMATO"]
ANIMALS = ["COW","SHEEP","GOOSE"]


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def action_key(a):
    return json.dumps(a, sort_keys=True, separators=(",", ":"))


def features(obs, seat):
    farm = obs["farms"][seat]
    priv = obs["private"]
    market = obs["market"]
    shed = priv.get("shed") or {}
    seeds = priv.get("seeds") or {}
    prices = market.get("prices") or {}
    inventory = market.get("inventory") or {}
    vals = [
        obs.get("day", 0), obs.get("hour", 0), farm.get("money", 0),
        len(farm.get("hands") or []), farm.get("hires_today", 0),
        len(farm.get("unlocked_quadrants") or []),
    ]
    vals += [shed.get(x, 0) for x in PRODUCTS + ANIMALS]
    vals += [seeds.get(x, 0) for x in SEEDS]
    vals += [prices.get(x, 0) for x in PRODUCTS]
    vals += [inventory.get(x, 0) for x in PRODUCTS]
    return np.asarray(vals, dtype=np.float64)


def load_rows(root: Path):
    rows = []
    for p in root.rglob("episode-*-replay.json"):
        d = json.loads(p.read_text(encoding="utf-8"))
        teams = list(d.get("info", {}).get("TeamNames") or [])
        seats = [i for i, t in enumerate(teams) if t == TEAM]
        if len(seats) != 1 or len(d.get("steps") or []) < PREFIX + 1:
            continue
        seat = seats[0]
        ep = int(d.get("info", {}).get("EpisodeId") or p.name.split("-")[1])
        samples = []
        for t in range(PREFIX):
            obs = d["steps"][t][seat]["observation"]
            action = d["steps"][t + 1][seat]["action"].get("market") or []
            samples.append((features(obs, seat), action))
        rows.append((ep, samples, p))
    rows.sort(key=lambda x: x[0])
    if len(rows) != TEACHER_TOTAL:
        raise RuntimeError(f"frozen original Majkel corpus must contain exactly 64 usable episodes, got {len(rows)}")
    return rows


def build_model(rows):
    dev = rows[:TEACHER_DEV]
    model = []
    fallback_steps = []
    for t in range(PREFIX):
        train = [r[1][t] for r in dev]
        X = np.stack([x for x, _ in train])
        mu = X.mean(axis=0)
        sd = X.std(axis=0)
        sd[sd < 1e-9] = 1.0
        Xz = (X - mu) / sd
        dtrain = ((Xz[:, None, :] - Xz[None, :, :]) ** 2).sum(axis=2)
        np.fill_diagonal(dtrain, np.inf)
        threshold = float(np.quantile(np.sqrt(dtrain.min(axis=1)), 0.95))
        modal = json.loads(Counter(action_key(a) for _, a in train).most_common(1)[0][0])
        model.append({
            "sd": sd.tolist(),
            "x": X.tolist(),
            "a": [a for _, a in train],
            "thr": threshold,
            "m": modal,
        })
        if threshold == 0.0:
            fallback_steps.append(t)
    return dev, model, fallback_steps


def extract_main(package: Path) -> str:
    with tarfile.open(package, "r:gz") as tf:
        f = tf.extractfile(tf.getmember("main.py"))
        if f is None:
            raise RuntimeError("CR071M package missing main.py")
        return f.read().decode("utf-8")


def write_tar(path: Path, main_text: str):
    data = main_text.encode("utf-8")
    info = tarfile.TarInfo("main.py")
    info.size = len(data)
    info.mtime = 0
    info.mode = 0o644
    raw = io.BytesIO()
    with tarfile.open(fileobj=raw, mode="w", format=tarfile.PAX_FORMAT) as tf:
        tf.addfile(info, io.BytesIO(data))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(gzip.compress(raw.getvalue(), compresslevel=9, mtime=0))


def runtime_block(model):
    raw = json.dumps(model, sort_keys=True, separators=(",", ":")).encode("utf-8")
    packed = zlib.compress(raw, 9)
    b85 = base64.b85encode(packed).decode("ascii")
    block = f'''# CR082 frozen strict-forward state-adaptive Majkel market policy.\nCR082_PREFIX = {PREFIX}\n_CR082_PRODUCTS = ("WHEAT", "CARROT", "MELON", "STRAWBERRY", "TOMATO", "EGG", "MILK", "WOOL", "FERTILIZER")\n_CR082_ANIMALS = ("COW", "SHEEP", "GOOSE")\n_CR082_SEEDS = ("WHEAT", "CARROT", "MELON", "STRAWBERRY", "TOMATO")\n_CR082_MODEL_B85 = {b85!r}\n_CR082_MODEL = None\n\ndef _cr082_features(obs, me):\n    farm = obs["farms"][me]\n    priv = obs["private"]\n    market = obs["market"]\n    shed = priv.get("shed") or {{}}\n    seeds = priv.get("seeds") or {{}}\n    prices = market.get("prices") or {{}}\n    inventory = market.get("inventory") or {{}}\n    vals = [obs.get("day", 0), obs.get("hour", 0), farm.get("money", 0),\n            len(farm.get("hands") or []), farm.get("hires_today", 0),\n            len(farm.get("unlocked_quadrants") or [])]\n    vals += [shed.get(x, 0) for x in _CR082_PRODUCTS + _CR082_ANIMALS]\n    vals += [seeds.get(x, 0) for x in _CR082_SEEDS]\n    vals += [prices.get(x, 0) for x in _CR082_PRODUCTS]\n    vals += [inventory.get(x, 0) for x in _CR082_PRODUCTS]\n    return [float(x) for x in vals]\n\ndef _cr082_model():\n    global _CR082_MODEL\n    if _CR082_MODEL is None:\n        _b64 = __import__("base64")\n        _zlib = __import__("zlib")\n        _json = __import__("json")\n        _CR082_MODEL = _json.loads(_zlib.decompress(_b64.b85decode(_CR082_MODEL_B85.encode("ascii"))).decode("utf-8"))\n    return _CR082_MODEL\n\ndef _cr082_policy_market(obs, me, step):\n    row = _cr082_model()[step]\n    q = _cr082_features(obs, me)\n    sd = row["sd"]\n    best_j = 0\n    best_d2 = None\n    for j, x in enumerate(row["x"]):\n        d2 = 0.0\n        for qi, xi, si in zip(q, x, sd):\n            z = (qi - xi) / si\n            d2 += z * z\n        if best_d2 is None or d2 < best_d2:\n            best_d2 = d2\n            best_j = j\n    chosen = row["a"][best_j] if best_d2 <= row["thr"] * row["thr"] else row["m"]\n    return [list(o) for o in chosen]\n\n'''
    return block, sha256_bytes(raw), sha256_bytes(packed), len(raw), len(packed)


def patch_source(source: str, model):
    block, raw_sha, packed_sha, raw_n, packed_n = runtime_block(model)
    const_anchor = "_CR053_COUNTER_LEAD = 1\n\n_BLOB = ("
    if source.count(const_anchor) != 1:
        raise RuntimeError("CR071M constant anchor mismatch")
    source = source.replace(const_anchor, "_CR053_COUNTER_LEAD = 1\n\n" + block + "_BLOB = (", 1)

    market_old = '        market = [list(o) for o in (base.get("market") or [])]\n'
    market_new = (
        '        market = [list(o) for o in (base.get("market") or [])]\n'
        '        # CR082: current-state 1-NN market policy only in the frozen prefix.\n'
        '        if 0 <= step < CR082_PREFIX:\n'
        '            market = _cr082_policy_market(obs, me, step)\n'
    )
    if source.count(market_old) != 1:
        raise RuntimeError("CR071M market anchor mismatch")
    source = source.replace(market_old, market_new, 1)

    counter_old = '        market = self._cr053_counter_market(step, market, proj)\n'
    counter_new = (
        '        # CR082 fidelity: CR053 counterplay is strategic, not a safety repair.\n'
        '        if step >= CR082_PREFIX:\n'
        '            market = self._cr053_counter_market(step, market, proj)\n'
    )
    if source.count(counter_old) != 1:
        raise RuntimeError("CR053 counter anchor mismatch")
    source = source.replace(counter_old, counter_new, 1)

    clamp_old = (
        '        for o in market:\n'
        '            if o and o[0] == "SELL":\n'
        '                have = avail.get(o[1], 0)\n'
        '                if have <= 0:\n'
        '                    continue\n'
        '                n = min(int(o[2]), have)\n'
        '                if n <= 0:\n'
        '                    continue\n'
        '                avail[o[1]] = have - n\n'
        '                kept.append(["SELL", o[1], n])\n'
        '            else:\n'
        '                kept.append(o)\n'
    )
    clamp_new = (
        '        for o in market:\n'
        '            # CR082 mechanical legality: an earlier same-turn BUY_PRODUCT can\n'
        '            # supply a later SELL in the same market queue.\n'
        '            if (step < CR082_PREFIX and o and len(o) >= 3\n'
        '                    and o[0] == "BUY_PRODUCT"):\n'
        '                avail[o[1]] = avail.get(o[1], 0) + max(0, int(o[2]))\n'
        '                kept.append(o)\n'
        '            elif o and o[0] == "SELL":\n'
        '                have = avail.get(o[1], 0)\n'
        '                if have <= 0:\n'
        '                    continue\n'
        '                n = min(int(o[2]), have)\n'
        '                if n <= 0:\n'
        '                    continue\n'
        '                avail[o[1]] = have - n\n'
        '                kept.append(["SELL", o[1], n])\n'
        '            else:\n'
        '                kept.append(o)\n'
    )
    if source.count(clamp_old) != 1:
        raise RuntimeError("CR071M clamp anchor mismatch")
    source = source.replace(clamp_old, clamp_new, 1)

    dead_old = '            if surplus > 0 and prices.get(it, 0) > 1:\n'
    dead_new = (
        '            # CR082 fidelity: dead_stock is inherited strategy and is disabled\n'
        '            # while the frozen state-adaptive market policy is active.\n'
        '            if step >= CR082_PREFIX and surplus > 0 and prices.get(it, 0) > 1:\n'
    )
    if source.count(dead_old) != 1:
        raise RuntimeError("dead_stock anchor mismatch")
    source = source.replace(dead_old, dead_new, 1)
    return source, (raw_sha, packed_sha, raw_n, packed_n)


def _reference_predict(model_row, q):
    X = np.asarray(model_row["x"], dtype=np.float64)
    sd = np.asarray(model_row["sd"], dtype=np.float64)
    d2 = (((X - q) / sd) ** 2).sum(axis=1)
    j = int(d2.argmin())
    return model_row["a"][j] if float(np.sqrt(d2[j])) <= float(model_row["thr"]) else model_row["m"]


def self_audit(source_base: str, source_patched: str, rows, model):
    assert source_patched.count("market = _cr082_policy_market(obs, me, step)") == 1
    assert source_patched.count("if step >= CR082_PREFIX:\n            market = self._cr053_counter_market(step, market, proj)") == 1
    assert source_patched.count("if step >= CR082_PREFIX and surplus > 0 and prices.get(it, 0) > 1:") == 1
    if "EpisodeId" in source_patched or "TeamNames" in source_patched:
        raise RuntimeError("forbidden identity metadata string found in candidate source")

    ns = {}
    exec(compile(source_patched, "cr082_main.py", "exec"), ns)
    policy_queries = 0
    for k in [0, 8, 16, 24, 32, 40, 48, 63]:
        ep, _, path = rows[k]
        d = json.loads(path.read_text(encoding="utf-8"))
        seat = list(d.get("info", {}).get("TeamNames") or []).index(TEAM)
        for t in range(PREFIX):
            obs = d["steps"][t][seat]["observation"]
            expected = _reference_predict(model[t], features(obs, seat))
            got = ns["_cr082_policy_market"](obs, seat, t)
            policy_queries += 1
            if got != expected:
                raise RuntimeError(f"runtime/reference policy mismatch ep={ep} step={t}: {got!r} != {expected!r}")

    base_ns = {}
    exec(compile(source_base, "cr071m_main.py", "exec"), base_ns)
    physical_queries = 0
    for k in [0, 16, 32, 48, 63]:
        ep, _, path = rows[k]
        d = json.loads(path.read_text(encoding="utf-8"))
        seat = list(d.get("info", {}).get("TeamNames") or []).index(TEAM)
        a = base_ns["Agent"]()
        b = ns["Agent"]()
        for t in range(PREFIX):
            obs = d["steps"][t][seat]["observation"]
            oa = a.act(obs)
            ob = b.act(obs)
            physical_queries += 1
            if oa.get("farmer") != ob.get("farmer") or oa.get("hands") != ob.get("hands"):
                raise RuntimeError(f"physical backbone mismatch ep={ep} step={t}")
    return {
        "source_strategic_isolation_pass": True,
        "runtime_policy_equivalence_queries": policy_queries,
        "runtime_policy_equivalence_mismatches": 0,
        "physical_backbone_equivalence_queries": physical_queries,
        "physical_backbone_equivalence_mismatches": 0,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--majkel-root", type=Path, required=True)
    ap.add_argument("--cr071m", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--manifest", type=Path, required=True)
    a = ap.parse_args()

    rows = load_rows(a.majkel_root)
    dev, model, zero_threshold_steps = build_model(rows)
    source = extract_main(a.cr071m)
    patched, blob_meta = patch_source(source, model)
    compile(patched, "main.py", "exec")
    audit = self_audit(source, patched, rows, model)
    write_tar(a.output, patched)

    teacher_ids = [ep for ep, _, _ in dev]
    manifest = {
        "schema_version": "cr082-state-adaptive-1nn-v1-frozen",
        "candidate": "CR082",
        "architecture": "unchanged CR071M physical/runtime backbone + same-step current-state Majkel 1-NN market prefix",
        "prefix_steps": PREFIX,
        "runtime_market_window": [0, PREFIX - 1],
        "teacher_total_original_episodes": len(rows),
        "teacher_development_episodes": len(dev),
        "teacher_episode_range": [teacher_ids[0], teacher_ids[-1]],
        "teacher_episode_ids": teacher_ids,
        "teacher_newest_16_not_used_in_build": True,
        "feature_dimension": len(model[0]["sd"]),
        "features": "day/hour; own money; hand count; hires_today; unlocked quadrants; own shed products/animals; own seeds; public prices; public market inventory",
        "per_step_standardization": "teacher mean/std ddof=0 (mean cancels from pairwise runtime distance)",
        "distance": "euclidean_zscore",
        "k": 1,
        "tie_break": "first/oldest teacher example at same step (numpy argmin semantics)",
        "ood_threshold": "per-step 95th percentile of leave-one-out nearest-neighbor Euclidean z-score distance",
        "ood_fallback": "per-step exact modal teacher market queue",
        "zero_threshold_steps": zero_threshold_steps,
        "model_raw_sha256": blob_meta[0],
        "model_compressed_sha256": blob_meta[1],
        "model_raw_bytes": blob_meta[2],
        "model_compressed_bytes": blob_meta[3],
        "base_cr071m_sha256": sha256_bytes(a.cr071m.read_bytes()),
        "candidate_sha256": sha256_bytes(a.output.read_bytes()),
        "room_guard_retained_in_prefix": True,
        "clamp_sells_retained_in_prefix": True,
        "same_turn_buy_product_funds_later_sell_in_prefix": True,
        "cr053_counter_disabled_in_prefix": True,
        "dead_stock_disabled_in_prefix": True,
        "farmer_hands_source": "CR071M same-step unchanged",
        "identity_features": False,
        "episode_id_feature": False,
        "seed_feature": False,
        "future_state_feature": False,
        "opponent_private_feature": False,
        "replay_continuation": False,
        "self_audit": audit,
    }
    a.manifest.parent.mkdir(parents=True, exist_ok=True)
    a.manifest.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
