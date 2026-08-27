# KEXP-20260827-036 — terminal SELL impact ordering

Status: **RUNNING / DEVELOPMENT CANDIDATE**

## Prize-first mechanism

The official market processes market-order **slots sequentially**: slot 0 from both players, then slot 1, etc. Within one slot, both players quote each unit from the same pre-commit market inventory. Therefore, when two players liquidate the same product in different slots, the player placing that product earlier receives the less-crashed price first.

Frozen R4B already solves terminal sale completeness, but its step-718 product ordering is not an explicit market-race optimization.

## Candidate

`candidates/r4d_terminal_sell_impact.py`

Everything in frozen R4B is preserved, including:

- all physical unit actions;
- all production/routing decisions;
- projected same-turn DROP accounting;
- exact step-718 terminal SELL quantities;
- the set of products sold.

The only mutation is **order of existing step-718 SELL rows**.

For each SELL item with quantity `q` and current market inventory `I`, compute using the exact frozen price curve:

`impact = q * max(0, price(I) - price(I + q))`

Earlier slots are assigned to larger impact exposure; ties use current gross sale value and unit price. This prioritizes resources whose liquidation value is most vulnerable to being preceded by an opponent dump.

No opponent private inventory, team, seed, episode identity or future state is used.

Candidate blob: `c3a21c93863f39c69ed7e8fe18852c5d4154b96a`.  
Base R4B blob: `e564125f0c4a1711fd3ea065dc1cb27d4a62ce37`.

## Frozen development gate

Run all 16 development seeds in both seats against:

- Kaito V27;
- Rayk V11;
- Andrew V12;
- frozen R4B directly.

Promotion to exploratory testing requires:

- zero runtime/status errors;
- modern panel no worse than frozen R4B's **81-15**;
- no opponent family loses more than one win versus its R4B reference;
- direct candidate-vs-R4B score rate >= **0.53125**;
- direct mean terminal delta > 0.

Because this candidate changes only terminal SELL ordering, a clear direct edge is particularly informative: it isolates market-slot value without confounding physical policy.

Passing does not authorize validation or hosted submission by itself; it authorizes fresh distribution testing and combination with independently supported mechanisms.

No validation or held-out seeds are accessed.
