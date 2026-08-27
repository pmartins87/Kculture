# STATUS — Kculture

Last updated: 2026-08-27

## Mission

**Goal: maximize probability of a top-10 final finish in Kaggriculture; each top-10 position pays US$5,000.**

Repository `pmartins87/Kculture` is the source of truth for code, experiments, hosted submissions, public-package provenance and continuation state.

## Hosted reality

Latest observed snapshot from Kaggle UI:

- **R4B** — submission ID `55784381`: **143.2**;
- **KEXP-050** — submission ID `55818927`: **93.8**.

Known hosted episode IDs supplied from the Kaggle UI:

- R4B: `100996939`;
- KEXP-050: `100987834`.

KEXP-050 passed extensive local development/stress/validation and exact package parity, yet became materially worse than R4B in the live ladder. This is strong evidence that local win rates against narrow frozen public opponents are not reliable hosted-strength proxies.

Exact hosted replay forensics is scheduled four times per day. As of the latest manual retry on 2026-08-27 23:43 UTC, the daily 27-Aug episode dataset still returned 403/unavailable; the target episodes are absent from the public 24–26 Aug manifests.

**Held-out remains 32/32 sealed.**

## Frozen hosted references

### R4B

- candidate: `candidates/r4b_ablation_market_only.py`;
- blob: `e564125f0c4a1711fd3ea065dc1cb27d4a62ce37`;
- submission ID: `55784381`;
- latest observed hosted snapshot: **143.2**;
- role: weak hosted baseline / exploit detector, not likely final candidate.

### KEXP-050

- candidate: `candidates/r4d_reallocate_614_carrot.py`;
- blob: `61b77be136836328917441cb03f89bc6665c4c27`;
- formal package SHA-256: `59a45adf283f2f4dd1f9272150786c014585aa08c9b31b3348cf992ebe3bb64c`;
- submission ID: `55818927`;
- latest observed hosted snapshot: **93.8**;
- role: calibration evidence that a locally validated micro-improvement can regress severely hosted.

## Competitive Reset

### CR-001 — exact public-package identity: CLOSED

The hypothesis that old benchmarks used the wrong files was falsified. Kaito/Rayk/Andrew benchmark files were identity-equivalent to exact high-scoring public submission packages.

### CR-002 — historical-public BT proxy: CLOSED / CALIBRATION_FAIL

- 12 agents;
- 66/66 unordered pairs;
- 792 games;
- zero runtime errors;
- public order accuracy 0.6889;
- Spearman 0.5758 < frozen 0.60 gate;
- KEXP-050 #1 local, R4B #2;
- R4B **112-8** against ten public references historically rated roughly 1771–3090.

Conclusion: the historical public generation is structurally unrepresentative of the hosted field relevant to Kculture. Old 81-15/three-agent panels are permanently retired as promotion evidence.

### CR-002B — current-meta calibration research

Config: `configs/competitive_reset_current_meta_v1.json`.

Nine exact recent public snapshots were preflighted with package identities frozen, spanning approximately 1897–2882 observed public score. Current-meta calibration remains useful for opponent diversity, but no local public-agent league may overrule direct hosted evidence. Any benchmark that ranks R4B/KEXP-050 as prize-grade despite their ~143/~94 hosted reality is invalid for promotion.

## Shared-economy mechanics — architecture-changing fact

Permanent note: `docs/SHARED_ECONOMY_MECHANICS.md`.

Kaggriculture is best modeled as **private production + shared economy**:

- each farm/worker/board is private;
- players do not collide physically;
- market inventory and prices are shared;
- town consumption acts on the same shared inventory;
- market order positions resolve sequentially: position 0 fully before position 1, etc.;
- same-position same-product transactions use the same pre-commit quote in lockstep, so there is no intrinsic player-0 pricing advantage;
- therefore one player's sale/buy changes the economic state faced by later orders from either player.

Final reward is own bank money, but match outcome depends on relative money. A response may reduce own absolute revenue yet still be strategically good if it reduces the opponent more; promotion gates must track both own reward and relative delta/W-L.

## Opponent adaptation line — ACTIVE PRIMARY RESEARCH

### CR-004 — opponent-state predictive signal: PASS

Adding the opponent's public farm state/history to otherwise identical features improved out-of-time prediction materially.

- median error improvement: **7.10%**;
- 9/16 supported targets improved >5%;
- strong signals included SELL_CARROT +53.1%, SELL_TOMATO +37.7%, BUY_SEED_CARROT +32.4%, BUY_LAND +26.1%, SELL_STRAWBERRY +22.3%.

Conclusion: public opponent state contains exploitable predictive information.

### CR-005 — four-turn sell forecast: PASS

Out-of-time improvements included:

- MELON +30.9%, AUC ~0.978;
- CARROT +21.4%, AUC ~0.961;
- TOMATO +7.2%, AUC ~0.952;
- STRAWBERRY +6.2%, AUC ~0.848.

### CR-006 — naive low-threshold response: FAIL

Large economic proxy headroom existed, but trigger precision was only 32.1%. Broad reactive behavior was rejected.

### CR-007 — high-confidence selective adaptation: PASS

Frozen out-of-time thresholds:

- CARROT probability >= **0.90**;
- STRAWBERRY probability >= **0.85**;
- TOMATO/MELON disabled.

Test precision:

- CARROT 85.7%;
- STRAWBERRY 98.3%;
- combined **250/257 = 97.3%**.

