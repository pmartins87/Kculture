# Live-meta demand-response diagnostic — 2026-08-26

## Executive conclusion

The first hosted Kculture submission is mechanically valid but its visible ladder score fell from 161.6 to **135.7**, while the frozen local current-public-agent panel remains 81-15 over 96 development games. Treat this as a calibration failure of the old benchmark set, not as evidence that the submitted archive is corrupt.

The highest-value new evidence comes from the **official public ladder episode datasets**, not from building a full solver or making another fixed-route tweak. Current high-Elo agents visibly use the complete late public shop state to alter crop allocation. CARROT is the clearest short-horizon response because it matures quickly and now has a scarcity-sensitive hinge price curve.

This finding is strong enough to justify a bounded R4D development experiment. It is **not** strong enough to justify a second hosted submission or validation access yet.

> Experiment-ID note: the demand studies were initially drafted under IDs that collided with an earlier KEXP-019. Their canonical IDs are now **KEXP-021** (same-day demand response) and **KEXP-022** (longitudinal replication). The original duplicate paths are historical aliases only.

## 1. Hosted/local contradiction

Frozen hosted champion:

- `R4B-market-only-validated-v1`;
- candidate blob `e564125f0c4a1711fd3ea065dc1cb27d4a62ce37`;
- hosted archive SHA-256 `19cc08d2b3bcb8f8f947806c0ee01f4d7643d36f0c15abe0a978129ed1c53117`;
- package parity run `32919305800`: 4/4 full trajectories identical;
- Kaggle status `Complete` / green check;
- visible score sequence **161.6 -> 135.7**.

Frozen local current-public-agent screen:

- Kaito V27: 25-7;
- Rayk V11: 30-2;
- Andrew V12: 26-6;
- combined 81-15 / score 0.84375.

This mismatch means the fixed public-agent panel is useful for regression testing but no longer sufficient as the primary model of the live field.

## 2. Solver hypothesis was tested and deprioritized

KEXP-017 compared three existing COK macro continuations with an ex-post oracle over 96 contexts:

- baseline R4B;
- default -> 10C/4S;
- default -> 6C/8S.

Even perfect future-aware branch choice moved the aggregate W/L only from **81-15 to 83-13**. Kaito and Andrew did not gain a single W/L; the two recovered losses were against Rayk.

Conclusion: a solver over the **current route library** has low headroom. Search/optimization remains a tool for well-defined subproblems, but it is not a prize-first project direction by itself.

## 3. Official live-meta radar

### KEXP-018

Tool: `tools/live_meta_radar.py`

Official source:

- `kaggle/kaggriculture-episodes-index`;
- daily dataset `kaggle/kaggriculture-episodes-2026-08-25`.

Top-20 episodes on Aug-25:

- daily episode count: 688;
- median episode avg Elo: ~2761.31;
- selected top Elo: ~3056.61 to 3069.55;
- 40 player-games.

Key winner averages:

- reward ~105k in the top-20 extended report;
- movement ~54%;
- productive actions ~42%;
- PASS ~4%;
- late herd reduction from step 672 to terminal ~5.8 animals versus ~1.25 for losers.

Late winner lifecycle:

- steps 672-695: almost no CARE (~0.05 mean), low FEED (~3.85), continued harvest/sales;
- steps 696-718: zero CARE and zero FEED.

The final farm shape is highly diverse. There is no evidence for one static herd template dominating the live top band.

## 4. Frozen COK lifecycle audit

Tool: `tools/inspect_cok_live_meta_gap.py`
Workflow: `.github/workflows/cok-live-meta-gap.yml`
Latest run: `33019622974` — SUCCESS.
Artifact `9625980030`, ZIP SHA-256 `09ceabc082093af71ceb46a8fa9f50fd567dac3a5b2c6683a154166f22b65afe`.
Exact COK source hash check passed:
`faf57412e2c56dcc669043865a185324bab9952d865abccc2203284e854eceb3`.

A tempting hypothesis was rejected: COK does **not** waste final-day actions on CARE/FEED. Its main route tapes also have CARE=0 and FEED=0 during 696-718.

A weaker lifecycle mismatch remains during 672-695, where COK uses around 8-9 CARE and 9-10 FEED in several routes while live winners use much less. This may matter, but it is not yet isolated enough to modify safely.

The larger structural gap is crop allocation.

Representative `10C4S` tape:

- 576-599: PLANT WHEAT 10, BUY_SEED WHEAT 10;
- 600-671: PLANT WHEAT 32 + CARROT 3; BUY_SEED WHEAT 32 + CARROT 3;
- 672 onward: no new planting.

First-Yarn route:

- 576-599: WHEAT 6;
- 600-671: WHEAT 28, CARROT 0.

