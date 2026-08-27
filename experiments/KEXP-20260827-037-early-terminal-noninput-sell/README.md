# KEXP-20260827-037 — early terminal non-input liquidation

Status: **RUNNING / DEVELOPMENT CANDIDATE**

## Prize-first mechanism

At the default town intervals, step **716** is the final town-consumption tick before terminal scoring. Neither executable step 717 nor 718 has another town tick.

For `CARROT`, `TOMATO`, `STRAWBERRY`, `MELON`, `EGG`, `MILK`, and `WOOL`:

- they cannot be bought back through `BUY_PRODUCT`;
- after step 717 their market inventory cannot decrease before step 718;
- therefore their market price between 717 and 718 can only remain unchanged or fall because of player sales.

For stock that is already in (or same-turn projected into) the shed at step 717, selling one turn earlier is therefore weakly better than waiting for R4B's step-718 liquidation, and may strictly improve price by front-running an opponent terminal dump.

WHEAT and FERTILIZER are intentionally excluded because they remain usable/buyable inputs and do not satisfy the same dominance argument.

## Candidate

`candidates/r4d_early_terminal_noninput_sell.py`

Frozen R4B is unchanged except at executable step 717:

1. obtain R4B's exact base action;
2. use the same frozen COK projected-shed routine already trusted by R4B's step-718 liquidation;
3. preserve every existing market order;
4. append SELL orders for eligible non-input products not already sold in that action, limited by the official 10-order cap;
5. prioritize appended products by current gross sale value.

Step 718 is left to normal R4B. Any stock sold at 717 is absent from the later shed state, preventing double liquidation naturally.

No route, production, WATER, FEED, CARE, PLANT, HARVEST, DROP, seed purchase, opponent-private state, team, episode or seed identity is changed or used.

Candidate blob: `222e9c1de9bab043780af4a1f10bf8cd2f0c210f`.  
Base R4B blob: `e564125f0c4a1711fd3ea065dc1cb27d4a62ce37`.

## Frozen development gate

Run all 16 development seeds in both seats against:

- Kaito V27;
- Rayk V11;
- Andrew V12;
- frozen R4B directly.

Promotion to exploratory live-meta distribution testing requires:

- zero runtime/status errors;
- modern panel no worse than frozen R4B's **81-15**;
- no opponent family loses more than one win versus its R4B reference;
- direct candidate-vs-R4B score rate >= **0.53125**;
- direct mean terminal delta > 0.

Because the intervention is a one-turn market-only front-run with a mechanics-based dominance argument, a clean direct edge plus panel preservation would justify immediate exploratory distribution testing. It still would not by itself authorize validation or a hosted submission.

No validation or held-out seeds are accessed.
