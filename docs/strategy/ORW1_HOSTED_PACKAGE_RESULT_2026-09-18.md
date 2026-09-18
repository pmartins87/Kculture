# O-RW1 Hosted Package Gate Result — 2026-09-18

## Binding result

Workflow `35360173417`, artifact `10554278438`.

Candidate:
`KCULTURE_V47_ORW1_ONESHOT_V1.tar.gz`

Frozen archive SHA-256:
`b994e00d7adba05827eb8839b806211c2c8199dd0ad09a28b63815b58479c80f`

Candidate `main.py` SHA-256:
`f65be27b47839eb0cb6b44b217fc1edb33f63796bf5bc0bdd4f0bd311d3c2ff4`

O-RW1 wrapper SHA-256:
`34dfca26ebc0fa36163ed22028299dcfb70e42d6112e4ea6675a63cfad4079fc`

Exact V47 base:
- public handle:
  `ahmedberatozer/kaggriculture-v47-reactive-market-coordination`
- public output archive SHA:
  `08e56c43ecf28253605b61066dd769334d96262056b8cd337489f1f4f909ad01`
- exact base `main.py` SHA:
  `f4ecd4876fde93a14e3381993283f3b6a1afa023b48dd57217f4d90794d39842`.

## Packaging mechanics

The build is deterministic and the archive contains only:
- `main.py`
- `ATTRIBUTION.txt`.

The V47 source is downloaded transiently. It is not committed to the Kculture repository.
The builder appends only the frozen O-RW1 one-shot wrapper.

## Exact package parity

Fresh parity seeds: `66001,66002`.

Opponent blocks:
- exact V47;
- Tactical Memory.

Both seats.

Results:
- 8 paired package/reference comparisons;
- 16 complete episodes;
- 719 candidate action calls per episode;
- **exact action parity: 8/8**;
- **exact reward parity: 8/8**;
- failures: **0**.

Binding package verdict:
**`ORW1_HOSTED_PACKAGE_PASS_READY_FOR_PROBE_AUTHORIZATION`**.

## License / attribution audit

The exact packaged `main.py` retains the upstream source verbatim before the appended
wrapper. Direct inspection confirms:
- full Apache License 2.0 text is embedded in the source;
- an Apache-2.0 SPDX notice is present;
- the V47 attribution and modification notice is present;
- existing upstream attribution notices remain intact.

`ATTRIBUTION.txt` adds Kculture provenance for the O-RW1 modification.

## What this means

The candidate that passed the runtime transfer gate is now reproducibly packageable and
the actual submission archive has been proven action-for-action identical to the
reference implementation on fresh exact-engine games.

No further local retuning is required before a hosted sensor. A Kaggle hosted submission
now answers a genuinely different question: whether the +0.1875 offline W/L transfer of
O-RW1 survives the live population/rating environment.

The package gate does **not** automatically authorize a Kaggle submission.
