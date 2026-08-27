# KEXP-20260827-023 — late crop cycle audit

Status: **COMPLETE / BLIND LATE-CROP SWAP REJECTED / SAFE SUBWINDOWS IDENTIFIED**

## Prize-first question

KEXP-022 showed that current high-Elo agents adapt late CARROT allocation to the full public shop-demand state, while frozen COK/R4B remains heavily WHEAT-tape dominated. Before changing crop type, verify that the existing spatial tape harvests late WHEAT soon enough for a CARROT substitution to remain mechanically sensible.

## Protocol

Frozen `R4B-market-only-validated-v1` unchanged against deterministic `starter` on:

- all 16 frozen **development** seeds;
- the 20 exploratory environmental seeds reconstructed from official 2026-08-25 top ladder episodes.

For every `PLANT WHEAT` during steps **576..647**, record the physical tile and locate the next `HARVEST` action on the same tile.

CARROT timing classes use frozen official mechanics:

- `clean_le_72`: harvest within 3 in-game days, at or before CARROT max-yield day;
- `decay_risk_73_95`;
- `unsafe_ge_96`;
- `no_harvest`.

## Canonical result

Canonical rerun after import-only fix:

- Actions run **`33037701080`** — SUCCESS;
- artifact **`9632722866`**;
- artifact ZIP SHA-256 **`30969cf5e44a33d1b9e5fd9c3494f7dd751b5f601079670830e0f2c8a501229b`**;
- 36 episodes;
- 1,039 late WHEAT plant events.

Overall timing:

- `clean_le_72`: **675 / 1039 = 64.97%**;
- `decay_risk_73_95`: **236 / 1039 = 22.71%**;
- `unsafe_ge_96`: **78 / 1039 = 7.51%**;
- `no_harvest`: **50 / 1039 = 4.81%**;
- mean delay 66.785 turns;
- median 67;
- min 34;
- max 98.

Replication by seed source:

- development: 301/460 clean = **65.43%**;
- exploratory live-meta environmental seeds: 374/579 clean = **64.59%**.

The aggregate pattern therefore generalizes across the two environmental pools.

## Step-level structure

The aggregate 65% clean rate hides highly structured timing.

Clearly unsuitable/risky WHEAT plant steps in the observed tape include the 588–599 block. In contrast, these observed plant-step blocks were **100% `clean_le_72`** across the audit sample:

- **614–618**;
- **620–623**;
- **636–647**.

Step **619 is an explicit exception**: only 8/38 cases were clean and 30/38 entered `decay_risk_73_95`.

This step structure is a property of the frozen tape's physical crop cycle; it is not a deployable seed/opponent identity rule.

## Decision

A blanket “late WHEAT → CARROT” mutation is **rejected**: ~35% of observed late WHEAT slots are not clean CARROT substitutions under the existing physical schedule.

A bounded crop-response candidate remains eligible only if it:

1. touches mechanically safe plant-step subwindows rather than all late WHEAT;
2. uses legal public shop-demand + market/economic state to decide whether CARROT is preferable;
3. preserves the rest of R4B/COK;
4. proves W/L gain across families and environmental pools.

No policy is promoted from this diagnostic alone. KEXP-024 terminal CARE reallocation has higher immediate priority because its intervention is narrower and its terminal-value theorem is stronger.

No validation or held-out seed was accessed. No seed, episode or opponent identity may become a deployment feature.
