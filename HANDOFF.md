# HANDOFF — Kculture



## Binding update — 2026-09-22 — V28C COMPLETE / FINAL PAIR ACTIVE / MATURITY WATCH

**This block supersedes lower stale current-action sections.**

### V28C — COMPLETE

Authorized exact-V47 submission:
- workflow `35739943846`;
- submission **`56466970`**;
- status **COMPLETE**;
- initial listed publicScore **600.0**.

Verified latest-two active pair:
1. exact V47 `56466970`;
2. ALL3 `56367770`.

O-RW1 `56336027` remains outside the latest two.

At the same read-only snapshot, ALL3 was COMPLETE with listed publicScore **1988.8**.

### V28C maturity audit — INITIAL SCORE NOT DECISION-GRADE

Read-only workflow:
**`35740643501`**.

Snapshot UTC:
`2026-09-22T14:29:32.606521+00:00`.

Listed public episode counts:
- new V47 `56466970`: **1**;
- ALL3 `56367770`: **382**;
- historical exact V47 `56336025`: **169**;
- historical exact V47 `56333577`: **36**.

Therefore the new V47 score of 600.0 is based on only one listed episode and is **not mature enough to justify reversing the slot decision**. The bytes, internal main.py hash, and loader were already verified exact before submission.

Current strategy remains:
**ALL3 primary + V47 hedge**.

No additional Kaggle submission is authorized.

**Binding immediate action:** monitor V47 `56466970` read-only as its episode count/rating matures. Re-evaluate only on a meaningful maturity checkpoint or active-pair drift; do not react to the one-episode score.

## Binding update — 2026-09-22 — V28C SUBMITTED / V47 REGISTERED / COMPLETION WATCH

**This block supersedes lower stale current-action sections.**

The user explicitly authorized the frozen V28B recommendation. V28C executed that authorization successfully.

### V28C — EXACT V47 FINAL HEDGE REGISTERED

Workflow:
**`35739943846`**.

Launch commit:
`d5d23b2ce570cceac34dd03a90f80f630aebc779`.

Result document:
`docs/strategy/V28C_FINAL_V47_SLOT_SUBMISSION_RESULT_2026-09-22.md`.

Provenance artifact:
- ID `10699168127`;
- digest `sha256:a24b5f90a57beae66f475ac8f39337c4b0946e330e9d9267871eb0e5af8dd96d`.

Strict preflight passed:
- latest two before mutation = ALL3 `56367770` then O-RW1 `56336027`;
- daily count projected = 1/5;
- exact V47 archive SHA = `08e56c43ecf28253605b61066dd769334d96262056b8cd337489f1f4f909ad01`;
- exact V47 `main.py` SHA = `f4ecd4876fde93a14e3381993283f3b6a1afa023b48dd57217f4d90794d39842`;
- official loader entrypoint = `_y_agent_shopherd`.

New exact-V47 submission:
**`56466970`**.

Initial registered status:
**PENDING**.

Verified latest-two immediately after registration:
1. V47 `56466970`;
2. ALL3 `56367770`.

O-RW1 `56336027` is no longer among the latest two.

The intended active pair is therefore now:
**ALL3 primary + V47 hedge**.

No additional Kaggle submission is authorized by this result.

**Binding immediate action:** monitor submission `56466970` read-only until it leaves PENDING, then re-audit the latest-two pair/current ratings and update the canonical sources. Do not create a third final-slot mutation without a new gate and explicit authorization.

## Binding update — 2026-09-22 — V27 CLOSED / V28B FINAL PAIR READY / USER DECISION REQUIRED

**This block supersedes lower stale current-action sections.**

### V27C — CLOSED

Binding workflow:
`35725924827`.

Decision:
**`V27C_BEHAVIORAL_DISTILLATION_DATA_TOO_COMPLEX`**.

Mechanical:
- 96/96 trajectories;
- 69,024 labeled turns;
- 0 failures;
- H=256 legal history representation;
- duplicate-feature conflict rates 0.0 for complete/MARKET/FARMER/HANDS.

But fast cross-seed distillation fails:
- unique complete labels: 2597;
- validation decomposable coverage: 0.6358368104;
- test decomposable coverage: 0.6021094112;
- step-modal complete-action test accuracy: 0.3561659713.

Therefore V27D remains dormant and fast rank-1 behavioral cloning is CLOSED.

Result:
`docs/strategy/V27C_BOUNDED_HISTORY_BEHAVIORAL_DISTILLATION_CENSUS_RESULT_2026-09-22.md`
(commit `53716433748bed5b57665f331d2f77b09b75fd02`).

### V28A — READ-ONLY FINAL-SLOT AUDIT COMPLETE

Workflow:
`35683053247`.

Current active/latest pair at audit:
1. ALL3 submission `56367770` — publicScore 2050.6;
2. ORW1 submission `56336027` — publicScore 2014.4.

Historical exact-V47 calibration:
- `56336025`: 2344.6;
- `56333577`: 2387.9.

Audit confirmed:
- only latest 2 submissions remain active/tracked;
- team final score uses the better of the 2 active submissions;
- the second slot is a hedge.

### V28B — COMPLETE / FINAL PAIR RECOMMENDATION READY

Binding workflow:
**`35683424225`**.

Decision:
**`V28B_FINAL_PAIR_RECOMMENDATION_READY`**.

Fresh common panel:
- 12 current executable frontier sources;
- seeds 80301..80306;
- both seats;
- 144 contexts per candidate;
- 0 failures.

Metrics:
- ALL3: score rate 0.4444444, 64-80-0, mean margin **+26.3750**;
- V47: score rate 0.4444444, 64-80-0, mean margin **-62.7986**;
- ORW1: score rate 0.4444444, 64-80-0, mean margin **-70.3681**.

Frozen selector:
- PRIMARY = **ALL3**;
- HEDGE = **V47**.

Recommended active pair:
**ALL3 + V47**.

Current active pair:
**ALL3 + ORW1**.

Thus the only recommended slot change is:
replace ORW1 with exact V47, while preserving ALL3.

No Kaggle submission has been made.

**Binding immediate action:** USER DECISION REQUIRED — explicitly authorize or reject changing the active pair from ALL3 + ORW1 to ALL3 + V47.


## Binding update — 2026-09-22 — V27B BOUNDED HISTORY PASS / V27C ACTIVE

**This block supersedes lower stale current-action sections.**

### V27B — COMPLETE / BOUNDED LEGAL HISTORY VIABLE

Corrected binding shard workflow:
**`35676166396`**.

Corrected aggregate-only workflow:
**`35725538992`**.

Decision:
**`V27B_BOUNDED_LEGAL_HISTORY_DISTILLATION_VIABLE`**.

Selected horizon:
**`H=256`**.

H=256:
- complete-action parity: 0.9962962963;
- MARKET parity: 0.9962962963;
- FARMER parity: 1.0;
- HANDS parity: 1.0;
- minimum source complete-action parity: 0.9777777778;
- minimum checkpoint complete-action parity: 0.9444444444.

H=128 fails the frozen gate.
FULL history parity is 1.0.

Result:
`docs/strategy/V27B_LEGAL_HISTORY_RECONSTRUCTIBILITY_RESULT_2026-09-22.md`
(commit `ad073ddc19f5ff1ca4f0364aad9a2d846652f4cf`).

