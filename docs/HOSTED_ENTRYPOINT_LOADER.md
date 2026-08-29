# Kaggle hosted Python entrypoint invariant

## Incident — 2026-08-29

The first hosted CR-008 and CR-011 calibration submissions failed immediately with:

```text
TypeError: _ka_apply() missing 2 required positional arguments: 'player' and 'step'
```

The archives were structurally valid and `module.agent` imported locally.  The failure came from a mismatch between that test and Kaggle's Python-file loader.

## Root cause

For a Python source-file agent, `kaggle-environments` executes the file and selects the last callable from the resulting namespace (`get_last_callable`).  Redefining an existing dictionary key named `agent` does not move that key to the end of Python insertion order.  The adaptive overlay defined helper callables after the original base agent key had first been inserted, so the hosted loader selected a helper (`_ka_apply`) instead of the intended two-argument `agent`.

## Permanent invariant

Every generated Kaggriculture submission package must be tested through the same file-path loading route used by `kaggle-environments`, not only by importing `module.agent`.

Required pre-submission checks:

1. `get_last_callable(main_source, path=...)` selects the intended agent callable.
2. The selected callable accepts the Kaggle observation/configuration contract.
3. The packaged `main.py` runs a complete 720-step episode from each seat when passed to `env.run()` by file path.
4. Source/package action parity is tested separately after the hosted-entrypoint check.

## First corrected evidence

Workflow: `hosted-entrypoint-regression-fixed`, run `33236373300`.

Corrected CR-008 and CR-011 packages both passed:

- selected callable: `agent`;
- positional argument count: 2;
- both seats completed with `DONE/DONE`;
- engine: `kaggle-environments==1.32.7`.

This check is now mandatory for all future hosted packages, including CR-015/CR-020 and later candidates.
