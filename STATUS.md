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
- latest authenticated score checkpoint (`34745664559`, rerun job `103694087017`): **1596.2**
- mature CR071M control `56124705`: **1642.4** at the same checkpoint
- current gap: **-46.2**, narrowed from the earlier `-83.3`

Important correction: Kaggle simulation submissions start from `mu_0 = 600` with high uncertainty and converge through repeated episodes. A new CR083 rating therefore cannot be maturity-compared directly with the much older CR071M after only a few dozen games. Money margin does not affect the rating update; W/L/T does.

Frozen hosted checkpoint and maturity rule: `docs/strategy/CR083_HOSTED_PROBE_CHECKPOINT_2026-09-13.md`.

### 36-replay hosted forensic freeze

Read-only forensic run `34745898829`, artifact `10314660085`:

- **27W–9L–0T = 75.0% raw win rate**;
- mean money margin `+14,703.1`, median `+6,385`;
- seat 0: 14W–4L; seat 1: 13W–5L;
- 36/36 opponents matched exactly to fresh full leaderboard artifact `10313912424`, snapshot `2026-09-13T07:47:09 UTC`.

Opponent-strength split from the fresh snapshot:

- `<1200`: 6–0;
- `1200–1499`: 8–2;
- `1500–1699`: 10–3;
- `1700–1999`: 2–0;
- `2000–2299`: 1–0;
- `2300–2599`: **0–3**;
- `2600+`: **0–1**.

Current rating `2300.8` is approximately rank 1000. The strongest current warning is therefore **0–4 against the four sampled opponents at >=2300 / roughly top-1000 strength**. This is small-n evidence, not a final CR083 verdict, but it exposes a missing high-strength population proxy in our old local gate.

### Frozen maturity decision

Project heuristic, not an official Kaggle rule:

- **do not close CR083 before 100 completed public episodes**;
- at 100+, re-freeze hosted replays, rating trend, overall W/L and high-strength W/L;
- no CR083A/B/C, no `step 434` retuning, no crop exception, no clamp-formula tuning from hosted outcomes;
- no second hosted candidate while CR083 is still being diagnosed.

## Current hosted frontier

Fresh full leaderboard snapshot `2026-09-13T07:47:09 UTC`:

1. Majkel1337 `3217.2`
2. Mengfei Li `3068.7`
3. THIRD FARM CLUB `3034.7`
4. ymg_aq `3034.2`
5. Artem The Farmer `3028.0`
6. SpaTaro `3021.9`
7. feel the agi `3002.8`
8. Otter Vibe `2990.0`
9. Subramanya N `2974.9`
10. binghua `2970.8`

Population thresholds: rank 100 `2782.8`, rank 500 `2578.1`, rank 1000 `2300.8`, rank 2000 `1679.7`.

## Closed / quarantined

- CR078: closed.
- CR079 SpaTaro 1-NN clone: closed / FAIL.
- CR080 Mengfei route stitching: closed / FAIL; economic-state aliasing.
- CR081 v1/v2 invalid; CR081 v3 valid catastrophic FAIL / CLOSED.
- CR082 state-adaptive Majkel 1-NN: valid catastrophic FAIL / CLOSED; canonical run `34708795892`, SHA `199d32fdda64d4c8d4334f7174d1532147b75837c51104eab9a7c78aec302c2a`.

Behavioral imitation / replay stitching remains closed as the primary representation.

## CR083 local evidence

Phase 0 mechanics: `34709053070`.

Phase 1 broad family ablation: `34715158344`; every whole-market-family deletion lost 0–16 to exact CR071M, so broad deletion remains closed.

Phase 2 canonical promotion: **`34715575445`**.

- CR083 vs CR071M: **45W–1L–18T = 0.84375** over 64 fresh games;
- direct mean margin `+172.5`, median `+240`;
- guardrail score delta vs CR053/CR061/CR065: `0 / 0 / 0`;
- zero execution errors / incomplete games.

Conclusion: local anchor dominance was real, but it did not test upper-population transfer. Future gates must include an independent high-strength population proxy.

## Active research direction

**Population-strength proxy gap.** Build a legal offline stress layer from high-strength public live replays/current-observation regimes. The goal is not to clone opponent actions; it is to expose economic states and strategy pressures absent from CR071M/CR053/CR061/CR065 validation.

Runtime remains prohibited from using identity, EpisodeId, hidden seed, future state or opponent-private state.

## Binding policies

- Authenticated Kaggle API first.
- Exact H2H uses `kaggle-environments==1.32.7`, isolated package processes and both seats.
- Original final holdout remains sealed.
- Invalid/duplicate evaluations are quarantined before score interpretation.
- Closed hypotheses stay closed unless genuinely new evidence invalidates their closure.
- Runtime features/actions use only legal current observation plus frozen public mechanics/constants.
- CR083 remains immutable at SHA-256 `648fbcdb370f7e48fafda18a1112c5f1b57a17a81b7191f010fe4058f41a41b8`.
- **No new hosted submission while CR083 matures and the population proxy is being rebuilt.**