### V27C — ACTIVE / BOUNDED-HISTORY DISTILLATION CENSUS

Protocol:
`docs/strategy/V27C_BOUNDED_HISTORY_BEHAVIORAL_DISTILLATION_CENSUS_PROTOCOL_2026-09-22.md`
(commit `5ab18ce72a162980d6e2a25cac2cec073f92b102`).

Binding workflow:
**`35725924827`**.

Frozen history window:
**256 legal prior observations**.

Fresh census seeds:
`79901..79904`, both seats, all 12 immutable V26A opponents.

Representation:
- current 114 programme features;
- lags 1/4/16/64/128/256;
- per-feature min/max/mean/window delta;
- 1254-dimensional legal numeric state;
- no source/rank/SHA/opponent identity feature.

V27C is a compactness/label-conflict census only. If it passes, V27D fits exactly one pre-frozen component-wise tree model family. If it fails, fast rank-1 behavioral distillation closes.

No Kaggle submission is authorized.

**Binding immediate action:** resolve workflow `35725924827`.


## Binding update — 2026-09-22 — V28A AUDIT COMPLETE / V28B ACTIVE

**This block supersedes lower stale current-action sections.**

### V28A — COMPLETE / READ-ONLY CURRENT COMPETITION AUDIT

Binding workflow: **`35683053247`**.  
Artifact: `10675491726`.  
Digest: `sha256:53914e363c1104f0d4c49307a923ed28a51d391d6b3903282a014cc0a9df0c54`.

Current team:
- rank **1629 / 9795**;
- displayed score **2050.6**;
- active/latest pair:
  - ALL3 submission `56367770`: 2050.6;
  - O-RW1 submission `56336027`: 2014.4.

Historical calibration:
- exact V47 `56336025`: 2344.6;
- exact V47 `56333577`: 2387.9;
- CR053 `56073870`: 2064.8.

Current public #1 at audit: **3188.5**.

Official final-evaluation rule:
- only latest 2 submissions remain active/tracked;
- team score is the better of the two active submissions;
- second slot is a hedge with no downside;
- final Bradley-Terry uses episodes between agents that remain active.

Result:
`docs/strategy/V28A_FINAL_SLOT_READONLY_AUDIT_RESULT_2026-09-22.md`
(commit `788f11bded40dcc2027e1f51388d5a7512210b33`).

### V28B — ACTIVE / FRESH FINAL-SLOT CANDIDATE BENCHMARK

Protocol:
`docs/strategy/V28B_FRESH_FINAL_SLOT_CANDIDATE_BENCHMARK_PROTOCOL_2026-09-22.md`
(commit `52b3cdbcab9fd7df59e763c15976573934c14f0c`).

Binding workflow:
**`35683424225`**.  
Launch commit:
`405335b3c031df3ab0357822b117021bcc362c98`.

Candidates:
- exact V47;
- exact V47 + O-RW1 only;
- ALL3 = V47 + O-RW1 + O-TW1 + O-LQ2.

Fresh seeds:
`80301..80306`, both seats.

Fresh current-frontier snapshot:
- up to 12 unique executable sources;
- minimum 8;
- exact SHA snapshot before episodes.

Frozen pair selector:
- primary: overall score rate -> source breadth -> seed breadth -> mean margin -> lexical;
- hedge: wins in contexts where primary is non-win -> overall score rate -> source breadth -> mean margin -> lexical.

No Kaggle submission is authorized.

**Binding immediate action:** resolve workflow `35683424225`.


## Binding update — 2026-09-21 — V27C2 CLOSED / FINAL-SLOT STRATEGY ACTIVE

**This block supersedes lower stale current-action sections.**

### V27C2 — COMPLETE / STRUCTURAL DISTILLATION NOT VIABLE

Binding workflow: **`35682535729`**.  
Train job: `106603317949`.  
Final artifact: `10675616361`.  
Digest: `sha256:4a40b1156a52b2bb26ae5473d7bf339e2dab8d1b84b448f53d268ca1b7de434c`.

Mechanical:
- 12/12 collectors PASS;
- 192/192 teacher episodes;
- no runtime identity;
- no teacher call at inference.

Decision:
**`V27C2_STRUCTURAL_POLICY_DISTILLATION_NOT_VIABLE`**.

Untouched holdout:
- complete-action parity: **0.5734817**;
- MARKET: **0.6978442**;
- FARMER: **0.9541029**;
- HANDS: **0.7493046**;
- minimum source complete parity: **0.5625869**;
- minimum 120-turn stage parity: **0.1454861**.

Result:
`docs/strategy/V27C2_STATEFUL_STRUCTURAL_DISTILLATION_RESULT_2026-09-21.md`
(commit `a2a7053c3bda8cadfe983798df3e2afc3ff691c3`).

Per frozen routing:
- V27D remains DORMANT and MUST NOT be activated;
- no tree/history/feature sweep;
- no source-conditioned distillation;
- fast rank-1 behavioral distillation is CLOSED for this competition.

### Active next stage — final-slot / competition strategy

The technical solver branches V23–V27 have now resolved:
- additive ALL3 options cannot transfer persistent teacher headroom;
- PrizeSolverV4 is not competitive;
- source-agnostic teacher consensus is not competitive;
- compact interaction control is not identity-free;
- rank-1 bounded legal history is reconstructible but not compressible by the frozen fast first-party distillation route.

The next work is a read-only current competition audit:
- verify current leaderboard/frontier;
- verify our current submissions / ratings / ordering;
- verify which two submissions would currently count under the competition final-evaluation rule;
- preserve the strongest proven candidates;
- identify whether any final submission action is actually justified.

No Kaggle submission is authorized without explicit user approval.


## Binding update — 2026-09-21 — V27C WHOLE-LABEL CLOSED / V27C2 STRUCTURAL ACTIVE

**This block supersedes lower stale current-action sections.**

### V27C whole-component classification — CLOSED / COMPUTATIONAL MECHANICS INVALID

Binding collection workflow:
`35678874775`.

Preserved evidence:
- 12/12 data shards PASS;
- 192 teacher episodes;
- no validation/holdout model result was ever produced.

Both frozen training attempts reached the identical matrix:
- 57,520 training turns;
- 2,215 features;
- 881 MARKET classes;
- 50 FARMER classes;
- 1,765 HANDS classes;
then the hosted runner received a shutdown signal during ExtraTrees fitting.

This representation is closed as computationally invalid, not strategically negative.

Closure:
`docs/strategy/V27C_WHOLE_COMPONENT_COMPUTATIONAL_INVALID_2026-09-21.md`
(commit `02db35134e0949c9dc9022f32b7d1932d4961fc2`).

### V27C2 — ACTIVE / STATEFUL STRUCTURAL DISTILLATION

Protocol:
`docs/strategy/V27C2_STATEFUL_STRUCTURAL_DISTILLATION_PROTOCOL_2026-09-21.md`
(commit `29a08da5cf200e85d219936f38a8de07363bcdec`).

Binding workflow:
**`35682535729`**.  
Launch commit:
`7a9567d78a21be4fb6b139d5bf109d2d7c4142c0`.

Same teacher / opponents / seeds / split as V27C.

