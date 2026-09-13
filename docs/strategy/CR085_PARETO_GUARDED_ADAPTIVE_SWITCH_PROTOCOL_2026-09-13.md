# CR085 — Pareto-guarded adaptive route switches

Status: **FROZEN BEFORE CANDIDATE BUILD / NO HOSTED SUBMISSION AUTHORIZATION**

Base package: exact frozen CR083.

Base SHA-256:

`648fbcdb370f7e48fafda18a1112c5f1b57a17a81b7191f010fe4058f41a41b8`

## Motivation — exploratory evidence only

CR084 is closed. Its late `noop -> FEED` rescue did not survive promotion and had zero opportunities in the independent temporal high-strength proxy. CR085 therefore does **not** preserve animals by opportunistic FEED patches and does not retune CR084.

Offline decomposition of the already-frozen 36 hosted CR083 replays found a different architecture-level issue:

- all four opponents rated `>=2300` in the old frozen cohort beat CR083;
- two losses executed the prefix-compatible `YARN -> YARN_CARROT` switch at step 360;
- two executed the prefix-compatible `MAIN -> MILK_GLUT` switch at step 433;
- both adaptive tails intentionally reduce late FEED counts and productive capacity compared with their predecessor routes;
- the same adaptive routes also win against weaker states, so the route itself is not universally bad;
- immediately before the destructive late behavior, wins tended to have a substantial public economic cushion while losses did not;
- crucially, at the **natural switch point itself**, every loss in these two adaptive branches failed a zero-threshold public Pareto-dominance test, while several wins passed it.

This is exploratory architecture-design evidence only. It is spent and may not validate CR085.

## New architecture

CR085 changes only the eligibility of the two later adaptive switches already present in CR083.

### Public dominance vector

At the switch observation, compute for each farm from the legal current public observation:

- `money`: current farm money;
- `animals`: count of live animals on public farm tiles;
- `plants`: count of active crop plants on public farm tiles.

For our farm `me` and the opponent farm `opp`, define:

`PUBLIC_PARETO_DOMINANT = (money_me >= money_opp) and (animals_me >= animals_opp) and (plants_me >= plants_opp)`

There is **no fitted margin**, no learned weight, no opponent rating, and no replay lookup. The threshold is the natural zero boundary in each public state dimension.

### Frozen switch rules

CR083 currently has:

- step 226: if `shop_YARN_STORE >= 1`, prefix-compatible `MAIN -> YARN`;
- step 360: if `px_CARROT >= 42`, prefix-compatible `YARN -> YARN_CARROT`;
- step 433: if `inv_MILK >= 10067`, prefix-compatible `MAIN -> MILK_GLUT`.

CR085 freezes the following changes:

1. **Step 226 remains byte-for-byte behaviorally unchanged.**
2. At step 360, `YARN -> YARN_CARROT` is allowed only when both the original CR083 condition and `PUBLIC_PARETO_DOMINANT` are true.
3. At step 433, `MAIN -> MILK_GLUT` is allowed only when both the original CR083 condition and `PUBLIC_PARETO_DOMINANT` are true.
4. If the Pareto guard is false, retain the already-active current route. No later route stitching or mid-tail fallback is allowed.

Because the original `_switch_ok` prefix-compatibility rule remains mandatory and a rejected switch simply keeps the current route, CR085 introduces no state-aliasing transition.

## Explicit non-changes

- no change to CR083 seed-demand clamp;
- no change to original market thresholds `42` and `10067`;
- no change to step 226/YARN decision;
- no change to route tapes;
- no action-level FEED/CARE rescue;
- no route transplant or replay stitching;
- no market-order logic change;
- no CR053 detector/counter change;
- no room guard, dead-stock or sell-clamp change;
- no identity, team name, EpisodeId, rating/rank, hidden seed, future state or opponent-private feature;
- no learned model or fitted coefficient.

## Score-blind semantic audit

Before any score interpretation, a shadow audit must prove on exact observations that:

- CR085 and CR083 are identical except where a step-360 or step-433 switch is blocked by the frozen Pareto guard;
- step 226 behavior is identical;
- all original `_switch_ok` prefix checks remain active;
- the guard uses only the three public farm dimensions above;
- route tapes and all downstream repair/market logic are unchanged;
- candidate rebuild is byte-identical;
- at least one guarded switch is exercised in the audit corpus.

If any semantic check fails, candidate is invalid before score interpretation.

## Fresh seed firewall

Audit master: **`91508509`**.

Gate A master: **`9150851`**.

Promotion master: **`9150852`**.

All generated seeds must have zero overlap with CR079–CR084 masters and with each other.

## Gate A — fresh direct test

16 fresh seeds x both seats = **32 games**.

CR085 vs exact frozen CR083.

PASS requires all:

- exactly 32 games / 16 fresh seeds;
- zero errors / zero non-DONE;
- seat-balanced score rate **>= 0.5625**;
- mean terminal-money margin **> 0**.

FAIL decision:

`CLOSE_CR085_PARETO_GUARDED_SWITCH`

No tuning of the Pareto dimensions, no removal of a dimension, no added monetary buffer, and no per-route exception on master `9150851`.

## Promotion panel — only after Gate A PASS

Master `9150852`, 32 fresh seeds x both seats = 64 games per row:

- CR085 vs CR083;
- CR085 vs CR071M;
- CR085 vs CR053;
- CR085 vs CR061;
- CR085 vs CR065;
- CR083 vs CR071M;
- CR083 vs CR053;
- CR083 vs CR061;
- CR083 vs CR065.

PASS requires:

- zero errors/non-DONE everywhere;
- direct CR085 vs CR083 score rate **>= 0.5625**;
- direct CR085 mean terminal-money margin **> 0**;
- aggregate guardrail score delta versus same-master CR083 across CR071M/CR053/CR061/CR065 **>= 0**;
- each individual guardrail delta **>= -0.0625**.

Promotion FAIL decision:

`CLOSE_CR085_PARETO_GUARDED_SWITCH`

Promotion PASS decision:

`ELIGIBLE_FOR_FUTURE_TEMPORAL_HIGH_STRENGTH_PROXY_ONLY`

A local PASS does **not** authorize a hosted submission.

## Independent population-stress requirement

The 36 old hosted replays used to discover this architecture are spent and prohibited as CR085 validation evidence.

If local promotion passes, the independent high-strength proxy must use only public CR083 episodes created **after this protocol was frozen**. The proxy is evaluated once at a material checkpoint; do not poll repeatedly for episodes.

The proxy protocol itself must be frozen before looking at those future outcomes. A hosted CR085 probe can only be considered if direct, guardrail and independent temporal population-stress layers all pass.

## Interpretation rule

CR085 tests a specific causal proposition:

> **A market-triggered adaptive route that sacrifices later productive capacity should not be entered when our current public farm state is already Pareto-inferior in money, live animals, or active crops.**

If this proposition fails on fresh local seeds, close it. Do not optimize it on spent validation evidence.
