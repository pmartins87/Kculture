# KEXP-20260825-011 — exact Kaito V27 strong screen

## Purpose

Raise the R4 development opponent ceiling from older public policies to an exact current high-rating public artifact before attempting another strategy mutation.

## Opponent provenance

Kaito Fukami public notebook:
`kaitofukami/25-27-strict-future-v27-midgame-meta-reset`

- exact notebook version: **4**
- public score snapshot: **3090.1**
- best score snapshot: **3090.1 V4**
- license displayed on the Version-4 Kaggle page: **Apache-2.0**
- published production `main.py` SHA-256: `f48c21166eac68d1b05a401f04f94a2eb6154e65415af64893672365ff33c7b8`
- published size: `20813` bytes

### Exact acquisition proof

GitHub Actions run `32920859121` used `kagglehub.notebook_output_download` with all Kaggle credential environment variables explicitly blank.

The public Version-4 output downloaded successfully and contained:

- `main.py` — 20,813 bytes — SHA-256 `f48c21166eac68d1b05a401f04f94a2eb6154e65415af64893672365ff33c7b8`;
- `submission.tar.gz` — 12,148 bytes — SHA-256 `9a158d0b251d18d042386d33fb31a4f4096005637c80953162e329d2eb7ff072`.

The acquired `main.py` therefore matches the independent digest published in the notebook's research text exactly. Artifact ID `9589807795`; acquisition ZIP digest `789fa07916aef511f957379c334c0232a92ae874f4c29a0af77fe96bb9185a58`.

Kculture does not modify the Kaito artifact for this benchmark.

## Candidate/control

A. `R4A-public-base-v1` / exact COK V8 control.

B. `R4B-market-only-validated-v1`, Git blob `e564125f0c4a1711fd3ea065dc1cb27d4a62ce37`.

## Protocol

GitHub Actions run `32921007864`.

Use all **16 frozen development seeds**, both seats, `kaggle-environments==1.32.7`:

- R4A vs exact Kaito V27 — 32 games;
- R4B market-only vs exact Kaito V27 — 32 games.

Total: 64 development games.

Every job independently downloads Version 4 via KaggleHub and rejects the run unless `main.py` matches the published SHA-256 above.

No validation or held-out seed is opened.

## Results

| Candidate | W-L-T | Score rate | Mean delta | Median | Min | Max | Errors |
|---|---:|---:|---:|---:|---:|---:|---:|
| R4A / COK V8 | **25-7-0** | **0.78125** | **+4,382.03125** | +2,821.5 | -5,603 | +17,468 | 0 |
| R4B market-only | **25-7-0** | **0.78125** | **+4,396.84375** | +2,821.5 | -5,603 | +17,468 | 0 |

R4B increases mean money delta by **+14.8125 per game** while leaving the W/L pattern unchanged.

### Exact loss pattern

Both R4A and R4B lose the same seven games:

- seed `150614441`, seat 1: `-5,603`;
- seed `1743398262`, seat 0: `-2,896`;
- seed `1743398262`, seat 1: `-2,488`;
- seed `163219477`, seat 0: `-3,516`;
- seed `163219477`, seat 1: `-3,516`;
- seed `598340816`, seat 0: `-539`;
- seed `598340816`, seat 1: `-539`.

The market-only terminal intervention therefore preserves its small economic gain against V27 but **does not flip any frontier matchup outcome**. The difficult cases are driven by earlier economic/continuation differences rather than the final liquidation edge.

## Interpretation

**FRONTIER ADVERSARY CONFIRMED; NO BASE MIGRATION.**

1. Exact Kaito V27 is materially stronger than the older V18/Seyamalam panel because it creates seven losses where those opponents create none.
2. Nevertheless, both R4A and R4B beat V27 decisively on this frozen development partition: **25-7**, score rate `0.78125`, with positive mean delta above `+4.3k`.
3. A public Kaggle score of 3090.1 is therefore valuable meta evidence but not proof that V27 is a superior local engineering base to COK/R4B.
4. R4B remains preferable to R4A because it preserves all 25 wins / 7 losses while adding a small positive mean-delta edge, consistent with its prior validation/generalization evidence.
5. The seven V27 losses identify a real frontier failure family. Their recurrence in both seats for seeds `1743398262`, `163219477`, and `598340816` shows genuine seed-level weaknesses rather than only seat-order noise. Seed `150614441` is seat-sensitive.
6. The next strategy mutation should not copy V27 wholesale. First add at least one additional independent current-meta public family around the ~2900–3000 range, then determine whether the same failure seeds/economic regimes recur.
7. If a recurring frontier pattern is confirmed, prioritize a single auditable midgame/continuation mechanism; the market-only terminal layer is retained unchanged.

## Decision

- **Keep `R4B-market-only-validated-v1` as the frozen hosted-submission candidate.**
- **Keep COK/R4B as the active engineering lineage.**
- Add exact current-meta opponents (Rayk/Andrew where version/provenance can be verified) before R4D mutation.
- Use V27 as a frontier opponent and diagnose the seven exact losses.
- Do not reopen validation for exploratory work.
- Held-out remains sealed **32/32**.

## Evidence

- acquisition run: `32920859121`;
- strong-screen run: `32921007864`;
- R4A artifact: `9589959331`, ZIP SHA-256 `580cfc4994e00c268ebc33b113087de1a239a62aa8b71d52df1c2d23a0a4dd30`;
- R4B artifact: `9589962626`, ZIP SHA-256 `f5d4fc97a605068d1dedf7c62e0e6012b5e1b22051f01bc53c4332b1172703b1`.

## Status

**COMPLETE — FRONTIER SCREEN PASS AS DIAGNOSTIC; NO BASE MIGRATION.**
