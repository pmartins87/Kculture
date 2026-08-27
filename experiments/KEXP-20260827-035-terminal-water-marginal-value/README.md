# KEXP-20260827-035 — exact terminal WATER marginal value

Status: **COMPLETE / HEADROOM GATE FAIL / WATER THROUGHPUT BRANCH CLOSED**

## Why this follows KEXP-032

KEXP-032 failed because one-time crop WATER can increase `yield_units` immediately during the bonus window. KEXP-035 therefore audits each final-day WATER from state rather than classifying it by step alone.

## Frozen protocol

Unchanged `R4B-market-only-validated-v1` vs deterministic `starter` on all 16 development seeds and 20 exploratory live-meta environmental seeds. Every R4B WATER intent in executable states 696..718 is inspected with corrected replay alignment (`state t -> action frame t+1`).

For each WATER, the audit computes exact immediate yield gain from crop type, age, already-watered state, fertilizer status and max-yield cap. Any positive marginal unit is then traced through the unchanged R4B future trajectory for a later same-tile HARVEST and same-actor DROP before terminal liquidation.

## Canonical result

Actions run **`33042953766` — SUCCESS**.  
Artifact **`9634630280`**, ZIP digest **SHA-256 `4c2e924058834d2fd6594e486dd17b8c7cd2a5081b311d38c11d644e5745e7cb`**.

Combined 36 episodes:

- WATER intents: **374**;
- WATER with immediate yield bonus: **371**;
- immediate-gain WATER with later HARVEST→DROP delivery path: **365**;
- audited zero-terminal-value WATER: **9 / 374 = 2.41%**;
- median zero-value WATER per episode: **0**;
- mean: **0.25**;
- episodes with at least 3 zero-value WATER: **0/36**.

Development:

- 167 WATER;
- **167/167** produced immediate WHEAT yield;
- 164 had a later delivery path;
- only **3** audited zero-value WATER;
- median zero per episode **0**.

Exploratory live-meta:

- 207 WATER;
- 204 produced immediate WHEAT yield;
- 201 had a later delivery path;
- only **6** audited zero-value WATER;
- median zero per episode **0**.

The delivered marginal units represented a terminal-price proxy sum of approximately **17,341 coins** across the 36 trajectories. This is not a causal reward estimate, but it makes clear why blanket suppression was so destructive.

## Decision

The predeclared headroom gate fails overwhelmingly. **Close WATER as a terminal-throughput source.**

Do not spend further experiments trying to reclaim final-day WATER by step, threshold or broad class. Nearly all observed R4B WATER in this window is direct yield creation followed by collection/delivery.

A future terminal planner may still optimize routing, harvest, drop and sale, but it must preserve these value-bearing WATER actions unless it replaces them with an action sequence of demonstrably higher complete terminal value.

No validation or held-out seeds were accessed.

Tool: `tools/audit_terminal_water_marginal_value.py`  
Frozen tool blob: `b2ce97dfb03d755bed60b97dedc3f2fb25259e5b`
