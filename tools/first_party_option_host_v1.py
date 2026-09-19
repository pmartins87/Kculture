#!/usr/bin/env python3
"""Reusable first-party option host: O-RW1 + O-TW1 + O-LQ2.

This module contains no opponent identity logic. It accepts the exact current V47
base action and applies only legal-state first-party operators.
"""
from __future__ import annotations
from dataclasses import dataclass
from tools.bounded_transaction_oracle_v1 import canonical_action
from tools.first_party_ready_wool_causal_gate import eligible as rw_eligible, treated_action as rw_treated_action
from tools.first_party_town_wheat_deferral_causal_gate import eligible as tw_eligible, treated_action as tw_treated_action
from tools.first_party_lq2_canonical_sell_queue import lq2_action

@dataclass
class OptionHostState:
    rw_used: bool = False
    tw_used: bool = False

def apply_option_host(
    obs,
    config,
    base_action,
    state: OptionHostState,
    *,
    use_rw: bool = True,
    use_tw: bool = True,
    use_lq2: bool = True,
):
    base=canonical_action(base_action)
    out=base

    # Preserve the frozen one-shot semantics: eligibility is evaluated on exact V47.
    if use_tw and not state.tw_used and tw_eligible(obs,config,base):
        out,removed=tw_treated_action(base)
        if removed<=0:
            raise RuntimeError("O-TW1 eligible but removed no WHEAT sale")
        state.tw_used=True
    elif use_rw and not state.rw_used and rw_eligible(obs,base):
        out=rw_treated_action(base)
        state.rw_used=True

    if use_lq2:
        out=lq2_action(obs,config,out)

    out=canonical_action(out)
    if out["farmer"]!=base["farmer"] or out["hands"]!=base["hands"]:
        raise RuntimeError("option host changed exact V47 physical action")
    return out
