# CR085 — bounded offline discovery evidence

Status: **EXPLORATORY / SPENT FOR ARCHITECTURE DESIGN ONLY**

This document records the bounded offline analysis that motivated the already-frozen CR085 protocol. No result below may be reused as CR085 validation evidence.

## Data boundary

No live polling was used for this discovery pass. Analysis used only previously frozen artifacts:

- CR083 hosted 36-replay forensic artifact `10314660085` from run `34745898829`;
- full leaderboard snapshot artifact `10313912424`, timestamp `2026-09-13T07:47:09 UTC`;
- exact frozen CR083 package SHA `648fbcdb370f7e48fafda18a1112c5f1b57a17a81b7191f010fe4058f41a41b8`.

The raw 36 replay JSONs expand to roughly 1.15 GB, so they were processed one episode at a time and reduced to day-level public/economic state.

## First finding: animal collapse is not itself causal

The four old frozen opponents rated `>=2300` all beat CR083. Their target live-animal trajectory averaged:

- day 25: `16.5` animals;
- day 26: `8.0`;
- day 28: `5.5`;
- day 29: `5.5`.

However, many CR083 wins exhibit the same deterministic capacity reduction. Across all 36 episodes:

- 18 games reached `<=8` CR083 animals on day 26;
- 12 of those were wins;
- 6 were losses.

Therefore the CR084-style proposition “prevent the animal drop” is not supported. The drop is a route/regime marker, not sufficient evidence of a causal defect.

## Same collapse, different economic cushion

Among the 18 games with `<=8` animals on day 26:

- 12 wins had mean public money lead versus the opponent on day 25 of about **`+10,626`**;
- 6 losses had mean public money difference of about **`-2,127`**;
- CR083 absolute money itself was nearly the same in both groups (~59k), so the discriminating signal was **relative public state**, not an absolute bankroll threshold.

At day 24/25, collapsed winners were also generally less inferior in public productive assets than collapsed losses.

## Correct route reconstruction

A provisional route label based only on market thresholds was rejected after inspecting CR083 `_switch_ok`.

CR083 allows a switch only when target and current route tapes are identical through the switch point. Exact tape first divergences are:

- MAIN vs YARN: step `226`;
- MAIN vs YARN_CARROT: step `226`;
- YARN vs YARN_CARROT: step `360`;
- MAIN vs MILK_GLUT: step `577`;
- YARN/YARN_CARROT vs MILK_GLUT: step `226`.

Therefore the actual legal route graph is:

- MAIN -> YARN at 226;
- YARN -> YARN_CARROT at 360;
- MAIN -> MILK_GLUT at 433;
- a route that already left MAIN at 226 cannot later jump to MILK_GLUT.

This correction is binding for future analysis.

### Actual 36-replay route outcomes

- MAIN: `12W–0L`, mean opponent score ~1314, zero day-26 collapse;
- YARN: `3W–3L`, mean opponent score ~1472, zero day-26 collapse;
- YARN_CARROT: `4W–2L`, mean opponent score ~1820, all six collapse to 8 animals on day 26;
- MILK_GLUT: `8W–4L`, mean opponent score ~1689, all twelve collapse by day 26, generally to 3 animals by day 28.

All four old `>=2300` opponents occurred in the two adaptive capacity-reducing branches:

- Roshan Roy `2589.7`: YARN_CARROT, loss `-3243`;
- Veerakrishna `2584.4`: YARN_CARROT, loss `-3487`;
- Clement Lau `2546.9`: MILK_GLUT, loss `-200`;
- Annsatz `2744.3`: MILK_GLUT, loss `-38184`.

This does not mean those routes are universally bad: both have multiple wins.

## Static maintenance structure

Exact frozen route tapes show the productive-capacity tradeoff directly.

Daily FEED counts:

- MAIN/YARN days 24–27: `17,17,17,17`;
- YARN_CARROT days 24–27: `8,8,8,8`;
- MILK_GLUT days 24–27: `8,8,3,3`.

Thus the adaptive routes intentionally sacrifice animals; CR084 failed because it tried to repair incidental noop opportunities rather than reconsidering whether entering that macro tradeoff was appropriate.

## Why simple price-rebound logic was not enough

Milk price often rebounds after cows disappear, but not universally. Example:

- Roshan Roy: MILK price rose from ~17 on day 25 to 108 on day 29;
- Vladimir Babin: ~34 -> 114;
- Annsatz: MILK remained at price floor `1` through terminal despite the catastrophic loss.

Therefore “keep cows because MILK will rebound” is not a universal causal explanation and was not used as the CR085 rule.

## Public Pareto guard — exploratory discrimination

A zero-threshold public state vector was tested:

- farm money;
- live animals;
- active plants.

`Pareto dominant` means CR083 is `>= opponent` in all three current public dimensions. No fitted weights or margins are used.

### At the natural YARN -> YARN_CARROT switch (step 360)

Actual YARN_CARROT branch in the frozen sample:

- both losses failed the public Pareto test;
- 2/4 wins passed;
- the 2 wins that failed were relatively small wins compared with the strongest wins in the branch.

High-strength losses:

- Roshan Roy: money `-2662`, animals `0`, plants `0` -> guard false;
- Veerakrishna: money `-2494`, animals `-1`, plants `0` -> guard false.

### At the natural MAIN -> MILK_GLUT switch (step 433)

All 4 MILK_GLUT losses failed the guard. Five of eight wins passed; three smaller wins failed.

Examples among losses:

- Clement Lau: money `-1616`, animals `0`, plants `0` -> false;
- Annsatz: money `-2686`, animals `-1`, plants `-1` -> false;
- Vladimir Babin: money `-543`, animals `0`, plants `0` -> false;
- Adhiraj Jagtap: money `-5423`, animals `-5`, plants `-1` -> false.

The exploratory evidence therefore supports a **state-eligibility guard at an already-existing prefix-compatible decision**, not a late route transplant.

## Why CR085 is architecturally distinct

CR085 does not:

- transplant a public replay route (CR080 class);
- transplant time-indexed market actions (CR081 class);
- imitate a teacher state/action map (CR082 class);
- repair late animal FEED noops (CR084 class);
- retune the original CARROT/MILK market thresholds.

It asks a different causal question:

> when an existing prefix-compatible adaptive branch trades future productive capacity for a market-regime response, should that branch be entered if our current **public farm state is already inferior** to the opponent?

Rejecting a switch leaves the agent on its already-consistent route; there is no state aliasing or mid-tail stitching.

## Frozen next step

Protocol frozen before build:

`docs/strategy/CR085_PARETO_GUARDED_ADAPTIVE_SWITCH_PROTOCOL_2026-09-13.md`

Protocol commit:

`518e11e4bf2ad3fa5d81876366244747c8385c68`

Fresh masters:

- semantic/audit firewall namespace: `91508509`;
- Gate A: `9150851`;
- promotion: `9150852`.

The 36 episodes in this document are spent. CR085 succeeds or fails on fresh seeds and, only after local promotion, on a future temporal high-strength proxy frozen after the protocol date.
