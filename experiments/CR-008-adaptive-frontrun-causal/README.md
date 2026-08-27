# CR-008 — High-confidence identity-free adaptive front-run

Status: **COMPLETE — STRATEGIC FAIL / PREDICTION ARCHITECTURE REMAINS OPEN**

## Question

Do the high-confidence opponent forecasts proved in CR-004/005/007 improve an actual agent causally when converted into a minimal market best response?

## Frozen candidate

Corrected deployable candidate: `candidates/cr008_adaptive_frontrun.py` blob `8e1c26202c3101c19668bf61edf2ae51d4329d5d`.

Frozen base: `candidates/r4b_ablation_market_only.py` blob `e564125f0c4a1711fd3ea065dc1cb27d4a62ce37`.

Frozen pure model: `models/cr007_pure_models.json` blob `d4b29e753e2328ac43503f8daa655cc63abdd336`, file SHA-256 `6f12e86d0b19c5ba39c2ab4131e186ea14b49f42cc33b33a2ad895fab55783bb`.

Adaptive behavior was deliberately narrow:

- use only public opponent state; never name/team/submission identity;
- retain 24-turn public history inside the episode;
- CARROT trigger threshold 0.90;
- STRAWBERRY trigger threshold 0.85;
- if triggered and current own shed stock exists, append a same-turn SELL only when the frozen base is not already selling that product and a market slot is free;
- all physical actions and all other market decisions remain frozen R4B behavior.

## Mechanical-null run 1

GitHub Actions run **33099779694** never reached any strategic episode. Candidate/base/model identity checks passed, then the mandatory deployed feature-parity gate failed on exactly the player-1 half of the replay samples: 3000/6000 value mismatches, zero key mismatches. The frozen training encoder treats missing player-1 replay `step` as zero, while the first wrapper reconstructed it from day/hour. Its cache clock reconstruction was also 24 turns low because Kaggriculture `day` is zero-based.

This was corrected **before observing any CR-008 W/L** by separating:

- feature clock: exact CR-004 semantics (`obs.step` or zero when absent);
- memory clock: `obs.step` when available, otherwise `day*24 + hour`.

No seeds, opponents, thresholds, models or strategic response rules changed. Run 1 is therefore recorded as **MECHANICAL_NULL**, not a strategic FAIL.

## Deployability gates

Run 2 passed every mechanical gate before strategic interpretation:

- pure-tree file SHA matched the frozen SHA;
- sklearn→pure-tree probability parity had max absolute error **0.0** and 100% trigger agreement across 48,000 comparisons;
- deployed feature encoder parity: **6,000/6,000 exact**, zero key mismatches, zero value mismatches, max abs error 0.0;
- zero environment/action errors.

## Fresh exploratory field

`configs/cr008_fresh_exploratory_seeds_v1.json` blob `01b29fb4e19cba185b7d99a37ac13ee4715de574`.

12 seeds generated from independent master seed `2026082708`, explicitly excluding development, validation and held-out partitions. Validation/held-out remained untouched.

Exact public package opponents:

- Kaito Sparse V13 — snapshot 2882.0;
- Prvsiyan Frontier V10 — 2610.2;
- Tactical Memory V1 — 2491.7;
- Andrew V11 — 2441.2.

For each opponent, CR-008 and R4B played identical 12 seeds from both seats: **96 paired field episodes per policy**. A separate direct CR-008 vs R4B duel used the same 12 seeds from both seats.

## Strategic result

Run **33100148882** completed the full field and failed the frozen causal gate.  
Artifact **9659011814**; ZIP SHA-256 `4c8f3a4a1370cae33cee77318dc86028500da2aaf59d5c1e0c9da594e1864140`.

### Aggregate field

- R4B: **74–22**, score rate **0.77083**;
- CR-008: **75–21**, score rate **0.78125**;
- score-rate gain: **+0.01042**;
- mean CR-008 minus R4B own terminal reward: **−64.60**;
- mean relative-delta gain: **−33.45**;
- median own-reward gain: **0**;
- opponent families with positive mean own-reward gain: **0/4**.

The superficial W/L result therefore improved by one game while the primary causal economic measures regressed.

### By opponent family

| Opponent | Base score | CR-008 score | Own reward gain | Relative delta gain |
| --- | ---: | ---: | ---: | ---: |
| Andrew | 1.0000 | 1.0000 | **−8.83** | +56.75 |
| Kaito | 0.0833 | 0.1250 | **−8.00** | +50.00 |
| Prvsiyan | 1.0000 | 1.0000 | **−100.08** | −112.92 |
| Tactical | 1.0000 | 1.0000 | **−141.50** | −127.63 |

### Direct CR-008 vs R4B

- **4–4–16**;
- score rate **0.5000**;
- mean terminal delta **+5.5**;
- zero errors.

## Gate

Passed:

- complete pair coverage;
- zero errors;
- aggregate score rate not worse than −0.02;
- no family score-rate regression worse than −0.08.

Failed:

- positive mean own-reward gain;
- positive mean relative-delta gain;
- positive own-reward gain in at least two opponent families.

Final status: **ADAPTIVE_CAUSAL_FIELD_FAIL**.

## Decision

Reject the specific response rule **“high-confidence SELL sometime in the next 24 turns → sell all eligible own shed stock immediately.”** Do not hosted-submit CR-008 and do not tune CARROT/STRAWBERRY thresholds against this W/L result.

The opponent-state prediction architecture itself remains open: CR-007 still has strong out-of-time predictive evidence. CR-008 shows that prediction and best-response timing are separate problems. The next experiment must diagnose trigger-to-sale delay and the value of waiting before designing another causal response.
