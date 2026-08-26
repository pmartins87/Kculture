# KEXP-20260826-020 — longitudinal live-meta demand response

Status: **COMPLETE / MECHANISM CONFIRMED / POLICY NOT YET PROMOTED**

## Prize-first question

KEXP-019 found a striking same-day association in the top-20 official 2026-08-25 ladder episodes: winners bought far more CARROT seed during steps 600–671, especially as public carrot-demand weight from the full eight-shop multiset increased. However, those 20 episodes were only Crop Dusta vs Ryo Hasegawa, so team identity was a serious confounder.

KEXP-020 repeated the exact same measurement over several recent daily ladder datasets before any Kculture policy change.

## Frozen protocol

Run `tools/live_meta_demand_response.py` independently on:

- 2026-08-22, top 10 episodes by `avg_score`;
- 2026-08-23, top 10;
- 2026-08-24, top 10;
- 2026-08-25, top 10.

Each episode contributes both players: up to 80 player-games total. Primary variables are identical to KEXP-019:

- complete public shop multiset at step 600;
- official carrot-demand weight = `2 * count(PET_CAFE) + count(FARMERS_MARKET)`;
- BUY_SEED CARROT during 600–671;
- final-day CARROT SELL during 696–718;
- W/L outcome;
- team name for confounding diagnosis only.

## Reproducibility

Actions run: **`33019559986` — SUCCESS**.
Artifact: **`9625961691`**, ZIP SHA-256 `76ddbf8e2d453cdb357143002646e14c59fdbed054240089ef19968ce26a3963`.

Official public ladder episodes only. No frozen validation or held-out seeds were touched.

## Primary result — full-shop CARROT demand response generalizes across days

The correlation between public CARROT-demand intensity and late CARROT seed purchases was positive and remarkably stable on every sampled day:

| Day | demand→late CARROT seed-buy Pearson |
|---|---:|
| 2026-08-22 | **+0.49505** |
| 2026-08-23 | **+0.52212** |
| 2026-08-24 | **+0.53413** |
| 2026-08-25 | **+0.50326** |

This is the main causal-intelligence result. Strong live agents are not simply following one static crop tape: they systematically react to the complete late public shop demand state.

The mechanism is also consistent with the frozen official engine:

- all eight shop instances are normally visible by late season;
- PET_CAFE consumes CARROT at double rate because it is a single-product shop;
- FARMERS_MARKET also consumes CARROT;
- CARROT uses the current `hinge` scarcity price curve;
- CARROT reaches first yield in two days and max yield in three, so it is one of the few crops that can still repay a day-24/25 pivot.

## Important negative result — CARROT is not an unconditional winner rule

Winner-vs-loser CARROT allocation was not monotonic across days:

| Day | Winner mean CARROT seed buy 600-671 | Loser mean | Winner mean final-day CARROT sell | Loser mean |
|---|---:|---:|---:|---:|
| 2026-08-22 | **11.7** | 3.3 | **12.8** | 5.4 |
| 2026-08-23 | 3.0 | **3.8** | 5.6 | **13.8** |
| 2026-08-24 | 9.1 | **10.3** | 13.5 | **28.3** |
| 2026-08-25 | **15.7** | 2.7 | **45.7** | 6.7 |

Therefore the policy inference is **not** “buy more carrot late”. The robust inference is narrower:

> current high-Elo agents condition their late crop allocation on the full public demand state; CARROT becomes an important short-horizon response in high-CARROT-demand regimes, but profitability also depends on the rest of the economic state.

A deployable Kculture candidate should therefore combine public demand with current market/economic observables rather than copy a fixed CARROT quantity.

## Multi-team evidence

The response is not unique to one Aug-25 team. Distinct high-Elo families show late CARROT allocation:

- 2026-08-22: `Subramanya + Aakarsh` mean late CARROT buy ~16.0 over its sampled games;
- 2026-08-23/24/25: `Crop Dusta` shows strong CARROT allocation in high-demand regimes;
- `Ryo Hasegawa` generally remains more WHEAT-heavy.

This is enough to reject the hypothesis that the KEXP-019 relationship was merely a Crop Dusta identity artifact. Team identity remains forbidden as a deployment feature.

## Demand-level counterexamples matter

Several days contain high-demand cases where the loser bought more CARROT than the winner, for example demand weight 6 on Aug-23 and weight 3 on Aug-24. These are valuable anti-overfitting cases. Any R4D threshold learned solely from Aug-25 would be rejected.

## Relationship to frozen COK/R4B

Static exact COK V8 audit (`cok-live-meta-gap-v2`) shows a large structural mismatch:

- route choice is largely committed from the first three shops;
- at steps 576-599 the main routes plant roughly 6-10 WHEAT and essentially no CARROT;
- at steps 600-671 they plant roughly 28-32 WHEAT and only 0-3 CARROT depending on route;
- the movement/plant slots already exist, so a bounded late crop substitution can be tested without rewriting the whole spatial route.

This gap is higher-value than the previously tested three-route macro solver, whose perfect ex-post upper bound improved only 81-15 to 83-13.

## Decision

**KEXP-020 supports opening a bounded R4D late-demand-response development candidate.** It does not justify submission or validation access by itself.

Candidate design constraints:

1. preserve frozen R4B/COK behavior outside the late crop mechanism;
2. use only legal public observables such as the full shop multiset and current market state;
3. never use team, episode or seed identity;
4. substitute only a bounded subset of existing late WHEAT seed/plant slots rather than rewriting movement;
5. test W/L first on the frozen 16-seed modern panel and separately on exploratory environmental regimes drawn from current high-Elo public episodes;
6. do not open fresh validation until one exact candidate is frozen and has cross-panel evidence;
7. keep all 32 held-out seeds sealed.

## Next experiment

Build one or two conservative R4D crop-response variants, predeclare their exact triggers, and evaluate pairwise against frozen R4B. Prefer a price/demand-aware trigger over a pure demand threshold because KEXP-020 demonstrates demand-level counterexamples.
