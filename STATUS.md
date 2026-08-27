# STATUS — Kculture

Last updated: 2026-08-27

## Mission

**Goal: maximize probability of a top-10 final finish in Kaggriculture; each top-10 position pays US$5,000.**

Repository `pmartins87/Kculture` is the source of truth for code, experiments, hashes, Actions evidence, validation discipline, hosted submissions and continuation state.

## Competition / hosted baseline

- R0 COMPLETE; R1 PASS; R2 PASS.
- R3 DELIVERY PASS / HOSTED CALIBRATION FAIL for the original R4B submission.
- Current hosted baseline: `R4B-market-only-validated-v1`.
- R4B candidate: `candidates/r4b_ablation_market_only.py`, blob `e564125f0c4a1711fd3ea065dc1cb27d4a62ce37`.
- Visible hosted rating progression: **161.6 → 135.7 → 110.5**.
- R4B package itself is valid; package parity was exact. Hosted weakness is therefore treated as real strategic/calibration evidence.
- **Held-out remains 32/32 sealed.**

## Current promoted R4D calibration candidate — KEXP-050

Candidate: `candidates/r4d_reallocate_614_carrot.py`  
Frozen blob: `61b77be136836328917441cb03f89bc6665c4c27`.

Mechanism: at state 614, only when public market value satisfies

`3 * (CARROT_price - WHEAT_price) - 10 > 0`

and frozen R4B itself submits a one-unit WHEAT seed buy, replace that same market slot with one CARROT seed. At state 615, convert exactly one actual R4B WHEAT plant to CARROT only if observed seed stock proves the substituted CARROT purchase arrived. Incremental seed cost is +10; no seed/team/opponent identity is used.

### Open-data evidence

- mechanical execution: **10/10** intended reallocations and conversions exact, zero errors;
- development modern public panel: exact R4B preservation **81-15**;
- development direct vs R4B: **21-11**, score **0.65625**, mean +103.97;
- exploratory live-meta direct: **15-11-14**, score **0.55**, mean +11.85;
- KEXP-052 fresh independent stress, 96 unseen exploratory seeds × both seats: **87-47-58 / 192**, score **0.6041667**, mean +41.24, seat scores 0.59896 / 0.60938, zero errors.

KEXP-045 tied KEXP-050 at exactly 0.6041667 in KEXP-052. The predeclared tie-break selected KEXP-050 because it changes fewer actions and has lower incremental capital cost.

## KEXP-054 — FRESH VALIDATION PASS

Frozen validation experiment: `experiments/KEXP-20260827-054-kexp050-fresh-validation/README.md`.

First run `33073158744` was a **mechanical null**: a development-only runner refused `partition=validation` before any episode ran; no validation outcome was observed.

Correct validation run: **`33073517302`**, using the repository's approved `tools/run_tournament.py` with exactly the frozen 16 validation seeds × both seats.

Direct KEXP-050 vs R4B:

- **14-8-10 / 32**;
- score **0.59375**;
- mean money delta **+31.0625**;
- zero errors.

Validation public-opponent regression panel:

| Family | KEXP-050 | R4B control |
|---|---:|---:|
| Kaito V27 | 25-7 | 25-7 |
| Rayk V11 | 32-0 | 32-0 |
| Andrew V12 | 21-11 | 21-11 |
| Combined | **78-18** | **78-18** |

Predeclared gate: direct score >=0.53125, positive direct mean delta, zero errors, combined public panel not worse than R4B, no family down >1 win. **Every clause PASS.**

Validation is now consumed evidence for this frozen KEXP-050. Do not tune KEXP-050 against individual validation outcomes.

## Formal self-contained package — PASS

Preparation parity run `33073890448`:

- 8/8 development seat/seed comparisons have identical full action trajectories;
- all terminal rewards/statuses identical;
- deterministic archive SHA-256 `59a45adf283f2f4dd1f9272150786c014585aa08c9b31b3348cf992ebe3bb64c`.

Formal post-validation package run: **`33074434495`**.

Formal filename:

`Kculture_KEXP050_reallocate614_validated_v1_submission.tar.gz`

Frozen identities:

