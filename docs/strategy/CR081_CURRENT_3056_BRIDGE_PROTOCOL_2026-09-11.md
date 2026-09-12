# CR081 — current 3056-lineage bridge protocol

Frozen before collecting the deep current corpus for the selected target lineage.

## Why this target

The authenticated Kaggle API snapshot from run `34668645531` (2026-09-11/12 UTC boundary) shows:

- Majkel1337 3181.9
- ymg_aq 3075.1
- Unknown Mother-Goose 3056.5, current submission `56169353`
- Artem The Farmer 3029.3
- SpaTaro 3029.0

The target is **Unknown Mother-Goose (UMG), current submission 56169353**, not because it is the highest score, but because it is the strongest current agent found with a demonstrated structural bridge from our lineage.

In three independent recent hosted CR071M losses against Sidharth Hulyalkar / XiaoYan12 / ocean240812, the opponent policy is identical to each other over important windows and is closely related to UMG. Comparing the sampled UMG current replays with that hosted loss-family reference over steps 0–191 gives approximately 90% farmer-action equality, 74.5% hands-action equality and 78.8% market-action equality. The family already beat CR071M by roughly 4k–9.6k final reward in those games.

This makes UMG a materially better bridge candidate than replaying the older Mengfei lineage (CR080), while remaining much closer to our known mechanics than fully adaptive SpaTaro/Majkel policies.

## Frozen research question

Can the current ~3056 UMG policy be represented as a stable, legally observable transformation of the CR071M/Tetsu backbone, especially in the market/economy channel, without replay-route stitching?

## Corpus

Primary target: newest 128 episodes of submission `56169353`, fetched through authenticated official Kaggle API with retries and exact episode provenance.

Context corpora, not target-selection data:

- newest 64 episodes of current #1 Majkel1337 submission `56156662`;
- newest 64 episodes of current #2 ymg_aq submission `56161578`.

The target identity and architecture choice above are frozen before those corpora are inspected.

## Analysis split

For UMG, usable episodes are ordered chronologically. Earliest 75% are development; newest 25% are holdout. If target-seat identity is ambiguous, that episode is excluded rather than guessed.

No team name, episode ID, seed, future state, opponent private state or final outcome may be an agent feature.

## Gate A — stable bridge exists

Compare UMG actions with the already-frozen hosted loss-family reference and measure within-UMG policy concentration. A market-first CR081 implementation is allowed only if the UMG holdout satisfies all of:

1. steps 0–191 farmer exact-action similarity to the frozen family reference >= 0.80 median;
2. steps 0–191 hands exact-action similarity >= 0.60 median;
3. market behavior has a reproducible structure: either exact per-step modal coverage >= 0.65 over steps 0–191, or a state-conditioned semantic policy fitted on development improves market-action fidelity by >= 0.10 absolute over a step-only baseline on holdout;
4. no evidence that the apparent bridge depends on opponent identity/private data.

These thresholds are exploratory architecture gates, not final promotion thresholds.

## If Gate A passes

Construct exactly one **CR081 market-first bridge**:

- preserve the robust CR071M physical backbone wherever UMG and the bridge lineage agree;
- port only stable UMG economic/market semantics and any strictly necessary physical actions supported by current state;
- all actions must be reconstructed from legal current observation, not copied with stale IDs;
- no route selection/stitching by nearest replay;
- no UMG identity detector or opponent-name feature.

The candidate then gets a fresh exact paired-seed screen against CR071M and current relevant anchors. Promotion gate will be frozen before seeing those screen results.

## If Gate A fails

Do not make CR081A/B/C by loosening similarity thresholds. Close the market-first bridge and use UMG/Majkel corpora to train a state-adaptive macro-economic policy instead.

## Separation from CR080

CR080 remains closed after confirmation run `34655496708` failed the frozen gate. Its post-failure telemetry is diagnostic only. Nothing in CR081 reopens or retunes CR080.
