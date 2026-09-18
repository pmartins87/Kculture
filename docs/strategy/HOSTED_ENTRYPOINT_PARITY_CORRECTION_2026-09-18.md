# Hosted EntryPoint Parity Correction — 2026-09-18

## Discovery

The authorized O-RW1 hosted A/B exposed a loader mismatch.

Exact hosted control V47 was loaded by Kaggle as:

`_y_agent_shopherd`

The O-RW1 treatment package was loaded as:

`_kc_orw1_wool`

instead of the intended wrapper.

The official loader evidence came from the submission workflow itself:

```
control _y_agent_shopherd 2
treatment _kc_orw1_wool 1
```

Hosted treatment replay `110482337` then confirmed the failure mechanically:
the Kculture side emitted `PASS / [] / []` from step 0 through the end and finished with
reward 3000. The self-team replay `110481069` was PASS-only on both sides and ended
3000-3000.

Therefore submission `56333579` is **not a valid O-RW1 competitive sensor**.

## Root cause

The public V47 source retains an older top-level symbol named `agent`, but appends later
wrappers. Its true Kaggle-hosted entrypoint is the last callable created while executing
the source, `_y_agent_shopherd`.

Kculture's helper `load_public_agent()` incorrectly imported `mod.agent`.
That is not equivalent to Kaggle's hosted loader.

The first O-RW1 package also appended helper functions and then redefined the existing
name `agent`. Rebinding an existing dict key does not move that key to the end of the
globals insertion order, so Kaggle's `get_last_callable` selected the newly-created
helper `_kc_orw1_wool` instead.

## Evidence invalidated / downgraded

Until rerun with the official hosted loader, do **not** use the following as competitive
promotion evidence:

- Adaptive Wrapper Proposal Oracle V2b run `35310754131`;
- first-party O-RW1 causal run `35311750191`;
- O-RW1 one-shot runtime run `35313204723`;
- O-RW1 package parity run `35360173417`;
- hosted treatment submission `56333579`.

The exact CONTROL submission `56333577` remains a valid exact-public-V47 hosted sensor.

Earlier experiments that explicitly depend on `tools.programme_adaptive_expert_gate.load_public_agent`
must be treated cautiously until their entrypoint identities are audited. This correction
does **not** invalidate unrelated historical experiments that used official packages /
loaders through other infrastructure.

## Infrastructure fix

Commit `b78477bdd80d51bfb63333ab2017c6242131d6d2` changes
`load_public_agent()` to Kaggle's official
`kaggle_environments.agent.get_last_callable`.

The corrected O-RW1 builder captures the true existing last callable before adding any
new helper and defines a uniquely-named final hosted entrypoint
`_kc_orw1_entrypoint`. It also fails closed unless:
- exact public V47 loader resolves to `_y_agent_shopherd`;
- candidate loader resolves to `_kc_orw1_entrypoint`.

## Recovery protocol

Do not submit another O-RW1 package yet.

1. Re-run the frozen first-party O-RW1 causal gate with official hosted loading.
2. Only if that passes, re-run one-shot runtime transfer with official hosted loading.
3. Only if runtime passes, rebuild the package and require official-loader action/reward
   parity.
4. Only then consider a corrected hosted sensor.

No O-RW1 threshold/product/quantity/step tuning is allowed during recovery.
