# CR-002 — Broad proxy league calibration

Status: **FROZEN / READY TO RUN**

## Why this exists

CR-001 falsified the easy explanation that Kculture had benchmarked the wrong files. The exact historically scored packages were checked:

- Kaito V27 V4 (3090.1): packaged `main.py` byte-identical to the file Kculture had used;
- Rayk V11 (2990.4): packaged `main.py` byte-identical;
- Andrew V12 (2883.0): packaged `submission.py` byte-identical to the top-level `main.py` Kculture had used.

Therefore R4B beating those three agents locally while scoring ~142 hosted is evidence that a tiny head-to-head panel is not a calibrated field-strength proxy. Non-transitivity / matchup coverage is now the primary hypothesis.

## Frozen league

`configs/competitive_reset_league_v1.json` defines 12 entrants:

- 10 identity-proven public agents spanning historical scores 1771.3–3090.1;
- frozen R4B (hosted snapshot 142.0);
- frozen KEXP-050 (hosted snapshot 145.1).

All 66 unordered pairs are generated automatically. No pair can be removed after results are observed.

Each pair plays the same 6 fresh deterministic environmental seeds in both seats = 12 episodes/pair, 792 total episodes. The fresh seed generator excludes all frozen development/validation/held-out partitions.

## Primary metric

Fit one Bradley–Terry model from the full local league. For the 10 public references only, compare local BT strength ordering with historical Kaggle score ordering.

Predeclared calibration gate:

- complete 66/66 pair matrix;
- zero runtime/status errors;
- Spearman(public local BT, historical score) >= **0.60**;
- public BT pair-order accuracy >= **0.65**.

If the gate fails, CR-002 is diagnostic only. We must expand/reweight the field or episode design before using it for candidate promotion.

If the gate passes, this league becomes the first promotion-grade local strength proxy of the Competitive Reset. Candidate development then targets broad BT/coverage improvement rather than isolated wins versus Kaito/Rayk/Andrew.

## Important interpretation

Historical Kaggle scores were observed at different snapshots and are not immutable ground truth. The gate asks only for useful rank correlation, not equality of numeric scores. R4B/KEXP-050 are excluded from the historical-score correlation because their 142/145 values are current dynamic snapshots; their local placement remains a crucial diagnostic.

No validation or held-out outcomes are opened by CR-002.
