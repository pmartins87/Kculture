from __future__ import annotations
import argparse, copy, hashlib, importlib.util, json, shutil, tarfile, tempfile
from pathlib import Path

VARIANTS = {
    'PARENT': ('parent', 0),
    'CR071L_CR053_REORDER': ('reorder', 0),
    'CR071M_CR053_PRESALE1': ('presale', 1),
    'CR071N_CR053_PRESALE6': ('presale', 6),
}

def sha256_file(p: Path) -> str:
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1<<20), b''): h.update(b)
    return h.hexdigest()

def safe_extract(archive: Path, dst: Path):
    base=dst.resolve()
    with tarfile.open(archive,'r:*') as tf:
        for m in tf.getmembers():
            t=(dst/m.name).resolve()
            if t!=base and base not in t.parents: raise RuntimeError(f'unsafe member {m.name}')
            if m.issym() or m.islnk(): raise RuntimeError('links forbidden')
        tf.extractall(dst)

def load_cr053_tape(archive: Path):
    with tempfile.TemporaryDirectory(prefix='cr053-counter-src-') as td:
        root=Path(td); safe_extract(archive, root)
        main=root/'main.py'
        spec=importlib.util.spec_from_file_location('_cr053_counter_source', main)
        mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
        tape=getattr(mod,'_TAPE',None)
        if not isinstance(tape,list) or len(tape)<700: raise RuntimeError('CR053 _TAPE missing')
        return copy.deepcopy(tape)

def sell_schedule(tape):
    out={}
    for step,a in enumerate(tape):
        rows=[]
        for idx,o in enumerate((a or {}).get('market',[]) or []):
            if o and len(o)>=3 and o[0]=='SELL':
                q=max(0,int(o[2]))
                if q>0: rows.append([idx,str(o[1]),q])
        if rows: out[str(step)]=rows
    return out

HELPERS = r'''
    def _cr053_public_shape(self, farm):
        plants = animals = 0
        for row in (farm.get("tiles", []) or []):
            for tile in row or []:
                if not isinstance(tile, dict):
                    continue
                if tile.get("kind") == "PLANT":
                    plants += 1
                if tile.get("animal") is not None:
                    animals += 1
        return {
            "money": float(farm.get("money", 0) or 0),
            "hands": len(farm.get("hands", []) or []),
            "quadrants": len(farm.get("unlocked_quadrants", []) or []),
            "plants": plants,
            "animals": animals,
        }

    def _cr053_update_detector(self, obs, step, me):
        if step != 12:
            return
        farms = list(obs.get("farms", []) or [])
        if len(farms) < 2:
            self._cr053_like = False
            return
        x = self._cr053_public_shape(farms[1 - me])
        self._cr053_like = bool(
            abs(x["money"] - 39.0) <= 0.01
            and x["hands"] == 7
            and x["quadrants"] == 1
            and x["plants"] == 12
            and x["animals"] == 6
        )

    def _route_window_sells(self, item, start, end):
        r = self.R[self.cur]
        total = 0
        for t in range(max(0, start), min(len(r), end)):
            for o in (r[t].get("market") or []):
                if o and len(o) >= 3 and o[0] == "SELL" and o[1] == item:
                    total += max(0, int(o[2]))
        return total

    def _cr053_counter_market(self, step, market, proj):
        if not self._cr053_like:
            return market
        schedule = _CR053_SELLS
        # Same-turn ordering counter: if CR053 is expected to sell an item earlier
        # in its queue, move our sell of that item to the front. Quantity unchanged.
        same = schedule.get(str(step), [])
        pressured = {row[1]: row[0] for row in same if int(row[2]) >= 4}
        if pressured:
            head, tail = [], []
            for o in market:
                if o and len(o) >= 3 and o[0] == "SELL" and o[1] in pressured:
                    head.append(o)
                else:
                    tail.append(o)
            market = head + tail
        if _CR053_COUNTER_LEAD <= 0:
            return market

        # Pull forward only stock the route already plans to sell within the next day.
        # Trigger only when CR053 has a >=4-unit dump in the next LEAD steps.
        predicted = {}
        for dt in range(1, _CR053_COUNTER_LEAD + 1):
            for _, item, qty in schedule.get(str(step + dt), []):
                if int(qty) >= 4:
                    predicted[item] = predicted.get(item, 0) + int(qty)
        if not predicted:
            return market
        existing = {}
        for o in market:
            if o and len(o) >= 3 and o[0] == "SELL":
                existing[o[1]] = existing.get(o[1], 0) + max(0, int(o[2]))
        room = max(0, MAX_ORDERS - len(market))
        if room <= 0:
            return market
        for item, opp_qty in sorted(predicted.items(), key=lambda kv: -kv[1]):
            if room <= 0:
                break
            have = max(0, int(proj.get(item, 0)) - existing.get(item, 0))
            if have <= 0:
                continue
            planned = self._route_window_sells(item, step + 1, step + 25)
            if planned <= 0:
                continue
            qty = min(have, planned, max(1, int(opp_qty)))
            if qty <= 0:
                continue
            slot = next((i for i,o in enumerate(market) if o and len(o)>=3 and o[0]=="SELL" and o[1]==item), -1)
            if slot >= 0:
                market[slot][2] = max(0, int(market[slot][2])) + qty
            else:
                market.insert(0, ["SELL", item, qty])
                room -= 1
            existing[item] = existing.get(item, 0) + qty
        return market
'''

