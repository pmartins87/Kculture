"""Build a deterministic, self-contained Kaggriculture submission for the frozen market-only candidate.

The laboratory candidate imports the hash-pinned COK V8 artifact from
artifacts/public_opponents. Kaggle requires main.py at archive root, so this
builder embeds that exact verified source and appends only the Kculture
market-only terminal overlay.
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
LICENSE_URL = f"https://raw.githubusercontent.com/COK-ZhangZiliang/Kaggriculture/{UPSTREAM_COMMIT}/LICENSES/Apache-2.0.txt"
NOTICES_URL = f"https://raw.githubusercontent.com/COK-ZhangZiliang/Kaggriculture/{UPSTREAM_COMMIT}/THIRD_PARTY_NOTICES.md"
OUT_DIR = ROOT / "artifacts" / "submissions" / "r4b_market_only_v1"
ARCHIVE = ROOT / "artifacts" / "submissions" / "r4b_market_only_v1.tar.gz"

OVERLAY = r'''

# ---------------------------------------------------------------------------
# Kculture R4B market-only terminal overlay.
# Kculture modification: preserve all upstream physical actions; on executable
# step 718, sell the complete same-turn projected shed inventory.
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
    main_py.write_bytes(base_bytes + OVERLAY.encode("utf-8"))

    license_bytes = download(LICENSE_URL)
    (OUT_DIR / "LICENSE-APACHE-2.0.txt").write_bytes(license_bytes)

    upstream_notices = download(NOTICES_URL).decode("utf-8")
    notice = (
        "Kculture R4B market-only v1\n"
        "Derived from COK-ZhangZiliang/Kaggriculture COK V8 under Apache-2.0.\n"
        f"Upstream commit: {UPSTREAM_COMMIT}\n"
        f"Upstream main.py SHA-256: {EXPECTED_BASE_SHA256}\n"
        "Kculture change: final-step market liquidation only; all upstream physical actions are preserved.\n\n"
        "----- Upstream THIRD_PARTY_NOTICES.md -----\n\n"
        + upstream_notices
    )
    (OUT_DIR / "THIRD_PARTY_NOTICES.txt").write_text(notice, encoding="utf-8")

    package_files = [
        OUT_DIR / "main.py",
        OUT_DIR / "LICENSE-APACHE-2.0.txt",
        OUT_DIR / "THIRD_PARTY_NOTICES.txt",
    ]
    deterministic_tar_gz(ARCHIVE, package_files)

    manifest = {
        "candidate": "R4B-market-only-validation-v1",
        "base_sha256": base_sha,
        "upstream_commit": UPSTREAM_COMMIT,
        "files": {p.name: sha256_bytes(p.read_bytes()) for p in package_files},
        "archive": str(ARCHIVE.relative_to(ROOT)),
        "archive_sha256": sha256_bytes(ARCHIVE.read_bytes()),
        "archive_bytes": ARCHIVE.stat().st_size,
    }
    manifest_path = OUT_DIR / "BUILD_MANIFEST.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
