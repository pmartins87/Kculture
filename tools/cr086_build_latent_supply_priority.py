"""Build frozen CR086 latent-supply priority candidate from exact CR083.

The builder embeds only the already-confirmed legal estimator primitives from
``cr086_opponent_inventory_estimator_eval.py``. Offline truth-label code is never
embedded. CR086 changes only the ordering of existing premium SELL orders after
all CR083 market logic has finished.
"""
from __future__ import annotations

import argparse
import ast
import gzip
import hashlib
import io
import json
import tarfile
from pathlib import Path

BASE_SHA = "648fbcdb370f7e48fafda18a1112c5f1b57a17a81b7191f010fe4058f41a41b8"
PRIMARY = ("CARROT", "TOMATO", "STRAWBERRY", "MELON", "EGG", "MILK", "WOOL")
ALLOWED_ESTIMATOR_FUNCS = (
    "private_total",
    "public_yield_total",
    "town_demand",
    "units_on_tile",
    "point_creation",
    "upper_creation",
)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def extract_main(package: Path) -> str:
    with tarfile.open(package, "r:gz") as tf:
        f = tf.extractfile(tf.getmember("main.py"))
        if f is None:
            raise RuntimeError("main.py missing")
        return f.read().decode("utf-8")


def extract_confirmed_estimator_primitives(path: Path) -> str:
    """Extract only runtime-legal functions from the confirmed evaluator source."""
    text = path.read_text(encoding="utf-8")
    tree = ast.parse(text)
    chunks = []
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name in ALLOWED_ESTIMATOR_FUNCS:
            seg = ast.get_source_segment(text, node)
            if not seg:
                raise RuntimeError(f"cannot recover estimator function {node.name}")
            chunks.append(seg)
    found = {ast.parse(c).body[0].name for c in chunks}
    if found != set(ALLOWED_ESTIMATOR_FUNCS):
        raise RuntimeError(f"estimator primitive mismatch: {found}")
    out = "\n\n".join(chunks)
    # Namespace every extracted symbol/global so CR083 constants remain untouched.
    replacements = {
        "private_total": "_cr086_private_total",
        "public_yield_total": "_cr086_public_yield_total",
        "town_demand": "_cr086_town_demand",
        "units_on_tile": "_cr086_units_on_tile",
        "point_creation": "_cr086_point_creation",
        "upper_creation": "_cr086_upper_creation",
        "CROPS": "_CR086_CROPS",
        "ANIMALS": "_CR086_ANIMALS",
        "SHOPS": "_CR086_SHOPS",
    }
    # Longest-first avoids accidental partial replacement.
    for old in sorted(replacements, key=len, reverse=True):
        out = out.replace(old, replacements[old])
    return out


