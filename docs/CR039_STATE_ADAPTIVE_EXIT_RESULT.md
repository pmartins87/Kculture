# CR039 — State-adaptive rank5 exit result

Date: 2026-09-06
Workflow run: `34040596297`
Head: `83405b45a33f950efd6896057ebc4721ad581543`

## Mechanical result

- workflow: SUCCESS
- reference parity: PASS
- errors: 0
- fresh validation touched: false
- held-out touched: false
- runtime identity features: false

## Frozen references on the already-open 24-game panel

### CR029

- W/L: 12 / 12
- score: 12 / 24
- mean delta: +10,673.58

### Full rank5 selector

- W/L: 15 / 9
- score: 15 / 24
- paired score gain vs CR029: +3
- favorable conversions: 4
- unfavorable conversions: 1
- mean paired delta gain vs CR029: -8,491.29
- mean delta: +2,182.29

## Best CR039 rule

The best frozen state-adaptive rule was:

- enter the rank5 lineage only under the pre-existing public regime selector at clock 24;
- evaluate at clock 168;
- public feature: `opp_animal_sheep`;
- if `opp_animal_sheep <= 3.0`, exit rank5 and resume CR029;
- otherwise remain on rank5.

This rule uses public state only. It does not use opponent name, team, rank, episode ID, seed or submission identity.

### Result

- W/L: 16 / 8
- score: 16 / 24
- paired score gain vs CR029: **+4**
- favorable conversions: **4**
- unfavorable conversions: **0**
- mean delta: **+9,214.92**
- mean paired delta gain vs CR029: -1,458.67
- margin improvement vs full rank5: **+7,032.63**

Decision: `CR039_PROMOTE_BEST_RULE_TO_FRESH_VALIDATION`.

## Interpretation and anti-overfit warning

CR039 improves the known W/L conversions of full rank5 while eliminating its known regression and recovering most of the margin damage. This is a meaningful result, but the rule was discovered and evaluated on the same already-open 12-scenario family used by CR035/CR036. Therefore this result is not sufficient for package promotion by itself.

The next step is a genuinely fresh reactive validation on unseen seeds against pinned executable opponents. In parallel, an independent live-meta/economic scan must continue so that CR039 does not become the project's only theory.
