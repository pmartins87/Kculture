# ALL3 V22B Source-Unavailable Closure — 2026-09-21

## Exact status

V22B did **not** reach a valid exact strategic decision.

Exact evidence accumulated across the two mechanically compatible attempts:
- **356 / 368 exact (context, mode) keys**;
- **89 / 92 exact contexts**;
- **0 cross-attempt conflicts** among duplicated valid rows;
- exact missing contexts: `v22a_hard_059`, `v22a_hard_063`, `v22a_hard_067`;
- all three missing contexts belong to frozen rank-11 SHA
  `254eba4713f092e7bbdd6efe8b2b31ee8cf2873fcfbdf16ca7c530628a0f51ef`.

The current public ref `romantamrazov/kaggriculture-yummers` changed to SHA
`338a1a08fa612585e01ace53fbd9e83d294750e13d6f981739b174209a967080`.

## Historical recovery

Workflow: `35624010734`.

Attempted historical Kaggle versions `1..60`.
All were inaccessible through the authenticated Kaggle API (HTTP 403).
No other V22A ref was known to share the frozen rank-11 SHA.

Therefore the exact frozen bytes cannot currently be reacquired.

## Frozen sensitivity fallback

Protocol:
`docs/strategy/V22B_SOURCE_UNAVAILABLE_SENSITIVITY_CLOSURE_PROTOCOL_2026-09-21.md`.

Workflow: `35624589618`.

Outcome: **REJECTED**.

The current-source BASE replay failed all three missing contexts:

| Context | Frozen BASE margin | Current-source BASE margin |
|---|---:|---:|
| `v22a_hard_059` | -3061 | -3136 |
| `v22a_hard_063` | -3729 | -3789 |
| `v22a_hard_067` | -132 | -194 |

Thus:
- `base_replay_pass=false`;
- 0/12 sensitivity treatment rows are admissible;
- no imputation is allowed;
- no V22B decision label may be promoted from the incomplete aggregate.

## Important partial evidence

This evidence is recorded for diagnosis only and is **not** a V22B decision:
- among 89 exact contexts, FULL_SHADOW shows large positive headroom;
- MARKET_ONLY improvements were concentrated in one seed;
- PHYSICAL_ONLY improvements were also concentrated in one seed.

Because the three unavailable contexts could affect frozen seed-support criteria, the exact V22B router is not mathematically invariant to the missing rows.

## Closure decision

**`V22B_EXACT_ROUTING_INCONCLUSIVE_SOURCE_UNAVAILABLE`**

Per the pre-registered fallback rule:
- do not relax V22B thresholds;
- do not treat current-source rows as historical rows;
- do not create a V22B-derived option;
- refresh the current-frontier population under a new pre-registered block.

## Architectural lesson

The failure mode is not strategic but reproducibility-related: live third-party notebook refs can mutate between population discovery and upper-bound evaluation.

The successor block must eliminate this class of failure by preserving the exact acquired source bytes in an ephemeral workflow artifact and evaluating the domain upper bound from that immutable snapshot rather than reacquiring mutable refs later.

No Kaggle submission is authorized.