Structural representation:
- one shared UNIT model over farmer + all real hands/workers;
- one shared MARKET-SLOT model over slots 0..9;
- raw legal memory only: step-2 opponent-money/WHEAT state, ordered first-two-shop memory, phase flags;
- actor-local legal position/inventory/tile/neighborhood features;
- no route ID/table, source identity, rank, SHA, hidden seed, EpisodeId, or teacher call at inference.

Frozen models:
- 2 x `DecisionTreeClassifier`;
- max_depth 32;
- min_samples_leaf 2;
- random_state 20260921;
- no hyperparameter sweep.

Original V27C holdout thresholds are unchanged.

No Kaggle submission is authorized.

**Binding immediate action:** resolve workflow `35682535729`.

V27D is already PRE-REGISTERED / READY-DORMANT:
- protocol: `docs/strategy/V27D_FRESH_CAUSAL_DISTILLED_POLICY_PROTOCOL_2026-09-21.md`;
- protocol commit: `782b965c7809b5a43e1567130c5ff3666a23ab34`;
- fresh seeds: `80101..80106`, both seats;
- fresh current-frontier immutable snapshot;
- causal shard + aggregator + first-party runtime already implemented;
- dormant workflow template: `docs/strategy/templates/V27D_FRESH_CAUSAL_DISTILLED_POLICY_WORKFLOW.yml`;
- activate only if V27C2 returns `V27C2_STRUCTURAL_POLICY_DISTILLATION_VIABLE`.


## Binding correction — V27C mechanical retry

Initial V27C workflow `35678728124` is NON-BINDING. Several collectors failed before any episode because `plain` was imported from the wrong module.

Mechanical correction:
- only import path changed;
- teacher, opponents, seeds, split, 256-step representation, sampling rule, ExtraTrees parameters and gates are unchanged.

Corrected binding workflow:
**`35678874775`**.

Collector fix commit:
`725a66061a7d601a5c4eb90d343250c49c66e1d9`.

Relaunch commit:
`c2c16c11086b1d83e109e5f6c729427913a1d949`.

**Binding immediate action:** resolve workflow `35678874775`.


## Binding update — 2026-09-21 — V27B BOUNDED HISTORY / V27C ACTIVE

**This block supersedes lower stale current-action sections.**

### V27B — COMPLETE / BOUNDED LEGAL HISTORY VIABLE

Corrected episode workflow: `35676166396`.  
Aggregate-only binding workflow: **`35678269956`**.  
Aggregate artifact: `10673273774`.  
Digest: `sha256:927a1f266329aa02965b3ed76c3ec3fe149a82429efbde519616c5b1ec99ec63`.

Decision:
**`V27B_BOUNDED_LEGAL_HISTORY_DISTILLATION_VIABLE`**.

Selected minimum viable horizon:
**256 prior legal candidate observations**.

H=256:
- complete-action parity: **0.9962963**;
- MARKET: **0.9962963**;
- FARMER: **1.0000000**;
- HANDS: **1.0000000**;
- minimum source complete-action parity: **0.9777778**;
- minimum checkpoint complete-action parity: **0.9444444**.

FULL legal history:
- complete/MARKET/FARMER/HANDS parity: **1.0**.

Result:
`docs/strategy/V27B_LEGAL_HISTORY_RECONSTRUCTIBILITY_RESULT_2026-09-21.md`
(commit `702243cda86f9aa1e5ea6d991d6b9d87808869c5`).

### V27C — ACTIVE / 256-STEP BEHAVIORAL DISTILLATION

Protocol:
`docs/strategy/V27C_256_HISTORY_BEHAVIORAL_DISTILLATION_PROTOCOL_2026-09-21.md`
(commit `99c6c70a301d9f6949273c51b5049ed4e9ee9a6d`).

Binding workflow:
**`35678728124`**.  
Launch commit:
`c208e67f4a9ab7e852be4df391c58beb52e4be47`.

Dataset:
- exact rank-1 teacher SHA `a1ad0fd1d174477ee2cbdd561a812bcb7029647ce34599e79d6b79e9057eff6c`;
- all 12 immutable V26A snapshot opponents;
- fresh seeds `79901..79908`;
- both seats;
- 192 expected teacher episodes;
- every candidate turn labeled.

Representation:
- current 114 programme features;
- legal lag snapshots at 1,2,4,8,16,32,64,128,256;
- current-minus-lag deltas;
- legal previous-action structural summaries;
- no source/rank/SHA/cluster/opponent identity.

Model:
- independent MARKET/FARMER/HANDS `ExtraTreesClassifier`;
- 256 trees;
- no hyperparameter sweep;
- fixed random state 20260921.

Frozen holdout gate:
- complete action >=0.90;
- MARKET >=0.94;
- FARMER >=0.99;
- HANDS >=0.98;
- minimum source complete-action >=0.80;
- minimum 120-turn stage parity >=0.80.

PASS =>
`V27C_HISTORY_POLICY_DISTILLATION_VIABLE` and open fresh causal V27D.

FAIL =>
`V27C_HISTORY_POLICY_DISTILLATION_NOT_VIABLE` and close fast rank-1 distillation.

No Kaggle submission is authorized.

**Binding immediate action:** resolve workflow `35678728124`.


## Binding update — 2026-09-21 — V27A HISTORY-AWARE / V27B MECHANICAL RETRY ACTIVE

**This block supersedes lower stale current-action sections.**

### V27A — COMPLETE

Binding workflow: **`35665757174`**.

Decision:
**`V27A_HISTORY_AWARE_DISTILLATION_REQUIRED`**.

Mechanical:
- 72/72 episodes;
- 1080/1080 checkpoint comparisons;
- failures 0.

Parity:
- complete action: **0.9222222**;
- MARKET: **0.9296296**;
- FARMER: **1.0000000**;
- HANDS: **0.9925926**;
- minimum checkpoint complete-action parity: **0.6666667**;
- minimum source complete-action parity: **0.8666667**.

State-only behavioral cloning is closed. The teacher is sufficiently reconstructible to justify one explicit legal-history audit.

Result:
`docs/strategy/V27A_RANK1_TEACHER_MARKOV_RECONSTRUCTIBILITY_RESULT_2026-09-21.md`.

### V27B attempt 1 — NON-BINDING MECHANICS INVALID

Attempt workflow:
`35672298198`.

All live episodes ended DONE/DONE, but the implementation performed long counterfactual history replays inside the live agent callback. This consumed the per-turn runtime budget and only 13/15 frozen checkpoints were observed.

No strategic horizon result from attempt 1 is valid.

Mechanics document:
`docs/strategy/V27B_ATTEMPT1_MECHANICS_INVALID_2026-09-21.md`
(commit `20284111894f79056b89e42dc03f0f007a775256`).

### V27B corrected binding — ACTIVE

Corrected workflow:
**`35676166396`**.

Corrections:
- live episode runs ongoing teacher normally;
- all legal observations/actions are recorded;
- frozen history reconstruction is performed offline after the episode;
- 12-way sharding replaces 4-way sharding to reduce wall-clock time only.

Frozen experiment is unchanged:
- rank-1 teacher SHA `a1ad0fd1d174477ee2cbdd561a812bcb7029647ce34599e79d6b79e9057eff6c`;
- all 12 V26A snapshot opponents;
- seeds `79801..79803`;
- both seats;
- checkpoints `0,1,2,3,4,8,16,32,64,128,256,384,512,640,718`;
- horizons `0,1,2,4,8,16,32,64,128,256,512,FULL`;
- original V27B parity gates unchanged.

