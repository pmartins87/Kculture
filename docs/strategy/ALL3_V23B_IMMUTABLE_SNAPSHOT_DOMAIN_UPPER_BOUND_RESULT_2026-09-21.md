# ALL3 V23B Immutable Snapshot Domain Upper Bound — Result — 2026-09-21

## Binding result

Workflow: **`35632311093`**  
Aggregate job: `106449044810`  
Final artifact: `10656170070`  
Digest: `sha256:6d626768832cd29029094bc8d4f129e6f78acece250fa39a67ed51530520509f`

Mechanical status:
- 4/4 shards success;
- 93 hard contexts;
- 4 modes each;
- **372/372 exact rows**;
- 0 failures;
- V23A immutable snapshot used;
- no live Kaggle source reacquisition.

Decision:

**`V23B_CROSS_DOMAIN_INTERACTION_HEADROOM`**

Frozen router output:

**`ARCHITECTURAL_INTERACTION_RESET`**

## Domain results

### MARKET_ONLY

- improved-score contexts: **18/93**;
- improved source SHAs: **9**;
- improved functional clusters: **6**;
- improved seeds: **1** — only `79301`;
- mean score delta: **+0.1935483871**;
- mean margin delta: **-12503.5376**;
- regressed-score contexts: 0.

The frozen gate requires >=2 improved seeds. Therefore MARKET_ONLY does **not** pass.

### PHYSICAL_ONLY

- improved-score contexts: **0/93**;
- improved seeds: 0;
- improved sources: 0;
- mean score delta: 0;
- mean margin delta: **-4181.9570**;
- regressed-score contexts: 0.

PHYSICAL_ONLY does **not** pass.

### FULL_SHADOW

- improved-score contexts: **81/93**;
- improved source SHAs: **9**;
- improved seeds: **5/5 hard seeds**;
- mean score delta: **+0.4838709677**;
- mean margin delta: **+3246.3226**;
- regressed-score contexts: 0.

FULL_SHADOW passes the frozen interaction-ceiling gate with large headroom.

## Interaction-exclusive evidence

Among the 93 exact hard contexts:

- **63** improve under FULL_SHADOW while neither MARKET_ONLY nor PHYSICAL_ONLY improves score;
- these 63 contexts span **9 source SHAs**;
- **6 functional clusters**;
- **4 seeds**: `79302, 79304, 79305, 79306`.

This is strong evidence that the missing capability is not a market-only rule or a physical-only rule. The gain depends on coordinated trajectory changes across both domains.

## Routing consequence

Per the frozen V22/V23 router:

- do **not** open a MARKET-only option;
- do **not** open a PHYSICAL-only option;
- do **not** return to V19 schedule subsets, V20 state-tree tuning, V21 category combinations, or old threshold search;
- open one architectural interaction-discovery family;
- discover the earliest recurrent coupled market/physical divergences across multiple functional clusters;
- at most one interaction controller may proceed to causal testing;
- any controller must be identity-free and use legal runtime state;
- FULL_SHADOW is an offline upper bound, never a deployable option;
- no Kaggle submission is authorized.

Next block:
`V24A_COUPLED_DIVERGENCE_TRACE_DISCOVERY`.
