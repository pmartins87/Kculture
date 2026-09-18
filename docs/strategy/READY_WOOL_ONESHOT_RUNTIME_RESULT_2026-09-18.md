# O-RW1 One-Shot Runtime Transfer Result — 2026-09-18

## Binding result

Workflow `35313204723`, artifact `10534778422`, exact engine `1.32.7`.

Mechanical PASS:
- 64 paired matchups / 128 complete episodes;
- zero failures;
- pre-trigger observation and exact-V47 action parity passed;
- O-RW1 triggered exactly once in every treatment episode;
- trigger steps were 151, 153 or 155.

Primary W/L result:
- BASE score rate: **0.5000**;
- V47 + O-RW1 score rate: **0.6875**;
- **delta: +0.1875**;
- **28 non-win -> win flips**;
- **0 win -> non-win regressions**.

Per opponent:
- V47 mirror: `0.500 -> 0.875`, delta **+0.375**, 14 positive flips;
- V48: `0.500 -> 0.875`, delta **+0.375**, 14 positive flips;
- Tactical Memory: `1.000 -> 1.000`, W/L neutral;
- Ready Stock: `0.000 -> 0.000`, W/L neutral.

All four opponent blocks had nonnegative score delta. Worst block delta was 0.0.

Binding verdict: **`READY_WOOL_RUNTIME_PASS`**.

## Important diagnostic

Overall mean terminal-margin delta was negative (`-743.5`) even though median delta was
`+10`. This comes from a small number of very large negative money deltas against
Tactical Memory while the treatment still won those games.

Therefore:
- keep W/L as the primary objective;
- do not optimize O-RW1 using terminal money alone;
- hosted calibration remains essential;
- the Tactical Memory outliers should later become useful value-model / catastrophe
  features rather than a reason to discard a W/L-positive option.

## Frozen runtime option

```
O-RW1:
if not used
and V47 current market == []
and own private shed.WOOL >= 2
and step <= 671:
    append/execute SELL WOOL 2
    used = True
```

Exactly one fire per episode. No changes to farmer/hands or any other V47 decision.

## Next binding step

Build a reproducible Kaggle candidate package:
- exact V47 source identity pinned to
  `f4ecd4876fde93a14e3381993283f3b6a1afa023b48dd57217f4d90794d39842`;
- O-RW1 appended as a transparent one-shot wrapper;
- package provenance/attribution receipt and SHA-256;
- exact-engine package smoke/parity before any hosted submission.

A successful packaging gate makes the candidate **hosted-probe ready**, but does not
authorize submitting it automatically.
