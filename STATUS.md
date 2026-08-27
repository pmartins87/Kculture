# STATUS — Kculture

Last updated: 2026-08-27

## Mission

**Goal: maximize probability of a top-10 final finish in Kaggriculture; each top-10 position pays US$5,000.**

Repository `pmartins87/Kculture` is the source of truth. R4B is now a reproducible hosted baseline, not a likely final candidate.

## Competition / hosted baseline

- R0 COMPLETE; R1 PASS; R2 PASS.
- R3 DELIVERY PASS / HOSTED CALIBRATION FAIL.
- Hosted champion: `R4B-market-only-validated-v1`.
- Frozen candidate: `candidates/r4b_ablation_market_only.py`, blob `e564125f0c4a1711fd3ea065dc1cb27d4a62ce37`.
- Modern public development panel: Kaito 25-7, Rayk 30-2, Andrew 26-6 = **81-15 / 96**.
- Kaggle package valid / Complete / green check.
- visible hosted rating progression: **161.6 → 135.7 → 110.5**.
- Package parity run `32919305800`: 4/4 exact trajectories.
- **Held-out 32/32 sealed.** Validation is still unopened for the current R4D branch.

Hosted weakness is treated as a real strategic/architecture failure. Recent official high-Elo replays are strongly state-adaptive, while COK/R4B remains route/tape dominated.

## Replay / laboratory correctness

- Replay convention is frozen: action selected from state `t` is stored on replay frame `t+1`.
- KEXP-026 corrected CARROT seed ledger: **0/36** episodes contain truly unreserved spare CARROT stock.
- KEXP-028: **10/10** sampled top tapes replay exact terminal rewards after alignment correction.
- Fixed replay tapes are not valid counterfactual opponents because changed market state makes the tape non-adaptive.
- Official daily high-Elo episode datasets remain primary live-meta evidence.

## Closed / deprioritized branches

- KEXP-017 route oracle: perfect ex-post route selection only improves 81-15 → 83-13; route-selector solver deprioritized.
- KEXP-024 terminal CARE: neutral vs R4B.
- KEXP-027 exact step-695 FEED: zero ceiling.
- KEXP-030 blanket late FEED suppression: rejected.
- KEXP-032 post-695 WATER suppression: rejected; WATER can create immediate yield.
- KEXP-033 naive terminal collector: 2-30 vs R4B; rejected.
- KEXP-035: 371/374 final WATER actions create immediate yield; most are valuable.
- KEXP-036 terminal SELL ordering: no promotion.
- KEXP-043 found large PASS headroom, but KEXP-044 showed lower PASS is not itself associated with winning. Generic dispatcher remains secondary.
- KEXP-049: 3,132 midgame HIREs audited; even hires costing >=89 average ~7.26 productive actions. Simple “remove expensive last hire” is rejected.

## Small replicated component — KEXP-037 terminal non-input liquidation

Candidate `candidates/r4d_early_terminal_noninput_sell.py`.

- development direct vs R4B: **13-11-8**, score 0.53125;
- exploratory live-meta: **12-8-20**, score **0.55**, mean delta **+32.2**;
- zero errors;
- modern public panel preserved.

Keep as a small independent component for later combination. It is not sufficient alone for hosted submission.

## Primary R4D line — state-adaptive crop value

### KEXP-038 — PASS

Equal-route WHEAT/CARROT mechanics support a public-state value rule. Across diagnostics, **234/234** sign-positive purchase states remained positive at later plant/harvest-price checkpoints.

### KEXP-040 — PASS

JIT extra-seed rule using current state only:

`q * (CARROT_price - WHEAT_price) - 20 > 0`

passed its support/stability diagnostics.

### KEXP-041 — DEVELOPMENT PASS / EXPLORATORY FAIL

Candidate `candidates/r4d_jit_carrot_one.py`, blob `97e102933f96a85fcc586ec4a96500069902f035`.

- mechanical execution: 14/14 intended conversions exact;
- modern development panel preserved at 81-15;
- direct development vs R4B: **20-12**, score **0.625**, mean +53.53;
- exploratory live-meta: **14-14-12**, score **0.50**, mean **-21.35**.

KEXP-046 paired-world causal audit explains the failure: on triggered development cases, mean own reward +89.5 / relative +77.9; on triggered live-meta cases, mean own reward **-49.6** / relative **-61.0**. The mutation itself fails to generalize. **NO VALIDATION / NO PROMOTION.**

### KEXP-045 — CROSS-DISTRIBUTION W/L PASS / HOLD

Candidate `candidates/r4d_jit_carrot_two.py`, blob `9d199b3c263254805c64f122367afe180027afeb`.

Two bounded JIT pairs: 614→615 and 619→620.

Mechanical KEXP-048 audit:

- 14/36 episodes trigger both pairs;
- 28/28 buy→plant handshakes exact;
- zero errors/state leakage.

