# ROADMAP — Kculture live plan

Updated: 2026-09-14

Objective: maximize probability of a prize-winning / top-10 Kaggriculture finish. The target class is ~3000+ hosted rating.

## Binding principles

1. Hosted leaderboard strength is the primary outcome.
2. Local H2H is for mechanics, catastrophe filtering, causal comparison and **hosted-calibrated league** evidence — never a single-incumbent surrogate for population skill.
3. A local anchor may represent a hosted agent only if its exact submitted bytes/hash are proven.
4. Authenticated Kaggle API is the default current-meta source.
5. Use both seats and `kaggle-environments==1.32.7` for exact local H2H.
6. No identity, team, rating, EpisodeId, hidden seed, future state or opponent-private runtime features.
7. Original final holdout remains sealed.
8. Do not retune closed hypotheses on spent validation evidence.
9. Do not enter polling loops.
10. Distinct mechanically valid candidates may be probed hosted earlier; submission slots are experimental sensors as well as final promotion slots.

## Critical reset — exact hosted incumbent

Best known historical project agent is **CR053 submission `56073870`**, score checkpoint **2064.8**, exact SHA:
`095080e791bd8d58369893c1a421beb57b7f64c2808c011f576e09684ffb9a15`.

The later `CR053_CONTROL` anchor SHA `a9fea449...bd4c` is a different file and is quarantined as a proxy for hosted CR053.

The exact CR053/CR052 candidate artifact is preserved in run `34105008373`, artifact `10012004237`.

## Track A — hosted-calibrated league

Workflow: `.github/workflows/hosted-calibrated-league-v1.yml`, commit `a42b4589e568e3203ede7dad653e1c000f22b710`.

Initial exact cohort:
- CR053_REAL — 2064.8 hosted
- CR052_REAL — ~1700–1750 hosted
- CR083 — ~1619.8 latest authenticated
- CR086 — active hosted probe

Run `34802917553` completed with zero errors, but the local order is not hosted-calibrated: CR083 and CR086 each beat CR053_REAL 20–4 locally although CR053 remains substantially stronger on Kaggle. CR053_REAL beat CR052_REAL 14–10.

Decision: do not expand this as if more exact anchors alone will repair transfer. Keep exact packages for mechanics, catastrophe and diversity screens. Hosted probes remain the calibration instrument for population strength.

## Track B — CR086 latent-supply hosted probe

CR086 SHA `11296a4e658f37c109a2cc953be0ea7db8e2fbde6286ac483e0466f52f4af888`.
Gate A vs CR083: 26W–6L = 0.8125, mean +260.5625, symmetric seats, zero errors.
Hosted submission `56220184`, description `CR086_LATENT_SUPPLY_11296A4E`.

One-shot run `34802927151` saw COMPLETE at initial rating `600.0` with one episode only. This is not a verdict. Do not repeatedly poll; a later deliberately scheduled checkpoint may be used after meaningful episode accumulation.

## Track C — CR087 current-top lineage mining

Goal: reconstruct the current ~3000-class open-loop backbone directly from active top-team public submissions/replays, not notebook titles.

Evidence from current community/meta:
- elite remains predominantly heuristics/fixed-policy lineages;
- new ~720-action lineages reportedly propagate through the top every few days;
- strongest design hypothesis is a strong static production backbone plus selective market adaptation.

Discovery tool: `tools/cr087_current_top_lineage_miner.py`.
It resolves current top-team active submissions, samples public episodes, and preserves:
- every coherent 719-action tape;
- tape hashes and source metadata;
- pairwise Hamming matrix statistics;
- medoid coherent route;
- per-step modal consensus and agreement.

Corrected run `34803148700` completed: 30/30 tapes recovered, all exact tapes unique, mean pairwise Hamming 702.8/719 and no majority action at any step. Current elite submissions are materially state-adaptive; modal or medoid tape cloning is not the target architecture.

Macro run `34803658746` recovered repeated production-level families from 26 replays (`docs/strategy/CR087_TOP_MACRO_PROFILE_RESULT_2026-09-14.md`). Preserve at least the five descriptive families recorded in `STATUS.md`; action-level diversity is real, while macro convergence is the useful signal.

## Track D — CR087 CR053-real + latent-supply overlay

Builder: `tools/cr087_build_cr053_latent_supply.py`.
Screen workflow: `.github/workflows/cr087-cr053-latent-supply-screen-v1.yml`.

Candidate preserves the exact hosted CR053 719-action route and market multiset, changing only ordering of existing premium SELLs using the CR086 cash-at-risk layer.

Run `34803266002` was mechanically safe but demonstrated no result change against CR052: candidate and base were both 10–6 with identical mean margin; direct candidate vs base was 8–8. Do **not** spend a hosted slot on CR087 absent a demonstrated intervention. Retain the generic latent-supply operator for population experiments.

## CR088 automatic policy search — PHASE 1 ACTIVE

Phase 0 run `34806600636` completed: 30/30 current-top tape seeds were mechanically valid across 720 fresh exact games. Seven diverse bases were retained rather than a single local winner: Majkel, Orbital, feel the agi, redblackbst, ymg_aq, Otter and SpaTaro.

Phase-1 protocol: `docs/strategy/CR088_PHASE1_PROTOCOL_2026-09-14.md`.
Run: **`34807533884`**.

The frozen Phase-1 factorial has 42 members: each complete base plus latent-supply ordering and four bounded risk-sale variants (caps 8/16; price floors 1.00x/1.25x). Physical actions remain coherent and unchanged. Every variant receives a direct edge against its own base and the four-anchor safety panel on fresh master `9230881`.

After Phase 1:

1. close any failed operator class without cap/floor retuning;
2. retain materially different, mechanically valid representatives in hosted-rank/macro-family order, not local-score order;
3. perform current authenticated slot accounting;
4. send only high-information hosted sensors; do not spend a slot on the neutral CR087 overlay;
5. use hosted transfer to update the population objective;
6. advance production-capacity operators only as linked, execution-coherent bundles.

Stop rules: no CR088A/B manual patch ladder; no raw local-champion promotion; no revival of CR080/081/082 representations.

## Closed hypotheses

CR078, CR079, CR080 replay stitching, CR081 market-prefix transplant, CR082 1-NN teacher imitation, CR084 FEED rescue, CR085 Pareto gating: closed / do not retune.

Direct adoption of the three previously screened public notebook packages is closed; their mechanisms remain research inputs.

## Current frontier

Fresh frozen top-10 snapshot from 2026-09-14 starts at Majkel1337 `3191.4`; rank 10 redblackbst `2958.4`. Our task is to discover/construct a policy in that class, not optimize the ~1600 CR083 lineage indefinitely.
