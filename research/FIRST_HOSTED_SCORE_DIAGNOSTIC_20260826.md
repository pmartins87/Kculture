# First hosted score diagnostic — 2026-08-26

## Event

The first exact Kculture hosted submission has completed Kaggle validation and joined the live ladder.

User-visible Kaggle Submissions UI at approximately **2026-08-26 04:37 UTC** shows:

- filename: `Kculture_R4B_market_only_validated_v1_submission.tar.gz`;
- description: `Kculture R4B market-only validated v1`;
- status: **Complete** with green check;
- displayed score: **161.6**.

Submission ID and hosted episode count were not visible in the captured screen and remain unknown at this checkpoint.

## Exact submitted artifact

- strategy: `R4B-market-only-validated-v1`;
- frozen candidate Git blob: `e564125f0c4a1711fd3ea065dc1cb27d4a62ce37`;
- package-build Git SHA: `29a883aba3df6347d72e321c9970c9694e0b6fa0`;
- archive SHA-256: `19cc08d2b3bcb8f8f947806c0ee01f4d7643d36f0c15abe0a978129ed1c53117`;
- packaged `main.py` SHA-256: `07bda5229dec0e50b56df8e76523188169213ba7cea4d2e118be61491fdc0cd1`;
- package parity Actions `32919305800`: PASS, 4/4 full trajectories identical to frozen candidate.

## Why 161.6 is not the expected ~3000

The ~2900–3100 values used during current-meta research are **mature public Kaggle skill-rating snapshots** for specific benchmark submissions/notebook versions. They are not deterministic scores produced directly by the agent code and they are not the starting value for a new submission.

Kaggle's simulation-evaluation documentation specifies that a valid new submission is initialized with skill-rating mean **mu0 = 600** after its self-play validation episode. Ongoing matched episodes then update the estimate based on win/loss/tie results and uncertainty. Kaggriculture also states that coin margin does not control rating movement; the match outcome does.

Therefore the observed **161.6** means the hosted estimate has already moved materially *below* its 600 initialization. It is an early online contradiction to the local calibration, not a harmless display of a different ~3000 scale.

## Local evidence before hosted submission

The same frozen candidate had strong reproducible local evidence under `kaggle-environments==1.32.7`:

- validation: 32-0 vs Seyamalam V21; direct vs R4A 8-6-18, score rate 0.53125;
- exact Kaito V27 V4 (public score snapshot 3090.1): 25-7 on 16 development seeds × both seats;
- exact Rayk V11 (best-score snapshot 2990.4): 30-2;
- exact Andrew V12 (best-score snapshot 2915.2): 26-6;
- combined current public panel: **81-15-0 / 96**, zero runtime errors.

This evidence remains valid for the specified deterministic local matchups. The live rating demonstrates that it was not sufficient to predict initial ladder behavior.

## Hypotheses now under test

The hosted contradiction can arise from one or more of the following, and no single explanation is assumed without episode evidence:

1. **early rating variance / high uncertainty** — new submissions receive frequent games, so a short adverse run can move the estimate sharply;
2. **ladder-distribution mismatch** — live opponents may exercise strategies and market interactions poorly represented by the pinned public panel;
3. **strategic exploitability** — the COK/R4B route lineage may be strong against known public agents while exposing a recurrent weakness against other live policies;
4. **hosted behavior mismatch** — despite package parity, hosted replay evidence must confirm action behavior under the actual ladder execution context;
5. **meta/version effects** — current live play may emphasize state regimes that deterministic development seeds under-sample.

## Immediate research response

- Do **not** assume 161.6 will automatically climb to ~3000.
- Do **not** discard the validated artifact based on one early snapshot alone.
- Preserve the submission as an online probe while continuing local work.
- Obtain submission ID and hosted episode list as soon as available; analyze W/L/T, opponents, rating trajectory, logs and replays.
- Keep the frozen submitted artifact immutable so hosted evidence remains attributable.
- Do not spend another submission slot until a new candidate has a mechanically justified improvement and its own reproducible gates.

## Parallel local finding

KEXP-013 independently found a multi-family late-game weakness in the frozen candidate. Across eight captured losses to exact Rayk V11 / Andrew V12, R4B is ahead at step 672 in every game (mean **+2007.5**) and finishes at mean **-1782.75**.

A deeper replay inspection adds a specific lifecycle clue:

- at step 672, losing R4B states average **13 strawberries whose `max_lifespan_step` is exactly 672**, plus **6.5** more expiring at 696;
- by step 696, R4B averages **13.5 weeds** versus **4.625** for those opponents;
- R4B then averages only **8 hands vs 9.75**, **18.5 vs 29.75 HARVEST actions**, **8 vs 13.75 DROP actions**, and **139.5 vs 222.75 requested SELL units** over steps 696–718.

The numerical match between the 13 step-672-expiring strawberries and the ~13.5 weeds visible at step 696 is a strong mechanistic lead: final-horizon productive acreage may be collapsing as old strawberry tiles age out and are not recovered fast enough. This is not yet causal proof and must be checked across **wins as well as losses** before R4D changes policy.

## Next gate

Create a development-only full-panel lifecycle diagnostic across all 16 development seeds, both seats, and independent current-meta families. Test whether:

- expiring-crop load at step 672 predicts late relative collapse;
- weed load at step 696 predicts late relative collapse;
- productive-acreage recovery, final-day hand count, HARVEST/DROP throughput and sellable-unit conversion explain residual variation;
- the signal survives across opponent families and winning games.

Only after that diagnostic should the narrowest state-based R4D crop-lifecycle intervention be coded.
