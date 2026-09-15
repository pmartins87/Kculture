# STATUS — Kculture live source of truth

Updated: 2026-09-15

Authoritative branch: `fix/kaggle-parity-v1`.

## Mission

Win / maximize probability of a prize-winning top-10 Kaggriculture finish. Hosted leaderboard strength is the primary outcome. Local H2H is a mechanics/catastrophe/causal tool and must not be treated as a single-opponent proxy for population skill.

## Binding integration doctrine — cumulative competitive knowledge

**Innovation is additive, not a reset.** The project must not discard knowledge obtained from prior opponent analysis, replay mining, route reconstruction, copied/derived baselines, hosted experiments, failed hypotheses, top-player macro studies or population testing merely because a new first-principles track exists.

Binding rules:

- anything already shown to work remains an admissible baseline, prior, module, architecture clue or adaptation signal until stronger evidence supersedes it;
- public competitor/replay evidence may inform policy construction when legal under competition rules; there is no purity requirement that a winning agent be novel for novelty's sake;
- failed representations remain closed where documented, but the mechanics and lessons learned from them remain research inputs;
- FP001 contributes new causal/economic primitives to the existing competitive stack; it does **not** replace CR053/CR086/CR087/CR088 knowledge;
- the final promotion criterion is expected hosted/population performance and prize probability, not originality;
- integrations must preserve legality: no identity, rating, EpisodeId, hidden seed, future state or opponent-private runtime features.

The target architecture is therefore allowed to combine a proven/elite-informed macro backbone, mechanics-derived production primitives, state-adaptive market logic and opponent/population knowledge whenever the combined policy wins stronger tests.

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
6. CR083 `56199767`: latest authenticated list ~1619.9
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
- later authenticated checkpoint around CR088 work: ~`1612.6`, below CR083 ~`1619.9`; this confirms that a strong local causal edge can fail to improve hosted population rating.

## Hosted-calibrated exact-byte league — COMPLETED / LOCAL ORDER NOT HOSTED-CALIBRATED

Run `34802917553`, master `9190861`, 24 games per edge, zero errors:

- CR083 vs CR053_REAL: **20–4**, score `0.8333`, mean +9833.6;
- CR086 vs CR053_REAL: **20–4**, score `0.8333`, mean +9765.2;
- CR083 vs CR052_REAL: **24–0**;
- CR086 vs CR052_REAL: **24–0**;
- CR053_REAL vs CR052_REAL: **14–10**, score `0.5833`, despite negative mean margin.

This local graph reverses the known hosted hierarchy: CR053_REAL (~2064.8) remains materially above CR083 (~1619.9) on Kaggle. Exact bytes fixed the identity error but did not make local single-seed-distribution H2H a hosted population predictor. The league remains useful for mechanics, catastrophe and diversity; its numeric ordering may not directly promote hosted candidates.

## CR087 — current top-lineage and macro mining — COMPLETE

Corrected discovery run `34803148700` resolved the active submissions of all current top-10 teams and preserved 30 public 719-action tapes, three per team.

Key result: all 30 exact tapes are unique; median cross-pool Hamming distance is 719/719, mean 702.8. Even within the same active submission, hundreds of physical and market actions change between episodes. No step reaches 50% modal agreement across the pool. A modal/medoid tape is therefore not a faithful reconstruction of the current elite.

Macroeconomic profile run `34803658746` parsed 26 replays and shows repeated high-level production families despite action-level variability. Full result: `docs/strategy/CR087_TOP_MACRO_PROFILE_RESULT_2026-09-14.md`. Descriptive families to preserve in population work are:

- Majkel / DSM / Orbital: roughly 9–10 WHEAT + 6 MELON with ~2 COW + 3 SHEEP early;
- Mengfei / feel the agi / redblackbst: roughly 7 WHEAT + 12 MELON with ~2 COW + 2 SHEEP early;
- ymg_aq / Howard: WHEAT-heavier, lower MELON, later STRAWBERRY + mixed animals;
- Otter: distinctive GOOSE/TOMATO emphasis;
- SpaTaro: mixed-product market with large late SHEEP capacity.

Cross-family elite convergence worth preserving: early MELON/STRAWBERRY, later WHEAT/CARROT/TOMATO plus animal support, usually three lands in the first half, productive animals deep into the season and highly state-adaptive market queues.

CR087 CR053-real + latent-supply screen `34803266002` was mechanically safe but economically neutral: 8–8 direct against CR053, and candidate/base were identical at 10–6 against CR052 with the same mean margin. It is **not submitted** absent demonstrated causal impact.

## CR088 — automatic population search — HOSTED SENSOR VERDICT COMPLETE

Phase 0 run `34806600636`: 720/720 games, 30/30 current-top tape packages mechanically valid. Phase 1 corrected run `34808258927`: 42/42 policies valid and 26 overlays passed the frozen local non-regression filter. Full selection evidence remains in `docs/strategy/CR088_PHASE1_RESULT_AND_HOSTED_SENSOR_SELECTION_2026-09-14.md`.

Corrected submission workflow `34858890714` sent the two exact frozen packages once:

- **CR088A** submission `56233701`, Orbital base, SHA `24e78d657d6c16371fcc7393fbea4d23ce695fd456e722e37f5398f7866ab16e`;
- **CR088B** submission `56233703`, feel + `risk8_p125`, SHA `055fbbcd09dc3112bef3ef7a78965ed09f28ec999283dab87641e60d5cf9d053`.

