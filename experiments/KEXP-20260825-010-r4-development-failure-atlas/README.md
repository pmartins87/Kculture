# KEXP-20260825-010 — R4 development failure atlas

## Purpose

Build a higher-resolution failure map for the frozen `R4B-market-only-validated-v1` candidate before attempting another strategy modification.

This is **development-only diagnostic evidence**. It does not reopen or extend the completed validation claim and cannot promote a changed candidate by itself.

## Frozen candidate

- path: `candidates/r4b_ablation_market_only.py`
- Git blob: `e564125f0c4a1711fd3ea065dc1cb27d4a62ce37`
- status: `R4B-market-only-validated-v1`
- hosted package SHA-256: `19cc08d2b3bcb8f8f947806c0ee01f4d7643d36f0c15abe0a978129ed1c53117`

## Opponent panel

1. R4A / COK V8 — direct base-regression control.
2. Seyamalam V21 — independent mixed-farm architecture.
3. Kaito public V18 / C20 exact-replication mirror — third attributed public family.

All third-party artifacts are hash-pinned in `configs/public_opponents.json` and fetched through `tools/fetch_public_opponents.py`.

## Protocol

Use **all 16 frozen development seeds**, both candidate seats, `kaggle-environments==1.32.7`.

Candidate blocks:

- market-only vs R4A — 32 games;
- market-only vs Seyamalam V21 — 32 games;
- market-only vs Kaito V18 — 32 games.

Same-seed controls:

- R4A vs Seyamalam V21 — 32 games;
- R4A vs Kaito V18 — 32 games.

Total: **160 development games**.

Validation and all 32 held-out seeds remain sealed for this experiment.

## Execution

GitHub Actions run `32920250892` completed all five jobs successfully with zero runtime errors.

## Results

| Matchup | W-L-T | Score | Mean delta | Median | Min | Max | Errors |
|---|---:|---:|---:|---:|---:|---:|---:|
| Market-only vs R4A | **15-9-8** | **0.59375** | **+20.000** | 0 | -3,904 | +4,088 | 0 |
| Market-only vs Seyamalam V21 | **32-0-0** | **1.000** | **+20,004.0625** | +19,969 | +5,567 | +38,860 | 0 |
| Market-only vs Kaito V18 | **32-0-0** | **1.000** | **+19,739.000** | +18,575 | +5,575 | +39,362 | 0 |
| R4A vs Seyamalam V21 | 30-2-0 | 0.9375 | +18,704.875 | +18,945 | -1,365 | +38,860 | 0 |
| R4A vs Kaito V18 | 30-2-0 | 0.9375 | +18,439.96875 | +18,263.5 | -1,357 | +39,362 | 0 |

### External-family failure pattern

The R4A control's only losses against both Seyamalam and Kaito V18 occurred on development seed `583180324`, both seats. The market-only candidate flipped all four of those control losses into wins:

- vs Seyamalam: +5,567 / +5,597;
- vs Kaito V18: +5,575 / +5,605.

Across the full 16-seed development partition, the market-only candidate therefore has **zero losses** against both independent public families.

### Direct market-only vs R4A losses

The nine direct losses were:

- seed `150614441`, seat 1: `-215`;
- seed `1743398262`, seat 1: `-167`;
- seed `1743757108`, seat 1: `-218`;
- seed `918851422`, seat 0: `-3,904`;
- seed `163219477`, seat 0: `-58`;
- seed `1873301133`, seat 1: `-220`;
- seed `10278190`, seat 1: `-229`;
- seed `414859172`, seat 1: `-20`;
- seed `598340816`, seat 1: `-70`.

These raw seat-level losses are mostly paired mirror effects. Summing both seats of each seed gives the following paired-seed deltas versus R4A:

- 11 / 16 seeds: exactly `0`;
- seed `724229404`: `+192`;
- seed `918851422`: `+184`;
- seed `1793968273`: `+32`;
- seed `163219477`: `+150`;
- seed `1422177419`: `+82`.

**No development seed has a negative paired-seat aggregate.** Total paired advantage is `+640`, equal to the observed `+20` mean across 32 games.

This is important because the largest single loss (`-3,904` on seed `918851422`, seat 0) is paired with a `+4,088` win in seat 1 on the same seed, for a net `+184` rather than a true seed-level regression.

## Diagnostic conclusion

**ATLAS COMPLETE — CURRENT PANEL SATURATED.**

1. The market-only intervention remains a very low-risk improvement over its COK base: paired-seat aggregate is non-negative on every development seed.
2. It completely eliminates the only COK losses observed against Seyamalam V21 and Kaito V18 and reaches 32-0 against both on the full development partition.
3. Therefore these two external opponents no longer expose actionable weaknesses. Further tuning against them would risk overfitting a saturated panel.
4. The next engineering stage should raise opponent strength toward the current public meta before introducing another strategy mutation.
5. Fresh public-meta evidence points toward **coherent midgame continuation / labor / market execution after roughly step 160** as a higher-value research family than another terminal micro-optimization. See `research/PUBLIC_META_CONTINUATION_20260826.md`.
6. A naive late switch between unrelated full policies remains ruled out by the earlier prefix-divergence result; any new continuation must be compatible with its opening/state assumptions.

## Decision

This experiment has no promotion gate and promotes no changed code. `R4B-market-only-validated-v1` remains the frozen hosted-submission candidate unchanged.

The next task is **stronger-opponent acquisition / continuation research**, followed by a new separately identified development candidate only when there is a concrete failure pattern or mechanically justified continuation hypothesis.

Validation is not reopened. Held-out remains sealed **32/32**.
