# V31C — Near-Miss Second-Slot Confirmation Protocol — 2026-09-24

## Status
PRE-REGISTERED after binding V31A R3 completed with decision `V31A_RETAIN_V47_SECOND_SLOT`.

V31A is not reinterpreted. This is a new independent confirmation experiment motivated by the two best V31A near-misses. No V31C result authorizes Kaggle mutation.

## Frozen candidates
Primary:
- exact hosted V30B policy SHA `4f8637a3e33348b98f531de246d353f5d2955b2f85480e3fd02bf4a7874f0d01`.

Control hedge:
- exact V47 SHA `f4ecd4876fde93a14e3381993283f3b6a1afa023b48dd57217f4d90794d39842`.

Near-miss hedge A:
- ref `prvsiyan/kaggriculture-frontier-the-moon-counts-melons`;
- SHA `178ae0f727641cf4b618ebb98ade7aa1a1bed7517281aab9849de82a59d8ed3a`.

Near-miss hedge B:
- ref `ahmedberatozer/kaggriculture-v53-opening-signature`;
- SHA `20fe549dd4573b9fd1dfb32a1782c205fa74f0edfdfd6cbe935079533e0a9d0e`.

These are the only V31C candidates.

## Independent population
Acquire a new current public frontier snapshot after this protocol is committed, using the audited V28B snapshot path.

Seeds:
`80701..80706`.

Seats:
both 0 and 1.

Every policy is run on the identical full context panel.

## Metrics
For V47 and each near-miss:
- standalone score rate;
- best-of-two pair score rate using `max(V30B_score, hedge_score)` per context;
- pair score delta vs V30B alone;
- V30B loss -> hedge win conversions;
- V30B loss -> hedge tie conversions;
- V30B nonwin -> hedge win conversions;
- positive rescue source breadth;
- positive rescue seed breadth;
- positive support in both seats;
- mean hedge margin on V30B non-win contexts.

## Frozen replacement gate
A near-miss may replace V47 only if all:
1. mechanics PASS;
2. pair score rate >= V30B+V47 pair score rate + 0.03;
3. V30B loss->hedge-win conversions >= V47 + 3;
4. rescue source breadth >= V47;
5. rescue seed breadth >= V47;
6. positive rescue support in both seats.

If one or both pass, select by:
1. highest pair score rate;
2. highest loss->win conversions;
3. source breadth;
4. seed breadth;
5. mean residual hedge margin;
6. lexical SHA.

Decisions:
- `V31C_SECOND_SLOT_REPLACEMENT_CONFIRMED`
- `V31C_RETAIN_V47_CONFIRMED`
- `V31C_MECHANICS_INVALID`

Routing:
- REPLACEMENT CONFIRMED => freeze exact ref/SHA/package and request explicit user authorization before any Kaggle mutation.
- RETAIN V47 => no further second-slot fishing from this frozen public pool.
