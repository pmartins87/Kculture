# ROADMAP — Kculture

## Objective

Maximize the probability of a **top-10 final finish** by combining accurate mechanics, strong long-horizon planning, opponent-aware adaptation, automated local tournaments, disciplined public-meta benchmarking and controlled final-agent selection.

## Current gate summary

- **R0: COMPLETE for working purposes.** Competition entry user-confirmed.
- **R1: PASS — 2026-08-25.**
- **R2: PASS — 2026-08-25.**
- **R3: HOSTED UPLOAD IN PROGRESS.** Exact validated package is being manually uploaded by the user; hosted validation/submission ID/ladder entry are still required for PASS.
- **R4: ACTIVE.** `R4B-market-only-validated-v1` remains the frozen engineering/hosted candidate while frontier diagnostics continue on development only.

Public repository development is deliberate. See `docs/DECISION_PUBLIC_DEVELOPMENT.md`.

## R0 — Intake and freeze official facts

Capture rules, mechanics, timeline, action API, validation behavior, submission packaging, ladder behavior and prize structure.

**Exit:** competition-critical facts traceable/current and competition entry confirmed.

**Status:** **COMPLETE FOR WORKING PURPOSES.**

## R1 — Baseline reproduction

Run official/simple baseline and verify legal actions, 720-turn completion, observations, state transitions and terminal scoring.

**Status:** **PASS.** `KEXP-20260825-001-official-starter-parity`.

## R2 — Local tournament laboratory

- deterministic seeds and both seats;
- development / validation / held-out separation;
- fresh module loading;
- raw outcomes, money deltas, errors, summaries/replays and provenance.

**Status:** **PASS.** `KEXP-20260825-003-r2-closure` froze 16 development / 16 validation / 32 held-out seeds.

## R3 — First ladder submission

- submit the exact validated package;
- pass hosted self-play validation;
- capture submission ID/status;
- reconcile hosted behavior with local execution;
- record rating/episodes and exact hash/source;
- establish disciplined submission cadence.

Exact package:

- candidate `R4B-market-only-validated-v1`;
- archive SHA-256 `19cc08d2b3bcb8f8f947806c0ee01f4d7643d36f0c15abe0a978129ed1c53117`;
- packaged `main.py` SHA-256 `07bda5229dec0e50b56df8e76523188169213ba7cea4d2e118be61491fdc0cd1`;
- package parity run `32919305800`, 4/4 full trajectories identical.

**Status:** **HOSTED UPLOAD IN PROGRESS (user-reported).** Do not mark PASS until Kaggle reports a valid submission and ladder entry.

## R4 — Strong economic baseline and evidence-driven refinements

### R4A — frozen strong public base

COK V8 is `R4A-public-base-v1`.

**Status:** **COMPLETE / FROZEN BASE.**

### R4B — terminal market completeness

Broad physical-DROP terminal optimizer was rejected. Ablation retained only complete final-step market liquidation while preserving every physical COK action.

Validation run `32918640409`:

- 32-0 vs Seyamalam on validation;
- 8-6-18 direct vs R4A, score 0.53125, mean +165.03125;
- zero errors.

**Status:** **VALIDATED ENGINEERING CANDIDATE / HOSTED CANDIDATE.**

### R4C — guarded ninth cow

Development result was neutral.

**Status:** **NO PROMOTION.**

### KEXP-010 — older-panel saturation

R4B reached 32-0 vs Seyamalam V21 and 32-0 vs Kaito V18 across all 16 development seeds × both seats.

**Conclusion:** old panel saturated; stop tuning to it.

### KEXP-011 — exact Kaito V27 frontier screen

Exact V27 V4 (public/best 3090.1, Apache-2.0, SHA `f48c2116...`) acquired without Kaggle credentials and hash-verified.

All 16 development seeds × both seats:

- R4A vs V27: **25-7**, mean +4382.03125;
- R4B vs V27: **25-7**, mean +4396.84375.

