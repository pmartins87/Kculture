# Lessons from AgentSec — operational rules for Kculture

Date: 2026-09-06

## Why this exists

The AgentSec competition produced a severe public/private inversion. Public-oriented EXFIL candidates reached the high-80s, while the final/private outcome showed that the project had optimized too strongly for a permissive public proxy and had not preserved enough probability mass on mechanisms that generalized under the hidden regime.

The purpose of this note is not bureaucracy. These are decision rules intended to prevent the same failure mode in Kculture.

## AgentSec failure modes to avoid

### 1. Never let one scalar proxy become the objective

In AgentSec, a single public leaderboard score hid large model/regime differences. Mechanical validation, public score and private robustness were different things.

Kculture rule:
- never promote a candidate from one aggregate number alone;
- keep W/L, margin, opponent/regime breakdown and temporal/current-meta evidence separate;
- a candidate that wins mainly by crushing one narrow opponent family while regressing elsewhere is not automatically the best final agent.

### 2. A mechanically green artifact is not a strategically good agent

AgentSec repeatedly had SDK-valid, CI-green candidates that were still strategically wrong for the hidden evaluator.

Kculture rule:
- compile/package/parity PASS proves deployability only;
- strategy promotion requires actual game evidence;
- never use audit PASS as evidence of expected leaderboard improvement.

### 3. Do not dilute a promising specialist before testing it standalone

AgentSec identified Confused Deputy as a materially different lane but mostly pursued broad mixed hedges and continued optimizing EXFIL. The specialist hypothesis did not receive enough clean hosted evaluation before final selection.

Kculture rule:
- when a materially different strong policy appears, preserve it as its own candidate;
- test it standalone before blending it into CR024 or another anchor;
- if two independent policies survive, keep both alive through hosted calibration rather than immediately averaging/splicing them.

This directly applies to `indar_v1` and `full_recent_top` after CR027/CR028.

### 4. Do not confuse diversity with a hedge

AgentSec's broad private hedge covered many families, but broad coverage diluted the strongest alternative mechanism. A hedge is useful only if it preserves meaningful performance under a different regime.

Kculture rule:
- a 'hybrid' or 'consensus' is not automatically safer;
- do not combine strategies just because they are different;
- blending must earn its place through paired evidence;
- preserve at least one coherent non-anchor policy if it survives independent evaluation.

### 5. Hidden-regime robustness must be approximated deliberately

AgentSec knew the private evaluator could differ but the available private proxies were too assumption-heavy and were not decisive enough.

Kculture rule:
- reserve a genuinely untouched final stress block;
- include temporal shift/current-meta tests using later official episodes where possible;
- include package-aware reactive opponents, not only deterministic tape clones;
- require both seats and fresh seeds;
- do not tune thresholds after seeing the sealed block.

### 6. Read failures per opponent/regime, not only in aggregate

AgentSec's aggregate public score obscured GPT-OSS/Gemma imbalance.

Kculture rule:
- final reports must expose per-opponent results;
- W/L regressions against a specific strong family cannot be hidden by large margin gains elsewhere;
- promotion priority is W/L robustness first, margin second.

### 7. Do not spend the endgame polishing the wrong family

AgentSec invested substantial final effort in increasingly sophisticated public-path EXFIL variants even though the core uncertainty was hidden-regime survival.

Kculture rule:
- once a family saturates, stop micro-tuning it;
- redirect effort toward materially different strong policies and current-meta external benchmarks;
- sophistication is not value unless it changes game outcomes.

### 8. Use Kaggle hosted slots as reality checks on distinct finalists

The costly AgentSec miss was not lack of code quality; it was insufficient direct evidence for the alternative regime before the final decision.

Kculture rule:
- do not waste daily slots on byte-identical repeats unless variance itself is the question;
- use slots on materially different finalists;
- if CR029 leaves two genuinely independent candidates alive, both deserve hosted consideration before forcing a single merged solution;
- hosted reality can override a beautiful local theory.

## Immediate application to CR029 and after

CR029 itself remains frozen and must not be changed mid-run.

After CR029:

1. Keep `cr024`, `full_recent_top`, and `indar_v1` as distinct identities until the evidence eliminates one.
2. Do not create `Indar + Recent + CR024` merely because all three contain useful ideas.
3. If both challengers pass CR029, package both independently first.
4. Before final promotion, run one sealed distribution-shift stress evaluation on untouched seeds/opponents/current official episodes.
5. Inspect per-opponent W/L regressions before aggregate margins.
6. Use Kaggle submissions on materially different survivors, not repeats of the same underlying strategy.
7. Preserve one coherent regime hedge if the final-selection format permits it.

## Decision principle

The target is not the best-looking local experiment and not the prettiest public score.

The target is the agent with the highest probability of surviving the evaluation distribution we do not fully observe.

That means Kculture final selection must optimize for **generalization across opponents, seeds, seats and time**, while still spending hosted slots aggressively enough to learn what the real evaluator rewards.