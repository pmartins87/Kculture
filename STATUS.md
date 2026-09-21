# STATUS — Kculture live source of truth

## Binding update — 2026-09-21 — V20A NOT TRAINABLE / V21A SEMANTIC DECOMPOSITION ACTIVE

**This block supersedes lower stale V20/V21 current-action sections.**

### V20A — COMPLETE / CLOSED

Workflow: **`35557692905`**.  
Decision: **`V20A_GATE_NOT_TRAINABLE`**.

- 5/5 shards PASS; 120/120 paired contexts; failures 0.
- O-TM1 changed market in 120/120 contexts.
- Training seeds 78711..78714: **0 positive W/L labels / 80 non-positive**.
- No classifier was fit or tuned.
- Across all 120 contexts: 0 positive score deltas, 0 negative score deltas, mean score delta 0.0, mean margin delta **-742.75**.
- V20B / O-TM2 is BLOCKED and remains dormant.

Result: `docs/strategy/ALL3_V20A_STATE_GATE_RESULT_2026-09-21.md`.

### V21A — ACTIVE / PRE-REGISTERED

Workflow: **`35558880526`**.  
Launch commit: `a815ee73dad8fda5f1c6a587417e22415120ec87`.

Causal decomposition of the frozen 102-turn V19A P2 schedule.

Frozen categories:
- EMPTY: 40;
- SELL_PRESENT: 33;
- BUY_ONLY: 22;
- HIRE_PRESENT: 7.

Population:
- already-consumed seeds 78711..78716;
- same 10 exact source SHAs;
- both seats;
- 120 contexts;
- no fresh validation seed consumed.

Modes:
- BASE;
- FULL;
- four single-category modes;
- four FULL-minus-one-category modes.

Hard binding:
- BASE must reproduce all 120 V20A BASE score+margin rows exactly;
- FULL must reproduce all 120 V20A treatment score+margin rows exactly;
- only W/L headroom with zero score regressions may select a candidate;
- margin-only cannot pass.

Dormant promotion path:
- V21B fresh seeds: `78901..78904`;
- V21C package/parity seeds: `79001..79002`;
- V21D: exactly one hosted submission only after V21A+B+C PASS.

Protocols:
- `docs/strategy/ALL3_V21A_SEMANTIC_SCHEDULE_DECOMPOSITION_PROTOCOL_2026-09-21.md`;
- `docs/strategy/ALL3_V21B_SEMANTIC_SCHEDULE_FRESH_PROTOCOL_2026-09-21.md`;
- `docs/strategy/ALL3_V21C_SEMANTIC_PACKAGE_PARITY_PROTOCOL_2026-09-21.md`;
- `docs/strategy/ALL3_V21D_SEMANTIC_HOSTED_SUBMISSION_PROTOCOL_2026-09-21.md`.

No Kaggle submission is currently authorized.

Stopping rule:
- if V21A has no semantic W/L headroom, close the V19A-derived schedule family;
- do not search post-hoc category pairs/turn subsets;
- activate the independent fresh-frontier V22 branch instead.

Pre-registered stop/next-branch document:
`docs/strategy/V21_STOP_RULE_AND_V22_FRESH_FRONTIER_BRANCH_2026-09-21.md`.

**Binding immediate action:** resolve workflow `35558880526`.

## Binding update — 2026-09-21 — V19C FRESH FAIL / V20A STATE GATE ACTIVE

**This block supersedes lower stale V19/V20 current-action sections.**

### V19C — COMPLETE / CLOSED

Workflow: **`35556749095`**.

Decision:
**`V19C_CONSENSUS_FRESH_FAIL_CLOSE`**.

Mechanical:
- 80/80 frozen pairs;
- failures 0;
- changed-market coverage 80/80;
- exact binding schedule SHA PASS.

Strategic:
- positive-score contexts: **10**;
- positive-score sources: **5**;
- negative-score contexts: **10**;
- BASE-win -> treatment-nonwin: **10**;
- mean score delta: **0.0**;
- mean margin delta: **-241.6375**.

Regime evidence:
- seed 78602 produced the score regressions;
- seed 78603 produced the score improvements;
- 78601/78604 produced no score changes.
The sign is therefore environmental-regime dependent, not a stable source-identity effect.

Result:
`docs/strategy/ALL3_V19C_CONSENSUS_FRESH_RESULT_2026-09-21.md`.

O-TM1 unconditional is CLOSED.

### V19D / V19E — NOT ACTIVATED

Because V19C failed:
- do not run V19D package parity;
- do not run V19E hosted submission;
- do not submit O-TM1.

Their pre-registered protocols remain archival only.

### V20A — ACTIVE

Workflow: **`35557692905`**  
Launch commit: `4613d77ea10d16110edf943948a18ea2d3b63573`.

Architecture:
one identity-free gate decided once at turn 464:
- OFF -> exact ALL3;
- ON -> unchanged frozen V19A O-TM1 schedule during P2.

V19C seeds are excluded from model fitting and validation.

Discovery:
- seeds 78711..78716;
- 10 exact source SHAs;
- both seats;
- 120 paired unconditional O-TM1 contexts.

Training:
- 78711..78714.

Internal holdout:
- 78715..78716.

Features:
- legal state/action snapshots at 463 and 464;
- current + previous + delta + abs(delta);
- no source/ref/rank/context/seed/seat/outcome/reward feature.

Frozen classifier:
- tree depth 3;
- min leaf 8;
- balanced classes;
- threshold P(benefit) >=0.80.

Only V20A_STATE_GATE_READY may activate untouched V20B seeds 78801..78804.

No Kaggle submission.

**Binding immediate action:** resolve workflow **`35557692905`**.


## Binding update — 2026-09-21 — V19B CONSENSUS WL HEADROOM / V19C FRESH VALIDATION ACTIVE

**This block supersedes lower stale V19 current-action sections.**

### V19B — COMPLETE / PASS

Workflow: **`35553022505`**.

Decision:
**`V19B_CONSENSUS_WL_HEADROOM`**.

Mechanical:
- 24/24 hard contexts;
- failures 0;
- changed-market coverage 24/24;
- source coverage 10/10;
- frozen schedule SHA256:
  `c68d857500b71a40f8cf4ef5f2ff693f6da1d97ced03e7d7f19eaedfded1ff22`.

Strategic:
- positive-score contexts: **14/24**;
- positive-score sources: **7**;
- negative-score contexts: **0**;
- mean score delta: **+0.5833333333333334**;
- mean margin delta: **+1273.0833333333333**.

Result:
`docs/strategy/ALL3_V19B_CONSENSUS_CAUSAL_RESULT_2026-09-21.md`.

### V19C — ACTIVE

Frozen config:
`configs/all3_v19c_consensus_fresh_validation.json`.

Population:
- same 10 exact hard-source SHAs;
- fresh seeds `78601..78604`;
- both seats;
- **80 paired contexts**;
- exact frozen V19A schedule / O-TM1 candidate.

Fresh PASS requires:
- all 80 pairs mechanically clean;
- changed-market coverage >=20 contexts;
- positive-score contexts >=2 across >=2 source SHAs;
- negative-score contexts = 0;
- BASE-win -> treatment-nonwin regressions = 0;
- mean score delta >0;
- mean margin delta >=0.

No candidate change is allowed.

### Parallel V18B2 note

The V18B2 transition-event experiment created later in a parallel chat path is **NON-BINDING** for the current roadmap.
The binding source-of-truth branch had already advanced through V19A/V19B.
Do not use V18B2 to supersede or alter O-TM1/V19C.

No Kaggle submission.

**Binding immediate action:** resolve V19C fresh validation.

### V19D/V19E — DORMANT / PRE-FROZEN PROMOTION PATH

Only if V19C returns `V19C_CONSENSUS_FRESH_PASS`:

**V19D package/parity**
- deterministic package: `KCULTURE_V47_ALL3_TM1_V1.tar.gz`;
- exact frozen V19A schedule embedded in standalone `main.py`;
- fresh parity seeds 78701,78702;
- opponents V47 mirror, V48 and tactical-memory;
- both seats;
- exact action + reward parity required in 12/12 contexts.

Protocol:
`docs/strategy/ALL3_V19D_TM1_PACKAGE_PARITY_PROTOCOL_2026-09-21.md`.

Only V19D parity PASS may activate V19E.

**V19E hosted submission**
- exactly one submission;
- frozen description:
  `PS_ALL3_TM1_V1_P2_CONSENSUS_C68D8575`;
- package SHA must equal V19D binding receipt;
- daily submission cap <=5;
- no post-hoc mutation after hosted observation.

Protocol:
`docs/strategy/ALL3_V19E_TM1_HOSTED_SUBMISSION_PROTOCOL_2026-09-21.md`.




## Binding update — 2026-09-20 — V18B CLOSED / V19A CONSENSUS READY / V19B ACTIVE

**This block supersedes lower stale V18/V19 current-action sections.**

### V18B — COMPLETE / CLOSED

Binding trainer-recovery workflow: **`35552606264`**.

Decision:
**`V18B_CONTROLLER_NOT_DISTILLABLE`**.

Dataset:
- 3072 exact P2 rows;
- 24 hard contexts;
- 10 unique source SHAs;
- zero replay/source failures.

Actionable recurrent SELL families: 19.  
Retained under frozen leave-one-source-out gate: **0**.

Best near misses were high-recall / low-precision:
- W3 FERTILIZER QTY +1: precision 0.56098, recall 0.95833, F1 0.70769;
- W3 FERTILIZER presence ADD: same metrics;
- W2 STRAWBERRY 5+ QTY INC: precision 0.54054, recall 1.0, F1 0.70175.

Do not relax tree thresholds or increase depth post-hoc.

Result:
`docs/strategy/ALL3_V18B_P2_MARKET_CONTROLLER_RESULT_2026-09-20.md`.

### V19A — COMPLETE / READY

Workflow: **`35552885627`**.

Decision:
**`V19A_CONSENSUS_SCHEDULE_READY`**.

Source-balanced P2 exact-market consensus:
- scope: turns 464..591;
- 10 source votes/turn;
- turn selected iff modal market support >=8/10 sources and >=16/24 contexts;
- **102/128 turns scheduled**;
- minimum source support 8;
- minimum context support 16;
- no source identity in runtime schedule.

Binding artifact:
`all3-v19a-p2-consensus-schedule`.

Result:
`docs/strategy/ALL3_V19A_P2_CONSENSUS_SCHEDULE_RESULT_2026-09-20.md`.

### V19B — ACTIVE

Workflow: **`35553022505`**  
Launch commit: `88248e361c61f00c0c9cccd0ef76bc79da2282c8`.

Candidate:
**O-TM1 — P2 Cross-Source Consensus Market Schedule**.

Runtime:
- exact ALL3 outside scheduled turns;
- on scheduled P2 turns, replace market only with the frozen consensus market;
- SELL quantities conservatively capped to current available own inventory;
- BUY_SEED / BUY_PRODUCT / HIRE remain exactly as frozen;
- farmer/hands never changed;
- no identity, seed, seat, context, future state or outcome feature.

