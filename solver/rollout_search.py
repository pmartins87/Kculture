from __future__ import annotations

"""Exact-engine counterfactual rollout helpers for Prize Solver training.

Offline only: cloned engine branches may observe terminal rewards to create labels.
Runtime agents never receive seed, future events, or hidden opponent state.
"""

import copy

from .prize_solver_v0 import Plan, _step


class _ForcedPlanMixin:
    def _select_plan(self, obs, config):
        if _step(obs, config) < self.force_until_step:
            return self.forced_plan
        return super()._select_plan(obs, config)


def forced_plan_solver(base_solver, forced_plan: Plan, force_until_step: int):
    """Clone any current PrizeSolver subclass and force one macro temporarily."""
    forced_cls = type(
        f"Forced{base_solver.__class__.__name__}",
        (_ForcedPlanMixin, base_solver.__class__),
        {},
    )
    out = forced_cls.__new__(forced_cls)
    out.__dict__ = copy.deepcopy(base_solver.__dict__)
    out.forced_plan = forced_plan
    out.force_until_step = int(force_until_step)
    out.current_plan = None
    out.current_day = -1
    return out


def clone_solver(solver):
    return copy.deepcopy(solver)
