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

### KEXP-010 — full development failure atlas

160 development games completed. R4B reached **32-0 vs Seyamalam V21** and **32-0 vs Kaito V18** across all 16 development seeds × both seats. Direct R4B vs R4A paired-seat aggregate was non-negative on all 16 seeds.

**Conclusion:** older panel saturated; stop tuning to it.

### KEXP-011 — exact Kaito V27 frontier screen

Exact V27 V4 (public/best 3090.1, Apache-2.0, SHA `f48c2116...`) was acquired without Kaggle credentials and hash-verified.

Development result, all 16 seeds × both seats:

- R4A vs V27: **25-7**, mean +4382.03125;
- R4B vs V27: **25-7**, mean +4396.84375.

Seven losses are concentrated in four seeds: `150614441` (seat-sensitive), `1743398262`, `163219477`, `598340816`.

**Decision:** no migration to V27; retain R4B/COK lineage and diagnose frontier regimes.

### R4D — next frontier continuation candidate

R4D must not be created from a single opponent or a single losing seed. Before mutation:

1. capture full V27 frontier replays for the four loss seeds in both seats;
2. benchmark exact Rayk V11 (best 2990.4) and Andrew V12 (best 2915.2) on all 16 development seeds × both seats;
3. identify a recurring mechanism across modern families;
4. propose one auditable midgame/continuation change compatible with COK's opening/state assumptions;
5. preserve R4B terminal liquidation unchanged unless new evidence directly targets it.

Current exact artifacts:

- Rayk V11 `main.py` SHA-256 `adc61ab15b3b4016e49efe525f4906e6ae3bbb66c4ff29ab795ae09df9fbaa5f` — benchmark-only until license independently verified;
- Andrew V12 `main.py` SHA-256 `df4e899ad535754cf2ddbd3c16e48085916b0cd2baa5182a1a2cfc6a856abae5` — Apache-2.0.

Current Actions:

- V27 loss-replay capture: `32926648674`;
- Rayk/Andrew exact strong screen: `32926727240`.

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
