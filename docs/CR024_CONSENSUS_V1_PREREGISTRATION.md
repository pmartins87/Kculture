# CR024_CONSENSUS_V1 — preregistration

Date: 2026-09-01

## Purpose

Turn the strong CR023/CR024 raw-top19 signal into a materially new, self-contained candidate without the failed dynamic WOOL guard.

## Frozen candidate

`CR024_CONSENSUS_V1` is the deterministic public-tape composition:

- canonical action shell / farmer component: `top19_openloop`;
- `hands`: `top11_openloop`;
- `market`: `top19_openloop`;
- no opponent identity;
- no seed input;
- no submission identity;
- no dynamic guard;
- no CR008 adaptive overlay in this candidate;
- no runtime network access in the eventual package.

The Stage-A component decomposition showed `h11_m19` matched raw top19 W/L on all 168 already-open rows while improving mean margin by about +40.36; the reverse composition degraded two rows. This document freezes `h11_m19` before any reserved validation is opened.

## Fresh validation block

Use exactly `adaptive_overlay_stage_a_seeds_reserved` from `configs/cr023_public_tape_preregistered_seeds_v1.json`, both seats, against the seven currently reproducible frozen opponents:

- kaito_sparse
- prvsiyan
- salem
- rayk
- tactical
- boatlee
- andrew

`tetsu` and `kaito_future` are excluded only because their exact Kaggle notebook outputs currently return HTTP 403; no replacement opponent is selected after seeing results.

Expected rows: 7 opponents × 12 seeds × 2 seats = 168.

Controls, evaluated on the exact same rows:

1. frozen CR008;
2. raw top19 tape;
3. frozen CR024_CONSENSUS_V1.

The 32/32 final held-out seeds remain sealed. `adaptive_overlay_stage_b_seeds_reserved` remains unopened.

## Frozen promotion gate

Mechanical requirements:

- 168/168 paired rows complete;
- zero agent/runtime errors;
- all final statuses DONE.

Against CR008:

- total score gain >= +12 points across 168 rows;
- net favorable W/L conversions >= +12;
- mean margin gain > 0;
- unfavorable conversions <= 10.

Against raw top19:

- consensus total score difference >= -2 points;
- consensus mean margin difference >= -500;
- consensus must not create more than 4 additional unfavorable W/L outcomes versus raw top19.

Decision:

- if every condition passes: `CR024_CONSENSUS_V1_PASS__BUILD_PACKAGE`;
- otherwise: `CR024_CONSENSUS_V1_FAIL__DO_NOT_SUBMIT`.

No threshold or component change is allowed after viewing this reserved block. A failed candidate is retired or replaced by a separately preregistered strategy.
