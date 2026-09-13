# CR084 — final result

Status: **CLOSED / DO NOT RETUNE**

CR084 tested one frozen physical-action mechanism on top of exact CR083: during steps `576 <= step < 696`, replace only engine-certain noop actions with `FEED` when a controlled unit stood on an immediately at-risk live animal, had not fed it that day, and carried WHEAT.

Frozen corrected candidate SHA-256:

`3aa08bb2ee163d1707dbf0bf9d2cb4b6f8c194fa2dbd715c38a67a4a41d414a2`

Base CR083 SHA-256:

`648fbcdb370f7e48fafda18a1112c5f1b57a17a81b7191f010fe4058f41a41b8`

## Invalid first implementation

The first implementation inserted FEED before final market logic and could indirectly change `room_guard` market behavior. It was quarantined before score interpretation. No score from that implementation is strategy evidence.

## Corrected semantic audit

Canonical corrected Gate-A run: `34758074656`.

Score-blind shadow audit:

- 5,752 compared steps;
- 23 exercised rescue actions;
- 21 COW, 2 SHEEP;
- 0 market mismatches;
- 0 invalid physical differences;
- deterministic byte-identical rebuild;
- seed firewall clean.

Therefore the corrected candidate was semantically valid.

## Gate A

Master `9140841`, 16 fresh seeds × both seats = 32 games.

CR084 vs CR083:

- 11W–7L–14T;
- score rate `0.5625`;
- mean terminal-money margin `+140.6875`;
- 0 errors / 0 non-DONE;
- paired 95% bootstrap interval `0.4375–0.6875`.

This met the pre-frozen numerical Gate-A threshold exactly, but was not statistically decisive.

## Frozen promotion panel — FAIL

Canonical promotion run: `34758417896`.
Master: `9140842`, 32 fresh seeds × both seats = 64 games per row.

Direct CR084 vs CR083:

- 12W–10L–42T;
- score rate **`0.515625`**;
- mean terminal-money margin **`-106.625`**;
- zero errors / non-DONE.

Guardrail deltas versus same-master CR083:

- CR071M: **`-0.125`**;
- CR053: `+0.03125`;
- CR061: `0`;
- CR065: `0`;
- aggregate delta: negative.

Pre-frozen promotion checks failed:

- direct score rate `< 0.5625`;
- direct mean margin not positive;
- aggregate guardrail delta negative;
- individual CR071M delta below `-0.0625`.

Decision: **`CLOSE_CR084_CRITICAL_FEED_RESCUE`**.

## Independent temporal high-strength proxy — also FAIL

Run `34758785488` evaluated a holdout window frozen after the CR084 protocol commit: public CR083 episodes created from `2026-09-13T08:00:31Z` through `2026-09-13T12:55:00Z`.

- 36 completed public episodes in the frozen temporal window;
- 6 matched opponents with rating `>=2300`;
- 5 of those 6 were CR083 losses;
- exact CR083 base-action reproduction: 100%;
- semantic fidelity: 100%;
- **0 unique first-rescue opportunities**;
- **0 confirmed preventable escapes**;
- **0 high-strength losses aligned with a preventable escape**.

The workflow's final artifact upload failed only because Kaggle's downloaded leaderboard filename contained `:` characters, which GitHub artifact upload rejects. The analytical step itself completed and returned the substantive FAIL above. No rerun is required because CR084 was already closed by the promotion panel.

## Interpretation

The strong-opponent livestock-retention correlation from the earlier exploratory sample was not a portable causal mechanism. A small local Gate-A uplift did not survive a larger fresh direct panel, and the independent temporal high-strength holdout contained no actual instances of the proposed rescue mechanism.

Binding conclusion:

> **Late animal attrition is not a validated causal bottleneck for CR083. Do not tune the FEED window, risk threshold, animal exceptions, or rescue rule.**

Future work must return to economic-state decomposition of high-strength losses and identify a genuinely different mechanism before building CR085.
