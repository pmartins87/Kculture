# V27 frontier replay diagnostic — 2026-08-26

## Scope

Diagnostic-only analysis of complete official-environment replays for the four development seeds where frozen `R4B-market-only-validated-v1` lost at least one seat to exact Kaito V27 V4 in KEXP-011.

Replay Actions run: `32926648674`.

Exact opponent:

- `kaitofukami/25-27-strict-future-v27-midgame-meta-reset/versions/4`
- `main.py` SHA-256 `f48c21166eac68d1b05a401f04f94a2eb6154e65415af64893672365ff33c7b8`.

Seeds captured in both orientations:

- `150614441` — artifact `9591771527`, ZIP SHA-256 `dc9e2aa67ead3d3f6f309294e87792e43d47e29c710e4a7d77d17177cce839da`;
- `1743398262` — artifact `9591768290`, ZIP SHA-256 `36e19860567ab62501aea4e93a7197163c82795564a2dfa9c7a3bedf67f2c8ef`;
- `163219477` — artifact `9591767574`, ZIP SHA-256 `1b7dfe168abfa52388cda3461c5c25af91c3e0cb2a3f478be0612ffd9860f7c4`;
- `598340816` — artifact `9591765107`, ZIP SHA-256 `f0faa638c863548d95d1f1fbeeef0dbdc529a0c7a91284cbefe479b2d78170bb`.

Eight complete replays were inspected. Seven are R4B losses; seed `150614441` in the favorable orientation is an R4B win.

No validation or held-out seed is involved.

## Main finding: the symmetric failures are late collapses

For the three seeds where R4B loses **both seats**, R4B is still ahead on money at step 672:

| Seed | R4B minus V27 at step 672 |
|---|---:|
| 1743398262 | +249 |
| 163219477 | +990 |
| 598340816 | +3,679 |

Yet all six orientations finish as R4B losses.

From step 672 to terminal:

| Seed/orientation | R4B money gained | V27 money gained | Relative late swing |
|---|---:|---:|---:|
| 163219477 A | +5,246 | +9,752 | -4,506 |
| 163219477 B | +5,246 | +9,752 | -4,506 |
| 1743398262 A | +12,459 | +15,196 | -2,737 |
| 1743398262 B | +12,051 | +15,196 | -3,145 |
| 598340816 A | +5,446 | +9,664 | -4,218 |
| 598340816 B | +5,446 | +9,664 | -4,218 |

This is strong evidence that these failures are **not primarily opening failures and not merely missing step-718 liquidation**. The decisive loss of advantage occurs during roughly the final 47 executable turns.

Seed `150614441` is different: the losing orientation is already behind by about 1,119 at step 672 and finishes -5,603. It remains a seat-sensitive regime rather than part of the clean symmetric pattern.

## Aggregate checkpoint trajectory over the seven losing games

Average R4B minus V27 money delta:

| Checkpoint | Mean delta |
|---|---:|
| step 120 | -381.7 |
| step 160 | +326.1 |
| step 192 | -783.7 |
| step 240 | -174.1 |
| step 360 | **+4,692.4** |
| step 480 | **+6,550.6** |
| step 600 | +2,807.1 |
| step 672 | +1,245.3 |
| step 718 | -2,475.7 |
| terminal | -2,728.1 |

The typical losing trajectory is therefore: competitive opening → strong middle-game lead → erosion after ~480/600 → decisive final-two-day collapse.

## Structural differences observed in the seven losses

The values below are descriptive averages, **not causal proof**.

Relative R4B minus V27:

- around step 160: roughly +2 cows, -2 sheep, +1 hand and +1 quadrant; more melon-heavy board;
- around step 240: roughly -0.6 cow, +0.6 sheep, substantially more melon and fewer strawberries; lower notional immediately liquidatable stock in the sampled states;
- around step 360: similar cow count, roughly +2.6 sheep;
- around step 480: similar cow count, roughly +3.1 sheep;
- around step 600: roughly -1 cow, +3.1 sheep, substantially fewer wheat tiles and more strawberry tiles;
- around step 672: roughly -1 cow, +3.1 sheep;
- around step 718: roughly -1 cow, +2.3 sheep and -2 hands.

The agents also differ fundamentally in opening architecture. R4B/COK starts with a more cow-heavy route; V27 opens near the current public 1-cow/4-sheep meta and scales cattle/labor later. Since R4B still wins 25-7 overall, **wholesale copying of V27 is explicitly not supported**.

## Late market / production observations

Across the six symmetric-loss orientations, approximate aggregate behavior in the late window indicates V27 realizes substantially more terminal-period value from wheat/milk/fertilizer, while R4B is relatively more exposed to strawberries/wool. Observed late quantities included roughly:

- HIRE: R4B 18 vs V27 20;
- fertilizer SELL: 21 vs 38;
- milk SELL: 41 vs 53;
- strawberry SELL: 28.3 vs 6;
- wheat SELL: 113 vs 205;
- wool SELL: 29 vs 16.

These figures are **observational only**. Market prices are endogenous and actions are coupled to prior production, crop state, labor and route choices; they do not establish that simply selling more wheat/milk would improve R4B.

## Working hypothesis

The most credible R4D search region is now **late-phase continuation control**, approximately after step 600/672, involving the coupled choice of:

- production mix;
- remaining labor capacity;
- harvest/drop throughput;
- sale timing and product mix;
- stopping/continuing production when too little horizon remains.

The existing step-718 market-only controller remains useful but acts too late to recover value that was never produced, harvested or moved to shed.

## Anti-overfitting boundary

Do not patch these seed IDs or detect Kaito identity.

Before defining R4D, require another current public family to expose the same mechanism. KEXP-012 already found that seed `163219477` loses both seats to exact Rayk V11 as well, making it the first multi-family recurrent hard regime. Andrew V12 exposes a different set of hard regimes, so full Rayk/Andrew replays are the next diagnostic input.

## Status

**DIAGNOSTIC COMPLETE; HYPOTHESIS OPEN, NO STRATEGY MUTATION YET.**
