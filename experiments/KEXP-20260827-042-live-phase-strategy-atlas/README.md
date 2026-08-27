# KEXP-20260827-042 — live phase strategy atlas

Status: **COMPLETE / MIDGAME LABOR UTILIZATION FLAGGED AS MAJOR ARCHITECTURE GAP**

## Prize-first question

R4B is strong against frozen public agents yet very weak on the hosted ladder. Late-game audits found bounded improvements, but the larger gap could begin much earlier. KEXP-042 profiles the whole game to locate the first major divergence between recent official top winners and frozen R4B.

## Protocol

Top 10 complete official episodes from each of 2026-08-24, 25 and 26 (30 winner trajectories). For each public episode:

1. profile the actual winner;
2. extract only the environmental seed;
3. run frozen R4B versus deterministic starter on that same environmental seed;
4. profile checkpoints 0, 96, 192, 288, 384, 480, 576, 648, 696 and 719;
5. aggregate market/unit actions in coarse phases.

This is descriptive calibration. R4B is not claimed to be playing the same counterfactual market because its opponent differs. Market-money differences are therefore not direct strength estimates. Structural action-utilization and composition differences identify follow-up hypotheses only.

## Canonical result

GitHub Actions run **33044955439 — SUCCESS**.  
Artifact **9635359053**, ZIP digest **SHA-256 `c812e7520ca85b6cb07368865c61a6f839d3b2b2b5212873b56333b0fbe43c10`**.

30 live winners and 30 R4B same-environment trajectories were profiled.

### Earliest large divergence: PASS / labor utilization

Mean PASS actions:

| Phase | Live winners | R4B |
|---|---:|---:|
| 0–95 | 96.0 | 128.0 |
| 96–191 | **32.9** | **119.9** |
| 192–287 | **37.1** | **159.2** |
| 288–383 | 34.8 | 47.3 |
| 384–479 | 15.5 | 18.8 |
| 480–575 | 9.4 | 6.7 |

The midgame gap is not explained by fewer hires. In 192–287, live winners issue ~41.2 HIRE orders while R4B issues ~46.0. The frozen COK controller mechanically pads workers with `PASS` when the static trace has fewer hand actions than currently hired hands, making static-trace labor under-utilization a plausible architecture defect.

During 96–191, live winners also show substantially more actual farm work than R4B, including roughly:

- WATER 102.6 vs 67.8;
- PLANT 30.5 vs 11.8;
- HARVEST 13.4 vs 9.0;
- DROP 2.8 vs 0;
- WHEAT seeds bought 18.4 vs 11.0.

During 192–287, winners use more WATER and DROP while R4B simultaneously has much more PASS despite more hires.

### Composition divergence

The live winners are also much less monocultural than R4B as the game develops:

- checkpoint 192: winners ~11.8 WHEAT / 14.6 STRAWBERRY / 12.9 MELON; R4B ~3.0 / 8.3 / 12.3;
- checkpoint 480: winners already average ~0.9 CARROT and ~2.6 TOMATO; R4B has ~0 of both and ~38 STRAWBERRY;
- checkpoint 648: winners ~11.2 CARROT and ~2.4 TOMATO; R4B ~2.6 CARROT and 0 TOMATO;
- winners carry more SHEEP and fewer COWs than R4B over much of the middle/late game.

This reinforces the existing evidence that top strategies adapt resource allocation instead of replaying one rigid production tape.

## Decision

The next high-ceiling architecture branch is **labor/task allocation**, beginning with KEXP-043 to determine whether R4B PASS actions can be cheaply reclaimed on the same tile or require a dynamic dispatcher. Before implementing a large dispatcher, a winner-vs-loser phase labor audit should confirm whether stronger labor utilization is associated with winning within the same official episodes rather than merely being a family-style difference.

The crop value-controller branch continues independently (KEXP-041).

No validation or held-out seeds were accessed. Team/episode/seed identity is forbidden as a deployable feature.

Tool: `tools/live_phase_strategy_atlas.py`  
Frozen blob: `fe989739d378f4ee25b917429e1b3a4eb4f8d33e`.