Second-Yarn route:

- 576-599: WHEAT 10;
- 600-671: WHEAT 28, CARROT 1.

The route therefore already contains many late planting/movement slots that can support a bounded crop substitution without rewriting the spatial plan.

## 5. KEXP-021 — same-day demand response

Run `33019276166` — SUCCESS.
Artifact `9625868747`, ZIP SHA-256 `0a0c9028ce33b177b61a41fe4da691f6de6b7740c4729a0108ad4991e33dd821`.

At step 600, compute public CARROT demand weight as:

`2 * count(PET_CAFE) + count(FARMERS_MARKET)`

because PET_CAFE is a single-product shop and consumes twice per town tick.

Across 40 top-20 Aug-25 player-games:

- CARROT demand -> late CARROT seed-buy Pearson **+0.46156**;
- winners mean CARROT seed buy 600-671: **14.20**;
- losers: **2.95**;
- winners final-day CARROT sell: **50.95**;
- losers: **4.85**.

However, the sample was only Crop Dusta vs Ryo Hasegawa, so team identity was a severe confounder. No candidate was promoted.

Canonical record: `experiments/KEXP-20260826-021-live-meta-demand-response/README.md`.

## 6. KEXP-022 — longitudinal replication

Run `33019559986` — SUCCESS.
Artifact `9625961691`, ZIP SHA-256 `76ddbf8e2d453cdb357143002646e14c59fdbed054240089ef19968ce26a3963`.

Top-10 daily episodes for Aug-22, 23, 24, 25.

Demand -> late CARROT seed-buy Pearson:

- Aug-22: **+0.49505**;
- Aug-23: **+0.52212**;
- Aug-24: **+0.53413**;
- Aug-25: **+0.50326**.

This stability across days is the strongest evidence in the current frontier work. It demonstrates that strong live agents are systematically reacting to full late public demand.

It does **not** demonstrate that CARROT should always replace WHEAT. Winner means are mixed on Aug-23 and Aug-24, and there are demand-level counterexamples. The useful causal abstraction is:

> use the complete late economic state to decide crop rotation; CARROT is a fast-response option in high-CARROT-demand regimes.

A deployable policy likely needs demand plus current prices/economics, not a raw demand threshold.

Canonical record: `experiments/KEXP-20260826-022-live-meta-demand-longitudinal/README.md`.

## 7. Why CARROT is mechanically plausible

Frozen engine facts:

- CARROT first yield: 2 days;
- max yield: 3 days;
- WHEAT first yield: 2 days, max yield: 4 days;
- CARROT current price curve: `hinge` with strong scarcity gain;
- shop draws occur with replacement, so multiple PET_CAFE/FARMERS_MARKET instances can create unusual late scarcity;
- the complete eight-shop multiset is public by late season.

This makes late CARROT rotation one of the few crop interventions with enough time to mature and monetize before the terminal horizon.

## 8. Exploratory live-meta environmental seeds

`configs/exploratory_live_meta_seeds_20260825.json` freezes the 20 environmental seeds corresponding to the Aug-25 top-20 official episodes. These are a new **development-only** stress set.

Rules:

- they never replace or enter the frozen validation/held-out partitions;
- seed/episode/team identity are prohibited strategy features;
- they exist only to reproduce current high-Elo shop/randomness regimes in the official engine.

This is a better environmental calibration supplement than adding more hand-picked random development seeds.

## 9. Prize-first R4D recommendation

Open a small, auditable crop-response experiment rather than a broad planner rewrite.

Candidate properties:

1. frozen R4B behavior everywhere except bounded late crop allocation;
2. decision starts only after the full shop multiset is public;
3. uses only legal public features: shop multiset, current prices/market state, own seed inventory and time remaining;
4. converts only a bounded subset of existing WHEAT seed/plant slots to CARROT;
5. preserves movement, labor, animal routes, recovery controllers and terminal market liquidation;
6. W/L is the primary gate;
7. test on both the canonical 16 development seeds against Kaito/Rayk/Andrew and the 20 exploratory live-meta environmental seeds;
8. reject any candidate with family-specific gain plus significant regression elsewhere;
9. fresh validation only after exact freeze;
10. held-out remains 32/32 sealed.

## 10. Current interpretation of the 135.7 hosted score

We still do not have the exact hosted episode IDs for Kculture, so no causal claim about those losses is allowed yet. Official episode metadata forensics confirmed that episode JSON contains `info.seed`, `Agents`, and `TeamNames`, while daily manifests do not expose identity fields. Once the Aug-26 episode dataset or our Episode IDs become available, we can locate and reproduce the hosted environmental regimes directly.

Until then, the correct response is to improve calibration using current official top-ladder data, not to overreact with an unvalidated second submission.
