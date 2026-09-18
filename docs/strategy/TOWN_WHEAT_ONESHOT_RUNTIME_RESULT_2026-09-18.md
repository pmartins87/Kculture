# O-TW1 Autonomous Runtime Result — 2026-09-18

Workflow `35395548699`, artifact `10569241095`, exact engine `1.32.7`.

## Binding result

Treatment:
at the first runtime-legal public town-WHEAT pulse where exact hosted-faithful V47 wants
to sell already-owned WHEAT, suppress only those current-turn SELL WHEAT orders once.
Exact V47 resumes immediately afterward.

Fresh panel:
- seeds `68001..68008`;
- both seats;
- V47 mirror, V48, Tactical Memory, Ready Stock;
- 64 paired matchups / 128 complete episodes.

Results:
- BASE score rate: **0.6250**;
- O-TW1 score rate: **0.71875**;
- score delta: **+0.09375**;
- **14 non-win -> win flips**;
- **0 win -> non-win regressions**;
- 14 positive-score pairs;
- 2 negative-score pairs;
- 48 neutral-score pairs;
- mean margin delta: **+9.28125**;
- median margin delta: **+18**;
- trigger rate: **100%**.

By opponent:
- V47 mirror: `0.500 -> 0.875`, delta **+0.375**;
- V48: W/L neutral;
- Tactical Memory: W/L neutral;
- Ready Stock: W/L neutral.

All four opponent blocks had nonnegative mean W/L delta; worst block = 0.0.

Binding verdict:
**`TOWN_WHEAT_RUNTIME_PASS`**.

## Interpretation

O-TW1 survives the autonomous runtime gate on fresh seeds and therefore becomes a second
independent causal option in the offline V47 option library alongside O-RW1.

The two negative-score pairs are tie->loss regressions in V47 mirror; there were no
win->nonwin regressions. Do not describe O-TW1 as monotone or universally safe.

No Kaggle submission is authorized. The next stage is unified state-conditioned
option-value data generation and selector/value learning.
