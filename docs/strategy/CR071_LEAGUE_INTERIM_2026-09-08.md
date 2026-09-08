# CR071 exact-reference league — interim findings (2026-09-08)

Run: `34276243787`
Branch: `fix/kaggle-parity-v1`
Reference: `kaggle-environments==1.32.7`
Primary metric: seat-balanced W/L. Money margin is diagnostic only.

## Completed exact H2Hs relevant to the frontier

| A | B | A W-L-T | A score rate | Paired 95% CI | Interpretation |
|---|---|---:|---:|---|---|
| CR053 | CR061 | 23-41-0 | 0.359375 | [0.203125, 0.53125] | CR061 leads, unresolved at 32 paired seeds |
| CR053 | CR065 | 33-31-0 | 0.515625 | [0.34375, 0.6875] | essentially tied |
| CR053 | CR068A | 53-11-0 | 0.828125 | [0.6875, 0.9375] | CR053 decisive |
| CR053 | CR068B | 46-18-0 | 0.718750 | [0.5625, 0.875] | CR053 decisive |
| CR053 | CR070A | 29-35-0 | 0.453125 | [0.28125, 0.625] | CR070A leads, unresolved |
| CR061 | CR065 | 6-58-0 | 0.093750 | [0.000000, 0.21875] | CR065 decisive |
| CR061 | CR068A | 64-0-0 | 1.000000 | [1.0, 1.0] | CR061 decisive |
| CR061 | CR068B | 64-0-0 | 1.000000 | [1.0, 1.0] | CR061 decisive |
| CR061 | CR070A | 1-63-0 | 0.015625 | [0.000000, 0.046875] | CR070A decisive |
| CR065 | CR068A | 64-0-0 | 1.000000 | [1.0, 1.0] | CR065 decisive |

The league is strongly non-transitive. CR061 can beat CR053 yet is almost swept by both CR065 and CR070A. Therefore no single-opponent H2H is a valid promotion gate.

## Provisional Bradley–Terry before CR065 vs CR070A

Using only the completed edges above plus the completed CR053 edges, provisional centered ratings were approximately:

- CR070A: +272
- CR065: +223
- CR053: +77
- CR061: +57
- CR068B: -248
- CR068A: -381

This is explicitly provisional because the round robin is incomplete and CR070A/CR065 still lack their direct edge.

## CR061 and CR070A are mostly redundant against CR053

On the same 32 paired seeds, CR053 paired-seed scores against CR061 and CR070A have correlation about **0.715**.

Categorizing each seed by whether the alternate candidate beats CR053:

- both CR061 and CR070A beat CR053: 16 seeds;
- only CR061 beats CR053: 4 seeds;
- only CR070A beats CR053: 1 seed;
- neither beats CR053: 11 seeds.

This weakens the hypothesis that CR061 and CR070A occupy cleanly complementary exogenous regimes.

## CR061 vs CR070A exact forensic subset

Forensic run `34277950457` used 12 paired seeds / 24 games and is explanatory only. It produced CR061 1-23 CR070A. Reconstructing CR070A's own route branch from its visible-state conditions:

- MAIN: CR061 1-8;
- MILK_GLUT: CR061 0-10;
- YARN: CR061 0-3;
- YARN_CARROT: CR061 0-2.

Thus CR070A's advantage over CR061 is not isolated to one obvious internal route branch.

Important causal warning: shop/market observations differed across opponent matchups on the same master seed, so those states are at least partly endogenous to the trajectory. They must not be treated as pure exogenous selector labels.

## Full-agent switching between CR065 and CR070A is mechanically unsuitable

Direct comparison of the frozen action tapes shows:

- CR065 route 0 vs every CR070A route: first action divergence at step **1**;
- CR065 route 1 vs every CR070A route: first action divergence at step **1**.

Therefore a CR065↔CR070A selector cannot safely wait for late public evidence and then switch complete policies. Their physical/economic trajectories have already diverged almost immediately.

Internal route coherence is very different:

- CR065 route0 vs route1 first diverges at step 360;
- CR070A MAIN vs YARN first diverges at step 226;
- CR070A YARN vs YARN_CARROT first diverges at step 360;
- CR070A MAIN vs MILK_GLUT first diverges at step 577 (despite the branch being latched earlier).

### Consequence

CR071 should use the winner of the broad league as the backbone and test **small causal component transplants**. Do not build a late full-agent selector between CR065 and CR070A.

## Immediate decision still pending

The most informative remaining edge is **CR065 vs CR070A**. Do not submit either as a new CR071 derivative before that exact-reference H2H and the full round-robin summary are available.
