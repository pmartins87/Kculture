# KEXP-20260827-045 — double JIT CARROT candidate

Status: **CROSS-DISTRIBUTION W/L PASS / HOLD FOR KEXP-050+051**

## Mechanism

KEXP-045 extends the KEXP-041 one-step JIT rule to two tightly bounded mechanically safe pairs:

- state 614 -> 615, q=3;
- state 619 -> 620, q=3.

At each buy state, append exactly one `BUY_SEED CARROT` only when

`3 * (CARROT_price - WHEAT_price) - 20 > 0`

and a market slot is free. On the following state, convert exactly one actual frozen-R4B `PLANT WHEAT` to `PLANT CARROT` only if observed CARROT stock proves that the added seed arrived above frozen-base expected stock.

Candidate: `candidates/r4d_jit_carrot_two.py`  
Blob: `9d199b3c263254805c64f122367afe180027afeb`  
Frozen R4B blob: `e564125f0c4a1711fd3ea065dc1cb27d4a62ce37`.

## Mechanical execution — PASS

KEXP-048 run `33046797858`, artifact `9636162076`, digest `sha256:de7064346a39f6fcb4e77fe1192334643f014af0afe70530dae4cf6cd80bc155`.

Across 36 development + exploratory episodes:

- 14/36 episodes triggered both pairs;
- development: 6/16;
- exploratory live-meta: 8/20;
- pair 614→615: 14/14 added purchases arrived and 14/14 exact +1 CARROT / -1 WHEAT conversions;
- pair 619→620: 14/14 added purchases arrived and 14/14 exact +1 CARROT / -1 WHEAT conversions;
- zero status errors.

Execution therefore matches design exactly.

## Development W/L — PASS

Run `33046361583`, artifact `9636295255`, digest `sha256:6a24f56ec7169d59e14d85ddf2bb957723ba23a8bdef28eea116f37e44689ca7`.

Modern public regression panel, 16 development seeds × both seats:

- Kaito V27: **25-7**;
- Rayk V11: **30-2**;
- Andrew V12: **26-6**;
- combined **81-15**, exactly preserving frozen R4B;
- zero errors.

Direct candidate vs frozen R4B:

- **22-10**;
- score rate **0.6875**;
- mean terminal delta **+165.5**;
- zero errors.

The predeclared direct gate was >=0.5625 with positive mean delta. KEXP-045 materially passes and improves on KEXP-041's development 20-12 / 0.625 result.

## Exploratory live-meta W/L — REPLICATED

Run `33047810903`, artifact `9636510840`, digest `sha256:52ee9adf5722d10cc5d1d0c45473510ef49862524a70196981878c694112c23c`.

20 independently sourced live-meta environmental seeds × both seats, direct against frozen R4B:

- **17 wins / 11 losses / 12 ties**;
- score rate **0.575**;
- mean terminal delta **-1.05** (essentially neutral money margin);
- seat 0: **11-3-6**;
- seat 1: **6-8-6**;
- zero errors.

This is materially stronger cross-distribution evidence than KEXP-041, which fell to score 0.50 on the same exploratory pool. The W/L signal replicated, but seat asymmetry and neutral mean money keep confidence below validation-ready freeze by themselves.

## Current decision

**Cross-distribution W/L PASS, validation temporarily held.**

Before opening validation, compare two already-running diagnostics/candidates:

1. KEXP-051 paired-world causal audit of the two conversions, to determine whether the replicated W/L comes from own-farm value or market interaction and to inspect the seat asymmetry;
2. KEXP-050 same-slot WHEAT→CARROT reallocation, which pays only +10 incremental seed cost instead of KEXP-045's +20 extra purchase and is evaluated on both open distributions in one protocol.

If neither produces a clearly safer/stronger alternative, KEXP-045 is currently eligible to become the first R4D candidate considered for a fresh validation gate. Held-out remains 32/32 sealed.

No seed, episode, opponent or team identity is a policy feature.
