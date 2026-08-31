# CR024A guarded top19 — Stage B preregistration

Frozen before any CR024A Stage-B reward is observed.

## Motivation

CR023 raw top19 produced a strong Stage-A net advantage over frozen CR008 but had five harmful W/L conversions on the seven still-reproducible current-meta opponents. CR024A Stage-A dynamic diagnosis found one simple identity-free public-state guard eligible for one untouched validation:

- checkpoint clock: `192`
- feature: `dmarket_price_wool`
- direction: `>=`
- threshold: `11.5`
- Stage-A evidence (168 rows): TP=5, FN=0, FP=15, TN=148; recall 1.0; FPR 0.0920

The rule was selected before touching the raw Stage-B seeds. Two originally frozen opponents (`tetsu`, `kaito_future`) are currently inaccessible to authenticated Kaggle output download with HTTP 403. They are excluded mechanically, not strategically. No replacement opponent is introduced.

## Frozen CR024A policy for Stage B

For every episode:

1. execute the frozen `top19_openloop` public action tape from CR023;
2. keep legal public observation snapshots and the frozen CR008 adaptive-history state warm in parallel, without executing CR008 actions;
3. at clock 192 only, compare public WOOL market price with clock 168;
4. if `price_wool(192) - price_wool(168) >= 11.5`, switch permanently at clock 192 to frozen CR008 semantics for the rest of the episode;
5. otherwise remain on top19 for the whole episode.

No seed, opponent identity, submission identity, hidden state, replay identity, or held-out result is available to the runtime rule.

## Untouched Stage B field

Use exactly `raw_backbone_stage_b_seeds` from `configs/cr023_public_tape_preregistered_seeds_v1.json`, both seats, and the seven still-downloadable exact current-meta opponents:

- kaito_sparse
- prvsiyan
- salem
- rayk
- tactical
- boatlee
- andrew

This is 7 × 12 × 2 = 168 paired conditions. The reserved adaptive-overlay seeds and all 32/32 held-out seeds remain sealed.

## Frozen comparisons

Each condition runs three arms:

- frozen CR008 control;
- frozen top19 raw tape;
- CR024A guarded hybrid.

A favorable conversion means an arm changes CR008's W/L score upward. An unfavorable conversion means it changes CR008's W/L score downward.

## Frozen Stage-B promotion gate

CR024A is package-eligible only if all mechanical checks pass and all of the following hold:

1. all 168 rows complete with no errors;
2. Stage B contains at least 2 raw-top19 unfavorable conversions, so guard validation is informative;
3. guard recall on those raw-top19 unfavorable conversions is at least 0.50;
4. guard false-positive rate among raw-top19 non-harmful rows is at most 0.15;
5. CR024A favorable minus unfavorable conversions versus CR008 is at least +4;
6. CR024A unfavorable conversions are at most 60% of raw top19 unfavorable conversions (`ceil(0.60 * raw_unfavorable)`);
7. CR024A total paired W/L score is at least 4 points above CR008 total score;
8. CR024A total paired W/L score is no more than 2 points below raw top19 total score.

If Stage B contains fewer than two raw harmful cases, guard validation is **inconclusive** and CR024A is not packaged from this path. Per the already-frozen CR024 branch, the project moves to a consensus/shrinkage backbone rather than relaxing the guard after seeing results.

If any other gate fails, do not tune the threshold on Stage B. Move to the consensus/shrinkage branch.

## Submission policy

Passing this gate authorizes building a mechanically audited **new strategy package**. It does not authorize resubmitting CR008/CR011 or another near-duplicate calibration agent.
