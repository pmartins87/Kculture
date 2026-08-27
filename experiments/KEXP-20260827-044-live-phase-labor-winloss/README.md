# KEXP-20260827-044 — live phase labor win/loss audit

Status: **RUNNING / OBSERVATIONAL FALSIFICATION**

## Prize-first question

KEXP-042 found a very large midgame PASS gap between current live winners and frozen R4B, and the COK code confirms that static route traces are padded with PASS when more workers exist than scripted actions. Before building a large dynamic worker dispatcher, test whether stronger labor utilization is actually associated with winning **within the same official episodes** rather than merely distinguishing one strategy family from another.

## Protocol

Use top-20 official episodes on 2026-08-24, 25 and 26. With corrected replay alignment (`state t -> action frame t+1`), compare winners and losers phase by phase on:

- total worker action slots;
- PASS count and non-PASS fraction;
- movement count;
- productive non-movement/non-PASS actions;
- HIRE orders;
- PASS per HIRE.

Phases match KEXP-042: 0–95, 96–191, 192–287, 288–383, 384–479, 480–575, 576–647, 648–695, 696–718.

## Interpretation

The key falsification target is the 96–287 midgame. If winners consistently show fewer PASS / higher non-PASS or productive utilization than losers, it strengthens the case for a dynamic labor allocator. If winners and losers are indistinguishable or losers are more active, KEXP-042's large R4B gap may be a strategy-family fingerprint rather than a causal weakness; a dispatcher should then be tested much more cautiously.

This experiment is observational only and never creates a deployable identity rule.

No validation or held-out seeds are accessed.

Tool: `tools/live_phase_labor_winloss.py`  
Frozen blob: `e7eaed7424c185ed0a9963bf59b58f6e49008de8`.
