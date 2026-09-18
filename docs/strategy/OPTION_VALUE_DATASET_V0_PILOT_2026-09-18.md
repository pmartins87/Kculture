# Option-Value Dataset V0 Pilot — 2026-09-18

## Purpose

Build the first unified counterfactual dataset for a state-conditioned option selector on
the hosted-faithful V47 backbone.

This pilot does **not** train a model and does **not** authorize a Kaggle submission.
It proves the data contract required for later Ryzen-scale value learning.

## Options

- `BASE`: exact hosted-faithful V47.
- `O-RW1`: one-shot `SELL WOOL 2` at the frozen ready-WOOL eligibility state.
- `O-TW1`: suppress current-turn `SELL WHEAT` at the frozen public town-WHEAT pulse state.

Both options are already frozen by independent causal/runtime gates. No thresholds or
definitions may change in response to this pilot.

## Feature contract

Runtime features come from `solver.value_features.encode_value_features()` plus a small
option-context block derived from the same legal observation/current exact V47 action.

Forbidden from model features:
- seed;
- opponent identity/name;
- submission/rating;
- EpisodeId;
- hidden RNG/future state;
- opponent-private inventory/shed/seeds;
- terminal reward.

Seed, seat and opponent key are retained as **offline metadata only** for stratification.

Each row contains:
- `state_hash`: hash of the legal agent-visible observation;
- `option_id`: O-RW1 or O-TW1;
- `features`: stable legal feature mapping;
- `base_action_key`: exact V47 action at branch;
- `base_score`, `option_score`, `score_delta`;
- `base_margin`, `option_margin`, `margin_delta`;
- offline metadata: seed, seat, opponent.

Primary training target is `score_delta`. Margin is secondary/diagnostic.

## Frozen pilot panel

Fresh seeds:
`69001,69002`.

Both seats.

Opponents:
1. exact V47 mirror;
2. exact V48;
3. Tactical Memory.

For each matchup:
1. discovery episode using exact hosted-faithful V47;
2. exact BASE replay parity;
3. branch O-RW1 at its first eligible state, if one exists;
4. branch O-TW1 at its first eligible state, if one exists.

Expected maximum:
12 matchups and up to 24 labeled option rows.

## Pilot PASS

Require all:
- exact V47 hosted entrypoint is `_y_agent_shopherd`;
- zero mechanical/runtime failures;
- 12/12 discovery-vs-BASE reward parity;
- every row feature key set exactly matches the frozen contract;
- every numeric feature finite;
- no forbidden metadata key appears inside `features`;
- at least 8 total labeled rows;
- at least 2 rows for each option.

A PASS validates the **dataset pipeline only**, not option strength.

## After PASS

Build a resumable multiprocessing Ryzen generator using the same schema, with:
- many fresh seeds;
- diverse opponent league;
- shard-per-seed checkpointing;
- no hosted submissions;
- output suitable for selector/value-model training.

Do not start a long Ryzen run until the pilot schema passes.
