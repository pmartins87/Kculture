# KEXP-20260827-033 — bounded final-day collector

Status: **COMPLETE / REJECTED / ARCHITECTURAL LESSON RETAINED**

## Mechanics correction

KEXP-033 was launched under the same incomplete WATER premise as KEXP-032. One-time crop WATER can increase `yield_units` immediately during the bonus window, even without another day refresh. PLANT can also create a base-yield tile immediately. Therefore blanket suppression of final-day maintenance/investment actions is unsound.

## Candidate tested

`candidates/r4d_terminal_collector.py`

The candidate kept R4B through step 695, then attempted a greedy final-day collector:

- inventory-bearing actors routed to shed access and DROPed;
- actors on positive yield HARVESTed;
- remaining actors were assigned to positive-yield tiles when travel + HARVEST + return + DROP fit before terminal;
- target priority used current market value per required action;
- many base maintenance actions were suppressed;
- step-718 R4B liquidation was recomputed after rewritten unit actions.

Candidate blob: `dc01e2abba24d67e575344b1720a7991cb05772c`.  
Base R4B blob: `e564125f0c4a1711fd3ea065dc1cb27d4a62ce37`.

## Canonical result

Actions run **`33042179129` — SUCCESS**.  
Artifact **`9634534616`**.  
Artifact ZIP digest **SHA-256 `dc200b3f509467d0d2cdd060cc6dde659cc3d8f6a540d79f835c7e4585641b56`**.

Zero runtime/status errors.

Modern development panel:

- Kaito V27: **25-7-0**, mean terminal delta +3,838.13;
- Rayk V11: **28-4-0**, mean terminal delta +6,915.69;
- Andrew V12: **23-9-0**, mean terminal delta +4,770.09;
- combined: **76-20-0**, materially worse than frozen R4B **81-15-0**.

Direct candidate vs R4B, 16 development seeds × both seats:

- **2-30-0**;
- score rate **0.0625**;
- mean terminal delta **-468.78125**.

## What the failure teaches

The planner did achieve one intended surface behavior: candidate final-day DROP count rose to roughly **30 per game**, versus roughly 8 in the frozen R4B traces. But this did not translate into strength.

At the same time, candidate final-day HARVEST fell to roughly **16 per game** in the modern panel, versus roughly 28–29 for the simpler WATER-ablation/R4B-like trajectory. It routed inventory home too aggressively and suppressed actions that either create or collect value.

Thus the optimization target cannot be `maximize DROP` or `maximize amount routed to shed`. It must optimize the **marginal terminal value of an entire action sequence**:

`yield creation -> harvest -> transport -> drop -> sale`, subject to the remaining action budget.

A WATER that adds one unit and still has a feasible harvest/delivery path can dominate an immediate movement action. Conversely, a WATER with no possible delivered marginal unit is genuine reclaimable throughput.

## Decision

**Reject KEXP-033. Do not promote or validate it.**

Retain only the bounded-planning idea. Rebuild it from exact marginal action value rather than a blanket post-695 action taxonomy.

KEXP-035 is the immediate successor: it audits every final-day WATER for immediate yield gain and a later HARVEST -> DROP delivery path before considering any new planner.

No validation or held-out seeds were accessed.
