# V26B Persistent Teacher-Consensus Viability — Result — 2026-09-21

## Binding result

Workflow: **`35660845547`**  
Aggregate job: `106542706979`  
Final artifact: `10667886918`  
Digest: `sha256:c47ebfcb406f6077165a0b1779ede2a2060a283f9476d79129feb36e2207132e`

Mechanical:
- 4/4 shards PASS;
- 144/144 paired contexts;
- 0 failures;
- 12 frozen teachers from the immutable V26A snapshot;
- no live Kaggle source reacquisition.

Decision:

**`V26B_NO_SOURCE_AGNOSTIC_POLICY_HEADROOM`**

## Paired result

CONTROL = exact V47+ALL3.  
TREATMENT = persistent modal complete-action consensus of all 12 frozen teachers.

- CONTROL score rate: **0.3472222**;
- CONSENSUS score rate: **0.1527778**;
- mean score delta: **-0.1944444**;
- mean margin delta: **-2131.0833**;
- positive-score contexts: **2/144**;
- negative-score contexts: **30/144**;
- CONTROL-win -> CONSENSUS-nonwin regressions: **30**;
- positive source SHAs: **1**;
- positive seeds: **1**;
- positive CONTROL functional clusters: **1**.

Consensus support itself was high:
- mean modal support: **9.925 / 12 teachers**;
- minimum modal support observed: 3.

Thus the failure is not lack of voting consensus. The modal policy is simply not a source-agnostic competitive policy.

## Consequence

Per the frozen V26B protocol:

- close current multi-teacher source-agnostic imitation;
- do not reweight teachers after outcomes;
- do not drop weak teachers post-hoc;
- do not route by opponent identity;
- do not return to ALL3 option mining;
- do not brute-force train PrizeSolverV4.

The next solver work, if any, must use a genuinely different learning/search architecture.

Current hosted preservation facts:
- strongest exact project-hosted anchor remains CR053_REAL, submission `56073870`, historical checkpoint ~2064.8;
- current preserved hosted pair remains O-RW1 `56336027` and ALL3 `56367770` until a deliberate final-slot decision.

Next research block:
**V27A — rank-1 teacher statefulness / Markov reconstructibility audit.**

No Kaggle submission is authorized.
