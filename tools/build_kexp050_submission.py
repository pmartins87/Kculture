"""Build a deterministic self-contained Kaggriculture package for frozen KEXP-050.

This builder is preparation only. A package produced by it is not authorized for
hosted submission unless KEXP-054 fresh validation passes and package parity is
then checked.

Composition:
1. hash-pinned COK V8 upstream main.py;
2. exact R4B terminal-market overlay semantics;
3. exact KEXP-050 state-614 WHEAT->CARROT reallocation overlay semantics.
"""
from __future__ import annotations

import gzip
import hashlib
import json
import shutil
import tarfile
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts/public_opponents/cok_v8_779caae.py"
EXPECTED_BASE_SHA256 = "faf57412e2c56dcc669043865a185324bab9952d865abccc2203284e854eceb3"
UPSTREAM_COMMIT = "779caaec88a441345871e2d62eb5de93606b7b52"
FROZEN_R4B_BLOB = "e564125f0c4a1711fd3ea065dc1cb27d4a62ce37"
FROZEN_KEXP050_BLOB = "61b77be136836328917441cb03f89bc6665c4c27"
LICENSE_URL = f"https://raw.githubusercontent.com/COK-ZhangZiliang/Kaggriculture/{UPSTREAM_COMMIT}/LICENSES/Apache-2.0.txt"
NOTICES_URL = f"https://raw.githubusercontent.com/COK-ZhangZiliang/Kaggriculture/{UPSTREAM_COMMIT}/THIRD_PARTY_NOTICES.md"
OUT_DIR = ROOT / "artifacts" / "submissions" / "kexp050_reallocate614_v1"
ARCHIVE = ROOT / "artifacts" / "submissions" / "kexp050_reallocate614_v1.tar.gz"

# Exact semantics of candidates/r4b_ablation_market_only.py, made self-contained
# by wrapping the upstream COK `agent` already defined above it.
R4B_OVERLAY = r'''

# ---------------------------------------------------------------------------
# Kculture R4B terminal market-only overlay.
# ---------------------------------------------------------------------------
import copy as _kculture_copy

_kculture_base_agent = agent
_KCULTURE_TERMINAL_STEP = 718
_KCULTURE_SELLABLE = (
    "WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON",
    "EGG", "MILK", "WOOL", "FERTILIZER",
)


def _kculture_get(obj, key, default=None):
    try:
        return obj.get(key, default)
    except AttributeError:
        try:
            return obj[key]
        except (KeyError, TypeError):
            return default


def _kculture_terminal_market_only(obs, base_action):
    action = _kculture_copy.deepcopy(base_action)
    projected = _v5_projected_shed(obs, action)
    prices = _kculture_get(_kculture_get(obs, "market", {}) or {}, "prices", {}) or {}
    existing_order = []
    seen = set()
    for order in list(action.get("market") or []):
        if not (isinstance(order, list) and len(order) >= 2 and order[0] == "SELL"):
            continue
        item = order[1]
        if item in _KCULTURE_SELLABLE and item not in seen:
            seen.add(item)
            existing_order.append(item)
    market = []
    for item in existing_order:
        try:
            quantity = max(0, int(projected.get(item, 0) or 0))
        except (TypeError, ValueError):
            quantity = 0
        if quantity:
            market.append(["SELL", item, quantity])
    omitted = []
    for item in _KCULTURE_SELLABLE:
        if item in seen:
            continue
        try:
            quantity = max(0, int(projected.get(item, 0) or 0))
            price = max(0.0, float(_kculture_get(prices, item, 0) or 0))
        except (TypeError, ValueError):
            continue
        if quantity:
            omitted.append((price * quantity, item, quantity))
    omitted.sort(reverse=True)
    market.extend(["SELL", item, quantity] for _, item, quantity in omitted)
    action["market"] = market[:10]
    return action


def agent(obs, config=None):
    action = _kculture_base_agent(obs, config)
    try:
        step = max(0, int(_kculture_get(obs, "step", 0) or 0))
    except (TypeError, ValueError):
        return action
    if step != _KCULTURE_TERMINAL_STEP:
        return action
    return _kculture_terminal_market_only(obs, action)
'''

