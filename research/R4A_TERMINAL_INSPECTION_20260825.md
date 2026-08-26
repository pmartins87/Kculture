# R4A terminal route inspection — 2026-08-25

## Evidence

- Workflow: `r4a-terminal-inspection`
- GitHub Actions run: `32913552498`
- Result: **SUCCESS**
- Frozen source: `artifacts/public_opponents/cok_v8_779caae.py`
- COK source commit: `779caaec88a441345871e2d62eb5de93606b7b52`
- Verified source SHA-256: `faf57412e2c56dcc669043865a185324bab9952d865abccc2203284e854eceb3`
- Uploaded inspection artifact ID: `9587681886`
- Artifact ZIP SHA-256 reported by Actions: `3206a1a6e98764a202e96208a045702ff477d0c4bd4fd21921050c96dbffd75c`

All ten current/legacy route tapes have length 719 and last action index 718.

## Step-718 static route summary

| Family | Route | DROP actions at 718 | SELL orders at 718 | Static terminal sale tape |
| --- | --- | ---: | ---: | --- |
| current | `10c4s_3q` | 4 | 4 | STRAWBERRY 2, WHEAT 10, WOOL 4, MILK 6 |
| current | `8c6s_3q` | 4 | 4 | STRAWBERRY 2, WHEAT 10, WOOL 4, MILK 6 |
| current | `6c8s_3q` | 4 | 4 | STRAWBERRY 2, WHEAT 10, WOOL 4, MILK 6 |
| current | `6c12s_4q_first_yarn` | 2 | 2 | WHEAT 8, MILK 6 |
| current | `6c12s_4q_second_yarn` | 0 | 0 | none |
| legacy | `10c4s_3q` | 0 | 0 | none |
| legacy | `8c6s_3q` | 1 | 2 | MILK 3, WHEAT 2 |
| legacy | `6c8s_3q` | 1 | 1 | WHEAT 6 |
| legacy | `6c12s_4q_first_yarn` | 2 | 2 | WHEAT 8, MILK 6 |
| legacy | `6c12s_4q_second_yarn` | 0 | 0 | none |

## Important context from step 717

A zero-sale action at 718 does not automatically mean a liquidation failure. Several routes deliberately perform large `DROP`/`SELL` batches on 717. For example, both `second_yarn` variants perform their terminal cleanup on 717 and then PASS on 718. The static tape therefore cannot prove stranded stock by itself.

The inspection does establish a narrower fact: terminal liquidation behavior is **route-dependent and quantity-fixed**. Current 3-quadrant routes end with the same hard-coded four-product sale bundle, while legacy routes are markedly sparser at action 718.

## Consequence for R4B

This evidence strengthens the rationale for a state-dependent terminal experiment without converting it into a bug claim. `R4B terminal-capacity liquidation` asks whether replacing the final static route action with a current-state inventory/capacity-aware action improves actual outcomes.

What R4B can potentially fix:

- actual inventories differing from the tape's expected quantities because of recovery/preemption;
- available sellable products omitted by a route's fixed terminal sale bundle;
- several actors reaching shed access with more inventory than fixed DROP choices anticipate;
- shed-capacity competition between low-value and high-value actor inventories.

What this inspection does **not** establish:

- that any evaluated episode actually strands inventory;
- that step 718 is the cause of COK's documented late-game revenue deficits;
- that aggressive final liquidation is superior to selling earlier at a better price.

The R4B development tournament remains the causal test. Validation and held-out remain closed until that result is known and the candidate decision is frozen.
