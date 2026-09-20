# ALL3 V11A Hosted Hard-Population Refresh Protocol — 2026-09-20

## Motivation

V10A closes V48-residual market imitation as the next option source.

The previous hosted hard-population collection `35459722091` targeted O-RW1 submission `56336027`, not the current ALL3 policy.

The first ALL3 hosted snapshot `35465520238` contained only 34 resolved games (28W–6L) and was explicitly an early informative snapshot.

The current discovery source must therefore be refreshed from the current ALL3 hosted submission itself.

## Target

Submission: **ALL3 `56367770`**.

Collect up to the newest **128 public replays** currently available.

Target team name:
`Paulo Martins`.

## Outputs

Produce:
- full hosted forensics summary;
- W/L/tie and score rate;
- unique-opponent count;
- loss-opponent table sorted first by repeated losses, then mean losing margin;
- worst 25 individual losses;
- close-loss subset with margin in [-1000,0);
- repeated-loss opponents with >=2 observed losses.

Opponent identity is **offline forensic metadata only** and is prohibited as a runtime policy feature.

## Gate

This stage is descriptive; it does not promote an option.

If >=64 resolved games and >=10 losses are available:
- `V11A_HOSTED_HARD_POPULATION_READY`;
- next step must derive mechanism hypotheses from loss replay state/action structure, not merely opponent names.

If fewer:
- `V11A_HOSTED_SAMPLE_STILL_THIN`;
- retain as descriptive evidence and avoid overfitting to a handful of episodes.

No automatic Kaggle submission.
