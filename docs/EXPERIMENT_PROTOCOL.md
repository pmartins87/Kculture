# Experiment protocol — Kculture

## Purpose

Prevent noisy ladder results and cherry-picked matches from driving strategy decisions.

## Every promoted experiment must record

- experiment ID and timestamp
- git commit SHA
- environment/version hash
- agent configuration
- opponent pool versions
- seed set
- episode count
- win/loss/tie counts
- mean/median profit delta
- variance / tail losses
- crash/invalid/no-op rate
- key economic diagnostics
- comparison against current champion

## Experiment IDs

Use `KEXP-YYYYMMDD-NNN-short-name`.

Example: `KEXP-20260827-004-expansion-timing`.

## Evaluation tiers

1. **Smoke:** legal 720-turn completion and zero crashes.
2. **Development:** small fixed seed/opponent set for rapid iteration.
3. **Validation:** larger unseen seed set and champion archive.
4. **Held-out:** reserved opponents/seeds used only for promotion/final selection.

## Promotion rule

A candidate may replace the local champion only when it:

1. completes reliably;
2. beats the champion across enough episodes to overcome obvious noise;
3. does not depend on one narrow matchup;
4. preserves or improves worst-case behavior;
5. is reproducible from committed code/config;
6. passes held-out evaluation for major promotions.

## Ladder submissions

Kaggle submissions are expensive observations, not substitutes for local evaluation. Log exact source/config and reconcile hosted episode behavior with local expectations.

## Failure logging

Preserve concise notes on failed ideas. This is especially important for apparently profitable mechanics that lose due to action cost, timing, market interaction, or matchup effects.
