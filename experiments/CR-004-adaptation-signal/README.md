# CR-004 — Identity-free opponent adaptation signal

Status: **COMPLETE / ADAPTATION_SIGNAL_PASS**

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

## Canonical result

GitHub Actions run **`33089536803` — SUCCESS**.  
Artifact **`9653789496`**, ZIP SHA-256 **`249f407625a35e45036c6a15a7936aad74a2747e720846c8a6bf0424bfc835ba`**.

All frozen gates passed:

- eligible targets: **16**;
- median relative Brier improvement from opponent-public features: **+7.10%**;
- targets improving Brier by >=5%: **9/16**;
- targets worsening by >5%: **1/16 (6.25%)**.

Largest strict-test improvements:

| Target | Relative Brier improvement |
|---|---:|
| `SELL_CARROT` | **+53.14%** |
| `SELL_TOMATO` | **+37.71%** |
| `BUY_SEED_CARROT` | **+32.41%** |
| `BUY_LAND` | **+26.08%** |
| `SELL_STRAWBERRY` | **+22.29%** |
| `BUY_SEED_TOMATO` | **+18.47%** |
| `BUY_SEED_STRAWBERRY` | **+16.48%** |
| `BUY_ANIMAL_COW` | **+8.90%** |
| `SELL_MELON` | **+5.30%** |

For `SELL_CARROT`, the adaptive test model reached ROC-AUC ~**0.989**; its dominant features were opponent CARROT acreage and the recent change in opponent CARROT acreage. `SELL_TOMATO` reached ROC-AUC ~**0.974**, with opponent TOMATO acreage as the dominant feature. `BUY_LAND` reached ROC-AUC ~**0.984**, with recent opponent WHEAT change, opponent money and money gap among the major opponent-aware features.

The result is not simply “state helps.” The baseline already had step, market/town state and our own public state. The measured gain comes from adding **opponent-public information** under an unchanged model family and a later-day test.

## Decision

**Proceed to adaptive best-response work.**

CR-004 proves that deployable public observations of the opponent contain meaningful forward-looking signal. It does **not** prove that reacting to every predicted event increases reward. CR-005 must convert the strongest signals into exact value tests.

Initial priority:

1. same-turn / very-short-horizon opponent SELL forecast for CARROT/TOMATO/STRAWBERRY;
2. opponent-aware market order timing/front-running under the official lockstep market engine;
3. opponent-aware expansion/crop allocation only after market responses show positive realized value.

## Deployment principle

The eventual agent must adapt to **observed state**, never to opponent identity. A legal mental model is poker-style range updating:

1. start with a prior over opponent behavior families;
2. observe public actions/state transitions;
3. update the posterior/forecast;
4. choose the response with the highest estimated value under that forecast;
5. keep a strong fallback policy whenever confidence is low.

Tool: `tools/cr004_adaptation_signal.py`.  
Frozen tool blob: `db57a1d7431a205ab6475f6e9435dc8bb8f7abab`.
