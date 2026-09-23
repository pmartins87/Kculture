# V28F — ALL3-Centered Hedge Complementarity Benchmark Protocol — 2026-09-22

## Status

PRE-REGISTERED after V28E established that raw hosted W/L was heavily confounded by opponent strength.

No Kaggle submission, deletion, or slot reordering is authorized.

## Strategic question

With ALL3 frozen as the primary agent, which mechanically reproducible hedge best complements ALL3 on a fresh current-frontier common panel?

The goal is **not** to select the strongest standalone candidate. The official tracked pair benefits from diversity: the hedge should win contexts where ALL3 does not.

## Frozen primary

Primary is fixed:
- **ALL3** = exact V47 + O-RW1 + O-TW1 + O-LQ2.

V28F cannot replace the primary.

## Hedge candidates

Exactly four:
1. **V47** — exact public V47;
2. **ORW1** — exact V47 + O-RW1 only;
3. **CR053** — exact historical CR053 route package, archive SHA-256
   `095080e791bd8d58369893c1a421beb57b7f64c2808c011f576e09684ffb9a15`;
4. **CR029** — exact deterministic FULL_RECENT_TOP policy rebuilt by the frozen CR029 builder, requiring canonical tape SHA-256
   `6c56840b9510e0688da2fbec47e8f89583c63a0124fa4c8801fa5d93c197226b`.

CR053 and CR029 are included for lineage diversity. Their historical hosted scores are provenance/calibration only and do not enter the selector.

## Exact-candidate acquisition

### CR053

Download the preserved `cr052-cr053-hosted-candidates` artifact from workflow run `34105008373`.

Require:
- exact archive name `R4D_CR053_ROUTE106309334_V1.tar.gz`;
- exact archive SHA above;
- embedded `main.py` SHA-256
  `6e5d298797117bc72ad43c06b1d6a37634ad33a16a5c371c8c7e1a0aa5fc4519`;
- both-seat smoke against starter.

### CR029

Rebuild with:
`tools/build_cr029_recent_top_submission.py --authorization CR029_FULL_RECENT_TOP_PASS__BUILD_PACKAGE`.

Require:
- builder canonical tape SHA exactly as frozen above;
- manifest/archive/main hash consistency;
- both-seat smoke against starter.

## Fresh frontier

At V28F workflow start:

1. query current public Kaggriculture Top-30 once;
2. acquire serially with bounded retry;
3. SHA-deduplicate;
4. both-seat smoke against starter;
5. exclude exact V47 identity;
6. select up to 12 unique executable sources by representative rank;
7. minimum selected: 8;
8. freeze V47 base, the selected sources, exact CR053 and rebuilt exact CR029 in one immutable snapshot;
9. remove Kaggle credentials before any benchmark episode.

No source reacquisition after snapshot.

The existing V28B snapshot implementation may be reused unchanged because its acquisition/mechanical contract already satisfies these rules.

## Fresh contexts

Seeds:
`80401,80402,80403,80404,80405,80406`.

Both seats.

With 12 sources:
- 144 common contexts;
- ALL3 and every hedge run on every identical context.

## Mechanical validity

Require:
- >=8 selected unique frontier sources;
- all selected sources smoke PASS both seats;
- CR053 exact archive/main SHA PASS;
- CR029 frozen tape/manifest/archive/main consistency PASS;
- CR053 and CR029 both-seat smoke PASS;
- every candidate/context cell DONE/DONE, >=720 steps, finite rewards;
- no duplicate/missing cells;
- immutable snapshot only during benchmark;
- Kaggle credentials removed before candidate/opponent execution.

Failure => `V28F_MECHANICS_INVALID`.

## Metrics

For each candidate:
- contexts;
- score rate;
- W/T/L;
- mean/median margin;
- source-level score rates;
- seed-level score rates.

For each hedge H relative to ALL3 primary report:
- `primary_nonwin_to_hedge_win`;
- `primary_loss_to_hedge_win`;
- `primary_tie_to_hedge_win`;
- number of distinct frontier source SHAs with >=1 ALL3-nonwin -> hedge-win conversion;
- number of distinct seeds with >=1 conversion;
- best-of-two pair score rate = mean(max(ALL3 score, H score));
- pair score-rate delta versus ALL3 alone;
- standalone hedge score rate and mean margin.

## Frozen hedge selector

Among V47, ORW1, CR053, CR029, rank by:

1. greater best-of-two pair score rate with ALL3;
2. greater distinct-source complement breadth;
3. greater ALL3-loss -> hedge-win conversions;
4. greater standalone score rate;
5. greater mean margin;
6. lexical hedge key.

## Material replacement gate versus current V47 hedge

Let H* be the selector winner.

A non-V47 hedge is a **material replacement recommendation** only if:
- H* adds at least **3 more** ALL3-nonwin -> hedge-win conversions than V47 on the same common panel; and
- H* complement source breadth is **not lower** than V47's.

Otherwise preserve V47 even if another hedge wins a lower-order tiebreak.

## Decisions

### `V28F_ALTERNATE_HEDGE_RECOMMENDATION_READY`

Mechanical PASS, H* != V47, and material replacement gate PASS.

This is a recommendation only. A Kaggle slot mutation still requires explicit user authorization and a fresh slot/quota preflight.

### `V28F_KEEP_V47_HEDGE_READY`

Mechanical PASS and selector winner is V47.

### `V28F_NO_MATERIAL_HEDGE_REPLACEMENT`

Mechanical PASS, another hedge ranks first, but material replacement gate versus V47 fails.

### `V28F_MECHANICS_INVALID`

Repair mechanics only and rerun the exact same frozen candidates/rules.

## Anti-overfit

After outcomes:
- no seed filtering;
- no source filtering;
- no candidate code edits;
- no threshold changes;
- no hosted/public score used to alter V28F ordering;
- no Kaggle submission to decide V28F.

No Kaggle mutation is authorized by this protocol.
