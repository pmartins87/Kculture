# KEXP-20260827-054 — KEXP-050 fresh validation

Status: **PASS / PACKAGE PARITY AUTHORIZED**

## Candidate freeze

Selected candidate: `candidates/r4d_reallocate_614_carrot.py`  
Candidate blob: `61b77be136836328917441cb03f89bc6665c4c27`  
Frozen parent R4B blob: `e564125f0c4a1711fd3ea065dc1cb27d4a62ce37`.

No candidate code, trigger threshold, timing, action selection, or market logic changed after freeze and before validation outcomes were read.

## Evidence before validation

KEXP-050 passed three open-data stages without accessing validation or held-out outcomes:

- development direct vs R4B: **21-11**, score 0.65625, mean terminal delta +103.97, zero errors;
- exploratory live-meta pool: **15-11-14**, score 0.55, mean terminal delta +11.85, zero errors;
- KEXP-052 fresh independent 96-seed stress, both seats: **87-47-58**, score **0.6041667**, mean terminal delta **+41.24**, zero errors; seat scores 0.59896 / 0.60938.

KEXP-045 tied KEXP-050 at 0.6041667 on the KEXP-052 stress. The predeclared tie-break selected KEXP-050 because it changes fewer actions, reallocates an existing WHEAT purchase instead of appending a new seed purchase, and incurs only +10 incremental seed cost.

## Validation design

Exactly the frozen 16-seed `validation` partition from `configs/seed_partitions.json`, both seats. Seven independent blocks:

1. KEXP-050 vs frozen R4B direct;
2. KEXP-050 vs Kaito V27;
3. R4B vs Kaito V27 control;
4. KEXP-050 vs Rayk V11;
5. R4B vs Rayk V11 control;
6. KEXP-050 vs Andrew V12;
7. R4B vs Andrew V12 control.

All public opponents remained hash pinned to the development versions.

## Mechanical-null first attempt

Run `33073158744` is **MECHANICAL NULL**, not a validation result. All seven jobs were refused before any validation episode started because `tools/run_late_lifecycle_panel.py` intentionally enforces a development-only guard:

`Exploratory lifecycle panel is development-only; refusing partition='validation'`

No result artifact was generated. No validation outcome was observed. The candidate and gate were unchanged.

The runner was repaired in commit `e9cc6bb84d93b96aff21f785711163f15f1362a8` to use the repository's validation-approved `tools/run_tournament.py`, matching the earlier R4B validation method.

## Successful validation run

Run: **`33073517302`**.

### Direct KEXP-050 vs frozen R4B

Artifact `9647040397`, digest `sha256:64b550691c20b09ccf231008d1d0993a1dee6fe2268db6ce0b87eea85e5139c5`.

- 32 episodes;
- **14 wins / 8 losses / 10 ties**;
- score rate **0.59375**;
- mean money delta **+31.0625**;
- median delta 0;
- zero errors.

Predeclared direct gate: score >=0.53125 and mean delta >0. **PASS**.

### Public-opponent regression controls

KEXP-050:

- Kaito V27: **25-7**, artifact `9647031718`, digest `sha256:8a7faa4f81d4d397d6e9d07eb75607d409d860c8402429463af8032acb9795f4`;
- Rayk V11: **32-0**, artifact `9647030080`, digest `sha256:1048349f5ee8998a6d32fea67a7d6687d8625278192ce48fc25e48b46181cb87`;
- Andrew V12: **21-11**, artifact `9647032941`, digest `sha256:33796e57d008d38912744e4d09e1f936c145672c56cf51196258043d1f63d167`;
- combined **78-18**, zero errors.

Frozen R4B controls on the identical validation seeds:

- Kaito V27: **25-7**, artifact `9646987551`, digest `sha256:86a6223e8518358bb0c44b8228b351863c5732cad0edcf6fdef354b5eec6ea7d`;
- Rayk V11: **32-0**, artifact `9647027804`, digest `sha256:1b76f3771238a22b3a25c3092de520d05c9553ad246d5cc75a65004e2a679a0e`;
- Andrew V12: **21-11**, artifact `9647027822`, digest `sha256:58774c2955f898a2dce393cc49c19b7690c23f7f80e21120fea9d7f6a177b800`;
- combined **78-18**, zero errors.

The candidate preserved every public-family win exactly; no regression occurred.

## Predeclared promotion gate — PASS

- zero runtime/status errors in every block: **PASS**;
- direct score >=0.53125: **0.59375 PASS**;
- direct mean terminal delta >0: **+31.0625 PASS**;
- candidate combined public-panel W/L not worse than R4B control: **78-18 vs 78-18 PASS**;
- no individual family loses >1 candidate win versus R4B: **0 lost wins in every family PASS**.

**Decision: KEXP-050 is promoted to package-parity preparation.**

This is a local validation promotion, not evidence of top-10 hosted strength. The known hosted/local calibration gap remains large; after exact self-contained package parity, the next Kaggle submission should be treated as a materially different hosted calibration agent.

Held-out: **32/32 remain sealed**.
