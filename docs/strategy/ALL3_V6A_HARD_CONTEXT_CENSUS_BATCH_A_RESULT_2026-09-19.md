# ALL3 V6A Hard-Context Census — Batch A Result — 2026-09-19

## Binding run

Corrected workflow:
**`35472777632`**.

The earlier run `35472681958` is non-binding mechanical-invalid because the module-purge helper
received a directory where it expected a list of agent paths. The correction changed only cleanup
mechanics; seeds, opponents and evaluation remained frozen.

## Result

Decision:
**`V6A_EXPAND_HARD_CENSUS`**.

Mechanical:
- PASS;
- 112/112 exact-engine games;
- zero failures.

Aggregate:
- **111 wins**;
- **1 loss**;
- 0 ties.

By opponent:
- V47 mirror: 16-0, min margin +238;
- Ready Stock: 16-0, min +773;
- V48: **15-1**, min -86;
- router_2715: 16-0, min +5,888;
- Conditional Memory: 16-0, min +35,037;
- Tactical Memory: 16-0, min +31,156;
- Best Market: 16-0, min +23,572.

Only fresh hard context:
- opponent: V48;
- family: modern41_queue;
- seed: `75103`;
- seat: `1`;
- terminal margin: **-86**.

## Interpretation

ALL3 is extremely strong on this exact local seven-family panel, but the census has not yet supplied
enough non-winning trajectories for the predeclared V6 continuation discovery gate.

Close wins — especially V48 and V47 margins near zero — remain diagnostics only and cannot replace
actual non-wins.

Per protocol, open an untouched Batch B:
`75109..75116`, both seats, same seven opponents.

Do not run V6 until the combined frozen hard-context pool reaches at least 4 non-wins.
