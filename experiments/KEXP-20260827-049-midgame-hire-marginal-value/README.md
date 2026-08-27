# KEXP-20260827-049 — midgame marginal HIRE value audit

Status: **RUNNING / DIAGNOSTIC ONLY**

## Why this follows KEXP-047

Official winner-vs-loser evidence shows a consistent three-day labor-timing signal: winners HIRE more in 0-191, **less in 192-383**, then more again late. Frozen R4B also exhibits very high midgame PASS volume. Rather than suppress HIRE from correlation alone, this audit measures the actual utilization of each one-day rental.

## Engine fact

A hand lasts only until the next daily reset. Same-day HIRE cost is Fibonacci-indexed:

`1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, ...`

where the cost uses the number of hires already made that day.

## Protocol

Run unchanged frozen R4B vs starter on all 16 development and 20 exploratory live-meta environmental seeds. Inspect states 192-383.

For every successfully observed HIRE:

1. identify the newly appended hand index;
2. record HIRE ordinal and exact engine cost;
3. follow only that hand until the daily reset;
4. count remaining PASS, movement and productive actions;
5. summarize by ordinal/cost and specifically for cost >=34 and >=89.

HIRE on an end-of-day boundary that cannot be attributed to a persistent next-state hand is marked ambiguous and excluded from utilization summaries.

## Decision use

This experiment cannot promote a policy. It asks whether a narrow, mechanics-based HIRE suppression experiment is worth running.

A follow-up candidate is justified only if both development and exploratory pools show a repeated class of **high-cost marginal hires with very low productive utilization**. If high-cost hires are routinely productive, the three-day live winner/loser HIRE association remains observational and this branch closes.

No validation or held-out access.

Tool: `tools/audit_midgame_hire_marginal_value.py`  
Frozen blob: `fed7647b378efaba35d1cd4dc2d82bd3fb6998d8`.
