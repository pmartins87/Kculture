# CR081 Gate A — result

Primary current target: Unknown Mother-Goose, submission `56169353` (~3056.5 in authenticated snapshot run `34668645531`). Deep corpus: run `34669006417`, artifact `cr081-umg_current_56169353`.

The submission exposed 111 episodes at collection time. One UMG-vs-UMG episode is seat-ambiguous and was excluded exactly as predeclared, leaving **110 usable episodes**. Chronological split: **82 development + 28 newest holdout**.

Canonical bridge-family reference is the earliest of the three already-identified recent CR071M hosted loss-family games, selected deterministically before deep-corpus inspection: **Sidharth Hulyalkar, episode 107807039**. The two sibling family examples XiaoYan12 and ocean240812 are ~98.4–100% identical to that reference in farmer/hands and ~99% in market over the first 192 steps, so canonicalization does not select a favorable family member.

## Frozen Gate A results

Newest-28 holdout, steps 0–191:

- farmer exact-action similarity to bridge reference: **median 0.90104**, gate >= 0.80;
- hands exact-action similarity: **median 0.74479**, gate >= 0.60;
- market exact-action similarity: median **0.79167** (diagnostic, not required directly);
- development-only per-step modal market policy -> holdout exact market fidelity: **0.94959 overall**, median per episode **0.97917**, gate >= 0.65.

**Decision: PASS — build exactly one CR081 market-first bridge.** No threshold rescue or alternate Gate-A interpretation was needed.

## Development-only architecture observation

The candidate boundary is selected from development data only, not from the holdout. Mean per-step modal support by 96-step block in the 82 development episodes:

| Steps | Farmer | Hands | Market |
|---|---:|---:|---:|
| 0–95 | 0.956 | 0.932 | 0.971 |
| 96–191 | 0.909 | 0.861 | 0.942 |
| 192–287 | 0.897 | 0.703 | 0.918 |
| 288–383 | 0.629 | 0.154 | 0.687 |

There is a sharp regime break after step 287. Therefore the single bridge candidate uses **288 steps as the fixed stable-prefix boundary**. This boundary is not moved in response to H2H results.

A second development-only finding explains the lineage bridge mechanically: through step 287, UMG's modal physical and market behavior is strongly aligned to the CR071M MAIN route **one step later**. Comparing UMG modal action at step `s` with CR071M MAIN at `s-1` gives, by block:

- farmer: 0–95 **0.9368**, 96–191 **0.8958**, 192–287 **0.7917**;
- hands: 0–95 **0.7789**, 96–191 **0.8021**, 192–287 **0.5312**;
- market: 0–95 **0.9053**, 96–191 **0.8021**, 192–287 **0.6458**.

The strongest novel market mechanism occurs immediately at step 1: UMG consistently executes `BUY_PRODUCT WHEAT 13`, then an additional `BUY_PRODUCT WHEAT 36`, then `SELL WHEAT 36`, before continuing the delayed backbone. Numerous later market quantities/timings also differ systematically, while still retaining the same general physical lineage.

This supports a state-safe economic transfer, not replay-route stitching.
