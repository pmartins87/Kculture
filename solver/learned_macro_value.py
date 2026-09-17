from __future__ import annotations

"""Pure-Python inference for Prize Solver PS3 macro-advantage models.

The offline trainer exports a JSON MLP. Hosted inference intentionally avoids numpy or
any ML framework so the Kaggle agent only needs the standard library. The model scores
one of the five PLANS_V2 macro plans from the current visible state.
"""

import json
from pathlib import Path
from typing import Dict, Iterable, List, Optional

from .value_features import encode_value_features


DEFAULT_MODEL_PATH = Path(__file__).resolve().parents[1] / "models" / "prize_solver_value_v1.json"


def _dense(vec: List[float], weight: List[List[float]], bias: List[float]) -> List[float]:
    if not weight:
        return list(bias)
    out_dim = len(weight[0])
    out = [float(bias[j]) for j in range(out_dim)]
    for i, x in enumerate(vec):
        row = weight[i]
        fx = float(x)
        for j in range(out_dim):
            out[j] += fx * float(row[j])
    return out


def _relu(vec: Iterable[float]) -> List[float]:
    return [x if x > 0.0 else 0.0 for x in vec]


class LearnedMacroValue:
    def __init__(self, path: Optional[str] = None):
        self.path = Path(path) if path else DEFAULT_MODEL_PATH
        self.model: Optional[Dict] = None
        self.error: Optional[str] = None
        self._load()

    @property
    def valid(self) -> bool:
        return self.model is not None

    @property
    def plan_names(self):
        if not self.model:
            return ()
        return tuple(self.model.get("plan_names", []))

    def _load(self):
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            if data.get("schema") != "prize-solver-value-v1":
                raise ValueError(f"unexpected schema {data.get('schema')!r}")
            feature_names = list(data.get("feature_names", []))
            plan_names = list(data.get("plan_names", []))
            mean = list(data.get("input_mean", []))
            std = list(data.get("input_std", []))
            weights = data.get("weights", {})
            expected = len(feature_names) + len(plan_names)
            if not feature_names or not plan_names:
                raise ValueError("empty feature/plan contract")
            if len(mean) != expected or len(std) != expected:
                raise ValueError(f"normalization width mismatch expected={expected} mean={len(mean)} std={len(std)}")
            for key in ("W1", "b1", "W2", "b2", "W3", "b3"):
                if key not in weights:
                    raise ValueError(f"missing weight {key}")
            self.model = data
            self.error = None
        except Exception as exc:
            self.model = None
            self.error = f"{type(exc).__name__}: {exc}"

    def score(self, obs, config, plan_name: str) -> float:
        if not self.model:
            raise RuntimeError(self.error or "learned macro value model is unavailable")
        m = self.model
        plan_names = list(m["plan_names"])
        if plan_name not in plan_names:
            raise KeyError(plan_name)

        feats = encode_value_features(obs, config or {})
        feature_names = list(m["feature_names"])
        x = [float(feats.get(name, 0.0)) for name in feature_names]
        x.extend(1.0 if name == plan_name else 0.0 for name in plan_names)

        mean = m["input_mean"]
        std = m["input_std"]
        xn = []
        for i, raw in enumerate(x):
            den = float(std[i])
            if abs(den) < 1e-12:
                den = 1.0
            xn.append((float(raw) - float(mean[i])) / den)

        w = m["weights"]
        h1 = _relu(_dense(xn, w["W1"], w["b1"][0] if w["b1"] and isinstance(w["b1"][0], list) else w["b1"]))
        h2 = _relu(_dense(h1, w["W2"], w["b2"][0] if w["b2"] and isinstance(w["b2"][0], list) else w["b2"]))
        y = _dense(h2, w["W3"], w["b3"][0] if w["b3"] and isinstance(w["b3"][0], list) else w["b3"])
        return float(y[0]) * float(m.get("target_scale", 1.0))
