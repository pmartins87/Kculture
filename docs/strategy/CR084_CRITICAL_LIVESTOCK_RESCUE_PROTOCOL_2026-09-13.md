# CR084 — critical late-livestock rescue protocol

Status: **FROZEN BEFORE CANDIDATE BUILD / NO HOSTED SUBMISSION**

## Why this is a new architecture, not CR083 retuning

CR083's seed-demand clamp remains immutable. CR084 starts from the exact frozen CR083 package and adds one independent physical-action invariant motivated by live-population forensic evidence. It does **not** change CR083's seed clamp, activation step 434, route-switch thresholds, market logic, or crop exceptions.

Base package SHA-256:

`648fbcdb370f7e48fafda18a1112c5f1b57a17a81b7191f010fe4058f41a41b8`

## Exploratory evidence — spent for architecture design only

The 36-replay CR083 hosted forensic freeze (`34745898829`) is **not promotion evidence** for CR084.

Fresh leaderboard cross-match showed:

- overall CR083: 27W–9L;
- versus current `>=2300` opponents: 0W–4L;
- those four opponents were ranks 145, 461, 479 and 584 at the 2026-09-13T07:47:09 UTC snapshot.

In those four games:

- CR083 was near parity in money through approximately day 26;
- mean CR083 money deficit was only about `-907` at end of day 26;
- mean deficit expanded to about `-2,593` by day 28, `-8,287` by day 29 and `-11,279` at terminal;
- CR083 had roughly 16–17 live animals around day 25 but its selected adaptive route dropped to 8 around day 27 and sometimes 3 by day 29;
- all four stronger opponents retained 17 live animals through terminal;
- route inspection shows the adaptive `YARN_CARROT` and `MILK_GLUT` suffixes intentionally schedule substantially fewer late `FEED` actions than MAIN/YARN;
- exact-observation shadow inspection found many late states where a CR083-controlled unit was standing on an at-risk animal, carried WHEAT, and the route's planned action was an engine-certain noop.

This identifies a concrete candidate mechanism: **prevent avoidable animal escape using only a physical turn that the engine would otherwise ignore**.

Correlation is not causality. Therefore the live sample may motivate the invariant, but cannot validate it.

## Single frozen intervention

CR084 v1 changes only farmer/hand actions satisfying **all** conditions below:

1. `576 <= step < 696` (human days 25–29; never the final day 30);
2. the controlled unit is currently standing on a tile containing a live animal;
3. `fed_today == False`;
4. `consecutive_unfed >= 1` (the animal is at immediate escape risk if another day is missed);
5. that unit's carried private inventory contains at least one `WHEAT`;
6. the exact CR083 action already selected for that unit is engine-certain noop under the existing `_noop(...)` implementation;
7. if all conditions hold, replace only that unit's planned noop with `['FEED']`.

No other action is modified.

### Explicit non-changes

- no CARE repair in CR084 v1;
- no replacement of any non-noop movement/work action;
- no route switch / route tape modification;
- no market action modification;
- no BUY_SEED modification beyond the already-frozen CR083 clamp;
- no HIRE, BUY_ANIMAL, BUY_LAND or SELL change;
- no identity, team name, EpisodeId, hidden seed, future state or opponent-private runtime feature;
- no current-opponent rating or rank in runtime;
- no hosted replay lookup at runtime.

The intervention consumes one carried WHEAT, so it is **not declared weakly dominant a priori**. Its value must be established empirically on fresh local seeds before any further work.

## Build and semantic audit gate

The builder must:

- accept only the exact CR083 SHA above;
- emit a deterministic tarball and manifest;
- rebuild byte-identically;
- compile successfully.

Score-blind shadow audit must run CR083 as the environment driver and compare CR083-shadow versus CR084-shadow on identical exact observations. It must prove:

- no action difference before step 576;
- no action difference at/after step 696;
- market queues identical on every compared step;
- any physical difference is only `noop -> FEED` and satisfies every frozen condition above;
- at least one rescue is exercised;
- no additional farmer/hand difference is allowed.

If any check fails, candidate is invalid before score interpretation.

## Fresh Gate A

Fresh master: **`9140841`**.

- 16 fresh seeds × both seats = 32 games;
- CR084 vs exact frozen CR083;
- isolated package processes; `kaggle-environments==1.32.7`;
- seed firewall must show zero overlap with all earlier masters and CR083 hosted-design audit masters.

PASS requires all:

- exactly 32 games / 16 fresh seeds;
- zero errors / zero non-DONE;
- CR084 score rate `>= 0.5625`;
- CR084 mean terminal-money margin `> 0`.

FAIL decision:

`CLOSE_CR084_CRITICAL_FEED_RESCUE`

No tuning of step 576/696, risk threshold, crop/animal exceptions, or replacement rule on master `9140841`.

## Promotion panel — only after Gate A PASS

Fresh master: **`9140842`**.

32 fresh seeds × both seats = 64 games per row:

- CR084 vs CR083;
- CR084 vs CR071M;
- CR084 vs CR053;
- CR084 vs CR061;
- CR084 vs CR065;
- CR083 vs CR071M;
- CR083 vs CR053;
- CR083 vs CR061;
- CR083 vs CR065.

The extra CR083 rows establish same-master deltas rather than reusing old evidence.

Promotion PASS requires:

- zero errors/non-DONE everywhere;
- direct CR084 vs CR083 score rate `>= 0.5625`;
- direct CR084 mean terminal-money margin `> 0`;
- aggregate guardrail score delta versus CR083 across CR071M/CR053/CR061/CR065 `>= 0`;
- each individual guardrail score delta `>= -0.0625`.

A local promotion PASS does **not** authorize a hosted submission.

## Population-proxy requirement after local PASS

CR084 is the first architecture subject to the new proxy rule. Even after local promotion, it must pass a separate frozen high-strength population stress layer before any hosted probe can be considered.

The existing 36 CR083 hosted episodes are spent exploratory evidence and may not serve as CR084 promotion holdout.

## Decisions

- Gate A FAIL: `CLOSE_CR084_CRITICAL_FEED_RESCUE`.
- Local promotion FAIL: `CLOSE_CR084_CRITICAL_FEED_RESCUE`.
- Local promotion PASS: `ELIGIBLE_FOR_INDEPENDENT_HIGH_STRENGTH_PROXY_ONLY`.
- **There is no automatic hosted-submission path in this protocol.**
