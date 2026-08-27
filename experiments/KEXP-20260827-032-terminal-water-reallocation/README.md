# KEXP-20260827-032 — terminal WATER reallocation

Status: **RUNNING / DEVELOPMENT CANDIDATE**

## Prize-first mechanism

The final executable partial day is states 696..718. There is no later daily crop/animal production refresh before terminal scoring. Therefore WATER submitted in this window has zero possible terminal-production value.

Inspection of the KEXP-024 development replays showed frozen R4B still emits roughly **10 WATER actions per game** in 696..718 (324 candidate-side WATER actions across 32 direct-panel games). This is a large, exact-mechanics terminal-throughput leak.

## Candidate

`candidates/r4d_terminal_water_harvest.py`

Frozen R4B is unchanged everywhere except when a farmer/hand base action is WATER during 696..718:

1. if the actor is already standing on a tile with positive `yield_units`, replace WATER with HARVEST;
2. else if the actor is on the shed and carries sellable inventory, replace with DROP;
3. otherwise replace with PASS.

No movement, route selection, crop allocation, FEED, CARE, seed buying, earlier action, or market logic is changed. R4B's step-718 projected-shed liquidation remains active.

This first candidate is deliberately bounded. It tests whether simply reclaiming impossible-to-pay WATER produces measurable gain before building a full final-day planner.

Candidate blob: `a34f7d137b6a06b45714bc7f79bb8c3995c835d0`.
Base R4B blob: `e564125f0c4a1711fd3ea065dc1cb27d4a62ce37`.

## Frozen development gate

Run all 16 development seeds in both seats against the modern public panel:

- Kaito V27;
- Rayk V11;
- Andrew V12.

Also run 16 seeds × both seats directly against frozen R4B.

Promotion to broader exploratory testing requires:

- zero runtime/status errors;
- combined modern-panel W/L no worse than frozen R4B's **81-15**;
- no opponent family loses more than one win versus the frozen R4B reference;
- direct candidate-vs-R4B score rate >= **0.53125** (at least a one-game edge on 32 games, ties half);
- direct mean terminal delta > 0.

A panel tie with only tiny money gain is not enough for hosted submission. A clear direct edge plus preserved panel W/L would justify expanding toward a stronger terminal planner or, if the effect is already material and mechanically stable, considering hosted calibration under the revised submission policy.

No validation or held-out seeds are accessed.
