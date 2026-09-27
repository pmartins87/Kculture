# V35B — Authorized Hosted Pair Submission Result — 2026-09-27

Binding workflow: `36284057319`.

Decision: **`V35B_AUTHORIZED_PAIR_SUBMITTED`**.

User authorization covered exactly:
1. submit Kaito Fast Routes V2 first;
2. submit Barnyard Economist V7 second as keeper;
3. replace V30B + V31C if the final preflight showed no slot drift.

## Final preflight

UTC: `2026-09-27T00:57:41Z`.

Before mutation, latest-two were exactly:
1. V31C `56528406` — `PS_V31C_HEDGE_MOON_MELONS_BBAFAAD4`;
2. V30B `56509591` — `PS_V30B_HERDSAFE_VALIDATED_70D93426`.

No drift.

UTC-day submissions before mutation: **0**.
Projected after both authorized submissions: **2**.

Exact package hashes were re-verified before mutation:
- Kaito V2 archive SHA-256: `1425ce1071d0872cc507660a39278a078cd9be276dcd4e900ecc41ff8b23daf2`;
- Barnyard V7 archive SHA-256: `1573dd58af311c6448640fb89380b63f88b0d63a10e788d516fb928f005be968`.

## Submission 1 — Kaito V2

Description:
`PS_V35_KAITO_V2_3009_1425CE10`.

Registered submission ID:
**`56593613`**.

Immediately after registration, latest-two were verified as:
1. Kaito V2;
2. prior newest V31C.

Thus V30B was displaced exactly as intended.

## Submission 2 — Barnyard V7 keeper

Description:
`PS_V35_BARNYARD_V7_3034_1573DD58`.

Registered submission ID:
**`56593614`**.

Final latest-two:
1. **Barnyard V7 `56593614`** — `PENDING`;
2. **Kaito V2 `56593613`** — `PENDING`.

V31C was displaced exactly as intended.

The order leaves Barnyard as the newest/keeper slot. A future third submission, if ever justified, would displace the older Kaito slot first.

No additional Kaggle submission is authorized by this result.

## Immediate route

1. Monitor Barnyard `56593614` and Kaito `56593613` read-only.
2. Do not mutate slots while both are still in initial validation unless a mechanical failure/invalid submission is observed.
3. First decision checkpoint:
   - first non-empty hosted public score for either candidate; or
   - validation failure/status anomaly; or
   - a sufficiently informative episode count to compare transfer versus their published hosted provenance.
