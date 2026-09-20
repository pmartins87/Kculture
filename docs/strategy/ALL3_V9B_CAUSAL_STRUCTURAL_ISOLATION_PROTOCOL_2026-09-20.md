# ALL3 V9B Causal Structural Category Isolation Protocol — 2026-09-20

## Source

V9A binding workflow `35517515758` returned `V9A_STRUCTURAL_RESIDUAL_READY`:
- 233 residual market divergences;
- 161 INSERT_DROP;
- 63 QTY_UP;
- 9 REORDER_ONLY;
- structural residuals in 4/4 hard contexts;
- zero physical divergences.

## Frozen state selection

Selection is frozen before any V9B causal outcome.

Use exactly 16 states from `configs/all3_v9b_representative_states.json`:

1. earliest structural residual in each hard context (4 states);
2. repeated INSERT_DROP at turn 337 in all four contexts (4);
3. repeated QTY_UP at turn 427 in all four contexts (4);
4. repeated late QTY_UP at turn 698 in all four contexts (4).

Rationale:
- both dominant categories covered;
- all hard contexts covered;
- earliest + repeated signatures;
- temporal separation;
- no state selected using causal treatment outcome.

## Causal branch

For each frozen state:
- base = exact ALL3;
- treatment follows exact ALL3 until target turn;
- exact V48 shadow is evaluated on every candidate observation solely as offline proposal source;
- treatment applies only the selected semantic category for exactly one turn;
- next turn resumes ALL3.

### QTY_UP isolation

Preserve:
- farmer;
- hands;
- market slot positions;
- operation/product signatures;
- non-target quantities.

Only SELL quantities for which V48 proposes a larger quantity are raised to the V48-shadow quantity.

### INSERT_DROP isolation

For the frozen INSERT_DROP states, apply the exact V48 shadow market structural insertion/drop for that one turn after verifying the live category is still INSERT_DROP and physical action is identical.

The selected states are simple insert/drop or split-insertion states; non-market physical actions remain unchanged.

## Mechanical requirements

- all 16 branches complete;
- base replay exactly matches frozen context score/margin;
- pre-target action parity;
- live target category matches frozen category;
- branch fires exactly once;
- zero failures.

## Frozen strategic gate

Primary target: LOSS -> WIN.

For each category separately:

- loss->win in >=2 distinct hard contexts:
  **`V9B_CATEGORY_WL_REPEATABLE`**;
- exactly one loss->win, with positive margin deltas in >=2 distinct contexts for the same category:
  **`V9B_CATEGORY_WL_NARROW`**;
- otherwise, if there is no loss->win in any branch:
  **`V9B_NO_WL_HEADROOM_CLOSE_ONE_TURN_STRUCTURAL`**.

If a single loss->win occurs without the supporting multi-context margin condition:
**`V9B_SINGLE_FLIP_UNSUPPORTED`** and close this one-turn structural family rather than tune state thresholds.

Margin-only evidence with zero W/L flips cannot advance.

If repeatable/narrow passes, the next step must derive at most one opponent-independent public-state semantic rule for the winning category and validate it on untouched seeds before any hosted candidate.

No automatic Kaggle submission.
