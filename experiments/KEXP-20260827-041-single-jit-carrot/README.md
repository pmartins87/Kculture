# KEXP-20260827-041 — single JIT CARROT candidate

Status: **RUNNING / DEVELOPMENT CANDIDATE**

## Prize-first mechanism

KEXP-040 passed its predeclared gate: one step before mechanically safe late WHEAT slots, the legal public-state signal

`q * (CARROT_price - WHEAT_price) - 20 > 0`

predicted positive later comparative value with 100% oracle-sign precision in both development and exploratory live-meta pools.

For the 614→615 opportunity specifically:

- same-route yield is exactly `q=3` by KEXP-034;
- every one of the 36 audited episodes has at least one frozen-R4B `PLANT WHEAT` at state 615;
- every sign-positive episode in KEXP-040 also has a sign-positive opportunity at this block.

This makes it the lowest-risk first deployable crop controller.

## Candidate

`candidates/r4d_jit_carrot_one.py`

Frozen R4B is delegated everywhere except:

1. at state 614, if `3*(Pc-Pw)-20 > 0`, append exactly one `BUY_SEED CARROT` when a market slot is free;
2. record a conservative counterfactual next-turn CARROT seed stock for untouched R4B;
3. at state 615, only if observed CARROT stock exceeds that frozen-base expectation, replace exactly one actual R4B `PLANT WHEAT` intent with `PLANT CARROT`;
4. otherwise do nothing.

The wrapper therefore refuses to spend a base-reserved CARROT seed if the added purchase failed.

Candidate blob: `97e102933f96a85fcc586ec4a96500069902f035`.
Frozen R4B blob: `e564125f0c4a1711fd3ea065dc1cb27d4a62ce37`.

## Development gate

Run all 16 frozen development seeds in both seats against:

- Kaito V27;
- Rayk V11;
- Andrew V12;
- frozen R4B directly.

Promotion requires:

- zero runtime/status errors;
- combined modern-panel W/L no worse than R4B's 81-15;
- no family loses more than one win versus the R4B reference;
- direct candidate-vs-R4B score rate >= 0.53125;
- direct mean terminal delta > 0.

A candidate that only raises coin margin but ties direct score 0.50 is not promoted. A passing result authorizes exploratory distribution testing and a second, still-bounded CARROT conversion; validation and held-out remain closed.

No seed, episode, opponent or team identity is a policy feature.