Development:

- Kaito 25-7;
- Rayk 30-2;
- Andrew 26-6;
- combined **81-15**;
- direct vs R4B **22-10**, score **0.6875**, mean **+165.5**.

Exploratory live-meta, 20 seeds × both seats:

- **17-11-12**;
- score **0.575**;
- mean terminal delta **-1.05**;
- seat0 11-3-6; seat1 6-8-6;
- zero errors.

KEXP-051 paired-world causal audit shows the two conversions are strongly positive on development (triggered mean relative +240.73) but nearly neutral on live-meta (triggered mean relative -3.0). Therefore the positive live-meta W/L may contain substantial matchup variance. Candidate is held pending larger fresh-seed stress, not yet validation-frozen.

### KEXP-050 — CROSS-DISTRIBUTION POSITIVE / HOLD

Candidate `candidates/r4d_reallocate_614_carrot.py`, blob `61b77be136836328917441cb03f89bc6665c4c27`.

Instead of buying an extra CARROT for +20, replace one existing one-unit WHEAT seed buy at state 614 with CARROT in the same market slot. Incremental seed cost = +10.

Mechanical audit:

- development 4/16 exact reallocations;
- live-meta 6/20 exact reallocations;
- 10/10 conversions executed exactly;
- zero status errors.

Development:

- modern public panel exactly **81-15**;
- direct vs R4B **21-11**, score **0.65625**, mean **+103.97**.

Exploratory live-meta:

- **15-11-14**;
- score **0.55**;
- mean **+11.85**;
- zero errors.

050 has slightly weaker W/L than 045 in the small exploratory pool but positive mean value and lower intervention/cost. It remains a serious candidate pending KEXP-052.

## KEXP-052 — RUNNING / current promotion discriminator

Run `33069453972`.

Fresh deterministic exploratory distribution:

- 96 new seeds generated from master `202608270052`;
- excludes every frozen development, validation, held-out seed and the prior live-meta exploratory pool;
- both seats;
- **192 games for KEXP-045 and 192 games for KEXP-050** in parallel.

Predeclared gate per candidate:

- zero errors;
- overall W/L/T score >= **0.53**;
- mean terminal delta > 0;
- each seat score >= **0.48**.

If both pass and overall score differs by <0.01, prefer KEXP-050 for lower intervention/cost. Passing authorizes exact freeze + fresh validation. Held-out remains sealed.

## Live-meta architecture signals beyond CARROT

KEXP-047 same-episode winner-vs-loser radar across Aug-24/25/26 found temporally consistent patterns:

- winners have much more money by checkpoints 576/648/696;
- winners SELL more WHEAT during 192-575 but less WHEAT late;
- winners BUY fewer WHEAT seeds in 384-647;
- winners BUY more CARROT in 576-647;
- winners BUY more TOMATO seed in 384-575 and hold more TOMATO at checkpoints 576/648/696;
- winners buy/hold more SHEEP in early/midgame;
- winners HIRE fewer hands in 192-383, but KEXP-049 shows simply deleting expensive hires from R4B is not justified.

Interpretation: the likely prize-grade architecture is a dynamic capital/production allocator, not merely a larger fixed tape.

## KEXP-053 — RUNNING / TOMATO physical feasibility

Run `33069678715`.

TOMATO needs ~192 turns before first yield. Audit every R4B WHEAT/CARROT plant in states 240-527 across 16 development + 20 exploratory seeds, pairing it with next same-tile HARVEST and maintenance.

Gate: at least 4 development and 5 exploratory episodes must contain a >=192-turn natural slot before a wrapper-style TOMATO candidate is allowed. If gate fails, TOMATO requires physical-route/planning architecture rather than another local substitution wrapper.

## Exact continuation

1. Poll KEXP-052 first. Apply its predeclared gate exactly.
2. If one candidate passes decisively, freeze it and open a **fresh exact validation**. If neither passes, do not spend validation.
3. If 045 and 050 are effectively tied, prefer 050 by predeclared lower-intervention rule.
4. Poll KEXP-053 and classify TOMATO as wrapper-feasible vs planner-required.
5. Only after crop-candidate selection, test combination with independent KEXP-037 terminal liquidation.
6. New hosted submission is allowed after exact fresh validation + package parity; it is a calibration submission of a materially different state-adaptive policy.
7. Keep all **32/32 held-out sealed** until later promotion/final selection.

## Frozen environment facts

- `kaggle-environments==1.32.7`;
- official engine commit `28b6d8af3ce73926b3d0fda1410c1ddd8384ab8c`;
- 720 recorded states; state 718 is the final executable action;
- terminal reward is farm money;
- state/action replay alignment: `state t -> frame t+1 action`;
- W/L/T is primary for ladder/final tournament relevance; money margin is diagnostic/secondary.