Frozen discovery PASS:
- 24 paired hard contexts mechanical PASS;
- changed-market coverage >=8 contexts / >=4 sources;
- positive-score contexts >=4 across >=2 sources;
- negative-score contexts =0;
- mean score delta >0;
- mean margin delta >0.

### V19C — DORMANT / PRE-FROZEN

Config:
`configs/all3_v19c_consensus_fresh_validation.json`.

If and only if V19B returns WL_HEADROOM:
- same 10 exact hard-source SHAs;
- fresh seeds 78601..78604;
- both seats;
- 80 paired contexts.

No Kaggle submission.

**Binding immediate action:** resolve workflow **`35553022505`**.


## Binding update — 2026-09-20 — V18A P2 HEADROOM / V18B CUMULATIVE CONTROLLER ACTIVE

**This block supersedes lower stale V18 current-action sections.**

### V18A — COMPLETE / BINDING

Workflow: **`35547247595`**.

Decision:
**`V18A_SINGLE_PARTITION_HEADROOM`**.

Selected mode:
**`MARKET_P2_ONLY`** = turns **464..591**.

Mechanical:
- 24 contexts × 7 modes complete;
- failures 0;
- MARKET_P123 exactly reproduced all 24 binding V14A MARKET_W2PLUS score+margin outcomes;
- replication mismatches 0.

Selected P2:
- positive-score contexts: **14/24**;
- improved source SHAs: **7**;
- negative-score contexts: 0;
- mean score delta: **+0.5833333**;
- mean margin delta: **+1384.25**.

Interaction context:
- P1 alone: 0 score improvements;
- P3 alone: 0;
- P12: 20/24 improvements;
- P23: 22/24;
- P123: 18/24, exact V14A binding.

The pre-registered specificity rule binds P2 despite broader combinations scoring higher.

Result:
`docs/strategy/ALL3_V18A_W2PLUS_TEMPORAL_LOCALIZATION_RESULT_2026-09-20.md`.

### V18B — ACTIVE

Workflow: **`35552335995`**  
Launch commit: `a4d15571fc4d7a7594416e25de4a119b8f7f1118`.

Architecture:
- collect exactly **3072** P2 decision rows = 24 hard contexts × 128 turns;
- exact ALL3 gameplay;
- shadow teacher used only as offline market-residual label source;
- no identity/seed/seat/outcome predictive features.

Classifier:
- independent shallow trees per actionable recurrent SELL residual family;
- max depth 4;
- source-held-out validation over 10 unique hard-source SHAs;
- fixed precision/recall/F1 gates;
- JSON export with exact sklearn parity.

Controller v1 actionable kinds:
- SELL QTY;
- SELL PRESENCE;
- SELL DUPLICATE.

Generic REORDER/ORDER_COUNT and BUY/HIRE are excluded from first controller because they lack a uniquely safe standalone transformation.

READY requires:
- >=3 retained families;
- retained families span QTY/PRESENCE/DUPLICATE;
- >=4 positive source SHAs;
- exact sklearn/JSON parity;
- compiled structural validity on all 3072 rows.

No causal game is run in V18B.
No Kaggle submission.

**Binding immediate action:** resolve workflow **`35552335995`**.


## Binding update — 2026-09-20 — V17B CLOSED / V18A FULL W2PLUS TEMPORAL LOCALIZATION ACTIVE

**This block supersedes lower stale V17/V18 current-action sections.**

### V17B — COMPLETE / CLOSED

Workflow: **`35539385764`**.

Decision:
**`V17B_LQ6S_NO_HEADROOM_CLOSE`**.

Mechanical:
- 24/24 paired hard contexts;
- failures 0;
- fire coverage 24/24 contexts;
- source coverage 10/10 source SHAs;
- total O-LQ6S fires: 44.

Strategic:
- loss-to-win flips: 0;
- positive-score contexts: 0;
- negative-score contexts: 0;
- mean score delta: **0.0**;
- mean margin delta: **-42.833333333333336**.

O-LQ6S is closed. V17C fresh validation is not activated.

Result:
`docs/strategy/ALL3_V17B_LQ6S_CAUSAL_RESULT_2026-09-20.md`.

### V18A — ACTIVE

Workflow: **`35547247595`**  
Launch commit: `d02e63aea3dee0ff5c462f86f73450548a0d5959`.

Before any V18A game ran, the original V14A implementation was re-opened and confirmed:
`MARKET_W2PLUS` means **all turns t >= 336 through episode end**.

The dormant V18A draft that only covered 336..503 was therefore mechanically corrected before activation.

Frozen equal chronological partitions of the full 383-turn V14A treatment interval:
- P1: 336..463;
- P2: 464..591;
- P3: 592..718.

Modes:
- BASE;
- MARKET_P1_ONLY;
- MARKET_P2_ONLY;
- MARKET_P3_ONLY;
- MARKET_P12;
- MARKET_P23;
- MARKET_P123.

Hard mechanical requirement:
**MARKET_P123 must exactly reproduce score and margin for every one of the 24 binding V14A MARKET_W2PLUS rows** from workflow `35526276641`.

Only after exact replication may the narrower partitions be interpreted.

No Kaggle submission.

**Binding immediate action:** resolve workflow **`35547247595`**.


## Binding update — 2026-09-20 — V17A3 STATELESS CLOSE / V17A4 EDGE READY / V17B ACTIVE

**This block supersedes lower stale V17 current-action sections.**

### V17A3 — COMPLETE / STATELESS NOT COMPRESSIBLE

Workflow: **`35539020930`**.

Decision:
**`V17A3_STRAWBERRY_TRIGGER_NOT_COMPRESSIBLE`**.

Key trigger summaries:
- T0_AVAILABLE: recall 1.0, precision 0.0399;
- T1_CARRIED20: recall 0.5714, precision 0.3333;
- T2_SHED2: recall 0.4286, precision 0.90;
- T3_CARRIED20_OR_SHED2: recall 1.0, precision 0.4565.

The dominant false positives for T3 were persistence at turns 494/495 after the true turn-493 event.

### V17A4 — COMPLETE / READY

Workflow: **`35539277486`**.

Decision:
**`V17A4_STRAWBERRY_EDGE_TRIGGER_READY`**.

Selected trigger:
`E3_CARRIED20_OR_SHED2_RISING`.

Definition:
- W2;
- exact ALL3 market has no nonempty order;
- total own STRAWBERRY >=2;
- carried STRAWBERRY >=20 OR shed STRAWBERRY >=2;
- fire only on false -> true transition.

Metrics:
- targets 42;
- fires 44;
- TP 42;
- FP 2;
- FN 0;
- recall 1.0;
- precision 0.954545;
- 24/24 contexts;
- 10/10 source SHAs.

Frozen config:
`configs/all3_v17b_lq6s_trigger.json`.

### V17B — ACTIVE

Workflow: **`35539385764`**  
Launch commit: `303b3c72bb3bbc7ad73ed38d4fbebc7c23d9a538`.

Candidate:
**O-LQ6S — W2 STRAWBERRY first-free SELL2**.

Runtime:
- exact frozen V17A4 rising-edge trigger;
- insert SELL STRAWBERRY qty2 at first semantic free slot;
- recurrent on every rising edge;
- preserve all other market orders/quantities and physical action.

Discovery population:
- all 24 binding V13C hard contexts.

Frozen PASS:
- 24-context / 10-source fire coverage;
- loss-to-win flips >=4 across >=2 sources;
- mean score delta >0;
- mean margin delta >0.

Fresh V17C population/seeds remain pre-frozen and dormant.

No Kaggle submission.

**Binding immediate action:** resolve workflow **`35539385764`**.


## Binding update — 2026-09-20 — V17A/A2 READY / V17A3 TRIGGER AUDIT ACTIVE

**This block supersedes lower stale V17 current-action sections.**

### V17A — COMPLETE / READY

Workflow: **`35538621223`**.

Decision:
**`V17A_W2_JOINT_MARKET_BUNDLE_READY`**.

Selected exact recurrent W2 bundle:
- `PRESENCE|SELL|STRAWBERRY|ADD`;
- `QTY|SELL|STRAWBERRY|2|INC`.

Support:
- 24/24 hard contexts;
- 10/10 source SHAs;
- 42 occurrences;
- turns observed: 493 and 503;
- median turn 493.

### V17A2 — COMPLETE / READY

Binding workflow: **`35538843133`**.

Decision:
**`V17A2_STRAWBERRY_INSERTION_READY`**.

Translation:
- quantity = exactly 2 in 42/42 events;
- insertion index = 0 in 42/42 events;
- semantic insertion rule = **first free market slot** in 42/42 events;
- first free means first explicit empty slot, otherwise virtual append position;
- selected occurrence multiplicity:
  - 18 contexts: two events;
  - 6 contexts: one event.

The initial V17A2 workflow `35538722889` is NON-BINDING mechanical failure caused by equivalent `[]` vs `[[]]` empty-market representation. The binding rerun normalizes only that representation.

### V17A3 — ACTIVE

Workflow: **`35539020930`**  
Launch commit: `e7943512aee243921f1d115cad1ad832e4b182cb`.

Purpose:
find a legal identity-free runtime trigger that reproduces the 42 selected bundle events without exact-turn whitelisting.

Frozen trigger grammar:
- T0_AVAILABLE;
- T1_CARRIED20;
- T2_SHED2;
- T3_CARRIED20_OR_SHED2.

All require:
- W2;
- exact ALL3 market has no nonempty order;
- total own STRAWBERRY >=2.

READY requires:
- recall 1.0;
- precision >=0.90;
- all 24 contexts;
- all 10 source SHAs.

Selection:
1. highest precision;
2. fewest fires;
3. lexical name.

No STRAWBERRY treatment has been run yet.
No Kaggle submission.

**Binding immediate action:** resolve workflow **`35539020930`**.


## Binding update — 2026-09-20 — V16B MARGIN-ONLY CLOSE / V17A JOINT MARKET BUNDLE ACTIVE

**This block supersedes lower stale V16/V17 current-action sections.**

### V16B — COMPLETE / CLOSED

Workflow: **`35533510437`**.

Decision:
**`V16B_LQ5F_MARGIN_ONLY_CLOSE`**.

Mechanical:
- 24/24 paired hard contexts;
- failures 0;
- fire coverage 24/24 contexts, 10/10 sources;
- exactly one W2 O-LQ5F fire per treatment episode.

Strategic:
- loss-to-win flips: 0;
- positive-score contexts: 0;
- negative-score contexts: 0;
- mean score delta: **0.0**;
- mean margin delta: **+11.5**.

O-LQ5F is closed. V16C fresh validation is not activated.

Result:
`docs/strategy/ALL3_V16B_LQ5F_CAUSAL_RESULT_2026-09-20.md`.

