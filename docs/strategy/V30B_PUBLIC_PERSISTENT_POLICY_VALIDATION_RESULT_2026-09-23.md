# V30B-R2 — Binding Original Public Persistent Policy Validation Result — 2026-09-23

## Binding protocol

`docs/strategy/V30B_PUBLIC_PERSISTENT_POLICY_VALIDATION_PROTOCOL_2026-09-23.md`, committed before the later non-binding 4-seed protocol. Binding workflow: `35906418993`.

## Mechanics and package parity

- workflow conclusion: SUCCESS
- mechanics: PASS; failures: 0
- immutable V30A selected public ref: `arsgorynich/herd-safe-v3-experimental-risk-aware-feed`
- frozen `main.py` SHA-256: `4f8637a3e33348b98f531de246d353f5d2955b2f85480e3fd02bf4a7874f0d01`
- packaged `main.py` SHA: exact same frozen SHA
- deterministic package archive SHA-256: `70d93426baa309e3a13a6c837504e4d73b177cd05d7d2865c024844e1d2abe7b`
- package parity: exact 8/8 on seeds 80509,80510, both seats, first two executable V30A opponents
- fresh frontier: separately reacquired current Top-30 public-kernel snapshot; 12 executable SHA-unique representatives; smoke failures 0
- validation seeds: 80511..80516; both seats

## Binding validation result

Decision: **`V30B_PUBLIC_PERSISTENT_POLICY_VALIDATED_READY_FOR_USER_DECISION`**.

On the identical fresh common panel:
- candidate score rate: **0.9097222222**
- ALL3 score rate: **0.5833333333**
- mean paired score delta: **+0.3263888889**
- mean paired margin delta: **+6314.2013889**
- median paired margin delta: **+5629.5**
- positive / neutral / negative score contexts: **54 / 90 / 0**
- positive opponent-source breadth: **5**
- positive seed breadth: **6/6**
- positive support: **both seats 0 and 1**

Every frozen validation threshold passed. No threshold, population, seed, seat, candidate, or selector was changed after outcome observation.

## Governance and routing

This result validates exactly the V30A-selected public package for a user decision; it does **not** authorize a Kaggle submission. Preserve public attribution/ref/SHA and package manifest/archive SHA. The protected hosted latest-two remains exact V47 submission `56466970` + ALL3 submission `56367770` until new explicit user authorization.

Next action is read-only slot/quota/latest-two preflight only. If that preflight confirms the protected pair and submission capacity, present this evidence to the user and request explicit authorization before any hosted submission. A new hosted submission would become newest and therefore displace the older ALL3 `56367770` from the protected latest-two pair, while V47 `56466970` would remain, unless Kaggle slot semantics observed in preflight differ.
