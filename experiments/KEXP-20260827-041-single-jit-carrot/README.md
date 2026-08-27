# KEXP-20260827-041 — single JIT CARROT candidate

Status: **DEVELOPMENT PASS / EXPLORATORY REPLICATION RUNNING**

## Prize-first mechanism

KEXP-040 passed its predeclared gate: one step before mechanically safe late WHEAT slots, the legal public-state signal

`q * (CARROT_price - WHEAT_price) - 20 > 0`

predicted positive later comparative value with 100% oracle-sign precision in both development and exploratory live-meta pools.

For the 614→615 opportunity specifically:

- same-route yield is exactly `q=3` by KEXP-034;
- every one of the 36 audited episodes has at least one frozen-R4B `PLANT WHEAT` at state 615;
- every sign-positive episode in KEXP-040 also has this opportunity.

## Candidate

`candidates/r4d_jit_carrot_one.py`, blob `97e102933f96a85fcc586ec4a96500069902f035`.

Frozen R4B is delegated everywhere except:

1. state 614: if `3*(Pc-Pw)-20 > 0`, append exactly one `BUY_SEED CARROT` when a market slot is free;
2. record a conservative counterfactual next-turn CARROT seed stock for untouched R4B;
3. state 615: only if observed CARROT stock exceeds that frozen-base expectation, replace exactly one actual R4B `PLANT WHEAT` with `PLANT CARROT`;
4. otherwise do nothing.

Frozen R4B blob: `e564125f0c4a1711fd3ea065dc1cb27d4a62ce37`.

## Mechanical execution audit

Independent audit run **33044850064 — SUCCESS**.  
Artifact **9635413649**, ZIP digest **SHA-256 `22cb9915579ffd68f821e058da46dffef8f2e29397fd61fd6186decb915b4ebc`**.

Across 36 development + exploratory episodes:

- signal/buy fired in exactly **14/36** episodes;
- added CARROT purchase committed in **14/14**;
- corresponding state-615 mutation was exactly `+1 PLANT CARROT / -1 PLANT WHEAT` in **14/14**;
- 22/36 non-trigger episodes had exactly zero mutation;
- development: 6/16 conversions;
- exploratory pool: 8/20 conversions;
- zero status errors.

The execution therefore matches the KEXP-040 predicted trigger distribution exactly and does not steal frozen-base reserved CARROT stock.

## Development W/L result

GitHub Actions run **33044755062 — SUCCESS**.  
Artifact **9635541714**, ZIP digest **SHA-256 `55d0b21d15089741f282f172c9850fabe82e52e33c0684cfd6a6eb7b1c990ab3`**.

Modern public regression panel, 16 development seeds × both seats:

- Kaito V27: **25-7**;
- Rayk V11: **30-2**;
- Andrew V12: **26-6**;
- combined: **81-15**, exactly preserving frozen R4B;
- zero errors.

Direct candidate vs frozen R4B:

- **20-12-0**;
- score rate **0.62500**;
- mean terminal delta **+53.53125**;
- zero errors.

The predeclared direct gate was >=0.53125 with positive mean delta. KEXP-041 therefore clears the development gate materially rather than marginally.

## Current decision

**DEVELOPMENT PASS.** This is the first new state-adaptive crop candidate in the R4D branch to produce a clear direct W/L improvement while preserving the full modern public panel.

Before validation, replicate directly on the 20 exploratory live-meta environmental seeds × both seats. A clean replication authorizes testing a second bounded JIT conversion and/or combination with KEXP-037. Validation and all 32 held-out seeds remain closed until the stronger combined architecture is selected.

No seed, episode, opponent or team identity is a policy feature.
