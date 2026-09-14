#!/usr/bin/env python3
"""E1 preflight: print exact Kaggriculture 1.32.7 plant/animal runtime schema.

This is deliberately tiny.  The integrated hybrid must not guess observation keys.
"""
from pprint import pprint
from kaggle_environments.envs.kaggriculture import kaggriculture as kg

TPD = 24

print("E1_SCHEMA_PROBE")
print("STRAWBERRY_CONFIG")
pprint(dict(kg.CROPS["STRAWBERRY"]))
print("COW_CONFIG")
pprint(dict(kg.ANIMALS["COW"]))

plant = kg._new_plant("STRAWBERRY", 0, TPD)
animal = kg._new_animal("COW")
print("NEW_STRAWBERRY")
pprint(plant)
print("NEW_COW")
pprint(animal)

farm = kg._new_farm(10, 1_000_000)
private = kg._new_private()
pos = tuple(farm["farmer"])
x, y = pos
farm["tiles"][y][x] = kg._new_plant("STRAWBERRY", 0, TPD)
private["inventories"][0]["FERTILIZER"] = 3

for day in range(0, 14):
    tile = farm["tiles"][y][x]
    if not isinstance(tile, dict):
        break
    kg._apply_unit_action(farm, private, 0, ["WATER"], 10, day, TPD, 1000)
    # H11's strongest two-fertilizer exact schedule.
    if day in (9, 13):
        kg._apply_unit_action(farm, private, 0, ["FERTILIZE"], 10, day, TPD, 1000)
    print("DAY", day, "AFTER_ACTIONS")
    pprint(farm["tiles"][y][x])
    kg._daily_refresh_plants(farm, day, TPD)
    print("DAY", day, "AFTER_REFRESH")
    pprint(farm["tiles"][y][x])

print("E1_SCHEMA_PROBE_PASS")
