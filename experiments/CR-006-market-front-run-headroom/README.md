# CR-006 — Opponent-aware market front-run headroom

Status: **FROZEN / READY TO RUN**

## Question

CR-005 proved that opponent public state predicts several SELL events four turns ahead on a strict future-day test. Does that forecast expose enough **economic headroom** to justify an exact counterfactual market best-response candidate?

This is a screening experiment, not a promotion experiment. It measures the isolated value of selling inventory before a correctly forecast rival dump and an explicit false-positive wait-upside proxy.

## Frozen protocol

- train adaptive CR-005 decision trees on 2026-08-23..25;
- strict test day: 2026-08-26;
- top 20 complete official episodes;
- both players, states 96..695;
- products: CARROT, TOMATO, STRAWBERRY, MELON;
- four-turn horizon;
- identity-free public features only;
- prediction trigger: adaptive SELL probability **>= 0.20**;
- require our own private shed to contain at least one unit of the same product at trigger time.

## Value proxy

For each trigger, use the official `market_price()` curve and current public market inventory.

If the opponent really sells `Q` units of the product inside the four-turn horizon:

1. compute exact revenue from selling all currently-held units **before** those `Q` rival units;
2. simulate the rival `Q` units entering supply first under the official price-floor/inventory rules;
3. compute exact revenue from selling the same held units **after** the rival dump;
4. the difference is **isolated front-run headroom** attributable to the rival sale.

For a false-positive trigger, use a conservative opportunity-cost proxy: if the observed market inventory four turns later would have produced higher revenue for the same held units than selling now, record that upside as false-positive regret.

This is not a full causal replay because our early sale would itself alter later market/town trajectories. A PASS only authorizes CR-007 exact replay/action-tape counterfactual testing.

## Predeclared screening gate

`FRONTRUN_HEADROOM_PASS` requires all of:

1. >= **50** stock-eligible triggers on the strict test day;
2. true imminent-sale precision among those triggers >= **0.55**;
3. summed true-positive isolated headroom / summed false-positive wait-upside regret >= **1.50** (infinite if regret is zero and headroom positive);
4. mean `(true-positive headroom - false-positive regret)` per trigger >= **$10**;
5. at least **2 products** have positive net proxy with >=10 stock-eligible triggers each.

If PASS, build CR-007 exact counterfactual market response. If FAIL, do not ship a broad front-running rule; inspect product-specific timing/confidence or move adaptation to production/capital allocation.

No validation/held-out data. No opponent identity features.
