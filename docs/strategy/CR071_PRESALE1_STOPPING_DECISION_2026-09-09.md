# CR071 PRESALE1 development policy — 2026-09-09

## Correction

The previous wording in this document incorrectly treated a user question about possible infinite testing as an instruction to stop local development. That was not the user's intent.

The corrected policy is:

- do **not** stop evidence-generating work merely because many tests have already been run;
- do **not** create an open-ended chain of post-hoc threshold tweaks after every near miss;
- stop only a **specific falsified hypothesis/variant family** when its pre-registered gate fails;
- continue with higher-information validation or a genuinely independent strategy hypothesis when useful;
- hosted Kaggle evidence remains important, but it is not an artificial prerequisite for all further local research.

## What is actually closed

The CR071O opponent-money selector is rejected. Do not create further variants that merely retune the same step-110 opponent-money threshold on the already observed data.

Fresh validation run `34353924026` used 32 paired seeds from a fourth independent seed set (`master_seed=9092028`).

- CR071M PRESALE1 vs CR053: 44-20 (0.6875)
- CR071O OPPMONEY190 vs CR053: 42-22 (0.65625)
- PARENT vs CR053: 36-28 (0.5625)
- CR071O vs CR061: 64-0
- CR071O vs CR065: 63-1

CR071O failed its frozen gate because it did not beat PRESALE1 by at least two games. Decision from the workflow: `REJECT_CR071O_FRESH_GATE`.

## What remains open

The simple CR071M `PRESALE1` remains a strong candidate and should continue to receive evidence-driven evaluation and, where justified, independent improvements that are not post-hoc retuning of the failed OPPMONEY190 selector.

Four independent CR053 replications currently favor PRESALE1 over PARENT:

1. Screen: PRESALE1 20-12 vs PARENT 13-19
2. Fresh confirmation: PRESALE1 38-26 vs PARENT 24-40
3. Broad-frontier seed set: PRESALE1 36-28 vs PARENT 32-32
4. Fourth fresh validation: PRESALE1 44-20 vs PARENT 36-28

Combined diagnostic total across the four independent batches:

- PRESALE1: 138-86 = 61.61%
- PARENT: 105-119 = 46.88%
- 112 paired seeds / 224 games per policy against CR053

This combined total is diagnostic rather than a newly invented promotion gate. It supports continuing the line, not ending it prematurely.

## Robustness already observed

Across prior screen, fresh confirmation, and broad-frontier validation, PRESALE1 showed no material regression versus CR061, CR065, CR068A, or CR068B. In the broad-frontier comparison it was effectively neutral against the CR070A parent itself.

## Frozen candidate package

`CR071M_CR053_PRESALE1_SEATSAFE_V1.tar.gz`

SHA256:

`dbc6fc2b2c3673b1d9fc36e103b8369a53c7f2cc33381e11a3cb5f769bebe652`

Do not substitute regenerated packages without revalidating the hash.

## Anti-infinite-loop rule

An infinite loop is avoided by separating **hypothesis testing** from **hypothesis retuning**:

- a failed pre-registered selector hypothesis is not retuned repeatedly on the same evidence;
- a promising candidate can receive larger fresh-sample validation to reduce uncertainty;
- genuinely different mechanisms may still be researched;
- each new experiment must answer a material unresolved question, not merely seek a favorable seed batch.

Next research action: run a larger fresh-sample frontier validation of the frozen PRESALE1 package, then use that evidence together with hosted Kaggle results when available.