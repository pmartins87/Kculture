# STATUS — Kculture live source of truth

Updated: 2026-09-13

Authoritative branch: `fix/kaggle-parity-v1`.

## Mission

Maximize probability of a prize-winning / top-10 Kaggriculture finish before 2026-09-30 23:59 UTC. No hosted submission without a passed frozen promotion gate.

## Hosted live state

### CR083 — ACTIVE / IMMUTABLE / STILL CONVERGING

- submission: **`56199767`**
- file: `CR083.tar.gz`
- frozen SHA-256: **`648fbcdb370f7e48fafda18a1112c5f1b57a17a81b7191f010fe4058f41a41b8`**
- submitted: `2026-09-13 05:21:53 UTC`
- latest authenticated checkpoint already frozen in this work session: **1660.3**
- mature CR071M control `56124705` at the same checkpoint: **1638.8**
- current observed gap at that checkpoint: **CR083 +21.5**
- episode listing contained 77 completed rows including the validation episode, i.e. about **76 public completed episodes**.

CR083 has crossed CR071M on the live rating, which is encouraging, but the predeclared maturity rule remains binding: no final hosted verdict before 100 completed public episodes. Do not repeatedly poll; make one checkpoint only when the maturity condition is actually reached or when another material decision requires it.

Important: Kaggle simulation ratings converge through repeated episodes. Money margin does not directly determine the live rating; W/L/T does.

Frozen hosted checkpoint and maturity rule: `docs/strategy/CR083_HOSTED_PROBE_CHECKPOINT_2026-09-13.md`.

### Earlier 36-replay hosted forensic freeze

Read-only forensic run `34745898829`, artifact `10314660085`:

- **27W–9L–0T = 75.0% raw win rate**;
- mean money margin `+14,703.1`, median `+6,385`;
- seat 0: 14W–4L; seat 1: 13W–5L;
- 36/36 opponents matched exactly to the then-current full leaderboard snapshot.

The earlier warning was 0–4 versus sampled opponents rated >=2300. That observation motivated better population-strength validation, not CR083 retuning.

### Frozen maturity decision

Project heuristic, not an official Kaggle rule:

- **do not close CR083 before 100 completed public episodes**;
- at 100+, make one new frozen checkpoint of rating, rating trend, overall W/L/T and opponent-strength bands;
- no CR083A/B/C, no `step 434` retuning, no crop exception, no clamp-formula tuning from hosted outcomes;
- no new hosted candidate merely to reroll convergence.

## Current hosted frontier

Most recent read-only top-20 snapshot already obtained in this work session (`2026-09-13 ~12:48 UTC`):

1. Majkel1337 `3239.9`
2. Mengfei Li `3065.9`
3. Artem The Farmer `3064.4`
4. ymg_aq `3020.9`
5. SpaTaro `3019.2`
6. Otter Vibe `3005.0`
7. redblackbst `2991.3`
8. feel the agi `2990.5`
9. binghua `2968.2`
10. Subramanya N `2965.4`

Older full-snapshot population thresholds remain useful only as approximate context: rank 100 `2782.8`, rank 500 `2578.1`, rank 1000 `2300.8`, rank 2000 `1679.7`.

## Closed / quarantined