- archive bytes: **102524**;
- archive SHA-256: **`59a45adf283f2f4dd1f9272150786c014585aa08c9b31b3348cf992ebe3bb64c`**;
- packaged `main.py` SHA-256: **`10b904ef9c26c7e87462e1f033c8e6d92bee5984e96a23e67a18804f3034e2d9`**.

The formal workflow independently rechecks candidate/source hashes, KEXP-054 promotion record, deterministic archive identity and exact full-trajectory package parity before upload.

**Next hosted action: submit this exact archive to Kaggle as a calibration candidate.** It is not declared the final champion. Its purpose is to test whether a disciplined state-adaptive improvement that generalizes locally also improves the real hosted field, where R4B calibration failed severely.

## Architecture diagnosis

The central gap remains strategic adaptivity. Official recent high-Elo episodes show state-dependent production/capital allocation, while R4B remains strongly route/tape based. A one-step CARROT reallocation passing local validation does not erase the enormous R4B hosted gap; hosted KEXP-050 evidence is now essential.

Important closed/falsified simplifications:

- route-oracle over existing variants has low ceiling (KEXP-017);
- terminal CARE neutral (KEXP-024);
- exact step-695 FEED zero ceiling (KEXP-027);
- blanket late FEED suppression rejected (KEXP-030);
- post-695 WATER suppression false; WATER creates immediate yield (KEXP-032/035);
- naive terminal collector rejected (KEXP-033);
- generic PASS elimination unsupported by winner-vs-loser data (KEXP-043/044);
- deleting expensive HIREs unsupported: KEXP-049 audited 3,132 hires and high-cost hands still performed substantial productive work.

Small independent KEXP-037 terminal non-input liquidation remains replicated but not yet combined with the frozen KEXP-050 package.

## Next-generation branch — TOMATO / portfolio allocation

KEXP-047 live winner-vs-loser radar showed consistent broader portfolio differences: winners use less late WHEAT, more late CARROT, more TOMATO in midgame, more SHEEP in early/midgame, and different capital/labor allocation.

### KEXP-053 — physical TOMATO feasibility PASS

Across 2,128 R4B midgame plant events, 32 WHEAT slots had a same-tile HARVEST >=192 turns later, enough for TOMATO's first production. These occurred in 4/16 development and 6/20 exploratory episodes.

Recurring long slots:

- state 262 `(0,4)`, delay 281;
- state 310 `(9,7)`, delay 398;
- state 334 `(5,9)`, delay 356;
- state 381 `(0,2)`, delay 213;
- state 451 `(7,3)`, delay 229;
- state 477 `(0,9)`, delay 211.

### KEXP-055 — succession audit PASS for bounded route

Run `33073812783`, artifact `9647111604`.

- 26/32 long slots have **no future same-tile PLANT** after the audited HARVEST;
- 6/32 conflict, all the exact same structural slot: state 381 `(0,2)`, HARVEST 594 → WHEAT PLANT 595;
- conflict fraction 18.75%, below the predeclared 25% routing threshold.

Decision: a bounded TOMATO development experiment may use the five non-conflicting slot families. Exclude state381 `(0,2)` unless explicit tile-release logic is added.

## Exact continuation

1. User submits the exact formal KEXP-050 archive to Kaggle.
2. Record submission timestamp/description and hosted score/episodes in `docs/SUBMISSION_LEDGER.md` as they appear.
3. Treat KEXP-050 hosted performance as calibration evidence; do not declare success from local validation alone.
4. While hosted episodes accumulate, continue R4D development on bounded TOMATO/portfolio allocation using only development + exploratory evidence.
5. Do not combine KEXP-037 or alter KEXP-050 under the already-consumed validation result; any changed candidate must earn its own fresh validation decision.
6. Keep all **32/32 held-out sealed** for later promotion/final selection.
7. Continue monitoring official live-meta episodes; prioritize value/allocation mechanisms that can explain both hosted and local behavior.

## Frozen environment facts

- `kaggle-environments==1.32.7`;
- official engine commit `28b6d8af3ce73926b3d0fda1410c1ddd8384ab8c`;
- 720 recorded states; state 718 final executable action;
- terminal reward is farm money;
- replay alignment: `state t -> action frame t+1`;
- W/L/T is primary for leaderboard/final Bradley-Terry relevance; money margin is diagnostic/secondary.