Pure deployed-tree parity passed 48,000 inferences with max probability error 0 and 100% trigger agreement.

### CR-008 — append adaptive sale at end of order list: STRATEGIC FAIL

Mechanically clean opponent-aware candidate, but action placement was wrong.

- candidate field 75-21 vs R4B 74-22;
- mean own reward effect **-64.60/game**;
- mean relative-delta effect **-33.45/game**;
- direct vs R4B 4-4-16.

Prediction quality did not translate to value.

### CR-009 — forecast too early?: NOT SUPPORTED

- trigger true-positive rate again 97.28%;
- opponent first sale delay median **0 turns**, mean 0.464;
- 75% within 1 turn, 100% within 3;
- waiting for a better pre-sale price rarely helped.

Conclusion: forecast timing was already correct.

### CR-010 — exact in-turn order-sequence value: PASS

Run 2: `33106343741`.

Among 138 high-confidence same-turn sale events:

- opponent first same-product sale in position 0: **86.96%**;
- moving our adaptive sale to position 0 vs after that opponent sale: mean **+139.96** revenue/event;
- median **+72**;
- positive in **99.28%**;
- total measured counterfactual headroom **+19,314**;
- STRAWBERRY dominates the effect (~+152.65/event mean).

Conclusion: CR-008 often predicted the correct same-turn sale but placed its response too late in the shared market sequence.

### CR-011 — same adaptation, early order position: CAUSAL PASS

Candidate: `candidates/cr011_adaptive_early_order.py`  
Blob: `c4f1cb79f3c20b8229ab09e00a6878289cf9648d`  
Canonical successful run: `33110421956`.

Mechanical proof on official Aug-26 states:

- 28,760 states compared;
- zero action/multiset mismatches;
- 40 states where **only market-order sequence** changed.

Fresh 96-game current-meta field:

- CR-011 **72-24**;
- CR-008 **72-24**;
- R4B **72-24**;
- zero errors.

CR-011 vs R4B paired:

- mean own reward **+40.38/game**;
- mean relative delta **+235.26/game**;
- W/L score gain 0;
- positive own-reward effect in 3/4 opponent families.

CR-011 vs CR-008 paired:

- own reward **+158.76/game**;
- relative delta **+306.35/game**;
- W/L unchanged.

**Interpretation:** opponent-aware adaptation plus correct order placement causally improves economic/relative value, but the tested matches were too far from the decision boundary to establish W/L/BT improvement. CR-011 is **not hosted-submission-ready**.

## Active experiments

### CR-012 — attribute CR-011 effects

Run: `33127460773`.

Repeats the frozen CR-011/R4B 96-pair field and attributes the first actual adaptive action to product, quantity, price/state and terminal effect. Purpose: determine whether the next response refinement should be quantity sizing, product/context gating or another axis. Diagnostic only; it cannot directly authorize hosted promotion.

### CR-013 — close-match flip stress

Run: `33127568374`.

Frozen design:

- 20 new exploratory seeds;
- 9 current public snapshots;
- both seats;
- **360 R4B screening games**;
- CR-011 is excluded from selection;
- select 40 tuples nearest the W/L boundary using R4B only (<=1000 if enough, else <=3000, else 40 closest);
- replay CR-011 only on those tuples.

Primary question: can the +relative-money effect of CR-011 actually flip outcomes near zero? Frozen diagnostic gate requires positive relative gain plus a net positive score-rate change. No validation/held-out access.

## TOMATO structural branch — SECONDARY

KEXP-053/055/056 established that several recurrent long-lived physical route slots can support a bounded TOMATO experiment without immediate replant collision.

KEXP-056 PASS:

- 32 candidate slots;
- 19 post-maturity revisit opportunities;
- recurrent exact families in both development and exploratory distributions include 310@(9,7), 334@(5,9), 477@(0,9).

This branch remains secondary while opponent adaptation is producing stronger causal information.

## Submission policy

Do **not** submit CR-011 merely because its money/relative margin improved. W/L was unchanged in the broad field and hosted calibration is known to diverge from local narrow tests.

Next hosted submission must be a materially different strategic architecture with evidence that it changes matchup outcomes/BT-relevant coverage, or be explicitly justified as a high-information calibration submission under a frozen policy. Package parity remains mandatory.

## Exact continuation

1. Finish CR-012 and identify the context/product/quantity pattern behind CR-011 positive and negative effects.
2. Finish CR-013 and determine whether CR-011 converts close base outcomes into favorable outcomes.
3. Re-check hosted replay availability automatically; when 27-Aug data opens, analyze episode `100996939` (R4B) and `100987834` (KEXP-050) before trusting another local promotion.
4. If CR-013 shows real flips, build the next opponent-aware candidate with the smallest refinement supported by CR-012; test on new exploratory seeds/current-meta families.
5. If close-match flips remain absent, do not optimize margin for its own sake; move adaptation toward production/allocation/cash decisions with larger potential outcome impact.
6. Keep all **32/32 held-out sealed**.

## Frozen environment facts

- `kaggle-environments==1.32.7`;
- official engine commit `28b6d8af3ce73926b3d0fda1410c1ddd8384ab8c`;
- 720 recorded states; state 718 final executable action;
- replay alignment: observation state `t` -> submitted action stored at replay frame `t+1`;
- terminal reward = bank money;
- final competition relevance is Bradley–Terry/matchup strength, so broad **current-field** coverage and actual W/L flips matter more than isolated money gains.
