#!/usr/bin/env python3
"""CR079 SpaTaro chronological imitation gate.

Implements the preregistered protocol in
`docs/strategy/CR079_SPATARO_CLONE_PROTOCOL_2026-09-11.md`.

The script intentionally uses a simple same-step 1-nearest-neighbour policy,
with a clock-only modal baseline and a strict episode-level chronological holdout.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import re
import statistics
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import numpy as np

try:
    import orjson as _orjson
except Exception:  # pragma: no cover - standard json remains supported
    _orjson = None


def load_json_file(path: Path) -> Any:
    if _orjson is not None:
        return _orjson.loads(path.read_bytes())
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


TARGET = "SpaTaro"
MISSING = "<MISSING>"
UUID_RE = re.compile(r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-5][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}$")
HEX_ID_RE = re.compile(r"^[0-9a-fA-F]{24,64}$")

CROPS = ["CARROT", "MELON", "STRAWBERRY", "TOMATO", "WHEAT"]
ANIMALS = ["COW", "GOOSE", "SHEEP"]
MARKET_ITEMS = ["CARROT", "EGG", "FERTILIZER", "MELON", "MILK", "STRAWBERRY", "TOMATO", "WHEAT", "WOOL"]
PRIVATE_ITEMS = MARKET_ITEMS + ANIMALS
SHOPS = ["BAKERY", "BRUNCH_SPOT", "FARMERS_MARKET", "ICE_CREAM_SHOP", "PET_CAFE", "PIZZA_SHOP", "SMOOTHIE_SHOP", "YARN_STORE"]
QUADRANTS = ["NW", "NE", "SW", "SE"]
TILE_KINDS = ["PLANT", "PASTURE", "COOP", "WEED"]
UNKNOWN_BUCKETS = 4

WEIGHTS = {"farmer": 0.40, "hands": 0.35, "market": 0.25}
GATES = {
    "composite_min": 0.55,
    "delta_min": 0.08,
    "farmer_min": 0.50,
    "hands_min": 0.50,
    "market_min": 0.35,
}


def stable_bucket(value: str, n: int = UNKNOWN_BUCKETS) -> int:
    h = hashlib.blake2b(value.encode("utf-8"), digest_size=8, person=b"cr079v1").digest()
    return int.from_bytes(h, "little") % n


def _num(v: Any, default: float = 0.0) -> float:
    if isinstance(v, bool):
        return float(v)
    if isinstance(v, (int, float)) and math.isfinite(float(v)):
        return float(v)
    return default


def _scrub(obj: Any) -> Any:
    if isinstance(obj, str):
        if UUID_RE.match(obj) or HEX_ID_RE.match(obj):
            return "<ID>"
        return obj
    if isinstance(obj, list):
        return [_scrub(x) for x in obj]
    if isinstance(obj, tuple):
        return [_scrub(x) for x in obj]
    if isinstance(obj, dict):
        return {str(k): _scrub(v) for k, v in sorted(obj.items(), key=lambda kv: str(kv[0]))}
    if isinstance(obj, float) and obj.is_integer():
        return int(obj)
    return obj


def canon(obj: Any) -> str:
    return json.dumps(_scrub(obj), sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def action_labels(action: Any) -> tuple[str, list[str], str]:
    if not isinstance(action, dict):
        action = {}
    farmer = action.get("farmer") or ["PASS"]
    hands = action.get("hands") or []
    market = action.get("market") or []
    return canon(farmer), [canon(a or ["PASS"]) for a in hands], canon(market)


def add_unknown_buckets(vec: list[float], pairs: Iterable[tuple[str, float]], known: set[str]) -> None:
    buckets = [0.0] * UNKNOWN_BUCKETS
    for k, v in pairs:
        if k not in known:
            buckets[stable_bucket(str(k))] += _num(v)
    vec.extend(buckets)


def farm_features(farm: dict[str, Any], current_step: int) -> list[float]:
    v: list[float] = []
    farmer = farm.get("farmer") or [0, 0]
    hands = farm.get("hands") or []
    quads = farm.get("unlocked_quadrants") or []
    v.extend([
        _num(farm.get("money")),
        _num(farmer[0] if len(farmer) > 0 else 0),
        _num(farmer[1] if len(farmer) > 1 else 0),
        _num(farm.get("hires_today")),
        float(len(hands)),
    ])
    v.extend([1.0 if q in quads else 0.0 for q in QUADRANTS])

    xs = [_num(h[0]) for h in hands if isinstance(h, (list, tuple)) and len(h) >= 2]
    ys = [_num(h[1]) for h in hands if isinstance(h, (list, tuple)) and len(h) >= 2]
    if xs:
        v.extend([sum(xs), sum(ys), min(xs), max(xs), min(ys), max(ys)])
    else:
        v.extend([0.0] * 6)
    row_hist = [0.0] * 10
    col_hist = [0.0] * 10
    for x, y in zip(xs, ys):
        xi, yi = int(round(x)), int(round(y))
        if 0 <= xi < 10:
            col_hist[xi] += 1.0
        if 0 <= yi < 10:
            row_hist[yi] += 1.0
    v.extend(row_hist)
    v.extend(col_hist)

    tiles = farm.get("tiles") or []
    kind = Counter()
    crop = Counter()
    animal = Counter()
    crop_unknown = [0.0] * UNKNOWN_BUCKETS
    animal_unknown = [0.0] * UNKNOWN_BUCKETS
    locked = empty = other_string = 0.0
    watered = unwatered = fertilized = 0.0
    fed = unfed = cared = uncared = fertilizer_available = 0.0
    yield_units = consecutive_unwatered = consecutive_unfed = remaining_life = 0.0

    for row in tiles:
        if not isinstance(row, list):
            continue
        for t in row:
            if t is None:
                empty += 1.0
                continue
            if isinstance(t, str):
                if t == "LOCKED":
                    locked += 1.0
                else:
                    other_string += 1.0
                continue
            if not isinstance(t, dict):
                other_string += 1.0
                continue
            k = str(t.get("kind") or "OTHER")
            kind[k] += 1
            c = t.get("crop")
            if c:
                c = str(c)
                if c in CROPS:
                    crop[c] += 1
                else:
                    crop_unknown[stable_bucket(c)] += 1.0
            a = t.get("animal")
            if a:
                a = str(a)
                if a in ANIMALS:
                    animal[a] += 1
                else:
                    animal_unknown[stable_bucket(a)] += 1.0
            if "watered_today" in t:
                if t.get("watered_today"):
                    watered += 1.0
                else:
                    unwatered += 1.0
            if _num(t.get("fertilized_until_day"), -1) >= 0:
                fertilized += 1.0
            if "fed_today" in t:
                if t.get("fed_today"):
                    fed += 1.0
                else:
                    unfed += 1.0
            if "cared_today" in t:
                if t.get("cared_today"):
                    cared += 1.0
                else:
                    uncared += 1.0
            if t.get("fertilizer_available"):
                fertilizer_available += 1.0
            yield_units += _num(t.get("yield_units"))
            consecutive_unwatered += _num(t.get("consecutive_unwatered"))
            consecutive_unfed += _num(t.get("consecutive_unfed"))
            ml = t.get("max_lifespan_step")
            if isinstance(ml, (int, float)):
                remaining_life += max(0.0, float(ml) - float(current_step))

    v.extend([empty, locked, other_string])
    v.extend([float(kind[k]) for k in TILE_KINDS])
    v.append(float(sum(n for k, n in kind.items() if k not in TILE_KINDS)))
    v.extend([float(crop[c]) for c in CROPS])
    v.extend(crop_unknown)
    v.extend([float(animal[a]) for a in ANIMALS])
    v.extend(animal_unknown)
    v.extend([
        watered, unwatered, fertilized, fed, unfed, cared, uncared,
        fertilizer_available, yield_units, consecutive_unwatered,
        consecutive_unfed, remaining_life,
    ])
    return v


def private_features(priv: dict[str, Any]) -> list[float]:
    v: list[float] = []
    seeds = priv.get("seeds") or {}
    v.extend([_num(seeds.get(k)) for k in CROPS])
    add_unknown_buckets(v, ((str(k), _num(val)) for k, val in seeds.items()), set(CROPS))

    shed = priv.get("shed") or {}
    v.extend([_num(shed.get(k)) for k in PRIVATE_ITEMS])
    add_unknown_buckets(v, ((str(k), _num(val)) for k, val in shed.items()), set(PRIVATE_ITEMS))

    invs = priv.get("inventories") or []
    agg: Counter[str] = Counter()
    total = 0.0
    nonempty = 0.0
    for inv in invs:
        if not isinstance(inv, dict):
            continue
        if inv:
            nonempty += 1.0
        for k, val in inv.items():
            q = _num(val)
            agg[str(k)] += q
            total += q
    v.extend([float(len(invs)), nonempty, total])
    v.extend([float(agg.get(k, 0.0)) for k in PRIVATE_ITEMS])
    add_unknown_buckets(v, ((k, float(val)) for k, val in agg.items()), set(PRIVATE_ITEMS))
    return v


def market_features(market: dict[str, Any]) -> list[float]:
    v: list[float] = []
    prices = market.get("prices") or {}
    inv = market.get("inventory") or {}
    for k in MARKET_ITEMS:
        v.extend([_num(prices.get(k)), _num(inv.get(k))])
    known = set(MARKET_ITEMS)
    add_unknown_buckets(v, ((str(k), _num(val)) for k, val in prices.items()), known)
    add_unknown_buckets(v, ((str(k), _num(val)) for k, val in inv.items()), known)
    return v


def town_features(town: dict[str, Any]) -> list[float]:
    shops = [str(s) for s in (town.get("unlocked_shops") or [])]
    counts = Counter(shops)
    v = [float(len(shops))]
    v.extend([float(counts[s]) for s in SHOPS])
    unknown = [0.0] * UNKNOWN_BUCKETS
    for s, n in counts.items():
        if s not in SHOPS:
            unknown[stable_bucket(s)] += float(n)
    v.extend(unknown)
    return v


def extract_vector(obs: dict[str, Any], seat: int, step: int) -> np.ndarray:
    day = _num(obs.get("day"), step // 24)
    hour = _num(obs.get("hour"), step % 24)
    player = int(_num(obs.get("player"), seat))
    v: list[float] = [float(step), day, hour, float(player)]

    farms = obs.get("farms") or []
    own = farms[seat] if seat < len(farms) and isinstance(farms[seat], dict) else {}
    opp_seat = 1 - seat if len(farms) >= 2 else seat
    opp = farms[opp_seat] if opp_seat < len(farms) and isinstance(farms[opp_seat], dict) else {}
    v.extend(farm_features(own, step))
    v.extend(farm_features(opp, step))
    v.extend(private_features(obs.get("private") or {}))
    v.extend(market_features(obs.get("market") or {}))
    v.extend(town_features(obs.get("town") or {}))
    return np.asarray(v, dtype=np.float32)


def parse_chronology(path: Path) -> dict[int, str]:
    payload = load_json_file(path)
    stdout = payload.get("stdout", "")
    out: dict[int, str] = {}
    stripped = stdout.lstrip()
    if stripped.startswith("{") or stripped.startswith("["):
        raw = json.loads(stdout)
        episodes = raw.get("episodes", []) if isinstance(raw, dict) else raw
        for e in episodes:
            try:
                out[int(e["id"])] = str(e.get("createTime") or e.get("create_time") or "")
            except Exception:
                pass
        return out
    for row in csv.DictReader(io.StringIO(stdout)):
        try:
            out[int(row["id"])] = str(row.get("createTime") or "")
        except Exception:
            continue
    return out


@dataclass(frozen=True)
class EpisodeRef:
    episode_id: int
    path: Path
    seat: int
    create_time: str


def discover_episodes(replay_dir: Path, chronology: dict[int, str]) -> tuple[list[EpisodeRef], dict[str, Any]]:
    refs: list[EpisodeRef] = []
    ambiguous: list[int] = []
    missing_target: list[int] = []
    fallback_chronology: list[int] = []
    all_files = sorted(replay_dir.glob("*.json"))
    for path in all_files:
        # `info` precedes the multi-megabyte `steps` array. Prefix discovery avoids
        # decoding the 6+ GB corpus twice.
        with path.open("r", encoding="utf-8") as f:
            prefix = f.read(262144)
        m_id = re.search(r'"EpisodeId"\s*:\s*(\d+)', prefix)
        if not m_id:
            m_id = re.search(r'episode-(\d+)-replay', path.name)
        if not m_id:
            raise RuntimeError(f"cannot discover episode id from {path}")
        eid = int(m_id.group(1))
        m_names = re.search(r'"TeamNames"\s*:\s*(\[[^\]]*\])', prefix)
        if m_names:
            try:
                names = list(json.loads(m_names.group(1)))
            except Exception:
                names = []
        else:
            names = []
        if not names:
            d = load_json_file(path)
            names = list((d.get("info") or {}).get("TeamNames") or [])
        seats = [i for i, name in enumerate(names) if name == TARGET]
        if len(seats) != 1:
            if len(seats) > 1:
                ambiguous.append(eid)
            else:
                missing_target.append(eid)
            continue
        ct = chronology.get(eid, "")
        if not ct:
            ct = f"9999-12-31T23:59:59Z::{eid:020d}"
            fallback_chronology.append(eid)
        refs.append(EpisodeRef(eid, path, seats[0], ct))
    refs.sort(key=lambda r: (r.create_time, r.episode_id))
    meta = {
        "replay_files": len(all_files),
        "usable_unique_target": len(refs),
        "ambiguous_target_count": len(ambiguous),
        "ambiguous_episode_ids": sorted(ambiguous),
        "missing_target_count": len(missing_target),
        "missing_target_episode_ids": sorted(missing_target),
        "chronology_fallback_count": len(fallback_chronology),
        "chronology_fallback_episode_ids": sorted(fallback_chronology),
    }
    return refs, meta


def lexical_mode(labels: Iterable[str]) -> str:
    c = Counter(labels)
    if not c:
        return MISSING
    mx = max(c.values())
    return min(k for k, n in c.items() if n == mx)


@dataclass
class TrainStep:
    X: np.ndarray
    Z: np.ndarray
    mean: np.ndarray
    scale: np.ndarray
    farmer: list[str]
    hands: list[list[str]]
    market: list[str]
    baseline_farmer: str
    baseline_hands: list[str]
    baseline_market: str


@dataclass
class MetricAcc:
    farmer_correct: int = 0
    farmer_total: int = 0
    hands_correct: int = 0
    hands_total: int = 0
    hands_whole_correct: int = 0
    hands_whole_total: int = 0
    market_correct: int = 0
    market_total: int = 0

    def update(self, pred: tuple[str, list[str], str], actual: tuple[str, list[str], str]) -> None:
        pf, ph, pm = pred
        af, ah, am = actual
        self.farmer_total += 1
        self.farmer_correct += int(pf == af)
        self.market_total += 1
        self.market_correct += int(pm == am)
        self.hands_whole_total += 1
        self.hands_whole_correct += int(ph == ah)
        n = max(len(ph), len(ah))
        for i in range(n):
            p = ph[i] if i < len(ph) else MISSING
            a = ah[i] if i < len(ah) else MISSING
            self.hands_total += 1
            self.hands_correct += int(p == a)

    def metrics(self) -> dict[str, float]:
        farmer = self.farmer_correct / self.farmer_total if self.farmer_total else 0.0
        hands = self.hands_correct / self.hands_total if self.hands_total else 0.0
        market = self.market_correct / self.market_total if self.market_total else 0.0
        hands_whole = self.hands_whole_correct / self.hands_whole_total if self.hands_whole_total else 0.0
        composite = WEIGHTS["farmer"] * farmer + WEIGHTS["hands"] * hands + WEIGHTS["market"] * market
        return {
            "farmer_accuracy": farmer,
            "hands_slot_accuracy": hands,
            "hands_whole_list_accuracy_diagnostic": hands_whole,
            "market_ordered_list_accuracy": market,
            "composite": composite,
        }


def load_records(ref: EpisodeRef) -> list[tuple[int, np.ndarray, tuple[str, list[str], str]]]:
    d = load_json_file(ref.path)
    rows = []
    steps = d.get("steps") or []
    for step, seats in enumerate(steps):
        if ref.seat >= len(seats):
            continue
        state = seats[ref.seat] or {}
        obs = state.get("observation") or {}
        if step < len(steps):
            seat0 = (steps[step][0] or {}) if steps[step] else {}
            shared0 = seat0.get("observation") or {}
            for key in ("step", "day", "hour", "farms", "market", "town"):
                if key not in obs and key in shared0:
                    obs[key] = shared0[key]
        vec = extract_vector(obs, ref.seat, step)
        labels = action_labels(state.get("action"))
        rows.append((step, vec, labels))
    return rows


def build_training(train_refs: list[EpisodeRef]) -> tuple[dict[int, TrainStep], dict[str, Any]]:
    by_step: dict[int, dict[str, list[Any]]] = defaultdict(lambda: {"X": [], "farmer": [], "hands": [], "market": []})
    dim = None
    action_inventory = {"farmer": Counter(), "hand": Counter(), "market": Counter()}
    for epi, ref in enumerate(train_refs, 1):
        for step, vec, labels in load_records(ref):
            if dim is None:
                dim = len(vec)
            elif len(vec) != dim:
                raise RuntimeError(f"feature dimension changed: {len(vec)} != {dim} in episode {ref.episode_id}")
            f, h, m = labels
            b = by_step[step]
            b["X"].append(vec)
            b["farmer"].append(f)
            b["hands"].append(h)
            b["market"].append(m)
            action_inventory["farmer"][f] += 1
            action_inventory["market"][m] += 1
            for ha in h:
                action_inventory["hand"][ha] += 1
        if epi % 20 == 0 or epi == len(train_refs):
            print(f"parsed train episodes {epi}/{len(train_refs)}", flush=True)

    out: dict[int, TrainStep] = {}
    for step in sorted(by_step):
        b = by_step[step]
        X = np.stack(b["X"]).astype(np.float32, copy=False)
        mean = X.mean(axis=0, dtype=np.float64).astype(np.float32)
        scale = X.std(axis=0, dtype=np.float64).astype(np.float32)
        scale[scale < 1e-6] = 1.0
        Z = (X - mean) / scale
        farmer = list(b["farmer"])
        hands = list(b["hands"])
        market = list(b["market"])

        max_slots = max((len(x) for x in hands), default=0)
        bh = []
        for slot in range(max_slots):
            labels = [x[slot] if slot < len(x) else MISSING for x in hands]
            bh.append(lexical_mode(labels))
        while bh and bh[-1] == MISSING:
            bh.pop()

        out[step] = TrainStep(
            X=X,
            Z=Z,
            mean=mean,
            scale=scale,
            farmer=farmer,
            hands=hands,
            market=market,
            baseline_farmer=lexical_mode(farmer),
            baseline_hands=bh,
            baseline_market=lexical_mode(market),
        )
    inv = {
        part: [{"label": k, "count": n} for k, n in c.most_common()]
        for part, c in action_inventory.items()
    }
    return out, {"feature_dim": dim or 0, "action_inventory": inv}


def evaluate(train: dict[int, TrainStep], holdout_refs: list[EpisodeRef]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    candidate_total = MetricAcc()
    baseline_total = MetricAcc()
    per_episode = []
    distances: list[float] = []
    missing_step = 0

    for epi, ref in enumerate(holdout_refs, 1):
        cand = MetricAcc()
        base = MetricAcc()
        epi_dist = []
        for step, vec, actual in load_records(ref):
            tr = train.get(step)
            if tr is None:
                missing_step += 1
                continue
            z = (vec - tr.mean) / tr.scale
            diff = tr.Z - z
            d2 = np.einsum("ij,ij->i", diff, diff, optimize=True)
            idx = int(np.argmin(d2))
            dist = float(math.sqrt(max(0.0, float(d2[idx]))))
            distances.append(dist)
            epi_dist.append(dist)
            pred = (tr.farmer[idx], tr.hands[idx], tr.market[idx])
            baseline = (tr.baseline_farmer, tr.baseline_hands, tr.baseline_market)
            cand.update(pred, actual)
            base.update(baseline, actual)
            candidate_total.update(pred, actual)
            baseline_total.update(baseline, actual)
        per_episode.append({
            "episode_id": ref.episode_id,
            "create_time": ref.create_time,
            "seat": ref.seat,
            "candidate": cand.metrics(),
            "baseline": base.metrics(),
            "mean_nn_distance": float(statistics.fmean(epi_dist)) if epi_dist else None,
        })
        if epi % 10 == 0 or epi == len(holdout_refs):
            print(f"evaluated holdout episodes {epi}/{len(holdout_refs)}", flush=True)

    cm = candidate_total.metrics()
    bm = baseline_total.metrics()
    result = {
        "candidate": cm,
        "baseline": bm,
        "composite_delta": cm["composite"] - bm["composite"],
        "counts": {
            "candidate": candidate_total.__dict__,
            "baseline": baseline_total.__dict__,
            "missing_training_step_decisions": missing_step,
        },
        "nn_distance": {
            "count": len(distances),
            "mean": float(statistics.fmean(distances)) if distances else None,
            "median": float(statistics.median(distances)) if distances else None,
            "p95": float(np.percentile(np.asarray(distances, dtype=np.float32), 95)) if distances else None,
        },
    }
    return result, per_episode


def gate(metrics: dict[str, Any]) -> tuple[bool, dict[str, bool]]:
    c = metrics["candidate"]
    checks = {
        "candidate_composite_ge_0.55": c["composite"] >= GATES["composite_min"],
        "composite_delta_ge_0.08": metrics["composite_delta"] >= GATES["delta_min"],
        "farmer_ge_0.50": c["farmer_accuracy"] >= GATES["farmer_min"],
        "hands_ge_0.50": c["hands_slot_accuracy"] >= GATES["hands_min"],
        "market_ge_0.35": c["market_ordered_list_accuracy"] >= GATES["market_min"],
    }
    return all(checks.values()), checks


def write_report(summary: dict[str, Any], outdir: Path) -> None:
    c = summary["evaluation"]["candidate"]
    b = summary["evaluation"]["baseline"]
    checks = summary["gate_checks"]
    lines = [
        "# CR079 SpaTaro chronological imitation holdout", "",
        f"Decision: **{summary['decision']}**", "", "## Corpus / split", "",
        f"- Replay files: {summary['corpus']['replay_files']}",
        f"- Usable unique-target episodes: {summary['corpus']['usable_unique_target']}",
        f"- Ambiguous SpaTaro-vs-SpaTaro excluded: {summary['corpus']['ambiguous_target_count']}",
        f"- Train episodes: {summary['split']['train_count']}",
        f"- Holdout episodes: {summary['split']['holdout_count']}",
        f"- Train last timestamp: {summary['split']['train_last_create_time']}",
        f"- Holdout first timestamp: {summary['split']['holdout_first_create_time']}",
        "", "## Metrics", "",
        "| Metric | Candidate 1NN | Clock baseline |", "|---|---:|---:|",
        f"| Farmer exact | {c['farmer_accuracy']:.6f} | {b['farmer_accuracy']:.6f} |",
        f"| Hands slot | {c['hands_slot_accuracy']:.6f} | {b['hands_slot_accuracy']:.6f} |",
        f"| Market ordered list | {c['market_ordered_list_accuracy']:.6f} | {b['market_ordered_list_accuracy']:.6f} |",
        f"| Composite | {c['composite']:.6f} | {b['composite']:.6f} |",
        f"| Hands whole-list (diagnostic) | {c['hands_whole_list_accuracy_diagnostic']:.6f} | {b['hands_whole_list_accuracy_diagnostic']:.6f} |",
        "", f"Composite delta: **{summary['evaluation']['composite_delta']:+.6f}**", "",
        "## Frozen gate checks", "",
    ]
    for name, ok in checks.items():
        lines.append(f"- {'PASS' if ok else 'FAIL'} — `{name}`")
    lines.extend(["", "## Interpretation", "", summary["interpretation"], "",
                  "This result is an offline imitation-fidelity test only. A PASS would authorize an executable legality/H2H stage, not a hosted submission by itself."])
    (outdir / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", required=True, type=Path, help="Artifact extraction root or spataro_current directory")
    ap.add_argument("--out", required=True, type=Path)
    args = ap.parse_args()

    root = args.corpus
    current = root / "spataro_current" if (root / "spataro_current").is_dir() else root
    replay_dir = current / "replays"
    chrono_file = current / "episodes_command.json"
    if not replay_dir.is_dir() or not chrono_file.is_file():
        raise SystemExit(f"corpus layout not found below {root}")

    args.out.mkdir(parents=True, exist_ok=True)
    chronology = parse_chronology(chrono_file)
    refs, corpus_meta = discover_episodes(replay_dir, chronology)
    if len(refs) < 4:
        raise SystemExit(f"too few usable episodes: {len(refs)}")

    train_n = int(math.floor(len(refs) * 0.75))
    train_refs = refs[:train_n]
    holdout_refs = refs[train_n:]
    split = {
        "train_count": len(train_refs), "holdout_count": len(holdout_refs),
        "train_first_episode_id": train_refs[0].episode_id,
        "train_last_episode_id": train_refs[-1].episode_id,
        "holdout_first_episode_id": holdout_refs[0].episode_id,
        "holdout_last_episode_id": holdout_refs[-1].episode_id,
        "train_first_create_time": train_refs[0].create_time,
        "train_last_create_time": train_refs[-1].create_time,
        "holdout_first_create_time": holdout_refs[0].create_time,
        "holdout_last_create_time": holdout_refs[-1].create_time,
    }
    print(json.dumps({"corpus": corpus_meta, "split": split}, indent=2), flush=True)

    train, train_meta = build_training(train_refs)
    evaluation, per_episode = evaluate(train, holdout_refs)
    passed, checks = gate(evaluation)
    decision = "PASS" if passed else "FAIL"
    interpretation = (
        "CR079 met every preregistered imitation gate. Proceed to semantic action reconstruction plus exact-environment legality/H2H testing; do not submit from this offline result alone."
        if passed else
        "CR079 failed at least one preregistered imitation gate. Reject simple same-step SpaTaro 1NN cloning on this holdout; do not tune this holdout into CR079A/B/C. Pivot to the predeclared materially different architecture/bridge branch."
    )
    summary = {
        "protocol": "CR079_SPATARO_CLONE_PROTOCOL_2026-09-11", "target": TARGET,
        "corpus_provenance": {
            "source_run_id": 34554072056, "source_artifact_id": 10182031598,
            "source_artifact_name": "hosted-spataro-current-corpus-v1",
            "source_artifact_sha256": "12e17e246c984ceba8a664adf4d05fb1a2f260d96079a1e413135b2bd4eb4a2e",
        },
        "corpus": corpus_meta, "split": split,
        "model": {"name": "same-step standardized 1-nearest-neighbour", "feature_dim": train_meta["feature_dim"], "weights": WEIGHTS, "gates": GATES},
        "evaluation": evaluation, "gate_checks": checks, "decision": decision, "interpretation": interpretation,
    }
    (args.out / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (args.out / "per_episode.json").write_text(json.dumps(per_episode, indent=2) + "\n", encoding="utf-8")
    (args.out / "action_inventory.json").write_text(json.dumps(train_meta["action_inventory"], indent=2) + "\n", encoding="utf-8")
    (args.out / "split_manifest.json").write_text(json.dumps({
        "train": [{"episode_id": r.episode_id, "path": r.path.name, "seat": r.seat, "create_time": r.create_time} for r in train_refs],
        "holdout": [{"episode_id": r.episode_id, "path": r.path.name, "seat": r.seat, "create_time": r.create_time} for r in holdout_refs],
    }, indent=2) + "\n", encoding="utf-8")
    write_report(summary, args.out)
    print(json.dumps({"decision": decision, "candidate": evaluation["candidate"], "baseline": evaluation["baseline"], "delta": evaluation["composite_delta"], "checks": checks}, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