No Kaggle submission is authorized.

**Binding immediate action:** resolve workflow `35676166396`.


## Binding update — 2026-09-21 — V26B CLOSED / V27A ACTIVE

**This block supersedes lower stale current-action sections.**

### V26B — COMPLETE / NO SOURCE-AGNOSTIC POLICY HEADROOM

Binding workflow: **`35660845547`**.  
Aggregate job: `106542706979`.  
Final artifact: `10667886918`.  
Digest: `sha256:c47ebfcb406f6077165a0b1779ede2a2060a283f9476d79129feb36e2207132e`.

Mechanical:
- 4/4 shards PASS;
- 144/144 paired contexts;
- 0 failures;
- immutable 12-teacher snapshot;
- no live Kaggle source reacquisition.

Decision:
**`V26B_NO_SOURCE_AGNOSTIC_POLICY_HEADROOM`**.

Key results:
- ALL3 control score rate: 0.3472222;
- teacher-consensus score rate: 0.1527778;
- mean score delta: -0.1944444;
- mean margin delta: -2131.0833;
- positive-score contexts: 2;
- negative-score contexts: 30;
- CONTROL-win -> consensus-nonwin regressions: 30;
- positive source SHAs: 1;
- positive seeds: 1;
- positive CONTROL functional clusters: 1;
- mean modal support: 9.925 / 12 teachers.

Result:
`docs/strategy/V26B_PERSISTENT_TEACHER_CONSENSUS_RESULT_2026-09-21.md`
(commit `0f07d70c9d8ddd81040a3265a51cc767596462db`).

Closed:
- PrizeSolverV4 as current base;
- source-agnostic 12-teacher consensus;
- ALL3 additive option mining.

### V27A — ACTIVE / RANK-1 TEACHER MARKOV RECONSTRUCTIBILITY

Protocol:
`docs/strategy/V27A_RANK1_TEACHER_MARKOV_RECONSTRUCTIBILITY_PROTOCOL_2026-09-21.md`
(commit `5045ddb827b03cd0e66bd102d3756581da47700e`).

Binding workflow:
**`35665757174`**.  
Launch commit:
`6538f221f5fa6c7f7cbbc42cca797e3d23584461`.

Frozen teacher:
- current V26A rank-1 public representative;
- ref `ahmedberatozer/kaggriculture-v56-smarter-seeds-and-fertilizer`;
- SHA `a1ad0fd1d174477ee2cbdd561a812bcb7029647ce34599e79d6b79e9057eff6c`.

Population:
- all 12 immutable V26A opponent sources;
- fresh seeds 79701..79703;
- both seats;
- 72 episodes;
- 15 frozen checkpoints per episode;
- 1080 ongoing-vs-fresh action comparisons.

Question:
does the same legal current state reproduce the teacher action without its hidden episode history?

Routes:
- >=95% complete action parity + strict component/source/checkpoint gates => state-only distillation;
- >=70% complete parity but Markov gate fail => explicit legal-history distillation;
- <70% complete parity => fast teacher distillation closed.

No teacher source will be embedded into a candidate under V27.

Final-slot preservation protocol:
`docs/strategy/FINAL_HOSTED_SLOT_PRESERVATION_PROTOCOL_2026-09-21.md`
(commit `d7b3d3904462636dcb96531513c6ef25ab802239`).

Current protected fallback:
- ALL3 submission `56367770`, latest observed rating 2412.1;
- O-RW1 submission `56336027`, latest observed rating 2361.6;
- CR053 `56073870` is a legacy historical anchor, not the current strongest hosted result.

No Kaggle submission is authorized.

**Binding immediate action:** resolve workflow `35665757174`.


## Binding update — 2026-09-21 — V26A CLOSED / V26B ACTIVE

**This block supersedes lower stale current-action sections.**

### V26A — COMPLETE / PRIZE SOLVER BASE NOT READY

Binding workflow: **`35653189539`**.  
Aggregate job: `106517283200`.  
Final artifact: `10664405274`.  
Digest: `sha256:a43451c248c92eff000d624690cdba4233f9777106f45e496541d6c168c953c9`.

Current-frontier snapshot:
- 12 selected unique executable representatives;
- 0 unavailable refs;
- 0 smoke failures;
- immutable snapshot artifact `10663530412`;
- snapshot digest `sha256:69f6407c34155af19671963c1ce107fab45926283098b422790cd1d86117ed43`.

Mechanical:
- 144/144 paired contexts;
- failures 0;
- fresh seeds `79501..79506`;
- both seats.

Decision:
**`V26A_PRIZE_SOLVER_BASE_NOT_READY`**.

Competitive:
- ALL3 control score rate: **0.3611111**;
- PrizeSolverV4 treatment score rate: **0.0**;
- positive treatment contexts: **0**;
- negative treatment contexts: **52**;
- CONTROL-win -> TREATMENT-nonwin: **52**;
- mean score delta: **-0.3611111**;
- mean margin delta: **-135390.7847**.

PrizeSolverV4 is not a competitive base in its current heuristic form. Do not scale PS2/PS3 to rescue it.

Result:
`docs/strategy/V26A_FIRST_PARTY_BASE_ARCHITECTURE_BENCHMARK_RESULT_2026-09-21.md`
(commit `92f29f4e61e6d623a47cd1ba6ed793c6bf1ddbb2`).

### V26B — ACTIVE / PERSISTENT SOURCE-AGNOSTIC TEACHER CONSENSUS

Protocol:
`docs/strategy/V26B_TEACHER_DERIVED_PERSISTENT_POLICY_VIABILITY_PROTOCOL_2026-09-21.md`
(commit `d48bbea1158dab464b343589cfb27be3ee524487`).

Binding workflow:
**`35660845547`**.  
Launch commit:
`356349db5a70763cafa722a0231b07bafc6e8ff8`.

Inputs:
- exact immutable V26A current-frontier snapshot;
- same 12 selected teachers and opponents;
- no live Kaggle source reacquisition.

Fresh seeds:
`79601..79606`, both seats.

Treatment:
- every turn, evaluate all 12 snapshot teachers on the same legal observation;
- choose modal complete canonical action;
- lexical canonical JSON tie-break;
- no component mixing;
- no source weights;
- no opponent-specific subset;
- no identity/rank/SHA runtime feature.

Frozen headroom gate:
- >=8 positive-score contexts;
- >=3 opponent SHAs;
- >=3 fresh seeds;
- mean score delta >0;
- negatives <= positives/2;
- CONTROL-win -> CONSENSUS-nonwin <= positives/2;
- >=2 CONTROL functional outcome clusters.

PASS:
`V26B_CONSENSUS_POLICY_HEADROOM` => distill persistent first-party policy.

FAIL:
`V26B_NO_SOURCE_AGNOSTIC_POLICY_HEADROOM` => close current teacher-bank imitation and move to competition-strategy reassessment / genuinely new learning architecture.

No Kaggle submission is authorized.

**Binding immediate action:** resolve workflow `35660845547`.


## Binding update — 2026-09-21 — V25A PERSISTENT POLICY / V26A ACTIVE

**This block supersedes lower stale current-action sections.**

### V25A — COMPLETE / PERSISTENT POLICY REQUIRED

