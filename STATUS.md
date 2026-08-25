# STATUS — Kculture

Last updated: 2026-08-25

## Mission status

**Technical phase: R4 ACTIVE.**  
**R1: PASS (2026-08-25).**  
**R2: PASS (2026-08-25).**  
**R3: pending first hosted ladder submission.**  
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

## R4 ACTIVE — strong economic baseline

Current experiment: `KEXP-20260825-004-r4-public-base-screen`.

The first R4 step is deliberately not a hand-written rewrite from the starter. We are screening two independent, public, attributed strong architectures on the frozen 1.32.7 engine:

- COK V8 — `COK-ZhangZiliang/Kaggriculture`, commit `779caaec...`, SHA-256 `faf57412...`, Apache-2.0.
- Seyamalam V21 — `Seyamalam/Kaggriculture`, commit `8b8c421e...`, SHA-256 `0cd14b65...`, Apache-2.0 derivative with preserved attribution.

Protocol uses development seeds only. Each policy is tested against the frozen simple pool and they then play a direct both-seat head-to-head. The winner becomes `R4A-public-base`; Kculture-specific changes then proceed one audited delta at a time.

GitHub Actions workflow: `r4-public-base-screen.yml`, run `32868407585`.

## R3 status

R3 requires the first valid hosted ladder submission and local↔hosted reconciliation. It is not yet PASS.

Account-side prerequisite still pending: confirm Kaggle `Join Competition` / entered status before first submission. Verification can be done through Kaggle UI or `kaggle competitions list --group entered`.

## Immediate next actions

1. Finish R4 public-base screen and freeze `R4A-public-base`.
2. Compare action prefixes and failure modes of the screened bases to determine whether expert-selection/portfolio routing is feasible or whether the first improvement should stay base-local.
3. Add independent strong public opponents so no policy is optimized against one benchmark family.
4. Develop R4 changes on development seeds only; use validation after design freeze and held-out only for promotion.
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
