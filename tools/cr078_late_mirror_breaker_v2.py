"""CR078 builder v2: deterministic marker fix only; strategy is unchanged."""
from __future__ import annotations
import cr078_late_mirror_breaker as base


def patch_source(src: str) -> str:
    init = "        self._fs = None\n        self._fs_for = None\n        self._cr053_like = False\n"
    if src.count(init) != 1:
        raise RuntimeError("CR071M init block marker mismatch")
    src = src.replace(init, init + "        self._cr078_mirror_stage = 0\n", 1)

    act = "    def act(self, obs):\n"
    if src.count(act) != 1:
        raise RuntimeError("act marker mismatch")
    src = src.replace(act, base.HELPERS + "\n" + act, 1)

    detector = "        self._cr053_update_detector(obs, step, me)\n"
    if src.count(detector) != 1:
        raise RuntimeError("detector marker mismatch")
    src = src.replace(detector, detector + "        self._cr078_update_mirror_detector(obs, step, me)\n", 1)

    ret = '        return {"farmer": acts[0], "hands": acts[1:],\n                "market": (market + extra)[:MAX_ORDERS]}\n'
    if src.count(ret) != 1:
        raise RuntimeError("final return marker mismatch")
    repl = '        final_market = (market + extra)[:MAX_ORDERS]\n        final_market = self._cr078_break_late_mirror(step, final_market, proj)\n        return {"farmer": acts[0], "hands": acts[1:], "market": final_market}\n'
    src = src.replace(ret, repl, 1)
    compile(src, "<cr078-late-mirror-v2>", "exec")
    return src


base.patch_source = patch_source
if __name__ == "__main__":
    base.main()
