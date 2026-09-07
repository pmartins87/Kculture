"""CR050: channel-gated state-conditioned clone of the frozen live king.

CR049 proved that copying a whole composite action from one nearest state is
catastrophic off-manifold.  This experiment keeps CR029 as the coherent base
policy and learns farmer / hands / market independently.  Every channel model:

* is trained only on the exact 32 public episodes frozen by CR049;
* chooses its feature mask and categorical penalty by train-only leave-one-
  episode-out exact-action accuracy;
* z-scores continuous features at each clock before distance measurement;
* chooses a conservative distance gate from train-only LOO precision/coverage;
* replaces only its own channel when the live state lies inside that gate.

Seven fixed channel combinations are screened on a development seed panel.  At
most two finalists are then evaluated on an independent larger seed panel.
Nothing is submitted to Kaggle automatically.
"""
from __future__ import annotations

import argparse
import copy
import itertools
import json
import math
import random
import statistics
import time
from pathlib import Path

import numpy as np
import kagsim

import cr049_live_king_knn_clone as c49

ROOT = Path(__file__).resolve().parents[1]
CFG = ROOT / "configs/cr050_channel_gated_clone.json"
PASS = {"farmer": ["PASS"], "hands": [], "market": []}
CHANNELS = ("farmer", "hands", "market")


def make_seeds(spec: dict) -> list[int]:
    r = random.Random(int(spec["master_seed"]))
    lo, hi = int(spec["range_min"]), int(spec["range_max"])
    n = int(spec["count"])
    out = set()
    while len(out) < n:
        out.add(r.randint(lo, hi))
    return sorted(out)


def mask_indices(name: str) -> np.ndarray:
    # c49.signature layout:
    # own farm 0:44 | opponent farm 44:88 | shed 88:97 | seeds 97:106 |
    # actor inventories 106:223 | market prices/inventory/demand 223:250.
    if name == "full":
        idx = list(range(250))
    elif name == "own_opp_market":
        idx = list(range(0, 88)) + list(range(223, 250))
    elif name == "own_private_market":
        idx = list(range(0, 44)) + list(range(88, 250))
    elif name == "own_market":
        idx = list(range(0, 44)) + list(range(223, 250))
    elif name == "money_shed_market":
        idx = [0] + list(range(88, 97)) + list(range(223, 250))
    elif name == "money_private_market":
        idx = [0] + list(range(88, 250))
    else:
        raise KeyError(name)
    return np.asarray(idx, dtype=np.int32)


def channel_canon(action: dict, channel: str) -> str:
    default = ["PASS"] if channel == "farmer" else []
    return json.dumps((action or {}).get(channel, default), sort_keys=True,
                      separators=(",", ":"), ensure_ascii=True)


def list_frozen_episodes(cfg: dict) -> tuple[list[dict], list[dict]]:
    sid = int(cfg["source_submission_id"])
    eps = c49.fetch_json(c49.LIST_URL, post={"submissionId": sid}).get("episodes") or []
    meta = {int(e["id"]): e for e in eps if e.get("id") is not None}
    want_train = [int(x) for x in cfg["train_episode_ids"]]
    want_hold = [int(x) for x in cfg["holdout_episode_ids"]]
    missing = [x for x in want_train + want_hold if x not in meta]
    if missing:
        raise RuntimeError(f"frozen episode metadata missing: {missing}")
    train = [c49.episode_pairs(meta[eid], sid) for eid in want_train]
    hold = [c49.episode_pairs(meta[eid], sid) for eid in want_hold]
    return train, hold


