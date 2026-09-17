#!/usr/bin/env python3
from __future__ import annotations

"""PS2 Ryzen rollout runner v2.

PrizeSolverV4 inherits its strategic plan family from PrizeSolverV2 (PLANS_V2).
The original PS2 runner accidentally branched over the older V0 PLANS, so the
counterfactual rollouts themselves were valid engine runs but were not labels for the
macro choices that V4 actually makes. This wrapper binds the validated resumable
runner to PLANS_V2.

For the first training dataset, do not branch at day >= 24 because V4 switches to the
dynamic TERMINAL plan there. Use pre-terminal branch days (e.g. 3,6,9,12,15,18,21,23).
"""

import tools.prize_solver_rollout_ryzen as runner
from solver.prize_solver_v2 import PLANS_V2

# The base runner intentionally references its module-global PLANS everywhere:
# branch generation, manifest provenance and aggregation. Rebinding it here keeps the
# already-smoked multiprocessing/checkpoint implementation unchanged while making the
# labels match PrizeSolverV4's actual strategic action space.
runner.PLANS = PLANS_V2


if __name__ == "__main__":
    runner.main()
