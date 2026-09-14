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
- one-shot read-only status workflow `34802927151` completed: submission COMPLETE at the initial `600.0` rating state with only one public episode. This is initialization only; no strength verdict is permitted.

## Hosted-calibrated exact-byte league — COMPLETED / LOCAL ORDER NOT HOSTED-CALIBRATED

Run `34802917553`, master `9190861`, 24 games per edge, zero errors:

- CR083 vs CR053_REAL: **20–4**, score `0.8333`, mean +9833.6;
- CR086 vs CR053_REAL: **20–4**, score `0.8333`, mean +9765.2;
- CR083 vs CR052_REAL: **24–0**;
- CR086 vs CR052_REAL: **24–0**;
- CR053_REAL vs CR052_REAL: **14–10**, score `0.5833`, despite negative mean margin.

This local graph reverses the known hosted hierarchy: CR053_REAL (~2064.8) remains materially above CR083 (~1619.8) on Kaggle. Exact bytes fixed the identity error but did not make local single-seed-distribution H2H a hosted population predictor. The league remains useful for mechanics, catastrophe and diversity; its numeric ordering may not directly promote hosted candidates.

## CR087 — current top-lineage and macro mining — COMPLETE

Corrected discovery run `34803148700` resolved the active submissions of all current top-10 teams and preserved 30 public 719-action tapes, three per team.

Key result: all 30 exact tapes are unique; median cross-pool Hamming distance is 719/719, mean 702.8. Even within the same active submission, hundreds of physical and market actions change between episodes. No step reaches 50% modal agreement across the pool. A modal/medoid tape is therefore not a faithful reconstruction of the current elite.

Macroeconomic profile run `34803658746` parsed 26 replays and shows repeated high-level production families despite action-level variability. Descriptive families to preserve in population work are:

- Majkel / DSM / Orbital;
- Mengfei / feel the agi / redblackbst;
- ymg_aq / Howard;
- Otter;
- SpaTaro.

CR087 CR053-real + latent-supply screen `34803266002` was mechanically safe but economically neutral: 8–8 direct against CR053, and candidate/base were identical at 10–6 against CR052 with the same mean margin. It is **not submitted** absent demonstrated causal impact.

## CR088 — automatic population search — PHASE 0 ACTIVE

Frozen protocol: `docs/strategy/CR088_PHASE0_PROTOCOL_2026-09-14.md`.
Workflow run: **`34806600636`**.

Phase 0 screens all 30 current-top public tapes against exact CR053_REAL, CR052_REAL, CR083 and CR086 on master `9220881`, three fresh seeds and both seats: 720 games total. It is explicitly a mechanical/catastrophe/diversity screen, not a hosted-rating gate. No Kaggle submission is authorized from Phase 0.

Continuation rule: preserve several source-team/macro families, then build a state-coherent Phase-1 population with economically meaningful operators. Do not select one tape solely because it tops the local score.

## Public notebook benchmark — characterization only

Run `34798209070`: three public executable agents each lost 0–32 to CR083. Cross-anchor run `34802342857` also showed severe non-transfer: none was broadly competitive, and each had multiple 0–16 or near-zero edges. These exact public notebook bytes are closed as direct backbones; their mechanisms remain architectural evidence.

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