# Exact deployable semantics of candidates/r4d_reallocate_614_carrot.py, with
# the self-contained R4B `agent` above as the frozen parent.
KEXP050_OVERLAY = r'''

# ---------------------------------------------------------------------------
# Kculture KEXP-050 same-slot WHEAT -> CARROT reallocation overlay.
# ---------------------------------------------------------------------------
import copy as _kc50_copy

_kc50_r4b_agent = agent
_KC50_BUY_STEP = 614
_KC50_PLANT_STEP = 615
_KC50_Q = 3.0
_KC50_STATE = {}


def _kc50_get(obj, key, default=None):
    try:
        return obj.get(key, default)
    except AttributeError:
        try:
            return obj[key]
        except Exception:
            return default


def _kc50_step(obs):
    try:
        return int(_kc50_get(obs, "step", 0) or 0)
    except Exception:
        return 0


def _kc50_player(obs):
    try:
        return int(_kc50_get(obs, "player", 0) or 0)
    except Exception:
        return 0


def _kc50_seeds(obs):
    return _kc50_get(_kc50_get(obs, "private", {}) or {}, "seeds", {}) or {}


def _kc50_price(obs, item):
    try:
        prices = _kc50_get(_kc50_get(obs, "market", {}) or {}, "prices", {}) or {}
        v = float(_kc50_get(prices, item, 0) or 0)
        return v if v > 0 else None
    except Exception:
        return None


def _kc50_unit_ops(action):
    yield action.get("farmer")
    for op in list(action.get("hands") or []):
        yield op


def _kc50_count_carrot_plants(action):
    return sum(
        isinstance(op, list) and len(op) >= 2 and op[:2] == ["PLANT", "CARROT"]
        for op in _kc50_unit_ops(action)
    )


def _kc50_count_carrot_buys(action):
    total = 0
    for row in list(action.get("market") or []):
        if isinstance(row, list) and len(row) >= 3 and row[:2] == ["BUY_SEED", "CARROT"]:
            try:
                total += max(0, int(row[2] or 0))
            except Exception:
                pass
    return total


def _kc50_reallocate_one_wheat_buy(action):
    market = [list(row) if isinstance(row, list) else row for row in list(action.get("market") or [])]
    for i, row in enumerate(market):
        if not (isinstance(row, list) and len(row) >= 3 and row[:2] == ["BUY_SEED", "WHEAT"]):
            continue
        try:
            qty = max(0, int(row[2] or 0))
        except Exception:
            continue
        if qty != 1:
            continue
        market[i] = ["BUY_SEED", "CARROT", 1]
        action["market"] = market
        return True
    return False


def _kc50_replace_one_wheat_plant(action):
    op = action.get("farmer")
    if isinstance(op, list) and len(op) >= 2 and op[:2] == ["PLANT", "WHEAT"]:
        action["farmer"] = ["PLANT", "CARROT"]
        return True
    hands = list(action.get("hands") or [])
    for i, op in enumerate(hands):
        if isinstance(op, list) and len(op) >= 2 and op[:2] == ["PLANT", "WHEAT"]:
            hands[i] = ["PLANT", "CARROT"]
            action["hands"] = hands
            return True
    return False


def agent(obs, config=None):
    base = _kc50_r4b_agent(obs, config)
    action = _kc50_copy.deepcopy(base)
    step = _kc50_step(obs)
    pid = _kc50_player(obs)
    st = _KC50_STATE.get(pid)
    if st is None or step == 0 or step <= int(st.get("last_step", -1)):
        st = {"last_step": step, "pending": False, "expected_carrot": None}
        _KC50_STATE[pid] = st
    st["last_step"] = step

    if step == _KC50_BUY_STEP:
        pw, pc = _kc50_price(obs, "WHEAT"), _kc50_price(obs, "CARROT")
        margin = None if pw is None or pc is None else _KC50_Q * (pc - pw) - 10.0
        if margin is not None and margin > 0:
            try:
                carrot_before = max(0, int(_kc50_get(_kc50_seeds(obs), "CARROT", 0) or 0))
            except Exception:
                carrot_before = 0
            expected = max(0, carrot_before - _kc50_count_carrot_plants(base)) + _kc50_count_carrot_buys(base)
            if _kc50_reallocate_one_wheat_buy(action):
                st["pending"] = True
                st["expected_carrot"] = expected
                return action
        st["pending"] = False
        st["expected_carrot"] = None
        return action

    if step == _KC50_PLANT_STEP and st.get("pending"):
        try:
            actual = max(0, int(_kc50_get(_kc50_seeds(obs), "CARROT", 0) or 0))
            expected = max(0, int(st.get("expected_carrot", 0) or 0))
        except Exception:
            actual = expected = 0
        if actual > expected:
            _kc50_replace_one_wheat_plant(action)
        st["pending"] = False
        st["expected_carrot"] = None
        return action

    if step > _KC50_PLANT_STEP:
        st["pending"] = False
        st["expected_carrot"] = None
    return action
'''


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def download(url: str) -> bytes:
    with urllib.request.urlopen(url, timeout=30) as response:
        return response.read()


