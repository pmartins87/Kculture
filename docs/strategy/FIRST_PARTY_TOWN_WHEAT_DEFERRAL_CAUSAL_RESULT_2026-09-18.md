# O-TW1 Town-WHEAT Deferral Causal Result — 2026-09-18

Workflow `35378191104`, exact engine `1.32.7`, official hosted loader.

## Result

- 48 valid branch states;
- zero failures;
- mean W/L score delta **+0.125**;
- **14 non-win -> win flips**;
- **0 win -> non-win regressions**;
- 14 positive-W/L states;
- 2 negative-W/L states;
- 32 neutral-W/L states;
- median margin delta **+30**.

Per opponent:
- V47 mirror: score delta **+0.375**, 14 positive flips, 2 tie->loss regressions;
- V48: W/L neutral, mean margin **+38**;
- Tactical Memory: W/L neutral, mean margin **-1266.1875**.

Binding verdict:
**`TOWN_WHEAT_DEFERRAL_CAUSAL_PASS_SAFE_OPTION`**.

Interpretation:
O-TW1 demonstrates real causal W/L headroom on the hosted-faithful V47 backbone, but it
is not universally safe. The two V47 tie->loss regressions and Tactical Memory money
downside forbid describing it as monotone. Do not tune from these seeds.

Next gate:
autonomous one-shot runtime transfer on fresh seeds, same frozen public-state operator,
no Kaggle submission.
