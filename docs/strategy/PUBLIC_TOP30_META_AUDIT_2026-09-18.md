# Public Top-30 Meta Audit — 2026-09-18

## Scope

The authenticated Kaggle CLI returned the live public code list sorted with `scoreDescending`.
The first 30 current notebooks were downloaded successfully (30/30) and statically audited
without executing their notebook code.

The CSV returned by the CLI contains ref/title/author/run-time/votes, but not the numeric
score column. Therefore rank below means **position in the score-descending API response**;
it is not a reconstructed numeric rating.

## Main finding: the apparent diversity is much smaller than 30 independent agents

Static source recovery produced 23 unique extracted agent sources from the 30 notebooks.

Exact source duplicates include:
- ranks 1 and 2: identical V47 source, SHA-256 `f4ecd487...`
- ranks 3 and 15: identical source, SHA-256 `45628c71...`
- ranks 7 and 11: identical V39 source, SHA-256 `708c7485...`
- ranks 18, 19, 28 and 29: identical V45-lineage source, SHA-256 `2536d41e...`
- ranks 23 and 24: identical Pipe-7 source, SHA-256 `6150b7f9...`

More importantly, most of those different wrappers contain one of only two shared long
programme libraries.

### Modern 41-route bank

A compressed payload with `actions/routes/shops` reconstructs 41 complete 719-turn
programmes. The same payload appears in ranks:

1, 2, 3, 4, 5, 8, 13, 15, 16, 18, 19, 21, 22, 23, 24, 28, 29.

These notebooks differ materially in guards, market transformations, opening edits,
routing and terminal logic, but much of their physical route chassis comes from the same
41-route programme family.

### Legacy 13-route bank

A compressed `base + 12 patches` payload reconstructs 13 complete 719-turn programmes.
It appears in ranks:

6, 7, 9, 10, 11, 12, 26.

The legacy and modern banks are distinct programme sets.

### Additional independent programmes

Static extraction also found:
- rank 14 conditional-memory route
- rank 17 compact replay-consensus routes
- rank 20 v21 tactical-memory route
- rank 25 four complete tapes plus decision-tree router/model files
- rank 27 explicit V14 parent route (final overlay promotion is notebook-test-dependent)
- rank 30 two native C++ tapes

After exact tape deduplication, the current extractor produces **61 unique 719-turn
programmes** from the Top-30 sample.

## Competitive pattern

The high-ranking public meta is primarily:

```
strong long programme
+ sparse observable-state routing
+ exact guards / repair
+ market microstructure
+ bounded programme transformations
+ terminal / storage exactness
```

It is not primarily end-to-end PPO.

This is consistent across the major lineages.

## Selected mechanisms worth preserving

### V46 / V47 / V48 family

The modern route chassis is augmented by:
- first-turn wheat market microstructure
- sale preemption when stock is physically ready
- clone/public-similarity gating
- sale-queue ordering
- shop-dependent livestock choices
- impossible-sale cleanup
- storage / overflow protection
- exact terminal settlement

V48 adds queue cleanup around executable sale capacity.

### V38 / V39 family

The legacy route chassis adds:
- feed decisions based on production/care opportunity cost
- bounded wheat replenishment
- protected grain pickup scheduling
- fertilizer-sale protection
- reservation before market rush

### Rank 14 conditional memory

Uses public farm state to select nearest identity-free route memory and changes market
sell order without using hidden identity/seed/opponent-private information.

### Rank 20 v21 tactical memory

The notebook states that exact main.py SHA
`630125b3f592fdb773f1fac6532b08e97e829ae188180ea17540b702b606a054`
was submitted as competition submission ref `55284874` with a public score snapshot of
`2837.3`.

Treat this as a claim recorded in the downloaded public notebook; the competition's
Submissions page remains authoritative for current asynchronous rating.

The runtime itself is a small tactical-memory programme, not a large neural policy.

### Rank 25 "2715-6"

The downloaded submission is a multi-file programme router:
- `actions.json`: four complete 719-turn tapes
- `model.json`: small staged decision structure
- `observation.py`: feature extraction
- `main.py`: bounded routing

Its architecture is especially relevant: complete programmes are selected at dawn
boundaries using only own/public features and conservative out-of-domain handling.

This independently validates the architecture now being built in Kculture:
**state-conditioned routing between strong programmes**.

### Rank 30 Apex V7

Uses a compiled C++ policy plugin with two route tapes and a sparse visible-state decision
at a block boundary, plus budget protection. Its C++ source contains an Apache-2.0 SPDX
notice.

## What this changes for Kculture

The failed native 32-parameter controller should remain only as a randomized/exploiter
opponent family.

Keep:
- bit-exact kagsim 1.32.7
- L2 vector simulator
- native high-throughput evaluation
- CR053 / CR089 historical programmes
- CR086 legal opponent sensor
- economic findings (care, feed/wheat, livestock, fertilizer, sale timing)

Competitive nucleus becomes:

```
Public + historical strong programme library
        ->
exact-prefix / transaction-compatible continuation set
        ->
exact native counterfactual suffix evaluation
        ->
state-conditioned continuation targets
        ->
Policy + Value distillation
        ->
league evaluation + bounded runtime search
```

The first conservative teacher only allows a route switch when candidate programmes have
the exact same already-executed prefix. Therefore the candidate suffixes all start from
the same exact current state; no hidden state reconstruction is needed.

## First corpus/search gate

The committed corpus extractor statically recovers public source payloads without running
the notebooks and produces a deduplicated dense tape bank.

Expected result for this Top-30 snapshot:
- notebooks: 30
- unique extracted sources: 23
- unique 719-turn programmes: 61
- action width: 170

The first programme teacher evaluates the full programme matrix in native C++, then at
checkpoints 144, 168, 192, 216 and 240:
1. forms exact-prefix-compatible continuation groups;
2. generates the legal observable state for both seats across fresh seeds/opponents;
3. exact-evaluates every continuation;
4. creates an offline oracle target;
5. fits a small state-only decision tree on train seeds;
6. evaluates it on disjoint holdout seeds against a fair best-static-continuation
   baseline.

No seed or opponent identity is included in the router feature vector. Seeds are retained
only as offline provenance.

The purpose of this gate is not to claim Kaggle rating. It tests whether **observable
state can exploit suffix choice headroom in the strong programme library**. If yes, the
next stage is Policy + Value distillation of the generated counterfactual targets. If
not, the next expansion is bounded transactional transforms / non-prefix programme
bridges rather than another fixed-controller CEM.