def runtime_block(estimator_source: Path) -> str:
    primitives = extract_confirmed_estimator_primitives(estimator_source)
    return f'''# ---- CR086 latent-supply representation + exact market value helpers ----
_CR086_PRIMARY = {PRIMARY!r}
_CR086_CROPS = {{
    "CARROT": {{"first": 2, "maxday": 3, "max": 4, "ongoing": False, "interval": 0}},
    "TOMATO": {{"first": 8, "maxday": 8, "max": 4, "ongoing": True, "interval": 1}},
    "STRAWBERRY": {{"first": 10, "maxday": 10, "max": 4, "ongoing": True, "interval": 2}},
    "MELON": {{"first": 10, "maxday": 12, "max": 6, "ongoing": False, "interval": 0}},
}}
_CR086_ANIMALS = {{
    "GOOSE": {{"first": 4, "interval": 1, "max": 4, "product": "EGG"}},
    "COW": {{"first": 8, "interval": 2, "max": 6, "product": "MILK"}},
    "SHEEP": {{"first": 6, "interval": 3, "max": 6, "product": "WOOL"}},
}}
_CR086_SHOPS = {{
    "BAKERY": ("EGG", "WHEAT"),
    "PIZZA_SHOP": ("MILK", "TOMATO", "WHEAT"),
    "BRUNCH_SPOT": ("EGG", "WHEAT", "STRAWBERRY"),
    "YARN_STORE": ("WOOL",),
    "ICE_CREAM_SHOP": ("STRAWBERRY", "MILK", "WHEAT"),
    "PET_CAFE": ("CARROT",),
    "SMOOTHIE_SHOP": ("STRAWBERRY", "MILK"),
    "FARMERS_MARKET": ("WHEAT", "CARROT", "TOMATO", "STRAWBERRY"),
}}
_CR086_MARKET_PARAMS = {{
    "CARROT": {{"base":35,"I0":10000,"T":450,"below_func":"hinge","below_target":1.00,"above_func":"sqrt","above_target":0.70}},
    "TOMATO": {{"base":60,"I0":10000,"T":200,"below_func":"hinge","below_target":0.40,"above_func":"sqrt","above_target":0.60}},
    "STRAWBERRY": {{"base":120,"I0":10000,"T":100,"below_func":"sqrt","below_target":0.70,"above_func":"linear","above_target":1.60}},
    "MELON": {{"base":250,"I0":10000,"T":300,"below_func":"log","below_target":0.20,"above_func":"sq","above_target":3.60}},
    "EGG": {{"base":50,"I0":10000,"T":332,"below_func":"hinge","below_target":0.40,"above_func":"log","above_target":0.20}},
    "MILK": {{"base":160,"I0":10000,"T":122,"below_func":"sqrt","below_target":0.60,"above_func":"linear","above_target":1.60}},
    "WOOL": {{"base":200,"I0":10000,"T":105,"below_func":"log","below_target":0.20,"above_func":"sq","above_target":3.20}},
}}

{primitives}


def _cr086_shape(func, x, T):
    x = max(0.0, float(x))
    if func == "linear": return x
    if func == "sq": return x * x
    if func == "sqrt": return math.sqrt(x)
    if func == "log": return math.log(1.0 + x)
    if func == "hinge":
        u = x / T
        return u + 8.0 * max(0.0, u - 1.0) ** 2
    return x


def _cr086_market_price(item, inventory):
    p = _CR086_MARKET_PARAMS[item]
    base, I0, T = p["base"], p["I0"], p["T"]
    if inventory < I0:
        f = p["below_func"]
        amp = p["below_target"] * base / _cr086_shape(f, T, T)
        price = base + amp * _cr086_shape(f, I0 - inventory, T)
    else:
        f = p["above_func"]
        amp = p["above_target"] * base / _cr086_shape(f, T, T)
        price = base - amp * _cr086_shape(f, inventory - I0, T)
    return max(1, int(round(price)))


def _cr086_advance(item, inventory, units):
    m = int(inventory)
    for _ in range(max(0, int(units))):
        if _cr086_market_price(item, m) > 1:
            m += 1
    return m


def _cr086_revenue(item, inventory, units):
    m, total = int(inventory), 0
    for _ in range(max(0, int(units))):
        price = _cr086_market_price(item, m)
        total += price
        if price > 1:
            m += 1
    return total


def _cr086_snapshot(obs):
    return {{
        "farms": copy.deepcopy(obs.get("farms") or []),
        "market": copy.deepcopy(obs.get("market") or {{}}),
        "town": copy.deepcopy(obs.get("town") or {{}}),
        "private": copy.deepcopy(obs.get("private") or {{}}),
    }}


def _cr086_update(agent, obs, step):
    if not hasattr(agent, "_cr086_prev"):
        agent._cr086_prev = None
        agent._cr086_point_mass = None
        agent._cr086_upper_mass = None
        agent._cr086_ever_floor = dict((x, False) for x in _CR086_PRIMARY)
        agent._cr086_upper = dict((x, 0) for x in _CR086_PRIMARY)

    if agent._cr086_prev is None:
        agent._cr086_point_mass = {{}}
        agent._cr086_upper_mass = {{}}
        for item in _CR086_PRIMARY:
            mass = (int(obs["market"]["inventory"].get(item, 0))
                    + _cr086_public_yield_total(obs["farms"], item)
                    + _cr086_private_total(obs.get("private") or {{}}, item))
            agent._cr086_point_mass[item] = mass
            agent._cr086_upper_mass[item] = mass
            agent._cr086_upper[item] = 0
        agent._cr086_prev = _cr086_snapshot(obs)
        return

    if step <= 0:
        agent._cr086_prev = _cr086_snapshot(obs)
        return

    pre = agent._cr086_prev
    transition_step = step - 1
    for item in _CR086_PRIMARY:
        if (int((pre.get("market") or {{}}).get("prices", {{}}).get(item, 999)) <= 1
                or int(obs["market"]["prices"].get(item, 999)) <= 1):
            agent._cr086_ever_floor[item] = True
        demand = _cr086_town_demand(pre, item, transition_step)
        agent._cr086_point_mass[item] += _cr086_point_creation(pre, obs, item, transition_step) - demand
        agent._cr086_upper_mass[item] += _cr086_upper_creation(pre, obs, item, transition_step) - demand
        known = (int(obs["market"]["inventory"].get(item, 0))
                 + _cr086_private_total(obs.get("private") or {{}}, item)
                 + _cr086_public_yield_total(obs["farms"], item))
        zero_loss_point = max(0, int(agent._cr086_point_mass[item] - known))
        point = 0 if agent._cr086_ever_floor[item] else zero_loss_point
        upper = max(point, max(0, int(agent._cr086_upper_mass[item] - known)))
        agent._cr086_upper[item] = upper
    agent._cr086_prev = _cr086_snapshot(obs)


def _cr086_cash_risk(agent, obs, order):
    if not (order and len(order) >= 3 and order[0] == "SELL" and order[1] in _CR086_PRIMARY):
        return 0
    item = order[1]
    qty = max(0, int(order[2]))
    latent = max(0, int(agent._cr086_upper.get(item, 0)))
    if qty <= 0 or latent <= 0:
        return 0
    inventory = int(obs["market"]["inventory"].get(item, 0))
    now = _cr086_revenue(item, inventory, qty)
    after = _cr086_revenue(item, _cr086_advance(item, inventory, latent), qty)
    return max(0, int(now - after))


def _cr086_prioritize(agent, obs, market):
    urgent = []
    for idx, order in enumerate(market):
        risk = _cr086_cash_risk(agent, obs, order)
        if risk > 0:
            urgent.append((risk, idx, list(order)))
    if not urgent:
        return [list(o) for o in market]
    urgent_indices = {{idx for _, idx, _ in urgent}}
    urgent.sort(key=lambda row: (-row[0], row[1]))
    return ([order for _, _, order in urgent]
            + [list(order) for idx, order in enumerate(market) if idx not in urgent_indices])
'''


