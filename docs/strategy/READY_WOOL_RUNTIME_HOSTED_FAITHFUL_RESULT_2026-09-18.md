# O-RW1 Hosted-Faithful Runtime Transfer Result — 2026-09-18

## Binding result

Workflow `35367785929`, artifact `10558221804`, exact engine `1.32.7`.

Loader contract:
`kaggle_environments.agent.get_last_callable`.

Exact public V47 hosted entrypoint:
`_y_agent_shopherd`.

Mechanical PASS:
- 64 paired matchups / 128 complete episodes;
- zero failures;
- pre-trigger observation/action parity passed;
- O-RW1 triggered once in every treatment episode;
- trigger steps: 151, 153 or 155.

Primary W/L result:
- BASE score rate: **0.6250**;
- V47 + O-RW1 score rate: **0.71875**;
- delta: **+0.09375**;
- **14 non-win -> win flips**;
- **0 win -> non-win regressions**;
- 14 positive-score pairs;
- 2 negative-score pairs;
- 48 neutral-score pairs.

Per opponent:
- V47 mirror: `0.500 -> 0.875`, delta **+0.375**;
- V48: `0.000 -> 0.000`, W/L neutral;
- Tactical Memory: `1.000 -> 1.000`, W/L neutral;
- Ready Stock: `1.000 -> 1.000`, W/L neutral.

All four opponent blocks had nonnegative mean score delta. Worst block delta was 0.0.

Binding verdict:
**`READY_WOOL_RUNTIME_PASS`**.

## Important correction versus the pre-entrypoint run

The old runtime run reported `0.500 -> 0.6875` (+0.1875) using the wrong public-agent
loader. It is superseded for promotion purposes.

The hosted-faithful runtime effect is roughly half as large:
`+0.09375`.

O-RW1 is also **not universally safe**:
- seed 65008 versus V47 mirror produced two tie->loss regressions (one per seat);
- however, there were no win->nonwin regressions;
- the block-average V47 delta remained strongly positive.

Money margin is again diagnostic only:
- mean margin delta: **-805.78125**;
- median: **+10**;
- Tactical Memory produced large negative money deltas while W/L remained wins.

## Decision

O-RW1 survives the hosted-entrypoint correction as an autonomous runtime option, but it
must no longer be described as universally safe or broadly transferable.

The next step is purely mechanical:
- rebuild the candidate so the final callable selected by Kaggle is uniquely
  `_kc_orw1_entrypoint`;
- require exact action/reward parity under the official loader;
- do not submit a corrected hosted sensor until that package gate passes.

No O-RW1 retuning is authorized.
