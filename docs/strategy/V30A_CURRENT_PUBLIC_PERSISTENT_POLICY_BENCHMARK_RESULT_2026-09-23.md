# V30A — Current Public Persistent Policy Benchmark Result — 2026-09-23

## Binding result

Workflow: `35877442921`

Decision: **`V30A_PUBLIC_PERSISTENT_POLICY_CANDIDATE_READY`**

Mechanics: **PASS**. The workflow completed successfully with zero episode failures. The immutable current public-policy snapshot contained 12 executable SHA-unique representatives; ALL3 plus all 12 candidates were evaluated on the identical 12-opponent panel, seeds `80501..80504`, both seats, for 96 contexts per candidate.

No Kaggle submission, deletion, or slot reordering occurred.

## Frozen selector winner

Selected public persistent policy:

- Kaggle public ref: `arsgorynich/herd-safe-v3-experimental-risk-aware-feed`
- representative public-kernel rank in the frozen V30A snapshot: **14**
- exact `main.py` SHA-256: **`4f8637a3e33348b98f531de246d353f5d2955b2f85480e3fd02bf4a7874f0d01`**
- V30A score rate: **0.9166666667**
- paired score delta versus ALL3: **+0.3333333333**
- paired mean margin delta versus ALL3: **+3932.5104167**
- paired median margin delta: **+3821.0**
- positive / neutral / negative paired contexts: **34 / 62 / 0**
- positive opponent-source breadth: **5**
- positive seed breadth: **4/4**
- positive support: **both seats**

The candidate passed every preregistered promotion condition and won the frozen selector by highest score rate. Four candidates were promotion-eligible; the selector was not changed after outcomes.

## Binding route

Per the preregistered V30A protocol, preserve the exact public ref/SHA/package provenance and launch exactly one independent **V30B** fresh closed-loop validation/package-parity gate. V30B must use fresh seeds and a separately acquired fresh immutable frontier, verify reacquired candidate `main.py` SHA exactly equals the V30A selected SHA, compare the exact public policy directly against ALL3, and require multi-source/multi-seed evidence. V30B remains offline only.

Protected hosted pair remains exact V47 submission `56466970` + ALL3 submission `56367770`. Any Kaggle slot mutation requires new explicit user authorization.