# V28E — Hosted Opponent-Strength Attribution Result — 2026-09-22

## Binding run

Successful repair-only workflow:
- V28E-R3 workflow: `35807341491`
- job: `107010999757`
- artifact: `10728251773`
- artifact digest: `sha256:48b3daaec4065e5241fac72219888d889bb3998f389caa7e58494c733892b91f`

R1 `35806944875` was mechanically mapping-insufficient because `leaderboard --show` exposed only 20 teams.
R2 `35807122446` successfully downloaded the full leaderboard but failed only because the downloaded CSV uses UTF-8 BOM/title-cased headers.
R3 changed only header parsing. The temporal alignment, exact-match team-name rule, metrics, thresholds, and decision rule remained frozen.

## Mechanical validity

Full leaderboard:
- CSV lines including header: **9873**
- leaderboard teams parsed: **9872**

Exact opponent mapping:
- V47: **89/89 games mapped (100%)**
- ALL3 aligned: **23/23 games mapped (100%)**
- unmapped opponents: **0** for both populations

The same V28D V47 Episode-ID window was preserved:
`112051391..112150695`.

## V47 opponent population

Submission `56466970`.

89 resolved games:
- score rate: **0.5280898876**
- mean terminal margin: **+6198.47**

Opponent public scores:
- mean: **1892.5528**
- median: **1897.2**
- p25: **1770.6**
- p75: **2108.3**
- min: **490.0**
- max: **2784.6**

Outcome by opponent-score band:
- <1500: 10 games, score rate 1.0000, mean margin +55,768.0
- 1500–1799.9: 16 games, score rate 1.0000, mean margin +3,040.625
- 1800–2099.9: 39 games, score rate 0.474359, mean margin +13.62
- >=2100: 24 games, score rate 0.104167, mean margin -2,299.875

## ALL3 temporally aligned opponent population

Submission `56367770`.

23 games in the exact same Episode-ID window:
- score rate: **0.3913043478**
- mean terminal margin: **-1362.61**

Opponent public scores:
- mean: **2239.3739**
- median: **2147.0**
- p25: **1978.85**
- p75: **2501.2**
- min: **1809.9**
- max: **2658.9**

Outcome by opponent-score band:
- 1800–2099.9: 10 games, score rate 0.4000, mean margin -832.5
- >=2100: 13 games, score rate 0.384615, mean margin -1,770.38
- no aligned ALL3 game was against an opponent below 1800

## Frozen decision

Difficulty deltas, ALL3 minus V47:
- mean opponent score: **+346.8211**
- median opponent score: **+249.8**

Both exceed the pre-registered +100 threshold.

Binding decision:

**`V28E_ALL3_FACED_MATERIALLY_STRONGER_POPULATION`**

## Interpretation

V28D's raw W/L comparison was strongly confounded by matchmaking.

The V47's 52.8% realized score rate came from a substantially easier opponent population. In particular:
- 26/89 V47 games were against opponents below 1800, and V47 scored 100% in those games;
- ALL3 had zero temporally aligned games against opponents below 1800;
- ALL3's median opponent was about 250 rating points stronger than V47's median opponent.

Therefore the V47's raw positive W/L record cannot be used as evidence that it is at least as strong as ALL3.

This result does **not** prove V47 is a bad hedge, because hedge quality depends on complementarity to ALL3 rather than only standalone Bradley-Terry strength. It does, however, remove the apparent contradiction between V47's better raw W/L and its lower public score.

## Route

Preserve the current Kaggle pair while research continues:
- primary: ALL3 `56367770`
- hedge: exact V47 `56466970`

No Kaggle mutation is authorized by V28E.

The next useful research gate is a fresh, offline hedge-complementarity benchmark centered on ALL3. Candidate inclusion should not rely on stale hosted ratings; mechanically reproducible independent lineages such as CR053 may be reconsidered alongside V47/O-RW1 and other preserved first-party candidates.

Continue read-only V47 maturity monitoring to >=169 episodes in parallel.