- CR078: closed.
- CR079 SpaTaro 1-NN clone: closed / FAIL.
- CR080 Mengfei route stitching: closed / FAIL; economic-state aliasing.
- CR081 v1/v2 invalid; CR081 v3 valid catastrophic FAIL / CLOSED.
- CR082 state-adaptive Majkel 1-NN: valid catastrophic FAIL / CLOSED; canonical run `34708795892`, SHA `199d32fdda64d4c8d4334f7174d1532147b75837c51104eab9a7c78aec302c2a`.
- **CR084 critical late-livestock rescue: CLOSED / DO NOT RETUNE.** Corrected SHA `3aa08bb2ee163d1707dbf0bf9d2cb4b6f8c194fa2dbd715c38a67a4a41d414a2`. Gate A barely passed 0.5625, but frozen promotion run `34758417896` failed: CR084 vs CR083 12W–10L–42T = **0.515625**, mean margin `-106.625`, aggregate guardrail delta negative and CR071M delta `-0.125`. Independent temporal high-strength proxy `34758785488` also found **0 rescue opportunities / 0 preventable escapes** in 6 >=2300 episodes. Final record: `docs/strategy/CR084_FINAL_RESULT_2026-09-13.md`.
- **CR085 Pareto-guarded adaptive switch: CLOSED / DO NOT RETUNE.** Frozen SHA `eb7bac5c5619e70d1ef81dd18f28b642b96326be31ae50354cdca7770531bdf7`. Semantic audit and seed firewall passed, but Gate A run `34761593920` on master `9150851` produced **3W–3L–26T = 0.5000**, mean margin **-147.46875** versus CR083. Decision: `CLOSE_CR085_PARETO_GUARDED_SWITCH`. No tuning of guarded dimensions, switch steps, or zero thresholds.

Behavioral imitation / replay stitching remains closed as the primary representation. CR084-style late FEED rescue and CR085-style Pareto switch gating are also closed.

## CR083 local evidence

Phase 0 mechanics: `34709053070`.

Phase 1 broad family ablation: `34715158344`; every whole-market-family deletion lost 0–16 to exact CR071M, so broad deletion remains closed.

Phase 2 canonical promotion: **`34715575445`**.

- CR083 vs CR071M: **45W–1L–18T = 0.84375** over 64 fresh games;
- direct mean margin `+172.5`, median `+240`;
- guardrail score delta vs CR053/CR061/CR065: `0 / 0 / 0`;
- zero execution errors / incomplete games.

A fresh same-master row inside the CR084 promotion panel also reconfirmed CR083's local strength versus CR071M: **57W–1L–6T = 0.9375** on master `9140842`.

## Active research direction

**CR086 discovery — public strong-backbone benchmark + quantitative market/adversary-state modeling.**

Incremental patches on the CR083 route architecture have now failed twice independently (CR084 and CR085). The next step is not another route threshold. Public Kaggriculture notebooks currently exist with displayed ratings materially above CR083, including agents around the mid/high 2000s. Kaggle staff has publicly stated that freely/publicly available competition material is fair use, subject to normal competition/licensing requirements.

Before defining CR086:

1. pull selected public notebook sources read-only through authenticated Kaggle CLI;
2. freeze exact source/package hashes and notebook license/attribution metadata;
3. identify executable agent packages and architectural mechanisms;
4. benchmark exact public agents locally against CR083 and legacy anchors before modifying anything;
5. separately evaluate a legal quantitative opponent-inventory estimator derived from public state, with uncertainty around floor sales/private losses;
6. only after those benchmarks may a CR086 candidate protocol be frozen.

Public code is a benchmark/backbone candidate, not automatic permission to submit an unchanged third-party agent. Prize eligibility, attribution and license compliance must remain explicit.

Do not clone hidden/private strategies and do not condition runtime policy on identity, EpisodeId, rating, hidden seed, future state or opponent-private state.

## Binding policies

- Authenticated Kaggle API first.
- Exact H2H uses `kaggle-environments==1.32.7`, isolated package processes and both seats.
- Original final holdout remains sealed.
- Invalid/duplicate evaluations are quarantined before score interpretation.
- Closed hypotheses stay closed unless genuinely new evidence invalidates their closure.
- Runtime features/actions use only legal current observation plus frozen public mechanics/constants.
- CR083 remains immutable at SHA-256 `648fbcdb370f7e48fafda18a1112c5f1b57a17a81b7191f010fe4058f41a41b8`.
- **No repeated live polling. Re-check CR083 only at a material decision boundary, especially the predeclared 100-public-episode checkpoint.**
- **No new hosted submission until a genuinely independent architecture passes direct, guardrail and high-strength-population stress layers.**
