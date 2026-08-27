# Competitive Reset — 2026-08-27

## Trigger

Hosted snapshot after the validated KEXP-050 submission:

- KEXP-050: **145.1**;
- R4B at the same snapshot: **142.0**.

KEXP-050 had passed development, an exploratory live-meta pool, a fresh 192-game stress, fresh validation and exact package parity. The tiny hosted separation therefore invalidates the working assumption that the old local strong panel was a sufficiently calibrated promotion proxy.

## Critical benchmark-identity hypothesis

The old strong-panel workflows acquired `main.py` from public Kaggle notebook outputs and treated that file as the scored agent. Several high-scoring notebooks also publish a separate `submission.tar.gz`.

This creates a potentially severe identity error: the exact package submitted to Kaggle may contain a different `main.py`, additional modules, embedded policy data, or generated code. A local W/L result against the notebook-output helper `main.py` is not evidence against the 3000-class scored agent unless package equivalence is proved.

Old local results versus Kaito/Rayk/Andrew are therefore **descriptive only until identity proof**.

## Public ceiling targets to audit

Historical best versions selected before package inspection:

| Target | Exact Kaggle notebook version | Public/best score reference | License status | Reset role |
|---|---|---:|---|---|
| Kaito V27 | `kaitofukami/25-27-strict-future-v27-midgame-meta-reset/versions/4` | 3090.1 | Apache-2.0 verified on public notebook page | highest public ceiling reference |
| Rayk V11 | `raykkretzschmar/kaggriculture-rank-your-agent/versions/11` | 2990.4 best; historical public snapshot 2817.8 | public notebook; derivative reuse remains blocked until exact-version license is independently verified | independent near-ceiling identity audit |
| Andrew V12 | `andrewsokolovsky/kaggriculture-breaking-the-tie/versions/12` | 2883.0 | Apache-2.0 verified | independent high-score reference |
| Flex V59 | `flexonafft/kaggriculture-adaptive-replay-agent/versions/59` | 2767.3 | Apache-2.0 verified | multi-route reference |

Scores are historical discovery references, not permanent ladder ratings.

## CR-001 — exact scored-package identity audit

For each target:

1. download the exact notebook-version output with KaggleHub;
2. hash every output file;
3. enumerate every `.tar.gz`, `.tgz`, `.tar` and `.zip` archive;
4. hash every archive member without committing third-party code into this public repository;
5. locate every packaged `main.py` and compare its SHA-256 with top-level notebook-output `main.py`;
6. record package structure, sibling modules and obvious entry-point candidates;
7. classify:
   - `IDENTITY_MATCH`: output `main.py` and packaged `main.py` are byte-identical;
   - `BENCHMARK_IDENTITY_MISMATCH`: exact package `main.py` differs from the file previously benchmarked;
   - `NO_COMPARABLE_PACKAGE_MAIN`: package layout needs further forensic work.

The exact third-party package archives remain GitHub Actions artifacts only. They are not committed to this repository.

## CR-002 — rebuild the benchmark

After CR-001:

- benchmark only exact packaged agents whose entry point can be reproduced faithfully;
- preserve sibling dependencies/package layout;
- rank the public targets against each other and against R4B/KEXP-050 on broad fresh seeds and both seats;
- compare the local ordering with the historical hosted ordering 3090 > 2990 > 2883 > 2767.

A local benchmark is promotion-grade only if it demonstrates useful rank correlation with known hosted strength. Raw victory totals against identity-unproven notebook helper files are retired.

## CR-003 — true strong baseline

The next strategic milestone is **not** 145 → 170. It is to reproduce a legitimate public high-strength baseline in the approximate 2000–3000 historical score class, with license/provenance preserved and exact package parity.

Only after that milestone do we resume differentiation. Candidate directions include:

- dynamic production/capital allocation;
- market-aware crop and animal portfolio control;
- high-level behavioral cloning from strong public trajectories;
- bounded search/value models for high-leverage decisions;
- meta diversification to reduce non-transitive matchup risk.

End-to-end PPO is not the first reset step.

## Frozen old line

R4B and KEXP-050 remain useful as hosted calibration references. No more CARROT/TOMATO micro-overlay is allowed to delay CR-001/CR-002. KEXP-056 is paused before workflow launch.

## Prize-first decision rule

If exact public scored packages can be reproduced and immediately move our calibrated baseline into the high hundreds/thousands, continue aggressively. If we cannot reproduce even the public state of the art after package identity is solved, reassess the expected financial return of this competition rather than spending the remaining month on low-impact local patches.
