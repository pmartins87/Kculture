# CR081 Gate A — runtime-aligned result

Primary current target: Unknown Mother-Goose, submission `56169353` (~3056.5 in authenticated snapshot run `34668645531`). Deep corpus: run `34669006417`, artifact `cr081-umg_current_56169353`.

The submission exposed 111 episodes at collection time. One UMG-vs-UMG episode is seat-ambiguous and was excluded exactly as predeclared, leaving **110 usable episodes**. Chronological split: **82 development + 28 newest holdout**.

Canonical bridge-family reference is the earliest of the three already-identified recent CR071M hosted loss-family games, selected deterministically before deep-corpus inspection: **Sidharth Hulyalkar, episode 107807039**. The two sibling family examples XiaoYan12 and ocean240812 are effectively the same policy over the tested prefix, so canonicalization does not select a favorable family member.

## Replay indexing correction

A post-Gate implementation audit found that Kaggle stores `steps[s][seat].action` as the action that produced replay state `s`. Therefore runtime `observation.step=t` corresponds to replay action index **`t+1`**, not `t`.

This invalidates only the earlier interpretation that UMG's physical backbone was delayed by one turn. It does **not** invalidate Gate A because both UMG and the bridge reference had originally been compared in the same replay index convention. We nevertheless recomputed the gate explicitly using the correct runtime-aligned replay window: replay actions **1..192** = runtime steps **0..191**.

## Frozen Gate A results, runtime-aligned

Newest-28 holdout, runtime steps 0–191:

- farmer exact-action similarity to bridge reference: **median 0.90104**, mean 0.84059, gate >= 0.80;
- hands exact-action similarity: **median 0.73958**, mean 0.68694, gate >= 0.60;
- market exact-action similarity: median **0.79167** (diagnostic, not required directly);
- development-only per-step modal market policy -> holdout exact market fidelity: **0.94959 overall**, median per episode **0.97917**, gate >= 0.65.

**Decision remains PASS — build exactly one CR081 market-first bridge.** No threshold rescue or reinterpretation was needed.

## Development-only stable-prefix boundary

The candidate boundary is selected from development data only, not from the holdout. Runtime-aligned mean per-step modal support by 96-step block in the 82 development episodes:

| Runtime steps | Farmer | Hands | Market |
|---|---:|---:|---:|
| 0–95 | 0.9562 | 0.9308 | 0.9704 |
| 96–191 | 0.9088 | 0.8573 | 0.9423 |
| 192–287 | 0.8972 | 0.6996 | 0.9144 |
| 288–383 | 0.6230 | 0.1519 | 0.6827 |

There is a sharp regime break after runtime step 287. Therefore the single bridge candidate retains **288 runtime steps** as the fixed stable-prefix boundary. This boundary is not moved in response to H2H results.

## Correct architecture interpretation

The physical lineage does **not** require delaying CR071M. The apparent delay came from replay storage indexing. The correct runtime translation is:

- keep CR071M's physical/runtime backbone at the same runtime step;
- map UMG replay market action indices 1..288 onto runtime steps 0..287;
- retain CR071M safety/repair logic;
- support sequential same-turn market semantics inside that prefix.

The strongest novel market mechanism occurs at **runtime step 0** (stored in replay action index 1): UMG consistently executes `BUY_PRODUCT WHEAT 13`, then `BUY_PRODUCT WHEAT 36`, then `SELL WHEAT 36`. Numerous later market quantities/timings also differ systematically while the physical lineage remains close.

This supports state-safe economic transfer, not replay-route stitching.

## Invalidated implementation run

Workflow run `34671122716` was launched before this replay-index translation bug was caught. Its strategy package delays the physical backbone and is therefore **INVALID / SUPERSEDED**. Any H2H result it may produce must be ignored as policy evidence. The corrected confirmation uses a different fresh seed master so the invalid run cannot contaminate the decision.