Binding workflow: **`35645830010`**.  
Aggregate job: `106504353595`.  
Final artifact: `10661899016`.  
Digest: `sha256:e0d5190ffe6a8aded7b7df4610514bd616f04e9e744371bbc0b1aac9700b7d45`.

Mechanical:
- 4/4 shards PASS;
- 93 hard contexts;
- 9 frozen horizons per context;
- **837/837 rows**;
- failures 0;
- H=0 exact V23B BASE parity;
- H=720 exact V23B FULL_SHADOW parity.

Decision:
**`V25A_PERSISTENT_POLICY_REQUIRED`**.

Finite horizons `4,8,16,32,64,128,256`:
- **0/93 score improvements at every finite horizon**.

H=720:
- 81/93 score improvements;
- 9 source SHAs;
- 6 functional clusters;
- all 5 hard seeds;
- mean score delta +0.4838709677;
- mean margin delta +3246.3226;
- regressions 0.

Interpretation:
the competitive gap is persistent whole-episode policy, not an opening macro or finite state-basin prefix.

Result:
`docs/strategy/ALL3_V25A_SHADOW_PREFIX_STATE_BASIN_RESULT_2026-09-21.md`
(commit `e0c2ad42fdc6ab0b6f31b146759fd8903992f220`).

Additive option mining around V47+ALL3 is CLOSED.

### V26A — ACTIVE / FIRST-PARTY BASE ARCHITECTURE BENCHMARK

Protocol:
`docs/strategy/V26A_FIRST_PARTY_BASE_ARCHITECTURE_BENCHMARK_PROTOCOL_2026-09-21.md`
(commit `c9accb8416e860bc372ba1fd0890181b65419c8d`).

Binding workflow:
**`35653189539`**.  
Launch commit:
`26be628577a7ef555a3b32544f94178162ec6118`.

Fresh seeds:
`79501..79506`, both seats.

CONTROL:
exact V47+ALL3.

TREATMENT:
`PrizeSolverV4` end-to-end adaptive architecture.

Workflow:
1. query current public Top-30 once;
2. acquire / smoke / SHA-deduplicate;
3. select up to 12 unique executable representatives, minimum 8;
4. immutable-snapshot exact V47 base + selected opponents;
5. paired ALL3 vs PrizeSolverV4 on fresh seeds and both seats;
6. aggregate W/L headroom across sources, seeds and CONTROL functional clusters.

Frozen PrizeSolverV4 headroom gate:
- >=8 positive-score contexts;
- >=3 source SHAs;
- >=3 seeds;
- mean score delta >0;
- negative-score contexts <= positives/2;
- CONTROL-win -> TREATMENT-nonwin <= positives/2;
- >=2 CONTROL functional outcome clusters.

PASS:
`V26A_PRIZE_SOLVER_BASE_HEADROOM` => reopen Prize Solver roadmap at PS2/PS3.

FAIL:
`V26A_PRIZE_SOLVER_BASE_NOT_READY` => do not brute-force train V4; open teacher-derived persistent-policy reconstruction viability.

No Kaggle submission is authorized.

**Binding immediate action:** resolve workflow `35653189539`.


## Binding update — 2026-09-21 — V24B COMPACT CLOSED / V25A ACTIVE

**This block supersedes lower stale current-action sections.**

### V24A — COMPLETE

Workflow: `35641081142`.  
Decision: **`V24A_COMPACT_COUPLED_EVENT_FAMILY_FOUND`**.

Selected family:
**`M_TO_P|hands|2`**.

Properties:
- 63/63 interaction-exclusive contexts;
- 9 SHAs;
- 6 functional clusters;
- 4 seeds;
- median start turn 0;
- median end turn 2;
- 19 recurrent families passed the frozen recurrence gate.

Result document:
`docs/strategy/ALL3_V24A_COUPLED_DIVERGENCE_TRACE_RESULT_2026-09-21.md`
(commit `f4f9a4885dff7af97ad9667ac14f461ad36bad59`).

### V24B — CLOSED / NOT DISTILLABLE COMPACTLY

Binding identifiability audit workflow:
`35645479016`.

Decision:
**`V24B_NOT_DISTILLABLE_COMPACTLY`**.

R1:
- train occurrences: 21;
- best single signature train coverage: **66.67%** < frozen 70%;
- holdout coverage of that training-dominant signature: **0%**.

R2:
- selected family present in **93/93 hard contexts**;
- valid negative start states: **0**;
- unique legal turn-0 state keys: **1**;
- conflicting legal-state keys: **1**.

Therefore the same exact legal runtime state maps to two different teacher market labels. The missing discriminator is opponent/source identity, which is forbidden.

Result document:
`docs/strategy/ALL3_V24B_INTERACTION_MECHANISM_DISTILLATION_RESULT_2026-09-21.md`
(commit `db0b15c60145ab8c282885b0c6af35a208967f02`).

Compact <=2-turn interaction controller search is closed. No V24C is opened.

### V25A — ACTIVE / SHADOW PREFIX STATE-BASIN HORIZON

Protocol:
`docs/strategy/ALL3_V25A_SHADOW_PREFIX_STATE_BASIN_PROTOCOL_2026-09-21.md`
(commit `fa63ba0a1850aeabfe73bfa2edcdc108ddab2ac5`).

Binding workflow:
**`35645830010`**.  
Launch commit:
`641f28a3c836c8248f1ea42b9d60b3acebfb1faa`.

Frozen horizons:
`[0,4,8,16,32,64,128,256,720]`.

Population:
- all 93 V23 hard contexts;
- same immutable V23A snapshot;
- H=0 must reproduce exact V23B BASE;
- H=720 must reproduce exact V23B FULL_SHADOW.

Finite-horizon gate:
- >=4 score improvements;
- >=2 source SHAs;
- >=2 functional clusters;
- >=2 seeds;
- mean score delta >0;
- regressions <= improvements/2.

Selector:
- smallest finite H that passes.

Decision routing:
- H<=32 => EARLY_STATE_BASIN_HEADROOM;
- H in 64/128/256 => LONG_STATE_BASIN_HEADROOM;
- no finite pass but H720 pass => PERSISTENT_POLICY_REQUIRED.

No Kaggle submission is authorized.

**Binding immediate action:** resolve workflow `35645830010`.


## Binding update — 2026-09-21 — V23B CROSS-DOMAIN HEADROOM / V24A ACTIVE

**This block supersedes lower stale current-action sections.**

### V23B — COMPLETE / VALID

Binding workflow: **`35632311093`**.  
Aggregate job: `106449044810`.  
Final artifact: `10656170070`.  
Digest: `sha256:6d626768832cd29029094bc8d4f129e6f78acece250fa39a67ed51530520509f`.

Mechanical:
- 4/4 shards PASS;
- 93 hard contexts;
- 372/372 rows;
- 0 failures;
- immutable V23A snapshot only;
- no live Kaggle source reacquisition.

Decision:
**`V23B_CROSS_DOMAIN_INTERACTION_HEADROOM`**.

Frozen route:
**`ARCHITECTURAL_INTERACTION_RESET`**.

