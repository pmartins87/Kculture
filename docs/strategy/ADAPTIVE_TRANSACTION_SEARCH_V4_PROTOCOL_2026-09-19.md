# Adaptive Transaction Search V4 Protocol — conditional fallback — 2026-09-19

## Activation condition

This protocol is **frozen but dormant**. It may be executed only if the binding
Adaptive Wrapper Proposal Oracle V3 fails to demonstrate meaningful W/L headroom
outside the modern V47-family stratum.

A V3 mechanical failure does not activate V4; V3 must first be made mechanically valid.

## Why V4 exists

Ryzen Option-Value V2 showed that O-RW1 and O-TW1 produce almost all non-neutral W/L
labels against the V47 mirror. A larger value model cannot manufacture cross-family
headroom absent from the option set.

The earlier Bounded Transaction Oracle V1 closed only a narrow family:
- current-turn SELL queue reorder;
- one-turn removal/deferral;
- states where V47 often exposed only one effective SELL.

V4 therefore changes the **search horizon**, not merely the model.

## Question

Can a short transaction sequence, evaluated by the exact engine, produce W/L gains
against at least two unrelated non-V47 opponent families while preserving the strong
V47 physical programme outside the bounded intervention window?

## Host

Exact public V47:
- handle: `ahmedberatozer/kaggriculture-v47-reactive-market-coordination`;
- main SHA-256:
  `f4ecd4876fde93a14e3381993283f3b6a1afa023b48dd57217f4d90794d39842`;
- hosted entrypoint: `_y_agent_shopherd`;
- loader contract: official Kaggle last-callable semantics.

## Population

Use the seven-agent V2 league:
1. V47 mirror;
2. Ready Stock;
3. V48;
4. `2715.6` multi-program router;
5. Conditional Memory;
6. Tactical Memory;
7. Best Market Agent.

The **primary V4 success criterion is outside the modern V47 family**. V47/Ready Stock/V48
remain useful controls but cannot alone promote the architecture.

## Proposal source

Strong public agents may be used transiently as offline **proposal generators** only.
No third-party code is promoted into the final runtime agent by this gate.

At a legal current state, proposal generators may nominate a bounded transaction plan of
up to **3 consecutive turns**. Candidate plans are deduplicated by canonical action sequence.

The preferred source order is:
1. recurring transaction patterns actually observed in strong public adaptive agents;
2. first-party transformations derived from already validated mechanics (town pulse,
   ready-stock sales, latent supply, funding/reserve guards);
3. BASE exact V47 sequence.

## Bounded intervention contract

A plan may alter market actions only.

During the intervention window:
- preserve V47 farmer action exactly;
- preserve V47 hands actions exactly;
- preserve all non-target market orders unless the candidate explicitly represents a
  queue/timing transformation being evaluated;
- maximum 3 turns;
- maximum 10 market orders per turn;
- after the window, exact V47 resumes autonomously from the resulting state.

No candidate may depend at runtime on:
- opponent identity;
- rating;
- EpisodeId;
- hidden seed;
- future state;
- opponent-private inventory/state.

## Exact-engine evaluation

For every branch state:
1. reproduce BASE from a fresh replay and verify branch-state parity;
2. execute BASE continuation;
3. execute every unique bounded candidate from the identical branch state;
4. continue exact V47 to terminal state;
5. label by terminal competitive score delta first, margin delta second.

Primary target:
`score(candidate) - score(BASE)` in `{-1,-0.5,0,0.5,1}`.

Margin is diagnostic/tie-breaking only.

## Freshness / leakage

Use fresh seeds not present in V1/V2 option-value production or earlier V2b discovery.
Both seats are mandatory.

Opponent family is offline stratification metadata only and must never become a runtime
feature.

## Gate

Mechanical PASS requires:
- zero replay/branch parity failures;
- zero invalid actions;
- all episodes DONE;
- at least 24 valid branch states;
- at least two non-V47 opponent families represented in valid branch states.

Strategic **DIVERSE HEADROOM PASS** requires all:
- >= 4 nonwin→win flips outside the modern V47 family;
- positive W/L score delta outside the modern V47 family;
- gains in >= 2 unrelated non-V47 opponent families;
- no non-V47 family mean W/L regression below `-0.0625`;
- no evidence that one hidden identity/seed-specific rule is required.

If W/L headroom exists in exactly one non-V47 family:
`V4_OUTSIDE_HEADROOM_NARROW`; causalize the pattern but do not call it broad adaptation.

If only margin improves:
`V4_MARGIN_ONLY_CLOSE_AS_WL_OPTION_SOURCE`.

If no headroom:
`V4_NO_BOUNDED_TRANSACTION_HEADROOM`; move search to physical/macro guards rather than
increasing horizon indefinitely.

## Promotion rule

A public-proposal sequence is **never** deployed directly.

Any recurring winning pattern must be rewritten as a first-party option defined only from
legal current state, then pass:
1. fresh causal gate;
2. autonomous runtime gate;
3. broad population regression gate;
4. package parity;
5. only then option-library admission.

## Stop rule

Do not expand from 3 turns to arbitrary long-horizon search merely because V4 fails.
A longer horizon requires a new causal hypothesis showing why 3 turns are insufficient.

## Hosted policy

No Kaggle submission is authorized by V4 itself.
Active hosted slots remain preserved while offline search proceeds.


---

## Evidence-driven amendment after valid V3

This amendment was made **before any V4 execution**.

Valid V3 run `35426189093` showed:
- 56 branch states / 84 exact counterfactual rollouts;
- zero W/L improvement overall;
- eight positive-margin states outside modern41, all from `router_2715`;
- those outside-modern41 states were already BASE wins.

Therefore the original V4 requirement of W/L gains across multiple arbitrary non-V47 families
would target strata with no available nonwin→win headroom and is no longer the primary gate.

### Revised primary target

V4 must prioritize **hard BASE non-win strata**, not family diversity for its own sake.

Current highest-priority block is V48 because:
- valid V3 fresh seeds produced BASE losses vs V48 with small margins (`-303`, `-240`);
- one-turn proposals failed to flip them;
- the G1 composition gate also left V48 W/L unchanged.

Before V4 multi-turn search, run a V47×V48 divergence census on fresh seeds. Then:

1. If V47 and V48 mostly share farmer/hands while differing in market/queue decisions,
   launch market-only multi-turn V4 against V48 first, with V47 mirror and Ready Stock as
   regression controls.
2. If physical divergences are material before/around the competitive separation point,
   do **not** force a market-only V4. Open a bounded physical/macro guard search instead.
3. Cross-family validation remains required **after** a hard-stratum option is discovered,
   but it is a regression/generalization gate, not the discovery target.

### Revised promotion requirement

For the first V4 hard-stratum discovery gate, promote a causal hypothesis if:
- exact BASE has at least four non-win contexts in the targeted hard block;
- the candidate produces >=2 nonwin→win flips or a target-block score delta >= +0.125;
- no control block regresses by more than `-0.0625`;
- the winning mechanism can be expressed from legal runtime state without opponent identity,
  hidden seed, rating, EpisodeId, future state, or opponent-private state.

Only after causalization must the option pass broader unrelated-family regression tests.

This amendment replaces the earlier requirement that the *discovery* gate itself improve at least
two unrelated non-V47 families.
