# ROADMAP — Kculture

## Objective

Maximize probability of a **top-10 final finish** in Kaggriculture. Architecture, novelty and elegance are secondary. The project may use heuristics, search, optimization, ML, planning or public strategy components whenever measured evidence says they improve expected prize value.

See `docs/PRIZE_FIRST_DECISION_POLICY.md`.

## Current gate summary

- **R0 COMPLETE.** Competition entry user-confirmed.
- **R1 PASS — 2026-08-25.** Official starter/environment reproduction.
- **R2 PASS — 2026-08-25.** Deterministic laboratory and frozen seed partitions.
- **R3 PASS for hosted delivery.** First exact R4B package is valid/Complete and live. Hosted score observed **161.6 → 135.7**, creating a major calibration problem.
- **R4 ACTIVE.** `R4B-market-only-validated-v1` remains frozen hosted champion. No R4D has earned promotion.
- **Held-out 32/32 sealed.**

Public repository development is deliberate. See `docs/DECISION_PUBLIC_DEVELOPMENT.md`.

## Decision invariant

Every new idea is a hypothesis. Before an architectural pivot ask:

1. What competition failure could this fix?
2. What is the plausible W/L ceiling?
3. What is the cheapest experiment that can falsify it?
4. Does it generalize across seeds/opponent families?
5. Does it improve expected top-10 probability enough to beat the opportunity cost?

Hosted evidence outranks an attractive local story when they conflict.

## R0 — Intake and freeze official facts

Capture mechanics, timeline, action API, validation, packaging, ladder and prize structure.

**Status:** COMPLETE.

## R1 — Baseline reproduction

Exact 720-turn official/simple reproduction.

**Status:** PASS.

## R2 — Local tournament laboratory

Deterministic seeds, both seats, fresh module loading, development/validation/held-out separation, raw replays and provenance.

**Status:** PASS.

## R3 — Hosted calibration

First package identity:

- `R4B-market-only-validated-v1`;
- archive SHA-256 `19cc08d2b3bcb8f8f947806c0ee01f4d7643d36f0c15abe0a978129ed1c53117`;
- packaged `main.py` SHA-256 `07bda5229dec0e50b56df8e76523188169213ba7cea4d2e118be61491fdc0cd1`;
- package parity run `32919305800`, 4/4 exact trajectories;
- Kaggle status `Complete`, green check;
- observed live score sequence **161.6 → 135.7**.

**Status:** DELIVERY PASS / CALIBRATION FAILING.

The key task is no longer merely “get on the ladder”; it is explain why a locally strong 81-15 public-panel agent is performing so poorly hosted. Capture hosted Episodes/replays as soon as exposed and reconcile opponent distribution, W/L/T, rating uncertainty and runtime behavior.

## R4 — Strong baseline and evidence-driven replacement

### R4A — COK V8 frozen base

**Status:** COMPLETE / FROZEN.

### R4B — terminal market completeness

Physical-DROP optimizer rejected. Market-only terminal completeness survived validation and packaging parity.

**Status:** VALIDATED / HOSTED CHAMPION.

### R4C — guarded ninth cow

**Status:** NO PROMOTION.

### KEXP-010/011/012 — public meta screens

Older panel saturated. Exact modern public panel established:

- Kaito V27: 25-7;
- Rayk V11: 30-2;
- Andrew V12: 26-6;
- combined R4B: **81-15 / 96**.

This is useful controlled evidence but demonstrably not a calibrated live-field proxy.

### KEXP-013/014 — hard replay and lifecycle diagnosis

Repeated pattern: several hard losses are still ahead near step 672, then reverse in the final ~47 turns. Generic weeds/expiry explanation did not generalize.

The `8C/6S` weakness found in KEXP-014 is an **observed physical state at step 672**, not automatically the COK internal route label. That distinction is mandatory going forward.

### KEXP-015 — fixed route replacements

- baseline: 81-15, +5,720.5 mean;
- default→10C/4S: 81-15, +5,908.542;
- default→6C/8S: 78-18, +5,700.260.

**Status:** COMPLETE / NO PROMOTION.

### KEXP-016 — legal public-context diagnostic

Corrected run `32968422225`, all jobs PASS. It separated physical-state observations from the actual shop-prefix route signal and captured public money/layout/labor/market context.

**Status:** COMPLETE / DIAGNOSTIC ONLY.

### KEXP-017 — macro-oracle value-of-information

Run `32972566807`, 288 games. Perfect ex-post choice among baseline, default→10C/4S and default→6C/8S yields only:

- Kaito 25-7 → 25-7;
- Rayk 30-2 → 32-0;
- Andrew 26-6 → 26-6;
- combined **81-15 → 83-13**.

**Decision:** solver/route-oracle architecture **DEPRIORITIZED**. It cannot fix the majority of known losses. Bounded optimization/search remains allowed when tied to a higher-value subproblem.

### R4D — next candidate search

R4D is not a predetermined architecture. It must come from the strongest reproducible failure mechanism.

Current priority search space:

1. **Hosted-field mismatch:** what opponents/states make R4B weak online?
2. **Late-horizon reversals:** why Kaito/Andrew can erase advantages after ~672 when route choice cannot fix them.
3. **Action throughput:** worker utilization, movement, harvest/drop timing, shed access/capacity, idle/PASS rate.
4. **Economic exit timing:** when to stop investing/producing and turn remaining horizon into cash.
5. **Dynamic market response:** product timing and price-impact interaction with observable opponent state.
6. **Broader distribution robustness:** new exploratory seeds and newer/diverse public strategies.

Candidate methods may include manual mechanics fixes, parameter sweeps, evolutionary search, black-box optimization, supervised policy selection, value models or bounded lookahead. Choose by empirical return per engineering time, not by label.

**R4 exit:** a deterministic replacement materially improves cross-family W/L on predeclared development tests, survives a fresh exact validation gate, and has a plausible mechanism relevant to hosted failures.

## R5 — broader strategy search/planning (conditional)

Only pursue if R4 evidence shows high expected value. Possible tools:

- compact parameter/evolutionary search;
- state-value approximations;
- bounded late-game search;
- learned contextual policies;
- coherent long-horizon planner.

There is no requirement to build a solver or planner. They compete with simpler methods.

## R6 — opponent/market robustness

Use legal observable market/opponent state to adapt production, sales, labor and expansion without identity memorization.

## R7 — automated search at scale

Automate strategy search over compact, auditable spaces using newly generated development pools and strict validation separation.

## R8 — metagame and final pair

Use hosted episodes and current public meta to construct two complementary final candidates. The latest two submissions are strategic portfolio slots.

## R9 — final freeze

Reproduce final agents, verify imports/legality/time/memory/fallbacks, freeze hashes and submission IDs, submit both before deadline.

## Data-separation invariant

- original development: open;
- new exploratory development pools: allowed if independently generated and documented;
- validation: candidate-specific formal gates only;
- held-out: **32/32 sealed** until later promotion/final selection.
