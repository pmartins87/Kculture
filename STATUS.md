# STATUS — Kculture live source of truth

Updated: 2026-09-14

Authoritative branch: `fix/kaggle-parity-v1`.

## Mission

Win / maximize probability of a prize-winning top-10 Kaggriculture finish. Hosted leaderboard strength is the primary outcome. Local H2H is a mechanics/catastrophe/causal tool and must not be treated as a single-opponent proxy for population skill.

## Critical calibration correction

The historically hosted **CR053** that reached the project's best known hosted score is NOT the file later used as `CR053.tar.gz` guardrail in CR083/CR084/CR085 work.

### Real hosted CR053
- submission `56073870`
- filename `R4D_CR053_ROUTE106309334_V1.tar.gz`
- exact historical artifact run `34105008373`, artifact `10012004237`
- exact archive SHA-256 **`095080e791bd8d58369893c1a421beb57b7f64c2808c011f576e09684ffb9a15`**
- source episode `106309334`, seat 1
- original prehosted validation: 1268W / 780L, 61.91%, mean +988.625 vs then-CR029
- latest authenticated historical Kaggle list: **2064.8**

### False local CR053 representative — QUARANTINED AS HOSTED PROXY
- later local anchor SHA **`a9fea4493031cab1aa9b4fe6b45188459fee1c37e95b9a22e5638cb08ca3bd4c`**
- provenance: inherited `CR053_CONTROL.tar.gz`
- it is not byte-identical to hosted CR053 and must never again be described as the 2064.8 agent.

This materially invalidates the former practice of calling tests against `CR053_CONTROL` a guardrail against our strongest hosted agent.

Historical project documentation from 2026-09-07 had already concluded that single-anchor H2H was insufficient and that a broad hosted-calibrated league was required. That requirement is binding again.

## Hosted score hierarchy — exact known project submissions

Current best known historical project reference:

1. **CR053 `56073870`: 2064.8**
2. CR029 `56045848`: historically ~1892 (later authenticated list around mid-1800s)
3. CR052 `56073867`: ~1700–1750
4. CR011 `55866088`: 1723.3 historical checkpoint
5. CR008 `55866079`: 1705.6 historical checkpoint
6. CR083 `56199767`: latest authenticated list ~1619.8
7. CR071M `56124705`: latest authenticated list ~1590.1

Scores move with continuing episodes; exact archives and ordering evidence matter more than any single stale snapshot.

## Current external frontier

Fresh leaderboard CSV frozen 2026-09-14 during CR087 discovery attempt:

1. Majkel1337 `3191.4`
2. SpaTaro `3049.9`
3. ymg_aq `3024.2`
4. DSM `3011.6`
5. Mengfei Li `2984.6`
6. Orbital Terraformer `2980.4`
7. feel the agi `2979.8`
8. HowardLeeTW `2978.9`
9. Otter Vibe `2959.9`
10. redblackbst `2958.4`

Target class remains ~3000+, not incremental improvement around 1600.

## CR086 — opponent private-inventory representation PASS

Legal mechanical estimator confirmed on an independent strong-agent holdout, 100,660 commodity-step observations:
- MAE `1.25005`
- p95 abs error `9`
- interval coverage `0.969462`
- `stock>=10` accuracy `0.956338`

No identity/rating/EpisodeId/hidden seed/future/opponent-private runtime features.

## CR086 — latent-supply SELL-priority candidate

Exact SHA **`11296a4e658f37c109a2cc953be0ea7db8e2fbde6286ac483e0466f52f4af888`**.

Mechanism: preserves CR083 route, physical actions, market-order multiset/products/quantities; only reorders existing premium SELL slots by mechanics-derived cash-at-risk from estimated latent opponent supply.

Fresh Gate A `34800444746` vs exact CR083:
- **26W–6L–0T = 0.8125**
- mean margin **+260.5625**
- 13–3 from each seat
- zero errors/non-DONE
- paired CI95 `[0.6875, 0.9375]`

Hosted probe submitted exactly once:
- submission **`56220184`**
- description `CR086_LATENT_SUPPLY_11296A4E`
- submitted 2026-09-14 03:21:23 UTC
- one-shot read-only status workflow `34802927151` was started; do not poll it repeatedly.

## Hosted-calibrated league — ACTIVE

Workflow `.github/workflows/hosted-calibrated-league-v1.yml`, commit `a42b4589e568e3203ede7dad653e1c000f22b710`.

Exact bytes included:
- CR053_REAL `095080e7...b9a15` (~2064.8 hosted)
- CR052_REAL `b650a31d...b278d` (~1700–1750 hosted)
- CR083 `648fbcdb...41b8` (~1619.8 latest authenticated)
- CR086 `11296a4e...f888` (hosted probe active)

Fresh paired tests use master `9190861`. Purpose: calibrate local league structure against known hosted ordering and place CR086 relative to the true CR053, not the false control.

## CR087 — current top-lineage mining — ACTIVE

Current community/meta evidence indicates top agents remain largely heuristic/fixed-policy lineages with selective market adaptation. The project is therefore mining current top-team active submissions directly via Kaggle `team-submissions` + public episodes rather than relying on notebook titles.

First run `34803046771` failed only because current leaderboard CSV is rankless and already sorted; frozen CSV was preserved and confirmed the current top scores above.

Parser fixed in commit `666f8f0f3ddce078fc643789a48cd706a69db0ec` and discovery relaunched automatically. Miner now preserves every individual 719-action tape plus medoid/modal consensus statistics for population search.

## Public notebook benchmark — characterization only

Run `34798209070`: three public executable agents each lost 0–32 to CR083. This no longer means CR083 is globally stronger; it only characterizes those exact public bytes in that matchup. A cross-anchor diagnostic run `34802342857` was started but still in progress at its one permitted check. Do not poll repeatedly.

## Closed / quarantined classes

CR078, CR079, CR080 replay stitching, CR081 static market-prefix transplant, CR082 1-NN teacher imitation, CR084 FEED rescue, CR085 Pareto gating: closed / do not retune spent hypotheses.

Direct adoption of the three screened public notebook packages is closed; their ideas remain research evidence.

## Binding operating policy

- Hosted leaderboard/prize objective governs architecture choices.
- Local tests must use exact hosted bytes when claiming calibration against a hosted agent.
- Use a heterogeneous hosted-calibrated league, never one incumbent alone.
- Authenticated Kaggle API first for current meta/submission evidence.
- Exact H2H uses `kaggle-environments==1.32.7`, isolated packages, both seats.
- No identity/EpisodeId/rating/hidden seed/future/opponent-private runtime features.
- Original final holdout remains sealed.
- No repeated polling loops.
- Distinct mechanically valid architectures may receive hosted probes earlier; local rigor must prevent broken submissions, not prevent learning from the actual population.
