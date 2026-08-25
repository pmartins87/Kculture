# KEXP-20260825-003 — R2 closure

## Question

Is the Kculture local laboratory sufficiently reproducible and isolated to promote R2 and begin serious candidate development?

## Frozen setup

- Kculture commit under test: `70c93cfb3c436612c10385267fbc99aa27815efb`
- Environment: `kaggle-environments==1.32.7`
- GitHub Actions run: `32859938870`
- Job: `97841124028`
- CI environment: Ubuntu 24.04, CPython 3.11.16
- R2 seed partitions: 16 development / 16 validation / 32 held-out; 64 total, pairwise disjoint
- Reference pool: 7 deterministic opponents
- Public benchmark: `COK-ZhangZiliang/Kaggriculture` V8 at commit `779caaec88a441345871e2d62eb5de93606b7b52`, Apache-2.0, SHA-256 `faf57412e2c56dcc669043865a185324bab9952d865abccc2203284e854eceb3`

## Reproducibility checks

All workflow stages passed:

1. frozen package install;
2. official-starter parity and 720-turn self-play;
3. R2 seed/pool/provenance configuration validation;
4. fresh-module single-episode execution;
5. frozen reference pool tournament from both seats;
6. hash-pinned public-opponent fetch;
7. strong public benchmark match from both seats;
8. artifact preservation.

Config validator result:

- 64 unique seeds;
- 16 development;
- 16 validation;
- 32 held-out;
- 7 deterministic reference opponents;
- 1 hash-pinned public artifact;
- result: PASS.

Fresh-module episode check at seed 505 reproduced the official starter exactly at 3589–3589 with both agents `DONE`.

## Reference-pool smoke

Development seed `150614441`, both seats, 14 games total:

- 4 wins;
- 4 ties;
- 6 losses;
- 0 errors;
- tie-half score rate: 0.428571;
- mean money delta: -289;
- median money delta: 0;
- worst delta: -2505 (simple melon);
- best delta: +544 (pass).

This is intentionally not a strength gate: the frozen root `main.py` remains the official carrot reference. The result demonstrates that matchup execution and aggregation work and that the pool exposes obvious weaknesses.

## Strong public benchmark smoke

The COK V8 artifact downloaded as 158,056 bytes and matched the frozen SHA-256 exactly.

Against COK V8 on development seed `150614441`:

| Candidate seat | Kculture starter | COK V8 | Margin |
|---:|---:|---:|---:|
| 0 | 4,389 | 148,019 | -143,630 |
| 1 | 3,665 | 151,384 | -147,719 |

Both games completed `DONE/DONE`; zero runtime errors. Mean margin: -145,674.5.

The size of this gap is useful calibration: R4 must be a qualitatively different production system, not a small tweak to the carrot starter.

## Artifact

GitHub Actions artifact:

- name: `local-lab-smoke`
- artifact ID: `9567787169`
- ZIP SHA-256: `4dd229326eb1b5874817e45137f274ffee1ebd2387d3683bc1d15ea50c9b4af7`

## Decision

**R2 PASS — 2026-08-25.**

The runner, state isolation, seed discipline, deterministic reference pool, provenance checking, raw result preservation, and strong-opponent execution are adequate for serious candidate work.

## Newly identified competition-code exposure gate

`pmartins87/Kculture` is currently public. Competitive candidate source should not be committed publicly during active development: it would expose the policy to competitors, and Kaggle's competition-code sharing rules must be respected. Tooling, official snapshots, and already-public benchmark research can remain traceable here; private candidate work requires a private source location before implementation proceeds.

R3 also remains account-side blocked until competition-rule acceptance / entered status is confirmed and a hosted submission can be made.
