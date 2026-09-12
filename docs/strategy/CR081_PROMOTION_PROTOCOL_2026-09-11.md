# CR081 promotion protocol — frozen before H2H results

Candidate family is fixed by `CR081_GATE_A_RESULT_2026-09-11.md`. This protocol is frozen before any exact CR081-vs-anchor result is observed.

## Candidate

Exactly one CR081 implementation is allowed for this bridge experiment:

- exact CR071M source as base;
- route backbone delayed by one turn, with step 0 PASS;
- steps 0–287 market queue replaced by UMG development-only per-step modal market queue;
- original CR071M safety/repair logic retained;
- same-turn BUY_PRODUCT is credited before a later SELL while clamping the market queue, because the UMG step-1 mechanism explicitly uses buy -> buy -> sell in one queue;
- after step 287, continue the delayed CR071M backbone; no replay-route selection/stitching;
- no team name, episode ID, seed, future state or opponent-private feature.

The 288-step boundary was selected from **development-only** support: market modal support is 0.971 / 0.942 / 0.918 over the first three 96-step blocks and drops to 0.687 in the next block. It is not changed after H2H results.

Mechanical fixes are allowed only if the package fails to load or returns illegal/exception actions and must not change the strategic policy. A mechanically invalid run cannot be interpreted as policy evidence.

## Exact evaluation panel

Runtime: `kaggle-environments==1.32.7`, isolated package process, both seats.

Fresh master seed: **9120811**.

- 32 seeds x 2 seats = 64 games per H2H.
- Candidate direct: CR081 vs CR071M.
- Guardrails: CR081 vs CR053, CR061, CR065.
- Same-seed incumbents: CR071M vs CR053, CR061, CR065.

Seed firewall must verify no overlap with the earlier CR080 discovery/confirmation masters recorded in `experiments/CR080_MENGFEI_BRIDGE_2026-09-11/seed_firewall.json`, plus master 9112081.

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
