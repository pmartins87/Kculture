# CR071 PRESALE1 stopping decision — 2026-09-09

## Decision

The CR071O opponent-money selector is rejected. Do not create further CR071P/Q/R variants derived from the same step-110 selector hypothesis.

The simple CR071M `PRESALE1` variant is the nominated candidate for the next hosted Kaggle probe. Local micro-tuning on this line stops here.

## Why the selector line stops

Fresh validation run `34353924026` used 32 paired seeds from a fourth independent seed set (`master_seed=9092028`).

- CR071M PRESALE1 vs CR053: 44-20 (0.6875)
- CR071O OPPMONEY190 vs CR053: 42-22 (0.65625)
- PARENT vs CR053: 36-28 (0.5625)
- CR071O vs CR061: 64-0
- CR071O vs CR065: 63-1

CR071O failed its frozen gate because it did not beat PRESALE1 by at least two games. Decision from the workflow: `REJECT_CR071O_FRESH_GATE`.

## Four independent CR053 replications for PRESALE1

Using the frozen CR071M package and exact Kaggle reference environment:

1. Screen: PRESALE1 20-12 vs PARENT 13-19
2. Fresh confirmation: PRESALE1 38-26 vs PARENT 24-40
3. Broad-frontier seed set: PRESALE1 36-28 vs PARENT 32-32
4. Fourth fresh validation: PRESALE1 44-20 vs PARENT 36-28

Combined diagnostic total across the four independent batches:

- PRESALE1: 138-86 = 61.61%
- PARENT: 105-119 = 46.88%
- 112 paired seeds / 224 games per policy against CR053

Every independent batch favored PRESALE1 over PARENT. This combined total is diagnostic rather than a new post-hoc promotion gate, but it is sufficient to stop further local selector tuning and move to a hosted probe.

## Robustness already observed

Across prior screen, fresh confirmation, and broad-frontier validation, PRESALE1 showed no material regression versus CR061, CR065, CR068A, or CR068B. In the broad-frontier comparison it was effectively neutral against the CR070A parent itself.

## Exact hosted-probe package

`CR071M_CR053_PRESALE1_SEATSAFE_V1.tar.gz`

SHA256:

`dbc6fc2b2c3673b1d9fc36e103b8369a53c7f2cc33381e11a3cb5f769bebe652`

Do not substitute CR071O or any regenerated package without revalidating the hash.

## Stopping rule

No more local variants derived from the current PRESALE1/step-110 selector line before a hosted Kaggle observation.

Next action: one controlled hosted probe of the exact frozen PRESALE1 package, compared against the current hosted baseline under the same meta period. Further development should depend on that hosted evidence, not another chain of local micro-threshold tests.
