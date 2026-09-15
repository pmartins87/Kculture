# CR089 — integrated physical heterogeneous population result

Date: 2026-09-15  
Authoritative branch: `fix/kaggle-parity-v1`

## Verdict

**CLOSED — `M6S1_FAILS_POPULATION_COMPATIBILITY`.**

Run `34923802262` completed successfully with zero infrastructure or episode failures. The frozen protocol in `docs/strategy/CR089_INTEGRATED_PHYSICAL_POPULATION_PROTOCOL_2026-09-15.md` is binding.

Neither static physical candidate is an eligible population survivor:

- `C5_BASE`: **0W–132L**, 11/11 zero-score edges;
- `C5_M6S1`: **0W–132L**, 11/11 zero-score edges.

Both candidates were mechanically valid in all games. The failure is competitive population compatibility, not execution reliability.

## Frozen evaluation

- master seed: `9270915`;
- 11 opponents;
- 6 fresh seeds per edge;
- both seats;
- 12 games per edge;
- 132 games per candidate;
- exact `kaggle-environments==1.32.7` path;
- original final holdout untouched;
- automatic submission disabled.

Opponent panel:

- `CR053_REAL`;
- `CR052_REAL`;
- `CR083`;
- `CR086`;
- `r01_e108766633_s56156662`;
- `r02_e108761464_s56114097`;
- `r03_e108766659_s56209748`;
- `r06_e108754069_s56205640`;
- `r07_e108766657_s56132899`;
- `r09_e108766659_s56097405`;
- `r10_e108754200_s56210228`.

Aggregate artifact: `cr089-integrated-physical-population-aggregate-v1`, artifact ID `10378934443`, artifact ZIP SHA-256 `086b9aa14b127ee6ce655de00a4e5747d48aaea4e6948cf35a98b60dbe1d9620`.

## Absolute gate

For both candidates:

- mechanically valid: yes;
- mean edge score: `0.0`;
- median edge score: `0.0`;
- worst edge score: `0.0`;
- seat floor: `0.0`;
- edges >= 0.25: `0/11`;
- edges >= 0.50: `0/11`;
- zero-score edges: `11/11`;
- eligible population survivor: **false**.

This fails the predeclared absolute compatibility rule by a wide margin.

## Treatment versus control

W/L coverage was exactly tied at zero:

- mean edge-score delta: `0.0`;
- median edge-score delta: `0.0`;
- improved edges: `0`;
- regressed edges: `0`;
- tied edges: `11`;
- population transfer pass: **false**.

M6S1 nevertheless improved mean monetary margin on 10/11 edges. Averaged across the 11 edge means:

- `C5_BASE`: approximately **-108,777.85**;
- `C5_M6S1`: approximately **-92,211.64**;
- mean edge-margin improvement: approximately **+16,566.20**.

The only edge with a worse M6S1 mean margin was `r07_e108766657_s56132899` (about -4,027.67 versus C5_BASE). The largest positive margin shift was against `r06_e108754069_s56205640` (about +48,209.58).

This cleanly separates the conclusions:

1. **M6S1 remains a real economic/production primitive.** Its E4/E5 causal gains were not invalidated.
2. **Static C5 is not a viable competitive backbone.** A large bank/margin improvement is far too small to bridge its W/L deficit against this population panel.
3. Therefore M6S1 must be preserved as a module for later architectures, but C5/C5+M6S1 must not receive incremental rescue work.

## Binding stopping decision

Close all of the following as direct candidates:

- `C5_BASE`;
- `C5_M6S1`;
- threshold rescue on C5;
- opponent-specific patches on C5;
- immediate CR086/CR088/H1/H1B market factorial on C5;
- hosted submission of either C5 candidate.

Do **not** interpret this as closure of CARE, H10 batching, M6S1, H11 fertilizer conversion or H9 demand modeling. Those mechanisms remain reusable knowledge.

## Next gate

Advance to **CR090 / H9 public-shop adaptive marginal expansion**.

Rationale:

- H9 already proves that public shop composition changes expected remaining demand for MILK/WOOL/EGG;
- B4 shows the fifth animal is genuinely marginal: COW5_DAILY exceeded COW4_DAILY by only +1,497.75 mean with a 4–4 paired sign split, while a sixth CARE animal was decisively negative;
- therefore the fifth capacity slot is the cleanest place to test state-conditioned species allocation;
- E5 already showed that buying a fixed mixed composition at the opening can damage liquidity and M6S1 completion, so CR090 must use a timing-matched deferred marginal slot rather than another fixed opening grid.

CR090 must first compare an adaptive fifth-animal decision against **same-timing static COW and SHEEP controls**. Only a causal pass may proceed to default-environment robustness and then the heterogeneous population panel.

No Kaggle submission is authorized by CR089.
