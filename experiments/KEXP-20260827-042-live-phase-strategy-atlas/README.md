# KEXP-20260827-042 — live phase strategy atlas

Status: **RUNNING / CALIBRATION DIAGNOSTIC**

## Prize-first question

R4B is strong against frozen public agents yet very weak on the hosted ladder. Late-game audits have identified several bounded mechanisms, but the larger architectural gap may begin much earlier. This experiment profiles the whole game to locate the first major divergence between current official top winners and frozen R4B.

## Protocol

Use the top 10 complete official episodes from each of 2026-08-24, 2026-08-25 and 2026-08-26 (30 winner trajectories). For each public episode:

1. profile the actual winning trajectory;
2. extract only the environmental seed;
3. run frozen R4B versus deterministic starter on that same environmental seed;
4. profile both trajectories at checkpoints 0, 96, 192, 288, 384, 480, 576, 648, 696 and 719;
5. aggregate market/unit actions in coarse phases.

This is descriptive calibration. R4B is **not** claimed to be playing the same counterfactual market because its opponent differs. The atlas is used to identify large strategic timing/composition gaps worth mechanics-first follow-up, not to estimate an exact head-to-head score.

Metrics include money, hands, land quadrants, animal/crop composition, weeds, BUY_LAND, HIRE, BUY_ANIMAL, BUY_SEED by crop, SELL by product, and major unit actions.

No validation or held-out seeds are accessed. Team/episode/seed identity is forbidden as a deployable feature.

Tool: `tools/live_phase_strategy_atlas.py`  
Frozen blob: `fe989739d378f4ee25b917429e1b3a4eb4f8d33e`.
