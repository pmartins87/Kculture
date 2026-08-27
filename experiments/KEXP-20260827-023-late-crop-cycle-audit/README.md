# KEXP-20260827-023 — late crop cycle audit

Status: **PREDECLARED / DIAGNOSTIC ONLY**

## Prize-first question

KEXP-022 showed that current high-Elo agents adapt late CARROT allocation to the full public shop-demand state, while frozen COK/R4B remains heavily WHEAT-tape dominated. Before changing crop type, verify that the existing spatial tape harvests late WHEAT soon enough for a CARROT substitution to remain mechanically sensible.

## Protocol

Run frozen `R4B-market-only-validated-v1` unchanged against deterministic `starter` on:

- all 16 frozen **development** seeds;
- the 20 exploratory environmental seeds reconstructed from official 2026-08-25 top ladder episodes.

Candidate is player 0 only because this experiment measures its own physical crop-cycle timing, not matchup strength.

For every `PLANT WHEAT` during steps **576..647**, record the actor/tile and locate the next `HARVEST` action executed on that same physical tile. Report the delay.

CARROT timing classes are deliberately conservative using frozen official mechanics:

- `clean_le_72`: harvest within 3 in-game days, at or before CARROT max-yield day;
- `decay_risk_73_95`: mature but entering the one-time-crop decay region;
- `unsafe_ge_96`: four or more days later, unsuitable for a blind WHEAT→CARROT swap;
- `no_harvest`: no later harvest in the season.

## Decision rule

This experiment **cannot promote a policy**. It only decides implementation safety:

- if most intended late plant slots are `clean_le_72`, a bounded demand/price-aware substitution can be prototyped without rewriting movement;
- if a large share is decay-risk/unsafe/no-harvest, do not perform a blind crop substitution. A separate crop lifecycle controller would be required and must compete against other prize-first opportunities before implementation.

No validation or held-out seed is accessed. No seed, episode or opponent identity may become a deployment feature.
