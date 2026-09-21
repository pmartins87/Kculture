# ALL3 V19C O-TM1 Fresh Validation — Binding Result — 2026-09-21

Workflow: **`35556749095`**.

Decision:
**`V19C_CONSENSUS_FRESH_FAIL_CLOSE`**.

## Mechanical

- 80/80 frozen paired contexts;
- failures: 0;
- changed-market coverage: 80/80;
- exact binding V19A schedule SHA256:
  `c68d857500b71a40f8cf4ef5f2ff693f6da1d97ced03e7d7f19eaedfded1ff22`.

## Strategic

- positive-score contexts: **10/80**;
- positive-score source SHAs: **5**;
- negative-score contexts: **10/80**;
- BASE-win -> treatment-nonwin regressions: **10**;
- mean score delta: **0.0**;
- mean margin delta: **-241.6375**.

## Regime structure

The fresh effect is strongly seed/regime dependent rather than source-identity dependent:

- seed 78601: 0 positive / 0 negative score changes; mean margin positive;
- seed 78602: **10 negative score contexts**, 0 positive;
- seed 78603: **10 positive score contexts**, 0 negative;
- seed 78604: 0 positive / 0 negative score changes.

Across sources, the sign reverses relative to the hard-context discovery set: several source families that benefited under V19B regress under fresh seed 78602, while previously non-flipping families improve under 78603.

Binding interpretation:
- global unconditional O-TM1 is closed;
- do not activate V19D package parity;
- do not activate V19E hosted submission;
- do not tune the schedule using V19C outcomes.

V19C may nominate a new architecture only: an identity-free **state-conditioned gate** deciding whether to activate the frozen schedule. Any such gate must be discovered on new seeds and validated on another untouched seed set.

No Kaggle submission.
