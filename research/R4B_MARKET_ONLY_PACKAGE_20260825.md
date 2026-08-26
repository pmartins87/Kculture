# R4B market-only hosted package — 2026-08-25

## Identity

Validated candidate: `R4B-market-only-validated-v1`

Frozen laboratory source:
- path: `candidates/r4b_ablation_market_only.py`
- source commit: `148cc81fed390fd75c0cba00ceb779efaa17a46f`
- Git blob: `e564125f0c4a1711fd3ea065dc1cb27d4a62ce37`

Upstream base:
- COK V8 commit `779caaec88a441345871e2d62eb5de93606b7b52`
- upstream `main.py` SHA-256 `faf57412e2c56dcc669043865a185324bab9952d865abccc2203284e854eceb3`
- Apache-2.0 with notices preserved

## Build/parity gate

GitHub Actions run: `32919305800`
Artifact: `9589293098`
Artifact ZIP SHA-256: `2e07e216847ad919ec85347038e365a4eb43c2b6645d8d18691092aab1a09fc1`

The self-contained package was rebuilt deterministically from the hash-pinned base plus the Kculture market-only overlay.

Submission archive:
- path produced by builder: `artifacts/submissions/r4b_market_only_v1.tar.gz`
- bytes: `101557`
- SHA-256: `19cc08d2b3bcb8f8f947806c0ee01f4d7643d36f0c15abe0a978129ed1c53117`

Packaged files:
- `main.py` SHA-256 `07bda5229dec0e50b56df8e76523188169213ba7cea4d2e118be61491fdc0cd1`
- `LICENSE-APACHE-2.0.txt` SHA-256 `0d542e0c8804e39aa7f37eb00da5a762149dc682d7829451287e11b938e94594`
- `THIRD_PARTY_NOTICES.txt` SHA-256 `82d23b7e3be4e51abfc770a786e9b24cf85f0e1d13debe188235e45f50aef859`

## Parity result

Four development comparisons (2 seeds × 2 seats) were run independently for:
- frozen laboratory wrapper;
- extracted package `main.py`.

Result:
- comparisons: 4
- identical full action trajectories: **4/4**
- first action divergences: **0**
- terminal statuses/rewards: **identical 4/4**

Terminal rewards matched exactly:
- seed 150614441 seat 0: 158630
- seed 150614441 seat 1: 175301
- seed 583180324 seat 0: 184866
- seed 583180324 seat 1: 173413

## Decision

**PACKAGE_PARITY_PASS.** This exact archive identity is approved for the first hosted Kaggriculture submission.

No held-out seed was opened. Hosted submission/account authentication remains an R3 concern, not a reason to alter this frozen package.
