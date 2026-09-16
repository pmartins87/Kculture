# CR053 Adaptive Hands V1 — hosted sensor

## Why this exists

The seven frozen top-10 public replay tapes used in CR089 show a consistent labor regime that the FP001/C5 adaptive line did not implement. The top tapes average roughly 8.7–9.9 simultaneous farm hands per day and about 184–215 non-PASS hand actions per day. C5 explicitly used no routine HIRE and at most one crop hand per day.

Under the frozen Kaggriculture engine, HIRE resets daily and costs Fibonacci units with default multiplier 1, so the first nine hires cost only 88 total. This makes the labor-capacity gap structural rather than cosmetic.

CR053 itself already hires heavily (~10.6 max hands/day on its source tape) but follows a static replay tape. Its hand PASS fraction is ~11.3%, while top replay families such as r01/r06 are near 0–1% PASS.

## Candidate

- File: `R4D_CR053_ADAPTIVE_HANDS_V1.tar.gz`
- SHA256: `f528ba4d52baae7aad7376ef6b29ad45385cbbfe4a273ee70bd571d634da868e`
- Base CR053 package SHA256: `095080e791bd8d58369893c1a421beb57b7f64c2808c011f576e09684ffb9a15`

Intervention:
- preserve exact CR053 farmer action;
- preserve exact CR053 market order list and therefore its existing hiring schedule;
- preserve exact CR053 hand tape for the first 48 steps;
- after step 47, replace only hand actions with a deterministic adaptive dispatcher using own/public legal state;
- priorities: urgent FEED/WATER survival, then ordinary FEED/WATER, CARE, COLLECT_FERTILIZER, and mature/held-yield HARVEST;
- unique task reservations spread hands across targets;
- hands route to the shed and PICKUP WHEAT when required;
- no opponent identity, hidden seed, future state, or opponent-private input.

## Sanity only

This candidate is not promoted because of a local competitive score. Mechanical robustness checks only:
- compile PASS;
- import PASS;
- callable agent PASS;
- targeted synthetic task cases PASS;
- 5,000 randomized plausible observation calls, 0 exceptions;
- hand action cardinality matched observed hand count in all fuzz calls;
- market list remains base CR053 and <=10.

## Hosted purpose

This is a structural hosted sensor, not a micro market tweak. It asks whether replacing CR053's static worker execution with adaptive legal-state labor materially improves hosted performance while leaving its farmer and economy backbone unchanged.
