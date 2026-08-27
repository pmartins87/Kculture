# KEXP-20260827-024 — terminal CARE reallocation

Status: **COMPLETE / NO PROMOTION**

## Prize-first hypothesis

Frozen-engine inspection proves that the end-of-day refresh after executable step 695 is the final animal production refresh. `CARE` issued during steps 672..695 creates its `pending_care_bonus` only after that production check and therefore cannot generate terminal-season product.

The official live-meta top band independently shows that current high-Elo winners use essentially zero CARE in this interval, while frozen COK routes still schedule roughly 8–10 CARE actions depending on route. This is supporting external evidence, not the policy rule.

Official engine mechanics also prove that `HARVEST` on an animal tile transfers all currently held `yield_units` to the acting unit's inventory and resets the tile to zero, which can free `max_held` capacity before the final step-695 production refresh.

## Candidate

`candidates/r4d_terminal_care_reallocate.py`

The candidate delegates to frozen `R4B-market-only-validated-v1` and changes **one mechanism only** during steps 672..695:

- if a base physical action is `CARE` and the current animal tile has `yield_units > 0`, replace with `HARVEST`;
- else, if that animal tile has `fertilizer_available`, replace with `COLLECT_FERTILIZER`;
- else replace with `PASS`.

Everything else is unchanged, including FEED, movement, route selection, planting, other harvests, market orders, and the validated step-718 market-only liquidation.

No seed ID, opponent identity, episode identity, or future information is used.

## Development screen

Exact frozen modern public panel, all 16 development seeds × both seats:

- Kaito V27 V4;
- Rayk V11;
- Andrew V12.

Baseline R4B to beat:

- Kaito: 25-7;
- Rayk: 30-2;
- Andrew: 26-6;
- combined **81-15 / 96**, score 0.84375.

Also run a direct candidate-vs-R4B screen on the same 16 development seeds × both seats.

## Gate

Mandatory:

1. zero execution errors;
2. no reduction in wins against any of the three modern families;
3. combined modern-panel W/L must improve beyond 81-15 to justify promotion on this panel; money delta is secondary only;
4. direct candidate-vs-R4B score must be >= 0.50 and mean terminal delta >= 0.

If the candidate is mechanically sound but merely ties 81-15 while improving money, record `NO PROMOTION` and treat it only as a possible component for a later adaptive architecture. Do not spend validation or a hosted submission on money-only improvement.

Validation and all 32 held-out seeds remain closed.

## Result

GitHub Actions run: **33037860772 — SUCCESS**.
Artifact: `kexp024-terminal-care-reallocation`, artifact id **9633112705**, SHA-256 `f32ae2b1c87617bdd7d2ab8a81f25b9e499241a44dc42e88df1dcc83b23be9b5`.

Modern public panel:

| Opponent | W-L-T | Errors | Score rate | Mean terminal delta |
|---|---:|---:|---:|---:|
| Kaito V27 | 25-7-0 | 0 | 0.78125 | +4396.84375 |
| Rayk V11 | 30-2-0 | 0 | 0.93750 | +7477.21875 |
| Andrew V12 | 26-6-0 | 0 | 0.81250 | +5287.43750 |
| **Combined** | **81-15-0** | **0** | **0.84375** | — |

Direct candidate-vs-R4B:

- **12-12-8**;
- score rate **0.50000**;
- mean terminal delta **0.0**;
- zero execution errors.

## Decision

The candidate satisfies the safety/family-preservation/direct-neutrality parts of the gate, but **fails the required W/L improvement**: the modern panel remains exactly **81-15**, identical to R4B.

Therefore: **NO PROMOTION**. Do not open validation, do not access held-out, and do not spend a Kaggle submission on this mechanism alone.

The experiment still establishes a useful architecture fact: terminally useless CARE can be reallocated without degrading the frozen modern panel, but this isolated mechanism has insufficient prize-relevant ceiling. Future animal work should target a resource-bearing decision such as selectively avoiding terminally worthless FEED while preserving survival, payable care bonuses, inventory capacity and final liquidation.
