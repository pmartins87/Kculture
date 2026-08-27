# KEXP-20260827-055 — TOMATO slot succession diagnostic

Status: **RUNNING / DIAGNOSTIC ONLY**

## Question

KEXP-053 found 32 R4B WHEAT/CARROT plant events whose next same-tile HARVEST occurs at least 192 turns later, long enough for TOMATO's first production under the official engine.

TOMATO is ongoing: HARVEST resets its accumulated yield but does not remove the plant. Therefore a naive substitution can block a later `PLANT` that assumes the one-shot WHEAT/CARROT tile became empty.

KEXP-055 measures this exact succession risk before any TOMATO candidate is written.

## Method

On the same open development + exploratory live-meta environmental seeds used for KEXP-053:

- replay frozen R4B versus starter;
- identify only the >=192-turn compatible slots;
- after each slot's next HARVEST, record the next same-tile non-movement action;
- locate the next same-tile PLANT and measure its delay from HARVEST;
- summarize replant conflicts within 24, 48 and 96 turns.

No validation or held-out outcome is accessed.

## Routing criterion

A simple local TOMATO substitution remains plausible only if at most 25% of compatible slots need another PLANT within 96 turns after the original HARVEST. Otherwise the next TOMATO experiment must explicitly model tile release (`DIG`/expiry) and cannot be treated as a market-only substitution.

This is a design-routing diagnostic, not a promotion/performance gate.
