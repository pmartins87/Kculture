# CR092 — broad O1 transfer and counterfactual router-label result

Date: 2026-09-15/16  
Authoritative branch: `fix/kaggle-parity-v1`

## Verdict

**PASS — `CR092_BROAD_PASS_O1_ADVANCE_NEXT_OPTION`.**

The CR091 O1 option — exact CR086 latent-supply SELL-priority ordering applied on top of exact hosted CR053 — survives the frozen 11-opponent broad population gate with **no W/L regression on any edge**.

O1 is therefore retained as the current always-on market option over CR053. The CR092 labels do **not** support a BASE-vs-O1 router: all non-zero causal labels favor O1 and occur only in the CR053 stratum. The next step is to add a second separable option family, beginning with H1/H1B timing, rather than fit a selector to insufficient downside support.

No Kaggle submission is authorized by CR092.

## Immutable execution provenance

Original broad-evaluation workflow: `35015135956`.

All 11 evaluation jobs completed successfully. The original aggregation job failed only because `actions/download-artifact` retained an `artifacts/` subdirectory while `tools/cr092_aggregate.py` searched only the immediate input directory. This was a transport/layout error after all games had already finished; it is **not** a strategic or mechanics failure.

The 11 immutable edge artifacts from `35015135956` were reused without rerunning a single episode. Aggregation was made directory-layout invariant and executed by recovery-only workflow `35040078379` on research commit `92c614749e229120104d2eef527f373c9f8975b7`.

Canonical aggregate artifact:

- name: `cr092-recovered-canonical-aggregate-v1`
- artifact ID: `10425380109`
- artifact ZIP SHA-256: `9a74a296b181027a1f9f0382ae1dd1646547e5d10441442ceda90bea6c72ff20`
- `CR092_RESULT.json` SHA-256: `6841a0dabcebb2e3a78560528baacbaef0ca20f2b79b73f30214b6f87f5bcd1e`
- `CR092_ROUTER_LABELS.json` SHA-256: `2052831d6b08ff1c10484cc8b48deff0db2f7828bc6ff4a8f6c7785e64a3c484`

The original final holdout was untouched and automatic submission was disabled.

## Frozen evaluation

- engine: `kaggle-environments==1.32.7`
- treatments: exact `CR053_BASE` versus exact CR053 + O1 (`CR053_O1`)
- fresh seeds: `91401..91406`
- both seats
- 12 games per treatment per opponent edge
- 11 opponents
- 264 episodes total

Population:

- exact anchors: `CR052_REAL`, `CR053_REAL`, `CR083`, `CR086`
- current-top macro representatives: `r01_e108766633_s56156662`, `r02_e108761464_s56114097`, `r03_e108766659_s56209748`, `r06_e108754069_s56205640`, `r07_e108766657_s56132899`, `r09_e108766659_s56097405`, `r10_e108754200_s56210228`

## Mechanics

Mechanics gate passed completely:

- episode failures: `0`
- parity violations: `0`
- failed edges: `0`
- O1 reorder events: `2057`
- option active: `true`
- mechanics pass: `true`

Every candidate call preserved exact CR053 farmer/hands and exact normalized CR053 market-order multiset; BASE preserved exact full action parity.

## W/L result

Edge-score deltas `O1 - BASE`:

- `CR052_REAL`: `0.0000`
- `CR053_REAL`: **`+0.333333`** (`0.5000 -> 0.833333`)
- `CR083`: `0.0000`
- `CR086`: `0.0000`
- all seven macro representatives: `0.0000`

Aggregate frozen gate metrics:

- mean edge-score delta: **`+0.030303`**
- median edge-score delta: `0.0`
- macro-only mean delta: `0.0`
- positive edges: `1/11`
- nonnegative edges: **`11/11`**
- regressed edges: **`0/11`**
- maximum improvement: **`+0.333333`**
- worst regression: **`0.0`**
- catastrophe edges: `0`
- `BROAD_SURVIVAL = true`

The broad gate is therefore a safety/transfer PASS. This is not evidence that O1 alone closes the hosted top-10 gap: many edges are unchanged in W/L despite small margin changes.

## Counterfactual router labels

The matched-state branch check also passed cleanly:

- admissible matched labels: `132`
- rejected state-hash mismatches: `0`
- incomplete pairs: `0`
- no-reorder pairs: `0`
- positive W/L labels: `8`
- zero labels: `124`
- negative labels: `0`
- positive strata: only `CR053_REAL`
- negative strata: none
- `ROUTING_SIGNAL = false`

Therefore CR092 does **not** justify training a BASE/O1 router. There is no empirical downside class to learn and the positive class lacks cross-stratum support. Fitting a selector now would manufacture complexity rather than exploit demonstrated heterogeneous option value.

## Binding interpretation

Retain:

1. exact CR053 as the physical/macro host;
2. O1 as a broad-safe always-on market-order priority option;
3. CR092 matched-state label machinery for later multi-option routing;
4. CR086 latent-supply estimator/operator knowledge.

Do not:

- threshold-tune O1 after this result;
- train BASE-vs-O1 router from the CR092 labels;
- infer hosted rating from local edge scores;
- submit O1 automatically to Kaggle solely from CR092.

## Next gate

Advance to **CR093 — second separable timing option on CR053+O1**.

Historical evidence to preserve exactly:

- H1 runtime causal PASS `34843184110`, commit `ab951727a195dce2992a07bf3e8b08992187fdf6`, candidate blob `987c5bf31671a1553f6c097d55abf73faf389533`: active WHEAT carry around a legal known town pulse, +916.875 mean under passive control with a flat-price causal null of zero;
- H1B exact-engine PASS `34843556192`, commit `a00d2ffce9656b83df263f407ed9b92a718502db`, proof blob `09bd110f6b5a6ce289b1352039fc83742611c1b6`: delaying an already-owned sale until after known town consumption was positive in 104/104 tested engine counterfactuals.

Important distinction: H1 was a runtime agent probe; H1B was an engine counterfactual proof, **not yet a competitive runtime policy**. CR093 must therefore implement H1B minimally and auditably rather than falsely treating it as an already validated agent.
