# STATUS — Kculture

Last updated: 2026-08-25

## Mission status

**Technical phase: R2 PASS; R3/R4 preparation.**  
**R1: PASS (2026-08-25).**  
**R2: PASS (2026-08-25).**  
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

GitHub Actions run `32858531629` proved that root `main.py` reproduces the official deterministic carrot starter on fixed seeds and completes 720-turn self-play:

- seed 101: parity PASS, reward 3620;
- seed 202: parity PASS, reward 3601;
- seed 303: parity PASS, reward 3643;
- self-play seed 404: `DONE/DONE`, 3771–3771.

The root starter is a frozen legal/reference baseline, not the intended competitive policy.

## R2 PASS — deterministic tournament laboratory

Closure experiment: `KEXP-20260825-003-r2-closure`.

GitHub Actions run `32859938870` passed every R2 closure stage on `kaggle-environments==1.32.7`:

- fresh-module agent loading per episode prevents global-state leakage between games;
- 64 disjoint deterministic seeds frozen: 16 development / 16 validation / 32 held-out;
- 7 deterministic reference opponents frozen in `configs/opponent_pool.json`;
- raw W/L/T, terminal cash, money delta, errors, seat, seed, environment version, git SHA, and replay/summary artifacts are preserved;
- hash-pinned public benchmark acquisition and provenance validation pass;
- both candidate seats are exercised by default;
- zero runtime errors in closure smoke.

Reference-pool smoke on development seed `150614441`, both seats: 14 games, 4W/4T/6L, mean delta -289. This is expected for the intentionally weak carrot reference and confirms that the pool distinguishes simple strategies.

### Strong public calibration benchmark

Hash-pinned public V8 from `COK-ZhangZiliang/Kaggriculture`:

- source commit: `779caaec88a441345871e2d62eb5de93606b7b52`;
- Apache-2.0;
- SHA-256: `faf57412e2c56dcc669043865a185324bab9952d865abccc2203284e854eceb3`;
- exact frozen artifact downloaded and verified successfully.

On development seed `150614441`, our frozen carrot reference lost from both seats:

- seat 0: 4389 vs 148019, delta -143630;
- seat 1: 3665 vs 151384, delta -147719;
- mean delta: -145674.5;
- both games `DONE/DONE`.

This establishes the scale of R4: competitive work requires a qualitatively different multi-worker, multi-resource economic policy rather than incremental starter tuning.

R2 closure artifact: GitHub Actions artifact `9567787169`, ZIP SHA-256 `4dd229326eb1b5874817e45137f274ffee1ebd2387d3683bc1d15ea50c9b4af7`.

## Strategic source-exposure gate

`pmartins87/Kculture` is currently a **public GitHub repository**. Do not commit the next competitive candidate source here while the competition is active unless we deliberately intend to publish it and have confirmed compliance with Kaggle's competition-code sharing requirements. Publishing the policy would also make direct copying by competitors trivial.

Public-safe material may continue here: official mechanics/version locks, laboratory tooling, experiment protocols, results that do not reveal the private policy, and already-public external benchmark provenance.

**Preferred unblock:** make the authoritative competitive-development repository private, or provide a separate private repository for candidate source while keeping public-safe research/tooling here.

## R3 status

R3 requires the first valid hosted ladder submission and local↔hosted reconciliation. It is not yet PASS.

Account-side prerequisite still pending: confirm Kaggle `Join Competition` / entered status before first submission. Official verification command: `kaggle competitions list --group entered`.

## Immediate next actions

1. Resolve private storage for competitive candidate source before implementing the serious R4 policy.
2. Confirm Kaggle competition entry/account-side acceptance before hosted submission.
3. In the private candidate workspace, create the first economically strong policy family with movement scheduling, land expansion, daily hiring, livestock/crop production, town-demand routing, market-aware selling, recovery logic, and terminal liquidation.
4. Use the frozen R2 development seeds for iteration; validation only after an experiment design is frozen; held-out only for promotion gates.
5. Promote a candidate to R3 only after legal self-play and local tournament sanity checks; record exact submission ID/source/config in `docs/SUBMISSION_LEDGER.md`.
6. Require R4 candidates to dominate the simple reference pool and close a material fraction of the ~145k cash gap to the strong public V8 benchmark before broader planner/search work.

## Promotion gates

- **R0 PASS:** official mechanics, environment, submission contract, evaluation, and account entry captured/confirmed. Technical acquisition complete; account entry confirmation pending.
- **R1 PASS:** official/simple baseline reproduced locally with deterministic diagnostics. **PASS 2026-08-25.**
- **R2 PASS:** reliable simulator/runner, deterministic seed partitions, opponent pool, state isolation, provenance checks, and episode/tournament logging established. **PASS 2026-08-25.**
- **R3 PASS:** first valid ladder submission with local↔hosted behavior reconciled.
- **R4 PASS:** economically strong deterministic baseline robustly beats simple strategy pool.
- **R5 PASS:** planning/resource-allocation agent beats R4 across diverse opponents/seeds.
- **R6 PASS:** market/opponent-aware adaptations produce robust incremental value.
- **R7 PASS:** automated strategy search/tuning produces held-out gains.
- **R8 PASS:** candidate pair selected for strategic diversity and final robustness.
- **R9 PASS:** final two submissions frozen, independently reproduced, and submitted.

## Known strategic risks

- Ladder rating is adaptive/noisy; controlled local evidence remains primary.
- Final evaluation rewards head-to-head robustness, so bank-maximization evidence must be paired with W/L matchup evidence.
- Environment drift can invalidate economic calibration.
- Fixed/open-loop routes can be copied or overfit to shop sequences; strategic diversity and closed-loop state adaptation matter.
- Public source exposure can surrender competitive advantage and create competition-rule obligations.
