# V32A — Fresh Public Policy Delta Scan vs Hosted V30B — 2026-09-24

## Status
PRE-REGISTERED after V30B reached 100 hosted episodes / 2438.9 and current rank 592, while V31C second-slot confirmation runs independently.

No V32A result authorizes Kaggle mutation.

## Purpose
Search only for genuinely new public persistent policies that appeared in the current Kaggriculture Top-30 public-kernel population after immutable V30A workflow 35877442921.

Avoid rerunning the full V30A pool if nothing new exists.

## Frozen baseline
Exact hosted V30B:
- ref `arsgorynich/herd-safe-v3-experimental-risk-aware-feed`;
- main.py SHA `4f8637a3e33348b98f531de246d353f5d2955b2f85480e3fd02bf4a7874f0d01`;
- package artifact from binding V30B-R2 workflow `35906418993`.

## Candidate discovery
Acquire a new current public frontier snapshot using the audited V28B acquisition path after this protocol is committed.

Compare exact executable unique SHA set against immutable V30A snapshot workflow `35877442921`.

Candidate set = every executable unique current public-policy SHA absent from V30A.

If zero:
`V32A_NO_NEW_PUBLIC_POLICY`.

No old V30A candidate may be retested under V32A.

## Benchmark if new candidates exist
Opponent panel = every representative in the new immutable current snapshot.

Seeds exactly:
`80801,80802,80803,80804`.

Seats:
0 and 1.

Run exact V30B baseline and every new candidate on identical contexts.

## Promotion gate
A new candidate advances only if all:
1. mechanics PASS;
2. candidate score rate >= V30B + 0.08;
3. mean paired score delta >= +0.08;
4. positive source breadth >=4;
5. positive seed breadth >=3/4;
6. positive paired contexts > negative paired contexts;
7. positive support in both seats.

Selector:
score rate -> paired score delta -> paired margin delta -> source breadth -> seed breadth -> lower current representative rank -> lexical SHA.

Decisions:
- `V32A_NEW_PUBLIC_POLICY_CANDIDATE_READY`
- `V32A_NO_NEW_PUBLIC_POLICY`
- `V32A_NEW_PUBLIC_POLICIES_NO_ADVANTAGE`
- `V32A_MECHANICS_INVALID`

Routing:
READY => freeze exact ref/SHA/package and run one independent V32B validation on another fresh frontier/unseen seeds. No submission without explicit user authorization.
NO_NEW/NO_ADVANTAGE => close V32A without retesting old V30A policies.
