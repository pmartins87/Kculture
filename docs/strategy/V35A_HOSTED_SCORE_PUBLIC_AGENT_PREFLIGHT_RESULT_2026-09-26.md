# V35A — Hosted-Score Public Agent Preflight Result — 2026-09-26

Binding workflow: `36222809676`.

Decision: **`V35A_BOTH_HOSTED_STRONG_PACKAGES_READY_FOR_USER_DECISION`**.

No automatic Kaggle submission occurred.

## Exact candidate A — Barnyard Economist V7

Public provenance:
- notebook: `romanrozen/strong-barnyard-economist`;
- exact version: **7**;
- scriptVersionId: `341074820`;
- observed public hosted score at discovery: **3034.8**;
- license: **Apache-2.0**.

Mechanical preflight:
- acquisition: exact versioned notebook output;
- archive bytes: **13445**;
- archive SHA-256: `1573dd58af311c6448640fb89380b63f88b0d63a10e788d516fb928f005be968`;
- archive members: `main.py`;
- main.py bytes: **27244**;
- main.py SHA-256: `997e6bfc5234534e246e945bc61c87858ebf997ab85b0a5c9427dd4ed710f1b6`;
- full 720-step smoke: **4/4 PASS**;
- seeds: `81001,81002`;
- both seats;
- exact engine: `kaggle-environments==1.32.7`.

## Exact candidate B — Kaito Fast Routes V2

Public provenance:
- notebook: `kaitofukami/40-40-early-floor-39-46-top-10-v48-fast-routes`;
- exact version: **2**;
- scriptVersionId: `341206423`;
- observed public hosted score for V2 at discovery: **3009.0**;
- license: **Apache-2.0**.

Mechanical preflight:
- acquisition: exact versioned notebook output;
- archive bytes: **12523**;
- archive SHA-256: `1425ce1071d0872cc507660a39278a078cd9be276dcd4e900ecc41ff8b23daf2`;
- archive members: `main.py`;
- main.py bytes: **21330**;
- main.py SHA-256: `9bdfbafb6755067182d88ce594fd46fb1d712713ffd6931e83d5d50e84bc6fb2`;
- full 720-step smoke: **4/4 PASS**;
- seeds: `81001,81002`;
- both seats;
- exact engine: `kaggle-environments==1.32.7`.

## Read-only hosted preflight

At approximately 2026-09-26 06:09 UTC:

Current latest-two:
1. V31C `56528406` — COMPLETE — public score **2055.2**;
2. V30B `56509591` — COMPLETE — public score **2143.3**.

The ordering above is recency ordering; V30B has the higher score but is the older active submission.

UTC-day quota before any V35A mutation:
- submissions today: **0**;
- currently allowed now: **5**;
- projected after two submissions: **2**.

No slot drift was detected.

## Interpretation

The active hosted pair has materially deteriorated and is far below prize-class range.

V33A's negative result is retained but its scope is now correctly limited to the frozen `kaggle kernels list --sort-by scoreDescending` discovery population and its first 40 new executable SHA-unique policies. It did not include Barnyard V7 and was not a version-aware hosted-score search.

Because the project has repeatedly observed weak transfer from broad local panels to the live ladder, V35A intentionally uses local execution only as a mechanical integrity gate. It does not reinterpret a candidate's hosted public score through another local W/L tournament.

The Barnyard V7 hosted score is current high-confidence evidence. Kaito V2's 3009.0 is historical exact-version evidence and therefore carries more meta-drift risk, but it remains materially stronger evidence than preserving either currently active ~2.1k submission.

## Recommended slot mutation if explicitly authorized

Submit exactly in this order:

1. **Barnyard Economist V7** first.
   - This makes Barnyard newest and evicts older V30B `56509591`.
   - Interim pair: Barnyard + V31C.

2. **Kaito Fast Routes V2** second.
   - This makes Kaito newest and evicts V31C `56528406`.
   - Final pair: Kaito V2 + Barnyard V7.

This consumes 2 of the currently available 5 daily submissions.

The order protects Barnyard through the second submission and leaves the two hosted-score-backed candidates as the latest two.

A fresh read-only latest-two/quota check must occur immediately before mutation. Any slot drift aborts submission and returns to review.

**Explicit user authorization is required before either Kaggle submission.**
