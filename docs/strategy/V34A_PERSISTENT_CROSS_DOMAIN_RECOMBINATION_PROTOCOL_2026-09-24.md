# V34A — Persistent Cross-Domain Recombination High-Upside Gate — 2026-09-24

## Status
PRE-REGISTERED after current hosted primary V30B stabilized near 2391 and remained >500 rating points below Top-10.

No V34A result authorizes Kaggle mutation.

## Purpose
Test whether strong public persistent policies contain complementary MARKET versus PHYSICAL capabilities that can be recombined into a single first-party policy with higher ceiling than V30B.

## Frozen policy set

P0 — exact hosted V30B:
- ref `arsgorynich/herd-safe-v3-experimental-risk-aware-feed`;
- SHA `4f8637a3e33348b98f531de246d353f5d2955b2f85480e3fd02bf4a7874f0d01`.

P1 — confirmed hedge:
- ref `prvsiyan/kaggriculture-frontier-the-moon-counts-melons`;
- SHA `178ae0f727641cf4b618ebb98ade7aa1a1bed7517281aab9849de82a59d8ed3a`.

P2 — CHA22:
- ref `abhinav0370/kaggriculture-cha22-agent`;
- SHA `127ed3e62988c0474d386db6527ae8ca9de9bb1fe7004128557ddef67126c652`.

P3 — herd-safe sale-window:
- ref `dmitriigluzdov/kaggriculture-herd-safe-sale-window-lb-2700`;
- SHA `4889137f1adf1f9266b2ad5a6ac6700c40e9be6dfe3654e39db375fb55b71341`.

## Candidate family
Each underlying policy is evaluated every turn to preserve its own internal recurrent/global state.

Action schema is canonicalized to:
- FARMER;
- HANDS;
- MARKET.

For every ordered pair (market donor M, physical donor P), M != P:
- MARKET comes from M;
- FARMER + HANDS come from P.

This yields 12 directed cross-domain hybrids.

Also evaluate each of the four full policies, for 16 total candidate modes.

No source identity, opponent identity, seed, rank, SHA or EpisodeId is used as a runtime feature.

## Opponent population
Acquire a fresh standard immutable V28B public frontier after preregistration.

Seeds:
`80911,80912,80913,80914`.

Seats:
both 0 and 1.

Every mode runs on every identical context.

## Promotion gate
A hybrid advances only if all:
1. mechanics PASS;
2. hybrid score rate >= exact V30B + **0.10**;
3. mean paired score delta >= **+0.10**;
4. positive source breadth >=4;
5. positive seed breadth >=3/4;
6. positive paired contexts > negative paired contexts;
7. positive support in both seats.

Full policies are controls and cannot be selected as V34A hybrid winners.

Selector among eligible hybrids:
score rate -> paired score delta -> paired margin delta -> source breadth -> seed breadth -> lexical mode.

Decisions:
- `V34A_CROSS_DOMAIN_HYBRID_READY`
- `V34A_NO_HIGH_UPSIDE_CROSS_DOMAIN_HYBRID`
- `V34A_MECHANICS_INVALID`.

Routing:
READY => freeze exact donor pair and implement/package the first-party hybrid, then run one V34B fresh independent validation with package parity before any hosted decision.
NO_HIGH_UPSIDE => close this composition family.
No Kaggle mutation without explicit user authorization.
