# STATUS — Kculture

Last updated: 2026-08-25

## Mission status

**Technical phase: R4 ACTIVE.**  
**R1: PASS (2026-08-25).**  
**R2: PASS (2026-08-25).**  
**R3: pending first hosted ladder submission.**  
**R4A: frozen public base selected.**  
**R4B: development experiment pending GitHub Actions execution.**  
**R0 account-side confirmation still pending:** competition rule acceptance / entered status cannot be independently verified from this repository.

Goal: produce a **top-10 final result** in Kaggriculture, where each of the top 10 positions pays US$5,000.

## Confirmed competition constraints

- Entry/team-merger deadline: 2026-09-23 23:59 UTC.
- Final submission deadline: 2026-09-30 23:59 UTC.
- Games continue after close until convergence, approximately through 2026-10-15.
- One match spans 30 in-game days × 24 turns = 720 turns.
- Submission must expose an `agent` function from `main.py` at the archive root.
- Up to 5 agents may be submitted per day.
- Only the latest 2 submissions remain tracked and are used for final leaderboard evaluation.
- Validation episode runs the agent against itself before ladder entry.
- Default hosted action timeout is 1 second.
- Submission resources documented by Kaggle: 6.5 GiB RAM, 1.6 vCPU, 8 GiB disk, 100 MiB submission limit.

## Official environment freeze

- Official source: `Kaggle/kaggle-environments`.
- Frozen package: `kaggle-environments==1.32.7` (released 2026-08-15).
- Frozen latest engine-changing commit at intake: `28b6d8af3ce73926b3d0fda1410c1ddd8384ab8c`.
- Upstream file hashes: `official/UPSTREAM_LOCK.md`.
- Official advanced environment specification version: `0.1.0`.
- Current mechanics/market snapshot: `docs/OFFICIAL_MECHANICS_SNAPSHOT.md`.
- The 2026-08-15 engine change materially altered demand curves for previously underused resources; every promoted candidate must regression-test against environment drift.

## R1 PASS — official reference baseline

Experiment: `KEXP-20260825-001-official-starter-parity`.

GitHub Actions run `32858531629` proved exact starter parity on seeds 101/202/303 and full 720-turn self-play on seed 404. Root `main.py` remains the frozen legal/reference starter until a strong candidate is formally promoted.

## R2 PASS — deterministic tournament laboratory

Closure experiment: `KEXP-20260825-003-r2-closure`.

GitHub Actions run `32859938870` established:

- fresh-module loading per episode;
- 64 disjoint deterministic seeds: 16 development / 16 validation / 32 held-out;
- 7 deterministic reference opponents;
- both-seat evaluation by default;
- raw W/L/T, terminal bank, money delta, runtime errors and provenance preserved;
- hash-pinned public-agent acquisition;
- zero runtime errors in closure smoke.

Strong calibration on dev seed `150614441`: frozen carrot reference vs COK V8 produced deltas -143630 and -147719 from the two seats. This makes scaled multi-worker/multi-resource economics the R4 starting point.

## Public-development decision

`pmartins87/Kculture` intentionally remains **public** during the active competition. The owner explicitly accepts the discovery/copying risk in exchange for unrestricted GitHub Actions. This decision is recorded in `docs/DECISION_PUBLIC_DEVELOPMENT.md` and is **not a blocker** for R4-R9.

Competitive code may therefore be committed here. Imported public policies must preserve repository, commit, file path, SHA-256 and license provenance. Credentials, private/unpublished competitor code and redistribution-restricted private replay payloads remain prohibited.

## R4A frozen — first strong public base

Experiment: `KEXP-20260825-004-r4-public-base-screen`.

Two attributed public architectures were screened on the frozen 1.32.7 engine:

- COK V8 — `COK-ZhangZiliang/Kaggriculture`, commit `779caaec...`, SHA-256 `faf57412...`, Apache-2.0.
- Seyamalam V21 — `Seyamalam/Kaggriculture`, commit `8b8c421e...`, SHA-256 `0cd14b65...`, Apache-2.0 derivative with preserved attribution.

Direct first-8-development-seed both-seat result: **COK V8 14–2 Seyamalam V21**, mean COK money delta approximately **+21,064**, zero runtime errors. COK V8 is therefore frozen as `R4A-public-base-v1` in `configs/r4a_public_base.json`.

Seyamalam remains an important independent opponent because it generated more money against the simple pool than COK in the same screen. Prefix-divergence analysis also established that COK and Seyamalam diverge at state index 1, so a late shop-reveal switch between the full policies is not a valid composition strategy.

## R4B active — terminal-capacity liquidation

