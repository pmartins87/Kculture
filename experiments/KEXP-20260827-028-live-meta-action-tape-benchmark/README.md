# KEXP-20260827-028 — live-meta action-tape benchmark

Status: **COMPLETE / EXACT REPLAY PASS / OPEN-LOOP OPPONENT BENCHMARK DEPRIORITIZED**

## Prize-first problem

Frozen Kaito/Rayk/Andrew are useful regression controls but are poorly calibrated to the hosted field. Official high-Elo datasets expose complete public replays, including environmental state and both submitted action streams. This experiment tested whether those streams can serve as a closer development benchmark.

## Critical replay convention

The canonical V2 established the exact Kaggle JSON alignment:

> the action chosen from observation/state frame `t` is stored on replay frame `t+1`.

This convention is now mandatory for all replay-based Kculture diagnostics.

## Phase A — exact replayability

Freeze the official 2026-08-26 top 10 episodes by manifest `avg_score`, extract both action streams with the corrected one-frame alignment, recreate the official environment, and replay tape-vs-tape in original seats.

Canonical run **`33040385897` — SUCCESS**.
Artifact **`9633695306`**, ZIP digest **SHA-256 `ddd3ede71c21e3cbd16343243aa8212abf16826c9055edb5daa921d1cd70ec8f`**.

Result:

- exact terminal reproductions: **10/10**;
- fraction: **1.000**;
- every replay: 720 states, both players `DONE`;
- both terminal rewards exactly equal the official public episode.

The infrastructure gate therefore passes strongly. Public high-Elo trajectories are reliable for state/action forensics and temporal policy mining.

## Phase B — frozen R4B versus original winner tape

For each exact episode, keep the original winner tape in its original seat and replace the loser with frozen R4B.

Result:

- valid games: 10;
- R4B W/L/T: **6-4-0**;
- score rate: **0.60**;
- mean R4B terminal delta: **+21,938**;
- median delta: **+14,135.5**.

Taken alone, 6-4 would misleadingly suggest that R4B is competitive with the top field. The counterfactual diagnostic proves why it cannot be used that way:

- mean absolute change in the winner tape's reward versus its original episode: **44,824.2**.

The fixed winner tape cannot react when R4B changes market supply, prices, blocking and other shared state. Its policy is therefore badly off-distribution in the counterfactual game.

## Decision

**Exact replay infrastructure is promoted; open-loop tape-vs-agent W/L is not.**

Use high-Elo replays for:

- exact observation/action alignment;
- state-conditioned behavior mining;
- causal/mechanical hypothesis generation;
- temporal holdout studies;
- future behavioral/value-model training where legal.

Do **not** use winner tapes as a calibrated live-field opponent or infer hosted strength from the 6-4 result.

KEXP-029 is the first direct continuation: learn a small late crop demand+price decision surface from exact public state/action pairs, using Aug-22..25 as training days and Aug-26 as temporal test.

No validation or held-out seeds were accessed. Team, episode and seed identities remain forbidden deployment features.
