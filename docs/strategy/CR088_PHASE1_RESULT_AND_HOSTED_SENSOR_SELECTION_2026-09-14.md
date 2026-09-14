# CR088 Phase 1 result and hosted-sensor selection — 2026-09-14

## Outcome

Corrected run `34808258927` completed successfully:

- 42/42 policies mechanically valid;
- zero engine errors and zero non-DONE games;
- 26 overlays passed the frozen non-regression filter;
- original final holdout remained sealed;
- no automatic Kaggle submission occurred during the gate.

The first run `34807533884` is retained as an audit failure, not an economic result.
Its seven unchanged bases were valid, but all 35 overlays selected a helper callable
as the Kaggle entrypoint and therefore played zero games. The only correction was
to expose a fresh final alias for the intended two-argument agent and add an
official-loader smoke. No operator parameter, seed, anchor or threshold changed.

## Hosted calibration before selection

Read-only checkpoint run `34807828323`, observed at
`2026-09-14T04:56:32Z`:

- CR086 submission `56220184`: COMPLETE, 24 episodes, rating `1612.6`;
- CR083 submission `56199767`: COMPLETE, rating `1619.9`;
- exact hosted CR053 submission `56073870`: `2064.8`;
- one submission observed on 2026-09-14 UTC;
- the official competition page states a limit of five agents per day.

CR086 is therefore a mature hosted regression versus CR083, not an initialization
case. Latent-supply ordering is not granted a general hosted-transfer prior merely
because it wins direct local edges.

## Phase-1 interpretation

| Source base | Fresh base mean / robust | Best causal observation | Decision |
|---|---:|---|---|
| Majkel | 0.0000 / 0.0000 | every overlay lost the direct gate | reject this tape |
| SpaTaro | 0.0000 / 0.0000 | nominally eligible overlays still lost 0-24 to anchors | reject this tape |
| ymg_aq | 0.8333 / 0.7500 | order 5-1 direct, no anchor-score change | hold; fresh result is volatile versus Phase 0 and operator class already regressed hosted |
| Orbital | 0.5833 / 0.4583 | base remained stable across independent Phase 0/1 masters | select unchanged base as hosted control |
| feel the agi | 0.3333 / 0.1667 | risk8_p125: 6-0 direct, mean +0.1667, robust +0.2500 | select as causal market sensor |
| Otter | 0.4167 / 0.2083 | order: 4-2 direct, mean +0.1667, robust +0.2500 | hold for later diversity sensor |
| redblackbst | 0.4583 / 0.3958 | order: 5-1 direct, no anchor-score change | hold |

Local scores remain safety/causal evidence only. The exact local league is known to
reverse the hosted CR053/CR083 order.

## Frozen hosted sensors

### CR088A — Orbital coherent base

- variant: `r06_e108754069_s56205640__base`;
- macro family: Majkel / DSM / Orbital;
- source episode: `108754069`;
- source submission: `56205640`;
- operator: unchanged base;
- exact archive SHA-256:
  `24e78d657d6c16371fcc7393fbea4d23ce695fd456e722e37f5398f7866ab16e`;
- intended description: `CR088A_ORBITAL_BASE_24E78D65`.

### CR088B — feel risk-sale overlay

- variant: `r07_e108766657_s56132899__risk8_p125`;
- macro family: Mengfei / feel / redblack;
- source episode: `108766657`;
- source submission: `56132899`;
- operator: legal latent-supply ordering plus at most one premium sale, cap 8,
  price at least 1.25x base, no physical-action change;
- exact archive SHA-256:
  `055fbbcd09dc3112bef3ef7a78965ed09f28ec999283dab87641e60d5cf9d053`;
- intended description: `CR088B_FEEL_R8P125_055FBBCD`.

Only these two sensors are authorized in this selection. The preflight must rebuild
the exact bytes, verify both hashes, use the official loader smoke, recount the
current UTC-day submissions, reject duplicates and require that both submissions
fit under the five-agent daily cap. Two daily slots remain deliberately unused
after the expected total reaches three.
