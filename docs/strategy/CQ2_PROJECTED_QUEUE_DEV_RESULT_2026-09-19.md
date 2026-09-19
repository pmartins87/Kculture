# O-CQ2 Projected Queue Development Matrix — Result — 2026-09-19

## Binding run

Workflow: **`35440530160`**  
Head: `31ecc13aed94eaf691eb1dc3eb4c17a8a697bed8`  
Artifact: `10583303637`  
Artifact digest: `sha256:a3f2c1b3b33c4f92c226d0681c6275a57715cc3ff67868f866a53e5d2905624c`.

Mechanical PASS:
- 8 development episodes;
- 5,752 V47 decisions;
- zero failures;
- same frozen scientific grid as the earlier corrected run;
- cached projection only changed execution efficiency.

The prior corrected-count run `35440396122` independently produced the **identical ranking and metrics**,
confirming that caching did not change the experiment.

## Binding decision

**`CQ2_DEV_WEAK_USE_V4A`**

Best configuration:
- mode: **`slot_projected`**;
- `min_step=336`;
- exact V48 divergence matches: **424 / 488**;
- recall: **0.8688525**;
- precision: **0.5273632**;
- F1: **0.6563467**;
- false-positive changes: **332**;
- changed-but-not-exact: **48**;
- missed V48 changes: **16**;
- whole-action accuracy: **0.9311544**.

Runner-up:
- `slot_projected`, min_step 432;
- precision 0.569697;
- recall 0.770492;
- F1 0.655052.

## Interpretation

Projecting same-turn shed mechanics fixed much of CQ1's recall problem, but precision remains too low.
The remaining gap is not a small threshold error:
- the best configuration still rewrites hundreds of states that exact V48 leaves untouched;
- the top several configurations trade precision for recall but remain below the pre-registered
  PROMISING gate of 0.60 / 0.60;
- choosing another threshold after seeing this matrix would be post-hoc fitting.

Therefore:
- **do not freeze a CQ2 candidate**;
- **do not run the untouched CQ2 validation**;
- **do not run a causal CQ2 W/L gate**.

The pre-registered fallback is activated: targeted bounded V48 multi-turn market oracle **V4A**.

## Next experiment

Use the already-prepared V4A implementation unchanged:
- fresh seeds `74001..74006`;
- both seats;
- exact V47 physical actions preserved;
- first three replay-verified V47/V48 market divergences per hard context;
- horizons 1, 2 and 3 turns;
- exact V47 resumes after the bounded intervention.

The purpose is to establish whether V48's advantage requires a short **sequence** of market rewrites rather
than a compact one-state sanitizer.

No Kaggle submission is authorized by CQ2.
