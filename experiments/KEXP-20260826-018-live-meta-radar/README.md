# KEXP-20260826-018 — official live-meta radar

Status: **FIRST SCREEN COMPLETE / EXPANSION ACTIVE / OBSERVATIONAL**

## Motivation

The hosted R4B submission is valid (`Complete`) but its visible rating moved **161.6 → 135.7**, while the same frozen policy scores 81-15 against our three exact public benchmark snapshots. This is a large local/hosted contradiction.

The official Kaggriculture ecosystem publishes a daily Episodes index and per-day replay datasets. Those replays sample agents that are **actually playing in the current ladder**, including strategies whose source code may be private. This is a more direct calibration source than repeatedly tuning only against Kaito V27, Rayk V11 and Andrew V12.

## First screen execution

GitHub Actions run **`32976184254`** — SUCCESS.

Compact artifact:

- artifact ID `9609551447`;
- ZIP SHA-256 `a1862766f900b0c0591d64751db069c8f6e1d394b336bb2f28ed29771bfeec69`.

Latest official index date at execution: **2026-08-25**.

- daily episode count: **688**;
- median `avg_score`: **2761.313513**;
- top `avg_score`: **3069.552857**;
- selected top-five episode scores: `3069.552857`, `3068.856674`, `3068.856674`, `3068.579401`, `3066.290712`.

## First top-five result

The five winners came from two distinct high-performing strategy families, represented in replay metadata by `Crop Dusta` and `Ryo Hasegawa`.

Winner aggregate across the five episodes:

- mean terminal money: **118,244**;
- mean movement share: **52.47%**;
- mean PASS share: **4.94%**;
- mean productive-action share: **42.58%**;
- all five final winner farms used **3 quadrants**;
- mean seed buys included wheat 122.4, strawberry 30.2, carrot 21.4, melon 15.2, tomato 3.6;
- mean sales included wheat 1630.8, fertilizer 226.8, wool 219.0, strawberry 205.6, milk 185.2, melon 89.6, carrot 52.2 and tomato 23.6.

The five winner terminal animal/crop compositions were heterogeneous rather than one fixed terminal farm:

- `2C/7S/0G`;
- `7C/2S/0G`;
- `14C/4S/0G`;
- `1C/6S/0G`;
- `10C/2S/0G`.

This is evidence that the current high-Elo meta contains materially adaptive economic strategies and that our fixed three-opponent panel is too narrow to serve as a calibrated proxy for the live field.

## Late-herd-exit observation — hypothesis only

A striking pattern appears in one top family (`Crop Dusta`): in several episodes it carries a large cow/sheep herd around step 672 and aggressively reduces it by terminal time.

Observed winner herd-count changes (`COW + SHEEP`) from step 672 to 719 in the five top episodes:

- episode `99288626`: 20 → 9 (**-11**);
- episode `99625995`: 18 → 9 (**-9**);
- episode `99594187`: 18 → 18 (**0**) for the winning Ryo family;
- episode `99373065`: 20 → 7 (**-13**);
- episode `99443787`: 12 → 12 (**0**) for the winning Ryo family.

Mean across winners: **-6.6 animals**, but the mixture is bimodal: Crop Dusta often exits aggressively while Ryo often maintains a smaller/stable herd.

Comparison with the frozen KEXP-014 public benchmark replays shows that R4B and Kaito/Rayk/Andrew almost never exhibit an exit of this magnitude. Across R4B's 96 public-panel games, candidate herd reduction from 672→719 averages roughly **0.84 animals in wins and 0.4 in losses**; public opponents are essentially 0 in those same reports.

This observation is especially relevant because multiple Kculture hard losses are still ahead around step 672 and reverse during the final ~47 turns. However, **correlation is not a policy recommendation**. The mechanism must be checked against official animal pickup/sale economics and a broader live sample before any candidate is changed.

## Policy-use boundary

Opponent/team identity is **never** a deployable feature. Episode IDs are never policy features. The dataset is for discovering general strategic patterns and calibrating our lab to the actual live meta.

## Next falsification steps

1. Expand from top 5 to a broader high-Elo band before concluding that late herd exit is generally valuable.
2. Inspect exact official mechanics and top-replay actions used to reduce herds: pickup, market sale, replacement/redeployment and timing.
3. Compare live winners/losers within matched episodes so strategy-family effects are separated from simple outcome correlation.
4. If the mechanism remains strong, create a **development-only late-exit counterfactual** with one narrow intervention; do not modify hosted R4B yet.
5. Add new exploratory development seeds and more current strategy families so the same original 16×3 panel cannot dominate decisions.
6. Any changed policy still needs full cross-family W/L evidence, exact freeze and fresh validation before a second submission.

## Data separation

- does not consume frozen validation seeds;
- does not consume held-out seeds;
- all 32 held-out remain sealed.
