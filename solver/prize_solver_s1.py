from __future__ import annotations

"""Prize Solver S1 — V4 executor with PS3 learned macro selection.

S1 preserves the proven V4 bootstrap/executor/market/task layers and replaces the
post-bootstrap heuristic macro scorer with the PS3 learned macro-advantage model.
If the model is missing or invalid, it deterministically falls back to V4.
"""

from .learned_macro_value import LearnedMacroValue
from .prize_solver_v0 import Plan, _farm, _get, _ival, _step
from .prize_solver_v2 import BOOTSTRAP, PLANS_V2
from .prize_solver_v4 import PrizeSolverV4


class PrizeSolverS1(PrizeSolverV4):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.learned_macro = LearnedMacroValue()

    def _select_plan(self, obs, config):
        own = _farm(obs)
        animals, crops = self._existing_assets(own)
        step = _step(obs, config)
        turns = max(1, _ival(_get(config, "turnsPerDay", 24), 24))
        day = step // turns

        # Keep the proven cold-start prior. PS3 was trained on branch states beginning
        # at day 3; it should not be asked to invent a zero-asset opening.
        if day < 4:
            return BOOTSTRAP

        # Terminal behavior remains deterministic and does not need macro prediction.
        if day >= 24:
            return Plan(
                "TERMINAL",
                animals["COW"], animals["SHEEP"], animals["GOOSE"],
                0, 0, 0, 5,
                len(_get(own, "unlocked_quadrants", []) or []),
                0,
            )

        # Physical commitments are hard lower bounds; the learned model only chooses
        # among plans that can be reached without destroying existing assets.
        feasible = []
        for p in PLANS_V2:
            if p.cows < animals["COW"] or p.sheep < animals["SHEEP"] or p.geese < animals["GOOSE"]:
                continue
            if p.melons < min(crops["MELON"], 12):
                continue
            if p.strawberries < min(crops["STRAWBERRY"], 4):
                continue
            if p.tomatoes < min(crops["TOMATO"], 4):
                continue
            feasible.append(p)
        if not feasible:
            feasible = list(PLANS_V2)

        if not self.learned_macro.valid:
            return super()._select_plan(obs, config)

        model_plans = set(self.learned_macro.plan_names)
        candidates = [p for p in feasible if p.name in model_plans]
        if not candidates:
            return super()._select_plan(obs, config)

        scored = [(self.learned_macro.score(obs, config, p.name), p) for p in candidates]
        scored.sort(key=lambda row: (row[0], row[1].name), reverse=True)
        return scored[0][1]


_SOLVER = PrizeSolverS1()


def agent(obs, config=None):
    return _SOLVER.act(obs, config or {})
