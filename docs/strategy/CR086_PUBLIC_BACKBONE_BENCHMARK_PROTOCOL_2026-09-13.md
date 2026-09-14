# CR086 public-backbone benchmark protocol — frozen before H2H

Date: 2026-09-13

Purpose: compare selected public Kaggriculture agents against immutable CR083 before any modification or CR086 candidate definition.

## Sources

Read-only acquisition run: `34790801576`, artifact `10327672303`.

Executable public agents:

1. `indarkarhana/shape-the-shop-work-the-pasture-top-10` — deterministic package produced by notebook; declared entrypoint `kaggriculture_e776_agent`; notebook attribution cites CC0 replay priors from Kenjo1209 and NIklitaCheporev.
2. `boatlee/v29-r1-adaptive-market-hysteresis` — deterministic standalone `main.py` package.
3. `lynnsakurai/farming-score-v3-replay-revised` — deterministic standalone `main.py` package.

`tetsutani/shape-the-shop-work-the-pasture-kaggriculture` is excluded from H2H because the pulled notebook is analytical/visual rather than a standalone agent builder.

## Incumbent

Exact frozen CR083 SHA-256: `648fbcdb370f7e48fafda18a1112c5f1b57a17a81b7191f010fe4058f41a41b8` from canonical artifact `10304915100`.

## Frozen benchmark

- reference runtime: `kaggle-environments==1.32.7`;
- fresh spawned process per package per episode;
- both seats;
- 16 fresh seeds per candidate = 32 games each;
- master seed: `9160861`;
- no environment tape forcing;
- no agent RNG manipulation;
- no tuning from partial results;
- no hosted submission.

Seed firewall must prove zero overlap with all prior frozen masters through CR085.

## Eligibility threshold

A public backbone is **promising for CR086 architecture study** only if all hold:

- exactly 32 completed games / 16 seeds;
- zero execution errors and zero non-DONE games;
- score rate versus CR083 `>= 0.5625`;
- mean terminal-money margin `> 0`.

This threshold is only a discovery screen. Passing does **not** authorize hosted use, modification, or submission.

If multiple agents pass, rank for further study by score rate versus CR083, then mean margin. Before any candidate derived from public code can be promoted, provenance/license/attribution must be audited and the candidate must still pass independent legacy and high-strength stress gates.

## Binding interpretation

Do not retune a public agent after seeing this benchmark. If it fails, it remains useful only as architectural evidence. If it passes, benchmark it against legacy anchors and inspect mechanisms before defining CR086.
