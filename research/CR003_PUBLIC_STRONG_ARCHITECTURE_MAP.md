# CR-003 — Public strong-agent architecture map

Date: 2026-08-27  
Status: **STATIC ANALYSIS / NO THIRD-PARTY CODE COMMITTED**

## Purpose

CR-002 is calibrating whether the local laboratory can reproduce useful field-strength ordering. In parallel, CR-003 asks a different question: what architectural capabilities distinguish historically strong public Kaggriculture agents from the frozen R4B/KEXP-050 line?

This document records only behavioral/architectural observations. No third-party source code is copied into this repository. Exact scored-package identities remain frozen in `configs/competitive_reset_league_v1.json` and workflow artifacts.

Historical scores are discovery references, not current immutable ratings.

## Exact packages inspected

Static inspection used the exact package entries already hash-verified by CR-001/CR-002 preparation. The field spans approximately 1771–3090 historical score.

| Agent | Historical score | Static architecture signal |
|---|---:|---|
| Kaito V27 V4 | 3090.1 | compact wrapper over embedded/base policy; explicit regime classification, public demand/price features, dynamic sell-slot ranking and impact-aware market ordering |
| Rayk V11 | 2990.4 | base policy plus public-state/opponent-profile adaptation, cash reserve logic, sell planning, market race/front-running behavior and terminal liquidation |
| Andrew V12 | 2883.0 | base policy plus remembered public market state, demand/meta observation, counter-policy logic, front-running and terminal liquidation |
| Prvsiyan Frontier V5 | 2798.6 | large routed/tape-like base with terminal-value overlay |
| Flex V59 | 2767.3 | compact encoded multi-route/replay-style policy |
| Bruce Pipeline V1 | 2754.9 | large routed base with repair/pending-state handling and terminal cash-out |
| Roman Hamburger V21 | 2391.0 | routed base with additional cash-flow/soil-repair overlays |
| Anas V2 | 2213.8 | compact base wrapper with market-impact/sell-slot handling but less explicit demand/meta adaptation |
| Prvsiyan Baseline V2 | 2123.7 | very large static/routed policy family with limited opponent-aware hooks |
| Renji Builder V3 | 1771.3 | predominantly static generated action schedule |

## Main structural finding

The strongest public agents do **not** require an end-to-end learned policy or a full-game solver to reach the historical 2700–3100 band. A recurring pattern is:

1. start from a mechanically competent routed/base policy;
2. observe public market state at runtime;
3. alter economically high-leverage actions rather than rewriting every unit action;
4. explicitly manage cash/sale timing and terminal liquidation;
5. in the strongest variants, adapt to market regime or opponent/public-behavior signatures.

This is materially different from the Kculture R4B line. R4B has a strong deterministic route/tape core and can exploit particular public agents head-to-head, but its high-level economic policy has low state expressiveness. KEXP-050 changes one bounded crop allocation decision; hosted 145.1 shows that this scale of adaptation is nowhere near enough.

## Capability ladder suggested by the public field

The static field suggests a rough capability progression rather than a single magic heuristic:

- **Tier A — static schedule:** mechanically valid but weak field coverage;
- **Tier B — repaired/robust schedule:** handles weeds/pending actions/terminal mechanics better;
- **Tier C — economic overlay:** dynamic sell ordering, cash-flow protection, terminal cash-out;
- **Tier D — market-state adaptation:** demand/price/regime-dependent decisions across multiple time windows;
- **Tier E — meta/opponent adaptation:** public-behavior signatures, race/front-running logic, contextual counter-policy.

R4B is strong in deterministic execution but is structurally much closer to B/C than to D/E.

## CR-003 construction hypothesis

Prize-first development should no longer optimize isolated crop substitutions. The next legitimate Kculture baseline should combine:

- a proven mechanically strong base trajectory;
- a **stateful economic controller** that observes market inventory, prices, demand and own cash/inventory;
- explicit cash-reserve and sell-timing logic;
- multi-product allocation decisions instead of a fixed WHEAT-heavy route;
- terminal liquidation as a first-class objective;
- optional public-opponent/meta features only after the market controller proves robust.

The controller should be evaluated by CR-002-style broad field coverage/BT, not by one or three hand-picked opponents.

## Reuse / provenance gate

Static analysis is unrestricted research evidence. Any direct derivative implementation from a public notebook/package is separately gated by verified license and competition-rule compatibility. Kaito and Andrew had prior Apache-2.0 evidence recorded during the Competitive Reset; Rayk derivative reuse remains blocked until exact-version license is independently verified. Attribution/license notices must be preserved for any allowed derivative.

A safer default is to use the observations above to build an original Kculture controller around our own base, then compare its behavior against the public reference families.

## Next experiments after CR-002

If CR-002 calibrates, use its direct matchup matrix to identify which public families R4B/KEXP-050 fail against. The first CR-003 candidate should target the largest **coverage hole**, not the easiest opponent or the largest money-margin improvement.

If CR-002 fails calibration, do not promote CR-003 from the same local environment. First repair the proxy field/episode design, while continuing architecture work only as exploratory research.
