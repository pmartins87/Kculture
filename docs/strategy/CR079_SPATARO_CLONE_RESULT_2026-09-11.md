# CR079 — SpaTaro chronological imitation result

Date: 2026-09-11
Branch: `fix/kaggle-parity-v1`
Protocol commit before scoring: `c1409ac88575965da55324c48e8c74c93e13322b`

## Decision

**FAIL — reject simple same-step 1-nearest-neighbour SpaTaro cloning as the current prize-scale direction.**

The frozen candidate failed every preregistered gate and was materially worse than the clock-only baseline on the entire temporal holdout.

## Frozen corpus and split

- source run: `34554072056`
- artifact: `hosted-spataro-current-corpus-v1`
- artifact id: `10182031598`
- GitHub artifact digest: `sha256:2db7ac2aa6bc38f09a16281fbb543100bbc931a629f8ecb9630454b908990b98`
- replay files: 204
- unique SpaTaro target episodes: 203
- excluded ambiguous SpaTaro-vs-SpaTaro episode: `107017328`
- chronological train: 152 episodes
- newest holdout: 51 episodes
- train last createTime: `2026-09-10 08:35:59.428000`
- holdout first createTime: `2026-09-10 09:00:03.585000`
- newest createTime: `2026-09-11 02:04:44.730000`
- scored decisions per holdout episode: 719
- total holdout decisions: 36,669
- feature dimension: 177

Replay alignment used the leakage-safe rule frozen before scoring: observation at replay index `t-1` predicts the action stored at replay index `t`; index 0 dummy action is excluded.

## Results

| Metric | 1-NN candidate | Clock-only baseline |
|---|---:|---:|
| Farmer exact | 0.34299 | 0.39944 |
| Hands aligned slot | 0.22937 | 0.30733 |
| Hands whole-list exact | 0.06005 | 0.06790 |
| Market ordered-list exact | 0.27274 | 0.41956 |
| Composite | **0.28566** | **0.37223** |

Candidate minus baseline composite: **-0.08657**.

The candidate composite was lower than the baseline composite in **all 51/51 holdout episodes**. Nearest-neighbour distance across 36,669 decisions: mean 10.405, median 10.648, p95 15.412.

## Frozen gate evaluation

- candidate composite >= 0.55: **FAIL**
- candidate - baseline >= +0.08: **FAIL**
- farmer >= 0.50: **FAIL**
- hands-slot >= 0.50: **FAIL**
- market >= 0.35: **FAIL**

Overall: **FAIL**.

## Interpretation

The result is stronger than a marginal miss: under the frozen representation, nearest-neighbour state matching actively harms action reconstruction relative to a simple per-clock-step mode. SpaTaro's observed policy is not well captured by this low-capacity Euclidean same-step state metric. This does **not** imply SpaTaro is weak and does not rule out more sophisticated imitation in principle.

Per the preregistered anti-leakage rule, we will **not** tune CR079A/B/C against this holdout. The SpaTaro corpus remains available for descriptive/forensic analysis only.

## Next branch

Pivot immediately to a materially different current-meta bridge. Priority: exploit the much stronger clock/route regularity already observed in the Mengfei hosted corpus, build a reproducible route-level reconstruction rather than another SpaTaro nearest-neighbour variant, then require executable legality and exact-reference H2H evidence before any hosted slot is considered.
