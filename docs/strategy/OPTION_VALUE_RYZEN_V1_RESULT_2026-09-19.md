# Option-Value Ryzen V1 Production Result — 2026-09-19

Source commit: `6cab6bc2773ec3406e717c1e68cb4971a9d4432f`.

## Run

- 250 fresh seeds;
- V47 mirror, V48, Tactical Memory;
- both seats;
- O-RW1 + O-TW1;
- 1,500 BASE matchups;
- **3,000 counterfactual labels**;
- **584 unique state hashes**;
- **0 failures**;
- engine `1.32.7`;
- exact hosted V47 backbone.

Binding mechanical verdict:
**PASS**.

## Option labels

### O-RW1

- 1,500 rows;
- 348 unique state hashes;
- mean score delta **+0.096**;
- 370 positive;
- 82 negative;
- 1,048 neutral;
- mean margin delta **-161.6493**.

### O-TW1

- 1,500 rows;
- 236 unique state hashes;
- mean score delta **+0.14**;
- 436 positive;
- 16 negative;
- 1,048 neutral;
- mean margin delta **+35.7173**.

O-TW1 is therefore the cleaner intervention in this corpus.

## Population decomposition

V47 mirror:
- 1,000 rows;
- mean score delta **+0.354**;
- 806 positive labels;
- 98 negative labels.

V48:
- 1,000 rows;
- mean score delta **0**;
- no nonzero W/L labels.

Tactical Memory:
- 1,000 rows;
- mean score delta **0**;
- no nonzero W/L labels.

## Interpretation

The large corpus confirms real option headroom, but all W/L signal is concentrated in the
V47-mirror population. This is not yet a sufficient basis for a production selector.

Before model fitting, the project must audit:
1. repeated-state label consistency;
2. feature-alias conflicts;
3. grouped train/dev/test generalization with no state-hash leakage;
4. leave-one-opponent-out behavior;
5. selector realized delta versus always-fire and BASE.

A model is useful only if legal observable-state features can identify when to fire an
option without merely memorizing V47-mirror states.

No Kaggle submission is authorized.