def patch_source(src: str, schedule: dict, mode: str, lead: int) -> str:
    if mode=='parent': return src
    const = "\n_CR053_SELLS = " + repr(schedule) + f"\n_CR053_COUNTER_LEAD = {int(lead)}\n"
    marker='\n_BLOB = ('
    if marker not in src: raise RuntimeError('BLOB marker missing')
    src=src.replace(marker, const+marker, 1)
    init_needle='        self._fs_for = None\n'
    if src.count(init_needle)!=1: raise RuntimeError('init marker mismatch')
    src=src.replace(init_needle, init_needle+'        self._cr053_like = False\n',1)
    act_marker='    def act(self, obs):\n'
    if src.count(act_marker)!=1: raise RuntimeError('act marker mismatch')
    src=src.replace(act_marker, HELPERS+'\n'+act_marker,1)
    day_needle='        day = int(obs.get("day", step // 24))\n'
    if src.count(day_needle)!=1: raise RuntimeError('day marker mismatch')
    src=src.replace(day_needle, day_needle+'        self._cr053_update_detector(obs, step, me)\n',1)
    clamp_marker='        # ---- clamp_sells: a SELL the shed cannot fill burns one of only 10 slots ----\n'
    if src.count(clamp_marker)!=1: raise RuntimeError('clamp marker mismatch')
    inject='        # ---- CR053-like market counterplay (public trajectory only) ----\n        market = self._cr053_counter_market(step, market, proj)\n\n'
    src=src.replace(clamp_marker, inject+clamp_marker,1)
    compile(src,'<cr071-counter>','exec')
    return src

def build_one(base: Path, cr053: Path, out: Path, variant: str, mode: str, lead: int, schedule: dict):
    with tempfile.TemporaryDirectory(prefix=f'{variant.lower()}-') as td:
        root=Path(td); safe_extract(base, root)
        main=root/'main.py'; original=main.read_text(encoding='utf-8')
        patched=patch_source(original,schedule,mode,lead)
        main.write_text(patched,encoding='utf-8')
        for c in root.rglob('__pycache__'): shutil.rmtree(c,ignore_errors=True)
        for p in root.rglob('*.pyc'): p.unlink(missing_ok=True)
        dst=out/f'{variant}_SEATSAFE_V1.tar.gz'
        with tarfile.open(dst,'w:gz') as tf:
            for p in sorted(root.rglob('*')):
                if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc':
                    tf.add(p,arcname=p.relative_to(root).as_posix())
        return {'variant':variant,'mode':mode,'lead':lead,'archive':dst.name,'sha256':sha256_file(dst),'changed':patched!=original}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--base',required=True); ap.add_argument('--cr053',required=True); ap.add_argument('--output-dir',required=True)
    a=ap.parse_args(); base=Path(a.base); cr053=Path(a.cr053); out=Path(a.output_dir); out.mkdir(parents=True,exist_ok=True)
    tape=load_cr053_tape(cr053); schedule=sell_schedule(tape)
    rec={'schema_version':'kculture-cr071-cr053-counterplay-v1','base_sha256':sha256_file(base),'cr053_sha256':sha256_file(cr053),'detector':'step12 public shape: money39 hands7 quadrants1 plants12 animals6','schedule_sell_steps':len(schedule),'automatic_kaggle_submission':False,'variants':{}}
    for v,(m,l) in VARIANTS.items(): rec['variants'][v]=build_one(base,cr053,out,v,m,l,schedule)
    (out/'receipt.json').write_text(json.dumps(rec,indent=2,sort_keys=True),encoding='utf-8'); print(json.dumps(rec,indent=2,sort_keys=True))
if __name__=='__main__': main()