### V17A — ACTIVE

Workflow: **`35538621223`**  
Launch commit: `1baf3e1abbb51368841caff6d3f5f34a2f6e0c5d`.

Question:
does the V14B binding W2 atlas contain a recurrent **multi-edit market bundle** that could explain why complete MARKET_W2PLUS substitution produced large W/L headroom while isolated reorder and isolated quantity edits did not?

Frozen extraction:
- binding V14B artifact only;
- W2 events only;
- recurrent legal market edits only;
- multi-edit bundles only;
- exact co-occurrence signatures;
- no outcome-based ranking.

Deterministic selection:
1. max unique sources;
2. max context support;
3. max occurrence count;
4. earliest median turn;
5. lexical bundle key.

No Kaggle submission.

**Binding immediate action:** resolve workflow **`35538621223`**.


## Binding update — 2026-09-20 — V15A CLOSED ZERO EFFECT / V16B O-LQ5F ACTIVE

**This block supersedes lower stale V15/V16 current-action sections.**

### V15A — COMPLETE / CLOSED

Workflow: **`35532585508`**.

Decision:
**`V15A_LQ4E_NO_HEADROOM_CLOSE`**.

Mechanical:
- 24/24 paired hard contexts;
- failures 0;
- coverage 24/24 contexts, 10/10 sources;
- total O-LQ4E fires: 48;
- exactly two fires/context at turns 96 and 120.

Strategic:
- loss-to-win flips: 0;
- positive score contexts: 0;
- mean score delta: **0.0**;
- mean margin delta: **0.0**.

Every paired margin was exactly unchanged.

Binding interpretation:
the selected EARLY reorder relation is a structural marker but not causal. O-LQ4E is closed. V15B is not activated.

Result:
`docs/strategy/ALL3_V15A_LQ4E_CAUSAL_RESULT_2026-09-20.md`.

### V16A — COMPLETE

Workflow: **`35533351868`**.

Decision:
**`V16A_W2_SELL_QUANTITY_PHENOTYPE_READY`**.

Selected W2 SELL-quantity phenotype:
- `W2|QTY|SELL|FERTILIZER|2`;
- direction INC;
- +2 units;
- 24/24 contexts;
- 10/10 sources;
- direction share 1.0;
- exactly one selected occurrence/context;
- median turn 368.

Binding candidate translation:
**O-LQ5F — one-shot W2 Fertilizer Queue +2**.

Semantics:
- first eligible W2 ALL3 SELL FERTILIZER only;
- add +2 quantity to first existing order;
- one fire maximum/episode;
- no new order;
- preserve order positions, all other quantities, farmer/hands;
- no exact-turn whitelist or identity feature.

Result:
`docs/strategy/ALL3_V16A_W2_SELL_QUANTITY_RESULT_2026-09-20.md`.

### V16B — ACTIVE

Workflow: **`35533510437`**  
Launch commit: `12c3b9ea4c481c3e640688ca87cd346cd2777259`.

Population:
- all 24 binding V13C hard contexts;
- BASE exact ALL3 vs exact ALL3 + frozen one-shot O-LQ5F.

Frozen discovery PASS:
- clean mechanics;
- coverage >=8 contexts / >=2 sources;
- loss-to-win flips >=4 across >=2 sources;
- mean score delta >0;
- mean margin delta >0.

### V16C — DORMANT / PRE-FROZEN

Config:
`configs/all3_v16c_lq5f_fresh_validation.json`.

If and only if V16B returns WL_HEADROOM:
- same 10 exact source SHAs;
- fresh seeds `78301..78304`;
- both seats;
- 80 fresh paired contexts.

No candidate change after V16B.

No Kaggle submission.

**Binding immediate action:** resolve workflow **`35533510437`**.


## Binding update — 2026-09-20 — V14B REORDER TRANSLATED / V15A O-LQ4E CAUSAL ACTIVE

**This block supersedes lower stale V14B/V15 current-action sections.**

### V14B — COMPLETE

Phenotype atlas workflow: **`35526759114`**.

Decision:
**`V14B_RECURRENT_DOMAIN_PHENOTYPE_READY`**.

Selected phenotype by pre-registered deterministic ordering:
- `EARLY|REORDER`;
- 24/24 hard contexts;
- 10/10 source SHAs;
- 148 occurrences;
- direction share 1.0;
- median turn 150.

Outcome-free directional translation workflow:
**`35532446891`**.

Translation decision:
**`V14B_REORDER_DIRECTION_READY`**.

Selected pairwise precedence:
- earlier: **SELL FERTILIZER**;
- later: **HIRE**;
- 24/24 contexts;
- 10/10 sources;
- 48 occurrences;
- direction share 1.0;
- observed turns 96 and 120;
- median turn 108.

The candidate does not whitelist turns 96/120. It generalizes the selected EARLY structural phenotype:
step <336 + both target order types present + HIRE precedes SELL FERTILIZER.

Binding result:
`docs/strategy/ALL3_V14B_MARKET_PHENOTYPE_RESULT_2026-09-20.md`.

### O-LQ4E — FROZEN FIRST-PARTY CANDIDATE

**Early Fertilizer-before-Hire**.

Semantics:
- input exact ALL3;
- step <336;
- identify only target slots whose order is SELL FERTILIZER or HIRE;
- stable-sort target slots with SELL FERTILIZER first, HIRE second;
- preserve all non-target slots;
- preserve all quantities;
- preserve market multiset;
- preserve farmer/hands;
- no opponent identity or future information.

Implementation:
`tools/first_party_lq4e_early_fertilizer_before_hire.py`.

### V15A — ACTIVE

Workflow: **`35532585508`**  
Launch commit: `de0242ec264047517dd4974419cf75cee8dbbf46`.

Population:
- all 24 binding V13C hard contexts;
- BASE exact ALL3 vs exact ALL3 + O-LQ4E;
- same frozen source SHA / seed / seat.

Frozen W/L discovery PASS requires:
- mechanics clean;
- fire coverage >=8 contexts across >=2 sources;
- loss-to-win flips >=4 across >=2 sources;
- mean score delta >0;
- mean margin delta >0.

Margin-only closes the option.

Fresh V15B validation population/seeds are already pre-registered in the V15A protocol and cannot change after this result.

No Kaggle submission.

**Binding immediate action:** resolve workflow **`35532585508`**.


## Binding update — 2026-09-20 — V14A MARKET HEADROOM / V14B MARKET ATLAS ACTIVE

**This block supersedes lower stale V14A/V14B current-action sections.**

### V14A — COMPLETE / BINDING

Binding mechanical-completion workflow: **`35526276641`**.

Decision: **`V14A_MARKET_DOMAIN_HEADROOM`**.

Complete grid:
- 24 hard contexts;
- 6 pre-registered modes;
- **144/144 unique context-mode rows**.

Domain results:

**MARKET_ALL**
- improved-score contexts: **12/24**;
- improved unique sources: **5**;
- mean score delta: **+0.50**;
- mean margin delta: **+1812.83**;
- regressions: **0**.

**MARKET_W2PLUS**
- improved-score contexts: **18/24**;
- improved unique sources: **7**;
- mean score delta: **+0.75**;
- mean margin delta: **+1858.50**;
- regressions: **0**.

**PHYSICAL_ALL**
- improved-score contexts: **0/24**;
- mean margin delta: **-113.42**.

**PHYSICAL_W2PLUS**
- improved-score contexts: **0/24**;
- mean margin delta: **-265.33**.

**FULL_ALL**
- improved-score contexts: **24/24**;
- mean score delta: **+0.50**;
- mean margin delta: **+1364.75**.

Binding interpretation:
reusable current-frontier W/L upper-bound headroom is a **market-domain** effect, especially post-turn-336. Physical imitation is closed for this branch.

Result:
`docs/strategy/ALL3_V14A_CURRENT_FRONTIER_DOMAIN_UPPER_BOUND_RESULT_2026-09-20.md`.

### V14B MARKET phenotype atlas — ACTIVE

Workflow: **`35526759114`**  
Launch commit: `6183aea6077693c230a72f5eae94f88a543fc1d9`.

The V14B protocol was pre-registered before V14A completed.

Population:
- all 24 binding V13C hard contexts;
- same frozen source SHAs;
- exact ALL3 returned to the environment;
- shadow teacher evaluated only for offline market-difference localization.

Atlas records:
- legal candidate-visible state;
- market order-count deltas;
- per-product/side quantity deltas;
- add/remove presence;
- reorder-only differences;
- duplicate compaction/splitting;
- phase and coarse predeclared state buckets.

Recurrence gate:
- context support >=4;
- source support >=2;
- same direction >=75%;
- legal candidate-visible expression;
- no opponent identity.

If multiple families pass, deterministic selection:
1. most unique source SHAs;
2. most contexts;
3. earliest median turn;
4. lexical phenotype key.

At most one phenotype may advance to a first-party causal rule.

No Kaggle submission.

**Binding immediate action:** resolve workflow **`35526759114`**.


## Binding update — 2026-09-20 — V14A MECHANICAL COMPLETION ACTIVE

**This block supersedes lower stale V14A current-action sections.**

### V14A original parallel run — NON-BINDING MECHANICAL INVALID

Workflow: `35525689199`.

Strategically valid rows before rejection:
- 126/144 mode-context rows;
- 21/24 hard contexts complete.

Mechanical failures:
- `v13c_hard_14` — rank 19 source acquisition HTTP 429;
- `v13c_hard_16` — rank 23 source acquisition HTTP 429;
- `v13c_hard_18` — rank 23 source acquisition HTTP 429.

No failed context was partially interpreted; all three failures happened during teacher acquisition before treatment execution.

Preliminary completed-context evidence is non-binding until the full 144-grid is restored.

### V14A binding mechanical completion — ACTIVE

Workflow: **`35526276641`**  
Launch commit: `efc82c77060fe44025eee86cb239b698d6201229`.

Procedure:
1. reuse exactly 126 mechanically valid rows from workflow `35525689199`;
2. execute exactly the three missing contexts in all six pre-registered modes;
3. require supplement mechanical PASS;
4. verify exact 24 context × 6 mode = **144 unique keys**;
5. apply the unchanged pre-registered V14A domain gate.

No strategic population, mode, threshold, or decision rule changed.

V14B domain phenotype protocol remains DORMANT and was pre-registered before the binding V14A result.

No Kaggle submission.

**Binding immediate action:** resolve workflow **`35526276641`**.


## Binding update — 2026-09-20 — V13C HARD CONTEXTS READY / V14A ACTIVE

**This block supersedes lower stale current-action sections.**

### V13C — COMPLETE / READY

Binding mechanical-completion workflow: **`35523990217`**  
Binding completion head: `0a537f334334130fc083b52994744aa11366f342`.

Decision: **`V13C_CURRENT_FRONTIER_HARD_CONTEXTS_READY`**.

