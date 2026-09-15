# FP001 STATUS — mechanics/economics integration track

Updated: 2026-09-15

Authoritative experimental branch: `research/first-principles-economy-v1`.  
Competition source of truth: `STATUS.md` / `ROADMAP.md` on `fix/kaggle-parity-v1`.

## Mission

Discover causally defensible mechanics, economic primitives and higher-level options that improve prize probability when integrated with accumulated competitive knowledge. FP001 is additive; it does not replace CR053/CR086/CR087/CR088 knowledge.

## Proven primitives retained

- H1 WHEAT carry — PASS `34843184110`, +916.875 paired mean.
- H1B sale deferral — PASS `34843556192`, 104/104 positive exact cases.
- H8/B3 animals — COW strongest in tested physical baseline; DAILY CARE strongly positive (`34844919444`, `34847600991`).
- H9 public-town demand — representation PASS `34847099631`; public shops alter expected MILK/WOOL/EGG demand.
- H10 compact routing + threshold-6 batching — PASS `34848106237`.
- H11 fertilizer conversion — PASS `34848464648`; STRAWBERRY strong, TOMATO positive regions.
- B4 scale×CARE — fifth COW marginal; sixth beyond action/opportunity-cost frontier (`34848633407`).

## Premium crop integration

- E1 residual-idle STRAWBERRY CLOSED `34860319522`; labor bottleneck.
- E2 dedicated crop hand CAUSAL PASS through `34866890716` after weed/shop RNG correction.
- E3 M6S1 PASS `34868854114`; frozen 6 MELON + 1 STRAWBERRY.
- E4 robustness STRONG PASS `34869392514`, +9594.5 mean, 33–7, 80/80 mechanics.
- E5 fixed mixed animals FAIL `34922557868`; C3S2/C2S3 damaged crop completion.

M6S1 remains a genuine economic module, not a competitive backbone by itself.

## CR089 — COMPLETE / FAIL

Run `34923802262`: C5_BASE and C5_M6S1 both 0W–132L; zero mechanics failures. M6S1 improved monetary margins but zero W/L gain. Static C5/C5+M6S1 closed as backbones.

## CR090 — COMPLETE / FAIL

Run `34979280512`: mechanics exact. YARN H9 SHEEP minus delayed COW mean -174.46, median -451, positive 7/24. MILK H9 COW minus delayed SHEEP mean +2119.39, 28/28 positive. Overall H9 minus delayed COW mean -32.71.

Verdict: `CR090_H9_CAUSAL_FAIL_CLOSE_SIMPLE_SPECIES_ADAPTATION`. H9 remains a useful representation/state feature, not a sufficient action rule. No threshold tuning; Phase 2 cancelled.

## Current experiment — CR091 hierarchical market option gate

Architecture change: **hosted-proven backbone + separable options + W/L option value**.

CR053 remains the physical/macro host because it is the strongest exact project-hosted agent (~2064.8).

Frozen treatments:

1. exact CR053;
2. exact CR053 farmer/hands and exact market-order multiset, with only order sequencing changed by exact CR086 latent-supply cash-risk priority.

Frozen panel: CR052_REAL, CR053_REAL, CR083, CR086; seeds 91301..91308; both seats; 128 episodes total. Primary metric is W/L edge-score delta; money diagnostic only.

### First execution INVALID

Run `34987640694` cannot produce a strategic verdict. The first harness loaded historical `main.py` via direct `exec()` rather than a package-faithful Kaggle wrapper. CR052 failed all 32 treatment episodes.

The other three edges were mechanically clean. Non-binding diagnostic only:

- CR053 edge: 0.5000 -> 0.6875, delta +0.1875
- CR083 edge: 0.5000 -> 0.5000
- CR086 edge: 0.5000 -> 0.5000
- no physical/multiset parity violation on executable calls

Do not call this a PASS.

Competition record: `docs/strategy/CR091_RUN1_INVALID_2026-09-15.md` on `fix/kaggle-parity-v1`.

### Hosted-faithful rerun ACTIVE

- repair commit: `f49bff2e7adde626b01b9fa3c0413f7fc97d9649`
- authoritative workflow run: **`34990757344`**

The experimental design is unchanged. Only runner semantics changed to the already validated reference path:

- `kaggle_exact_runtime.AgentProcess`
- fresh spawned process per package per episode
- official `kaggle_environments.agent.Agent`
- `Environment.__get_shared_state(seat).observation`
- reference stepping/overage accounting
- no falsy-action PASS substitution
- exact CR053 package supplies each candidate base action before CR086 priority is applied
- detailed phase/step/traceback retained for any failure

Mandatory mechanics remain: zero failures; exact CR053 farmer/hand parity; exact market-order multiset parity; exact BASE action; latent option active.

Frozen strategic branches remain unchanged:

- broad transfer -> retain O1 and advance router;
- heterogeneous positive/negative value -> public-state router discovery;
- no meaningful value -> close option without threshold tuning, next H1/H1B timing option;
- mechanics issue -> repair semantics only, no strategic inference.

## Hosted policy

No CR091 Phase-1 Kaggle submission is authorized. Original final holdout untouched. Hosted slots remain reserved for mechanically exact candidates that survive meaningful population-transfer questions.
