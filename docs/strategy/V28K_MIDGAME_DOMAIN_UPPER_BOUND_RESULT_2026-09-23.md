# V28K — Midgame Hard-Core Domain Upper Bound — Binding Result

Date: 2026-09-23

Binding workflow: `35822623519`.

## Decision

**`V28K_NO_MIDGAME_WINDOW_WL_HEADROOM`**

Mechanical PASS, failures 0. All 66 frozen V28F ALL3 residual losses were evaluated under the preregistered 384–479 window and BASE replay parity contract.

## Frozen modes

- BASE: 0 loss-to-win flips; mean score delta 0; mean margin delta 0.
- MARKET_WINDOW: 0 flips; mean score delta 0; mean margin delta -548.33; 34 positive-margin and 32 negative-margin contexts.
- PHYSICAL_WINDOW: 4 loss-to-win flips across 2 sources and both seats, mean score delta +0.060606 and mean margin delta +171.23, but all four flips came from only **one seed (80401)**. It therefore fails the frozen domain-pass rule requiring >=4 flips across >=2 sources **and >=2 seeds** with positive mean score delta.
- FULL_WINDOW: 0 flips; mean score delta 0; mean margin delta +614.17.

No interaction-exclusive FULL_WINDOW flips existed.

## Interpretation

The 384–479 midgame window has no robust W/L causal headroom under the frozen upper-bound interventions. Physical action substitution is the only directional hint, but its four wins are seed-concentrated and explicitly fail the preregistered robustness rule. MARKET is not supported; FULL does not convert any loss.

This result is independent of V28J. Combined only after both gates resolved, V28J closes simple classifier risk gating on this window and V28K closes robust domain-level W/L headroom within this same midgame window. The next technical route should therefore remain direct mechanism/action discovery rather than classifier retuning, with causal localization moved beyond the exhausted 384–479 window rather than weakening V28K thresholds.

No Kaggle mutation was performed or authorized. Hosted pair remains exact V47 `56466970` + ALL3 `56367770`.