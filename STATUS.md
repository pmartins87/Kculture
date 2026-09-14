# STATUS — Kculture live source of truth

Updated: 2026-09-14

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

## CR088 — automatic population search — PHASE 1 COMPLETE

### Phase 0 — COMPLETE

Run `34806600636`: 720/720 games, 30/30 mechanically valid packages, zero engine failures. Highest local safety seeds were feel the agi `0.4583`, Orbital `0.4167` and Majkel `0.3333`; local scores are not hosted promotion scores.

Seven diverse bases were retained: Majkel, Orbital, feel the agi, redblackbst, ymg_aq, Otter and SpaTaro. This preserves hosted-rank priority, the five descriptive macro families and the distinct redblack four-land path.

### Phase 1 — COMPLETE after infrastructure correction

Frozen protocol: `docs/strategy/CR088_PHASE1_PROTOCOL_2026-09-14.md`.

Initial run `34807533884` is **not economic evidence** for modified overlays: the generated module exposed an internal `_cr088_risk_sale(...)` helper as the Kaggle loader entrypoint, so modified packages failed before valid play.

The branch then fixed only entrypoint/package selection and added official-loader smoke without changing the policy family. Corrected run **`34808258927`** completed with:

- **42/42 mechanically valid policies**;
- zero engine failures/non-DONE;
- **26 overlays** passing the frozen Phase-1 non-regression filter;
- original final holdout still sealed;
- no automatic Kaggle submission inside the gate.

Result/selection document: `docs/strategy/CR088_PHASE1_RESULT_AND_HOSTED_SENSOR_SELECTION_2026-09-14.md`.

Two high-information frozen hosted sensors were selected:

1. **CR088A — Orbital coherent base**
   - variant `r06_e108754069_s56205640__base`
   - SHA-256 `24e78d657d6c16371fcc7393fbea4d23ce695fd456e722e37f5398f7866ab16e`
   - description `CR088A_ORBITAL_BASE_24E78D65`.
2. **CR088B — feel the agi + bounded risk-sale**
   - variant `r07_e108766657_s56132899__risk8_p125`
   - legal latent SELL ordering + max-one premium sale, cap 8, price floor 1.25x; physical policy unchanged
   - SHA-256 `055fbbcd09dc3112bef3ef7a78965ed09f28ec999283dab87641e60d5cf9d053`
   - description `CR088B_FEEL_R8P125_055FBBCD`.

### Hosted sensor submission pipeline — PRE-SUBMISSION INFRA FIXED

First submission workflow run `34809554553` rebuilt both exact expected hashes but failed **before** loader smoke, quota check or Kaggle submission because the workflow incorrectly required `tar -tzf` output to equal exactly `main.py`; the archives validly also contain provenance. No candidate was submitted by that failed run and it consumed no Kaggle submission slot.

Infrastructure-only fix commit **`761a83b063b11385570ba923e28840d93286e54f`** changes the preflight to assert that `main.py` is present rather than the only member. Candidate bytes, expected SHA-256s, descriptions and quota/duplicate gates are unchanged.

Do not manually patch/rebuild these candidates. The corrected workflow is the only authorized path for these two frozen sensors.

## FP001 — additive first-principles production/economics track

FP001 is now formally an **additive module-discovery track**, not an alternative history of the project. Its job is to discover causal mechanisms that can strengthen elite-informed/population-tested architectures.

Strong results already established:

- B3 CARE is first-order: COW3 DAILY mean +27,308.5 vs +13,101.4 NONE, +14,207.1 paired mean, 16/16 wins;
- H10 compact scheduling + batched milk harvest is positive; batching alone +861.5 paired mean while preserving output;
- H11 exact engine audit shows selling all fertilizer is not generally optimal: for STRAWBERRY, two well-timed fertilizer applications add four berries and about +268 nominal value versus selling those fertilizer units at normal prices; TOMATO also has positive regions;
- B4 scale × CARE run **`34848633407`** found a real single-farmer action-capacity frontier.

### B4 current animal-only frontier

Mean final-bank delta over starting cash, 8 paired fresh seed/seat cases:

- COW4_DAILY **+37,949.75**;
- COW5_SURVIVAL **+36,685.25**;
- **COW5_DAILY +39,447.50** — current mean champion, median 41,050.5, min 28,920, max 46,769;
- COW6_DAILY +35,272.75;
- COW6_SURVIVAL +33,054.25.

Important nuance:

- 5 DAILY vs 4 DAILY is only +1,497.75 mean and **4–4 paired**, so COW5_DAILY is mean-best but not robustly dominant;
- 5 DAILY vs 5 SURVIVAL is +2,762.25 mean but 6–2, including one negative pair;
- 6 SURVIVAL vs 5 SURVIVAL is **−3,631 mean, 0–8**;
- 6 DAILY vs 5 DAILY is **−4,174.75 mean, 0–8**.

All animals survived, so the six-cow collapse is an **action/opportunity-cost saturation effect**, not mortality. This makes COW4_DAILY, COW5_SURVIVAL and COW5_DAILY three useful controls for the next hybrid rather than declaring five DAILY a universal optimum.

## Current integration decision

Do **not** build a pure COW5 agent and call the search complete. CR087 elite evidence and FP001 independently point toward mixed production: premium crops + durable animal economy + adaptive market handling.

Next integrated gate must compare elite-informed mixed/hybrid production programs against the best animal-only controls. Priority treatments:

- COW4_DAILY + fertilized STRAWBERRY;
- COW5_SURVIVAL + fertilized STRAWBERRY;
- COW5_DAILY + STRAWBERRY as an action-starvation control;
- labor ablation only where crop work creates measurable marginal value;
- elite-informed mixed-animal priors (not blind tape copying) such as the observed COW/SHEEP families;
- later H9 public-shop-conditioned expansion and CR088 legal market overlays.

The candidate that advances must first show causal economic/logistics value, then survive heterogeneous population testing and hosted calibration. Originality alone never promotes it.

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