def deterministic_tar_gz(output: Path, files: list[Path]) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("wb") as raw:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as gz:
            with tarfile.open(fileobj=gz, mode="w", format=tarfile.PAX_FORMAT) as tar:
                for path in sorted(files, key=lambda p: p.name):
                    info = tar.gettarinfo(str(path), arcname=path.name)
                    info.uid = 0
                    info.gid = 0
                    info.uname = ""
                    info.gname = ""
                    info.mtime = 0
                    info.mode = 0o644
                    with path.open("rb") as fh:
                        tar.addfile(info, fh)


def main() -> None:
    base_bytes = BASE.read_bytes()
    base_sha = sha256_bytes(base_bytes)
    if base_sha != EXPECTED_BASE_SHA256:
        raise SystemExit(f"Frozen COK V8 hash mismatch: {base_sha}")

    if OUT_DIR.exists():
        shutil.rmtree(OUT_DIR)
    OUT_DIR.mkdir(parents=True)

    main_py = OUT_DIR / "main.py"
    main_py.write_bytes(base_bytes + R4B_OVERLAY.encode("utf-8") + KEXP050_OVERLAY.encode("utf-8"))

    (OUT_DIR / "LICENSE-APACHE-2.0.txt").write_bytes(download(LICENSE_URL))
    upstream_notices = download(NOTICES_URL).decode("utf-8")
    notice = (
        "Kculture KEXP-050 reallocate614 v1\n"
        "Derived from COK-ZhangZiliang/Kaggriculture COK V8 under Apache-2.0.\n"
        f"Upstream commit: {UPSTREAM_COMMIT}\n"
        f"Upstream main.py SHA-256: {EXPECTED_BASE_SHA256}\n"
        f"Frozen R4B blob: {FROZEN_R4B_BLOB}\n"
        f"Frozen KEXP-050 blob: {FROZEN_KEXP050_BLOB}\n"
        "Kculture changes: R4B final-step liquidation plus KEXP-050 one-for-one state-614 WHEAT->CARROT seed reallocation with observed-stock handshake at state 615.\n\n"
        "----- Upstream THIRD_PARTY_NOTICES.md -----\n\n"
        + upstream_notices
    )
    (OUT_DIR / "THIRD_PARTY_NOTICES.txt").write_text(notice, encoding="utf-8")

    package_files = [OUT_DIR / "main.py", OUT_DIR / "LICENSE-APACHE-2.0.txt", OUT_DIR / "THIRD_PARTY_NOTICES.txt"]
    deterministic_tar_gz(ARCHIVE, package_files)

    manifest = {
        "candidate": "KEXP-050-reallocate614-validation-v1",
        "frozen_candidate_blob": FROZEN_KEXP050_BLOB,
        "frozen_r4b_blob": FROZEN_R4B_BLOB,
        "base_sha256": base_sha,
        "upstream_commit": UPSTREAM_COMMIT,
        "files": {p.name: sha256_bytes(p.read_bytes()) for p in package_files},
        "archive": str(ARCHIVE.relative_to(ROOT)),
        "archive_sha256": sha256_bytes(ARCHIVE.read_bytes()),
        "archive_bytes": ARCHIVE.stat().st_size,
        "authorization": "BUILD_PREP_ONLY_UNTIL_KEXP054_PASS",
    }
    (OUT_DIR / "BUILD_MANIFEST.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
