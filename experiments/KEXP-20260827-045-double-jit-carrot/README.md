# KEXP-20260827-045 — double JIT CARROT candidate

Status: **RUNNING / DEVELOPMENT CANDIDATE**

## Why this follows KEXP-041

KEXP-041 was the first state-adaptive crop controller to pass a direct W/L gate: 20-12 against frozen R4B on the 16-seed development partition while preserving the exact 81-15 modern public-panel result.

KEXP-045 tests whether the same mechanics-derived value rule scales from one to two bounded conversions without destabilizing the route.

## Candidate

`candidates/r4d_jit_carrot_two.py`

Frozen R4B is delegated everywhere except two mechanically audited pairs:

- state 614 -> 615, same-route yield `q=3`;
- state 619 -> 620, same-route yield `q=3`.

At each buy state, append exactly one `BUY_SEED CARROT` only when the public-state value test

`3 * (CARROT_price - WHEAT_price) - 20 > 0`

is positive and a market slot is free. On the next state, convert exactly one actual frozen-R4B `PLANT WHEAT` to `PLANT CARROT` only if observed CARROT stock proves that the added purchase executed above the conservative frozen-base expectation.

No seed, team, episode, opponent identity or future information is used.

Candidate blob: `9d199b3c263254805c64f122367afe180027afeb`.
Frozen R4B blob: `e564125f0c4a1711fd3ea065dc1cb27d4a62ce37`.

## Predeclared development gate

Run all 16 frozen development seeds in both seats against Kaito V27, Rayk V11, Andrew V12 and frozen R4B directly.

Promotion to exploratory live-meta testing requires:

- zero runtime/status errors;
- combined modern-panel W/L no worse than frozen R4B's 81-15;
- no opponent family loses more than one win versus its R4B reference;
- direct candidate-vs-R4B score rate >= **0.5625**;
- direct mean terminal delta > 0;
- direct score rate must not be materially worse than KEXP-041's 0.625; if it falls below 0.5625, the second conversion is rejected.

Passing does not open validation or held-out by itself. It authorizes exploratory distribution testing and later combination with independently replicated KEXP-037 terminal liquidation.

No validation or held-out seeds are accessed.
