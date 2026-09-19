# O-LQ2 Late Canonical SELL Queue — Fresh Causal Result — 2026-09-19

## Binding run

Workflow: **`35456018489`**  
Head: `19e11faf0bb8d04d1ec19a09f6d372438b247df4`  
Aggregate artifact: `10588222629`  
Aggregate digest: `sha256:156c559f975ba717db69aae15000114159353f871a2952054e28c937fd7e461d`.

Mechanical PASS:
- 8/8 seed shards PASS;
- 16/16 paired contexts;
- zero failures;
- pre-trigger parity PASS everywhere;
- exact V47 farmer/hands preserved.

## Binding decision

**`O_LQ2_V48_CAUSAL_PASS`**

Fresh seeds `74401..74408`, both seats:

- BASE score rate: **0.0**;
- O-LQ2 treatment score rate: **1.0**;
- mean score delta: **+1.0**;
- median/mean margin delta: **+555 / +567**;
- positive-score contexts: **16/16**;
- negative-score contexts: **0/16**;
- loss->win: **16/16**;
- loss->tie: 0;
- win->nonwin: 0.

Structural activity:
- mean fire count: **84.625 turns/context**;
- changed slots: **3,122**;
- canonicalized/merged runs: **1,354**.

## Interpretation

This is the strongest first-party causal result in the V48 research branch so far.

O-LQ2 recovers more than the V48 upper bound:
- V4B exact V48 market imitation moved loss -> tie;
- O-LQ2 first-party canonical SELL queue moved loss -> **win in every fresh context**.

Therefore the useful mechanism is not exact imitation of V48. It is the simplified structural rule
identified through V4E:
- always merge duplicate same-product SELLs;
- cap the aggregate to projected own inventory;
- remove zero-effective products;
- compact effective SELLs left.

This strongly suggests that V48's visible queue sanitation contained a more general exploitable market
ordering principle, and the first-party canonicalization removes additional inefficiency.

## Promotion status

O-LQ2 is **not yet globally promoted**.

The next mandatory gate is broad fresh regression across seven opponent families.

Broad protocol:
`docs/strategy/O_LQ2_BROAD_REGRESSION_PROTOCOL_2026-09-19.md`.

No Kaggle submission is authorized by this result alone.
