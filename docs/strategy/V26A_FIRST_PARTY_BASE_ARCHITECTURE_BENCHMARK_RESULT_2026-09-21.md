# V26A First-Party Base Architecture Benchmark — Result — 2026-09-21

## Binding result

Workflow: **`35653189539`**  
Aggregate job: `106517283200`  
Final artifact: `10664405274`  
Digest: `sha256:a43451c248c92eff000d624690cdba4233f9777106f45e496541d6c168c953c9`

Snapshot:
- current public Top-30 queried once;
- 0 unavailable refs;
- 0 smoke failures;
- 12 unique executable representatives selected;
- exact V47 base + selected opponents frozen in immutable artifact `10663530412`;
- snapshot digest `sha256:69f6407c34155af19671963c1ce107fab45926283098b422790cd1d86117ed43`.

Mechanical:
- 4/4 benchmark shards PASS;
- 144 paired contexts;
- 0 failures;
- fresh seeds `79501..79506`;
- both seats;
- immutable snapshot only.

Decision:

**`V26A_PRIZE_SOLVER_BASE_NOT_READY`**

## Competitive result

CONTROL — exact V47+ALL3:
- score rate: **0.3611111**.

TREATMENT — PrizeSolverV4:
- score rate: **0.0**.

Paired:
- positive-score contexts: **0/144**;
- negative-score contexts: **52/144**;
- neutral: 92/144;
- CONTROL-win -> TREATMENT-nonwin: **52**;
- mean score delta: **-0.3611111**;
- mean margin delta: **-135390.7847**;
- positive source SHAs: 0;
- positive fresh seeds: 0;
- positive functional clusters: 0.

The frozen architecture-headroom gate fails every positive-support requirement.

## Interpretation

PrizeSolverV4 is architecturally cleaner than replay hybrids, but in its current heuristic form it is not a competitive base.

Do not:
- scale PS2 rollout generation;
- train PS3/value models merely to rescue V4;
- submit V4 to Kaggle;
- replace ALL3 with V4;
- tune V4 parameters from this benchmark.

Per the pre-registered router:
activate **V26B teacher-derived persistent-policy reconstruction viability**.

V26B is allowed to test only one source-agnostic persistent consensus policy from the same immutable V26A frontier snapshot.

No Kaggle submission is authorized.