Domain evidence:
- MARKET_ONLY: 18/93 score improvements, 9 SHAs, 6 functional clusters, but only seed `79301`; frozen >=2-seed gate FAIL;
- PHYSICAL_ONLY: 0/93 score improvements; FAIL;
- FULL_SHADOW: 81/93 score improvements, 9 SHAs, all 5 hard seeds; mean score delta +0.4838709677; mean margin delta +3246.3226; interaction ceiling PASS;
- **63/93** contexts improve under FULL_SHADOW while neither one-domain treatment improves; these span 9 SHAs, 6 clusters, and 4 seeds.

Result document:
`docs/strategy/ALL3_V23B_IMMUTABLE_SNAPSHOT_DOMAIN_UPPER_BOUND_RESULT_2026-09-21.md`
(commit `b6b3d9c67a3050c334a1bb9a756a34a3f9b611e7`).

No MARKET-only or PHYSICAL-only option may be opened from V23B.

### V24A — ACTIVE / COUPLED DIVERGENCE TRACE

Protocol:
`docs/strategy/ALL3_V24A_COUPLED_DIVERGENCE_TRACE_PROTOCOL_2026-09-21.md`
(commit `130f15c1b810e8c296926be9c8d2ce1bceed2f12`).

Binding workflow:
**`35641081142`**.  
Launch commit: `d8cc5085b483da43a902f1751d08b1e97de9492c`.

Population:
- all 93 exact V23 hard contexts;
- same immutable V23A snapshot;
- exact V23B FULL_SHADOW replay required per context;
- no Kaggle source reacquisition.

Frozen eligible coupling topologies:
- SAME market+physical divergence;
- market-only -> physical within 1..3 turns;
- physical-only -> market within 1..3 turns.

Family key:
`(topology, physical_kind, lag)`.

Recurrence gate within the 63 interaction-exclusive contexts:
- >=4 contexts;
- >=2 source SHAs;
- >=2 functional clusters;
- >=2 seeds.

Frozen selector picks exactly one earliest recurrent family by:
median end step -> clusters -> SHAs -> seeds -> contexts -> lag -> lexical.

V24A is discovery only. Any selected family must still be distilled into one identity-free controller and pass untouched fresh causal validation before any hosted candidate.

No Kaggle submission is authorized.

**Binding immediate action:** resolve workflow `35641081142`.


## Binding update — 2026-09-21 — V22B CLOSED INCONCLUSIVE / V23 IMMUTABLE SNAPSHOT ACTIVE

**This block supersedes lower stale V22/V23 current-action sections.**

### V22B — CLOSED / EXACT ROUTING INCONCLUSIVE

Closure:
**`V22B_EXACT_ROUTING_INCONCLUSIVE_SOURCE_UNAVAILABLE`**.

Exact evidence:
- 356/368 exact keys;
- 89/92 exact contexts;
- 0 cross-attempt conflicts;
- only rank-11 frozen SHA `254eba4713f092e7bbdd6efe8b2b31ee8cf2873fcfbdf16ca7c530628a0f51ef` remained unavailable.

Historical recovery workflow `35624010734` failed: versions 1..60 returned HTTP 403.

Current-source sensitivity workflow `35624589618` was REJECTED:
- `base_replay_pass=false`;
- context 059: -3136 current vs -3061 frozen;
- context 063: -3789 current vs -3729 frozen;
- context 067: -194 current vs -132 frozen;
- 0 admissible treatment rows.

Closure document:
`docs/strategy/ALL3_V22B_SOURCE_UNAVAILABLE_CLOSE_2026-09-21.md`.

No V22B strategic decision or option promotion is valid.

### V23 — ACTIVE / IMMUTABLE SNAPSHOT FRONTIER

Binding workflow: **`35627972979`**.  
Launch commit: `ce1bd5abbb01926c073aafa69f7950be687db5d7`.

Protocol:
`docs/strategy/ALL3_V23_IMMUTABLE_SNAPSHOT_FRONTIER_PROTOCOL_2026-09-21.md`
(commit `fdfa1b672742a51ffc46e737a0977de29f8923ff`).

Fresh seeds:
- smoke: `79300`;
- discovery: `79301..79306`;
- seats: 0/1.

V23A:
- query current Top-30 once;
- unavailable non-selected refs are recorded but do not mechanically invalidate the run;
- select up to 12 unique executable SHAs by rank only, minimum 8;
- snapshot exact selected package bytes plus exact V47 base;
- run ALL3 discovery from the immutable snapshot;
- READY gate remains >=12 hard contexts, >=4 hard SHAs, >=3 seeds.

V23B, only if V23A READY:
- uses all and only V23A hard rows;
- loads teacher/opponent source only from immutable snapshot artifact;
- performs no live Kaggle source reacquisition;
- modes and domain-pass thresholds are unchanged from V22B;
- deterministic routing remains frozen.

Implementation:
- `tools/all3_v23a_immutable_frontier.py` — `e8560288a681648baaa649dc88307d307c2bd5a7`;
- `tools/materialize_v23b_hard_config_and_clusters.py` — `bda0dfa92216b2de4d9dd344d0cb8ca631964b11`;
- `tools/all3_v23b_immutable_snapshot_shard.py` — `b5be592471be003566e19b147dcade0cdb47f99e`;
- `tools/aggregate_all3_v23b_immutable_snapshot.py` — `bd9a6a5d7bb4cfbea7c92861183656485097823b`;
- `tools/route_v23b_outcome.py` — `f5619c257b44eff1d765674a3fcdbc8ecfeb626f`.

No Kaggle submission is authorized.

**Binding immediate action:** resolve workflow `35627972979`.



### V23A binding result

Workflow `35627972979` / discover job `106426918864`:

- decision: **`V23A_IMMUTABLE_HARD_POPULATION_READY`**;
- 144/144 discovery games complete;
- 0 episode failures;
- 0 unavailable refs among selected set;
- 12 selected executable representatives;
- **93 hard contexts**;
- **12 hard source SHAs**;
- **5 hard seeds**;
- immutable snapshot artifact ID `10655240502`;
- immutable snapshot digest `sha256:12a6f45ebd3ed44c3d9b57d49b6a53d77514dccf48d8cddff17cb2c829c99054`;
- V23A result artifact ID `10655010811`;
- V23 config artifact ID `10654531145`;
- materialized functional clusters: **9**.

Hard-source counts:
- rank 1: 10;
- rank 2: 10;
- rank 4: 10;
- rank 5: 10;
- rank 6: 10;
- rank 7: 10;
- rank 9: 10;
- rank 10: 10;
- rank 11: 1;
- rank 12: 1;
- rank 13: 10;
- rank 14: 1.

Observed V23A functional clusters:
- F01: rank 1;
- F02: ranks 2 + 9;
- F03: rank 4;
- F04: ranks 5 + 6 + 10;
- F05: rank 7;
- F06: rank 11;
- F07: rank 12;
- F08: rank 13;
- F09: rank 14.

### V23B mechanical rebind

The integrated V23B jobs in workflow `35627972979` failed before treatment execution because the runtime omitted `kagglehub` (`ModuleNotFoundError`).

This does **not** invalidate V23A or its immutable artifacts.

Fallback workflow, frozen before activation:
`docs/strategy/templates/V23B_FROM_BINDING_V23A_SNAPSHOT_WORKFLOW.yml`
(commit `71d28401f0eeef95788f3cee764a0095389cdf9f`).

Active corrected V23B binding workflow:
**`35632311093`**.

Independent snapshot audit: **13/13 `main.py` files (V47 base + 12 selected sources) match the exact SHAs in `MANIFEST.json`; 0 missing, 0 mismatches.**

