# ALL3 V7 Option Composition Attribution — Result — 2026-09-19

## Binding execution

Workflow:
**`35479297555`**.

Mechanical:
- PASS;
- 4 frozen hard contexts;
- 8 exact static compositions per context;
- 32 exact episodes;
- zero failures;
- ALL3 replay reproduced all frozen hard-context margins exactly.

## Verdict

**`V7_STATIC_COMPOSITION_MARGIN_ONLY`**

No non-ALL3 composition converted any frozen ALL3 loss into a win.

By composition:

- ALL3: 0W / 4L, mean margin **-406.75**;
- TW_LQ2: 0W / 4L, mean **-399.75**;
- LQ2: 0W / 4L, mean **-420.5**;
- RW_LQ2: 0W / 4L, mean **-427.5**;
- RW_TW: 0W / 4L, mean **-1506.5**;
- TW: 0W / 4L, mean **-1499.5**;
- V47: 0W / 4L, mean **-1520.25**;
- RW: 0W / 4L, mean **-1527.25**.

Best alternative:
`TW_LQ2`, only +7 mean margin vs ALL3 and zero W/L rescue.

## Per-context interpretation

V47 mirror seed 75113 seat 1:
- ALL3 is the best of all 8 compositions;
- V47: -836;
- LQ2: -297;
- TW_LQ2: -270;
- ALL3: -263.

V48 seed 75103 seat 1:
- V47: -1875;
- LQ2: -64;
- TW_LQ2: -65;
- ALL3: -86.

V48 seed 75110 seat 0:
- V47: -2003;
- LQ2: -493;
- TW_LQ2: -463;
- ALL3: -484.

V48 seed 75113 seat 1:
- V47: -1367;
- LQ2: -828;
- TW_LQ2: -801;
- ALL3: -794.

## Interpretation

The four residual losses are **not caused by simply including RW1, TW1 or LQ2**.

LQ2 is the dominant value-producing mechanism:
- removing LQ2 worsens residual margins by roughly 1k+ in the V48 contexts;
- adding/removing RW1/TW1 only shifts margins modestly.

Therefore:
- close static option suppression as a W/L source;
- do not submit TW_LQ2 merely because it improves mean margin by 7 on four selected losses;
- focus next on residual LQ2 queue structure itself.

## Next gate

V8A — LQ2 Residual SELL-Run Census.

Question:
after LQ2 canonicalization, how often do the hard contexts still contain consecutive SELL runs with
>=2 distinct non-empty products, where execution order could matter?

If such states exist, open a bounded exact permutation oracle over those SELL runs.
If they do not, close cross-product SELL ordering as the residual mechanism.

No Kaggle submission is authorized by V7.
