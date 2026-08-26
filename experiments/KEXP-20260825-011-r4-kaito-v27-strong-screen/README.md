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

## Interpretation rule

This is a **strength/failure screen**, not a promotion gate.

- If R4B performs materially better than R4A, preserve that evidence but do not extend the old validation claim to any changed future code.
- If both struggle, use exact losing seeds/seats and route/economic traces to define the next R4D continuation hypothesis.
- If the panel is again saturated, add another independent current-meta public family before tuning.
- Do not alter the validated hosted candidate because of this run; every changed policy receives a new development experiment identity.

## Status

**RUNNING.**
