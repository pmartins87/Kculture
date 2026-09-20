# ALL3 V8C Local Priority Value Atlas — Result — 2026-09-20

## Binding execution

Workflow: **`35516167350`**  
Head: **`b528ac9dafedefd17b65dfa7407b1b793adb6046`**

Mechanical:
- PASS;
- 4 frozen hard contexts;
- 46 baseline-discovered one-shot branch states;
- expected branch states: 46;
- failures: 0.

## Verdict

**`V8C_CONDITIONAL_ORDER_HEADROOM_NARROW`**

Aggregate:
- loss->win flips: **1**;
- positive-margin states: **6** across **4/4** hard contexts;
- negative-margin states: **37**;
- mean margin delta: **-113.1522**.

The global O-LQ3 direction is therefore highly unsafe in general, but there is one repeated local state family with real causal value.

## Strongest repeated state

Two independent frozen V48 hard contexts share the same structural post-LQ2 market shape:

- exactly **4 SELL** orders;
- exactly **6 HIRE** orders;
- **0 BUY** orders;
- no other nonempty market operation;
- MILK, WOOL and FERTILIZER all present in the SELL run;
- O-LQ3 changes their relative order.

Results:

1. V48 75103 / seat 1 / turn 600:
   - base -86;
   - conditional one-shot +10;
   - margin delta +96;
   - **LOSS -> WIN**.

2. V48 75110 / seat 0 / turn 600:
   - base -484;
   - conditional one-shot -220;
   - margin delta +264;
   - still LOSS.

No other V8C state had this exact 4-SELL + 6-HIRE structural signature.

## Frozen first-party candidate O-LQ3C

Eligibility is intentionally structural rather than opponent-, seed-, step- or price-specific:

1. start from exact ALL3 post-LQ2 market;
2. O-LQ3 must actually change a SELL run;
3. nonempty market must consist of exactly:
   - 4 SELL;
   - 6 HIRE;
   - 0 BUY;
   - 0 other operations;
4. MILK, WOOL and FERTILIZER must all be present among the SELL orders.

Treatment:
- apply the unchanged O-LQ3 stable priority `MILK -> WOOL -> FERTILIZER`;
- preserve quantities;
- preserve non-target SELL slots;
- preserve all HIRE slots;
- preserve farmer/hands;
- ALL3 resumes normally next turn.

No opponent identity, seed, rating, EpisodeId, future state or opponent-private state is used.

## Required next gate — V8D

Fresh paired validation only.

Population:
- V48;
- V47 mirror;
- Ready Stock.

Fresh seeds:
- `76001..76012`;
- both seats.

Pass requires:
- mechanical PASS;
- sufficient rule activation;
- >=1 positive W/L context against V48 and positive V48 mean score delta;
- **0 win->nonwin regressions overall**;
- **0 negative-score contexts** in V47 mirror and Ready Stock controls.

Margin-only evidence cannot pass.

No automatic Kaggle submission.
