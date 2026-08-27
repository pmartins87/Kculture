# HANDOFF — Kculture

Use this file as the **first read in any new Kculture chat**.

## Mission

Compete seriously for a **top-10 Kaggriculture prize**. Final submission deadline: 2026-09-30 23:59 UTC. `pmartins87/Kculture` is the source of truth and intentionally public.

The objective is **prize probability, not elegance**. A user suggestion, assistant suggestion, public notebook, solver idea or attractive architecture is only a hypothesis until evidence supports it.

## Mandatory first reads

1. `STATUS.md`
2. `docs/PRIZE_FIRST_DECISION_POLICY.md`
3. `ROADMAP.md`
4. `docs/SUBMISSION_LEDGER.md`
5. `experiments/KEXP-20260826-018-live-meta-radar/README.md`
6. `experiments/KEXP-20260826-019-live-meta-longitudinal/README.md`
7. `research/LATE_ANIMAL_TERMINAL_VALUE_20260826.md`
8. `experiments/KEXP-20260826-022-live-meta-demand-longitudinal/README.md`
9. `experiments/KEXP-20260827-023-late-crop-cycle-audit/README.md`
10. `experiments/KEXP-20260827-024-terminal-care-reallocation/README.md`
11. `experiments/KEXP-20260826-017-r4d-macro-oracle/README.md`
12. `official/UPSTREAM_LOCK.md`

Then inspect latest commits and GitHub Actions **before changing code**.

## Working rules

- Official engine facts outrank assumptions.
- **Ideas are hypotheses, not directives.** Do not pivot because the user or assistant casually mentions a technique.
- Optimize expected top-10 probability, not elegance, novelty or similarity to other projects.
- Cheap falsification before expensive implementation.
- W/L/T is primary; money delta is secondary.
- Local public benchmarks are regression controls; official hosted/live-ladder evidence is calibration truth when they conflict.
- Official daily high-Elo Episode datasets are now a first-class meta source, including private-agent behavior.
- Replay/team/seed identity may be used for research labels only, never as deployable policy features.
- Preserve exact public-agent source/version/path/hash/license provenance.
- Fresh-load file agents per episode.
- Development is for iteration. Changed code gets a fresh validation gate only after exact freeze.
- Never inherit R4B validation onto changed code.
- Never promote from replay correlation alone; replay mining generates hypotheses, controlled games test them.
- Never spend a hosted submission merely because a local metric looks prettier.
- Keep credentials/private competitor code out of the repo.
- Advance autonomously; surface only material blockers/results.

## Hosted champion / current problem

`R4B-market-only-validated-v1`

- candidate `candidates/r4b_ablation_market_only.py`;
- Git blob `e564125f0c4a1711fd3ea065dc1cb27d4a62ce37`;
- validation run `32918640409`;
- package parity run `32919305800`, 4/4 complete trajectories identical;
- archive SHA-256 `19cc08d2b3bcb8f8f947806c0ee01f4d7643d36f0c15abe0a978129ed1c53117`;
- Kaggle status `Complete` / green check;
- visible hosted rating progression **161.6 → 135.7**.

Local controlled modern panel is 81-15/96, so hosted/local calibration is badly inconsistent. Treat the hosted weakness as real. Keep R4B immutable until a replacement earns promotion.

## Controlled public regression panel

R4B on all 16 development seeds × both seats:

- Kaito V27 V4: 25-7, mean +4,396.84375;
- Rayk V11: 30-2, mean +7,477.21875;
- Andrew V12: 26-6, mean +5,287.43750;
- combined **81-15 / 96**, score 0.84375.

Do **not** treat this as a calibrated model of the current hosted ladder.

## Closed route/solver avenue

- KEXP-015: default→10C4S stays 81-15; default→6C8S regresses to 78-18.
- KEXP-017 run `32972566807`: perfect ex-post selector among baseline/10C4S/6C8S improves only 81-15→83-13.

Therefore solver/search over the current route library is **deprioritized**. It remains available only for bounded subproblems with demonstrated headroom.

## Live-meta intelligence — now primary research source

Official datasets:

- `kaggle/kaggriculture-episodes-index`;
- `kaggle/kaggriculture-episodes-YYYY-MM-DD`.

They are accessible anonymously through `kagglehub` and expose actual current high-Elo replays, including private agents.

`tools/live_meta_radar.py` now profiles checkpoints 600/648/672/696/708/717/719 and late windows 600-671, 672-695, 696-718. Workflow `live-meta-radar` is scheduled **twice daily** at 00:17 and 12:17 UTC.

Latest top-20 run `33036951875`, official date 2026-08-26:

- 687 daily episodes;
- median avg score 2752.948115;
- top avg score 3075.180535;
- selected top20 3075.180535→3057.712986;
- artifact `9632352609`, ZIP SHA `a0dc50e382ede83378b3c3c73c8b1479ec31d2101b484f339b5818d7d2a5dafd`.

