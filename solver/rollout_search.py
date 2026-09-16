from __future__ import annotations

"""Exact-engine counterfactual rollout helpers for Prize Solver training.

This module is OFFLINE training infrastructure. It may branch a cloned engine and
observe terminal rewards, but runtime policy features remain limited to legal current
observation state. No seed, future event or opponent identity is emitted as a runtime
feature.
"""

import copy
from typing import Optional

from .prize_solver_v0 import Plan, _step
from .prize_solver_v1 import PrizeSolverV1


class ForcedPlanSolverV1(PrizeSolverV1):
    """A cloned V1 that follows one strategic Plan for a bounded training horizon."""

    def __init__(self, forced_plan: Plan, force_until_step: int):
        super().__init__()
        self.forced_plan = forced_plan
        self.force_until_step = int(force_until_step)

    @classmethod
    def from_solver(cls, base: PrizeSolverV1, forced_plan: Plan, force_until_step: int):
        out = cls(forced_plan, force_until_step)
        # Preserve everything the baseline knew at the branch point: opponent belief,
        # previous step and any future learned-value parameters.
        out.__dict__.update(copy.deepcopy(base.__dict__))
        out.forced_plan = forced_plan
        out.force_until_step = int(force_until_step)
        # Force immediate reconsideration at the branch point. Subsequent day changes
        # call _select_plan normally, which remains forced until the horizon expires.
        out.current_plan = None
        out.current_day = -1
        return out

    def _select_plan(self, obs, config):
        if _step(obs, config) < self.force_until_step:
            return self.forced_plan
        return super()._select_plan(obs, config)


def clone_solver(solver: PrizeSolverV1) -> PrizeSolverV1:
    return copy.deepcopy(solver)
