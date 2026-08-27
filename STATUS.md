# STATUS — Kculture

Last updated: 2026-08-27

## Mission

**Goal: maximize probability of a top-10 final finish in Kaggriculture; each top-10 position pays US$5,000.**

Repository `pmartins87/Kculture` is the source of truth for strategy, code, experiments, Actions evidence, hashes, roadmap and handoff state.

## Current strategic position

- **R0 COMPLETE** — competition entry/facts frozen.
- **R1 PASS** — exact official starter/environment reproduction.
- **R2 PASS** — deterministic laboratory and partition discipline.
- **R3 DELIVERY PASS / HOSTED CALIBRATION FAIL** — R4B package is valid/Complete, but visible hosted rating deteriorated **161.6 → 135.7 → 110.5**.
- **R4 ACTIVE** — frozen hosted champion remains R4B while R4D builds a materially different state-adaptive replacement.
- **Held-out 32/32 sealed.**
- Validation is also closed for the current R4D line until exploratory replication is complete.

The hosted weakness is treated as real. R4B is now a reproducible baseline, not a likely prize candidate.

## Frozen hosted baseline — R4B

`R4B-market-only-validated-v1`

- candidate: `candidates/r4b_ablation_market_only.py`;
- blob: `e564125f0c4a1711fd3ea065dc1cb27d4a62ce37`;
- controlled modern public panel on development: Kaito 25-7, Rayk 30-2, Andrew 26-6, combined **81-15 / 96**;
- validation run `32918640409`;
- package parity run `32919305800`, 4/4 exact trajectories;
- Kaggle status Complete / green check;
- visible hosted rating: **110.5** latest observed.

Local 81-15 is a regression control only; it is not a calibrated model of the live field.

## Architecture diagnosis

Official recent top-agent replays show highly state-adaptive behavior. Exact action agreement within dominant high-Elo families is very low; COK/R4B remains strongly route/tape oriented. Hosted failure is therefore treated primarily as a strategic/architectural gap, not a rules or packaging problem.

KEXP-042 full-game atlas found major differences in labor/action mix and production composition. R4B generates far more PASS in midgame, but KEXP-044 winner-vs-loser analysis showed lower PASS is **not** itself a winning signal. KEXP-043 found large mechanical PASS headroom, but a generic dispatcher is deprioritized until value evidence supports it.

## Closed / deprioritized avenues

- **KEXP-015 NO PROMOTION:** fixed route replacements do not improve W/L.
- **KEXP-017 COMPLETE / route-oracle DEPRIORITIZED:** perfect ex-post selector among current route variants only moves 81-15 → 83-13.
- **KEXP-024 NO PROMOTION:** terminal CARE reallocation is exactly neutral vs R4B (12-12-8, mean delta 0).
- **KEXP-027 ZERO-CEILING:** no FEED intents at exact final executable step 695.
- **KEXP-030 NO PROMOTION:** only 35/331 late FEED actions lacked terminal value; blanket suppression rejected.
- **KEXP-032 REJECTED:** assumption that WATER after 695 is useless was false; engine gives immediate yield increments in the valid window.
- **KEXP-033 REJECTED:** naive terminal collector increased DROP but went 2-30 vs R4B.
- **KEXP-035 COMPLETE:** 371/374 audited terminal WATER actions create immediate yield; 365 retain a complete harvest/drop path.
- **KEXP-036 NO PROMOTION:** terminal SELL impact ordering did not meet direct edge gate.

## Live-meta calibration and replay correctness

- **KEXP-026 COMPLETE:** corrected state/action alignment gives exact seed ledger; **0/36** episodes contain truly unreserved CARROT seed for a free stock-only substitution.
- **KEXP-028 COMPLETE:** corrected replay convention `state t -> action frame t+1`; **10/10** sampled official top tapes reproduce exact terminal rewards. Fixed tape is not a valid counterfactual opponent benchmark because market changes break the tape.
- **KEXP-039 COMPLETE:** step-717 terminal selling exists in current top-agent behavior; it is supporting evidence only.
- **KEXP-042 COMPLETE:** full-game phase atlas against recent official winners.
- **KEXP-043 COMPLETE:** 10,150 R4B PASS intents in states 96-287; ~66% have some same-tile task and ~90% are within two moves of a task. This is headroom, not proof of value.
- **KEXP-044 COMPLETE:** winners do not systematically reduce PASS versus losers, preventing a premature labor-dispatcher pivot.

