# Native Teacher Hybrid V1 Result — 2026-09-17

## Bottom line

The fixed 32-parameter native controller family is **closed as the competitive nucleus**.

The hybrid run executed 729,088 exact games in 117.2 s and improved the bootstrap hybrid objective slightly on fresh holdout (+0.1179), but it scored **0 wins against every one of the seven frozen strong replay tapes** on both train and holdout. The margins remained enormous (roughly -78k to -104k per replay family for the promoted hybrid champion).

This is not a reason to abandon the exact native infrastructure. It is evidence that the current controller representation/executor cannot express the strong behaviour already present in historical/public routes.

## Key numbers

Holdout:
- bootstrap parametric win rate vs parametric league: 0.5059
- hybrid parametric win rate vs parametric league: 0.5049
- bootstrap replay-tape win rate: 0.0000
- hybrid replay-tape win rate: 0.0000
- bootstrap mean replay margin: -98,291
- hybrid mean replay margin: -95,776
- hybrid worst replay margin: -187,610
- hybrid objective delta vs bootstrap: +0.1179

Search:
- generations: 8
- population: 256
- total games: 729,088
- parametric arena: ~5.6k–6.0k eps/s
- replay arena: ~8.6k–9.2k eps/s

## Why this is structural, not just “needs more CEM”

The controller's day-0 growth formula is `ramp = min(1, growth_speed * (day+1) / 10)`.

Even at maximum growth-speed parameter, the first-day livestock/crop targets are sharply capped. By contrast, the historical CR053 route immediately buys roughly 5 cows, 1 sheep, 18 wheat seeds and 1 melon seed and hires 7 workers on day 0, later scaling labour to 10–12/day and buying land on days 3 and 8.

The current controller therefore cannot even represent a known strong opening faithfully. Its deterministic task scheduler is also a different mechanical family from the route programs that routinely generate six-figure banks.

A second issue is optimization signal: with replay margins around -100k, the tanh margin terms in the hybrid objective are nearly saturated. Once replay win rate is 0%, CEM receives weak information about whether -95k is meaningfully better than -120k. Running a much longer search over the same representation would spend compute on a bad surface.

## Cross-check against historical exact evidence

CR092 previously evaluated CR053 against the same frozen replay families under exact kaggle-environments 1.32.7. CR053 was competitive:
- r01: 8/12 wins
- r02: 12/12 wins
- r03: 6/12 wins
- r06: 6/12 wins
- r07: 8/12 wins
- r09: 4/12 wins
- r10: 8/12 wins

Therefore the frozen replay benchmark is not intrinsically unbeatable. The new controller family is simply far below the known historical behavioural frontier.

## Strategic correction

Do not run another long CEM on the fixed 32-vector controller.

Preserve:
- exact kagsim parity
- L2 vector environment
- high-throughput native evaluation
- controller as a weak/randomized opponent family
- all searched vectors as diversity data

Next:
1. ingest the current public high-scoring frontier;
2. audit their actual source and route/mechanical structures rather than guessing from titles;
3. add those strategies to the league/demonstration corpus;
4. use strong trajectories as warm starts for state-conditioned search / policy-value training;
5. maintain the native parametric family only as exploiters/randomized opponents.

This follows the campaign rule: preserve proven knowledge; do not reinvent the wheel; novelty is only useful if it raises the probability of winning.
