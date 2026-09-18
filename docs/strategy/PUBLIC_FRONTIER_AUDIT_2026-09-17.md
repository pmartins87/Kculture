# Public Frontier Audit — 2026-09-17

## Scope

Static audit of the eight current public Kaggriculture notebooks downloaded with the authenticated Kaggle CLI on 2026-09-17:

1. flexonafft/kaggriculture-multi-route-farming-agent
2. lynnsakurai/farming-score-v4-a-better-shop
3. lynnsakurai/farming-score-v3-replay-revised
4. lynnsakurai/farming-score-a-mathematical-approach
5. indarkarhana/shape-the-shop-work-the-pasture-top-10
6. tetsutani/shape-the-shop-work-the-pasture-kaggriculture
7. reyhanksatria/adaptive-route-agent-v2
8. vijaikm/kaggriculture-bc-policy-inference-starter

The audit is based on the downloaded notebook source and embedded submission payloads. Notebook metadata itself did not expose a reliable license field, so reuse rights must be determined from source notices / upstream provenance source-by-source.

## Main conclusion

The strongest public design pattern in this sample is **not end-to-end PPO**.

The recurring competitive pattern is:

1. a high-quality long action programme / route tape obtained from a strong replay or programme family;
2. sparse public-state routing between prefix-compatible continuations;
3. engine-exact guard and repair layers around the programme;
4. market queue / timing logic and opponent-conditioned microstructure;
5. bounded local substitutions / optimizations that conserve the original route geometry and service capacity;
6. final-turn and shed-capacity exactness.

This explains why the weak 32-parameter native controller failed against the frozen strong tapes despite massive search throughput: its executor and reachable behaviour family were below the demonstrated programme frontier.

The correct use of our native simulator is therefore not to rediscover farming from zero.  It is to perform exact state-conditioned search **around a library of already strong programmes**, then distill those decisions into Policy + Value.

## Family audit

### 1. Multi-Route Farming Agent

Downloaded current source is a large reactive route/programme lineage, not a learned neural policy.

Important mechanisms visible in source:
- long route-tape chassis;
- market price-curve modelling;
- public-state farm similarity / mirror detection;
- quote/sale queue reordering;
- opponent-conditioned reservation horizon;
- detection of quote-race losses from public market deltas and shed changes;
- warehouse/day-close protection;
- labour assignment;
- feed/fertilizer reserves;
- funding and supply gates;
- seed pre-funding;
- first-turn wheat buy/sell round-trip intended to alter public market microstructure against compatible openings.

This family contains embedded Apache-2.0 notices and retained upstream attribution in parts of the source.  Reuse must preserve the applicable notices for any copied portions.

**Strategic value:** very high for market microstructure, race handling and programme execution.

### 2. Farming Score V4 — A Better Shop

The notebook writes a large pure-Python route-replay chassis.

The top-level design explicitly treats a route as a precomputed 719-action programme and wraps it with small reactive layers including:
- hand alignment;
- weed repair;
- sell-lead/front-run logic;
- budget guard;
- shed room guard;
- impossible-sell clamping;
- dead-stock liquidation;
- terminal liquidation.

Later wrappers add more targeted transformations.  Two especially useful patterns:

**Confirmed-mirror sale ordering**
- identify a high-similarity public mirror state;
- intervene only when sale queue conditions and prior probe confirmation hold;
- perform bounded pair-swap ascent over sell order;
- require a minimum modelled gain before changing the source programme.

**Shop-conditioned livestock substitution**
- use visible shop demand to change a bounded animal purchase/placement bundle;
- keep the route geometry and generic feed/care/harvest programme;
- require visible-state confirmation before completing the transformation.

Some embedded sections carry Apache-2.0 / attribution notices; preserve those notices if reused.

**Strategic value:** extremely high as a blueprint for conservative programme transformation and market-order search.

### 3. Farming Score V3 — Replay Revised

This is a smaller two-route replay/router.

Important mechanisms:
- sparse route selection from public observations;
- multi-turn affordability/budget protection;
- reserve accounting for feed/fertilizer/unplaced animals;
- sell only true surplus when funding future required actions;
- deterministic programme backbone rather than free-form replanning.

**Strategic value:** high for suffix routing and funding constraints.

### 4. Farming Score — A Mathematical Approach

Four route variants share prefix structure.  Public checkpoints choose only prefix-compatible continuations.

Observed design:
- sparse checkpoints around selected turns;
- route switch only when continuation remains compatible with executed prefix;
- weed repair on otherwise dead/no-op route turns;
- projected shed accounting;
- day-close room guard around shed capacity;
- impossible-sell clamps;
- route-dead-stock liquidation;
- exact final executable-turn settlement.

No learned model is needed at runtime.

**Strategic value:** directly matches the programme-library + suffix-search teacher we need.

### 5. Shape the Shop Work the Pasture — TOP 10

The embedded bundle is a layered programme network.  It includes attributed action tapes from official public Kaggle episodes and a sequence of guarded wrappers.

