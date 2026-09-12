# ROADMAP — Kculture live plan

Updated: 2026-09-11 local / 2026-09-12 UTC boundary

Objective: maximize probability of a prize-winning / top-10 Kaggriculture finish. Working source of truth is branch `fix/kaggle-parity-v1`, together with `STATUS.md` and current frozen experiment protocols.

## Invariants

1. Hosted/live evidence and exact-reference W/L both matter; neither replaces the other.
2. Five daily submissions are a cap, not a quota. Do not retire an active slot for an unqualified candidate.
3. Every candidate family gets a predeclared gate before valid validation results are observed.
4. Failed validation data may diagnose failure but may not be used to retune the same candidate until it passes.
5. No seed, team identity, episode ID, future state or opponent-private state as an agent feature.
6. Authenticated official Kaggle API is the default current-meta source.
7. Original final holdout remains sealed.
8. A mechanically or semantically invalid evaluation is quarantined; its result is not strategy evidence.

## Completed / closed

- CR071M hosted as submission `56124705`; incumbent/calibration reference.
- CR078 late mirror breaker: closed.
- CR079 simple SpaTaro nearest-neighbor clone: closed after OOT generalization failure.
- CR080 Mengfei daily-route bridge: closed after independent confirmation run `34655496708` failed direct/guardrail gates.
- CR080 post-failure diagnostic `34668446703`: complete. Mechanical replay execution was intact; economic state aliasing under daily nearest-route stitching separated losses from wins. Replay-route stitching architecture closed.

## Current frontier

Authenticated run `34668645531`: Majkel 3181.9, ymg_aq 3075.1, UMG 3056.5, Artem 3029.3, SpaTaro 3029.0.

UMG is the bridge target because it is current-top-tier and structurally related to a hosted family already beating CR071M.

## CR081 Gate A — COMPLETE / PASS

Deep corpus run `34669006417`: UMG 111 downloaded episodes, 110 usable after excluding one ambiguous self-play; chronological split 82 development / 28 newest holdout. Majkel newest64 and ymg_aq newest64 collected in parallel.

Correct runtime-aligned Gate A:

- farmer median similarity 0.90104 >= 0.80;
- hands median similarity 0.73958 >= 0.60;
- dev-only modal market -> holdout fidelity 0.94959 >= 0.65.

The fixed stable prefix remains runtime steps 0..287 because development market support is ~0.970 / 0.942 / 0.914 over the first three 96-step blocks and falls to ~0.683 in the next.

## Replay-index gate

Kaggle replay action index `s` corresponds to runtime step `s-1`. This was caught before any valid CR081 H2H result was accepted.

- Run `34671122716` used the wrong translation and delayed the CR071M physical route. **INVALID / SUPERSEDED; ignore results.**
- Correct translation: keep CR071M physical route same-step; map UMG replay actions 1..288 onto runtime market steps 0..287.
- Invalid run seed master 9120811 is burned and included in the corrected seed firewall.

## CURRENT — corrected CR081 confirmation

Run **`34671446692`**, master seed **9120812**.

Single candidate architecture:

- unchanged same-step CR071M physical/runtime backbone;
- runtime steps 0..287 use UMG development-only modal market queue;
- CR071M safety/repair retained;
- same-turn BUY_PRODUCT can supply a later SELL inside the prefix, needed for observed UMG market semantics;
- no replay stitching or hidden/identity features.

Frozen 7-H2H panel:

1. CR081 vs CR071M;
2. CR081 vs CR053;
3. CR081 vs CR061;
4. CR081 vs CR065;
5. CR071M vs CR053;
6. CR071M vs CR061;
7. CR071M vs CR065.

Each: 32 fresh seeds x two seats = 64 games.

Promotion requires all:

- direct CR081 vs CR071M >=0.5625;
- aggregate guardrail delta >=0;
- each guardrail delta >= -0.0625;
- zero errors/non-DONE;
- complete exact panel.

## Conditional next path

### If corrected CR081 passes

1. freeze exact tested package hash;
2. account for which active hosted slot to retire;
3. submit exactly one hosted CR081 probe;
4. collect its episodes through authenticated API;
5. compare live W/L/rating trajectory against incumbents without overreacting to tiny samples.

### If corrected CR081 fails

Close CR081 bridge with no threshold/boundary/quantity retuning on validation data. Start the already-motivated **state-adaptive macro-economic policy** using current top-3 corpora. The key prior is that market behavior is highly structured across current leaders while physical routes differ; model economic macros as functions of legal current state instead of copying another tape.

## Stop / escalation criteria

- Never reopen PRESALE1 microvariants, CR078, CR079 simple 1-NN, CR080 route stitching, or invalid CR081-v1 without genuinely new evidence invalidating the closure reason.
- A current-frontier candidate that cannot generalize chronologically or survive fresh paired seeds is closed even if its source agent has a high Kaggle rating.
- If corrected CR081 fails, do not create CR081A/B/C. Change representation to state-adaptive macro economics.
- If a candidate passes a frozen fresh gate with material uplift, do not keep it local indefinitely for optional tests; move to one controlled hosted probe.
