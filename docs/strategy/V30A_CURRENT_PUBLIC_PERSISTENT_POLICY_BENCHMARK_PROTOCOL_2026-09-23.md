# V30A — Current Public Persistent Policy Direct Benchmark Protocol — 2026-09-23

## Status

PRE-REGISTERED after binding V29A failure and before any V30A benchmark outcome.

V30A is an offline benchmark only. It cannot mutate Kaggle slots.

## Why this branch is materially different

Binding evidence says:
- compact/additive options do not cover ALL3's residual hard core;
- finite imitation prefixes do not preserve W/L gains;
- tree and recurrent distillation of the persistent public teacher fail badly;
- only persistent whole-episode policies have shown large hard-context headroom.

Kaggriculture Rule 6.b explicitly permits Competition Code publicly shared in Kaggle competition notebooks/discussions and deems such shared code licensed under an OSI-approved license. V30A therefore evaluates complete **publicly shared competition policies** directly rather than attempting to reverse-engineer or distill them.

V30A does not use private code or privately shared material.

## Fresh public policy snapshot

At V30A runtime:
1. query the current Kaggriculture public kernels:
   `kaggle kernels list --competition kaggriculture --sort-by scoreDescending --page-size 100 -v`;
2. take the first 30 unique public refs;
3. acquire public source through the existing Kaggle public-source acquisition path;
4. SHA-deduplicate;
5. smoke-test both seats versus starter;
6. exclude exact V47 identity;
7. freeze up to 12 executable unique public representatives, minimum 8.

Reuse the existing audited snapshot implementation:
`tools/v28b_current_frontier_snapshot.py`.

The resulting immutable snapshot is the only policy source used by benchmark jobs. No live reacquisition inside episodes.

Every selected public source retains:
- representative Kaggle notebook ref;
- representative public-kernel rank;
- exact main.py SHA.

These fields are provenance/selection metadata only. Candidate policies themselves run exactly as published.

## Common opponent panel

Opponent panel:
all selected immutable public representatives from the same fresh snapshot.

The exact same opponent panel and contexts are used for every candidate.

## Candidate set

1. `ALL3` — exact protected first-party ALL3 baseline:
   exact V47 base + O-RW1 + O-TW1 + O-LQ2.

2. Every selected public representative as one complete persistent policy candidate.

No policy mixing, source-conditioned routing, action splicing, or identity-dependent switching is allowed.

## Frozen fresh contexts

Seeds:
`80501, 80502, 80503, 80504`.

Seats:
both 0 and 1.

With 12 representatives:
- 12 opponents × 4 seeds × 2 seats = 96 contexts per candidate.

Seeds are fresh relative to V28F/G/H/K/L.

## Mechanics

For each episode:
- instantiate candidate fresh;
- instantiate opponent fresh;
- episodeSteps=720;
- require DONE/DONE;
- require >=720 replay frames;
- finite two-player rewards.

Any candidate/opponent cell failure makes mechanics invalid. No outcome-based dropping of a public candidate or opponent after snapshot freeze.

## Metrics

For every candidate:
- contexts;
- W/L/T;
- score rate;
- mean and median terminal margin;
- score rate by opponent source;
- score rate by seed.

For every public candidate paired against ALL3 on identical contexts:
- positive score contexts: candidate score > ALL3;
- negative score contexts: candidate score < ALL3;
- neutral contexts;
- mean paired score delta;
- mean/median paired margin delta;
- opponent-source breadth where candidate aggregate score exceeds ALL3 aggregate score;
- seed breadth where candidate aggregate score exceeds ALL3 aggregate score;
- both-seat positive support.

## Frozen eligibility gate

A public candidate is **promotion-eligible** only if all:

1. candidate score rate >= ALL3 score rate + **0.08**;
2. mean paired score delta >= **+0.08**;
3. candidate aggregate score exceeds ALL3 on at least **4 distinct opponent sources**;
4. candidate aggregate score exceeds ALL3 on at least **3 of 4 seeds**;
5. positive paired score contexts > negative paired score contexts;
6. candidate has at least one positive paired context in **both seats**;
7. mechanics PASS.

No threshold may be weakened after outcomes.

## Frozen selector

Among eligible public candidates choose exactly one by:
1. highest score rate;
2. highest mean paired score delta;
3. highest mean paired margin delta;
4. lowest representative public-kernel rank;
5. lexical SHA.

Decision:
- eligible candidate exists => `V30A_PUBLIC_PERSISTENT_POLICY_CANDIDATE_READY`;
- none => `V30A_NO_PUBLIC_PERSISTENT_POLICY_ADVANTAGE`;
- mechanics failure => `V30A_MECHANICS_INVALID`.

## Routing

If READY:
- preserve exact selected public source package and attribution;
- open V30B independent validation/package-parity gate on fresh seeds and a separate fresh immutable frontier;
- V30B must still beat ALL3 with multi-source/multi-seed evidence;
- no Kaggle submission occurs automatically.

If NO_ADVANTAGE:
- do not cherry-pick a public source by hosted reputation or notebook rank;
- close direct-public-policy promotion from this snapshot.

Any eventual hosted slot mutation requires a separate preflight and explicit user authorization.