Mechanical:
- 76/76 frozen source-SHA × seed × seat contexts;
- exact ALL3 unchanged;
- 19 frozen unique-source current-frontier representatives;
- rank-14 source repaired only by immutable provenance pin:
  `tetsutani/demand-preserving-turn-sale-timing/versions/4`;
- full 76-key set verified before strategic decision.

Strategic:
- **24 hard contexts**;
- **10 unique hard source SHAs**;
- rank 14: 4/4 losses;
- rank 23: 4/4 losses;
- ranks 1,2,4,6,8,9,11,19: 2/4 losses each.

The 24 binding hard contexts are frozen in:
`configs/all3_v14a_hard_contexts.json`.

Result:
`docs/strategy/ALL3_V13C_CURRENT_FRONTIER_HARD_CONTEXT_RESULT_2026-09-20.md`.

Local H2H remains mechanism-discovery only and is not a hosted-rating estimator.

### V14A — ACTIVE

Workflow: **`35525689199`**  
Launch commit: `73f6dfdfc3e773c4b20bc9a3a888b2627c507521`.

V14A was pre-registered before the binding V13C result.

Frozen population:
- all and only 24 V13C binding hard contexts;
- no manual context selection.

Frozen modes:
- BASE;
- MARKET_ALL;
- MARKET_W2PLUS;
- PHYSICAL_ALL;
- PHYSICAL_W2PLUS;
- FULL_ALL.

Question:
identify whether reusable W/L upper-bound headroom is carried by MARKET, PHYSICAL, both, only cross-domain interaction, or not recoverable even under the shadow-teacher ceiling.

Margin-only evidence cannot pass a domain gate.

Opponent identity/code is offline shadow-teacher evidence only and is prohibited as a future runtime feature.

No Kaggle submission.

**Binding immediate action:** resolve workflow **`35525689199`**.


## Binding update — 2026-09-20 — V13C RERUN WITH IMMUTABLE RANK-14 PIN

**This block supersedes lower stale current-action sections.**

### V13C first run — NON-BINDING MECHANICAL INVALID

Workflow: `35520875702`.

Observed before mechanical rejection:
- 72/76 episodes completed;
- 20 nonwins across 9 source SHAs.

These strategic outcomes are **NON-BINDING** and were not used to alter the population, seeds, or strategic gate.

Mechanical failure:
- rank 14 `tetsutani/demand-preserving-turn-sale-timing`;
- V13B frozen main SHA: `1aa3717b3201997a95920c80cf5612c23f78f8716c7b1084b6a345ca4eae7e4f`;
- unversioned ref changed before V13C and returned SHA `827ddf2997fa442e80baadebc4cc91ffaeedec1ff333c1fa7d872b0f1d448181`.

Fail-closed behavior worked as designed.

### Rank-14 immutable provenance repair

Workflow `35523343530` searched public historical versions without executing third-party code.

Exact frozen source was recovered at:

`tetsutani/demand-preserving-turn-sale-timing/versions/4`

Verification:
- main SHA: `1aa3717b3201997a95920c80cf5612c23f78f8716c7b1084b6a345ca4eae7e4f`;
- archive SHA: `24250d6de0e1bf143ea0cc1b2bdab541aa94ee12c09b9f2f6e98e8afb7097610`;
- exact match to V13B bytes.

Config amendment commit:
`de85cbc11dea91ea80ea247437172aa50baf9e88`.

The amendment changes **only provenance immutability**:
- same 19 source SHAs;
- same population;
- same seeds `78101,78102`;
- same seats;
- same V13C strategic gate.

### V13C binding rerun — ACTIVE

Workflow: **`35523473844`**  
Head: `de85cbc11dea91ea80ea247437172aa50baf9e88`.

Expected:
- 19 source representatives;
- 2 seeds;
- 2 seats;
- 76 exact ALL3 episodes.

Decision remains the pre-registered V13C gate.

### V14A — DORMANT / PRE-REGISTERED

Protocol:
`docs/strategy/ALL3_V14A_CURRENT_FRONTIER_DOMAIN_UPPER_BOUND_PROTOCOL_2026-09-20.md`.

It was frozen before the binding V13C result.

Activate only if binding V13C returns
`V13C_CURRENT_FRONTIER_HARD_CONTEXTS_READY`.

No Kaggle submission.

**Binding immediate action:** resolve workflow **`35523473844`**.


## Binding update — 2026-09-20 — V13B READY / V13C HARD-CONTEXT CENSUS ACTIVE

**This block supersedes lower stale current-action sections.**

### V13B — COMPLETE / READY

Workflow: **`35520463598`**.

Decision: **`V13B_EXECUTABLE_FRONTIER_READY`**.

- 26/30 current refs acquired;
- 4 failures were Kaggle HTTP 429 on ranks 27–30;
- 19 unique current source SHAs;
- **19/19 unique sources passed both-seat exact-engine smoke**;
- all current Top-10 acquired refs map to smoke-passing sources.

Frozen population:
`configs/all3_v13c_current_frontier_representatives.json`.

Result:
`docs/strategy/ALL3_V13B_CURRENT_TOP30_EXECUTABLE_REFRESH_RESULT_2026-09-20.md`.

### V13C — ACTIVE

Workflow: **`35520875702`**  
Launch commit: `7cd012b74e794c4be6df9bfd601e1233de0f2b27`.

Population:
- 19 exact unique-source current frontier representatives;
- source SHA frozen before outcomes;
- exact ALL3 unchanged;
- fresh seeds `78101, 78102`;
- both seats;
- expected 76 episodes.

Decision gate was pre-registered before V13B result:
- >=4 nonwins across >=2 unique sources => HARD_CONTEXTS_READY;
- 1–3 or one-source only => NARROW;
- zero => LOCAL_FRONTIER_TOO_EASY;
- any unresolved SHA/runtime mechanics failure => MECHANICS_INVALID.

Local H2H remains mechanism-discovery only, never a hosted-rating estimator.

No Kaggle submission.

**Binding immediate action:** resolve workflow **`35520875702`**.


## Binding update — 2026-09-20 — V13A MODERATE DRIFT / V13B EXECUTABLE REFRESH ACTIVE

**This block supersedes lower stale current-action sections.**

### V13A — COMPLETE

Binding workflow: **`35520373817`**  
Binding head: `9fb21773f4b7318dbc12605d49e680296de3898a`.

Earlier workflow `35520312252` is NON-BINDING mechanical failure (repository import path before strategic data read).

Decision: **`V13A_FRONTIER_MODERATE_DRIFT_REFRESH_ALL_CURRENT`**.

Current score-sorted public Top-30 versus frozen 2026-09-18 corpus:
- overlap: **15/30**;
- new current refs: **15**;
- dropped frozen refs: **15**;
- unknown current source identities: **15**.

Binding action: refresh/extract all current Top-30 rather than reuse the old seven-agent league or only patch new entrants.

Frozen refs:
`configs/all3_v13b_current_top30_refs.json`.

Result:
`docs/strategy/ALL3_V13A_CURRENT_TOP30_DRIFT_RESULT_2026-09-20.md`.

### V13B — ACTIVE

Workflow: **`35520463598`**  
Launch commit: `79e14f85382c8f4d68fba2fab19bcae25c4d9437`.

For all 30 frozen current refs:
- acquire exact public package or static notebook source;
- compute current `main.py` SHA;
- deduplicate exact sources;
- remove Kaggle credentials before third-party execution;
- smoke one unique-source representative in both seats vs starter on exact engine 1.32.7;
- persist provenance/results only, never public source code.

READY gate:
- >=24/30 refs acquired;
- >=12 unique sources;
- >=10 unique sources pass both-seat smoke;
- >=5 current Top-10 refs map to smoke-passing sources.

Local smoke W/L is mechanically diagnostic only and must never be used as hosted-strength evidence.

No Kaggle submission.

Preserve hosted pair:
- O-RW1 `56336027`;
- ALL3 `56367770`.

**Binding immediate action:** resolve workflow **`35520463598`**.


## Binding update — 2026-09-20 — V12A CLOSED / V13A CURRENT FRONTIER DRIFT ACTIVE

**This block supersedes lower stale current-action sections.**

### V12A — COMPLETE / CLOSED

Workflow: **`35519704115`**  
Head: `f255d27997739690ff833828cc2adb1bc42bef04`.

Decision: **`V12A_PUBLIC_CROP_SHIFT_TRANSFER_SPARSE`**.

Mechanical:
- 112/112 exact ALL3 episodes;
- 7/7 frozen public families;
- both seats;
- failures 0.

Competitive:
- ALL3: **112W–0L–0T**;
- primary CARROT signal support: 12, all in Best Market;
- signal games: **12W–0L**;
- strict CARROT+4 / WHEAT-deficit-4 signal support: 0.

Binding interpretation:
the hosted V11B CARROT association is not a transferable causal failure rule on this league, and the frozen seven-agent league is now too weak/unrepresentative for discovery.

V12B remains **DORMANT_NOT_ACTIVATED**. Do not run or tune it.

Result:
`docs/strategy/ALL3_V12A_PUBLIC_CROP_SHIFT_TRANSFER_RESULT_2026-09-20.md`.

### V13A — ACTIVE

Workflow: **`35520312252`**  
Launch commit: `a10d264f39af48823f30f02f306396c6f033bdfd`.

Purpose:
refresh the current Kaggriculture score-sorted public Top-30 and compare it with the frozen 2026-09-18 Top-30 corpus before executing third-party agents.

This stage:
- performs read-only Kaggle metadata queries;
- executes no third-party agent code;
- records current refs, overlap, entrants, dropped refs, rank displacement and unknown source identities.

Gate:
- overlap >=24/30 and unknown/new <=6 => incremental executable refresh;
- overlap 15..23 => refresh all current Top-30;
- overlap <15 => full frontier rebuild.

No Kaggle submission.

Preserve hosted pair:
- O-RW1 `56336027`;
- ALL3 `56367770`.

**Binding immediate action:** resolve workflow **`35520312252`**.


## Binding update — 2026-09-20 — V11B REGIME SIGNAL / V12A TRANSFER ACTIVE

**This block supersedes lower stale current-action sections.**

### V11A — COMPLETE

Workflow: **`35518801971`**.

Decision: **`V11A_HOSTED_HARD_POPULATION_READY`**.

Current ALL3 hosted sample `56367770`:
- 128 resolved games;
- 57W–71L–0T;
- score rate **0.4453125**;
- 117 unique opponents;
- 30 close losses in [-1000,0).

This mature sample supersedes the early 34-game 28W–6L snapshot as the current hosted discovery source.

Result:
`docs/strategy/ALL3_V11A_HOSTED_HARD_POPULATION_RESULT_2026-09-20.md`.

### V11B — COMPLETE / OBSERVATIONAL SIGNAL

Workflow: **`35519476400`**.

Decision: **`V11B_PUBLIC_CROP_SHIFT_REGIME_SIGNAL`**.

