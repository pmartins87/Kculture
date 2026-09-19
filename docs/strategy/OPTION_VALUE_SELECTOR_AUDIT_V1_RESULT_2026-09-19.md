# Option-Value Selector Audit V1 — Result — 2026-09-19

Input corpus:
- 3,000 rows;
- 584 unique state hashes;
- O-RW1 + O-TW1;
- V47 mirror + V48 + Tactical Memory.

## State-grouped split result

Binding tool output before seed-group hardening:
`OPTION_VALUE_SELECTOR_AUDIT_PASS_LEARNABLE`.

Selected ridge:
- lambda: `0.01`;
- threshold: `0.1`;
- dev realized selector delta: **+0.1352087**.

Held-out state-group test:
- rows: 681;
- always-fire delta: **+0.1248164**;
- selector realized delta: **+0.1372981**;
- row-oracle delta: **+0.1372981**;
- positive captures: **187/187**;
- negative fires: **0/17**;
- nonzero sign accuracy: **0.9607843**.

This is strong evidence that the legal feature vector contains real information about
whether the option is beneficial inside the sampled mixed population.

## Conflict diagnostics

Exact state+option groups:
- 584 groups;
- 419 repeated;
- 230 with label disagreement;
- only 2 with both positive and negative labels.

Feature-alias groups:
- 283 groups;
- 266 repeated;
- 107 with label disagreement;
- only 1 with both positive and negative labels.

Thus the label is noisy but sign conflicts are rare.

## Leave-one-opponent-out

No cross-family W/L transfer was demonstrated:
- hold out V47 mirror: selector fires 0%, captures 0/806 positives;
- hold out V48: selector fires 93%, but all held-out W/L labels are neutral;
- hold out Tactical Memory: selector fires 95.7%, but all held-out W/L labels are neutral.

Therefore the state-group PASS is **not** authorization for production deployment. It
shows within-population learnability, while population generalization remains unresolved.

## Hardening required

Before fitting a deployable selector:
1. rerun the audit with whole-seed train/dev/test isolation;
2. expand opponent diversity with the V2 league;
3. require positive realized delta on disjoint seeds;
4. evaluate leave-family-out transfer after V2.

No Kaggle submission is authorized.
