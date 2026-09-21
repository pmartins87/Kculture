# ALL3 V22A Fresh Current-Frontier Refresh — Binding Result — 2026-09-21

Workflow: **`35562142399`**  
Job: `106216902367`  
Launch commit: `2ee8c8a0c73b7c11ff0487c0ed8e1a7a2f36ae7f`  
Artifact: `all3-v22a-fresh-current-frontier`  
Artifact ID: `10623710178`  
Artifact digest: `sha256:56c2ee63e78c7e3389687ec5ece3a815a9bc190f41e731f4084324e5acf343f3`

Decision: **`V22A_FRESH_FRONTIER_HARD_POPULATION_READY`**.

## Mechanical result

- Top-30 query completed;
- acquisition failures: **0**;
- smoke failures: **0**;
- episode failures: **0**;
- selected unique executable representatives: **12**;
- expected games: **144**;
- completed games: **144**;
- mechanical pass: **true**.

The corrected strict mechanics gate passed exactly as pre-registered.

## Hard-population result

ALL3 non-win contexts:
- total: **92 / 144**;
- unique hard source SHAs: **8**;
- hard seeds: **6 / 6** (`79101..79106`);
- both seats were evaluated.

Frozen READY thresholds were:
- >=8 executable source SHAs;
- >=96 valid contexts;
- >=12 non-wins;
- non-wins across >=4 source SHAs;
- non-wins across >=3 seeds.

All thresholds passed with substantial margin.

## Per selected source

| Rank | Public ref | Games | Wins | Non-wins | Mean margin |
|---:|---|---:|---:|---:|---:|
| 1 | nathanjacob/kaggriculture-pipe16-idle-workers | 12 | 0 | 12 | -2951.17 |
| 2 | haodou092/notebookdb6965aa8e | 12 | 0 | 12 | -2951.17 |
| 4 | dmitriigluzdov/kaggriculture-one-more-wheat | 12 | 0 | 12 | -3000.67 |
| 5 | dmitriigluzdov/kaggriculture-a-smaller-market-shock | 12 | 2 | 10 | -2095.08 |
| 7 | thomastschinkel/the-metav4-farm-submission-v13 | 12 | 0 | 12 | -2892.67 |
| 11 | romantamrazov/kaggriculture-yummers | 12 | 0 | 12 | -2951.17 |
| 12 | hanifnoerrofiq/a-wonderful-life | 12 | 2 | 10 | -2095.42 |
| 13 | ahmedberatozer/kaggriculture-v38-smarter-feed-stronger-margins | 12 | 12 | 0 | 3941.17 |
| 14 | ahmedberatozer/kaggriculture-v39-ready-before-the-rush | 12 | 12 | 0 | 3470.00 |
| 15 | ahmedberatozer/kaggriculture-v34-observed-market-timing | 12 | 12 | 0 | 6600.25 |
| 16 | ahmedberatozer/kaggriculture-v53-opening-signature | 12 | 0 | 12 | -2917.08 |
| 17 | ahmedberatozer/kaggriculture-v41-review-candidate | 12 | 12 | 0 | 3636.67 |

## Binding hard-context artifact

The exact V22B population was materialized deterministically from all and only binding V22A rows with `score < 1.0`:

`configs/all3_v22b_hard_contexts.json`

Config commit:
`5c6058ed4fcc267242f0b654f06bd669fec1849b`.

The config contains:
- **92** hard contexts;
- **8** hard source SHAs;
- **6** hard seeds;
- exact source ref/SHA, seed, seat, BASE score and BASE margin for every context.

No context was selected or removed by looking at any V22B treatment.

## Consequence

V22B is activated under the already-frozen protocol:

`docs/strategy/ALL3_V22B_FRESH_FRONTIER_DOMAIN_UPPER_BOUND_PROTOCOL_2026-09-21.md`.

Frozen modes:
- BASE;
- MARKET_ONLY;
- PHYSICAL_ONLY;
- FULL_SHADOW.

No Kaggle submission is authorized by V22A.