**Decision:** no migration to V27.

Full frontier replays then showed a critical pattern: on the three symmetric V27 loss seeds, R4B is still **ahead at step 672** but loses 2.7k–4.5k of relative value during the final ~47 turns. See `research/V27_FRONTIER_REPLAY_DIAGNOSTIC_20260826.md`.

### KEXP-012 — exact current-meta multi-family screen

Exact hash-pinned public outputs:

- Rayk V11, best score snapshot **2990.4**, SHA `adc61ab1...`;
- Andrew V12, best score snapshot **2915.2**, SHA `df4e899a...`.

Actions run `32926727240`, all 16 development seeds × both seats, zero errors:

- R4B vs Rayk V11: **30-2**, mean +7477.21875;
- R4B vs Andrew V12: **26-6**, mean +5287.43750.

Together with exact Kaito V27, frozen R4B is **81-15-0 across 96 current-meta development games**. This is descriptive rather than an independent statistical sample because the same seed panel is reused.

Rayk's only loss regime is `163219477`, both seats; the same seed loses both seats to V27. Andrew exposes different regimes (`150614441`, `393297156`, `598340816`, `1422177419`).

**Conclusion:** R4B/COK remains locally competitive against all three modern public families; failures are state/regime dependent rather than evidence for wholesale architecture replacement.

### KEXP-013 — current-meta hard replay diagnosis

Pre-registered diagnostic run `32927303182` captures:

- Rayk `163219477`, both orientations;
- Andrew `150614441`, `393297156`, `598340816`, `1422177419`, both orientations.

Exact notebook version/hash is checked in each job. Development only.

**Status:** **RUNNING.**

### R4D — next frontier continuation candidate

Do not create R4D from a single opponent or seed. R4D becomes eligible only after KEXP-013 determines whether a repeated legal-state mechanism exists across current families.

Current strongest search region is **late-phase continuation**, approximately after step 600/672, coupling:

1. remaining production horizon;
2. cow/sheep/crop mix;
3. available workers and whether extra HIRE still pays back;
4. harvest/drop throughput into shed;
5. sale timing/product mix;
6. stopping production early enough to realize terminal cash.

Constraints:

- no seed-ID rules;
- no opponent-identity rules;
- preserve frozen R4B step-718 market liquidation unless evidence directly contradicts it;
- one auditable mechanism per candidate;
- first test across all 16 development seeds, both seats, against a diverse strong panel;
- any frozen R4D requires its own future validation gate; old R4B validation cannot be inherited.

**R4 exit:** a deterministic Kculture policy robustly beats diverse strong-current public controls on a predeclared validation protocol, with hosted ladder behavior consistent enough to justify planner work.

## R5 — Long-horizon planner

- state-value approximations for future cashflow/action scarcity;
- planning over planting, harvest, expansion, labor, inventory and sales timing;
- tactical replanning when expected value changes materially;
- coherent board/economic-state model rather than unrelated route switching.

**Exit:** planner beats the R4 champion on a newly frozen validation protocol and later held-out evidence.

## R6 — Dynamic market and opponent awareness

Track observable market/opponent state, infer archetypes and test adaptive production/selling/expansion responses without destabilizing baseline play.

## R7 — Automated strategy search

Parameter sweeps/evolutionary/Bayesian/heuristic search over compact strategy parameters with strict development/validation/held-out separation.

## R8 — Metagame and final pair construction

Use hosted episodes and current public meta to build two complementary final candidates. Latest two submissions are strategic portfolio slots.

## R9 — Final freeze

Reproduce final agents cleanly; verify imports, legality, timeout/memory behavior, deterministic fallbacks; freeze hashes and submission IDs; submit both before 2026-09-30 23:59 UTC.

## Data-separation invariant

- development: open for iteration;
- validation: candidate-specific formal gates only;
- held-out: **32/32 still sealed** until later promotion/final-selection.
