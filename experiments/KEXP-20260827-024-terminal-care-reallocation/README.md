# KEXP-20260827-024 — terminal CARE reallocation

Status: **PREDECLARED / DEVELOPMENT ONLY**

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
