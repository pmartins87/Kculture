# KEXP-20260826-016 — R4D default-route public-context diagnostic

Status: **PREDECLARED / DEVELOPMENT ONLY**

## Why this experiment exists

KEXP-015 proved that a universal default-route mutation is the wrong abstraction.

On the exact 96-game modern development panel:

- frozen R4B baseline: 81-15, score 0.84375, mean +5720.5;
- default 8C/6S→10C/4S: 81-15, score 0.84375, mean +5908.542;
- default 8C/6S→6C/8S: 78-18, score 0.81250, mean +5700.260.

Within the 19 baseline-defined default 8C/6S exposure rows, 10C/4S improves mean margin from +1143.0 to +2093.105 but remains 12-7. On seed `163219477`, it flips both Rayk losses to wins while simultaneously flipping both Andrew wins to losses. This is direct evidence that the useful selector must react to legal public in-game context rather than apply one route to every default shop regime.

## Question

At the exact first state where the third shop is visible and frozen COK V8 would be in its default no-Yarn/no-milk branch, which small **public-state** features distinguish cases where 10C/4S is useful from cases where retaining 8C/6S is safer?

Opponent identity, seed identity, replay ID and hidden state are forbidden policy features.

## Diagnostic corpus

Use only the development seeds that produced baseline 8C/6S exposure in KEXP-014:

- `150614441`
- `1369296235`
- `393297156`
- `163219477`

Run both seats against each exact modern opponent family:

- Kaito V27 V4;
- Rayk V11;
- Andrew V12.

This is 4 seeds × 2 seats × 3 opponents = **24 baseline episodes**.

These seed IDs are an analysis sampling device only. No eventual agent may inspect them.

## Public snapshot to capture

At the first replay state where at least three shops are unlocked, record:

- exact first-three shop prefix;
- step/day/hour;
- both public farm tile-count vectors;
- COK-style L1 layout distance over cow, sheep, wheat, melon, strawberry and empty pasture;
- public money and labor counts;
- public actor positions/counts;
- shared town state;
- shared market state/prices.

The baseline episode continues normally to terminal only so the snapshot can be tied to its W/L/margin. KEXP-015 already provides paired terminal utility for the fixed route counterfactuals.

## Analysis rule

Join each `(opponent family, seed, candidate seat)` snapshot to the frozen KEXP-014/KEXP-015 paired outcomes.

Prefer the **smallest interpretable rule** that explains the direction of 10C/4S benefit without identity features. Candidate feature families, in priority order:

1. COK-style public production-layout distance;
2. simple signed differences in already-committed cow/sheep/crop tiles;
3. public money/labor divergence;
4. shared market-price or town-state terms only if simpler layout features cannot separate the interaction.

Do not fit a high-capacity classifier to 24 rows. This corpus is for causal feature discovery, not leaderboard-style training.

## Promotion boundary

KEXP-016 itself cannot promote a policy. It may only define a small contextual R4D rule.

Any contextual R4D candidate must then be tested from scratch on the full 16-development-seed × both-seat × Kaito/Rayk/Andrew panel. Only a full-panel development improvement can freeze a candidate for fresh validation.

## Leakage policy

- development: open;
- validation: closed for changed R4D code;
- held-out: sealed 32/32.
