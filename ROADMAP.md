# ROADMAP — Kculture live plan

Updated: 2026-09-13

Objective: maximize probability of a prize-winning / top-10 Kaggriculture finish. Working source of truth is branch `fix/kaggle-parity-v1`, `STATUS.md`, and frozen experiment protocols.

## Invariants

1. Hosted/live evidence and exact-reference W/L both matter.
2. Submission allowance is a cap, not a quota.
3. Every candidate family gets a predeclared gate before validation results are interpreted.
4. Invalid evaluations are quarantined; their scores are not strategy evidence.
5. No seed, team identity, EpisodeId, future state or opponent-private state as runtime features.
6. Authenticated Kaggle API is the default current-meta source.
7. Original final holdout remains sealed.
8. Do not tune a failed architecture on spent validation evidence; change representation instead.
9. Strong local H2H against CR071M/legacy anchors is **necessary but not sufficient** for hosted metagame value.

## Closed architecture classes

- CR078 late mirror breaker.
- CR079 SpaTaro 1-NN.
- CR080 replay/route stitching.
- CR081 time-indexed market transplant.
- CR082 same-step state-conditioned teacher 1-NN.

Combined conclusion: neither trajectory imitation nor behavioral prediction establishes causal economic value for CR071M. CR083 has additionally shown that even a mechanics-valid local improvement can fail to transfer immediately to the live population.

## ACTIVE — CR083 explicit economic value

Phase 0 (`34709053070`) established exact mechanics and offline branching.

### Phase 1 — complete

Causal deletion run `34715158344`, master `9130830`, removed one final market family at a time from exact CR071M. Every variant lost 0–16. Broad family disabling remains closed.

### Phase 2 — local promotion PASS / hosted probe active

Protocol: `docs/strategy/CR083_PHASE2_SEED_DEMAND_CLAMP_PROTOCOL_2026-09-12.md`.

Canonical promotion workflow: **`34715575445`**.

Frozen candidate SHA-256: **`648fbcdb370f7e48fafda18a1112c5f1b57a17a81b7191f010fe4058f41a41b8`** from artifact `10304915100` (`CR083.tar.gz`).

Fresh local promotion result:

- direct vs CR071M: **45W–1L–18T = 0.84375**;
- median margin `+240`, mean margin `+172.5`;
- guardrail score deltas vs CR053/CR061/CR065: **0 / 0 / 0**;
- zero execution errors and zero incomplete games.

Frozen hosted probe workflow `34740104210` submitted exactly one SHA-locked package. Kaggle submission: **`56199767`**.

Authenticated checkpoint run `34745664559`:

- CR083: `COMPLETE`, **1563.9**;
- CR071M control: **1647.2**;
- current gap: **-83.3**;
- CR083 maturity: **33 public episodes + 1 validation**;
- CR071M maturity: 361 listed completed episodes.

Interpretation: this is meaningful negative hosted evidence, but it is still an early checkpoint. Do not retune the seed clamp from this live score and do not spend another submission slot trying a nearby variant.

## Immediate diagnostic path

1. Complete read-only hosted replay forensics run **`34745733865`** over the public CR083 episodes.
2. Quantify CR083 hosted W/L/ties, money margins, opponent mix if legally observable offline, and whether losses are concentrated in specific economic states or opponent strategy families.
3. Compare those failures with the local promotion panel to identify the **proxy gap** — what the current CR071M/CR053/CR061/CR065 panel is not representing.
4. Freeze a new evaluation protocol that includes a genuinely independent population/metagame proxy before building the next architecture.
5. Preserve the CR083 package unchanged while its hosted evidence matures. No CR083A/B/C and no tuning of `step 434`, crop exceptions or clamp formula on this spent evidence.
6. No new hosted submission until a distinct architecture passes the revised frozen gate.

## Hosted frontier reality

Authenticated snapshot `34745664559`: top 10 ranges from **3214.8** (Majkel1337) to **2967.2** (binghua). CR083 at 1563.9 and CR071M at 1647.2 remain far outside prize range. The next breakthrough must therefore improve metagame representation, not merely add a few local rating points.

## Escalation rule

When a frozen mechanism passes fresh direct, broad guardrail **and independent population-proxy evidence**, move to one controlled hosted probe. When hosted evidence contradicts a local gate, treat that contradiction as evidence about the gate/proxy itself; do not retune the mechanism on the same spent panel.
