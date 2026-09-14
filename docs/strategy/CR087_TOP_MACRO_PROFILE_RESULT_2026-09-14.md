# CR087 current top-10 macro profile — result

Date: 2026-09-14  
Discovery run: `34803148700`  
Profile run: `34803658746`

## Scope

The discovery resolved the active public submission for each current top-10
team and collected three recent public episodes per submission.  It preserved
30 executable 719-action tapes.  The macro profiler parsed 26 of those replays
and sampled each selected agent's legal visible/private-own state at the start
of every game day.

This is architectural discovery, not a promotion dataset.  Each observed state
is endogenous to the opponent and prior action path.

## Action-level result

- 30/30 exact tapes are unique;
- cross-pool pairwise Hamming: mean `702.81`, median `719`, min `401`, max
  `719` out of 719 actions;
- modal consensus: no runtime step has even 50% exact agreement;
- within every active top submission, hundreds of actions change between its
  three sampled episodes.

Conclusion: the current elite is not recoverable as one modal or medoid action
tape.  The repeated signal is at the level of production/economic structure,
not exact commands.

## Descriptive macro families

Ward clustering is weak with only ten teams, so these are descriptive families
to preserve rather than categorical truth:

1. `Majkel1337 / DSM / Orbital Terraformer` — roughly 9–10 WHEAT + 6 MELON,
   2 COW + 3 SHEEP on day 1; rapid STRAWBERRY/MELON capacity and three lands by
   day 10.
2. `Mengfei Li / feel the agi / redblackbst` — roughly 7 WHEAT + 12 MELON,
   2 COW + 2 SHEEP on day 1; highly similar early crop trajectory, then divergent
   livestock/land expansion.
3. `ymg_aq / HowardLeeTW` — WHEAT-heavy opening with lower initial MELON and
   later convergence toward STRAWBERRY plus mixed animals.
4. `Otter Vibe` — distinct GOOSE/TOMATO emphasis and a different cash path.
5. `SpaTaro` — mixed-product market activity and large late SHEEP capacity;
   treat separately despite partial similarity to the MELON-heavy family.

## Cross-family common structure

- valuable early MELON/STRAWBERRY capacity is converted later toward
  WHEAT/CARROT/TOMATO and animal-supporting production;
- most policies reach three lands during the first half; `redblackbst` reaches
  four in the sampled trajectory;
- competitive farms maintain substantial productive animal capacity deep into
  the season rather than treating final liquidation as the only objective;
- market queues differ heavily across episodes, consistent with live-state
  funding, price and opponent-pressure responses.

## Architectural consequence

Do not build another modal tape, day-stitching follower, time-indexed market
transplant or same-step teacher 1-NN.  CR080–CR082 already falsified those
representations, and the current data reinforce the same conclusion.

CR088 must retain multiple macro families and search over coherent production
programs plus legal state-conditioned economic operators.  Local H2H may remove
broken/catastrophic members, but Kaggle hosted probes are required to measure
population transfer.
