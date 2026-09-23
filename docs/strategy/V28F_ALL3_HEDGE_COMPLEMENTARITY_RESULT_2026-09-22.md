# V28F — ALL3-Centered Hedge Complementarity Result — 2026-09-22

## Binding workflow

- workflow: `35807910104`
- conclusion: **SUCCESS**
- aggregate job: `107025823116`
- final artifact: `10729759999`
- artifact digest: `sha256:489a910097a36dd16bc5b6574d94a6aa50c2f3b7686be1fccb25ea41420145ec`

## Mechanical validity

**PASS**.

- fresh frontier sources: **12**
- contexts per candidate: **144** = 12 sources x 6 seeds x 2 seats
- candidates: ALL3, V47, O-RW1, exact CR053, exact CR029
- failures: **0**
- all four benchmark shards: SUCCESS
- immutable snapshot used; no live reacquisition inside benchmark episodes

## Primary result

ALL3:
- 78 wins / 0 ties / 66 losses
- score rate: **0.5416666667**
- mean margin: **+168.0417**

## Hedge results

| Hedge | W-L | Standalone score rate | Mean margin | ALL3 nonwin -> hedge win | Complement source breadth | Best-of-two pair score |
|---|---:|---:|---:|---:|---:|---:|
| V47 | 74-70 | 0.5138888889 | +91.0556 | **0** | **0** | 0.5416666667 |
| O-RW1 | 74-70 | 0.5138888889 | +91.2083 | **0** | **0** | 0.5416666667 |
| CR053 | 4-140 | 0.0277777778 | -10561.0694 | **0** | **0** | 0.5416666667 |
| CR029 | 0-144 | 0.0 | -24766.6111 | **0** | **0** | 0.5416666667 |

The lower-order frozen selector ranks O-RW1 first because its standalone mean margin is only slightly larger than V47's after all higher-order complementarity criteria tie. This does **not** pass the material replacement rule.

## Binding decision

**`V28F_NO_MATERIAL_HEDGE_REPLACEMENT`**

Material replacement gate:
**FAIL**.

Most important structural finding:

> On this fresh current-frontier panel, none of V47, O-RW1, CR053, or CR029 converted even one ALL3 non-win into a win.

Because there were no ties, the 66 ALL3 losses received **zero hedge-win rescue** from every tested lineage.

Thus:
- replacing V47 with O-RW1 would not improve pair coverage on this panel;
- CR053 and CR029 are decisively noncompetitive as direct hedges here;
- the currently available second-slot candidates are outcome-redundant with ALL3 on its residual losses.

## Strategic interpretation

The next useful problem is no longer "which preserved hedge should replace V47?" It is:

**what structural regimes generate ALL3's 66 residual losses, and what genuinely orthogonal policy family could win some of those contexts?**

The second-slot research target should therefore be discovered from ALL3 residual-loss anatomy, not by recycling historical agents whose wins are already contained inside ALL3's win set.

## Slot decision

Preserve active Kaggle pair:
- primary ALL3 `56367770`;
- hedge exact V47 `56466970`.

No Kaggle mutation is authorized by V28F.
