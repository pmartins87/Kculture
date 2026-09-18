# Programme Adaptive Expert Gate — 2026-09-18

## Purpose

Decide whether the frozen single-decision programme router deserves any further work as
a standalone candidate. The previous fixed-tape panel was neutral, so this gate replaces
static opponents with two complete current public adaptive agents while keeping the
router frozen.

This is a benchmark gate, not a Kaggle submission and not a claim about leaderboard
rating.

## Frozen treatments

Control:
- modern public programme bank recovered from the exact V47 package;
- programme 15 for the complete episode.

Treatment:
- the exact same programme 15 up to checkpoint 144;
- the already-frozen depth-4 observation-only router from
  `ROUTER_EPISODE_GATE.json`;
- no retraining, threshold tuning, feature changes, or opponent-specific branch logic.

The router may select only the prefix-compatible members already frozen in the prior
teacher result.

## Adaptive opponents

Two independent public lineages from the 2026-09-18 score-descending Top-30 snapshot:

1. Modern V47:
   `ahmedberatozer/kaggriculture-v47-reactive-market-coordination`
   expected packaged `main.py` SHA-256
   `f4ecd4876fde93a14e3381993283f3b6a1afa023b48dd57217f4d90794d39842`.

2. Legacy V39:
   `ahmedberatozer/kaggriculture-v39-ready-before-the-rush`
   expected packaged `main.py` SHA-256
   `708c7485fa964853b193f175dcd83020602c005e159ce82e38dc350b22e970c8`.

Third-party code is downloaded transiently and used only as an opponent. The workflow
persists hashes/results, not the third-party source.

## Evaluation

- official `kaggle-environments==1.32.7`;
- seeds 61001 through 61016;
- both seats;
- both treatments on every expert/seed/seat matchup;
- 64 paired matchups / 128 complete episodes;
- W/L score rate is primary;
- paired final-bank margin is secondary.

Any source-identity mismatch, runtime error, incomplete episode, or missed router
checkpoint invalidates the gate.

## Frozen decision rule

Promote the standalone router to a hosted-candidate gate only if all are true:

- overall router W/L score-rate improvement is at least +0.0625;
- mean paired margin delta is positive;
- neither expert block regresses by more than 0.03125 W/L.

Otherwise close the standalone router candidate. Do not tune the tree against the
result. The next architecture becomes bounded transaction/market proposal search on top
of strong adaptive programmes, using the exact simulator to choose local interventions.

## Branches

PASS for standalone router:
- package a runtime-safe router candidate;
- run one hosted sensor against the exact static control.

FAIL/neutral:
- preserve programme-router infrastructure as a proposal/routing component;
- extract only legally reusable transformation ideas;
- build bounded market-order / transaction proposals;
- exact-evaluate proposals from live compatible states;
- distill proposal/value decisions rather than reopening fixed-controller CEM.
