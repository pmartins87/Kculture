"""Build the deterministic self-contained CR024A guarded-top19 package.

Preparation only: creation of this builder does not authorize hosted submission.
The package is built only after the preregistered CR024A Stage-B gate passes.
The public top19 replay is used transiently at build time to extract its 719
public actions; no replay download or network access is required at runtime.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import shutil
import sys
import tempfile
from pathlib import Path

from kaggle.api.kaggle_api_extended import KaggleApi

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools import build_cr008_cr011_calibration_packages as P
from tools import build_kexp050_submission as B

CFG = ROOT / "configs/cr023_public_tape_preregistered_seeds_v1.json"
MODEL_PATH = ROOT / "models/cr007_pure_models.json"
OUT = ROOT / "artifacts/submissions/cr024a_guarded_top19_v1"
ARCHIVE_NAME = "R4D_CR024A_TOP19_WOOL_GUARD_HYBRID_V1.tar.gz"
CR008_BLOB = "8e1c26202c3101c19668bf61edf2ae51d4329d5d"
STAGE_B_SHARD_BLOB = "940ffa6e4332b09d21e0dab7e5995a7222cee110"
STAGE_B_AGG_BLOB = "4e850984a1b7f2b77984bb2620321a714c4750a5"
GUARD_CLOCK = 192
GUARD_FEATURE = "dmarket_price_wool"
GUARD_THRESHOLD = 11.5


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _clock(frame):
    try:
        raw = frame.get("step")
        if raw is not None:
            return max(0, int(raw))
    except Exception:
        pass
    try:
        return max(0, int(frame.get("day") or 0)) * 24 + max(0, int(frame.get("hour") or 0))
    except Exception:
        return 0


def extract_top19_tape() -> tuple[list[dict], dict]:
    cfg = json.loads(CFG.read_text(encoding="utf-8"))
    meta = cfg["routes"]["top19_openloop"]
    episode_id = int(meta["episode_id"])
    source_seat = int(meta["source_seat"])
    api = KaggleApi(); api.authenticate()
    with tempfile.TemporaryDirectory(prefix="cr024a-build-") as td:
        api.competition_episode_replay(episode_id, path=td, quiet=True)
        p = Path(td) / f"episode-{episode_id}-replay.json"
        replay = json.loads(p.read_text(encoding="utf-8"))
        steps = replay.get("steps") or []
        if len(steps) < 720:
            raise RuntimeError(f"short top19 replay: {len(steps)}")
        tape = []
        for t in range(719):
            frame = steps[t + 1][source_seat]
            action = frame.get("action") if isinstance(frame, dict) else None
            tape.append(copy.deepcopy(action or {}))
    if len(tape) != 719:
        raise RuntimeError("top19 tape length mismatch")
    tape_json = json.dumps(tape, separators=(",", ":"), sort_keys=True)
    provenance = {
        "episode_id": episode_id,
        "source_seat": source_seat,
        "action_count": len(tape),
        "canonical_tape_sha256": sha(tape_json.encode("utf-8")),
    }
    return tape, provenance


HYBRID_TEMPLATE = r'''

# ---------------------------------------------------------------------------
# Kculture CR024A: public top19 backbone + one frozen WOOL-regime guard.
# ---------------------------------------------------------------------------
_CR024_TAPE = _ka_json.loads(__TAPE_JSON_LITERAL__)
_CR024_GUARD_CLOCK = 192
_CR024_GUARD_FEATURE = "dmarket_price_wool"
_CR024_GUARD_THRESHOLD = 11.5
_CR024_STATE = {0:{"last":-1,"switched":False,"guard_value":None},1:{"last":-1,"switched":False,"guard_value":None}}


def _cr024_state(player, step):
    st = _CR024_STATE.setdefault(player,{"last":-1,"switched":False,"guard_value":None})
    if step == 0 or step < int(st.get("last",-1)):
        st.clear(); st.update({"last":-1,"switched":False,"guard_value":None})
    st["last"] = step
    return st


def agent(obs, config=None):
    player = int(_ka_get(obs,"player",0) or 0)
    step = _ka_clock_step(obs)
    st = _cr024_state(player,step)
    _ka_reset(player,step)

    if step == _CR024_GUARD_CLOCK and not st["switched"]:
        prev = _KA_HISTORY[player].get(step-24)
        if prev is not None:
            feat = _ka_public_features(obs,prev,player)
            value = float(feat.get(_CR024_GUARD_FEATURE,0.0)) if feat else 0.0
            st["guard_value"] = value
            if value >= _CR024_GUARD_THRESHOLD:
                st["switched"] = True

    if st["switched"]:
        action = _ka_base_agent(obs,config)
        action = _ka_apply(obs,action,player,step)
    else:
        action = _ka_copy.deepcopy(_CR024_TAPE[max(0,min(718,step))])

    _ka_remember(player,step,obs)
    return action

# Fresh final callable so kaggle-environments selects the intended wrapper.
_cr024_hosted_entrypoint = agent
'''


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage-b-decision", default="CR024A_STAGE_B_PASS__BUILD_NEW_STRATEGY_PACKAGE")
    args = ap.parse_args()
    if args.stage_b_decision != "CR024A_STAGE_B_PASS__BUILD_NEW_STRATEGY_PACKAGE":
        raise SystemExit("CR024A package build not authorized by Stage-B decision")

    base_bytes = B.BASE.read_bytes()
    if sha(base_bytes) != B.EXPECTED_BASE_SHA256:
        raise SystemExit("COK base hash mismatch")
    model_text = MODEL_PATH.read_text(encoding="utf-8")
    tape, provenance = extract_top19_tape()
    tape_json = json.dumps(tape, separators=(",", ":"), sort_keys=True)

    if OUT.exists():
        shutil.rmtree(OUT)
    package_dir = OUT / "package"
    package_dir.mkdir(parents=True)

    # P.ADAPTIVE_TEMPLATE gives exact frozen CR008 utilities and semantics over
    # the exact R4B parent.  CR024A then chooses between the public tape and
    # those exact utilities while keeping their 24-turn public history warm.
    adaptive = (
        P.ADAPTIVE_TEMPLATE
        .replace("__MODE__", "CR024A_INTERNAL_CR008")
        .replace("__MODEL_JSON__", repr(model_text))
        .replace("__EARLY__", "False")
    )
    hybrid = HYBRID_TEMPLATE.replace("__TAPE_JSON_LITERAL__", repr(tape_json))
    main_py = package_dir / "main.py"
    main_py.write_bytes(base_bytes + B.R4B_OVERLAY.encode("utf-8") + adaptive.encode("utf-8") + hybrid.encode("utf-8"))

    (package_dir / "LICENSE-APACHE-2.0.txt").write_bytes(B.download(B.LICENSE_URL))
    notice = (
        "Kculture CR024A guarded top19 hybrid v1\n"
        "Derived from COK V8 under Apache-2.0.\n"
        f"Upstream commit: {B.UPSTREAM_COMMIT}\n"
        f"R4B blob: {B.FROZEN_R4B_BLOB}\n"
        f"CR008 blob: {CR008_BLOB}\n"
        f"CR024A Stage-B shard blob: {STAGE_B_SHARD_BLOB}\n"
        f"CR024A Stage-B aggregate blob: {STAGE_B_AGG_BLOB}\n"
        f"Top19 public episode: {provenance['episode_id']} seat {provenance['source_seat']}\n"
        f"Top19 canonical action-tape SHA-256: {provenance['canonical_tape_sha256']}\n"
        "Runtime strategy: execute frozen top19 public action tape; at clock 192, if public WOOL price change from clock 168 is >=11.5, switch permanently to frozen CR008 semantics.\n\n"
        "----- Upstream notices -----\n"
        + B.download(B.NOTICES_URL).decode("utf-8")
    )
    (package_dir / "THIRD_PARTY_NOTICES.txt").write_text(notice, encoding="utf-8")

    archive = OUT / ARCHIVE_NAME
    B.deterministic_tar_gz(archive, [main_py, package_dir / "LICENSE-APACHE-2.0.txt", package_dir / "THIRD_PARTY_NOTICES.txt"])
    manifest = {
        "schema_version": "cr024a-package-v1",
        "authorization": args.stage_b_decision,
        "strategy_materially_new": True,
        "guard": {"clock": GUARD_CLOCK, "feature": GUARD_FEATURE, "direction": "ge", "threshold": GUARD_THRESHOLD},
        "top19_provenance": provenance,
        "cr008_blob": CR008_BLOB,
        "r4b_blob": B.FROZEN_R4B_BLOB,
        "archive": str(archive.relative_to(ROOT)),
        "archive_sha256": sha(archive.read_bytes()),
        "archive_bytes": archive.stat().st_size,
        "main_sha256": sha(main_py.read_bytes()),
        "runtime_network_required": False,
    }
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
