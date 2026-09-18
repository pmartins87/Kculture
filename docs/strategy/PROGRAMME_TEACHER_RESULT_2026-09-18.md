# Programme suffix teacher — 2026-09-18

## Decision
Infrastructure executed successfully. NO strategic promotion and NO Kaggle candidate.
Do not enlarge training or revive the 32-parameter CEM. The small seed-holdout gain is
insufficient evidence of robust transfer. Next: runtime observation-feature parity,
then opponent-family generalization before Policy/Value scale-up.

## Reproduced corpus
30 notebooks, 23 recovered distinct sources, 799 programme occurrences, 61 unique
719-turn programmes. Modern bank: 41 routes in 17 notebooks; legacy bank: 13 routes
in 7 notebooks. API index position is not a numeric leaderboard score.
62 payload checksums match. The manifest includes its own stale self-hash; that single
entry is excluded, not interpreted as payload corruption. Input hash is in RECEIPT.json.
Recovered tapes are proposals, NOT behavior-equivalent copies of adaptive wrappers.
Existing source-license/provenance classifications remain applicable to redistribution.

## Corrections made before the binding run
- Fix literal escaped shell variables in the Ryzen runner.
- Resolve fetched project ref once; install each source through a temporary file.
- Preserve previous run directories, rather than deleting results on rerun.
- Require the pinned simulator commit in the runner.
- Require exactly 719-turn arrays; longer arrays previously passed shape checks but
  would be decoded with an incorrect inter-programme stride.
- Mask native tile aggregates to fields actually emitted by public tile serialization;
  exclude internal stale values on empty structures. Earlier run is non-binding.
- Retain all per-group candidate margins and programme IDs in the NPZ, enabling Q targets.
- Mark PASS explicitly as infrastructure only. Runtime feature parity remains pending.

## Execution and evidence
Engine commit: f0084b916343c37bbcbdc7de9d833dc96caff78f (1.32.7).
Compiled with GCC in this workspace. 61 × 61 × 12 seeds × 2 seats = 89,304 full games.
Checkpoints: 144,168,192,216,240; 51 exact-prefix groups; 74,664 decision records.
Train seeds 51001–51006; test seeds 51007–51012. Same static opponent bank in both splits.
Records share games/prefixes: they are NOT 74,664 independent trials.
Matrix: 12,312.5 games/s, 7.25 seconds. Whole run: 9.84 seconds (environment-specific).

| Choice | Mean group W/L incl. half ties | Utility |
|---|---:|---:|
| Best static continuation selected on train | 0.55593057 | 0.57286105 |
| State-conditioned depth-4 tree | 0.55890389 | 0.57713682 |
| Offline future-aware oracle | 0.58582449 | 0.60945357 |

Tree improvement: +0.2973 percentage points W/L. Oracle headroom: +2.9894 points.
22 groups have positive utility deltas, 16 negative, 13 neutral.
Per test-seed W/L deltas: -0.00177, +0.01189, +0.01511, +0.01511, +0.01093, -0.03343.
No statistical significance or hosted-rating improvement is claimed.
No seed or opponent ID enters X; both remain dataset provenance only.
Oracle comparisons use exact same-prefix fixed programmes, evaluated from the beginning;
this implementation does not yet clone suffix states to avoid recomputing shared prefixes.
Group trees are independent one-decision experiments, not a tested sequential router.

## Durable evidence
`data/programme_teacher/2026-09-18/` contains corpus manifest, result, full candidate
return targets plus legal-state feature vectors, and SHA256 receipt. Public notebook
source blobs are not republished in this change.

## Gates and stopping rules
1. Establish observation-to-feature and native-action parity on representative programme
   states. Any discrepancy invalidates affected labels; fix and regenerate once.
2. Evaluate routing with held-out opponent families; deduplicate the shared route banks
   when constructing splits. Same-family seed validation cannot establish this.
3. If reproducible W/L/regret gain persists without a concentrated family regression,
   construct the bounded router and run a single end-to-end mechanical game, then hosted.
4. If the gain disappears, close this depth-4 prefix-only router as a promotion candidate;
   use preserved candidate returns to diagnose representation/transform headroom rather
   than another threshold ladder. No dataset/model scale-up until evidence warrants it.

The historical S0/S1 hosted equality and failed native/hybrid policy family remain
negative calibration evidence. Solver + Opponent Model + Value Learning remains the goal.
