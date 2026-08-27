# KEXP-20260827-045 — double JIT CARROT candidate

Status: **DEVELOPMENT PASS / EXPLORATORY REPLICATION RUNNING**

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

## Current decision

Development alone is insufficient because KEXP-041 failed exploratory replication despite a strong local result. KEXP-045 is therefore being replicated immediately on the 20 exploratory live-meta environmental seeds × both seats.

Exploratory run is launched from `.github/workflows/kexp045-exploratory-direct.yml`.

A robust positive result in the second distribution is required before fresh validation. Held-out remains sealed.

No seed, episode, opponent or team identity is a policy feature.
