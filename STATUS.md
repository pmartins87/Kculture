# STATUS — Kculture

Last updated: 2026-08-29

## Mission

**Goal: maximize probability of a top-10 final finish in Kaggriculture; each top-10 position pays US$5,000.**

Repository `pmartins87/Kculture` is the source of truth. Hosted/live evidence outranks local proxy stories when they conflict.

**Held-out remains 32/32 sealed.**

## Hosted reality — 2026-08-29 calibration

Frozen snapshot and interpretation: `docs/HOSTED_CALIBRATION_2026-08-29.md`.

Latest observed Kaggle UI snapshot:

- R4B_A control: **205.9**;
- CR008 adaptive append: **1705.6**;
- CR011 adaptive early: **1723.3**;
- R4B_B byte-identical repeat, submission `55868963`: **188.4**;
- Kaito V43 public reference, submission `55868969`: **1211.7**.

Scores drift while episodes accumulate; these are snapshots, not immutable ratings.

Key calibration:

- R4B temporal-control spread = **17.5**;
- CR011 − CR008 = **17.7**, therefore noise-scale in this window;
- CR008 − R4B midpoint = **+1508.45**;
- CR011 − R4B midpoint = **+1526.15**.

**Decision:** CR008 append adaptation is now the canonical hosted adaptive baseline. The opponent-aware sale response has a very large real hosted signal; early queue placement has no demonstrated hosted advantage beyond measured temporal noise.

## Frozen candidates

### R4B — weak deterministic control

- `candidates/r4b_ablation_market_only.py`
- blob `e564125f0c4a1711fd3ea065dc1cb27d4a62ce37`
- role: temporal/control baseline, not final-strength candidate.

### CR008 — canonical hosted baseline

- `candidates/cr008_adaptive_frontrun.py`
- blob `8e1c26202c3101c19668bf61edf2ae51d4329d5d`
- high-confidence public-opponent-state forecast;
- appends same-turn CARROT/STRAWBERRY sales;
- hosted score ~1705.6 in latest 29-Aug snapshot.

### CR011 — causal research arm, not current promotion choice

- `candidates/cr011_adaptive_early_order.py`
- blob `c4f1cb79f3c20b8229ab09e00a6878289cf9648d`
- same adaptation as CR008 but prepends adaptive sale.

CR014B decomposition on 16 affected close-match rows showed:

- adaptation CR008 vs R4B: no W/L flips in the critical five;
- early order CR011 vs CR008: four catastrophic W→L flips and one L→W flip;
- catastrophic early-order mean relative effect: about **-2441**;
- favorable case: about **+393**.

Because hosted CR011−CR008 is only noise-scale, CR008 is preferred.

### CR015 — VALIDATED / HOSTED ELIGIBLE

- `candidates/cr015_liquidation_phase_early_order.py`
- blob `fabd4bc398e7eadcfd1d44add4d0e593315140e8`
- 432 fresh preregistered pairs across Stage A+B;
- zero errors;
- vs R4B combined mean relative gain **+149.62**;
- favorable W/L changes **2**, unfavorable **0**;
- package parity 28,760 states / zero mismatches;
- official Kaggle entrypoint PASS both seats.

Hosted-ready archive SHA256: `41d35a97ebe714a3cb71506e17ec1e629b4a9628cacd688be7e79d524fd75c54`.

### CR020 — REJECTED

Stage A: 216/216, zero mechanical errors. It had one favorable / zero unfavorable W/L changes vs R4B, but regressed against CR015 by mean relative **-70.84/game**. Frozen gate failed; no Stage B and no hosted slot.

## Opponent-adaptation evidence chain

- CR004: public opponent state improves OOT prediction; median error improvement **7.10%**.
- CR005: strong four-turn SELL forecasts.
- CR006: broad low-threshold reaction failed on precision.
- CR007: high-confidence CARROT/STRAWBERRY triggers reached **97.3%** combined precision.
- CR008: append adaptation produced the major hosted breakthrough.
- CR009: prediction timing already correct.
- CR010: in-turn order has large economic causal value.
- CR011: early placement improves money in some local panels but creates severe boundary pathologies.
- CR012/013/014/014B/014C: localized those pathologies to early queue placement and state trajectory, not opponent identity.
- CR015: smallest validated placement refinement, hosted eligible.
- CR020: monotone latch rejected by preregistered comparison to CR015.

## CR016 — production-demand architecture signal

Diagnostic only, 54 episodes, engine 1.32.7, zero errors.

High-price demanded states:

- TOMATO: **644**, self producer zero **100%**, both producers zero **100%**;
- EGG: **370**, self producer zero **100%**, both zero **100%**;
- CARROT: **712**, self producer zero **63.1%**.

TOMATO is the first production-response target because it can be tested as a small crop substitution. EGG requires a larger goose/coop/feed branch and remains separate.

Public research independently shows recent Apache-2.0 agents using unlocked town shops as forward demand signals and sparse material-gap crop switching. We reuse the idea, not their implementation.

## CR021 — ACTIVE: sparse TOMATO response

Preregistration: `docs/CR021_PREREGISTRATION.md`  
Fresh seeds: `configs/cr021_demand_response_preregistered_seeds_v1.json`  
Candidate: `candidates/cr021_sparse_tomato_demand.py`  
Candidate blob: `467a56643e70f018b9a11e82bc5138c30a2a7307`  
Stage A workflow run: **33261563880**.

Frozen intervention:

- CR008 base everywhere;
- at state 309, buy one TOMATO seed only under strong public town demand, TOMATO price >=90, no existing own TOMATO, free market slot, and a mechanically visible approach to the audited `310@(9,7)` planting slot;
- at state 310, replace only that exact WHEAT plant if the extra seed actually arrived;
- later replace WATER→HARVEST only on that exact diverted tile when TOMATO `yield_units >= 4`.

Stage A uses 12 completely fresh seeds × 9 exact current-meta opponents × both seats = **216 pairs**. Stage B has 12 separately frozen seeds and is forbidden unless the unchanged candidate passes Stage A.

## Next hosted-reset policy

Five valid daily slots are treated as a perishable information budget.

Provisional next-window design:

1. CR008_A exact control;
2. CR015 fixed;
3. CR021 only if its preregistered Stage A/B evidence authorizes it;
4. CR008_B exact control;
5. a separately frozen high-information arm chosen before partial scores can bias the decision.

Do not use CR020. Do not spend a slot on CR011 merely because its current score is ~17.7 above CR008.

## Exact continuation

1. Finish CR021 Stage A run `33261563880` and read the frozen gate.
2. If PASS, run Stage B unchanged; if FAIL, kill CR021A without threshold rescue on the same seeds.
3. If Stage B passes, build exact hosted package/parity before using a Kaggle slot.
4. Keep researching sparse demand-response mechanics; evaluate EGG only as a separate architecture after TOMATO is resolved.
5. Maintain CR008 bracket controls around future hosted experiments.
6. Keep all 32/32 held-out sealed.

## Frozen environment facts

- `kaggle-environments==1.32.7`;
- official terminal reward = own bank money;
- winner is determined by relative final bank balance;
- final competition ranking is Bradley–Terry/matchup based;
- market/town economy is shared and market-order sequence is economically causal;
- W/L conversion and broad matchup coverage outrank isolated coin-margin optimization.