Public-state association:
- step 456: opponent CARROT > ALL3 CARROT in 9 games, **9/9 losses**;
- step 504: 13/13 losses;
- step 552: 17/17 losses;
- step 600: **22/22 losses**, mean margin -3504.27;
- strict step-600 CARROT+4 / WHEAT-deficit-4 signature: **15/15 losses**, mean margin -4157.07.

This is observational only and does not authorize a CARROT-response rule.

Result:
`docs/strategy/ALL3_V11B_HOSTED_LOSS_SIGNATURE_RESULT_2026-09-20.md`.

### V12A — ACTIVE

Workflow: **`35519704115`**  
Launch commit: `f255d27997739690ff833828cc2adb1bc42bef04`.

Exact ALL3 is run unchanged on fresh seeds `77001..77008`, both seats, against seven hash-pinned public families:
- V47 mirror;
- Ready Stock;
- V48;
- router_2715;
- Conditional Memory;
- Tactical Memory;
- Best Market.

Expected contexts: 112.

Primary question:
does the public `opponent CARROT > own CARROT` regime transfer outside hosted replay forensics and still discriminate poor ALL3 W/L?

Frozen TRANSFER_READY gate requires:
- signal support >=8;
- >=2 opponent families with >=2 signal contexts each;
- signal loss rate >=0.75;
- signal score rate <=0.25;
- non-signal support >=16;
- non-signal score rate at least 0.20 above signal score rate.

Only TRANSFER_READY may open a V12B causal macro-response oracle. V12A itself cannot promote or modify a policy.

Opponent identity remains offline evaluation metadata only.

No automatic Kaggle submission.

Preserve hosted pair:
- O-RW1 `56336027`;
- ALL3 `56367770`.

**Binding immediate action:** resolve workflow **`35519704115`**.


## Binding update — 2026-09-20 — V10A CLOSED / V11A HOSTED REFRESH ACTIVE

**This block supersedes lower stale current-action sections.**

### V10A — COMPLETE / CLOSED

Workflow: **`35518110487`**  
Head: `291442310a0397da0d7a670a5b20954b8450c06b`.

Decision: **`V10A_RESIDUAL_MARKET_UPPER_BOUND_CLOSED`**.

Mechanical:
- PASS;
- 4/4 frozen hard contexts;
- 28/28 mode-context runs;
- failures 0;
- zero physical fallback turns.

Strategic:
- FULL_ALL: 0/4 positive-score contexts, mean margin delta **-205.25**;
- FULL_W2PLUS: 0/4 positive-score contexts, mean margin delta **-191.5**;
- STRUCT_W2PLUS: 0/4 positive-score contexts, mean margin delta **-191.5**;
- INSERT_W2PLUS: 0/4 positive-score contexts, mean margin delta **-191.5**;
- QTY_W2PLUS: score/margin neutral;
- REORDER_W2PLUS: score/margin neutral.

Binding interpretation:
the remaining V48 market behavior has no local or cumulative W/L upper-bound headroom over ALL3. Further V48-derived market imitation/tuning is closed.

Result:
`docs/strategy/ALL3_V10A_RESIDUAL_CUMULATIVE_MARKET_RESULT_2026-09-20.md`.

### Historical option clarification

H1/H1B timing is **not** a new missing option: its public town-WHEAT sale-deferral mechanism was already distilled into **O-TW1**, and O-TW1 is already one of the three ALL3 components (O-RW1 + O-TW1 + O-LQ2). Do not reopen H1/H1B as a duplicate option family.

### V11A — ACTIVE

Current discovery source moves from V48 residual imitation to the actual hosted ALL3 population.

Workflow: **`35518801971`**  
Launch commit: `bbc4a9d74e930bf4fb334a0f5217ab3cb43133c0`.

Target:
- ALL3 hosted submission `56367770`;
- up to 128 newest public replays;
- loss-opponent table;
- repeated-loss opponents;
- worst 25 losses;
- close-loss subset.

Opponent identity is offline forensic metadata only and prohibited as runtime policy input.

Gate:
- >=64 resolved games and >=10 losses => `V11A_HOSTED_HARD_POPULATION_READY`;
- otherwise => `V11A_HOSTED_SAMPLE_STILL_THIN`.

No automatic Kaggle submission.

Preserve hosted pair:
- O-RW1 `56336027`;
- ALL3 `56367770`.

**Binding immediate action:** resolve workflow **`35518801971`**.


## Binding update — 2026-09-20 — V9A READY / V9B ACTIVE

**This block supersedes lower stale current-action sections.**

### V9A — COMPLETE

Workflow: **`35517515758`**  
Decision: **`V9A_STRUCTURAL_RESIDUAL_READY`**.

Mechanical:
- PASS;
- exact ALL3 hard-context replay matched;
- failures 0;
- physical divergences 0.

Residual market census:
- 233 total divergences;
- 161 INSERT_DROP;
- 63 QTY_UP;
- 9 REORDER_ONLY;
- structural residuals present in all 4 hard contexts.

Result:
`docs/strategy/ALL3_V9A_RESIDUAL_STRUCTURAL_CENSUS_RESULT_2026-09-20.md`.

### V9B — ACTIVE

Workflow: **`35517836947`**  
Launch commit: `fefc69744fb0b12bdd1c71141c53d0ff1083bd17`.

Frozen before causal outcomes:
- 16 representative states;
- earliest structural state from each hard context;
- repeated INSERT_DROP at turn 337 across all four;
- repeated QTY_UP at turns 427 and 698 across all four.

Config:
`configs/all3_v9b_representative_states.json`.

Each branch applies only one semantic category for one turn, then resumes ALL3.

Gate:
- same category loss->win in >=2 contexts => `V9B_CATEGORY_WL_REPEATABLE`;
- exactly one flip plus positive margin in >=2 contexts for same category => `V9B_CATEGORY_WL_NARROW`;
- zero W/L flips => `V9B_NO_WL_HEADROOM_CLOSE_ONE_TURN_STRUCTURAL`;
- unsupported single flip => close rather than tune state thresholds.

Margin-only evidence cannot advance.

No automatic Kaggle submission.

Preserve hosted pair:
- O-RW1 `56336027`;
- ALL3 `56367770`.

**Binding immediate action:** resolve workflow **`35517836947`**.


## Binding update — 2026-09-20 — O-LQ3C CLOSED / V9A ACTIVE

**This block supersedes lower stale current-action sections.**

### V8D FINAL CUMULATIVE — COMPLETE

Runs:
- V8D `35516560425`;
- E1 `35516899185`;
- E2 `35517228393`.

Across 216 paired contexts:
- failures 0;
- no score regressions;
- O-LQ3C unchanged throughout.

Final V48:
- 72 contexts;
- **6 fire contexts**;
- coverage minimum 4 => PASS;
- positive-score contexts 0;
- nonwin->win 0;
- negative-score contexts 0;
- mean score delta 0.

Decision: **`V8D_CONDITIONAL_ORDER_NO_WL_CONFIRMATION`**.

O-LQ3C is **CLOSED**:
- no more seeds;
- no threshold tuning;
- no modification of 4-SELL+6-HIRE eligibility;
- V8E remains dormant/not activated.

Result:
`docs/strategy/O_LQ3C_V8D_FINAL_CUMULATIVE_RESULT_2026-09-20.md`.

### V9A — ACTIVE

Pre-registered residual structural decomposition is now activated.

Workflow: **`35517515758`**  
Launch commit: `a551a38023ee268b43f71ed442b998a99d547a40`.

V9A is descriptive only:
- exact ALL3 baseline on the four frozen hard contexts;
- exact V48 shadow on the same candidate observations;
- V48 shadow action is never applied;
- classify residual differences as REORDER_ONLY, QTY_UP, QTY_DOWN, REPLACE, INSERT_DROP, MIXED_STRUCTURAL, OTHER;
- verify exact ALL3 replay against frozen hard-context margins/scores.

Gate:
- structural residuals in >=2 hard contexts => V9B causal category isolation;
- order-only residual => close richer structural imitation path accordingly;
- no residual difference => close this line;
- mechanics invalid => repair mechanics only.

No automatic Kaggle submission.

Preserve hosted pair:
- O-RW1 `56336027`;
- ALL3 `56367770`.

**Binding immediate action:** resolve workflow **`35517515758`**.


## Binding update — 2026-09-20 — V8D-E1 UNDERPOWERED / V8D-E2 FINAL ACTIVE

**This block supersedes lower stale current-action sections.**

### V8D-E1 — COMPLETE

Workflow: **`35516899185`**.  
Mechanical PASS: 72/72 paired contexts, failures 0.

E1:
- V48: 24 contexts, 0 fire contexts, score delta 0, margin delta 0;
- V47 mirror: 24 contexts, 0 fire contexts, score delta 0, margin delta 0;
- Ready Stock: 24 contexts, 0 fire contexts, score delta 0, margin delta 0.

Cumulative V8D + E1:
- V48 contexts = 48;
- V48 fire contexts = **2**;
- frozen minimum = 4;
- score regressions = 0.

Therefore O-LQ3C remains underpowered.

### V8D-E2 — FINAL EXTENSION ACTIVE

Workflow: **`35517228393`**  
Launch commit: `0d832a9c7732e124b018bad35a48321c3ee27ef5`.

Fresh seeds:
- `76025..76036`;
- both seats;
- V48, V47 mirror, Ready Stock;
- 72 additional paired contexts.

O-LQ3C is unchanged.

This is the **last permitted seed extension**.

Final cumulative gate:
- if V48 fire contexts remain <4 => `V8D_CONDITIONAL_ORDER_RARE_CLOSE`, close O-LQ3C, activate V9A;
- if coverage >=4 and W/L gate passes with zero regressions => activate V8E;
- if coverage >=4 but no W/L confirmation => close O-LQ3C, activate V9A;
- any score regression => close O-LQ3C, activate V9A.

No extension beyond E2.

Preserve hosted pair:
- O-RW1 `56336027`;
- ALL3 `56367770`.

**Binding immediate action:** resolve workflow **`35517228393`**. No manual Kaggle submission.


## Binding update — 2026-09-20 — V8D UNDERPOWERED / V8D-E1 ACTIVE

**This block supersedes lower stale current-action sections.**

### V8D — COMPLETE / UNDERPOWERED

Workflow: **`35516560425`**  
Decision: **`V8D_CONDITIONAL_ORDER_UNDERPOWERED`**.

Mechanical:
- PASS;
- 72/72 paired contexts complete;
- failures 0;
- score regressions 0.

By opponent:
- V48: 24 contexts, 2 fire contexts, mean score delta 0, mean margin delta +11.8333, no positive/negative score contexts;
- V47 mirror: 24 contexts, 2 fire contexts, mean score delta 0, mean margin delta +11.8333, no negative score contexts;
- Ready Stock: 24 contexts, 2 fire contexts, mean score delta 0, mean margin delta -2.0, no negative score contexts.

Overall:
- 6 fire contexts / 72;
- mean score delta 0;
- mean margin delta +7.2222;
- zero win->nonwin regressions.

