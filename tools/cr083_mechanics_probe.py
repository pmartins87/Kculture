"""CR083 Phase-0 mechanics probe for exact kaggle-environments==1.32.7.

No strategy score, teacher imitation or validation seed is used here. The purpose is
only to establish the official action/observation grammar and whether exact current-
state branching can be reproduced safely for future explicit-value research.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import inspect
import json
from pathlib import Path

PASS = {"farmer": ["PASS"], "hands": [], "market": []}


def plain(x):
    try:
        return json.loads(json.dumps(x))
    except Exception:
        if hasattr(x, "toJSON"):
            return json.loads(x.toJSON())
        return repr(x)


def state_digest(env) -> str:
    payload = json.dumps(plain(env.state), sort_keys=True, separators=(",", ":"), default=str).encode()
    return hashlib.sha256(payload).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--source-dir", type=Path, required=True)
    a = ap.parse_args()

    from importlib.metadata import version
    from kaggle_environments import make

    installed = version("kaggle-environments")
    if installed != "1.32.7":
        raise RuntimeError(f"expected 1.32.7, got {installed}")

    env = make("kaggriculture", configuration={"episodeSteps": 720, "seed": 123456789}, debug=False)
    env.reset(2)

    report = {
        "schema_version": "cr083-mechanics-probe-v1",
        "kaggle_environments_version": installed,
        "environment_name": getattr(env, "name", "kaggriculture"),
        "configuration": plain(env.configuration),
        "specification": plain(getattr(env, "specification", None)),
        "initial_state_digest": state_digest(env),
        "deepcopy_supported": False,
        "same_action_branch_deterministic": False,
        "divergent_branch_original_unchanged": False,
        "interpreter_source_available": False,
        "package_source_path": None,
        "errors": [],
    }

    # Capture exact interpreter source used by Environment when inspectable.
    try:
        interp = getattr(env, "interpreter")
        src = inspect.getsource(interp)
        a.output.parent.mkdir(parents=True, exist_ok=True)
        (a.output.parent / "interpreter_source.py").write_text(src, encoding="utf-8")
        report["interpreter_source_available"] = True
        report["interpreter_module"] = getattr(interp, "__module__", None)
        report["interpreter_qualname"] = getattr(interp, "__qualname__", None)
    except Exception as exc:
        report["errors"].append(f"interpreter_source:{type(exc).__name__}:{exc}")

    # Snapshot the installed Kaggriculture environment package source for a separate
    # human/code audit. This is provenance only, not runtime strategy input.
    try:
        spec = importlib.util.find_spec("kaggle_environments.envs.kaggriculture")
        roots = list(spec.submodule_search_locations or []) if spec else []
        if roots:
            root = Path(roots[0]).resolve()
            report["package_source_path"] = str(root)
            a.source_dir.mkdir(parents=True, exist_ok=True)
            manifest = []
            for p in sorted(root.rglob("*")):
                if not p.is_file() or "__pycache__" in p.parts:
                    continue
                rel = p.relative_to(root)
                data = p.read_bytes()
                manifest.append({"path": str(rel), "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()})
                dst = a.source_dir / rel
                dst.parent.mkdir(parents=True, exist_ok=True)
                dst.write_bytes(data)
            report["package_source_files"] = manifest
    except Exception as exc:
        report["errors"].append(f"package_snapshot:{type(exc).__name__}:{exc}")

    # Test exact branching without looking at any competition replay or validation
    # result. First advance a few no-op turns to avoid testing only reset state.
    try:
        for _ in range(7):
            env.step([PASS, PASS])
        before = state_digest(env)
        branch = copy.deepcopy(env)
        report["deepcopy_supported"] = True
        report["prebranch_state_digest"] = before
        report["clone_initial_digest"] = state_digest(branch)
        report["clone_initial_equal"] = before == state_digest(branch)

        env.step([PASS, PASS])
        branch.step([PASS, PASS])
        same_a = state_digest(env)
        same_b = state_digest(branch)
        report["same_action_branch_digest_original"] = same_a
        report["same_action_branch_digest_clone"] = same_b
        report["same_action_branch_deterministic"] = same_a == same_b

        # Now branch again and deliberately make only the clone attempt a benign
        # legal-looking market no-op alternative; regardless of whether the order is
        # accepted/effective, mutating the clone must not mutate its source env.
        source = copy.deepcopy(env)
        source_before = state_digest(source)
        alt = copy.deepcopy(source)
        alt.step([{"farmer":["PASS"],"hands":[],"market":[["SELL","WHEAT",1]]}, PASS])
        report["divergent_branch_original_unchanged"] = state_digest(source) == source_before
        report["divergent_branch_clone_digest"] = state_digest(alt)
        report["divergent_branch_source_digest"] = state_digest(source)
        report["divergent_branch_changed_state"] = state_digest(alt) != state_digest(source)
    except Exception as exc:
        report["errors"].append(f"branching:{type(exc).__name__}:{exc}")

    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
