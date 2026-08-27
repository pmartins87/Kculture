# CR-002 — Broad proxy league calibration

Status: **CLOSED — CALIBRATION_FAIL**

## Why this exists

CR-001 falsified the easy explanation that Kculture had benchmarked the wrong files. The exact historically scored packages were checked:

- Kaito V27 V4 (3090.1): packaged `main.py` byte-identical to the file Kculture had used;
- Rayk V11 (2990.4): packaged `main.py` byte-identical;
- Andrew V12 (2883.0): packaged `submission.py` byte-identical to the top-level `main.py` Kculture had used.

Therefore R4B beating those three agents locally while scoring ~142 hosted is evidence that a tiny head-to-head panel is not a calibrated field-strength proxy. CR-002 tested whether a much broader historical-public league could repair that problem.

## Frozen league

`configs/competitive_reset_league_v1.json` defines 12 entrants:

- 10 identity-proven public agents spanning historical scores 1771.3–3090.1;
- frozen R4B (hosted snapshot 142.0);
- frozen KEXP-050 (hosted snapshot 145.1).

All 66 unordered pairs were generated automatically. Each pair played the same 6 fresh deterministic environmental seeds in both seats = 12 episodes/pair, 792 total episodes. The fresh seed generator excluded all frozen development/validation/held-out partitions.

## Predeclared calibration gate

- complete 66/66 pair matrix;
- zero runtime/status errors;
- Spearman(public local BT, historical score) >= **0.60**;
- public BT pair-order accuracy >= **0.65**.

## Attempt history

### Attempt 1 — run `33083452488`: MECHANICAL NULL

Preparation succeeded. Pair jobs failed before any episode with `ModuleNotFoundError: No module named 'tools'`. No competitive outcome was observed.

Fix commit: `08d242366037b19e20ee906e06dbe2bc6b760242`.

### Attempt 2 — run `33083761765`: MECHANICAL NULL

Preparation succeeded. Pair jobs failed before any episode while constructing the seed exclusion set with `TypeError: 'int' object is not iterable`. No competitive outcome was observed.

Fix commit: `df23ba195688f599280f9e246b61342bf65bdc5d`.

### Attempt 3 — run `33084489238`: VALID / CALIBRATION_FAIL

Canonical result artifact: `cr002-league-result`, artifact id **9652034347**, artifact ZIP digest **sha256:52698fd46d11968893a96baac908cac86afccd0ce9dbe93c726ab4246fd97787**.

Results:

- pair matrix: **66/66 complete** — PASS;
- runtime/status errors: **0** — PASS;
- public BT pair-order accuracy: **0.6888889** — PASS vs 0.65;
- public Spearman: **0.5757576**, p=0.08155 — **FAIL** vs 0.60;
- majority cycles: 0 in this small deterministic proxy league;
- formal status: **CALIBRATION_FAIL**.

Local BT ranking:

1. KEXP-050 — BT centered Elo 2246.0; hosted snapshot 145.1
2. R4B — 2216.4; hosted snapshot 142.0
3. Flex V59 — 2145.9; historical public 2767.3
4. Andrew V12 — 1979.7; historical public 2883.0
5. Kaito V27 — 1821.0; historical public 3090.1
6. Rayk V11 — 1424.9; historical public 2990.4
7. Anas V2 — -67.8; historical public 2213.8
8. Prvsiyan Baseline V2 — -1607.6; historical public 2123.7
9. Bruce Pipeline V1 — -1803.1; historical public 2754.9
10. Roman Hamburger V21 — -2067.8; historical public 2391.0
11. Prvsiyan Frontier V5 — -2263.4; historical public 2798.6
12. Renji Builder V3 — -4024.2; historical public 1771.3

## Strong falsification from R4B

R4B beat every one of the ten historical public references on the six fresh seeds, totaling **112-8 / 120**:

- Kaito: R4B 8-4;
- Rayk: 12-0;
- Andrew: 10-2;
- Prvsiyan Frontier: 12-0;
- Flex: 10-2;
- Bruce: 12-0;
- Roman: 12-0;
- Anas: 12-0;
- Prvsiyan Baseline: 12-0;
- Renji: 12-0.

This is incompatible with treating the historical-public league as a current-field strength proxy while R4B/KEXP-050 remain around 142/145 hosted. The result is stronger than a simple failed Spearman threshold: the sampled public generation is structurally unrepresentative of the current ladder distribution relevant to Kculture.

## Decision

**CR-002 is diagnostic only. It is retired for promotion decisions.**

Do not promote a candidate because it beats this historical-public field, Kaito/Rayk/Andrew, or improves local BT here. The next proxy must be anchored to current-meta evidence and current public snapshots, with temporal freshness treated as a first-class variable.

Historical public packages remain useful for architecture study and regression coverage, but no longer define competitive strength.

## Next step

Build a current-meta calibration set using recent public notebook snapshots with contemporaneous public scores plus official recent episode behavior. Before strategic promotion, require the new proxy to explain both:

1. ordering among current public snapshots; and
2. why R4B/KEXP-050 are weak in hosted play despite exploiting the historical-public generation.

No validation or held-out outcomes were opened by CR-002.
