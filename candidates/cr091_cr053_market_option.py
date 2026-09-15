"""CR091 gate-1 wrapper: exact CR053 physical route + exact CR086 market priority.

Phase 1 deliberately injects the donor CR053 agent and CR086 module at runtime from
byte-verified historical artifacts.  This keeps the experiment tied to exact hosted
bytes and prevents reimplementation drift in the CR086 estimator/operator.
"""
from __future__ import annotations

import copy
from types import SimpleNamespace


def _clock(obs):
    try:
        raw = obs.get("step")
        if raw is not None:
            return max(0, int(raw))
    except Exception:
        pass
    try:
        return max(0, int(obs.get("day") or 0)) * 24 + max(0, int(obs.get("hour") or 0))
    except Exception:
        return 0


class CR053MarketOption:
    """Apply only CR086's order-priority operator to an injected CR053 agent."""

    def __init__(self, base_agent, cr086_module, enabled=True):
        self.base_agent = base_agent
        self.cr086 = cr086_module
        self.enabled = bool(enabled)
        self.state = SimpleNamespace()
        self.reorders = 0

    def __call__(self, obs, config=None):
        try:
            base = self.base_agent(obs, config)
        except TypeError:
            base = self.base_agent(obs)
        action = copy.deepcopy(base)
        if not self.enabled:
            return action

        step = _clock(obs)
        self.cr086._cr086_update(self.state, obs, step)
        market = [list(order) for order in (action.get("market") or [])]
        prioritized = self.cr086._cr086_prioritize(self.state, obs, market)
        if prioritized != market:
            self.reorders += 1
        action["market"] = prioritized
        return action


def make_agent(base_agent, cr086_module, enabled=True):
    return CR053MarketOption(base_agent, cr086_module, enabled=enabled)
