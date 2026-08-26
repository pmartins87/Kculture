# KEXP-20260826-018 — official live-meta radar

Status: **TOP-20 SCREEN COMPLETE / OBSERVATIONAL**

## Motivation

The hosted R4B submission is valid (`Complete`) but its visible rating moved **161.6 → 135.7**, while the same frozen policy scores 81-15 against our three exact public benchmark snapshots. This is a large local/hosted contradiction.

The official Kaggriculture ecosystem publishes a daily Episodes index and per-day replay datasets. Those replays sample agents that are **actually playing in the current ladder**, including strategies whose source code may be private. This is a more direct calibration source than repeatedly tuning only against Kaito V27, Rayk V11 and Andrew V12.

## First screen — top 5

GitHub Actions run `32976184254` — SUCCESS.

- artifact `9609551447`;
- ZIP SHA-256 `a1862766f900b0c0591d64751db069c8f6e1d394b336bb2f28ed29771bfeec69`.

Latest official index date at execution: **2026-08-25**.

- daily episode count: **688**;
- median `avg_score`: **2761.313513**;
- top `avg_score`: **3069.552857**.

The first five episodes exposed two high-performing families, `Crop Dusta` and `Ryo Hasegawa`, and suggested aggressive late herd reduction in the former. Because five episodes were too small to promote any mechanism, the screen was expanded before policy work.

## Expanded top-20 screen

GitHub Actions run **`32977177944`** — SUCCESS.

- artifact `9609951191`;
- ZIP SHA-256 `ec15ee2b2d5827e517af85e7018a7dcfe79a0b94f78ec574c17f30893b5b6964`;
- selection: 20 highest-`avg_score` episodes from the 2026-08-25 official manifest;
- score range: **3069.552857 → 3056.613226**;
- 40 player-games total;
- exactly two team labels in this top band: `Crop Dusta` and `Ryo Hasegawa`, 20 player-games each;
- winners: **Crop Dusta 14**, **Ryo Hasegawa 6**.

Winner aggregate:

- mean terminal money: **105,459.2**;
- movement: **53.97%** of unit actions;
- PASS: **4.22%**;
- productive actions: **41.81%**;
- all winners used 3 quadrants;
- mean seed buys: wheat 114.6, strawberry 33.25, carrot 23.2, melon 16.65, tomato 5.25;
- mean sales: wheat 1709.45, fertilizer 205.9, strawberry 219.3, milk 182.7, wool 171.9, melon 91.35, carrot 64.1, tomato 34.75, egg 8.65.

Terminal farms are highly heterogeneous rather than one fixed farm template. That is evidence for adaptive economics rather than a single universally dominant cow/sheep layout.

## Strong late-horizon signal

Across all 20 top episodes:

- **winner mean herd reduction, step 672→719: 5.8 animals**;
- **loser mean herd reduction: 1.25 animals**.

The effect is concentrated in `Crop Dusta`, not universal across all successful strategies. `Ryo Hasegawa` often maintains a smaller/stable herd. Within the Crop Dusta family itself, winning trajectories reduce substantially more herd than losing trajectories, so the signal is stronger than a simple between-team correlation, but it remains observational.

Most of Crop Dusta's reduction occurs by step 696. Species-level inspection of winning trajectories indicates a mix of cow and sheep exit, with sheep reduction larger on average. The official engine has no animal resale action: a placed animal disappears only through the starvation/escape path, leaving its pasture/coop. Therefore this pattern represents deliberate late cessation of maintenance rather than selling livestock.

## Action-window mismatch versus Kculture

Top-20 **winner** means:

| Window | FEED | CARE | HARVEST | DROP | PASS | movement | sell qty |
|---|---:|---:|---:|---:|---:|---:|---:|
| 600-671 | 37.55 | 30.15 | 65.9 | 4.8 | 16.05 | 460.0 | 193.5 |
| **672-695** | **3.85** | **0.05** | **21.15** | **4.3** | **21.35** | **163.75** | **75.4** |
| **696-718** | **0** | **0** | **21.85** | **15.7** | **30.05** | **165.7** | **168.25** |

By contrast, across R4B's 96 KEXP-014 public-panel games, the candidate averages approximately **9.75 FEED + 8.75 CARE actions during 672-695**, with almost no herd exit; it also stops FEED/CARE entirely during 696-718. Thus the key mismatch is not the final day itself. It is the **penultimate-day maintenance/exit decision**.

This is consistent with our independent late-collapse observation: several Kculture losses are still ahead at step 672 and reverse during the final ~47 turns.

## Exact engine interpretation

Frozen official engine commit `28b6d8af3ce73926b3d0fda1410c1ddd8384ab8c` establishes:

- animals escape after two successive end-of-day refreshes without feed;
- FEED consumes one wheat;
- CARE only banks a bonus that can be paid on a later scheduled production if that animal is fed;
- the end-of-day refresh after step 695 is the **last end-of-day refresh of the season**;
- steps 696-718 have no subsequent end-of-day production cycle before terminal reward;
- terminal reward is bank money.

Important implication: CARE performed during steps 672-695 can only bank a bonus for a production cycle that never occurs after that last refresh. Such CARE has no direct terminal-production value. FEED during 672-695 is more nuanced because it may protect an already-starving animal and may unlock an existing pending CARE bonus on the step-695 scheduled production. A future candidate must therefore be state-aware rather than blindly deleting all FEED.

## Policy-use boundary

Opponent/team identity is **never** a deployable feature. Episode IDs are never policy features. The dataset is for discovering general strategic patterns and calibrating our lab to the actual live meta.

## Disposition

1. Keep hosted R4B immutable.
2. Do **not** promote late herd exit from one day's sample.
3. Open KEXP-019: longitudinal official-meta falsification across multiple recent dates.
4. If the late stop-investment/exit signal survives across days/families, create a narrow development-only state-aware counterfactual.
5. Any changed policy must then beat diverse controls in W/L, freeze exactly, and pass a fresh validation gate before submission #2.
6. Validation and all 32 held-out seeds remain untouched by this observational work.
