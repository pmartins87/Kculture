from __future__ import annotations

import json
from kaggle_environments import make


def main():
    env = make("kaggriculture", debug=True)
    env.reset(num_agents=2)
    state = env.state
    out = []
    for i, s in enumerate(state):
        obs = s.observation
        try:
            obj = dict(obs)
        except Exception:
            obj = obs
        out.append({
            "agent_index": i,
            "top_keys": sorted(list(obj.keys())) if isinstance(obj, dict) else None,
            "player": obj.get("player") if isinstance(obj, dict) else None,
            "index": obj.get("index") if isinstance(obj, dict) else None,
            "agentIndex": obj.get("agentIndex") if isinstance(obj, dict) else None,
            "private_keys": sorted(list((obj.get("private") or {}).keys())) if isinstance(obj, dict) else None,
            "farms_len": len(obj.get("farms") or []) if isinstance(obj, dict) else None,
            "step": obj.get("step") if isinstance(obj, dict) else None,
        })
    print(json.dumps(out, indent=2, default=str))


if __name__ == "__main__":
    main()
