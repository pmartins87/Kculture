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

Fresh pair master `9190861`. Goal: determine which local population metrics reproduce known hosted ordering and place CR086 relative to the real strongest historical agent.

Expand with exact hosted CR029/CR011/CR008/CR071M bytes as they are recovered. Candidate-search fitness will eventually use mean league score, lower-tail matchup strength and diversity/robustness rather than one H2H.

## Track B — CR086 latent-supply hosted probe

CR086 SHA `11296a4e658f37c109a2cc953be0ea7db8e2fbde6286ac483e0466f52f4af888`.
Gate A vs CR083: 26W–6L = 0.8125, mean +260.5625, symmetric seats, zero errors.
Hosted submission `56220184`, description `CR086_LATENT_SUPPLY_11296A4E`.

One-shot status workflow exists; do not repeatedly poll. Hosted evidence from CR086 is used to learn transfer from local league to real population.

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

First run `34803046771` failed only on a rankless leaderboard CSV parser. Parser was fixed in commit `666f8f0f3ddce078fc643789a48cd706a69db0ec`; rerun is automatic.

After successful discovery:
1. screen every coherent top tape as a population, not only the medoid;
2. compare against exact hosted-calibrated league;
3. identify current dominant backbone(s);
4. package the strongest coherent route(s);
5. add selective latent-supply / market adaptation only where mechanics justify it;
6. probe hosted early if mechanically valid and not locally catastrophic.

## Track D — CR087 CR053-real + latent-supply overlay

Builder: `tools/cr087_build_cr053_latent_supply.py`.
Screen workflow: `.github/workflows/cr087-cr053-latent-supply-screen-v1.yml`.

Candidate preserves the exact hosted CR053 719-action route and market multiset, changing only ordering of existing premium SELLs using the CR086 cash-at-risk layer.

Fast safety screen:
- deterministic build from exact CR053 SHA;
- direct candidate vs exact CR053 real;
- same-seed candidate/base comparison vs exact CR052 real;
- if zero errors and candidate is not below 0.5 direct, it is eligible for an early hosted probe rather than a long legacy gate chain.

## Automatic policy search — next layer

Do not manually create long CR087/CR088/CR089 patch chains. Once the current-top tapes and hosted-calibrated league are available, build a deterministic population-search loop over economically meaningful dimensions:
- coherent route/backbone selection from current top lineage;
- premium SELL ordering / tranching;
- latent opponent supply / glut risk;
- shop-cycle timing;
- liquidity reserve / hiring timing;
- animal/crop portfolio switches that preserve execution coherence.

Fitness must be robust across the calibrated league, not optimized against CR083 alone. Top population members then receive hosted probes to calibrate transfer.

## Closed hypotheses

CR078, CR079, CR080 replay stitching, CR081 market-prefix transplant, CR082 1-NN teacher imitation, CR084 FEED rescue, CR085 Pareto gating: closed / do not retune.

Direct adoption of the three previously screened public notebook packages is closed; their mechanisms remain research inputs.

## Current frontier

Fresh frozen top-10 snapshot from 2026-09-14 starts at Majkel1337 `3191.4`; rank 10 redblackbst `2958.4`. Our task is to discover/construct a policy in that class, not optimize the ~1600 CR083 lineage indefinitely.
