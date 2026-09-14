# FP001 E3 — single-hand crop-density result

Date: 2026-09-14
Run: `34868854114`
Conclusion: **PASS — M6S1 selected**

## Frozen question

How much crop work can one first-cost daily hand absorb while the COW5_DAILY main-farmer backbone remains byte-for-byte intact?

The treatment grid was frozen before results in `FP001_E3_SINGLE_HAND_CROP_DENSITY_PROTOCOL_2026-09-14.md`. No post-result treatment was added.

## Environment

Causal economics environment:

- `weedSpawnChance=0`
- `townShopUnlockInterval=999`
- deterministic town-center demand preserved
- 720 steps, starting money 3000
- two fresh nominal seeds × both seats
- exact `kaggle-environments==1.32.7`

Because random shops and weeds were removed, the two seeds/seats are a symmetry / hidden-dependence check rather than independent statistical evidence. Every treatment produced exactly the same result in all four cases.

## Results versus COW5_DAILY animal-only BASE

| Treatment | Crop output | Final-bank delta | Increment vs BASE |
|---|---:|---:|---:|
| BASE | none | 14,989 | — |
| S1 | 8 STRAWBERRY | 15,908 | **+919** |
| S2 | 16 STRAWBERRY | 16,740 | **+1,751** |
| S4 | 32 STRAWBERRY | 17,847 | **+2,858** |
| M1 | 6 MELON | 16,515 | **+1,526** |
| M2 | 12 MELON | 17,993 | **+3,004** |
| M4 | 24 MELON | 20,828 | **+5,839** |
| M6 | 36 MELON | 23,739 | **+8,750** |
| M4S2 | 24 MELON + 16 STRAWBERRY | 22,737 | **+7,748** |
| **M6S1** | **36 MELON + 8 STRAWBERRY** | **24,522** | **+9,533** |

Every non-base treatment was positive in 4/4 nominal matched cases and mechanically valid.

## Animal backbone invariants

Every treatment preserved exactly:

- 5/5 COW survival;
- 147 MILK sold per case;
- 121 main FEED actions;
- 112 main CARE actions;
- 274 main moves;
- at most one hand simultaneously.

Thus crop gains did not come from sacrificing the animal economy.

## Hand utilization

Selected M6S1 per episode:

- 17 HIRE orders (first hand only);
- 110 hand moves;
- 174 hand PASS turns;
- 86 WATER;
- 2 FERTILIZE;
- 10 HARVEST;
- full theoretical crop output achieved: 36 MELON + 8 STRAWBERRY.

For comparison:

- S1: 331 PASS turns and +919;
- M6: 111 PASS turns and +8,750;
- M6S1: 174 PASS turns and +9,533.

The apparently higher PASS count of M6S1 than M6 is primarily because STRAWBERRY keeps the hand active for 17 days rather than MELON's shorter 12-day horizon; the relevant result is that the same one-hand architecture still reaches full output without degrading COW work.

## Economic interpretation

MELON dominates STRAWBERRY as the core dense hand workload in this causal environment:

- M1 +1,526 vs S1 +919;
- M2 +3,004 vs S2 +1,751;
- M4 +5,839 vs S4 +2,858.

This matches official mechanics: MELON seed costs 80, can reach six units with ordinary productive WATER, needs no fertilizer, and has base market price 250. STRAWBERRY seed costs 100, uses two fertilizer units to reach eight berries, and has base price 120.

The extra S1 on top of M6 adds +783 net (`9,533 - 8,750`) and still reaches full output, so the frozen selection rule chooses **M6S1**, not M6.

## Decision

**Advance exactly M6S1** to one normal-environment robustness gate.

Do not extend the deterministic ladder to M7/M8 or retune crop density after observing this result. The next gate restores default stochastic weeds and town shops and evaluates expected performance over a broad fresh-seed distribution. Same-seed pair deltas will be reported only descriptively because crop tile occupancy changes the RNG stream used for later town-shop selection; distributional expected performance, tails and mechanical robustness are the promotion criteria.

If M6S1 survives the normal environment, it becomes eligible for integration with CR087 mixed COW/SHEEP macro priors and later heterogeneous population/market-layer testing. If it fails materially, close this fixed crop block rather than patching it against individual seeds.
