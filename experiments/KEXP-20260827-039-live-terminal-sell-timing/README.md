# KEXP-20260827-039 — live terminal SELL timing

Status: **RUNNING / OBSERVATIONAL ONLY**

## Question

KEXP-037 derives a mechanics-based argument for selling already-available non-input products at state 717 instead of waiting for 718. KEXP-039 independently checks how recent high-Elo public agents actually time terminal SELLs.

This is supporting external evidence only; top-agent behavior is never used as an identity-conditioned deployable feature.

## Frozen protocol

Use official daily Kaggriculture episode datasets for:

- 2026-08-23;
- 2026-08-24;
- 2026-08-25;
- 2026-08-26.

Take the top 20 episodes by official `avg_score` each day.

Use the corrected replay alignment:

**state/observation `t` -> submitted action stored on frame `t+1`.**

For each player, inspect exact executable states 712..718 and record:

- SELL quantity by state step;
- number of SELL order rows by state step;
- fraction of players selling at each step;
- product quantities by exact step;
- market order slot used by each SELL.

Summaries are reported separately for episode winners, losers, all players and each date.

## Interpretation

Primary quantity of interest is the winner share of combined state-717/state-718 liquidation that occurs at **717**. A persistent 717 presence would be consistent with terminal price front-running; concentration at 718 would show that KEXP-037 is exploiting a mechanics opportunity that the sampled public meta may not systematically use.

There is no promotion gate because this experiment changes no policy. Actual candidate strength is determined by KEXP-037's controlled W/L screen.

No validation or held-out seeds are accessed.

Tool: `tools/live_terminal_sell_timing.py`  
Frozen tool blob: `67487d740a5e2a3ac67a01e60c7d58b59d91a6e5`
