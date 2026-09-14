"""Build CR087: exact historically hosted CR053 + CR086 latent-supply SELL ordering.

CR053 physical route and market-order multiset are preserved. Only the order of
already-existing premium SELL orders may change, using the independently validated
legal opponent-stock estimator and mechanics-derived cash-at-risk from CR086.
"""
from __future__ import annotations
import argparse, gzip, hashlib, io, tarfile
from pathlib import Path
import cr086_build_latent_supply_priority as c86

BASE_SHA = "095080e791bd8d58369893c1a421beb57b7f64c2808c011f576e09684ffb9a15"


def sha(b: bytes) -> str: return hashlib.sha256(b).hexdigest()


def extract(package: Path, name: str) -> bytes | None:
    with tarfile.open(package, "r:gz") as tf:
        try: m=tf.getmember(name)
        except KeyError: return None
        f=tf.extractfile(m); return None if f is None else f.read()


def patch(source: str, estimator_source: Path) -> str:
    # Freeze the original static agent before redefining the public entrypoint.
    block=c86.runtime_block(estimator_source)
    patched = source + "\n\n# ---- CR087: latent-supply overlay on exact hosted CR053 ----\nimport copy\nimport math\n" + block + r'''

_cr087_base_agent = agent

def agent(obs, config=None):
    step = _clock(obs)
    _cr086_update(agent, obs, step)
    out = _cr087_base_agent(obs, config)
    market = out.get("market") or []
    out["market"] = _cr086_prioritize(agent, obs, market)
    return out
'''
    compile(patched,"main.py","exec")
    return patched


def write_tar(path: Path, members: list[tuple[str,bytes]]):
    raw=io.BytesIO()
    with tarfile.open(fileobj=raw,mode="w",format=tarfile.PAX_FORMAT) as tf:
        for name,data in sorted(members):
            ti=tarfile.TarInfo(name); ti.size=len(data); ti.mode=0o644; ti.mtime=0; ti.uid=ti.gid=0; ti.uname=ti.gname=""
            tf.addfile(ti,io.BytesIO(data))
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("wb") as fh:
        with gzip.GzipFile(filename="",mode="wb",fileobj=fh,mtime=0) as gz: gz.write(raw.getvalue())


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--base',type=Path,required=True); ap.add_argument('--estimator-source',type=Path,required=True); ap.add_argument('--output',type=Path,required=True); ap.add_argument('--manifest',type=Path,required=True); a=ap.parse_args()
    b=a.base.read_bytes(); base_sha=sha(b)
    if base_sha!=BASE_SHA: raise RuntimeError(f'hosted CR053 SHA mismatch: {base_sha}')
    main_b=extract(a.base,'main.py')
    if main_b is None: raise RuntimeError('main.py missing')
    src=main_b.decode('utf-8'); patched=patch(src,a.estimator_source)
    old_prov=extract(a.base,'PROVENANCE.txt') or b''
    note=("CR087 = exact hosted CR053 SHA "+BASE_SHA+" plus CR086 legal latent-supply SELL priority.\nNo route/action-tape change; no market-order quantity/product/multiset change; ordering only.\n").encode()
    write_tar(a.output,[('main.py',patched.encode()),('PROVENANCE.txt',old_prov),('CR087_PROVENANCE.txt',note)])
    manifest={
      'schema':'cr087-cr053-latent-supply-v1','base_sha256':base_sha,'candidate_sha256':sha(a.output.read_bytes()),
      'base_submission_id':56073870,'base_hosted_score_checkpoint':2064.8,
      'physical_route_modified':False,'market_multiset_modified':False,'market_ordering_only':True,
      'uses_identity_rating_episodeid_hidden_seed_future_or_opponent_private':False,
      'value_rule':'cash_risk = revenue_now - revenue_after_opponent_upper_latent_supply; prioritize iff risk>0'
    }
    import json; a.manifest.parent.mkdir(parents=True,exist_ok=True); a.manifest.write_text(json.dumps(manifest,indent=2,sort_keys=True)); print(json.dumps(manifest,indent=2,sort_keys=True))

if __name__=='__main__': main()
