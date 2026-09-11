# CR079 — SpaTaro chronological imitation gate

Date frozen: 2026-09-11
Branch: `fix/kaggle-parity-v1`

## Objective

Test a narrow hypothesis before building or submitting an executable clone: **does SpaTaro's action policy contain enough repeatable state-conditioned structure that a simple, leakage-safe nearest-neighbour policy generalizes to later hosted episodes materially better than a clock-only baseline?**

This is an offline imitation gate, not a claim that imitation score equals Kaggle win rate. Passing only authorizes an executable legality/H2H stage. Failing rejects this simple clone family; it does not imply SpaTaro itself is weak.

## Frozen corpus

Source GitHub Actions run: `34554072056`.
Artifact: `hosted-spataro-current-corpus-v1`.
Artifact id: `10182031598`.
Artifact SHA256 digest recorded by GitHub: `2db7ac2aa6bc38f09a16281fbb543100bbc931a629f8ecb9630454b908990b98`.

The artifact's own `collector_report.json` and `FILELIST.txt` were verified directly before holdout scoring: **204 replay files, 204 listed episodes, 0 collection failures**. Exactly one replay (`107017328`) has `TeamNames=["SpaTaro","SpaTaro"]`, so the target seat is ambiguous and is excluded rather than guessed. Expected unique-target corpus: **203 episodes**.

This replaces an earlier preliminary inventory that stated 203 total / 7 ambiguous; that preliminary count was incorrect. The correction was made before any holdout action-fidelity score was computed and does not change the model, features, weights, gates, or split rule. The artifact digest above also corrects an earlier provenance transcription before scoring.

## Split — frozen before holdout scoring

1. Identify the unique SpaTaro seat from `info.TeamNames`.
2. Exclude ambiguous/missing-target episodes.
3. Obtain episode chronology from `episodes_command.json` `createTime`; replay metadata may be used only as a fallback for sorting if chronology is absent, and the fallback count must be reported.
4. Sort complete episodes oldest to newest.
5. Oldest 75% = training; newest 25% = holdout. The split is at episode level, never at action/step level.
6. Deterministic rounding rule: `train_count = floor(0.75 * N)`. For the frozen 203 unique-target episodes this is **152 training episodes and 51 holdout episodes**.

No later episode may contribute examples, normalization statistics, action modes, thresholds, or feature choices to training.

## Replay action/observation alignment — frozen before scoring

Direct replay-state verification showed that the action stored at replay index `t` has already been applied to the observation stored at the same index. For example, the step-1 opening market purchases are already visible in the step-1 money, hands, seeds, shed and market inventory. Using `steps[t].observation` to predict `steps[t].action` would therefore leak the answer through its consequences.

Accordingly, each decision example is aligned as:

- legal input state = target seat observation at replay index `t-1`;
- semantic label = target seat action stored at replay index `t`;
- scored decision indices = `t = 1..719` for a complete 720-state replay;
- replay index `0` action is an initialization/dummy record and is not scored;
- the same-step candidate pool and clock baseline are keyed by the **input observation's `step`** (`t-1`).

This alignment is a leakage-prevention correction made before any holdout score was computed; it is not a holdout-driven model change.

## Legal information only

Candidate features may use only information available to SpaTaro at that decision instant:

- step/day/hour and seat/player;
- own public farm state and own `private` observation;
- opponent *public* farm state contained in `farms`;
- current shared market state;
- current town/shop state.

Explicitly forbidden as model features:

- episode id;
- team/opponent names;
- seed;
- current/final reward or winner label;
- future observations/actions;
- opponent private state;
- `remainingOverageTime` or other runtime/timing artifacts.

## Candidate model

A deliberately simple **same-step 1-nearest-neighbour** policy.

For each holdout decision, compare its compact state vector only with training records from the exact same input-observation game step. Numeric features are standardized using training-only mean and scale for that step. Zero-variance dimensions contribute zero distance. Euclidean distance is used after standardization. Deterministic tie-break: earliest training episode in chronological order.

There is no holdout-driven feature selection, value weighting, k tuning, threshold tuning, or route tuning in CR079.

### Frozen compact state representation

The vector contains only numeric/categorical values derivable from the current legal observation:

- clock: day, hour, step;
- current player/seat;
- for both public farms, in seat-relative order (self then opponent): money, farmer coordinates, hires_today, hand count, unlocked-quadrant count; hand-position aggregates; tile-kind counts; crop counts; animal counts; watered/unwatered, fed/unfed, cared/uncared, fertilizer availability and yield-unit aggregates;
- own private state: seeds, shed quantities, and aggregate inventory quantities by item;
- shared market: current price and inventory by item;
- town: fixed indicators for known unlocked shops plus a total unlocked-shop count.

Unknown categorical values encountered by the extractor are mapped into stable hashed-count buckets, never into episode-specific identifiers.

## Action semantics

Actions are evaluated semantically from the target seat's recorded action label aligned to the preceding legal observation.

- **Farmer:** exact canonical farmer action, preserving ordered arguments. Opaque UUID-like tokens, if encountered, are mapped to `<ID>` rather than learned as identities.
- **Hands:** aligned per-slot semantic action accuracy. Missing/extra slots are mismatches. Whole-list exact match is also reported as a diagnostic but is not the gate metric.
- **Market:** exact ordered market-action list. Order is preserved because same-turn order can be causal through the shared market.

`PASS`/empty action is a legitimate label, not discarded.

## Baseline

Clock-only baseline = training **modal semantic action at the exact input-observation step**.

- farmer: mode canonical farmer action for that step;
- hands: mode action independently for each slot index at that step, with an explicit `<MISSING>` label where no slot exists;
- market: mode exact ordered market-action list for that step.

Tie-break for modes is lexical canonical-label order, fixed independent of the holdout.

## Frozen metrics

Gate metrics across all scored holdout decisions:

- farmer exact semantic accuracy;
- hands aligned per-slot semantic accuracy;
- market exact ordered-list accuracy.

Composite:

`0.40 * farmer + 0.35 * hands + 0.25 * market`

The same composite is computed for the clock-only baseline.

Additional diagnostics (not promotion gates): whole hands-list exact match, component confusion/action frequency, per-episode scores, and nearest-neighbour distance summaries.

## PASS/FAIL gate — frozen before scoring holdout

CR079 passes only if **all** conditions hold:

1. candidate composite >= **0.55**;
2. candidate composite - baseline composite >= **+0.08**;
3. candidate farmer accuracy >= **0.50**;
4. candidate hands slot accuracy >= **0.50**;
5. candidate market exact ordered-list accuracy >= **0.35**.

Any failed condition = FAIL.

## Decision tree

### PASS

Build an executable semantic-reconstruction agent, then require:

1. zero/near-zero illegal-action rate under exact Kaggle environment `kaggle-environments==1.32.7`;
2. closed-loop exact-reference testing in both seats;
3. frontier H2H / panel evidence relevant to promotion;
4. only then consider using one of the two hosted submission slots.

Offline imitation PASS alone never authorizes a submission.

### FAIL

Reject **simple SpaTaro same-step nearest-neighbour cloning** as the current prize-scale direction. Do not create CR079A/B/C by tuning the holdout until it passes. Preserve the result and pivot to the predeclared materially different bridge (next priority: Mengfei/current-meta architecture extraction or another independent mechanism), while retaining SpaTaro corpus for descriptive/forensic analysis only.

## Anti-leakage rule

After the holdout is scored, no change to features, model, weights, gates, split, canonicalization, action/observation alignment, or baseline may be called another CR079 validation on the same holdout. A changed model requires a new hypothesis and a genuinely fresh temporal evaluation set.
