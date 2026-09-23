# V28K — Midgame Hard-Core Domain Upper-Bound Protocol — 2026-09-23

## Status

PRE-REGISTERED while V28J is still running and before observing any V28K outcome.

V28K is an offline causal upper-bound discovery gate. It cannot create an opponent-identity runtime rule, edit ALL3, or mutate Kaggle slots.

## Strategic question

V28G found 66 universal-hard residual losses concentrated in six current-frontier sources. V28H located the first material hard-vs-easy economic separation at checkpoint 480, with explanatory window 384–479.

Within that frozen midgame window, is the missing capability primarily:
- market-domain;
- physical-domain;
- both independently;
- coordinated cross-domain interaction;
- or not recoverable by this window?

## Binding inputs

Use only immutable artifacts from:
- V28F workflow `35807910104`:
  - immutable frontier snapshot;
  - binding aggregate;
- V28G workflow `35812527508`;
- V28H-R2 workflow `35813287407`.

No Kaggle source reacquisition is allowed.

V28K is independent of V28J outcome.

## Population

Use **all 66 V28F ALL3 residual-loss contexts**, defined exactly by:
`candidate == ALL3 && score == 0.0`.

No post-hoc source/seed/seat filtering.

Each context source serves two offline roles:
1. actual opponent;
2. independent shadow teacher evaluated on the candidate's legal observation.

Source identity is offline forensic metadata only and is forbidden as a deployable runtime feature.

## Frozen window

Treatment window:
**steps 384–479 inclusive**.

Outside this window every treatment returns exact ALL3.

The shadow teacher is still evaluated on every turn to preserve its own state/history, but its action is only applied during the frozen window.

## Modes

Exactly four:

1. `BASE`
   - exact ALL3 throughout the episode.

2. `MARKET_WINDOW`
   - exact ALL3 farmer/hands;
   - teacher market action only during steps 384–479.

3. `PHYSICAL_WINDOW`
   - teacher farmer/hands only during steps 384–479;
   - exact ALL3 market.

4. `FULL_WINDOW`
   - full teacher action only during steps 384–479;
   - exact ALL3 outside the window.

No other horizon, mode, source subset, or threshold may be added after outcomes.

## Mechanical contract

For every context:
- BASE must exactly reproduce V28F ALL3 terminal score and margin;
- all episode statuses DONE/DONE;
- >=720 replay frames;
- finite rewards;
- immutable snapshot SHA checks PASS;
- no live Kaggle credential/source access inside episodes.

Any failure => `V28K_MECHANICS_INVALID`.

## Metrics

For each treatment mode relative to BASE:
- loss -> win flips;
- loss -> tie flips;
- still-loss contexts;
- mean score delta;
- mean margin delta;
- median margin delta;
- positive/negative margin contexts;
- distinct source SHAs with >=1 loss->win;
- distinct seeds with >=1 loss->win;
- both seats represented among flips.

Also report interaction-exclusive contexts:
- FULL_WINDOW wins while MARKET_WINDOW and PHYSICAL_WINDOW do not win.

## Frozen domain-pass rule

A treatment domain passes W/L headroom only if:
- loss->win flips >=4;
- flip source SHAs >=2;
- flip seeds >=2;
- mean score delta >0.

Apply this unchanged to MARKET_WINDOW, PHYSICAL_WINDOW, FULL_WINDOW.

## Decisions

If mechanics fail:
- `V28K_MECHANICS_INVALID`.

Else if MARKET passes and PHYSICAL does not:
- `V28K_MARKET_WINDOW_HEADROOM`.

Else if PHYSICAL passes and MARKET does not:
- `V28K_PHYSICAL_WINDOW_HEADROOM`.

Else if MARKET and PHYSICAL both pass:
- `V28K_BOTH_DOMAINS_WINDOW_HEADROOM`.

Else if neither single domain passes but FULL_WINDOW passes:
- `V28K_CROSS_DOMAIN_WINDOW_INTERACTION_HEADROOM`.

Else:
- `V28K_NO_MIDGAME_WINDOW_WL_HEADROOM`.

## Routing

- MARKET => discover compact identity-free market mechanism in 384–479.
- PHYSICAL => discover compact identity-free physical mechanism.
- BOTH => compare compact market and physical mechanisms independently before composition.
- CROSS_DOMAIN => trace recurrent coupled market/physical divergences inside 384–479; no single-domain threshold tuning.
- NO_HEADROOM => widen architecture/horizon only through a newly pre-registered gate; do not tune V28K.

V28J, when complete, answers whether risk can be recognized with legal state/history. V28K answers whether the frozen midgame window contains causal action headroom. They are complementary and neither authorizes Kaggle mutation.
