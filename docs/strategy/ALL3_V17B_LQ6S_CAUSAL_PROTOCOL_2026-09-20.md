# ALL3 V17B STRAWBERRY First-Free SELL2 Causal Protocol — 2026-09-20

## Status

DORMANT / PRE-REGISTERED BEFORE V17A3 RESULT.

Activate only after the V17A3/V17A4 trigger chain resolves to:
`V17A4_STRAWBERRY_EDGE_TRIGGER_READY`.

## Candidate family

**O-LQ6S — W2 STRAWBERRY first-free SELL2**.

The runtime trigger is exactly the frozen V17A4-selected rising-edge trigger from `configs/all3_v17b_lq6s_trigger.json`.
No trigger mutation is permitted after V17A4.

Common action transformation:
- W2 only;
- exact ALL3 market must have no nonempty order, as required by every V17A3 trigger candidate;
- own total available STRAWBERRY >=2;
- insert `["SELL","STRAWBERRY",2]` at the semantic **first free market slot**:
  - replace the first explicit empty slot if present;
  - otherwise append at `len(market)`;
- preserve every other market order and quantity;
- preserve farmer/hands.

The treatment is **recurrent**: fire every time the selected legal trigger is true.
No one-shot state is added.

No exact-turn whitelist.
No source/opponent identity, seed, rating, replay metadata or future state.

## Discovery population

All 24 binding V13C hard contexts:
`configs/all3_v14a_hard_contexts.json`.

Paired:
- BASE exact ALL3;
- TREATMENT exact ALL3 + O-LQ6S.

Expected:
- 24 pairs;
- 48 episodes.

## Mechanical gate

PASS requires:
- 24/24 pairs;
- zero failures;
- BASE exact frozen score/margin reproduction;
- pre-first-fire parity;
- every treatment fire satisfies the frozen selected trigger;
- every fire in W2;
- every fire inserts exactly one SELL STRAWBERRY qty2 at first free slot;
- no unrelated market edit;
- no physical action change.

## Strategic gate

Coverage requires:
- fires in all 24 hard contexts;
- fires span all 10 hard-source SHAs.

**`V17B_LQ6S_WL_HEADROOM`** iff:
- mechanical PASS;
- coverage PASS;
- loss-to-win flips >=4;
- flips span >=2 source SHAs;
- mean score delta >0;
- mean margin delta >0.

If coverage passes but W/L threshold fails and mean margin delta >0:
**`V17B_LQ6S_MARGIN_ONLY_CLOSE`**.

If mean margin delta <=0:
**`V17B_LQ6S_NO_HEADROOM_CLOSE`**.

Mechanics failure:
**`V17B_MECHANICS_INVALID`**.

## Fresh validation if PASS

Only `V17B_LQ6S_WL_HEADROOM` may activate V17C.

V17C frozen population:
- same 10 exact hard-source SHAs;
- fresh seeds `78401,78402,78403,78404`;
- both seats;
- BASE vs unchanged O-LQ6S;
- 80 paired contexts.

Fresh PASS requires:
- all 80 pairs mechanically clean;
- treatment fires in >=20 contexts;
- >=2 positive-score contexts;
- mean score delta >0;
- zero negative-score contexts;
- zero BASE-win -> treatment-nonwin regressions;
- mean margin delta >=0.

No candidate change after V17B.

No Kaggle submission.


### Activation amendment

The original dormant V17B protocol anticipated a directly compressible stateless V17A3 trigger.
V17A3 closed stateless triggers as non-compressible, and the pre-frozen V17A4 rising-edge audit then produced
`V17A4_STRAWBERRY_EDGE_TRIGGER_READY`.

This amendment changes only the trigger state semantics from stateless to the exact frozen V17A4 rising edge.
The STRAWBERRY action transformation, discovery population, strategic PASS gate, and V17C validation population/seeds remain unchanged.
