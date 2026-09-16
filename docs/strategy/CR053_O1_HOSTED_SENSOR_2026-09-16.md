# CR053 vs O1 — hosted sensor round (2026-09-16)

## Purpose

Use Kaggle hosted evaluation as the competitive arbiter. This round deliberately avoids another local competitive gate.

## Slot 1 — contemporaneous control

- File: `R4D_CR053_ROUTE106309334_V1.tar.gz`
- SHA256: `095080e791bd8d58369893c1a421beb57b7f64c2808c011f576e09684ffb9a15`
- This is the exact historical CR053 artifact recovered from workflow run `34105008373`, artifact `10012004237` (`cr052-cr053-hosted-candidates`).
- Historical hosted submission: `56073870`.
- Historical checkpoint: ~2064.8.

## Slot 2 — CR053 + frozen O1

- File: `R4D_CR053_O1_LATENT_PRIORITY_V1.tar.gz`
- SHA256: `47035565c2711373b04989f205ed07bf62105c32ba37766d2c9bcbc7ed6f7d35`
- Base package SHA256: `095080e791bd8d58369893c1a421beb57b7f64c2808c011f576e09684ffb9a15`
- CR053 embedded `main.py` SHA256: `6e5d298797117bc72ad43c06b1d6a37634ad33a16a5c371c8c7e1a0aa5fc4519`
- CR086 donor package SHA256: `11296a4e658f37c109a2cc953be0ea7db8e2fbde6286ac483e0466f52f4af888`
- CR086 embedded `main.py` SHA256: `17a5736eeb8b3f761d08f5e4ec598bc57b9fe34d7e8ce22929a5f89d0005928a`
- Frozen wrapper provenance: `candidates/cr091_cr053_market_option.py` at commit `f49bff2e7adde626b01b9fa3c0413f7fc97d9649`.
- Mechanism: execute exact CR053 action; update the exact CR086 latent-supply state; apply only `_cr086_prioritize` to the CR053 market order list.
- CR086 route/backbone is not executed.
- No threshold retuning.

## Existing evidence for O1

CR091 final run `34990757344`:
- 128/128 valid episodes;
- failures 0;
- parity violations 0;
- exact farmer/hands;
- exact market multiset;
- 1075 reorder activations;
- no edge regression.

CR092 canonical recovered aggregate:
- 264 episodes;
- failures 0;
- violations 0;
- 2057 reorder activations;
- nonnegative 11/11 edges;
- regressions 0/11.

These are safety/causal evidence only; they are not treated as a hosted-score oracle.

## Minimal package sanity for hosted candidate

- Python compile: PASS.
- Module import: PASS.
- callable `agent`: PASS.
- embedded CR053 source hash matches frozen source: PASS.
- embedded CR086 source hash matches frozen source: PASS.
- required donor helpers `_cr086_update` / `_cr086_prioritize`: PASS.
- sequential synthetic calls at steps 0 and 1: PASS.

No additional local tournament is required before hosted submission.

## Stable decision rule

Submit both packages in the same hosted round. Interpret the new CR053 submission as the contemporaneous control and CR053+O1 as the isolated intervention. The next development step must use hosted evidence from this round rather than opening another validation framework.
