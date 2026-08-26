"""R4C candidate: frozen COK V8 with only the guarded ninth-cow switch enabled.

This wrapper intentionally changes a single dormant upstream feature flag.
The base artifact must first be fetched and hash-verified by
`tools/fetch_public_opponents.py`.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "artifacts" / "public_opponents" / "cok_v8_779caae.py"


def _load_base_module():
    if not BASE.is_file():
        raise FileNotFoundError(
            f"Missing frozen base {BASE}. Run tools/fetch_public_opponents.py first."
        )
    spec = importlib.util.spec_from_file_location("kculture_r4c_cok_base", BASE)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load frozen base: {BASE}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if not hasattr(module, "_ENABLE_NINTH_COW"):
        raise RuntimeError("Frozen COK base no longer exposes _ENABLE_NINTH_COW")
    if module._ENABLE_NINTH_COW is not False:
        raise RuntimeError("Frozen COK base ninth-cow flag was expected to be False")
    module._ENABLE_NINTH_COW = True
    return module


_BASE = _load_base_module()


def agent(obs, config):
    return _BASE.agent(obs, config)
