# CR081 promotion protocol — corrected runtime-aligned freeze

Candidate family is fixed by `CR081_GATE_A_RESULT_2026-09-11.md`. The strategic gate thresholds remain exactly those frozen before H2H. This revision corrects a replay-storage indexing error discovered before any valid CR081 H2H result was interpreted.

## Invalid first implementation

Run `34671122716` is **INVALID / SUPERSEDED**. It incorrectly interpreted replay action index `s` as runtime step `s`, which caused it to delay the CR071M physical backbone by one turn. Kaggle replay `steps[s].action` actually corresponds to runtime step `s-1`. No strategic result from run `34671122716` may be used.

The corrected implementation is evaluated on a new, non-overlapping seed master.

## Correct candidate

Exactly one corrected CR081 implementation is allowed for this bridge experiment:

- exact CR071M source as base;
- **CR071M physical/runtime backbone remains same-step and unchanged**;
- runtime steps 0–287 market queue is replaced by UMG development-only per-step modal market queue learned from replay action indices 1–288;
- original CR071M safety/repair logic retained;
- same-turn BUY_PRODUCT is credited before a later SELL while clamping the market queue, because the UMG runtime-step-0 mechanism explicitly uses buy -> buy -> sell in one queue;
- after runtime step 287, use normal same-step CR071M behavior; no replay-route selection/stitching;
- no team name, episode ID, seed, future state or opponent-private feature.

The 288-runtime-step boundary was selected from development-only evidence. Runtime-aligned market modal support is approximately 0.970 / 0.942 / 0.914 over the first three 96-step blocks and drops to ~0.683 in the next block. It is not changed after H2H results.

Mechanical fixes are allowed only if the package fails to load or returns illegal/exception actions and must not change the strategic policy. A mechanically invalid run cannot be interpreted as policy evidence.

## Exact evaluation panel

Runtime: `kaggle-environments==1.32.7`, isolated package process, both seats.

Corrected fresh master seed: **9120812**.

- 32 seeds x 2 seats = 64 games per H2H.
- Candidate direct: CR081 vs CR071M.
- Guardrails: CR081 vs CR053, CR061, CR065.
- Same-seed incumbents: CR071M vs CR053, CR061, CR065.

Seed firewall must verify no overlap with earlier CR080 masters **and with invalid CR081 master 9120811**.

## Frozen promotion gate

All checks must pass:

1. complete 7-H2H panel, exactly 64 games / 32 fresh seeds each;
2. zero agent errors and zero non-DONE games;
3. CR081 direct score rate vs CR071M >= **0.5625**;
4. aggregate guardrail delta `sum(score(CR081, guard) - score(CR071M, guard)) >= 0`;
5. every individual guardrail delta >= **-0.0625**.

Primary metric is seat-balanced W/L score rate. Reward margin is diagnostic only.

## Decision tree

- **PASS:** freeze exact candidate hash, perform active-slot accounting, then submit exactly one hosted CR081 probe. Do not delay a qualified candidate for optional local tuning.
- **FAIL:** close this CR081 bridge implementation. Do **not** create CR081A/B/C by moving the 288 boundary, changing support thresholds, editing individual market quantities or retuning on these seeds. Advance to the predeclared state-adaptive macro-economic policy using current-frontier corpora.

Original final holdout remains sealed. No automatic Kaggle submission is part of this workflow.
