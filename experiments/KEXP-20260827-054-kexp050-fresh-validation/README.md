# KEXP-20260827-054 — KEXP-050 fresh validation

Status: **FROZEN / VALIDATION AUTHORIZED**

## Candidate freeze

Selected candidate: `candidates/r4d_reallocate_614_carrot.py`  
Candidate blob: `61b77be136836328917441cb03f89bc6665c4c27`  
Frozen parent R4B blob: `e564125f0c4a1711fd3ea065dc1cb27d4a62ce37`.

No candidate code, trigger threshold, timing, action selection, or market logic may change after this freeze and before reading validation outcomes.

## Why validation is now authorized

KEXP-050 has passed three open-data stages without accessing validation or held-out outcomes:

- development direct vs R4B: **21-11**, score 0.65625, mean terminal delta +103.97, zero errors;
- exploratory live-meta pool: **15-11-14**, score 0.55, mean terminal delta +11.85, zero errors;
- KEXP-052 fresh independent 96-seed stress, both seats: **87-47-58**, score **0.6041667**, mean terminal delta **+41.24**, zero errors; seat scores 0.59896 / 0.60938.

KEXP-045 tied KEXP-050 at 0.6041667 on the KEXP-052 stress. The predeclared tie-break selected KEXP-050 because it changes fewer actions, reallocates an existing WHEAT purchase instead of appending a new seed purchase, and incurs only +10 incremental seed cost.

## Fresh validation design

Use exactly the frozen 16-seed `validation` partition from `configs/seed_partitions.json`, both seats. Held-out remains sealed.

Run seven independent validation blocks:

1. KEXP-050 vs frozen R4B direct;
2. KEXP-050 vs Kaito V27;
3. R4B vs Kaito V27 control;
4. KEXP-050 vs Rayk V11;
5. R4B vs Rayk V11 control;
6. KEXP-050 vs Andrew V12;
7. R4B vs Andrew V12 control.

All public opponents remain hash pinned to the same versions already used in development.

## Predeclared validation promotion gate

Promotion to package-parity preparation requires all of the following:

- zero runtime/status errors in every block;
- direct KEXP-050 vs R4B score rate **>= 0.53125**;
- direct mean terminal delta **> 0**;
- candidate combined W/L against Kaito/Rayk/Andrew is **not worse than the R4B control combined W/L** on the same validation seeds;
- no individual public-opponent family loses more than **one candidate win** versus its corresponding R4B validation control.

Terminal money is secondary to W/L/T except for the positive direct-delta guard above.

If the gate fails, do not tune KEXP-050 against individual validation seeds. Validation becomes consumed evidence for this frozen candidate; return to development/exploratory work with a materially different policy.

If the gate passes, freeze the exact candidate/dependency closure, build a Kaggle submission package, and require exact package parity before any hosted calibration submission.

Held-out: **32/32 remain sealed**.
