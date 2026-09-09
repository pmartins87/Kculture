# CR073 — Public frontier calibration preregistration — 2026-09-09

## Question

Do current high-hosted public agents (roughly 2680–2990 historical best scores) also dominate the current Kculture PARENT / CR071M PRESALE1 under the exact local Kaggle reference environment?

This is a laboratory-calibration experiment, not a candidate-promotion experiment.

## Frozen corpus

Public packages come from CR072 run `34370093160`, artifact `cr072-public-frontier-corpus-v1`:

- `RAYK_V11_2990`: `rayk_v11_2990/submission.tar.gz`, SHA256 `99e3ab82275d1d6991553a50c67f7fb3c83c029072dab2e890155b34d34c3cc1`.
- `MOON_V11_2736`: `moon_v11_2736/submission.tar.gz`, SHA256 `f60cadee2fa54c6fd2b9c0ac9aec9d8106abdaa7d5fd2b3beffef51d3ec1b88a`.
- `MULTIROUTE_V59_2767`: `multiroute_v59_2767/submission.tar.gz`, SHA256 `af2ec593ac28333053ce66dd0616de831bba471dd98bbc334bedbd0526a90884`.
- `INDAR_V1_2686`: `indar_v1_2686/submission.tar.gz`, SHA256 `fa9e7eb1a0174a1bf292fb4d47bd209defed929758214d3506e050a68ee5f98f`.

Kculture controls come from frozen run `34315316048`:

- `PARENT_SEATSAFE_V1.tar.gz`.
- `CR071M_CR053_PRESALE1_SEATSAFE_V1.tar.gz`.

## Exact protocol

- engine: `kaggle-environments==1.32.7`;
- both seats;
- 32 paired seeds / 64 games per H2H;
- fresh `master_seed=9092031`;
- seed firewall against prior masters `5809072026`, `9092026`, `9092027`, `9092028`, `9092029` using conservative prior counts;
- primary metric: W/L / score_rate; money margin is not a decision target.

Eight H2Hs:

1. RAYK_V11_2990 vs PARENT
2. RAYK_V11_2990 vs PRESALE1
3. MOON_V11_2736 vs PARENT
4. MOON_V11_2736 vs PRESALE1
5. MULTIROUTE_V59_2767 vs PARENT
6. MULTIROUTE_V59_2767 vs PRESALE1
7. INDAR_V1_2686 vs PARENT
8. INDAR_V1_2686 vs PRESALE1

## Frozen interpretation tree

For each public agent, use its average score_rate across PARENT and PRESALE1 as the local-calibration score.

### Path A — LOCAL_CAPTURES_HOSTED_FRONTIER

Trigger if at least one public agent has score_rate >= 0.60 against BOTH PARENT and PRESALE1.

Action: prioritize causal decomposition of the strongest such public agent. First decompose backbone/route versus overlays; do not copy the whole agent blindly. The next candidate family must be derived from a mechanism with local causal support and legal observable state only.

### Path B — LOCAL_META_MISALIGNED

Trigger if NO public agent reaches 0.55 against either PARENT or PRESALE1, or if the historically strongest hosted agents are systematically <= 0.50 locally.

Action: stop treating historical local H2H rank as a strategic-strength proxy. Use local exact games mainly for mechanics, parity, regressions, and causal component checks. Hosted outcomes and current public-meta evidence become the primary strategic calibration layer.

### Path C — MIXED_CALIBRATION

All other outcomes.

Action: identify the single matchup whose uncertainty changes whether Path A or B is more plausible. Allow one expansion only, to 64 paired seeds for that matchup. No threshold tuning and no broad repeated expansion.

## Architectural observations frozen before results

Rayk V11 contains a strong fixed trajectory plus: public-farm clone detection; one-step premium front-run; terminal observation-driven harvest/drop/sell control; and premium SELL slot ordering by estimated marginal price impact.

Multi-Route V59 materializes a modal route from ten official public replays and applies observation-driven weed repair; its embedded RC5 source also includes a conservative one-step premium front-run/repay mechanism.

Moon V11 is a large tape/router ensemble with shop-prefix routing and a step-288 public money-gap latch for selected market tapes.

Indar V1 packages a multi-module route/pasture system with public-state components and engine-exact repairs.

These observations are explanatory only. CR073 W/L decides which architecture deserves the next causal decomposition.
