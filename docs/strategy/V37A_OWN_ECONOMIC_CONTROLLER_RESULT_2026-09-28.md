# V37-A — Own Economic Controller Result — 2026-09-28

## Binding run

Workflow: `36369508576` — SUCCESS mechanically.

Package:
- base V30B main SHA-256: `4f8637a3e33348b98f531de246d353f5d2955b2f85480e3fd02bf4a7874f0d01`
- V37-A main SHA-256: `3eff9beeb2164693e44a93eb325e8e5148f621090dfb89e95d8a92e881449491`
- V37-A archive SHA-256: `90cfe5e9456f37f202fd5595655af60846bdf648b497815c870a584532c7735a`

## Mechanical screen

PASS:
- 16/16 complete games;
- both seats;
- opponents: V30B, Ahmed V45, Tetsutani V23, Rayk V22;
- failures: 0.

## Strategic screen

Catastrophic fail:
- vs Ahmed: 0/4, mean margin -172,180.5
- vs Rayk: 0/4, mean margin -154,144.0
- vs Tetsutani: 0/4, mean margin -172,180.5
- vs V30B: 0/4, mean margin -179,186.0

Decision:
**V37A_CLOSE_CASHFLOW_DESTRUCTION_DO_NOT_SUBMIT**.

## Causal forensic

Workflow `36370099982` compared V37-A and exact V30B against Ahmed on identical seeds/seats.

Seed 81201:
- V37-A final bank: 745
- V30B final bank: 78,732

Seed 81202:
- V37-A final bank: 671
- V30B final bank: 89,616

The divergence begins early:
- step 48: V37-A bank 2 vs V30B 88
- step 96: 0 vs 284
- step 192: 0 vs 546
- step 288: 0 vs 15,647

V37-A removed parent SELL orders while retaining downstream purchases/hires/production assumptions. The result withheld ordinary output (for example fertilizer sells) and starved the organism of working cash.

This is an architecture error, not a threshold error. Do not retune V37-A.

## V37-B

Run `36370387010`: supply-first surplus monetization.

Rule:
- never remove/reorder/modify existing parent orders;
- append only bounded finished-product surplus sales at the END of the market queue;
- only under shed pressure or late horizon;
- no wheat/fertilizer interference.

## V37-C

Run `36370602453`: late-day idle-harvest rescue.

Rule:
- never replace a non-PASS physical action;
- only convert PASS actors standing on harvestable yield during hours 20..23;
- capacity guard protects end-of-day shed delivery;
- no market modification.

## Live hosted state / quota

Read-only snapshot workflow: `36370420608`.

At `2026-09-28T02:35:53Z`:
- latest: Ahmed V36 shot 1 `56619409` — 1400.8
- second: Barnyard V7 `56593614` — 750.4
- Kaito V2: 761.0 (no longer in latest-two)
- historical V30B `56509591`: 2010.0
- submission limits: `numTotal=37`, `numAllowedNow=5`

The current active pair has no strategic protection.

## Current route

1. Finish V37-B and V37-C mechanical/regression screens.
2. Do not use offline results as leaderboard proof.
3. First mechanically eligible V37 candidate is intended for hosted calibration.
4. A fresh exact V30B control is strategically useful after the first V37 shot so the final pair can become V30B-control + V37 candidate before later adaptive replacements.
