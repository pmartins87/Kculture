# O-TW1 Autonomous Runtime Gate — 2026-09-18

Frozen after causal PASS and before runtime outcomes.

Host: exact hosted-faithful V47, entrypoint `_y_agent_shopherd`.

Treatment: at the **first** runtime-legal state in the episode where public town mechanics
imply WHEAT consumption and exact V47 wants to SELL already-owned WHEAT, suppress only
those current-turn SELL WHEAT orders. Fire once maximum. Exact V47 resumes immediately
after that turn.

Fresh seeds: `68001..68008`.
Both seats.
Opponents: V47 mirror, V48, Tactical Memory, Ready Stock.
Total: 64 paired matchups / 128 complete episodes.

Frozen PASS:
- mechanics exact;
- overall mean W/L score delta > 0;
- >=4 non-win -> win flips;
- <=1 win -> non-win regression;
- >=3/4 opponent blocks nonnegative mean W/L;
- worst block >= -0.0625.

No hosted submission follows automatically. A PASS only promotes O-TW1 into the offline
option library / value-dataset stage. Hosted slots remain protected.