## Mechanism A — terminal non-input liquidation

**KEXP-037 passed development and exploratory replication.**

Mechanism: sell already-available non-input products at state 717, after the last town-consumption tick and before the terminal dump.

Development direct vs R4B: **13-11-8**, score 0.53125, positive mean delta; modern public panel preserved.

Exploratory live-meta environmental pool (20 seeds × both seats) direct vs R4B: **12-8-20**, score **0.55**, mean delta **+32.2**, zero errors.

Interpretation: small, replicated, independent component. Keep for later combination; insufficient alone to justify hosted submission.

Candidate: `candidates/r4d_early_terminal_noninput_sell.py`.

## Mechanism B — state-adaptive late crop value

This is the current primary R4D line.

### KEXP-038 — PASS

Mechanics-derived purchase-time rule for equal-route WHEAT/CARROT yield:

`q * (CARROT_price - WHEAT_price) - 10 > 0`

Across development + exploratory live-meta diagnostics, all **234/234** sign-positive purchase states remained positive at plant and harvest-price oracle checkpoints. This established that current public market state carries a stable crop-value signal.

### KEXP-040 — PASS

One-step JIT fallback treating existing WHEAT seed as sunk cost:

`q * (CARROT_price - WHEAT_price) - 20 > 0`

Passed predeclared support/stability gate in both pools.

### KEXP-041 — DEVELOPMENT PASS

Candidate: `candidates/r4d_jit_carrot_one.py`, blob `97e102933f96a85fcc586ec4a96500069902f035`.

Only mutation:

- state 614: if `3*(Pc-Pw)-20 > 0`, buy exactly one CARROT seed;
- state 615: only if extra stock is observed, convert exactly one actual R4B `PLANT WHEAT` to `PLANT CARROT`.

Independent execution audit: mutation triggered in **14/36** episodes (6/16 development, 8/20 exploratory); **14/14** purchases committed and **14/14** produced exactly +1 CARROT / -1 WHEAT; zero false mutations/errors.

Development W/L:

- Kaito 25-7;
- Rayk 30-2;
- Andrew 26-6;
- combined **81-15** — exact baseline preservation;
- direct vs R4B **20-12**, score **0.625**, mean terminal delta **+53.53**, zero errors.

**Decision:** first R4D state-adaptive candidate to pass a material direct W/L gate. Exploratory direct replication on 20 live-meta environmental seeds × both seats is currently running as run `33045892841`.

### KEXP-045 — RUNNING

Candidate: `candidates/r4d_jit_carrot_two.py`, blob `9d199b3c263254805c64f122367afe180027afeb`.

Extends KEXP-041 to two bounded safe pairs: 614→615 and 619→620, each with q=3 and the same legal JIT value rule. Development screen run `33046361583` is in progress.

Predeclared direct gate: score >=0.5625, positive mean delta, zero errors, modern public panel preserved.

## Current exact continuation

1. Poll KEXP-041 exploratory run `33045892841`.
2. Poll KEXP-045 development run `33046361583`.
3. If KEXP-041 replicates with score >0.50 and positive mean delta, it becomes eligible for an exact fresh validation after deciding whether KEXP-045 is stronger.
4. If KEXP-045 passes and is at least as convincing as KEXP-041, replicate KEXP-045 on exploratory live-meta environmental seeds before validation.
5. Combine KEXP-037 only after selecting the stronger crop controller; test combination directly versus its crop-only parent.
6. Open fresh validation only for the frozen candidate selected by those gates.
7. Keep all 32 held-out sealed.
8. Prepare a new hosted submission only after fresh validation and exact package parity. Hosted submission should be used as calibration of a materially different policy, not as a reaction to the 110.5 score.

## Frozen environment facts

- `kaggle-environments==1.32.7`;
- official engine commit `28b6d8af3ce73926b3d0fda1410c1ddd8384ab8c`;
- 720 recorded states; state 718 is final executable action;
- terminal reward is farm money;
- replay alignment: action chosen at state `t` is stored on frame `t+1`;
- W/L/T drives ladder/final tournament relevance; terminal money margin is secondary.

## Data discipline

- development: 16 frozen seeds — open;
- exploratory live-meta environmental seeds: development/calibration only;
- validation: closed until candidate freeze;
- held-out: **32/32 sealed**;
- team/episode/seed identity forbidden as deployable policy input.
