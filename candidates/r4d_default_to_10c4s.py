"""R4D-A: reroute only the fully observed COK V8 default 8C/6S regime to 10C/4S.

Development-only counterfactual over the validated R4B market-only wrapper.
The first three public shops must already be visible before the override can
activate. All other COK V8 route decisions and controllers remain untouched.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WRAPPER_PATH = ROOT / "candidates/r4b_ablation_market_only.py"
TARGET_ROUTE = "10c4s_3q"


def _load_wrapper():
    spec = importlib.util.spec_from_file_location(
        "kculture_r4d_default_to_10c4s_wrapper", WRAPPER_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load validated R4B wrapper: {WRAPPER_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_WRAP = _load_wrapper()
_ORIGINAL_V7_ROUTE_LABEL = _WRAP._BASE._v7_route_label


def _get(obj, key, default=None):
    try:
        return obj.get(key, default)
    except AttributeError:
        try:
            return obj[key]
        except (KeyError, TypeError):
            return default


def _r4d_v7_route_label(obs):
    label = _ORIGINAL_V7_ROUTE_LABEL(obs)
    shops = list(
        _get(_get(obs, "town", {}) or {}, "unlocked_shops", []) or []
    )
    # COK's provisional selector also returns 8C/6S before the full first-three
    # shop context exists. Do not alter that shared opening. Once three shops
    # are visible, original 8C/6S means the final default no-Yarn/no-milk regime.
    if len(shops) >= 3 and label == "8c6s_3q":
        return TARGET_ROUTE
    return label


_WRAP._BASE._v7_route_label = _r4d_v7_route_label


def agent(obs, config=None):
    return _WRAP.agent(obs, config)