It reuses exactly:
- V23A snapshot from workflow `35627972979`;
- V23 hard config / cluster map from workflow `35627972979`;
- no live Kaggle source reacquisition.

**Binding immediate action:** resolve V23B workflow `35632311093`.


## Binding update — 2026-09-21 — V22A READY / V22B DOMAIN UPPER BOUND ACTIVE

**This block supersedes lower stale V20/V21/V22 current-action sections.**

### V21A — COMPLETE / CLOSED

Workflow: **`35558880526`**.  
Decision: **`V21A_SEMANTIC_NO_WL_HEADROOM`**.

- 120/120 frozen contexts;
- BASE mismatches: 0;
- FULL mismatches: 0;
- no semantic mode produced any W/L-positive context;
- V19A-derived schedule family is CLOSED.

Result:
`docs/strategy/ALL3_V21A_SEMANTIC_SCHEDULE_DECOMPOSITION_RESULT_2026-09-21.md`.

### V22A — COMPLETE / READY

Corrected binding workflow: **`35562142399`**.  
Launch commit: `2ee8c8a0c73b7c11ff0487c0ed8e1a7a2f36ae7f`.  
Decision: **`V22A_FRESH_FRONTIER_HARD_POPULATION_READY`**.

Mechanical:
- selected executable representatives: **12**;
- expected/completed games: **144/144**;
- acquisition failures: **0**;
- smoke failures: **0**;
- episode failures: **0**;
- mechanical PASS.

Fresh hard population:
- ALL3 non-win contexts: **92/144**;
- hard unique source SHAs: **8**;
- hard seeds: **6/6** (`79101..79106`);
- both seats evaluated.

Binding artifact:
- artifact ID: `10623710178`;
- digest: `sha256:56c2ee63e78c7e3389687ec5ece3a815a9bc190f41e731f4084324e5acf343f3`.

Frozen hard config:
`configs/all3_v22b_hard_contexts.json`
(commit `5c6058ed4fcc267242f0b654f06bd669fec1849b`).

Result:
`docs/strategy/ALL3_V22A_FRESH_CURRENT_FRONTIER_RESULT_2026-09-21.md`.

Original workflow `35560761804` is NON-BINDING due the pre-outcome mechanics amendment.

### V22B — ACTIVE / PRE-REGISTERED DOMAIN UPPER BOUND

### V22B attempt-2 mechanical progress

Corrected binding workflow `35607214335` is still running serially.

Observed so far:
- shard 0 completed with 80/92 rows;
- its only failures were the 3 rank-2 contexts for SHA `fd39dffa68e2171fe6fc016b79804b52b862dc5c2af3427e9ca4c54e9fb410d8`;
- the representative ref `haodou092/notebookdb6965aa8e` now returns HTTP 404;
- binding V22A had already proven `degnonguidi/best-agent-ranking` as an exact-SHA alias for the same bytes;
- frozen alias map: `configs/all3_v22b_hard_contexts.json`, commit `f1c5628b2799e7acd62d2746d231ee0c2acbbd56`;
- executor exact-SHA alias support: commit `20195454330d67e786f33a49346f35504f5be07c`;
- strict mechanical merger: `tools/merge_v22b_mechanical_attempts.py`, commit `c04e01c54621320c5c52ceef4aa4b59f0d5277a2`;
- dormant merge workflow template: `docs/strategy/templates/ALL3_V22B_MECHANICAL_MERGE_WORKFLOW.yml`, commit `adaaea4f8750cd79d5d600833dd1c0fbc34c5c5c`.

Current union after attempt 2 completed:
- **356/368 exact keys**;
- **89/92 complete contexts**;
- only 3 contexts / 12 keys remain: shard-3 rank-11 contexts `v22a_hard_059`, `063`, `067`;
- rank-2 gaps are already filled from attempt 1;
- rank-11 current ref `romantamrazov/kaggriculture-yummers` drifted from frozen SHA `254eba47...` to `338a1a08...`;
- historical exact-SHA recovery workflow: **`35624010734`**;
- cross-attempt determinism audit: **116 duplicate keys compared, 0 conflicts**.

Therefore no third full V22B run is justified at this time. Let attempt 2 finish shards 2/3, then mechanically merge attempts 1+2. Strategic interpretation remains blocked until a complete 368-key aggregate exists.


Attempt 1 workflow: `35566168354` => **`V22B_MECHANICS_INVALID`** due 45 Kaggle HTTP 429 `teacher_acquire` failures; its partial aggregate is strategically NON-BINDING.  
Corrected binding workflow: **`35607214335`**.  
Mechanical-repair launch commit: `ade4a4180d7081e57f7cde7286c9de07abfe2e87`.

Frozen population:
- exactly all 92 V22A binding non-win contexts;
- no manual context selection;
- exact source ref/SHA, seed, seat, BASE score and BASE margin frozen.

Frozen modes:
- BASE;
- MARKET_ONLY;
- PHYSICAL_ONLY;
- FULL_SHADOW.

Domain W/L gate:
- >=4 improved-score contexts;
- improvements across >=2 source SHAs;
- improvements across >=2 seeds;
- mean score delta >0;
- regressions <= half the improvements.

Decision space:
- `V22B_MARKET_DOMAIN_HEADROOM`;
- `V22B_PHYSICAL_DOMAIN_HEADROOM`;
- `V22B_BOTH_DOMAINS_HEADROOM`;
- `V22B_CROSS_DOMAIN_INTERACTION_HEADROOM`;
- `V22B_NO_DOMAIN_WL_HEADROOM_RESET`;
- `V22B_MECHANICS_INVALID`.

Protocol:
`docs/strategy/ALL3_V22B_FRESH_FRONTIER_DOMAIN_UPPER_BOUND_PROTOCOL_2026-09-21.md`.

Attempt-1 mechanical diagnosis:
`docs/strategy/ALL3_V22B_ATTEMPT1_MECHANICS_INVALID_2026-09-21.md`.

Functional-diversity interpretation rule:
`docs/strategy/ALL3_V22B_FUNCTIONAL_DIVERSITY_INTERPRETATION_2026-09-21.md`.

Frozen functional-cluster map:
`configs/all3_v22b_functional_clusters.json` (commit `04be152448ef4f6b882530f2df93e6e4453391a9`).

Outcome router / architectural-reset protocol:
`docs/strategy/ALL3_V22B_OUTCOME_ROUTER_AND_ARCHITECTURAL_RESET_PROTOCOL_2026-09-21.md`.

Deterministic router implementation:
`tools/route_v22b_outcome.py` (commit `8acdf847d13dabd48fb208543aa20d923c287005`).

If V22B returns no MARKET/PHYSICAL W/L upper-bound headroom, stop ALL3 local-option mining and perform the pre-registered architectural reset / competition-strategy reassessment.

No Kaggle submission is currently authorized.

Historical recovery workflow `35624010734` exhausted versions 1..60 and all returned HTTP 403; exact frozen rank-11 bytes are unavailable through the authenticated Kaggle API.

Frozen fallback sensitivity protocol:
`docs/strategy/V22B_SOURCE_UNAVAILABLE_SENSITIVITY_CLOSURE_PROTOCOL_2026-09-21.md` (commit `51c699960868472f899c9ba4b4da7166a1b8d7f4`).

