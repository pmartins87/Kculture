# ROADMAP — Kculture

> **Current update — 2026-09-05:** Read [CR026_CONTINUATION](docs/CR026_CONTINUATION.md) first. CR024 submission 56025052 is near 1600; CR025 is rejected; CR026 Phase 0 finished 8-12. The continuation lists below are historical and superseded. Do not repeat CR008/CR015.

## Objective

Maximize probability of a **top-10 final finish** in Kaggriculture. Architecture, novelty and elegance are secondary. Use heuristics, search, optimization, ML or planning only when evidence says they improve expected prize value.

## Current gate summary

- **R0 COMPLETE** — competition entry/facts frozen.
- **R1 PASS** — exact official starter/environment reproduction.
- **R2 PASS** — deterministic laboratory and seed partitions.
- **R3 DELIVERY PASS / HOSTED CALIBRATION FAIL** — R4B package valid and live, visible hosted rating **161.6 → 135.7 → 110.5**.
- **R4 ACTIVE / FIRST ADAPTIVE PASS ACHIEVED** — KEXP-041 is the first R4D candidate to beat R4B directly while preserving the modern public regression panel.
- **Held-out 32/32 sealed.**

## Decision invariant

Before promoting any idea ask:

1. What failure could this fix?
2. What is the plausible W/L ceiling?
3. What is the cheapest falsification?
4. Does it generalize across seeds/opponent families?
5. Does it improve expected top-10 probability enough to justify opportunity cost?

Hosted/live evidence outranks an attractive local story when they conflict.

## R0 — Intake and official facts

Mechanics, timeline, action API, validation, packaging, ladder and prize structure.

**Status: COMPLETE.**

## R1 — Baseline reproduction

Exact official/simple environment reproduction.

**Status: PASS.**

## R2 — Local tournament laboratory

Deterministic seeds, both seats, fresh module loading, development/validation/held-out separation, raw replays and provenance.

**Status: PASS.**

## R3 — Hosted calibration

Frozen hosted package: `R4B-market-only-validated-v1`.

- exact package/parity passed;
- Kaggle status Complete / green check;
- visible rating **161.6 → 135.7 → 110.5**.

**Status: DELIVERY PASS / CALIBRATION FAIL.**

Interpretation: rules and packaging are working; the fixed-route policy is strategically weak against the real field. R4B remains useful as a deterministic baseline only.

## R4 — Evidence-driven replacement

### R4A/R4B — frozen baseline

COK V8-derived R4B remains immutable as the hosted baseline.

Controlled development panel: Kaito 25-7, Rayk 30-2, Andrew 26-6, combined **81-15 / 96**. This is a regression control, not a live-field strength estimate.

### Closed/deprioritized R4 branches

- fixed route substitutions: no W/L improvement;
- route macro-oracle: perfect ex-post route choice only reaches 83-13;
- terminal CARE patch: neutral;
- final FEED patch: zero/small ceiling;
- blanket terminal WATER suppression: false mechanics premise;
- naive terminal collector: severe regression;
- terminal SELL ordering: no promotion;
- generic PASS reduction: large headroom exists, but official winner-vs-loser data do not support PASS minimization as a primary winning mechanism.

### Live-meta calibration layer

Official daily high-Elo episode datasets are first-class research data. Replay alignment is frozen as `state t -> action frame t+1`; KEXP-028 reproduced 10/10 sampled official episodes exactly.

KEXP-042 full-game atlas shows top agents are highly adaptive and differ structurally from R4B in phase action mix and production composition. This supports moving away from a pure route-tape architecture.

### R4D mechanism 1 — terminal non-input liquidation

KEXP-037 sells eligible non-input products at state 717, before final dump.

- development direct vs R4B: 13-11-8;
- exploratory live-meta direct: **12-8-20**, score 0.55, mean +32.2.

**Status: REPLICATED SMALL COMPONENT.** Keep for later combination, not standalone submission.

### R4D mechanism 2 — state-adaptive crop value

Evidence chain:

- KEXP-026: no free CARROT seed; deliberate purchase/reallocation required.
- KEXP-034: mechanically safe WHEAT/CARROT routes have equal yield in audited blocks.
- KEXP-038: purchase-time value sign survives to later harvest oracle in 234/234 sign-positive events.
- KEXP-040: one-step JIT value rule passes both development and exploratory diagnostic gates.

#### KEXP-041 — single JIT CARROT

Candidate `candidates/r4d_jit_carrot_one.py`.

Development:

- exact modern panel preservation: **81-15**;
- direct vs R4B: **20-12**, score **0.625**, mean +53.53;
- zero errors;
- independent execution audit proves exact intended mutation in 14/14 triggered episodes.

**Status: DEVELOPMENT PASS / EXPLORATORY REPLICATION RUNNING (`33045892841`).**

#### KEXP-045 — double JIT CARROT

Candidate `candidates/r4d_jit_carrot_two.py`.

Adds a second bounded q=3 conversion pair (619→620) to the 614→615 pair.

**Status: DEVELOPMENT SCREEN RUNNING (`33046361583`).**

Gate: modern-panel preservation, zero errors, direct score >=0.5625 and positive mean delta.

### R4 exit criteria

R4 exits when a deterministic adaptive replacement:

1. beats R4B on predeclared development W/L;
2. replicates on exploratory live-meta environmental seeds;
3. survives a fresh exact validation gate;
4. passes package parity;
5. has a mechanism plausibly relevant to hosted weakness.

KEXP-041 has satisfied item 1. Items 2-5 remain.

## R5 — bounded planning/value search

Use only after R4 establishes a trustworthy adaptive base. Candidate areas:

- crop allocation across more than two safe slots;
- bounded forward value of seed/animal/land decisions;
- small terminal planners with exact mechanics;
- compact value models over public state.

There is no requirement to build a full-game solver. Search/planning must target demonstrated headroom.

## R6 — opponent/market robustness

Adapt production, sales, labor and expansion to legal observable opponent/market state without identity memorization.

## R7 — automated strategy search

Automate search over compact auditable spaces using new development pools and strict validation separation.

## R8 — metagame and final portfolio

Use hosted episodes/current meta to construct complementary final agents. Hosted submissions are calibration experiments and later portfolio slots; do not waste them on near-identical policies.

## R9 — final freeze

Reproduce final agents, verify legality/runtime/memory/fallbacks, freeze hashes and submission IDs, and submit before deadline.

## Immediate execution path

1. Finish KEXP-041 exploratory replication.
2. Finish KEXP-045 development screen.
3. If 045 passes, replicate 045 on exploratory live-meta seeds.
4. Select stronger crop controller.
5. Add KEXP-037 only if combination improves against crop-only parent.
6. Freeze candidate and open **fresh validation**.
7. Build exact submission package and parity test.
8. Submit the materially different adaptive candidate to Kaggle for hosted calibration.
9. Use hosted result to decide whether to scale crop/value architecture into R5 or pivot.

## Data separation invariant

- development: open;
- exploratory live-meta environmental pools: open for development/calibration;
- validation: candidate-specific formal gates only;
- held-out: **32/32 sealed** until later final selection.
