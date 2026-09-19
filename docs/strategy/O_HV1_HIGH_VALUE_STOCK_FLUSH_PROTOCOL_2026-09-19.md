# O-HV1 High-Value Stock Flush — Development Protocol — 2026-09-19

## Discovery evidence

ALL3 hosted submission `56367770` reached the first informative checkpoint:
- 34 resolved external games;
- 28 wins / 6 losses / 0 ties;
- raw score rate 0.8235294;
- 33 unique opponents;
- mean margin +13,626.97;
- current observed rating 2395.4.

This hosted sample is not a causal training set. It is used only to identify recurring mechanics.

Three concrete ALL3 losses expose the same local defect:

1. vs Vishal Kishore, step 348:
   - own shed includes WOOL 11;
   - public WOOL price 239;
   - ALL3 market has no SELL;
   - opponent sells WOOL 11;
   - money-delta swing -2634.

2. vs Vishal Kishore, step 299:
   - own shed includes MILK 6;
   - public MILK price 177;
   - ALL3 market has no SELL;
   - opponent sells MILK 6;
   - money-delta swing -1101.

3. vs qinsuikang, step 553:
   - own shed includes MILK 15;
   - public MILK price 254;
   - ALL3 does not sell MILK;
   - opponent sells MILK 24;
   - large adverse money swing.

Other severe losses (e.g. Timothy Adeyemi) include inventory-production deficits that this option
cannot solve and are explicitly out of scope.

## Hypothesis

**O-HV1 — High-Value Stock Flush** adds one missing high-value SELL to ALL3 when the current public
market price is unusually high and the product is already available in own projected shed.

Runtime inputs are strictly legal current state:
- own observation/private inventory;
- current public market prices;
- exact current ALL3 action;
- current configuration.

No opponent identity/rating/EpisodeId/hidden seed/future/opponent-private input is allowed.

## Finished-goods product set

To reduce strategic interference, HV1 only considers:

`MILK, WOOL, EGG, CARROT, STRAWBERRY, MELON, TOMATO`.

Excluded:
- WHEAT;
- FERTILIZER;
- animals/seeds.

WHEAT/FERTILIZER have broader operational roles and are not part of this first gate.

## Operator

For a frozen `min_step` and `min_price`:

1. start from exact ALL3 action;
2. project own shed through current physical actions;
3. process the existing ALL3 market in order:
   - subtract existing SELL quantities from projected remaining inventory;
   - account for current BUY_PRODUCT/BUY_ANIMAL inventory additions using existing engine model;
4. among eligible finished goods with remaining quantity >0 and public price >= `min_price`,
   choose the product maximizing `price * remaining_quantity`;
5. add exactly one `SELL product full_remaining_quantity`;
6. insert it after the leading SELL run and before later non-SELL market operations;
7. preserve ALL3 farmer/hands exactly.

## Frozen development matrix

Development opponents:
- V47 mirror;
- V48;
- Ready Stock.

Development seeds:
`74801..74804`, both seats.

Configurations:
- D1: min_step=240, min_price=175;
- D2: min_step=240, min_price=200;
- D3: min_step=336, min_price=175;
- D4: min_step=336, min_price=200.

No configuration may be added after seeing development results.

## Development selection rule

A configuration is eligible to freeze only if:
- zero negative-score paired contexts;
- mean score delta >= 0;
- mean margin delta > 0;
- it fires in at least 4 contexts.

Select among eligible configs by:
1. highest mean score delta;
2. then highest positive-score contexts;
3. then highest mean margin delta;
4. then more conservative configuration (higher price threshold, later start).

If no configuration is eligible:
**O_HV1_DEV_CLOSE**.

## Fresh validation after selection

The frozen configuration must then be tested on untouched seeds across all seven V2 opponent
families.

Validation PASS requires:
- overall mean score delta > 0;
- zero negative-score contexts;
- every opponent block mean score delta >= 0;
- positive overall mean margin delta.

A margin-only development result is not enough for hosted promotion.

No Kaggle submission is authorized by this protocol.