Current-source NON-BINDING sensitivity workflow: **`35624589618`**.

**Binding immediate action:** resolve sensitivity workflow `35624589618`; only a 12/12 unanimous current-source + rank1 + rank2 match permits sensitivity-only completion.

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

> **Current update — 2026-09-15:** CR091 completed with a valid PASS. The frozen CR086 latent-supply SELL-priority mechanism is now option **O1** on exact CR053. The current binding gate is **CR092 — broad O1 transfer + counterfactual router labels**, workflow `35015135956`.

## Mission

Win / maximize prize probability in Kaggriculture. Novelty is irrelevant unless it improves competitive strength. All accumulated legal competitive, replay, mechanics and economic knowledge remains usable unless stronger evidence supersedes it.

## Authoritative branches

- competition/source of truth: `fix/kaggle-parity-v1`
- experimental integration: `research/first-principles-economy-v1`

Read first:

1. `STATUS.md`
2. `ROADMAP.md`
3. `docs/strategy/CR091_HIERARCHICAL_MARKET_OPTION_RESULT_2026-09-15.md`
4. `docs/strategy/CR092_BROAD_OPTION_ROUTER_LABEL_PROTOCOL_2026-09-15.md`
5. `docs/strategy/CR091_RUN1_INVALID_2026-09-15.md` only for the invalid-run warning
6. experimental `docs/strategy/FP001_STATUS.md` / `FP001_ROADMAP.md`

## Competitive anchors / calibration

- **CR053_REAL**: strongest exact project-hosted anchor; submission `56073870`, checkpoint ~`2064.8`, SHA `095080e791bd8d58369893c1a421beb57b7f64c2808c011f576e09684ffb9a15`.
- CR052_REAL ~`1749.2`.
- CR083 ~`1619.9`.
- CR086 ~`1612.6`.
- frozen external frontier 2026-09-14: top ~3191; rank 10 ~2958; target remains ~3000+.

Critical calibration: exact-byte local H2H can reverse hosted order. Use local exact-engine work for mechanics, causal intervention, catastrophe and diversity, not as a direct hosted-rating predictor.

## Closed major routes

Keep closed absent new causal evidence changing the failure mechanism: CR078/079; CR080 replay stitching; CR081 static market-prefix transplant; CR082 1-NN imitation; CR084 FEED rescue; CR085 Pareto gating; direct CR088 tape backbones; static C5/C5+M6S1; fixed C3S2/C2S3; CR090 simple first-shop species selector.

## Retained modules / knowledge

CR053 macro/physical route; CR086 latent-supply estimator + SELL priority; CR087/CR088 elite macro/replay corpus; H1 WHEAT carry; H1B sale deferral; H8/B3+DAILY CARE; H9 public-shop demand representation; H10 compact routing/batching; H11 fertilizer conversion; M6S1 as an economic module.

## CR089 / CR090

CR089 run `34923802262`: C5_BASE and C5_M6S1 each 0W–132L. Static C5 closed; M6S1 retained as a module.

CR090 run `34979280512`: simple H9 COW/SHEEP rule failed causally despite a strong MILK/COW contrast. Binding verdict `CR090_H9_CAUSAL_FAIL_CLOSE_SIMPLE_SPECIES_ADAPTATION`; H9 remains a state representation, not a standalone action rule.

## CR091 — COMPLETE / PASS

The first run `34987640694` is invalid/non-binding because direct `exec()` did not reproduce CR052 package semantics.

The authoritative hosted-faithful rerun is **`34990757344`**, head commit `f49bff2e7adde626b01b9fa3c0413f7fc97d9649`.

Artifact `cr091-hierarchical-market-option-gate-v1`, ID `10406926564`, ZIP SHA-256 `d6d9a5a7cb187e48dc4cb187e348adb7fff4d10666f18f27b4030ccc8ad2f3d0`.

Mechanics:

- 128 valid episodes;
- failures 0;
- parity violations 0;
- exact CR053 farmer/hand parity;
- exact normalized market-order multiset parity;
- exact BASE full-action parity;
- O1 active with 1,075 reorders.

Seat-balanced W/L edge deltas `O1 - BASE`:

- CR052_REAL: `0.0000`
- CR053_REAL: `+0.1875`
- CR083: `0.0000`
- CR086: `0.0000`

Mean edge delta `+0.046875`, 4/4 nonnegative, worst regression `0`.

Binding verdict: **`CR091_LATENT_OPTION_TRANSFER_PASS_ADVANCE_ROUTER`**.

Promote the exact CR086 latent-priority mechanism to frozen option **O1** on exact CR053. Do not retune it. CR086 itself is not promoted as the backbone.

## Current binding experiment — CR092

Protocol: `docs/strategy/CR092_BROAD_OPTION_ROUTER_LABEL_PROTOCOL_2026-09-15.md`.

Purpose: test frozen O1 on the broader frozen CR089 population and collect hash-validated public-state counterfactual labels for a future router.

Population:

- exact anchors: CR053_REAL, CR052_REAL, CR083, CR086;
- current-top macro representatives: r01/Majkel, r02/SpaTaro, r03/ymg-Howard, r06/Orbital, r07/feel, r09/Otter, r10/redblack;
- exact CR089 frozen population artifact `10378299284`.

Evaluation:

- fresh seeds `91401..91406`;
- both seats;
- exact BASE vs frozen O1;
- 12 games/treatment/edge;
- 264 episodes total;
- 11 edge jobs parallelized;
- exact `kaggle-environments==1.32.7` hosted-faithful package execution.

Counterfactual labels:

- at O1's first actual reorder, capture the legal strategic observation;
- accept the label only if BASE has the identical strategic-state hash at the same step for the same opponent/seed/seat;
- primary label is `W/L(O1) - W/L(BASE)`;
- terminal money is diagnostic only;
- opponent identity and seed are offline metadata only and may not be router features.

Frozen decision branches:

- broad survivor + heterogeneous causal labels -> `CR092_BROAD_PASS_HETEROGENEOUS_ADVANCE_ROUTER`;
- broad survivor without meaningful downside support -> `CR092_BROAD_PASS_O1_ADVANCE_NEXT_OPTION`;
- broad fail but strong heterogeneous option value -> `CR092_BROAD_FAIL_HETEROGENEOUS_ADVANCE_ROUTER_DISCOVERY`;
- otherwise -> `CR092_BROAD_FAIL_CLOSE_ALWAYS_ON_O1`;
- mechanics failure -> no strategic verdict.

Implementation:

- `tools/cr092_broad_option_edge.py`
- `tools/cr092_aggregate.py`
- `.github/workflows/cr092-broad-option-router-label.yml`
- workflow/head commit `b42347617a6967eeb2862fde23737c7538d3b9d3`
- active workflow **`35015135956`**
- prepare job already PASS: all 11 packages downloaded and SHA-verified.

## Non-negotiable legality / evaluation

Engine `kaggle-environments==1.32.7`; no identity/rating/EpisodeId/hidden seed/future/direct opponent-private runtime features; `town.unlocked_shops` legal shared state; original final holdout sealed; no automatic CR092 hosted submission.

## Immediate next action

Query workflow `35015135956` once on the next continuation. If complete, read the frozen aggregate and follow its declared branch immediately. Do not manually submit anything to Kaggle while CR092 is unresolved.