Important Aug-26 top-winner means:

- reward 112,307.2;
- herd 16.25 at step672 → 12.05 terminal: drop **4.2**;
- losers drop only **1.95**;
- 672-695: CARE0.6, FEED5.4, HARVEST21.25, DROP3.9, SELL86.2;
- 696-718: CARE0.5, FEED0, HARVEST21.35, DROP14.1, SELL158.25.

### Top-policy fingerprint

Run `33019862336` — SUCCESS.

The dominant high-Elo families are not fixed tapes:

- all sampled complete trajectories unique;
- exact action agreement in steps216-599 only ~1.36% Crop Dusta and ~0.88% Ryo Hasegawa;
- per-step modal exact action only ~7%.

This is a major architecture warning: COK/R4B's early route commitment is likely an important source of hosted weakness.

## Mechanism A — late animal stop-investment

### Frozen theorem

See `research/LATE_ANIMAL_TERMINAL_VALUE_20260826.md`.

- step695 end-of-day is the final animal-production refresh;
- CARE during 672-695 creates pending bonus only after that final production check → zero direct terminal-production value;
- FEED during 672-695 can still prevent escape or gate an existing pending bonus → do not blanket-remove;
- HARVEST on animal takes all current product and resets animal `yield_units` to zero, potentially freeing capacity for final step695 production;
- COK still issues roughly 8–10 CARE actions in 672-695.

### KEXP-019 — COMPLETE / longitudinal support

Run `33019193497`, top10 official episodes Aug23/24/25.

Winner herd reduction vs losers:

- Aug23 2.2 vs1.3;
- Aug24 2.6 vs0.4;
- Aug25 6.7 vs1.1.

Winner CARE in 672-695: 0.1 / 0.0 / 0.0 respectively.

Mechanism survives temporal replication.

### KEXP-024 — RUNNING

Candidate `candidates/r4d_terminal_care_reallocate.py`, blob `daab48a896535cd514e725affef6e8568e6b0a21`.

Only when base action is CARE during 672-695:

1. HARVEST if animal has product;
2. else COLLECT_FERTILIZER if available;
3. else PASS.

Everything else stays R4B.

Run `33037860772`. Development only. Primary gate: zero errors, no family W/L regression, aggregate >81-15, direct vs R4B score>=0.50 and mean>=0. No validation/heldout.

## Mechanism B — live crop demand response

KEXP-021 Aug25 top20: CARROT demand→late carrot seed buy Pearson +0.46156.

KEXP-022 run `33019559986` longitudinal replication:

- Aug22 +0.49505;
- Aug23 +0.52212;
- Aug24 +0.53413;
- Aug25 +0.50326.

Thus strong live agents adapt late crop allocation to the **complete public shop-demand state**. However “more carrot always” is false; winner/loser carrot quantities reverse on some dates. Candidate must use state/economic context, not a fixed quota.

COK gap: after all 8 shops are visible, route tapes still plant roughly 28–32 WHEAT vs 0–3 CARROT in 600-671.

### KEXP-023 — RUNNING

Before blind WHEAT→CARROT substitution, audit physical timing:

- unchanged R4B;
- 16 development + 20 exploratory live-meta environmental seeds;
- every `PLANT WHEAT` in 576-647 paired with next same-tile HARVEST;
- classify CARROT compatibility by delay.

First run `33037518259` failed **before any game** due only to Python direct-script import path. Import fixed without changing protocol. Canonical rerun `33037701080` in progress.

If most intended slots are <=72 turns to harvest, a bounded demand/price-aware substitution is eligible for prototyping. If not, blind substitution is killed and a real lifecycle controller is required.

## Data separation invariant

- development: 16 seeds, open;
- exploratory live-meta environmental seeds: development/diagnostic only;
- validation: candidate-specific formal gates only;
- held-out: **32/32 still sealed**.

## Exact continuation logic

1. Poll KEXP-023 run `33037701080` and KEXP-024 run `33037860772` first.
2. Apply their **predeclared gates exactly**; do not reinterpret after seeing results.
3. If KEXP-024 wins W/L cross-family, broaden it on exploratory live-meta seeds before fresh validation. If money-only, NO PROMOTION.
4. If KEXP-023 says late WHEAT slots are CARROT-compatible, build one conservative demand+market crop candidate; otherwise kill blind crop substitution.
5. Keep the twice-daily live radar operating and continue looking for mechanisms repeated across dates/families.
6. Continue hosted episode forensics when Kculture episode identities become available.
7. Freeze only a materially stronger candidate, then open a **fresh exact validation gate**.
8. Do not send submission #2 before that gate.
9. Keep R4B immutable and held-out **32/32 sealed**.
