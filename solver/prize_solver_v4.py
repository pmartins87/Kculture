from __future__ import annotations

"""Prize Solver V4 — valid crop actions + monotone livestock slot allocation.

V3 finally produced a profitable end-to-end economy, but tracing exposed two executor
bugs: PLANT lacked the crop argument at execution time, and fixed species->slot mapping
could strand newly purchased animals after the strategic plan changed. V4 fixes both
without changing the solver architecture.
"""

from collections import Counter
from typing import List, Tuple

from .prize_solver_v0 import ANIMAL_SLOTS, ANIMALS, Task, _get, _tile
from .prize_solver_v3 import PrizeSolverV3


class PrizeSolverV4(PrizeSolverV3):
    def _action_for_task(self, obs, farm, pos, inv, task: Task, reserved_pickups):
        # Base executor needs arguments for PLANT. V0 emitted ["PLANT"] and the engine
        # silently no-op'd every crop setup attempt.
        if tuple(pos) == tuple(task.pos) and task.op == "PLANT":
            return ["PLANT", task.item]
        return super()._action_for_task(obs, farm, pos, inv, task, reserved_pickups)

    def _desired_animal_slots(self, farm, plan):
        """Preserve all live animals and allocate only missing species to free slots.

        A plan change must never reinterpret an existing sheep slot as a cow slot. That
        positional mismatch in V3 could leave purchased cows permanently in the shed.
        """
        desired_counts = Counter({
            "COW": max(0, int(plan.cows)),
            "SHEEP": max(0, int(plan.sheep)),
            "GOOSE": max(0, int(plan.geese)),
        })
        assigned: List[Tuple[Tuple[int, int], str]] = []
        live_counts = Counter()
        occupied = set()

        # Existing live animals are immutable commitments.
        for pos in ANIMAL_SLOTS:
            if not self._unlocked(farm, pos):
                continue
            tile = _tile(farm, pos)
            animal = _get(tile, "animal", None) if isinstance(tile, dict) else None
            if animal in ANIMALS:
                assigned.append((pos, animal))
                live_counts[animal] += 1
                occupied.add(pos)

        missing = []
        for animal in ("COW", "SHEEP", "GOOSE"):
            missing.extend([animal] * max(0, desired_counts[animal] - live_counts[animal]))

        free = [
            pos for pos in ANIMAL_SLOTS
            if self._unlocked(farm, pos) and pos not in occupied
        ]

        for animal in missing:
            structure = ANIMALS[animal]["structure"]
            # Prefer already-correct empty structure, then bare tile, then a wrong
            # empty structure that can be DIG'd and rebuilt by _tasks below.
            ranked = []
            for pos in free:
                tile = _tile(farm, pos)
                if isinstance(tile, dict) and _get(tile, "animal", None) is not None:
                    continue
                if isinstance(tile, dict) and _get(tile, "kind", None) == structure:
                    rank = 0
                elif tile is None:
                    rank = 1
                elif isinstance(tile, dict) and _get(tile, "kind", None) in {"COOP", "PASTURE"} and _get(tile, "animal", None) is None:
                    rank = 2
                else:
                    continue
                ranked.append((rank, pos))
            if not ranked:
                break
            ranked.sort(key=lambda row: (row[0], ANIMAL_SLOTS.index(row[1])))
            pos = ranked[0][1]
            assigned.append((pos, animal))
            free.remove(pos)

        return assigned

    def _tasks(self, obs, config, plan):
        tasks = super()._tasks(obs, config, plan)
        farm = obs["farms"][int(obs.get("player", 0))]

        # If a dynamically allocated target currently contains the wrong *empty*
        # structure, clear it. Never DIG a structure containing a live animal.
        existing = {(t.op, t.pos, t.tag) for t in tasks}
        for pos, animal in self._desired_animal_slots(farm, plan):
            tile = _tile(farm, pos)
            if not isinstance(tile, dict):
                continue
            if _get(tile, "animal", None) is not None:
                continue
            desired_structure = ANIMALS[animal]["structure"]
            kind = _get(tile, "kind", None)
            if kind in {"COOP", "PASTURE"} and kind != desired_structure:
                key = ("DIG", pos, "rebuild_animal_structure")
                if key not in existing:
                    tasks.append(Task(65, "DIG", pos, tag="rebuild_animal_structure"))

        return self._resource_feasible_tasks(obs, tasks)


_SOLVER = PrizeSolverV4()


def agent(obs, config=None):
    return _SOLVER.act(obs, config or {})