def zprep(x: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    mu = x.mean(axis=0)
    sd = x.std(axis=0)
    # Very small variance dimensions otherwise explode harmless observation noise.
    sd = np.where(sd < 0.05, 0.05, sd).astype(np.float32)
    return ((x - mu[None, :]) / sd[None, :]).astype(np.float32), mu.astype(np.float32), sd


def loo_spec(train: list[dict], channel: str, mask_name: str, cat_penalty: float) -> dict:
    idx = mask_indices(mask_name)
    correct = 0
    total = 0
    distances: list[float] = []
    labels: list[bool] = []
    for t in range(719):
        full = np.stack([e["pairs"][t][0] for e in train], axis=0)
        x, _, _ = zprep(full[:, idx])
        cats = [e["pairs"][t][1] for e in train]
        target = [channel_canon(e["pairs"][t][2], channel) for e in train]
        # 32x32 matrix is tiny and avoids Python inner-neighbor loops.
        d = np.sum((x[:, None, :] - x[None, :, :]) ** 2, axis=2)
        if cat_penalty:
            cp = np.zeros_like(d)
            for i in range(len(train)):
                for j in range(len(train)):
                    cp[i, j] = sum(a != b for a, b in zip(cats[i], cats[j]))
            d += float(cat_penalty) * cp
        np.fill_diagonal(d, np.inf)
        nn = np.argmin(d, axis=1)
        md = d[np.arange(len(train)), nn]
        for i, j in enumerate(nn.tolist()):
            ok = target[i] == target[j]
            correct += int(ok)
            total += 1
            distances.append(float(md[i]))
            labels.append(bool(ok))
    return {
        "channel": channel,
        "mask": mask_name,
        "cat_penalty": float(cat_penalty),
        "accuracy": correct / total if total else 0.0,
        "correct": correct,
        "total": total,
        "distances": distances,
        "labels": labels,
    }


def choose_gate(spec: dict, quantiles: list[float]) -> dict:
    ds = np.asarray(spec["distances"], dtype=np.float64)
    labels = np.asarray(spec["labels"], dtype=np.bool_)
    candidates = []
    for q in quantiles:
        thr = float(np.quantile(ds, float(q)))
        use = ds <= thr
        coverage = float(use.mean()) if len(use) else 0.0
        precision = float(labels[use].mean()) if use.any() else 0.0
        utility = precision * math.sqrt(max(coverage, 1e-12))
        candidates.append({"quantile": float(q), "threshold": thr,
                           "coverage": coverage, "precision": precision,
                           "utility": utility})
    # Training-only choice.  Higher utility first, then higher precision, then
    # lower coverage (more conservative) as a deterministic tie-break.
    best = max(candidates, key=lambda x: (x["utility"], x["precision"], -x["coverage"]))
    return {"chosen": best, "candidates": candidates}


class ChannelModel:
    def __init__(self, train: list[dict], channel: str, spec: dict, threshold: float):
        self.channel = channel
        self.mask_name = spec["mask"]
        self.idx = mask_indices(self.mask_name)
        self.cat_penalty = float(spec["cat_penalty"])
        self.threshold = float(threshold)
        self.x = []
        self.mu = []
        self.sd = []
        self.cats = []
        self.values = []
        for t in range(719):
            full = np.stack([e["pairs"][t][0] for e in train], axis=0)
            z, mu, sd = zprep(full[:, self.idx])
            self.x.append(z)
            self.mu.append(mu)
            self.sd.append(sd)
            self.cats.append([e["pairs"][t][1] for e in train])
            default = ["PASS"] if channel == "farmer" else []
            self.values.append([copy.deepcopy((e["pairs"][t][2] or {}).get(channel, default)) for e in train])

    def predict(self, obs: dict, t: int) -> tuple[object, float, bool]:
        t = max(0, min(718, int(t)))
        q, cats = c49.signature(obs)
        z = (q[self.idx] - self.mu[t]) / self.sd[t]
        d = np.sum((self.x[t] - z[None, :]) ** 2, axis=1)
        if self.cat_penalty:
            d += self.cat_penalty * np.asarray(
                [sum(a != b for a, b in zip(cats, tc)) for tc in self.cats[t]],
                dtype=np.float32,
            )
        j = int(np.argmin(d))
        md = float(d[j])
        return copy.deepcopy(self.values[t][j]), md, md <= self.threshold


def train_models(train: list[dict], hold: list[dict], cfg: dict) -> tuple[dict, dict]:
    models = {}
    report = {}
    for channel in CHANNELS:
        specs = []
        for mask in cfg["feature_masks"][channel]:
            for cp in cfg["categorical_penalties"]:
                s = loo_spec(train, channel, mask, float(cp))
                gate = choose_gate(s, cfg["gate_quantiles"])
                slim = {k: v for k, v in s.items() if k not in ("distances", "labels")}
                slim["gate"] = gate
                specs.append((s, slim))
        # Feature choice is based only on train LOO exact-channel accuracy.
        chosen_raw, chosen_slim = max(
            specs,
            key=lambda z: (z[0]["accuracy"], z[0]["gate"]["chosen"]["utility"] if "gate" in z[0] else 0.0,
                           -z[0]["cat_penalty"]),
        )
        # choose_gate was attached to slim, not raw.
        gate = choose_gate(chosen_raw, cfg["gate_quantiles"])
        threshold = float(gate["chosen"]["threshold"])
        model = ChannelModel(train, channel, chosen_raw, threshold)
        models[channel] = model

        # Public replay holdout: diagnostic only, never used for model/gate selection.
        hc = 0; hu = 0; hcorrect = 0; hdist = []
        for e in hold:
            for t, (_, _, action) in enumerate(e["pairs"]):
                # We have the vector but not the raw obs here, so evaluate holdout
                # nearest-neighbor directly in normalized feature space.
                qvec, qcats = e["pairs"][t][0], e["pairs"][t][1]
                z = (qvec[model.idx] - model.mu[t]) / model.sd[t]
                d = np.sum((model.x[t] - z[None, :]) ** 2, axis=1)
                if model.cat_penalty:
                    d += model.cat_penalty * np.asarray(
                        [sum(a != b for a, b in zip(qcats, tc)) for tc in model.cats[t]], dtype=np.float32)
                j = int(np.argmin(d)); md = float(d[j]); pred = model.values[t][j]
                target = (action or {}).get(channel, ["PASS"] if channel == "farmer" else [])
                ok = json.dumps(pred, sort_keys=True, separators=(",",":")) == json.dumps(target, sort_keys=True, separators=(",",":"))
                hcorrect += int(ok); hc += 1; hdist.append(md)
                if md <= model.threshold:
                    hu += 1
        report[channel] = {
            "chosen_spec": {"mask": chosen_raw["mask"], "cat_penalty": chosen_raw["cat_penalty"],
                            "loo_accuracy": chosen_raw["accuracy"], "gate": gate},
            "holdout_exact_accuracy": hcorrect / hc if hc else None,
            "holdout_gate_coverage": hu / hc if hc else None,
            "holdout_median_distance": statistics.median(hdist) if hdist else None,
            "all_train_specs": [x[1] for x in specs],
        }
    return models, report


def candidate_action(models: dict, enabled: tuple[str, ...], obs: dict, t: int, base: dict,
                     counters: dict | None = None) -> dict:
    out = copy.deepcopy(base or PASS)
    out.setdefault("farmer", ["PASS"])
    out.setdefault("hands", [])
    out.setdefault("market", [])
    for channel in enabled:
        value, distance, use = models[channel].predict(obs, t)
        if counters is not None:
            counters[channel]["queries"] += 1
            counters[channel]["distances"].append(distance)
            counters[channel]["used"] += int(use)
        if use:
            out[channel] = value
    return out


def play(models: dict, enabled: tuple[str, ...], base_actions: list[dict], seed: int, seat: int) -> tuple[float, float, dict]:
    game = kagsim.Game(int(seed))
    counters = {ch: {"queries": 0, "used": 0, "distances": []} for ch in enabled}
    while not game.done:
        t = int(game.step_count)
        base = base_actions[t] if t < len(base_actions) else PASS
        if seat == 0:
            a0 = candidate_action(models, enabled, game.observe(0), t, base, counters)
            a1 = base
        else:
            a0 = base
            a1 = candidate_action(models, enabled, game.observe(1), t, base, counters)
        game.step(a0 or PASS, a1 or PASS)
    telemetry = {}
    for ch, c in counters.items():
        telemetry[ch] = {
            "queries": c["queries"], "used": c["used"],
            "coverage": c["used"] / c["queries"] if c["queries"] else 0.0,
            "median_distance": statistics.median(c["distances"]) if c["distances"] else None,
        }
    return float(game.reward(seat)), float(game.reward(1-seat)), telemetry


def metrics(rows: list[dict]) -> dict:
    ms = [float(r["margin"]) for r in rows]
    w = sum(x > 0 for x in ms); l = sum(x < 0 for x in ms); ti = len(ms) - w - l
    out = {
        "games": len(rows), "wins": w, "losses": l, "ties": ti,
        "score_rate": (w + 0.5 * ti) / len(rows) if rows else None,
        "mean_margin": statistics.mean(ms) if ms else None,
        "median_margin": statistics.median(ms) if ms else None,
    }
    cov = {}
    for ch in CHANNELS:
        vals = [r["telemetry"][ch]["coverage"] for r in rows if ch in r["telemetry"]]
        if vals:
            cov[ch] = statistics.mean(vals)
    out["mean_channel_coverage"] = cov
    return out


def evaluate_panel(models: dict, candidates: dict[str, tuple[str, ...]], base: list[dict], seeds: list[int], label: str) -> tuple[dict, list[dict]]:
    reports = {}; errors = []
    for cid, enabled in candidates.items():
        rows = []
        start = time.time()
        for i, seed in enumerate(seeds):
            for seat in (0, 1):
                try:
                    mine, opp, tele = play(models, enabled, base, int(seed), seat)
                    rows.append({"seed": int(seed), "seat": seat, "reward": mine,
                                 "opponent_reward": opp, "margin": mine - opp,
                                 "telemetry": tele})
                except Exception as exc:
                    errors.append({"panel": label, "candidate": cid, "seed": int(seed),
                                   "seat": seat, "error": repr(exc)[:1000]})
            if (i + 1) % 32 == 0:
                print(json.dumps({"panel": label, "candidate": cid, "seeds": i + 1,
                                  "games": len(rows), "errors": len(errors),
                                  "elapsed_s": time.time() - start}))
        reports[cid] = {"enabled_channels": list(enabled), "metrics": metrics(rows)}
    return reports, errors


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source-bundle", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()
    cfg = json.loads(CFG.read_text(encoding="utf-8"))

    if str(getattr(kagsim, "ENGINE_VERSION", "")) != "1.32.7":
        raise RuntimeError(f"wrong kagsim engine: {getattr(kagsim, 'ENGINE_VERSION', None)}")
    idle = kagsim.Stream([])
    if tuple(kagsim.run_episode(idle, idle, seed=11)) != (3000.0, 3000.0):
        raise RuntimeError("kagsim self-check failed")

    train, hold = list_frozen_episodes(cfg)
    models, imitation = train_models(train, hold, cfg)

    bundle = json.loads(Path(args.source_bundle).read_text(encoding="utf-8"))
    base = bundle["recent_top"]["tape"]
    if len(base) != 719:
        raise RuntimeError(f"CR029 base length {len(base)}")

    candidates = {
        "farmer": ("farmer",),
        "hands": ("hands",),
        "market": ("market",),
        "farmer_hands": ("farmer", "hands"),
        "farmer_market": ("farmer", "market"),
        "hands_market": ("hands", "market"),
        "all": ("farmer", "hands", "market"),
    }
    dev_seeds = make_seeds(cfg["dev_seed_generator"])
    val_seeds = make_seeds(cfg["validation_seed_generator"])
    overlap = sorted(set(dev_seeds) & set(val_seeds))
    if overlap:
        raise RuntimeError(f"dev/validation seed overlap: {overlap[:5]}")

    dev, errors = evaluate_panel(models, candidates, base, dev_seeds, "dev")
    minimum = float(cfg["selection"]["min_dev_score_rate_vs_cr029"])
    ranking = sorted(
        [cid for cid in candidates if dev[cid]["metrics"]["score_rate"] is not None],
        key=lambda cid: (dev[cid]["metrics"]["score_rate"], dev[cid]["metrics"]["mean_margin"]),
        reverse=True,
    )
    finalists = [cid for cid in ranking if dev[cid]["metrics"]["score_rate"] >= minimum]
    finalists = finalists[:int(cfg["selection"]["max_finalists"])]

    val = {}
    if finalists:
        val_candidates = {cid: candidates[cid] for cid in finalists}
        val, e2 = evaluate_panel(models, val_candidates, base, val_seeds, "validation")
        errors.extend(e2)

    passing = []
    for cid in finalists:
        m = val[cid]["metrics"]
        if (m["score_rate"] >= float(cfg["selection"]["min_validation_score_rate_vs_cr029"])
                and m["mean_margin"] >= float(cfg["selection"]["min_validation_mean_margin"])):
            passing.append(cid)
    passing.sort(key=lambda cid: (val[cid]["metrics"]["score_rate"], val[cid]["metrics"]["mean_margin"]), reverse=True)
    selected = passing[0] if passing else None

    payload = {
        "experiment": cfg["experiment"],
        "engine": "1.32.7",
        "source_submission_id": int(cfg["source_submission_id"]),
        "train_episode_ids": cfg["train_episode_ids"],
        "holdout_episode_ids": cfg["holdout_episode_ids"],
        "train_samples": len(train) * 719,
        "holdout_samples": len(hold) * 719,
        "imitation": imitation,
        "dev_seed_generator": cfg["dev_seed_generator"],
        "validation_seed_generator": cfg["validation_seed_generator"],
        "seed_overlap": overlap,
        "dev": dev,
        "dev_ranking": ranking,
        "finalists": finalists,
        "validation": val,
        "passing": passing,
        "selected_for_next_stage": selected,
        "errors": errors,
        "decision": (f"SHORTLIST_{selected}_FOR_PACKAGE_PREFLIGHT" if selected
                     else "CR050_NO_CHANNEL_GATED_CLONE_PROMOTION"),
        "kaggle_hidden_test_touched": false,
        "automatic_kaggle_submission": false,
    }
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    if errors:
        raise SystemExit(3)


if __name__ == "__main__":
    main()
