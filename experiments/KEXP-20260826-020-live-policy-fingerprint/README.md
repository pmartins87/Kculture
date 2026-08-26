# KEXP-20260826-020 — live top-policy determinism fingerprint

Status: **PREDECLARED / OBSERVATIONAL ONLY**

## Prize-first question

Are the current top-ladder agents mostly deterministic route tapes / low-dimensional branches, or do their actions vary substantially with live state?

This matters because the highest-value response differs:

- if top policies are highly repetitive, replay-derived route reconstruction/generalization may be a cheap high-ceiling strategy;
- if they are strongly state-dependent, cloning a few trajectories is likely brittle and dynamic policy/search work has higher value.

No agent code is changed by this experiment.

## Data

Official public Kaggriculture Episode datasets only. Initial screen uses the same 2026-08-25 top-20 band as KEXP-018, selected by official `avg_score`.

Raw episode JSONs are temporary. Only compact similarity/fingerprint statistics are preserved.

## Canonical action fingerprint

For each team-labelled player trajectory:

- canonicalize each submitted action dict with sorted JSON keys;
- compare actions at identical step numbers across episodes of the same team;
- compute full-trajectory hashes;
- compute pairwise exact-action agreement in windows:
  - 0-215;
  - 216-599;
  - 600-671;
  - 672-695;
  - 696-718;
- compute mean per-step modal agreement;
- group by first-three-shop prefix where sample count permits and recompute within-prefix agreement.

Team identity is a **research grouping label only** and is forbidden as a deployment feature.

## Predeclared interpretation

- **Very high repeatability:** mean exact-action agreement >= 0.90 within at least one repeated shop-prefix group over the core 216-599 window. Replay-route reconstruction becomes a serious research candidate.
- **Moderate repeatability:** 0.65-0.90. Investigate which public/private state variables explain branch points before any imitation candidate.
- **Low repeatability:** <0.65. Deprioritize trajectory cloning and favor dynamic state-based strategy work.

A high overall agreement without same-shop-prefix support is not enough, because shared openings can inflate similarity.

## Guardrails

- public official Episodes only;
- observational, no strategy mutation;
- no validation or held-out seeds;
- no episode ID/team ID/opponent identity in deployable policies;
- do not reconstruct or submit a replay-derived agent until repeatability and generalization are demonstrated;
- W/L testing remains mandatory for any later candidate.
