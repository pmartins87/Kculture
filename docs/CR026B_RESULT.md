# CR026B rank-10 fresh-gate result — 2026-09-05

## Decision

**REJECT — do not submit CR026B.**

Workflow `33993000544` evaluated the preregistered rank-10 backup from the CR026 screen with independent seeds, three accessible reactive public opponents, and a deterministic 20-game hosted counterfactual sample excluding all twenty CR026A hosted episodes.

## Valid completed evidence

### Package / direct

- deterministic package built successfully;
- 1,438 clock checks passed;
- file entrypoint parity passed in both seats;
- no runtime network required;
- fresh direct replication versus CR024: **8/8 wins-equivalent**;
- package SHA256: `2e40e2b6deda33cd5bbd368a2292aed98e4eb39e2cb128ae41eb290831518658`.

Direct superiority to CR024 is therefore real but insufficient for promotion.

### Reactive panel

Aggregate paired result versus CR024 over Rayk V23, Boatlee V2, and Prvsiyan V10:

- score gain: **-4**;
- regressions: **4**;
- improvements: **0**;
- mean relative-margin gain: **-9,936.54**.

Per opponent:

- Rayk V23: score gain 0, regressions 0, mean margin gain **+3,268**;
- Boatlee V2: score gain **-4**, regressions **4**, mean margin gain **-26,445.5**;
- Prvsiyan V10: score gain 0, regressions 0, mean margin gain **-6,632.125**.

The Boatlee shard alone is enough to reject the pure rank-10 route.

### Fresh hosted counterfactual panel

Twenty new CR024 public hosted episodes were selected deterministically and none overlapped the CR026A panel.

- paired W/L score gain: **0**;
- improvements: **6**;
- regressions: **6**;
- mean relative-margin gain: **+2,731.05**.

The route changes outcomes but does not improve net W/L and is too unstable for promotion.

## Conclusion

Both recent pure `keiz` routes (rank 5 and rank 10) dominate CR024 in direct tape-vs-tape tests yet lose robustness once opponents react. The failure is architectural, not packaging or clock execution. Do not spend another ladder submission on a pure route replacement from this lineage.

## Next direction

CR027 should stop searching only within our ~1600 lineage and screen exact packages from current public frontier notebooks that have demonstrated roughly 2.6k–2.9k public ratings. The goal is to establish a much stronger external baseline first, then improve or adapt it with attribution and independent fresh gates rather than continuing incremental CR024 tape mutations.
