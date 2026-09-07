# CR047 / CR048 — static-current and legacy-adaptive parent results

Date: 2026-09-07

## CR047 — current ~3000 winner tapes, massive fresh-seed screen

Workflow run: `34082452942`
Engine: bit-exact Kaggriculture `1.32.7` via kagsim
Panel: 4096 fresh seeds, both seats = 8192 games per candidate vs frozen CR029
Mechanical errors: 0
Decision: `CR047_NO_STATIC_TOP3000_TAPE_PROMOTION`

None of the eight exact 2026-09-06 top-winner trajectories passed the frozen gate.

Best by W/L was episode `106254763` seat 0:
- 3910 wins / 4282 losses
- score rate: 0.477294921875
- mean margin: -4658.0546875
- median margin: -1044

The other seven score rates were all lower. This confirms at high statistical power that the strength of the current ~3000 population is not contained in any one observed 719-action trajectory.

## CR048 — exact historical Rayk V11 adaptive package

Workflow run: `34082607111`
Candidate: `raykkretzschmar/kaggriculture-rank-your-agent/versions/11`
Archive SHA256: `99e3ab82275d1d6991553a50c67f7fb3c83c029072dab2e890155b34d34c3cc1`
main.py SHA256: `adc61ab15b3b4016e49efe525f4906e6ae3bbb66c4ff29ab795ae09df9fbaa5f`
Engine: bit-exact Kaggriculture `1.32.7`, L1 observations
Panel: 512 fresh seeds, both seats = 1024 games vs frozen CR029
Mechanical errors: 0

Result:
- wins: 0
- losses: 1024
- score rate: 0.0
- mean margin: -34769.041015625
- median margin: -36064.5
- p05: -50634
- p95: -19415

Decision: `CR048_DO_NOT_PROMOTE_RAYK_V11`

A historical high ladder score is not evidence that the package is a robust parent under the present broad distribution. V11 is retired as a parent candidate.

## Strategic consequence

Combined with the CR046A live-king x-ray (40 unique trajectories; ~84% weighted within-world trajectory variation; divergence from turn 2), these results force an architecture pivot:

1. stop promoting static tapes as primary agents;
2. stop treating historical ladder peaks as robust parents without broad fresh-seed evidence;
3. model the current live leader as a state-conditioned policy;
4. use public observation→action replay pairs for behavior cloning / policy inference;
5. use kagsim L1 for large fresh-seed evaluation of adaptive candidates.

CR049 is the first implementation of this track: a stepwise state-conditioned nearest-neighbor clone trained on 32 public episodes from the frozen live rank-1 submission and evaluated on 8 separate leader episodes plus fresh seasons vs CR029.

No Kaggle submission is authorized by CR047 or CR048.