Experiment: `KEXP-20260825-005-r4b-terminal-liquidation`.

COK's published V8 failure analysis reports a terminal-sale revenue deficit in **57 of 59** recorded losses. The worst route loss cluster is `current:6c8s_3q`; important revenue deficits include WHEAT, MILK and TOMATO.

`candidates/r4b_terminal_liquidation.py` therefore changes **only executable step 718** of the frozen R4A base. It:

1. inspects current shed and shed-adjacent actor inventories;
2. solves an actor-level 0/1 knapsack under the 100-item shed capacity using visible sale value;
3. selects terminal `DROP` actions without allowing lower-value inventory to crowd out higher-value stock;
4. projects same-turn shed state using the upstream execution model;
5. sells every projected sellable product within the market-order cap.

All earlier actions are delegated to the frozen COK V8 policy unchanged.

Development gate uses the first 8 development seeds, both seats:

- R4A vs Seyamalam control;
- R4B vs Seyamalam;
- R4B vs R4A direct.

Required before any validation seed is opened: zero runtime errors, R4B >= same-seed R4A control against Seyamalam, direct score rate vs R4A >= 0.50, and direct mean money delta vs R4A >= 0.

GitHub Actions run `32913752287` is currently queued; **no R4B performance conclusion exists yet**.

## Current public benchmark targets

Discovery snapshot: `research/PUBLIC_BENCHMARK_SNAPSHOT_20260825.md` and `configs/kaggle_public_targets.json`.

Highest-priority exact public versions currently identified:

- Kaito Fukami V27 V4 — public score snapshot **3090.1**, Apache-2.0.
- Rayk Kretzschmar V11 — best score snapshot **2990.4**.
- FlexonaFFt V59 — best score snapshot **2767.3**.
- Andrew Sokolovsky V10 — best score snapshot **2671.3**.

These scores are dated discovery metadata, not permanent ceilings. The current COK R4A is an engineering/reproducibility base, not assumed to be leaderboard-optimal.

Exact-version acquisition is prepared in `r4-acquire-kaggle-public.yml`. Kaggle requires authentication even for public kernel pulls, so the workflow is manual and reads only the GitHub repository secret `KAGGLE_API_TOKEN`; no credential belongs in source control.

## R3 status

R3 requires the first valid hosted ladder submission and local↔hosted reconciliation. It is not yet PASS.

Account-side prerequisite still pending: confirm Kaggle `Join Competition` / entered status before first submission. Verification can be done through Kaggle UI or authenticated Kaggle CLI.

## Immediate next actions

1. Complete the queued R4A terminal inspection and R4B development tournament.
2. If R4B passes its predeclared development gates, freeze the exact candidate before opening validation seeds; if it fails, record rejection and move to the `6c8s_3q` / midgame route weakness.
3. Acquire Kaito V27 V4 and Rayk V11 through the authenticated, hash-preserving workflow once `KAGGLE_API_TOKEN` is configured, then add them to the strong-opponent panel.
4. Keep validation unopened until a development candidate is frozen and held-out unopened until a formal promotion gate.
5. Confirm Kaggle entered status and submit the first strong candidate when local safety/robustness gates pass.
6. Record exact submission ID, source SHA/config and hosted reconciliation in `docs/SUBMISSION_LEDGER.md`.

## Promotion gates

- **R0 PASS:** technical intake complete; account entry confirmation remains pending.
- **R1 PASS:** official/simple baseline reproduced with deterministic diagnostics. **PASS 2026-08-25.**
- **R2 PASS:** reliable simulator/runner, seed partitions, opponent pool, state isolation, provenance checks and tournament logging. **PASS 2026-08-25.**
- **R3 PASS:** first valid ladder submission with local↔hosted behavior reconciled.
- **R4 PASS:** economically strong deterministic policy robustly beats the simple pool and survives strong-public-opponent validation without runtime instability.
- **R5 PASS:** planning/resource-allocation agent beats R4 across diverse opponents/seeds.
- **R6 PASS:** market/opponent-aware adaptations produce robust incremental value.
- **R7 PASS:** automated strategy search/tuning produces held-out gains.
- **R8 PASS:** candidate pair selected for strategic diversity and final robustness.
- **R9 PASS:** final two submissions frozen, independently reproduced, and submitted.

## Known strategic risks

- Ladder rating is adaptive/noisy; controlled local evidence remains primary.
- Final evaluation rewards head-to-head outcomes; raw bank maximization alone is insufficient.
- Environment drift can invalidate economic calibration.
- Fixed/open-loop routes can be copied or overfit; public-state adaptation and portfolio diversity matter.
- Public development exposes our work, a risk explicitly accepted for this project.
