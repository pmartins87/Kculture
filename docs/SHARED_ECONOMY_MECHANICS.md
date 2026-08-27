# Kaggriculture — shared economy and player interaction

Verified against the frozen official engine used by Kculture (`kaggle-environments==1.32.7`, engine commit `28b6d8af3ce73926b3d0fda1410c1ddd8384ab8c`).

## Correct mental model

Kaggriculture is **private production + shared commodity economy**.

Each player owns an independent farm/private inventory, but both players act on one shared market and observe a shared town/environment. Therefore terminal farm money is not generated independently: one player's market actions can change the prices and inventory faced by the other player.

## Private / non-colliding layer

- each player has a separate farm grid;
- farmer/farm-hand movement occurs only on that player's farm;
- players do not physically collide, occupy the same farm, steal tiles, block paths or directly harvest each other's crops;
- shed, seeds and carried inventories are private;
- crop seeds use fixed purchase costs;
- animals use fixed purchase costs;
- land unlocks and hires are private farm expenditures.

The public observation exposes both farms, while `private` contains only the observing player's private state.

## Shared market layer

There is one market object for the episode, shared by both players:

- shared inventory for WHEAT, CARROT, TOMATO, STRAWBERRY, MELON, EGG, MILK, WOOL and FERTILIZER;
- shared current prices derived deterministically from that inventory;
- SELL adds supply to shared market inventory and can lower later sale prices;
- BUY_PRODUCT is available for WHEAT/FERTILIZER, removes shared inventory and can raise later prices.

A player's decision can therefore improve or worsen the economics of the opponent's later transaction even when neither player's physical farm changes.

## Exact market-order sequence

Each player may submit an ordered list of market actions. The engine resolves market positions sequentially: position 0, then position 1, and so on.

Within one position, SELL/BUY operations are resolved per-unit in lockstep. Both players see the same pre-commit shared inventory for that unit before commits are applied. Consequently:

- there is no inherent player-0 price advantage when both players transact the same product in the same position;
- if both SELL the same product in the same position, both receive the same quote for a given lockstep unit while both remain active;
- after the position completes, shared inventory/prices reflect its transactions;
- a transaction placed in a later position sees the altered market left by earlier positions.

Therefore **order-list position itself is a strategic variable**.

## Example: same product, different order position

If player A sells a large quantity of STRAWBERRY in position 0 and player B sells STRAWBERRY in position 1, A's sale adds supply before B's order begins. B can receive materially lower prices.

If both place their STRAWBERRY sale in position 0, they share the pre-commit quotation path lockstep instead of one entire dump occurring before the other.

## Shared town demand

Town/shop state is common to the episode. Periodic shop/town consumption removes products from shared market inventory. That can create scarcity and raise later prices. Players do not directly control shop unlock randomness, but they can adapt crop mix, sale timing and inventory strategy to observed common demand.

Town consumption is processed after player market actions on the applicable turn, so transaction timing relative to demand ticks matters.

## Strategic consequence

A complete value function cannot be merely:

`expected own production -> expected own sale value`.

It must ultimately account for something closer to:

`own production + own cash-flow + shared-market trajectory + opponent public state + interaction/order effects -> terminal matchup value`.

This does not imply every action should be adversarial. Many physical production decisions remain essentially private. It means the economic controller must treat the opponent as part of the state whenever shared inventory, price, demand or transaction order can materially change value.

## Research implications for Kculture

- static route optimization is insufficient for prize-grade play;
- opponent/public-state adaptation is strategically legitimate and potentially valuable;
- sale timing alone is insufficient if same-turn order position is ignored;
- market proxies must reproduce exact shared-inventory and order-sequence mechanics before authorizing a causal candidate;
- broad current-meta matchup evaluation remains necessary because a policy can score well against one economic behavior and poorly against another.
