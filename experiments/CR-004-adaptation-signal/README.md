# CR-004 — Identity-free opponent adaptation signal

Status: **FROZEN / READY TO RUN**

## Prize-first question

Can a Kaggriculture agent predict economically important near-future opponent behavior materially better when it uses the opponent's **public state and recent public-state changes**, compared with an otherwise identical controller that sees only time/environment/self state?

This is the prerequisite for a principled adaptive opponent model. We do not want to build an identity-based counter table or a large adaptive controller before proving that deployable opponent-state information contains forward-looking signal.

## Why now

CR-002 showed that frozen historical public agents are a poorly calibrated promotion field: R4B/KEXP-050 can dominate those references locally while remaining ~142/145 hosted. KEXP-042 also showed that recent live winners differ structurally from R4B in labor utilization and production mix.

The official environment exposes both farms' public state to each agent: money, farmer/hand positions, unlocked quadrants and farm tiles, plus the shared market/town state. Opponent private shed, carried inventories and seeds are not visible. This makes identity-free within-episode opponent modelling legal and technically feasible.

## Frozen data protocol

- train days: **2026-08-23, 2026-08-24, 2026-08-25**;
- strict temporal test: **2026-08-26**;
- top 20 complete official episodes per day;
- use both players, not only winners;
- sample every 24 turns from state 48 through 672;
- replay alignment: action chosen at state `t` is stored on replay frame `t+1`;
- no validation or held-out partitions;
- no team name, team id, agent id, submission id, episode id or seed is ever a model feature.

## Prediction horizon

At each sampled state `t`, predict whether the opponent will perform each economically meaningful macro action during states `t..t+23`:

- SELL each sellable product;
- BUY_SEED for each crop;
- BUY_ANIMAL for COW/SHEEP/GOOSE;
- HIRE;
- BUY_LAND.

Targets without enough positive and negative examples in both train and test are excluded from the aggregate gate before metrics are averaged.

## Feature sets

### Baseline: `environment+self`

Deployable information that does **not** describe the opponent:

- step/day;
- town shop count;
- shared market prices and inventories;
- our public money, workers, unlocked quadrants and farm composition;
- 24-turn changes in shared market and our public farm.

### Adaptive: `environment+self+opponent`

Exactly the same baseline features plus:

- opponent public money, workers, unlocked quadrants and farm composition;
- 24-turn changes in those opponent-public quantities;
- public money/worker/quadrant gaps.

Both models use the same fixed shallow decision-tree hyperparameters. Therefore any systematic test improvement is attributable to opponent-state information rather than extra tuning budget.

## Frozen model

For every eligible binary target:

- `DecisionTreeClassifier(max_depth=5, min_samples_leaf=25, random_state=20260827)`;
- one tree for baseline features;
- one tree for adaptive features;
- no post-test threshold tuning.

Primary metric: **Brier score** on 2026-08-26. Lower is better.

Secondary metric: ROC-AUC when defined.

## Predeclared gate

`ADAPTATION_SIGNAL_PASS` requires all of:

1. at least **5 eligible targets** with >=20 positive and >=20 negative test samples;
2. median relative Brier improvement from adding opponent features >= **3%**;
3. at least **4 eligible targets** improve Brier by >= **5%**;
4. fewer than 25% of eligible targets worsen Brier by > **5%**.

If the gate fails, do not build a broad opponent model from these features. Revisit temporal resolution/history encoding or focus adaptation only on a narrower market subproblem.

If the gate passes, proceed to CR-005: a bounded best-response controller that converts the most predictable opponent events into counterfactual value tests (initial priority: market sale ordering/front-running, labor allocation, and production-mix response).

## Deployment principle

The eventual agent must adapt to **observed state**, never to opponent identity. A legal mental model is poker-style range updating:

1. start with a prior over opponent behavior families;
2. observe public actions/state transitions;
3. update the posterior/forecast;
4. choose the response with the highest estimated value under that forecast;
5. keep a strong fallback policy whenever confidence is low.

Tool: `tools/cr004_adaptation_signal.py`.
