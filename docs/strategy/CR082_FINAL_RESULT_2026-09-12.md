# CR082 — final result

Status: **CLOSED / FAIL**.

Canonical workflow: `34708795892`.

Candidate SHA-256: `199d32fdda64d4c8d4334f7174d1532147b75837c51104eab9a7c78aec302c2a`.

Master seed: `9120821`; 32 fresh non-overlapping seeds × both seats = 64 games/H2H.

The complete seven-row panel finished with zero execution errors and zero non-DONE games. The candidate package was deterministically reproducible and had passed its pre-H2H self-audits, so this is valid strategic evidence rather than an implementation failure.

## Frozen promotion-gate result

| Matchup | CR082 score | CR071M same-seed control | Delta |
|---|---:|---:|---:|
| CR082 vs CR071M | **0–64 = 0.0000** | — | — |
| vs CR053 | **0–64 = 0.0000** | 32–32 = 0.5000 | **-0.5000** |
| vs CR061 | **0–64 = 0.0000** | 62–2 = 0.96875 | **-0.96875** |
| vs CR065 | **0–64 = 0.0000** | 62–2 = 0.96875 | **-0.96875** |

CR082 vs CR071M reward margin was also catastrophic: mean `-128488.703125`, median `-129738.5`, and even the best game remained `-72758`.

Frozen requirements were direct score rate >= 0.5625, aggregate guardrail delta >= 0, and every individual guardrail delta >= -0.0625. CR082 fails all strategic requirements decisively.

Frozen decision:

`CLOSE_CR082_1NN_MOVE_TO_EXPLICIT_ECONOMIC_VALUE_MODEL`.

## Interpretation

CR082's strict-forward Gate A had shown that same-step state-conditioned 1-NN predicted Majkel's market queue materially better than a step-only modal baseline. Yet transplanting those correctly predicted market actions onto CR071M's physical/economic backbone lost every game in the exact reference panel.

Therefore **behavioral predictability is still not economic value**. Conditioning on a richer current state solved temporal aliasing enough to predict the teacher, but it did not solve policy compatibility or causal utility for CR071M.

This closes same-step nearest-neighbor teacher imitation for this validation generation. No change to `k`, features, OOD percentile, prefix, teacher subset, or teacher identity may be tuned on master `9120821`.

## Successor

CR083 is activated under `CR083_EXPLICIT_VALUE_ARCHITECTURE_BOUNDARY_2026-09-12.md` and `CR083_PHASE0_MECHANICS_RESULT_2026-09-12.md`.

The required representation is explicit mechanics-derived economic value under legal current observation. Exact simulator branching may be used offline for causal research, but hidden seed/future information is forbidden as a runtime feature or clairvoyant target shortcut.

No hosted CR082 submission is permitted.