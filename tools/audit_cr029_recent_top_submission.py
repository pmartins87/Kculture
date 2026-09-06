"""Mechanical and identity audit for CR029 FULL_RECENT_TOP_V1 archive."""
from __future__ import annotations

import argparse
import ast
import hashlib
import importlib.util
import json
import py_compile
import tarfile
import tempfile
import time
from pathlib import Path, PurePosixPath

EXPECTED_MEMBERS = {"main.py", "LICENSE-APACHE-2.0.txt", "THIRD_PARTY_NOTICES.txt"}
REQUIRED = ("_CR029_RECENT_TOP_TAPE =", "_cr029_full_recent_top_hosted_entrypoint = agent")
FORBIDDEN_TEXT = (
    "competition_episode_replay(", "notebook_output_download(", "requests.get(",
    "requests.post(", "urllib.request.urlopen(", "httpx.", "socket.", "subprocess.",
)
EXPECTED_TAPE_SHA256 = "6c56840b9510e0688da2fbec47e8f89583c63a0124fa4c8801fa5d93c197226b"


def safe(name: str) -> bool:
    p = PurePosixPath(name.replace("\\", "/"))
    return not p.is_absolute() and ".." not in p.parts


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_module(path: Path):
    spec = importlib.util.spec_from_file_location(f"cr029_pkg_{time.time_ns()}", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def tape_sha(actions: list[dict]) -> str:
    body = json.dumps(actions, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(body).hexdigest()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--archive", required=True)
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    archive = Path(args.archive)
    manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    errors: list[str] = []

    if manifest.get("candidate") != "full_recent_top":
        errors.append("manifest candidate mismatch")
    if manifest.get("policy_modified") is not False:
        errors.append("policy_modified must be false")
    if manifest.get("tape_sha256") != EXPECTED_TAPE_SHA256:
        errors.append("manifest tape SHA mismatch")
    if manifest.get("runtime_network_required") is not False:
        errors.append("runtime network must be false")
    if manifest.get("runtime_identity_features") is not False:
        errors.append("runtime identity features must be false")
    if manifest.get("held_out_touched") is not False:
        errors.append("held-out must remain untouched")
    if sha(archive.read_bytes()) != manifest.get("archive_sha256"):
        errors.append("archive SHA does not match manifest")

    with tarfile.open(archive, "r:gz") as tf:
        members = tf.getmembers()
        names = {m.name for m in members if m.isfile()}
        if names != EXPECTED_MEMBERS:
            errors.append(f"member set mismatch: {sorted(names)}")
        for m in members:
            if not safe(m.name):
                errors.append(f"unsafe member: {m.name}")
            if not m.isfile():
                errors.append(f"non-file member: {m.name}")
        info = next((m for m in members if m.name == "main.py"), None)
        fh = tf.extractfile(info) if info is not None else None
        main_bytes = fh.read() if fh else b""

    text = main_bytes.decode("utf-8") if main_bytes else ""
    for token in REQUIRED:
        if token not in text:
            errors.append(f"missing required token: {token}")
    for token in FORBIDDEN_TEXT:
        if token in text:
            errors.append(f"forbidden runtime capability token: {token}")

    try:
        tree = ast.parse(text)
        imports = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports |= {a.name.split(".")[0] for a in node.names}
            elif isinstance(node, ast.ImportFrom) and node.module:
                imports.add(node.module.split(".")[0])
        if imports - {"copy", "json"}:
            errors.append(f"unexpected imports: {sorted(imports - {'copy', 'json'})}")
    except Exception as exc:
        errors.append(f"AST parse failed: {exc!r}")

    with tempfile.TemporaryDirectory(prefix="cr029-package-audit-") as td:
        p = Path(td) / "main.py"
        p.write_bytes(main_bytes)
        try:
            py_compile.compile(str(p), doraise=True)
            mod = load_module(p)
            embedded = getattr(mod, "_CR029_RECENT_TOP_TAPE", None)
            if not isinstance(embedded, list) or len(embedded) != 719:
                errors.append(f"embedded tape length invalid: {None if embedded is None else len(embedded)}")
            elif tape_sha(embedded) != EXPECTED_TAPE_SHA256:
                errors.append("embedded tape SHA mismatch")
            else:
                # Exhaustive step-clock and day/hour clock action identity.
                for step in range(719):
                    expected = embedded[step]
                    if mod.agent({"step": step}, None) != expected:
                        errors.append(f"step-clock mismatch at {step}")
                        break
                    if mod.agent({"day": step // 24, "hour": step % 24}, None) != expected:
                        errors.append(f"day/hour-clock mismatch at {step}")
                        break
        except Exception as exc:
            errors.append(f"compile/runtime audit failed: {exc!r}")

    report = {
        "experiment": "CR029_FULL_RECENT_TOP_V1_PACKAGE_AUDIT",
        "archive": str(archive),
        "archive_sha256": sha(archive.read_bytes()),
        "archive_bytes": archive.stat().st_size,
        "main_sha256": sha(main_bytes),
        "main_bytes": len(main_bytes),
        "expected_tape_sha256": EXPECTED_TAPE_SHA256,
        "exhaustive_clock_states_checked": 719,
        "runtime_network_required": False,
        "runtime_identity_features": False,
        "held_out_touched": False,
        "error_count": len(errors),
        "errors": errors,
        "decision": "PASS" if not errors else "FAIL",
    }
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    if errors:
        raise SystemExit(3)


if __name__ == "__main__":
    main()