def patch_source(source: str, estimator_source: Path) -> str:
    imports = "import base64\nimport json\nimport zlib\n"
    if source.count(imports) != 1:
        raise RuntimeError("CR083 import anchor mismatch")
    source = source.replace(imports, "import base64\nimport copy\nimport json\nimport math\nimport zlib\n", 1)

    pass_anchor = 'PASS = {"farmer": ["PASS"], "hands": [], "market": []}\n\n'
    if source.count(pass_anchor) != 1:
        raise RuntimeError("CR083 PASS anchor mismatch")
    source = source.replace(pass_anchor, pass_anchor + runtime_block(estimator_source) + "\n\n", 1)

    act_anchor = '        me = int(obs.get("player", 0))\n        farm = obs["farms"][me]\n'
    if source.count(act_anchor) != 1:
        raise RuntimeError("CR083 act anchor mismatch")
    source = source.replace(
        act_anchor,
        '        me = int(obs.get("player", 0))\n        _cr086_update(self, obs, step)\n        farm = obs["farms"][me]\n',
        1,
    )

    return_anchor = (
        '            final_market = clamped\n'
        '\n'
        '        return {"farmer": acts[0], "hands": acts[1:],\n'
        '                "market": final_market}\n'
    )
    if source.count(return_anchor) != 1:
        raise RuntimeError("CR083 final market anchor mismatch")
    source = source.replace(
        return_anchor,
        '            final_market = clamped\n'
        '\n'
        '        # ---- CR086 latent-supply priority: ordering only ----\n'
        '        final_market = _cr086_prioritize(self, obs, final_market)\n'
        '\n'
        '        return {"farmer": acts[0], "hands": acts[1:],\n'
        '                "market": final_market}\n',
        1,
    )
    compile(source, "main.py", "exec")
    return source


def write_deterministic_tar_gz(path: Path, main_text: str) -> None:
    data = main_text.encode("utf-8")
    ti = tarfile.TarInfo("main.py")
    ti.size = len(data)
    ti.mode = 0o644
    ti.mtime = 0
    raw = io.BytesIO()
    with tarfile.open(fileobj=raw, mode="w", format=tarfile.PAX_FORMAT) as tf:
        tf.addfile(ti, io.BytesIO(data))
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as fh:
        with gzip.GzipFile(filename="", mode="wb", fileobj=fh, mtime=0) as gz:
            gz.write(raw.getvalue())


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", type=Path, required=True)
    ap.add_argument("--estimator-source", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--manifest", type=Path, required=True)
    a = ap.parse_args()

    base_sha = sha256_bytes(a.base.read_bytes())
    if base_sha != BASE_SHA:
        raise RuntimeError(f"frozen CR083 SHA mismatch: {base_sha}")

    patched = patch_source(extract_main(a.base), a.estimator_source)
    write_deterministic_tar_gz(a.output, patched)
    candidate_sha = sha256_bytes(a.output.read_bytes())

    manifest = {
        "schema_version": "cr086-latent-supply-priority-v1",
        "candidate": "CR086",
        "base": "CR083",
        "base_sha256": base_sha,
        "candidate_sha256": candidate_sha,
        "premium_products": list(PRIMARY),
        "estimator_source": str(a.estimator_source),
        "estimator_confirmed_semantics_only": True,
        "risk_stock_source": "opponent_private_stock_upper_bound",
        "cash_risk_threshold": 0,
        "queue_change": "urgent existing premium SELL orders to front, decreasing cash risk, stable original-index tie-break",
        "market_order_multiset_modified": False,
        "market_quantities_modified": False,
        "physical_actions_modified": False,
        "route_tapes_modified": False,
        "route_switch_modified": False,
        "cr083_seed_clamp_modified": False,
        "public_backbone_code_reused": False,
        "identity_episode_rating_seed_future_opponent_private_features": False,
    }
    a.manifest.parent.mkdir(parents=True, exist_ok=True)
    a.manifest.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
