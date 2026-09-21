# ALL3 V18B Temporal Market-Controller Distillation Protocol — 2026-09-20

## Status

**ACTIVE after binding V18A `V18A_SINGLE_PARTITION_HEADROOM`.**

Binding temporal scope: **P2 = turns 464..591**.

V18A exact V14A replication passed 24/24 contexts.

## Architectural purpose

The causal programme has now falsified several isolated market edits even though V14A showed large cumulative market-domain W/L headroom.

V18B therefore stops selecting one hand-written edit at a time.

Instead, it will distill a **cumulative first-party market controller** over exactly the temporal scope selected by V18A.

No opponent/source identity may be used at runtime.

## Frozen temporal scope mapping

The V18A selected mode maps mechanically to V18B scope:

- `MARKET_P1_ONLY` -> turns 336..463;
- `MARKET_P2_ONLY` -> turns 464..591;
- `MARKET_P3_ONLY` -> turns 592..718;
- `MARKET_P12` -> turns 336..591;
- `MARKET_P23` -> turns 464..718;
- `MARKET_P123` -> turns 336..718.

The scope is determined only by V18A's frozen decision rule.

## Training-data population

Use the same 24 binding V13C hard contexts only for **controller discovery/training**.

For every turn in the selected scope, replay exact ALL3 BASE and record:

1. current legal observation available to our agent;
2. exact ALL3 action;
3. exact shadow-teacher market action from that context's pinned public source;
4. normalized V14B-style elementary market residual families.

The shadow teacher is an offline label source only.

## Runtime-prohibited features

The following may never enter training features or runtime inference:

- opponent/source SHA;
- notebook/ref identity;
- source rank;
- seed;
- context id;
- replay label;
- future state;
- eventual score/margin/result.

Seat may not be used as a predictive feature.

## Allowed feature families

Only current-state/action information legal at decision time:

- current turn / normalized progress within the selected scope;
- own money and own resource/product inventories;
- own shed/carried product quantities;
- public prices / public market state exposed by the environment;
- exact current ALL3 market queue structure;
- exact current ALL3 farmer/hands action;
- current legal observation fields independent of opponent identity.

No feature threshold may be chosen from causal game outcomes.

## Label universe

Use **all recurrent V14B market-residual families that occur inside the V18A-selected temporal scope** and are expressible as a legal first-party market mutation.

Do not select only one family.

The already tested isolated families (reorder, FERTILIZER +2, STRAWBERRY insertion) remain eligible as components because V18B tests cumulative interaction, not their standalone causal effect.

## Learning form

For each eligible residual family, train an independent deterministic shallow decision tree classifier:

- max depth: 4;
- min leaf support: max(8, 1% of training rows);
- class weighting allowed only to balance positive/negative examples;
- no hyperparameter search beyond these frozen values.

Training implementation may use sklearn offline, but every accepted tree must be exported to a pure JSON/rule representation and inference must be pure first-party Python with no sklearn dependency.

## Source-held-out validation

Use **leave-one-source-SHA-out** validation across the 10 unique hard sources.

A residual-family classifier is retained only if, aggregated over held-out-source predictions:

- positive support spans >=4 source SHAs;
- precision >=0.80;
- recall >=0.70;
- F1 >=0.75;
- zero use of prohibited features.

These thresholds are frozen before V18A result.

## Composition

At runtime inside the selected temporal scope:

1. compute exact ALL3 action;
2. evaluate every retained residual-family classifier;
3. apply all predicted residual edits in a deterministic canonical order:
   - removals / quantity decreases;
   - insertions / quantity increases;
   - duplicate compaction;
   - reorder canonicalization;
4. resolve conflicts by conservative semantics:
   - never sell more than currently legal own inventory;
   - never create invalid order cardinality;
   - never alter farmer/hands;
   - if two predicted edits are structurally incompatible, skip the lower-support family.

Family support is fixed from the training dataset, not game outcomes.

Outside the selected V18A temporal scope, return exact ALL3.

## Discovery gate

Before any causal games, the compiled controller must pass:

- pure-Python replay parity with exported trees;
- no prohibited runtime features;
- deterministic output;
- legal-action validation on every training/held-out row;
- retained families span >=3 distinct residual kinds;
- retained families span >=4 source SHAs.

If these fail:
**`V18B_CONTROLLER_NOT_DISTILLABLE`**.

If they pass:
**`V18B_CONTROLLER_READY_FOR_CAUSAL`**.

## Causal stage

A later V18C causal test, frozen before its outcomes, will compare:

- BASE exact ALL3;
- ALL3 + compiled V18B cumulative market controller;

on the same 24 hard contexts.

Only real W/L improvement can activate untouched fresh validation.

No Kaggle submission is authorized by V18B alone.


## Binding implementation amendment — selected P2 scope

This amendment is frozen before any V18B dataset/model result.

### Selected scope

Binding V18A selected:
- `MARKET_P2_ONLY`;
- turns **464..591 inclusive**;
- 14/24 positive-score contexts;
- 7 improved source SHAs;
- mean score delta +0.5833333;
- mean margin delta +1384.25;
- zero negative-score contexts.