The original gate required >=4 V48 fire contexts. Only 2 were observed, so this result is insufficient to confirm or reject O-LQ3C.

### V8D-E1 — ACTIVE

Workflow: **`35516899185`**  
Launch commit: `a295970e373f02974adc1a6b6186b11d08254348`.

Candidate O-LQ3C is unchanged.

Fresh extension:
- seeds `76013..76024`;
- both seats;
- V48, V47 mirror, Ready Stock;
- 72 additional paired contexts.

The strategic decision will be applied **cumulatively** to V8D + E1.

If cumulative activation reaches >=4 V48 fire contexts:
- positive W/L confirmation + no regressions => advance;
- no W/L confirmation => close O-LQ3C and activate V9A;
- any score regression => close O-LQ3C and activate V9A.

If still underpowered, one final unchanged E2 on seeds `76025..76036` is pre-authorized. No further extensions after E2.

V8E remains dormant and activates only on a cumulative V8D PASS.
V9A remains dormant unless O-LQ3C closes.

Preserve hosted pair:
- O-RW1 `56336027`;
- ALL3 `56367770`.

**Binding immediate action:** resolve workflow **`35516899185`**. No manual Kaggle submission.


## Binding update — 2026-09-20 — V8C PASS-NARROW / V8D ACTIVE

**This block supersedes lower stale current-action sections.**

### V8C — COMPLETE

Binding workflow: **`35516167350`**  
Head: `b528ac9dafedefd17b65dfa7407b1b793adb6046`

Decision: **`V8C_CONDITIONAL_ORDER_HEADROOM_NARROW`**.

Mechanical:
- PASS;
- 46 exact baseline-discovered one-shot branches;
- expected branches 46;
- failures 0.

Strategic:
- 1 loss->win flip;
- 6 positive-margin states across all 4 hard contexts;
- 37 negative-margin states;
- mean margin delta -113.1522.

Repeated strongest structural state:
- exact post-LQ2 nonempty market shape = **4 SELL + 6 HIRE**;
- no BUY / no other nonempty operation;
- MILK, WOOL and FERTILIZER all present;
- unchanged O-LQ3 would alter their relative order.

The only two V8C states with this exact shape were both positive:
- V48 75103/seat1: -86 -> +10 (**LOSS -> WIN**, +96);
- V48 75110/seat0: -484 -> -220 (+264).

### O-LQ3C — FROZEN

Candidate eligibility is the structural 4-SELL + 6-HIRE signature above. No seed, opponent identity, turn number, price threshold, rating, EpisodeId, future state or opponent-private state is used.

Treatment:
apply the unchanged O-LQ3 stable priority `MILK -> WOOL -> FERTILIZER` for eligible turns only.

Module:
`tools/first_party_lq3c_conditional_sell_order.py`.

### V8D — ACTIVE

Workflow: **`35516560425`**  
Launch commit: `6afd5dd1a4ab4776437c49aae9807e948d032d8f`.

Fresh frozen validation:
- seeds `76001..76012`;
- both seats;
- V48 primary;
- V47 mirror control;
- Ready Stock control;
- 72 paired contexts total.

Frozen PASS requires:
- all 72 contexts mechanically clean;
- >=4 V48 fire contexts;
- >=2 combined control fire contexts;
- V48 mean score delta >0;
- >=1 positive-score V48 context;
- zero win->nonwin regressions overall;
- zero negative-score contexts in V47 mirror;
- zero negative-score contexts in Ready Stock.

If activation is underpowered, only more untouched seeds may be added with the same frozen rule. If activation is sufficient but no W/L confirmation, O-LQ3C closes and pre-registered V9A activates. Any W/L regression closes O-LQ3C.

A V8D PASS does **not** automatically authorize Kaggle submission; it advances to broader regression/package readiness.

V9 remains pre-registered and dormant unless V8D closes O-LQ3C.

Preserve hosted pair:
- O-RW1 `56336027`;
- ALL3 `56367770`.

**Binding immediate action:** resolve workflow **`35516560425`**. No manual Kaggle submission.


## Binding update — 2026-09-20 — O-LQ3 CLOSED / V8C ACTIVE

**This block supersedes any lower stale "current", "binding next steps", or "immediate action" section.**

O-LQ3 Stage A workflow **`35480144515`** completed mechanically clean and is closed as **`O_LQ3_STAGE_A_FAIL`**:
- 4/4 frozen hard contexts replayed with zero failures;
- 12 O-LQ3 fires per context;
- loss->win flips: **0**;
- mean margin delta: **-1304.25**;
- V47 mirror 75113/seat1: -263 -> -374;
- V48 75103/seat1: -86 -> -2366;
- V48 75110/seat0: -484 -> -3187;
- V48 75113/seat1: -794 -> -917.

The V8B local direction **MILK -> WOOL -> FERTILIZER** is therefore **not** a globally safe priority. No post-result threshold/frequency rescue of O-LQ3 is permitted.

Initial V8C run **`35514319440`** is non-binding: it incorrectly inherited the 12-fires-per-context count from the cumulatively treated O-LQ3 trajectory. A first correction run **`35514495824`** is also non-binding because it preceded the aggregate-gate correction. No strategic branch outcome was used for this amendment. Baseline ALL3 discovery showed 11 fires in two seat-1 contexts, proving treated-trajectory fire count cannot define one-shot branch count.\n\nRun **`35514497453`** is also non-binding because the aggregate file contained a literal `\\n`, causing Python `SyntaxError` during the syntax step before any strategic simulation ran. The repaired binding execution is `35516167350`.\n\nThe binding next experiment is **V8C — Local Priority Value Atlas**, binding workflow **`35516167350`**, head commit **`b528ac9dafedefd17b65dfa7407b1b793adb6046`**.

V8C freezes the same four hard contexts and applies the unchanged O-LQ3 transform on **exactly one firing turn at a time**, then immediately resumes exact ALL3. Binding aggregate size is the exact sum of O-LQ3 firing states discovered on the untouched ALL3 baseline trajectories; every discovered state must be branched exactly once.

Frozen V8C decision:
- mechanics invalid, any context with zero baseline events, or branch count != exact baseline-discovered event count -> `V8C_MECHANICS_INVALID`;
- loss->win in >=2 distinct hard contexts -> `V8C_CONDITIONAL_ORDER_HEADROOM_REPEATABLE`;
- >=1 loss->win plus positive-margin states in >=2 contexts -> `V8C_CONDITIONAL_ORDER_HEADROOM_NARROW`;
- positive-margin states in >=2 contexts without a win flip -> `V8C_CONDITIONAL_ORDER_MARGIN_HETEROGENEOUS`;
- otherwise -> `V8C_CONDITIONAL_ORDER_NO_REUSABLE_HEADROOM`.

Only the first two strategic W/L branches may justify deriving **one** compact opponent-identity-free public-state condition, frozen before fresh-seed V8D validation. Margin-only evidence does not authorize a hosted candidate. If V8C finds no reusable W/L headroom, close this simple SELL-priority family rather than retune it.

Runtime robustness note: a community report suggested `obs["step"]` can be absent for seat 1, but our exact-engine V8A binding runs on `kaggle-environments==1.32.7` showed LQ2 firing normally in seat-1 contexts (97, 115 and 97 changed turns, with observed turns 577/600/673 etc.). Treat the report as an external portability warning, **not** as evidence of a current ALL3 failure. V8C targeting itself uses an internal deterministic turn counter.

V9 fallback is now pre-registered and **dormant** before the V8C result: `docs/strategy/ALL3_V9_RESIDUAL_STRUCTURAL_DECOMPOSITION_PROTOCOL_2026-09-20.md`. It activates only if binding V8C closes without reusable W/L headroom; otherwise it remains dormant.\n\nPreserve hosted pair:
- O-RW1 submission `56336027`;
- ALL3 submission `56367770`.

**Binding immediate action:** resolve binding workflow **`35516167350`** once complete; do not submit a new Kaggle candidate from O-LQ3/V8C discovery alone.


## Current solver handoff — 2026-09-19

Active branch: `research/prize-solver-v0`.

### Hosted pair — preserve both slots

Maturity snapshot around 100 episodes:
- CONTROL `56336025`: rating **2429.1**, 103 listed / 102 resolved external, 76-24-2;
- O-RW1 `56336027`: rating **2506.7**, 106 listed / 105 resolved external, 60-44-1.

These are not matched opponent populations. Raw W/L is not a causal A/B comparison.
The hosted treatment remains higher-rated; do not replace either slot while offline
selector/value work proceeds.

### Option-value Ryzen V1 — production PASS

User Ryzen run completed:
- 250/250 fresh seeds;
- 1,500 BASE matchups;
- **3,000 counterfactual option labels**;
- **584 unique state hashes**;
- **0 failures**.

O-RW1:
- mean score delta **+0.096**;
- 370 positive / 82 negative / 1,048 neutral;
- mean margin delta **-161.6493**.

O-TW1:
- mean score delta **+0.14**;
- 436 positive / 16 negative / 1,048 neutral;
- mean margin delta **+35.7173**.

Population decomposition:
- V47 mirror: mean score delta **+0.354**;
- V48: W/L delta 0;
- Tactical Memory: W/L delta 0.

### Selector Audit V1 — whole-seed PASS; cross-family gate still OPEN

Binding local rerun on 2026-09-19:
`OPTION_VALUE_SELECTOR_AUDIT_PASS_LEARNABLE_SEED_HOLDOUT`.

Whole-seed held-out test:
- 492 rows;
- selector realized delta **+0.1341463**;
- always-fire delta **+0.1138211**;
- row oracle **+0.1382114**;
- **132/136** positive rows captured;
- **0/24** negative rows fired;
- nonzero sign accuracy **0.9625**;
- selected ridge lambda **0.1**, threshold **0.1**.

The state-grouped diagnostic remains strong:
- selector realized delta **+0.1372981**;
- **187/187** positive rows captured;
- **0/17** negative rows fired.

This establishes learnability across fresh whole seeds in the V1 sampled population. It does **not**
yet establish transfer to an unseen opponent family: the original leave-one-opponent-out diagnostic
still failed to recover the V47-mirror gains when that family was fully withheld.

### Ryzen V2 option-value production — COMPLETE / MECHANICS PASS / COVERAGE LIMIT FOUND

Binding user Ryzen run from source commit
`2c402f54462bb31be4f1061c64efe11613b24253`:

- 150/150 fresh seeds;
- 7 opponents;
- both seats;
- O-RW1 + O-TW1;
- 2,100 base matchups;
- **4,200 counterfactual labels**;
- **1,238 unique state hashes**;
- **0 failures**;
- exact engine `1.32.7`.

O-RW1:
- mean score delta **+0.0352381**;
- 208 positive / 60 negative / 1,832 neutral;
- mean margin delta **-88.5776**.

O-TW1:
- mean score delta **+0.0571429**;
- 253 positive / 16 negative / 1,831 neutral;
- mean margin delta **+85.7710**.