Important stages:
- execution network over an attributed strong programme;
- exact same-turn PLACE/funding projection;
- change to another attributed strong programme/medoid;
- demand-aligned COW/SHEEP pasture substitutions while conserving route geometry and sale/service budget;
- terminal livestock-product liquidation;
- guarded activation of a latent already-serviced pasture;
- exact worker pickup/move/place repair for that activation.

The source explicitly documents provenance of the replay tapes.  Its notebook also reports strong internal validation, but those reported numbers are **not independently verified here**.

**Strategic value:** highest-value example in this sample of “strong full programme + bounded visible-state transformations + engine-exact transactional guards.”

### 6. Shape the Shop Work the Pasture — tetsutani

Same broad family as the conserved route-replay approach:
- route programme backbone;
- visible-state shop / pasture conditioning;
- bounded repairs rather than rebuilding the farm plan every turn.

**Strategic value:** useful independent implementation/reference for the same paradigm.

### 7. Adaptive Route Agent V2

The notebook packages a small Python wrapper plus a compiled native `agent.so`.

The Python wrapper sends a compact observation ABI into the binary:
- step;
- public market inventory/prices;
- unlocked shops;
- both public farm summaries;
- own private shed/inventory.

The native decision logic is opaque in this artifact, so it should be treated as a black-box benchmark/opponent unless matching source is found separately.

**Strategic value:** benchmark/opponent; not a suitable source-teacher until source provenance is available.

### 8. BC Policy Inference Starter

This notebook is not a full competitive programme.  It demonstrates a compact pure-NumPy inference path:
- 1706 input features;
- hidden layer 256;
- hidden layer 128;
- 35-way action-head softmax.

It references:
- dataset: `vijaikm/kaggriculture-match-replay-corpus`
- model: `vijaikm/kaggriculture-spatial-bc-policy`

The actual weights/corpus are not part of the downloaded notebook bundle.

**Strategic value:** important evidence that replay imitation can be compact enough for CPU runtime.  The corpus/model should be separately acquired and audited before deciding whether to use it.

## What explains the gap versus our Native Teacher V0/V1

The public programme families encode information our 32-parameter controller could not express:

### Opening schedule

Our old controller gradually ramps targets.  Strong programmes can commit immediately to exact opening purchases, worker counts, placements and market sequences.

### Temporal precision

A scalar “sell threshold” or “care priority” cannot express a 719-turn coordinated programme where a purchase at turn 88, pickup at turn 92 and placement at turn 95 are one conserved transaction.

### Geometry preservation

Strong wrappers modify an animal/product token while preserving route geometry, labour capacity and service schedule.  Our generic executor rebuilds assignment decisions each turn and loses that structural guarantee.

### Market microstructure

The public frontier explicitly reasons about simultaneous order queues, public market deltas, mirrored strategies, first-turn pressure and sell-order permutations.  This is a qualitatively different control surface from broad crop/livestock targets.

### Transactional guards

Interventions are usually conditional and reversible/cancelled when live observation does not match the expected executable state.  This prevents a local “improvement” from corrupting a long programme.

## Architecture correction

Keep:
- exact 1.32.7 simulator;
- L2 VecGame;
- native high-throughput evaluator;
- frozen historical/public opponent bank;
- 32-parameter controller only as randomized weak/exploiter population;
- CR086 opponent sensor as a feature source;
- all proven economic findings.

Replace the competitive nucleus with:

```
Strong Programme Library
        |
        v
Current-state compatibility / transaction guards
        |
        v
Candidate continuation + bounded transform proposals
        |
        v
Exact native suffix / counterfactual search
        |
        v
Improved action / continuation / value targets
        |
        v
Policy + Value distillation
        |
        v
League evaluation + bounded runtime search
```

This is still a learned/search solver.  The key difference is that the search starts from demonstrated competent programmes instead of an intentionally generic weak executor.

## Immediate implementation plan

1. Expand the source audit to the live top-public index instead of assuming these eight manually chosen notebooks cover the current frontier.
2. Build a reproducible programme corpus:
   - source SHA / provenance;
   - license/attribution status;
   - base action programmes / route variants;
   - visible-state checkpoints;
   - bounded transform families;
   - runtime dependencies.
3. Convert compatible literal programme tapes to the native dense action schema.
4. Add strong programme/tape families to exact league evaluation.
5. Build a state-conditioned suffix-search teacher over programme continuations and transforms.
6. Generate state/action/value targets.
7. Distill a compact Policy + Value model.
8. Use hosted Kaggle only when this produces a materially different runtime-safe candidate.

## Anti-regression decision

Do **not** spend more compute optimizing the fixed 32-dimensional controller as the main agent.

Do **not** discard the native infrastructure.

Do **not** copy opaque or ambiguously licensed payloads into the final submission.  They can be used for analysis/benchmarking only until provenance/reuse terms are established.

Do **not** reduce the new programme library to “copy one public agent.”  The competitive objective is to use proven programmes as priors and exact search/learning to exceed them.
