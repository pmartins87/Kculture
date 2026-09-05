# HANDOFF — Kculture

> **Current update — 2026-09-05:** Read [CR026_CONTINUATION](docs/CR026_CONTINUATION.md) first. CR024 submission 56025052 is near 1600; CR025 is rejected; CR026 Phase 0 finished 8-12. The continuation lists below are historical and superseded. Do not repeat CR008/CR015.

Use this file as the **first read in any new Kculture chat**.

## Mission

Compete seriously for a **top-10 Kaggriculture prize**. Final submission deadline: 2026-09-30 23:59 UTC. Repository `pmartins87/Kculture` is the source of truth and intentionally public.

The objective is prize probability, not elegance. Every idea is a hypothesis until evidence supports it.

## Mandatory first reads

1. `STATUS.md`
2. `ROADMAP.md`
3. `docs/PRIZE_FIRST_DECISION_POLICY.md`
4. `docs/SUBMISSION_LEDGER.md`
5. `experiments/KEXP-20260827-041-single-jit-carrot/README.md`
6. `experiments/KEXP-20260827-045-double-jit-carrot/README.md`
7. `experiments/KEXP-20260827-037-early-terminal-noninput-sell/README.md`
8. `experiments/KEXP-20260827-042-live-phase-strategy-atlas/README.md`
9. `official/UPSTREAM_LOCK.md`

Then inspect latest commits and GitHub Actions before changing code.

## Working rules

- Official engine facts outrank assumptions.
- W/L/T generalization is primary; money delta is secondary.
- Hosted/live evidence outranks local public-panel stories when they conflict.
- Cheap falsification before expensive implementation.
- Replay/team/seed identity is research metadata only, never a policy feature.
- Fresh-load file agents per episode.
- Changed code never inherits old validation.
- Development and exploratory pools are open; validation only after exact candidate freeze; held-out stays sealed.
- Never promote from replay correlation alone; controlled games test hypotheses.
- Hosted submission is a calibration resource for materially different, evidence-backed policies.
- Advance autonomously; surface material blockers/results.

## Hosted baseline and calibration failure

Frozen hosted champion: `R4B-market-only-validated-v1`.

- candidate `candidates/r4b_ablation_market_only.py`;
- blob `e564125f0c4a1711fd3ea065dc1cb27d4a62ce37`;
- modern public development panel: Kaito 25-7, Rayk 30-2, Andrew 26-6, combined **81-15 / 96**;
- validation run `32918640409`;
- package parity run `32919305800`;
- Kaggle status Complete / green check;
- visible hosted rating **161.6 → 135.7 → 110.5**.

Treat R4B as a reproducible baseline, not a likely final candidate. The local public panel is a regression control, not a calibrated live-field proxy.

## Key architecture diagnosis

Recent official top-agent trajectories are highly state-adaptive. COK/R4B is still strongly route/tape based. The main remaining difficulty is strategic long-horizon allocation under dynamic public state, not basic understanding of game rules or packaging.

KEXP-042 found major phase/composition differences between R4B and recent winners. R4B has much more midgame PASS, but KEXP-044 showed winners do not systematically use fewer PASS than losers, so generic labor utilization is not currently the primary intervention.

Replay alignment is frozen as: **state `t` -> action stored on frame `t+1`**. KEXP-028 reproduced 10/10 official top tapes exactly with this convention.

## Closed/deprioritized avenues

- fixed route swaps: no W/L improvement;
- ex-post route oracle: only 81-15 → 83-13, insufficient;
- terminal CARE reallocation: neutral;
- final-step FEED suppression: zero/small ceiling;
- naive terminal collector: 2-30 vs R4B;
- suppressing late WATER: false premise; nearly all audited WATER creates immediate yield;
- terminal SELL impact reordering: no promotion.

## Replicated small component — KEXP-037

Candidate `candidates/r4d_early_terminal_noninput_sell.py` sells eligible already-available non-input goods at state 717, after the final town-consumption tick and before terminal liquidation.

- development direct vs R4B: 13-11-8, score 0.53125;
- exploratory live-meta direct: **12-8-20**, score **0.55**, mean +32.2, zero errors.

Keep as an independent component for later combination. Do not submit alone.

## Primary line — state-adaptive CARROT allocation

### Evidence chain

- KEXP-026: no free/unreserved CARROT seed in 0/36 episodes; substitution must deliberately buy/reallocate seed.
- KEXP-034: safe late WHEAT and CARROT slots have equal same-route yield q=3 or q=2.
- KEXP-038: purchase-time comparative-value sign remained positive to harvest oracle in **234/234** sign-positive events.
- KEXP-040: one-step JIT rule `q*(Pc-Pw)-20 > 0` passed predeclared support/stability gate in both development and exploratory pools.

### KEXP-041 — first material R4D PASS

Candidate `candidates/r4d_jit_carrot_one.py`, blob `97e102933f96a85fcc586ec4a96500069902f035`.

Mechanism: state 614 conditionally buy one CARROT; state 615 convert one actual R4B WHEAT plant only if extra CARROT stock is observed.

Execution audit:

- 14/36 episodes trigger;
- 14/14 purchases commit;
- 14/14 exact +1 CARROT / -1 WHEAT conversions;
- zero false mutations/errors.

Development:

- modern public panel preserved exactly **81-15**;
- direct vs R4B **20-12**, score **0.625**, mean +53.53, zero errors.

Exploratory replication run **`33045892841`** is currently in progress on 20 live-meta environmental seeds × both seats.

### KEXP-045 — two-conversion escalation

Candidate `candidates/r4d_jit_carrot_two.py`, blob `9d199b3c263254805c64f122367afe180027afeb`.

Two bounded q=3 pairs: 614→615 and 619→620, same legal JIT value rule.

Development run **`33046361583`** is currently in progress. Predeclared direct gate: score >=0.5625, positive mean, zero errors and modern-panel preservation.

## Exact continuation logic

1. Poll KEXP-041 exploratory run `33045892841`.
2. Poll KEXP-045 development run `33046361583`.
3. If 041 exploratory score >0.50 with positive mean, retain it as validation-eligible baseline.
4. If 045 passes development, replicate 045 on exploratory live-meta environmental seeds; prefer 045 only if its evidence is at least as strong as 041.
5. Select stronger crop controller.
6. Combine selected crop controller with replicated KEXP-037 and test direct vs crop-only parent; keep combination only if it adds W/L or robust positive value without regression.
7. Freeze the best candidate and open **fresh exact validation**.
8. If validation passes, build exact package, run parity, then use next hosted submission as calibration of the materially different adaptive policy.
9. Keep held-out **32/32 sealed** until later final-selection stage.

## User action

At this moment the user needs to do **nothing manually**. GitHub Actions run remotely; the browser/PC need not remain open. Manual Kaggle action is only needed after a candidate passes exploratory replication, fresh validation and package parity.