Authenticated checkpoint run `34910849970`:

- CR088A COMPLETE, **1252.8**, 59 listed episodes; newest 32: **11W–21L**, mean margin −12,062.47, median −7,565.5;
- CR088B COMPLETE, **1182.3**, 54 listed episodes; newest 32: **16W–16L**, mean margin +5,244.78, median −622;
- zero replay/non-DONE failures in both downloaded windows.

Verdict: both exact tape backbones are hosted regressions far below CR053 2064.8 and the ~3000 target class. Close CR088A/B as direct candidates and do not retune/resubmit their tape/cap/floor families. Preserve CR088B's legal market operator plus the replay/macro corpus as integration inputs. Full result: `docs/strategy/CR088_HOSTED_SENSOR_RESULT_2026-09-15.md`.

## FP001 — additive first-principles production/economics track

FP001 remains a module-discovery laboratory, not a replacement for cumulative competitive knowledge.

Proven primitives retained: H1 town-pulse carry, H1B owned-sale deferral, H9 public-shop demand, B3 DAILY CARE, H10 compact routing/batched harvest and H11 fertilizer conversion.

B4 run `34848633407` located the animal-only action frontier: COW5_DAILY mean +39,447.5, but only +1,497.75 and 4–4 over COW4_DAILY; COW6_DAILY lost −4,174.75 and 0–8 to COW5_DAILY despite full survival.

### E1–E2 — labor mechanism resolved

E1 residual-idle main-farmer STRAWBERRY is closed: it could not execute the crop without displacing higher-value work. E2/E2B initially showed implausible default-environment swings. E2C run `34866389261` traced them to official-engine RNG coupling: crop occupancy changes weed RNG consumption before random shop selection, so identical nominal seeds need not realize identical towns.

E2D run `34866890716` removed stochastic shop unlocks without changing policy bytes and proved one dedicated hand additive: full-module gains **+907 to +919**, all 8/8, with exact animal invariants and 8 STRAWBERRY output.

### E3 — one-hand crop density PASS

Run `34868854114` selected exact **M6S1**: 6 MELON + 1 STRAWBERRY. In the deterministic-town causal environment it added **+9,533** over COW5_DAILY, produced 36 MELON + 8 STRAWBERRY and preserved the full COW5 fingerprint. The density ladder is closed.

### E4 — default-environment robustness STRONG PASS

Run `34869392514`, 40 fresh seeds × both seats:

- mean M6S1 improvement **+9,594.5**;
- median **+8,643**;
- CI95 **[+6,057.83, +13,131.17]**;
- signs **33–7**; p10 gap **+7,970.6**;
- 80/80 full survival, exact animal fingerprint and full crop output; zero failures.

M6S1 is therefore a robust additive physical/economic module. It is not yet a hosted candidate.

## Current integration decision

**E5 elite-informed mixed-animal transfer is active on `research/first-principles-economy-v1`, corrected run `34922557868`.** Run `34922078827` is infrastructure-only because it lacked the pre-result exact COW5/E4 trajectory-parity gate. The frozen gate compares COW5+M6S1 with 3-COW/2-SHEEP+M6S1 and 2-COW/3-SHEEP+M6S1, plus own no-crop controls, over 32 fresh default-environment seeds and both seats.

A mixed policy becomes primary only by passing full mechanics/crop transfer and beating COW5+M6S1 under the frozen rule. Otherwise at most one bounded non-inferior mixed architecture is retained as a secondary challenger.

After E5, the survivor set enters heterogeneous population testing against exact hosted anchors and multiple CR088/current-top macro representatives. Only then do separable CR086/CR088/H1/H1B market factors and H9 adaptive expansion enter. No new Kaggle submission is authorized now.

## Public notebook benchmark — characterization only

Run `34798209070`: three public executable agents each lost 0–32 to CR083. Cross-anchor run `34802342857` also showed severe non-transfer: none was broadly competitive, and each had multiple 0–16 or near-zero edges. These exact public notebook bytes are closed as direct backbones; their mechanisms remain architectural evidence.

## Closed / quarantined classes

CR078, CR079, CR080 replay stitching, CR081 static market-prefix transplant, CR082 1-NN teacher imitation, CR084 FEED rescue, CR085 Pareto gating: closed / do not retune spent hypotheses.

Direct adoption of the three screened public notebook packages is closed; their ideas remain research evidence.

## Binding operating policy

- Hosted leaderboard/prize objective governs architecture choices.
- Competitive knowledge is cumulative; new tracks must integrate, not erase, proven prior evidence.
- Local tests must use exact hosted bytes when claiming calibration against a hosted agent.
- Use a heterogeneous hosted-calibrated league, never one incumbent alone.
- Authenticated Kaggle API first for current meta/submission evidence.
- Exact H2H uses `kaggle-environments==1.32.7`, isolated packages, both seats.
- No identity/EpisodeId/rating/hidden seed/future/opponent-private runtime features.
- Original final holdout remains sealed.
- No repeated polling loops.
- Distinct mechanically valid architectures may receive hosted probes earlier; local rigor must prevent broken submissions, not prevent learning from the actual population.
