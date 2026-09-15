# FP001 STATUS — mechanics/economics integration track

Updated: 2026-09-15

Authoritative experimental branch: `research/first-principles-economy-v1`.  
Competition-level source of truth: `STATUS.md` / `ROADMAP.md` on `fix/kaggle-parity-v1`.

## Mission

Discover causally defensible mechanics, economic primitives and higher-level options that improve prize probability when integrated with accumulated competitive knowledge. FP001 is additive; it does not replace CR053/CR086/CR087/CR088 knowledge.

## Proven primitives retained

- H1 town-pulse WHEAT carry — PASS `34843184110`, +916.875 paired mean; flat-price null 0.
- H1B owned-sale deferral — PASS `34843556192`, 104/104 positive exact cases.
- H8/B3 animals — COW > SHEEP/GOOSE in tested physical baseline; DAILY CARE strongly positive (`34844919444`, `34847600991`).
- H9 public-town demand — representation PASS `34847099631`; public shops alter expected MILK/WOOL/EGG demand.
- H10 compact routing + threshold-6 batching — PASS `34848106237`.
- H11 fertilizer conversion — PASS `34848464648`; STRAWBERRY strong, TOMATO has positive regions.
- B4 scale×CARE — fifth COW marginal, sixth COW beyond action/opportunity-cost frontier (`34848633407`).

## Premium crop integration

- E1 residual-idle STRAWBERRY — CLOSED `34860319522`; labor bottleneck.
- E2 dedicated crop hand — CAUSAL PASS through `34866890716` after correcting weed/shop RNG coupling.
- E3 M6S1 density — PASS `34868854114`; frozen 6 MELON + 1 STRAWBERRY.
- E4 normal-env robustness — STRONG PASS `34869392514`, +9594.5 mean, 33–7 signs, 80/80 mechanics.
- E5 fixed mixed animals — FAIL `34922557868`; exact C5_M6S1 transfer remained strong economically, but C3S2/C2S3 damaged crop completion. Fixed mixed openings remain closed.

M6S1 remains a genuine economic/physical module, not a competitive backbone by itself.

## CR089 population compatibility — COMPLETE / FAIL

Run `34923802262`:

- C5_BASE: 0W–132L
- C5_M6S1: 0W–132L
- zero mechanical failures
- M6S1 improved monetary margins on 10/11 edges and by ~+16.6k averaged across edge means, but zero W/L gain

Verdict: `M6S1_FAILS_POPULATION_COMPATIBILITY`.

Static C5/C5+M6S1 backbones are closed. M6S1 is retained only as a module for a stronger controller/backbone.

## CR090 H9 simple species adaptation — COMPLETE / FAIL

Run `34979280512`, artifact `10401171740`.

Mechanics were exact across all 128 matched cases per policy, with zero failures. Natural support: YARN 24, MILK 28, NEUTRAL 76.

Causal results:

- YARN: H9 SHEEP minus delayed COW mean -174.46, median -451, positive 7/24
- MILK: H9 COW minus delayed SHEEP mean +2119.39, median +2151, positive 28/28
- all H9 minus delayed COW mean -32.71, median 0

Verdict: `CR090_H9_CAUSAL_FAIL_CLOSE_SIMPLE_SPECIES_ADAPTATION`.

Interpretation: H9 is a useful demand/state representation, but `WOOL demand > MILK demand` is not a sufficient action-value rule. Do not threshold-tune it. CR090 Phase 2 H9+M6S1 is cancelled.

Competition result doc: `docs/strategy/CR090_H9_PUBLIC_SHOP_ADAPTIVE_RESULT_2026-09-15.md` on `fix/kaggle-parity-v1`.

## Current experiment — CR091 hierarchical market option gate

The architecture now changes from “new complete backbone per hypothesis” to **hosted-proven backbone + separable options + W/L option value**.

CR053 is preserved as the physical/macro host because it remains the strongest exact project-hosted agent (~2064.8), even though its implementation is a static 719-step tape.

Phase-1 implementation:

- candidate wrapper: `candidates/cr091_cr053_market_option.py`
- test: `tools/cr091_hierarchical_market_option_gate.py`
- workflow: `.github/workflows/cr091-hierarchical-market-option.yml`
- workflow run: `34987640694`
- workflow/head commit: `93e3926581706b10c11f93fbec9ae5559670dc55`

Treatments:

1. exact CR053;
2. exact CR053 farmer/hands and exact market-order multiset, with only order sequencing changed by the exact CR086 latent-supply cash-risk priority operator.

The donor operator is loaded from byte-verified historical CR086 artifact code to avoid reimplementation drift.

Exact Phase-1 opponents: CR052_REAL, CR053_REAL, CR083, CR086. Seeds 91301..91308, both seats, 128 episodes total.

Mandatory mechanics:

- zero non-DONE/errors;
- exact CR053 farmer parity every call;
- exact CR053 hand parity every call;
- exact normalized market-order multiset parity every call;
- CR053_BASE exact-action parity;
- latent option must actually reorder at least one call.

Primary outcome: seat-balanced W/L edge-score delta. Terminal money is diagnostic only.

Frozen branches:

- broad positive transfer -> retain option and advance router;
- strong positive + negative edges -> heterogeneous option value, advance public-state router discovery;
- no meaningful edge value -> close this transplanted option without threshold tuning, then test next separable option family (H1/H1B timing first);
- mechanics issue -> repair semantics only.

## Hosted policy

No CR091 Phase-1 Kaggle submission is authorized. Original final holdout untouched. Hosted slots remain reserved for a mechanically exact candidate that survives a meaningful population-transfer question.
