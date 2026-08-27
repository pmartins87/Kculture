# KEXP-20260827-035 — exact terminal WATER marginal value

Status: **RUNNING / DIAGNOSTIC ONLY**

## Why this follows KEXP-032

KEXP-032 failed because its core mechanics premise was incomplete. One-time crop WATER can increase `yield_units` immediately during the bonus window; no later day refresh is required.

Therefore the correct question is not whether WATER occurs after step 695. It is whether a **specific WATER action** can still create bank value before terminal scoring.

## Frozen protocol

Run unchanged `R4B-market-only-validated-v1` against deterministic `starter` on:

- all 16 development seeds;
- all 20 exploratory live-meta environmental seeds.

Inspect every R4B WATER intent in executable states **696..718**, using corrected replay alignment (`state t -> action frame t+1`).

For each WATER, compute from the exact observed tile state whether the action immediately adds yield:

- crop type;
- already-watered state;
- crop age;
- one-time watering bonus window;
- fertilizer state;
- current yield and max-yield cap.

Ongoing crops have no immediate WATER yield increment. One-time WHEAT/CARROT/MELON can.

For each WATER with positive immediate gain, trace the unchanged R4B future trajectory and ask whether that same tile is later HARVESTed and whether the harvesting actor subsequently DROPs before terminal liquidation. Only that complete path can turn the marginal WATER-created unit into shed inventory and bank value.

## Classification

A WATER is `zero_terminal_value_by_audit` when either:

1. it has zero immediate yield gain; or
2. it has immediate gain but that gain has no later HARVEST -> same-actor DROP path before the step-718 liquidation.

This classification is intentionally conservative and does not itself modify policy.

## Predeclared headroom gate

A corrected terminal replanner remains worth pursuing only if both pools show meaningful reclaimable WATER headroom:

- median audited zero-terminal-value WATER >= **3 per episode**;
- at least 50% of episodes contain >=3 such WATER actions.

Passing authorizes only a planner that **preserves every WATER with a delivered marginal-yield path**. It does not authorize validation or hosted submission.

If the gate fails, WATER is no longer a promising terminal-throughput source; terminal planning should focus on routing/harvest/drop/sale without suppressing maintenance that creates immediate yield.

No validation or held-out seeds are accessed.

Tool: `tools/audit_terminal_water_marginal_value.py`  
Frozen tool blob: `b2ce97dfb03d755bed60b97dedc3f2fb25259e5b`