Critical population result:
- V47 mirror: **458 positive / 76 negative**, mean score delta **+0.3183333**;
- Ready Stock: 2 positive / 0 negative;
- `2715.6`: 1 positive / 0 negative;
- V48, Conditional Memory, Tactical Memory, Best Market: W/L-neutral.

Thus **458/461 positive labels (99.35%) are V47-mirror labels**.
Outside V47 there are only **3 positives in 3,600 rows** and no negative W/L labels.

Binding interpretation:
- V1 seed-holdout learnability was real;
- more seeds on the same two-option library are **not** the current bottleneck;
- a production multi-family selector is blocked by **option coverage**, not raw model capacity;
- do not scale this exact dataset merely by brute force.

Result:
`docs/strategy/OPTION_VALUE_RYZEN_V2_RESULT_2026-09-19.md`.

### G1 — option-library composition: BINDING RESULT

Binding evidence comes from the seven successful shards of workflow **`35426256016`**.
The aggregate job failed only because the lightweight aggregate environment omitted
`kaggle-environments`; the seven strategy shards themselves were all mechanically clean.

56 matched contexts total:
- BASE score rate: **0.7857143**;
- O-RW1: **0.8392857**;
- O-TW1: **0.8392857**;
- BOTH: **0.8392857**;
- BOTH vs BASE: **+0.0535714**;
- score-regressing opponent blocks: **0/7**.

Mirror block:
- BASE **0.500**;
- RW1/TW1/BOTH **0.875**.

Binding decision: **`OPTION_LIBRARY_COMBO_ADVANCE`**.

Interpretation:
- retain O-RW1 + O-TW1 together as the current **offline option-library host**;
- composition is W/L-safe on this gate;
- BOTH adds no W/L over the best single option in this sample;
- no hosted Kaggle submission follows from this alone.

Result doc:
`docs/strategy/OPTION_LIBRARY_COMBO_RUNTIME_V0_RESULT_2026-09-19.md`.

### G2 — adaptive wrapper proposal oracle V3: BINDING RESULT

Valid workflow **`35426189093`**:
- 56 branch states;
- 84 exact candidate rollouts;
- zero failures;
- exact engine `1.32.7`;
- mechanical PASS.

Decision: **`WRAPPER_PROPOSAL_OUTSIDE_MARGIN_ONLY`**.

Overall:
- score delta **0.0**;
- nonwin→win flips **0**;
- 8 positive-margin states;
- mean oracle margin delta **+393.39**.

Outside modern41:
- BASE and oracle score rate both **1.0**;
- score delta **0.0**;
- 8/32 positive-margin states;
- mean oracle margin delta **+688.44**.

All promoted proposals came from `router_2715`, at step 0:
- V47: `BUY_PRODUCT WHEAT 7; SELL WHEAT 2`;
- router proposal: `BUY_PRODUCT WHEAT 13; SELL WHEAT 13; BUY_PRODUCT WHEAT 13`.

That proposal improved margin against weaker outside blocks but was harmful against the
hard strata V47 mirror, Ready Stock and V48. It is **not** a promotable generic option.

Result doc:
`docs/strategy/ADAPTIVE_WRAPPER_PROPOSAL_V3_RESULT_2026-09-19.md`.

### V4 activation — hard-stratum discovery

The conditional V4 protocol is now **activated in staged form** because valid V3 produced
no W/L headroom.

Evidence-driven amendment made before V4 execution:
- discovery now targets hard BASE non-win strata rather than arbitrary family diversity;
- highest priority is **V48**, where valid V3 lost by small margins and one-turn proposals
  did not flip the result;
- broad family testing moves to the regression/generalization stage after a causal option
  is discovered.

Protocol:
`docs/strategy/ADAPTIVE_TRANSACTION_SEARCH_V4_PROTOCOL_2026-09-19.md`.

### V47×V48 divergence census: BINDING RESULT

Workflow **`35439729714`** completed SUCCESS on fresh seeds `73001..73004`, both seats.

Decision: **`V48_CENSUS_MARKET_SEARCHABLE`**.

Hard-block result:
- V47 score rate vs V48: **0.0**;
- **0W / 0T / 8L**;
- mean margin **-454.0**;
- **458** same-farmer/hands market divergences;
- **0** farmer/hands divergences;
- zero failures.

The first market divergence appears around step 253/323, with many recurrent later
divergences. The observed V48 pattern repeatedly clears impossible/stale SELL slots or caps
huge V47 quantities (for example `SELL WHEAT 1000`) to feasible current inventory.

Result doc:
`docs/strategy/V47_V48_DIVERGENCE_CENSUS_V1_RESULT_2026-09-19.md`.

### O-CQ1 Queue Clamp/Clear — CLOSED AT PARITY

Workflow **`35439945148`** completed mechanically clean.

Binding decision: **`CQ1_PARITY_FAIL`**.

Against exact V48 action output on fresh audit seeds:
- V48 market-divergence rows: **456**;
- CQ1 changed rows: **1,356**;
- exact V48 matches: **288**;
- false-positive changes: **900**;
- changed-but-not-exact: **168**;
- missed V48 changes: **0**;
- precision: **0.21239**;
- recall: **0.63158**;
- failures: **0**.

The prepared O-CQ1 causal workflow is **NOT RUN** and remains dormant/non-binding.

Mechanistic diagnosis:
- current pre-action shed alone is the wrong availability state;
- Kaggriculture resolves farmer/hand actions before market;
- `DROP`, shed-adjacent `PLACE`, and `PICKUP` can alter shed before SELL;
- market slots execute in order, so an earlier `BUY_PRODUCT` can feed a later SELL;
- V48 also selectively clears/compacts the queue rather than applying a universal clamp.

### O-CQ2 — projected queue sanitation

New development hypothesis:
1. project own shed through the exact current V47 farmer/hands actions using only legal own state;
2. project earlier market inventory-changing slots before later SELLs;
3. test alternative SELL sanitation forms:
   - slotwise clamp;
   - clamp + compaction;
   - same-product shortage merge + compaction;
4. evaluate a small pre-frozen activation-threshold grid;
5. choose one configuration only on development seeds;
6. freeze it and validate on separate untouched seeds before any causal W/L gate.

This is still a **parity/mechanism** stage, not a performance-training stage.

The generic V4A multi-turn market oracle remains prepared but **dormant pending CQ2**.
It should run only if a compact first-party sanitation mechanism cannot explain enough of V48.

### Binding next steps

1. Run O-CQ2 development parity matrix.
2. Freeze exactly one sanitation rule + activation condition from that development result.
3. Validate the frozen rule on separate fresh seeds.
4. If validation parity is strong, open fresh causal V48 W/L gate.
5. If validation parity is weak, activate the already-prepared V4A bounded multi-turn oracle.
6. Keep O-RW1 + O-TW1 as current offline host.
7. No new Kaggle submission; preserve active hosted slots.

### ALL3 — HOSTED STATE

Current intended active pair:
1. O-RW1 `56336027`;
2. ALL3 `56367770`.

Latest hosted snapshot:
- ALL3 **2412.1**;
- O-RW1 **2361.6**.

These live ratings are observational and come from different histories/populations.

ALL3 first-informative checkpoint remains:
- 35 listed public episodes;
- 34 resolved external games;
- 28W / 6L / 0T;
- raw score rate 0.8235294;
- 33 unique opponents;
- mean margin +13,626.97.

### O-HV1 — CLOSED

Binding:
`O_HV1_DEV_CLOSE`.

No threshold/product rescue.

Result:
`docs/strategy/O_HV1_HIGH_VALUE_STOCK_FLUSH_RESULT_2026-09-19.md`.

### O-PC1 — CLOSED

Binding:
`O_PC1_DEV_CLOSE`.

Fresh paired result:
- mean score delta -0.25;
- 6 negative-score contexts;
- 0 positive-score contexts.

No ratio/start-step/yield rescue.

Result:
`docs/strategy/O_PC1_PROFIT_DOMINANT_CROP_ROTATION_RESULT_2026-09-19.md`.

### V5 Physical Proposal Oracle — CLOSED MARGIN-ONLY

Corrected binding runs:
- `35470046629`;
- `35470051852`.

Both agree exactly:
**`V5_PHYSICAL_MARGIN_ONLY`**.

Overall:
- 32 branch states;
- base score rate 0.9375;
- oracle score rate 0.9375;
- score delta 0;
- nonwin->win flips 0;
- loss->win flips 0;
- mean oracle margin delta +505.65625;
- median 0;
- 14 positive-margin states.

By opponent:
- router_2715: +1,317.625 mean margin, no W/L gain;
- Tactical Memory: +694, no W/L gain;
- V47 mirror: +11, no W/L gain;
- V48: 0 margin gain, no W/L gain.

Only non-winning V5 base trajectory:
- V48;
- seed 75002;
- seat 0;
- final margin -26.

No one-turn physical branch changed that result.

Therefore:
- do not promote V5 transforms;
- do not first-party PASS/movement micro-patches;
- close one-turn localized physical substitution as an option source.

Result:
`docs/strategy/ALL3_PHYSICAL_PROPOSAL_ORACLE_V5_RESULT_2026-09-19.md`.

### V6A hard-context census — COMPLETE

Binding runs:
- Batch A `35472777632`;
- Batch B `35473134791`.

Combined:
- 224 exact ALL3 games;
- **220W / 4L / 0T**;
- mechanical PASS;
- decision **`V6A_HARD_CONTEXTS_READY`**.

Frozen hard contexts:
1. V47 mirror — seed `75113`, seat 1, margin -263;
2. V48 — seed `75103`, seat 1, margin -86;
3. V48 — seed `75110`, seat 0, margin -484;
4. V48 — seed `75113`, seat 1, margin -794.

Config:
`configs/all3_v6_hard_contexts.json`.

Result:
`docs/strategy/ALL3_V6A_HARD_CONTEXT_CENSUS_AB_RESULT_2026-09-19.md`.

### V6 bounded physical continuation — CLOSED

Binding lifecycle-corrected workflow:
`35473780009`.

Decision:
**`V6_CONTINUATION_MARGIN_ONLY`**.

Mechanical:
- PASS;
- failures 0;
- 4 frozen hard contexts.

Strategic:
- loss->win flips: 0;
- mean oracle margin delta: +68.5.

Best hard-context outcomes:
- V47 mirror -263 -> -96;
- V48 -86 -> -76;
- V48 -484 -> -484;
- V48 -794 -> -697.

Therefore:
- close one-locus H2/H3 continuation as a W/L source;
- do not extend horizon automatically;
- do not promote margin-only physical patches.

Result:
`docs/strategy/ALL3_V6_BOUNDED_PHYSICAL_CONTINUATION_RESULT_2026-09-19.md`.

### V7 option-composition attribution — CLOSED

Workflow:
`35479297555`.