### Dataset rows

Collect exactly one row for every hard context and every turn 464..591:

- 24 contexts × 128 turns = **3072 rows**.

Each row contains:
- a numeric legal feature vector from the current observation and exact ALL3 action;
- the exact current ALL3 market;
- the exact shadow-teacher market;
- normalized V14B elementary market residual labels.

BASE gameplay remains exact ALL3.

### Frozen feature schema

The predictive feature vector may contain only numeric values from:

1. turn and normalized progress inside P2;
2. own and opponent public money / quadrants / public crop-animal counts;
3. own private shed, carried inventory and seed counts;
4. public product prices / public market inventory;
5. exact ALL3 market aggregate structure:
   - market length;
   - nonempty/empty counts;
   - per SELL product aggregate quantity/count;
   - per BUY_SEED/BUY_PRODUCT product aggregate quantity/count;
   - HIRE count;
   - total SELL/BUY units;
6. count of unlocked public town shops.

Explicitly prohibited from the feature vector:
- source SHA/ref/rank;
- context id;
- seed;
- seat;
- outcome/result/margin;
- future state.

Source SHA is retained only as offline fold provenance.

### Actionable residual families in controller v1

A V14B recurrent family is independently actionable in controller v1 only when its elementary kind is:

- `QTY` on `SELL <real-product>`;
- `PRESENCE` on `SELL <real-product>`;
- `DUPLICATE` on `SELL <real-product>`.

Generic `ORDER_COUNT` and `REORDER` are not independently actionable because they do not identify a unique legal transformation.

BUY/HIRE residuals are not independently applied in controller v1 because legality depends on coupled capital/capacity constraints not represented by a safe standalone transformation. They remain observable in the dataset but cannot become runtime edits in V18B v1.

This restriction is frozen before V18B model results.

### Family identity

A classifier target is the exact tuple:

`(group_key, dominant_direction)`

from the binding V14B recurrent-family atlas.

Only families whose dominant residual actually appears inside turns 464..591 and satisfy the actionable-family rule above are trained.

### Fixed classifier

For every eligible family and every leave-one-source-SHA-out fold:

- sklearn `DecisionTreeClassifier`;
- `max_depth=4`;
- `class_weight="balanced"`;
- `random_state=20260920`;
- `min_samples_leaf=max(8, ceil(0.01 * training_rows))`;
- no hyperparameter search.

Retain a family only if aggregated OOF predictions satisfy:
- true positive examples span >=4 source SHAs;
- precision >=0.80;
- recall >=0.70;
- F1 >=0.75.

### Pure-Python tree parity

Each retained final tree is refit on all 3072 rows with the same frozen parameters and exported to JSON.

A generic pure-Python JSON-tree predictor must reproduce sklearn predictions **exactly on all 3072 rows** for every retained family.

Any mismatch fails V18B.

### Frozen SELL compiler semantics

Predicted retained families are grouped by SELL product.

For each product:

1. If a predicted `PRESENCE REMOVE` exists:
   - remove all current SELL orders for that product;
   - ignore other predicted edits for that product on that turn.

2. Otherwise derive one predicted quantity delta from QTY families:
   - bucket 1 -> 1;
   - bucket 2 -> 2;
   - bucket 3-4 -> 3;
   - bucket 5+ -> 5;
   - INC positive, DEC negative;
   - if multiple QTY families for the same product fire, use the family with highest training positive support, then lexical family id.

3. If current aggregate SELL quantity is zero:
   - a predicted `PRESENCE ADD` creates one SELL order with quantity equal to the positive QTY delta when an INC QTY family also fires;
   - otherwise ADD creates quantity 1;
   - insert at first semantic free market slot.

4. If current aggregate SELL quantity is positive:
   - apply selected QTY delta to the first matching SELL order;
   - clamp aggregate sell quantity to [0, current legally available own product inventory];
   - if quantity becomes zero, replace that order with an empty slot.

5. `DUPLICATE COMPACT`:
   - combine all same-product SELL quantities into the first matching slot;
   - empty the later duplicate slots.

6. `DUPLICATE SPLIT`:
   - only if exactly one same-product SELL order has aggregate quantity >=2;
   - keep quantity 1 in the original slot;
   - place the remainder in the first semantic free slot;
   - otherwise skip.

Cross-product application order is lexical product name after the global canonical kind order already frozen in the parent protocol.

The compiler may skip an edit if its legality preconditions are not satisfied; it may never alter farmer/hands.

### Controller discovery PASS

`V18B_CONTROLLER_READY_FOR_CAUSAL` requires:

- exact 3072-row dataset;
- zero replay/source failures;
- at least 3 retained families;
- retained families span >=3 residual kinds among QTY/PRESENCE/DUPLICATE;
- retained-family positive examples span >=4 source SHAs;
- exact sklearn/JSON inference parity;
- compiled actions structurally valid on all 3072 dataset rows;
- no prohibited feature in the exported model schema.

Otherwise:
`V18B_CONTROLLER_NOT_DISTILLABLE`.

No causal game is run in V18B.
