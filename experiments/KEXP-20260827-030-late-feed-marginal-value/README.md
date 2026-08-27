# KEXP-20260827-030 — late FEED marginal terminal-value audit

Status: **COMPLETE / NARROW FEED SUPPRESSION REJECTED**

## Question

KEXP-027 showed zero FEED at step 695, but did not answer whether some FEED earlier in the final production day (672..695) spends scarce WHEAT without changing terminal animal output. KEXP-030 measures the exact marginal terminal-production value of every frozen-R4B FEED intent in that window.

Replay alignment is exact: observation/state frame `t` is paired with submitted action frame `t+1`.

## Frozen protocol

Unchanged R4B vs deterministic `starter` on all 16 development and 20 exploratory-live-meta environmental seeds. For every FEED intent, compute whether FEED can add any terminal product through the final refresh by preventing escape and/or unlocking already-existing pending CARE bonus, respecting production schedule and `max_held` capacity.

Predeclared candidate gate required:

- zero-value FEED holding WHEAT in >=4/16 development episodes;
- >=5/20 exploratory episodes;
- zero-value FEED >=20% of all valid FEED intents.

## Canonical result

Actions run **`33041367389` — SUCCESS**.
Artifact **`9634066492`**, ZIP digest **SHA-256 `a308f6af34624a4fc63583f93bae4656d21bdcfe85ce6d5d4cd595f7b640648b`**.

Combined 36 episodes:

- valid FEED intents: **331**;
- zero-terminal-production-value FEED: **35**;
- zero-value fraction: **10.574%**;
- episodes with such FEED while actor holds WHEAT: **35/36**.

By mechanism:

- **287** FEED unlock an already-existing pending CARE bonus;
- **9** preserve survival for a due final production;
- **35** occur when no final production is due and therefore have zero terminal-production value.

Development: 16/16 episodes contain a zero-value FEED, but only 16/154 = 10.39% of FEED intents are zero-value.
Exploratory live-meta: 19/20 episodes contain one, but only 19/177 = 10.73% of FEED intents are zero-value.

## Decision

**NO CANDIDATE under the predeclared gate.**

The episode-coverage condition passes strongly, but the 20% action-share condition fails by roughly half. The narrow rule saves approximately one WHEAT per typical episode and has lower expected prize-value than the much larger terminal throughput leak found in final-day WATER.

This result also rules out blanket late FEED suppression: 296/331 FEED intents have a mechanically identifiable terminal role under the model, overwhelmingly through pending CARE bonus.

Late-game engineering priority moves to harvest/drop/sale/labor throughput, beginning with KEXP-032 terminal WATER reallocation.

No validation or held-out seeds were accessed.

Tool blob: `9aa2951b7aa315334d5201a5c10eaaa38c6c3292`.
