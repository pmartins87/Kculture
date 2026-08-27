# KEXP-20260827-026 — exact late CARROT seed ledger

Status: **COMPLETE / STOCK-ONLY SUBSTITUTION REJECTED**

## Why this replaces KEXP-025

KEXP-025 incorrectly summed repeated snapshots of the same CARROT seed and therefore overstated stock-only substitution capacity. KEXP-026 rebuilt the seed ledger with exact replay alignment and same-turn/future reservation.

A second correction was required after establishing the Kaggle replay convention exactly: the action chosen from observation/state frame `t` is stored on replay frame `t+1`. V3 is the canonical aligned result.

## Canonical protocol

Frozen R4B unchanged vs deterministic `starter` on:

- all 16 development seeds;
- all 20 exploratory live-meta environmental seeds.

At every KEXP-023 mechanically safe WHEAT-plant step (614–618, 620–623, 636–647), ask whether any CARROT seed is truly unreserved after accounting for:

- base CARROT plant intents in the same turn;
- all later base CARROT plant intents;
- exact observation/action timing.

No strategy mutation, validation, or held-out access.

## Canonical result

Actions run **`33040343952` — SUCCESS**.
Artifact **`9633685604`**, ZIP digest **SHA-256 `236c1d4e7beb6b0337946bcd6422b3bccac6d923ba2be3e8974434ac3114926d`**.

Exact ledger sanity:

- development `alignment_bad_total`: **0**;
- exploratory live-meta `alignment_bad_total`: **0**;
- all 36 episodes: **0** alignment inconsistencies.

Truly unreserved safe CARROT stock:

- development: **0/16 episodes**;
- exploratory live-meta: **0/20 episodes**;
- combined: **0/36 episodes**;
- total stock-only swap capacity: **0**.

The last frozen-base CARROT plant intent is step 645 in 30/36 episodes; six episodes have no late CARROT intent. The apparent persistent one-seed stock seen by KEXP-025 is therefore normally reserved for the base route rather than idle capacity.

## Decision

**No-purchase WHEAT→CARROT substitution is rejected.**

Any serious late crop-response candidate must deliberately reallocate seed purchases before the mechanically safe planting windows. It must use legal public state and must preserve enough inventory to avoid atomic PLANT invalidation.

This result directly motivates KEXP-029, which searches for a conservative demand+price trigger from current high-Elo public trajectories before any seed-purchase mutation is implemented.

Canonical tool blob: `4a602abc7db509e0e4903e2896565403a9dd5530`.
