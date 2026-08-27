# KEXP-20260827-043 — midgame PASS headroom

Status: **RUNNING / ARCHITECTURE DIAGNOSTIC**

## Prize-first question

KEXP-042 found the first large full-game divergence between recent top winners and frozen R4B: during states 96–191 the sampled winners average ~33 PASS actions while R4B averages ~120, and during 192–287 winners average ~37 while R4B averages ~159. R4B is not hiring fewer workers; in 192–287 it actually issues more HIRE orders on average.

The frozen COK controller also mechanically pads available workers with `PASS` whenever the selected static trace has fewer hand actions than the current hand count. This makes labor under-utilization a plausible high-ceiling architectural defect.

KEXP-043 separates two remedies:

1. **cheap local fallback** — an idle actor is already standing on a useful task;
2. **dynamic dispatcher** — idle actors need routing to nearby useful tasks.

## Protocol

Run frozen R4B unchanged vs deterministic starter on all 16 development seeds and all 20 exploratory live-meta environmental seeds.

Inspect every corrected-alignment R4B PASS intent during states 96..287. For each idle actor record:

- current position and carried inventory;
- legal same-tile opportunities: DROP, DIG, WATER, HARVEST plant/animal, FERTILIZE, COLLECT_FERTILIZER, FEED, CARE;
- Manhattan distance to the nearest visible task-bearing tile (weed, unwatered plant, harvestable plant/animal, collectible fertilizer).

This experiment does not replace actions. It estimates opportunity headroom only.

## Predeclared interpretation

- `same_tile_fraction >= 20%` in both pools: authorize a cheap bounded PASS fallback prototype first;
- `within_2_task_fraction >= 50%` in both pools: authorize a bounded dynamic task dispatcher even if same-tile opportunities are sparse;
- if neither passes, the large PASS count is mostly route timing/positioning rather than trivially recoverable labor and requires a broader route planner.

No validation or held-out seeds are accessed. Seed/opponent/episode identity is forbidden as a deployable feature.

Tool: `tools/audit_midgame_pass_headroom.py`  
Frozen blob: `5afb75ca0b20f64af72ba32d0f80670fa3b8f89a`.