Decision:
**`V7_STATIC_COMPOSITION_MARGIN_ONLY`**.

No non-ALL3 composition rescued any of the four hard losses.

Mean margins:
- ALL3 -406.75;
- best alternative TW_LQ2 -399.75;
- LQ2 -420.5;
- V47 -1520.25.

Interpretation:
LQ2 is the dominant value-producing mechanism; static suppression is not the residual W/L answer.

Result:
`docs/strategy/ALL3_V7_OPTION_COMPOSITION_ATTRIBUTION_RESULT_2026-09-19.md`.

### V8A LQ2 residual SELL-run census — COMPLETE

Workflow:
`35479557496`.

Decision:
**`V8A_ORDER_SEARCH_READY`**.

Aggregate:
- 424 LQ2-changed turns;
- 170 eligible post-LQ2 multi-product SELL-run states;
- all 4 hard contexts represented;
- max 6 distinct products in one SELL run.

Frozen V8B states:
- context 0: steps 673, 577;
- context 1: steps 673, 600;
- context 2: steps 673, 600;
- context 3: steps 673, 577.

Config:
`configs/all3_v8b_lq2_order_states.json`.

Result:
`docs/strategy/ALL3_V8A_LQ2_RESIDUAL_SELL_RUN_CENSUS_RESULT_2026-09-19.md`.

### V8B LQ2 SELL-order oracle — COMPLETE

Workflow:
`35479783995`.

Decision:
**`V8B_ORDER_HEADROOM_NARROW`**.

Mechanical:
- PASS;
- zero failures;
- 1 / 4 hard-context loss->win flip;
- mean best-branch margin delta +96.

Strongest results:
- V48 75103/seat1, step 600: FERTILIZER 11 <-> WOOL 7, **-86 -> +10**;
- V48 75110/seat0, step 600: WOOL 7 <-> MILK 16, **-484 -> -220**.

The shared local direction is:
**MILK -> WOOL -> FERTILIZER**.

Result:
`docs/strategy/ALL3_V8B_LQ2_SELL_ORDER_ORACLE_RESULT_2026-09-19.md`.

### O-LQ3 priority SELL ordering — STAGE A ACTIVE

Workflow:
**`35480144515`**.

Candidate:
within each post-LQ2 SELL run, stable-sort only orders currently occupying MILK/WOOL/FERTILIZER
slots by fixed public priority:

`MILK -> WOOL -> FERTILIZER`.

Invariants:
- non-target products remain in their original slots;
- quantities unchanged;
- non-SELL slots unchanged;
- farmer/hands unchanged;
- market multiset unchanged;
- no opponent identity.

Stage A:
exact paired ALL3 vs ALL3+LQ3 replay on the four frozen hard contexts.

Gate:
- >=1 loss->win and positive mean margin delta -> Stage A PASS and fresh paired Stage B;
- zero flips but positive mean delta -> directional-only, narrow the legal-state condition;
- nonpositive mean or mechanics invalid -> fail.

No Kaggle submission is authorized by Stage A.

### Binding next steps

1. Resolve V6A `35472681958`.
2. If >=4 fresh nonwins: freeze selected hard-context list exactly.
3. Run bounded 2–3-turn localized physical continuation oracle only on those contexts.
4. If <4: expand untouched seed census before branching.
5. Preserve O-RW1 + ALL3 hosted pair.
6. No new Kaggle submission from V5/V6A discovery evidence.

## Historical record (superseded where inconsistent with the current handoff)

Updated: 2026-09-15

## Mission / objective

Maximize the probability of winning or reaching the prize frontier in Kaggriculture. Novelty is not the objective. Every legal piece of accumulated competitive, replay, mechanics and economic knowledge remains admissible unless stronger evidence supersedes it.

Authoritative branches:

- competitive source of truth: `fix/kaggle-parity-v1`
- experimental mechanics/integration: `research/first-principles-economy-v1`

## Engine / legality lock

- official evaluation path: `kaggle-environments==1.32.7`
- frozen upstream reference commit: `28b6d8af3ce73926b3d0fda1410c1ddd8384ab8c`
- public `town.unlocked_shops` is shared/legal runtime state and may contain repeated shop names
- no runtime identity, rating, EpisodeId, hidden seed, future state or direct opponent-private features
- original final holdout remains sealed

## Competitive target / calibration

Frozen external snapshot 2026-09-14: leader ~`3191`, rank 10 ~`2958`; target remains roughly `3000+`.

Strongest exact project-hosted anchor:

- **CR053_REAL** — submission `56073870`, checkpoint ~`2064.8`
- exact SHA `095080e791bd8d58369893c1a421beb57b7f64c2808c011f576e09684ffb9a15`
- source run `34105008373`, artifact `10012004237`

Other exact anchors: CR052_REAL ~`1749.2`; CR083 ~`1619.9`; CR086 ~`1612.6`.

Critical warning: exact-byte league `34802917553` locally ranked CR083/CR086 above CR053 although hosted Kaggle ranks CR053 materially higher. Local H2H is useful for mechanics, causal interventions, catastrophe and diversity, **not** as a hosted-rating oracle.

## Retained competitive / FP001 knowledge

- CR086 legal latent-opponent-supply estimator and SELL-priority operator are retained; CR086 itself is not the preferred backbone.
- CR087/CR088 elite macro/replay knowledge is retained; direct tape backbones remain closed.
- H1 WHEAT town-pulse carry, H1B sale deferral, H8/B3+DAILY CARE, H9 demand representation, H10 batching/routing, H11 fertilizer conversion and M6S1 remain reusable primitives/modules.
- M6S1 is a genuine economic module, not a standalone competitive backbone.

## CR089 — COMPLETE / FAIL

Run `34923802262`: C5_BASE and C5_M6S1 each **0W–132L**, 11/11 zero-score edges, zero mechanical failures. Static C5/C5+M6S1 are closed as competitive backbones; M6S1 survives as a module.

## CR090 — COMPLETE / FAIL

Run `34979280512`. Mechanics exact. YARN adaptive SHEEP minus delayed COW was negative; MILK adaptive COW minus delayed SHEEP strongly positive; natural adaptive policy did not beat delayed COW.

Binding verdict: `CR090_H9_CAUSAL_FAIL_CLOSE_SIMPLE_SPECIES_ADAPTATION`. No threshold rescue; H9 survives only as a state feature/prior.

## CR091 — COMPLETE / PASS

Binding rerun: **`34990757344`**, research commit `f49bff2e7adde626b01b9fa3c0413f7fc97d9649`.

Artifact: `cr091-hierarchical-market-option-gate-v1`, ID `10406926564`, ZIP SHA-256 `d6d9a5a7cb187e48dc4cb187e348adb7fff4d10666f18f27b4030ccc8ad2f3d0`.

The earlier run `34987640694` remains invalid/non-binding because its direct-`exec()` harness failed CR052 package semantics.

CR091 compared exact CR053 against exact CR053 plus the exact CR086 latent-supply SELL-priority operator, changing only the order of existing market orders.

Mechanics on the valid rerun:

- 128/128 episodes valid;
- failures: **0**;
- parity violations: **0**;
- exact farmer/hand parity every call;
- exact normalized market-order multiset parity every call;
- exact BASE full-action parity every call;
- O1 active with **1,075** market reorders.

Seat-balanced edge-score deltas `O1 - BASE`:

- CR052_REAL: `0.0000`
- CR053_REAL: `+0.1875`
- CR083: `0.0000`
- CR086: `0.0000`

Summary: 4/4 nonnegative edges, mean delta `+0.046875`, maximum `+0.1875`, worst regression `0.0`.

Binding verdict: **`CR091_LATENT_OPTION_TRANSFER_PASS_ADVANCE_ROUTER`**.

Interpretation: CR086 is not promoted as a backbone. Its latent-priority mechanism is promoted as frozen separable option **O1** on exact CR053. No threshold retuning.

Result: `docs/strategy/CR091_HIERARCHICAL_MARKET_OPTION_RESULT_2026-09-15.md`.

## Current binding gate — CR092 broad O1 transfer / router labels

Protocol: `docs/strategy/CR092_BROAD_OPTION_ROUTER_LABEL_PROTOCOL_2026-09-15.md`.

Purpose: test frozen O1 on the broader 11-edge CR089 population and collect causally clean public-state labels for a later router.

Frozen population:

- exact anchors: CR053_REAL, CR052_REAL, CR083, CR086;
- macro reps: `r01`, `r02`, `r03`, `r06`, `r07`, `r09`, `r10` from the exact CR089 frozen population artifact `10378299284`.

Fresh evaluation:

- seeds `91401..91406`;
- both seats;
- 12 games/treatment/edge;
- 132 games per treatment, 264 total;
- exact hosted-faithful package runner;
- no hosted submission.

Counterfactual label rule: for each matched BASE/O1 episode, record O1's legal state immediately before its first actual market reorder. A label is admissible only if that strategic-state hash exactly matches BASE's state hash at the same step. Primary label is `outcome(O1) - outcome(BASE)`; terminal money is diagnostic only. Opponent ID is offline stratification metadata only and is forbidden as a router feature.

Frozen broad-survival gate requires mean edge delta >= `+0.02`, >=8/11 nonnegative edges, worst regression >= `-0.125`, macro mean delta >=0 and no new zero-score catastrophe from a BASE edge >=0.25.

Frozen routing signal requires at least 8 positive and 8 negative hash-valid labels spanning at least two opponent strata per sign.

Implementation on research branch:

- `tools/cr092_broad_option_edge.py`
- `tools/cr092_aggregate.py`
- `.github/workflows/cr092-broad-option-router-label.yml`
- workflow/head commit `b42347617a6967eeb2862fde23737c7538d3b9d3`
- active run **`35015135956`**
- prepare job already PASS: all 11 opponent packages downloaded and SHA-verified.

Frozen outcomes:

- broad survivor + heterogeneous labels -> `CR092_BROAD_PASS_HETEROGENEOUS_ADVANCE_ROUTER`
- broad survivor without downside support -> `CR092_BROAD_PASS_O1_ADVANCE_NEXT_OPTION`
- broad fail but strong heterogeneous option value -> `CR092_BROAD_FAIL_HETEROGENEOUS_ADVANCE_ROUTER_DISCOVERY`
- otherwise -> `CR092_BROAD_FAIL_CLOSE_ALWAYS_ON_O1`
- mechanics failure -> no strategic verdict.

## Closed / do-not-retune absent new evidence

CR078/079, CR080 replay stitching, CR081 static market-prefix transplant, CR082 1-NN imitation, CR084 FEED rescue, CR085 Pareto gating, direct CR088 tapes, static C5/C5+M6S1, fixed C3S2/C2S3, simple CR090 first-shop species rule.

## Hosted policy

No CR092 outcome automatically authorizes a Kaggle submission. Hosted slots remain high-information population sensors, used only after a mechanically exact state-adaptive or multi-option candidate survives broad fresh-seed evaluation without a major catastrophe edge.
