from __future__ import annotations

"""Utilities for loading the seven frozen public replay-tape opponents used by CR089.

The source pack is a local artifact produced earlier in this project.  This module only
extracts the literal public action tapes from each rXX package and converts them into the
same dense action schema consumed by the exact C++ simulator.  No identity, hidden seed,
future state, or opponent-private state is used at runtime.
"""

from pathlib import Path
import ast
import io
import json
import tarfile
import zipfile

import numpy as np

MAX_UNITS = 40
RAW_ORDER_SLOTS = 16
ACTION_WIDTH = 1 + MAX_UNITS * 3 + 1 + RAW_ORDER_SLOTS * 3

ITEM = {
    "WHEAT": 0, "CARROT": 1, "TOMATO": 2, "STRAWBERRY": 3, "MELON": 4,
    "EGG": 5, "MILK": 6, "WOOL": 7, "FERTILIZER": 8,
    "GOOSE": 9, "COW": 10, "SHEEP": 11,
}
UNIT_OP = {
    "PASS": 0, "NORTH": 1, "SOUTH": 2, "EAST": 3, "WEST": 4,
    "PICKUP": 5, "DROP": 6, "PLACE": 7, "PLANT": 8, "WATER": 9,
    "HARVEST": 10, "FERTILIZE": 11, "DIG": 12, "BUILD_COOP": 13,
    "BUILD_PASTURE": 14, "FEED": 15, "COLLECT_FERTILIZER": 16, "CARE": 17,
}
MARKET_OP = {
    "HIRE": 1, "BUY_LAND": 2, "BUY_SEED": 3, "BUY_PRODUCT": 4,
    "BUY_ANIMAL": 5, "SELL": 6,
}


def _extract_literal_tape(source: str):
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        if not any(isinstance(t, ast.Name) and t.id == "_TAPE" for t in node.targets):
            continue
        call = node.value
        if (
            isinstance(call, ast.Call)
            and isinstance(call.func, ast.Attribute)
            and call.func.attr == "loads"
            and call.args
        ):
            raw = ast.literal_eval(call.args[0])
            tape = json.loads(raw)
            if not isinstance(tape, list):
                raise ValueError("_TAPE did not decode to a list")
            return tape
    raise ValueError("literal _TAPE = json.loads(...) not found")


def _encode_unit(row: np.ndarray, slot: int, action) -> None:
    if slot >= MAX_UNITS:
        return
    if not action:
        action = ["PASS"]
    op = str(action[0])
    if op not in UNIT_OP:
        raise ValueError(f"unknown unit op: {op}")
    off = 1 + slot * 3
    row[off] = UNIT_OP[op]
    row[off + 1] = ITEM.get(str(action[1]), -1) if len(action) >= 2 else -1
    row[off + 2] = int(action[2]) if len(action) >= 3 else 1


def _encode_step(action: dict) -> np.ndarray:
    row = np.zeros(ACTION_WIDTH, dtype=np.int32)
    farmer = action.get("farmer") or ["PASS"]
    hands = list(action.get("hands") or [])
    units = [farmer] + hands
    row[0] = min(MAX_UNITS, len(units))
    for i, unit in enumerate(units[:MAX_UNITS]):
        _encode_unit(row, i, unit)

    market = list(action.get("market") or [])
    base = 1 + MAX_UNITS * 3
    row[base] = min(RAW_ORDER_SLOTS, len(market))
    for i, order in enumerate(market[:RAW_ORDER_SLOTS]):
        if not order:
            continue
        op = str(order[0])
        if op not in MARKET_OP:
            raise ValueError(f"unknown market op: {op}")
        off = base + 1 + i * 3
        row[off] = MARKET_OP[op]
        row[off + 1] = ITEM.get(str(order[1]), -1) if len(order) >= 2 else -1
        row[off + 2] = int(order[2]) if len(order) >= 3 else 1
    return row


def load_frozen_top_tapes(pack: str | Path):
    pack = Path(pack)
    if not pack.is_file():
        raise FileNotFoundError(pack)

    names = []
    arrays = []
    with zipfile.ZipFile(pack) as zf:
        members = sorted(
            n for n in zf.namelist()
            if n.startswith("prepared/opponents/r") and n.endswith(".tar.gz")
        )
        if len(members) != 7:
            raise ValueError(f"expected 7 frozen rXX opponents, found {len(members)}")
        for member in members:
            blob = zf.read(member)
            with tarfile.open(fileobj=io.BytesIO(blob), mode="r:gz") as tf:
                fh = tf.extractfile("main.py")
                if fh is None:
                    raise ValueError(f"{member}: main.py missing")
                source = fh.read().decode("utf-8")
            tape = _extract_literal_tape(source)
            if len(tape) != 719:
                raise ValueError(f"{member}: expected 719 actions, found {len(tape)}")
            arrays.append(np.stack([_encode_step(a) for a in tape], axis=0))
            names.append(Path(member).name.removesuffix(".tar.gz"))

    out = np.ascontiguousarray(np.stack(arrays, axis=0), dtype=np.int32)
    if out.shape != (7, 719, ACTION_WIDTH):
        raise AssertionError(out.shape)
    return names, out


def find_default_pack(root: str | Path) -> Path:
    root = Path(root)
    candidates = [
        root / "artifacts" / "cr089-frozen-population-packages-v1.zip",
        root / "cr089-frozen-population-packages-v1.zip",
        Path("/mnt/c/Users/Rz9/Downloads/cr089-frozen-population-packages-v1.zip"),
    ]
    for p in candidates:
        if p.is_file():
            return p
    return candidates[-1]
