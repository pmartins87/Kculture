#!/usr/bin/env python3
from __future__ import annotations
import argparse, ast, base64, copy, gzip, hashlib, io, json, re, tarfile, zlib
from pathlib import Path
import numpy as np

MAX_UNITS=40
RAW_ORDER_SLOTS=16
ACTION_WIDTH=1+MAX_UNITS*3+1+RAW_ORDER_SLOTS*3
ITEM={"WHEAT":0,"CARROT":1,"TOMATO":2,"STRAWBERRY":3,"MELON":4,"EGG":5,"MILK":6,"WOOL":7,"FERTILIZER":8,"GOOSE":9,"COW":10,"SHEEP":11}
UNIT_OP={"PASS":0,"NORTH":1,"SOUTH":2,"EAST":3,"WEST":4,"PICKUP":5,"DROP":6,"PLACE":7,"PLANT":8,"WATER":9,"HARVEST":10,"FERTILIZE":11,"DIG":12,"BUILD_COOP":13,"BUILD_PASTURE":14,"FEED":15,"COLLECT_FERTILIZER":16,"CARE":17}
MARKET_OP={"HIRE":1,"BUY_LAND":2,"BUY_SEED":3,"BUY_PRODUCT":4,"BUY_ANIMAL":5,"SELL":6}

def sha(b): return hashlib.sha256(b).hexdigest()
def cells(nb): return [''.join(c.get('source',[])) for c in nb.get('cells',[]) if c.get('cell_type')=='code']

def literal_env(cs):
    env={}
    for s in cs:
        if s.lstrip().startswith('%%'): continue
        try: tree=ast.parse(s)
        except Exception: continue
        for node in tree.body:
            if isinstance(node,ast.Assign) and len(node.targets)==1 and isinstance(node.targets[0],ast.Name):
                try: env[node.targets[0].id]=ast.literal_eval(node.value)
                except Exception: pass
    return env

def large_constants(cs,minlen=5000):
    out=[]
    for ci,s in enumerate(cs):
        if s.lstrip().startswith('%%'): continue
        try: tree=ast.parse(s)
        except Exception: continue
        for n in ast.walk(tree):
            if isinstance(n,ast.Constant) and isinstance(n.value,str) and len(n.value)>=minlen:
                out.append((ci,n.value))
    return out

def tar_members(blob):
    try:
        with tarfile.open(fileobj=io.BytesIO(blob),mode='r:*') as tf:
            out={}
            for n in tf.getnames():
                fh=tf.extractfile(n)
                if fh is not None: out[n]=fh.read()
            return out
    except Exception:
        return None

def source_bytes_join(cs):
    for s in cs:
        if 'SOURCE_BYTES' not in s or s.lstrip().startswith('%%'): continue
        try: tree=ast.parse(s)
        except Exception: continue
        for n in ast.walk(tree):
            if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='SOURCE_BYTES' for t in n.targets):
                v=n.value
                if isinstance(v,ast.Call) and isinstance(v.func,ast.Attribute) and v.func.attr=='join' and v.args:
                    try: return ast.literal_eval(v.func.value).join(ast.literal_eval(v.args[0]))
                    except Exception: pass
                try:
                    x=ast.literal_eval(v)
                    return x.encode() if isinstance(x,str) else x
                except Exception: pass
    return None

def extract_source_and_extra(nb):
    cs=cells(nb)
    env=literal_env(cs)
    extra={}
    method='none'
    src=None

    for s in cs:
        ls=s.splitlines(True)
        if ls and re.match(r'^\s*%%writefile\s+(?:.*/)?main\.py\s*$',ls[0].strip()):
            src=''.join(ls[1:]).encode()
            method='writefile_main'
    if src is None:
        x=source_bytes_join(cs)
        if x is not None:
            src=x
            method='source_bytes'
    if src is None:
        decoders=[]
        if isinstance(env.get('SOURCE_B85'),str):
            decoders.append(('source_b85_gzip',lambda:gzip.decompress(base64.b85decode(env['SOURCE_B85']))))
        if isinstance(env.get('AGENT_GZ_B64'),str):
            decoders.append(('agent_gz_b64',lambda:gzip.decompress(base64.b64decode(env['AGENT_GZ_B64']))))
        if isinstance(env.get('AGENT_B64'),str):
            decoders.append(('agent_b64',lambda:base64.b64decode(env['AGENT_B64'])))
        if isinstance(env.get('_AGENT_B85_PARTS'),(list,tuple)):
            decoders.append(('agent_parts_b85_zlib',lambda:zlib.decompress(base64.b85decode(''.join(env['_AGENT_B85_PARTS'])))))
        if isinstance(env.get('agent_b85'),str):
            decoders.append(('agent_b85_zlib',lambda:zlib.decompress(base64.b85decode(env['agent_b85']))))
        for name,fn in decoders:
            try:
                src=fn()
                method=name
                break
            except Exception:
                pass

    if src is None:
        candidates=[]
        for k,v in env.items():
            if isinstance(v,str) and len(v)>5000:
                candidates.append((k,v))
        candidates += [(f'cell{ci}',v) for ci,v in large_constants(cs)]
        seen=set()
        for key,v in candidates:
            h=hashlib.sha1(v.encode(errors='ignore')).hexdigest()
            if h in seen: continue
            seen.add(h)
            for enc,decoder in [('b64',base64.b64decode),('b85',base64.b85decode)]:
                try: blob=decoder(v)
                except Exception: continue
                members=tar_members(blob)
                if members and any(Path(n).name=='main.py' for n in members):
                    extra.update(members)
                    mname=next(n for n in members if Path(n).name=='main.py')
                    src=members[mname]
                    method=f'archive_{enc}:{key}'
                    break
            if src is not None: break

    # The Andrewsokolovsky notebook promotes an overlay only after notebook-time tests.
    # Static corpus extraction conservatively retains its explicit parent programme.
    if src is None:
        for s in cs:
            ls=s.splitlines(True)
            if ls and re.match(r'^\s*%%writefile\s+.*parent_v14\.py\s*$',ls[0].strip()):
                src=''.join(ls[1:]).encode()
                method='parent_v14_fallback'
                break

    # Apex contains a separate native two-route tape library.
    for s in cs:
        ls=s.splitlines(True)
        if ls and re.match(r'^\s*%%writefile\s+source/tape\.inc\s*$',ls[0].strip()):
            extra['source/tape.inc']=''.join(ls[1:]).encode()
    return src,method,extra

def json_blobs(src):
    if not src: return []
    try: tree=ast.parse(src.decode('utf-8',errors='ignore'))
    except Exception: return []
    out=[]
    seen=set()
    for n in ast.walk(tree):
        if not (isinstance(n,ast.Constant) and isinstance(n.value,str) and len(n.value)>1000):
            continue
        st=n.value
        for enc,d1 in [('b85',base64.b85decode),('b64',base64.b64decode)]:
            try: raw=d1(st)
            except Exception: continue
            for comp,d2 in [('zlib',zlib.decompress),('gzip',gzip.decompress),('raw',lambda x:x)]:
                try:
                    b=d2(raw)
                    obj=json.loads(b)
                except Exception:
                    continue
                key=sha(json.dumps(obj,sort_keys=True,separators=(',',':')).encode())
                if key not in seen:
                    seen.add(key)
                    out.append((enc,comp,obj,key))
    return out

def reconstruct_routes(obj):
    routes=[]
    if isinstance(obj,dict) and set(obj)>= {'actions','routes','shops'} and isinstance(obj['actions'],list) and isinstance(obj['routes'],dict):
        actions=obj['actions']
        for rid,idxs in sorted(obj['routes'].items(),key=lambda kv:int(kv[0])):
            try: tape=[copy.deepcopy(actions[int(i)]) for i in idxs]
            except Exception: continue
            if len(tape)==719: routes.append((f'route_{rid}',tape))
    elif isinstance(obj,dict) and set(obj)>= {'base','patches'} and isinstance(obj['base'],list):
        base=copy.deepcopy(obj['base'])
        if len(base)==719:
            routes.append(('base',base))
            patches=obj['patches']
            iterable=patches.items() if isinstance(patches,dict) else enumerate(patches,1)
            for rid,patch in iterable:
                tape=copy.deepcopy(base)
                try:
                    for step,action in patch:
                        tape[int(step)]=copy.deepcopy(action)
                except Exception:
                    continue
                routes.append((f'patch_{rid}',tape))
    elif isinstance(obj,list) and len(obj)==719 and all(isinstance(x,dict) for x in obj):
        routes.append(('literal719',copy.deepcopy(obj)))
    return routes

def encode_action(action):
    row=np.zeros(ACTION_WIDTH,dtype=np.int16)
    units=[action.get('farmer') or ['PASS']]+list(action.get('hands') or [])
    row[0]=min(MAX_UNITS,len(units))
    for i,a in enumerate(units[:MAX_UNITS]):
        if not a: a=['PASS']
        off=1+i*3
        row[off]=UNIT_OP.get(str(a[0]),18)
        row[off+1]=ITEM.get(str(a[1]),-1) if len(a)>=2 else -1
        row[off+2]=int(a[2]) if len(a)>=3 else 1
    market=[x for x in list(action.get('market') or []) if x]
    base=1+MAX_UNITS*3
    row[base]=min(RAW_ORDER_SLOTS,len(market))
    for oi,o in enumerate(market[:RAW_ORDER_SLOTS]):
        off=base+1+oi*3
        row[off]=MARKET_OP.get(str(o[0]),0)
        row[off+1]=ITEM.get(str(o[1]),-1) if len(o)>=2 else -1
        row[off+2]=int(o[2]) if len(o)>=3 else 1
    return row

def encode_tape(tape):
    return np.stack([encode_action(a) for a in tape],axis=0)

def parse_tape_inc(blob):
    txt=blob.decode('utf-8',errors='ignore')
    m=re.search(r'kEncodedTapes\s*\[.*?\]\s*=\s*\{(.*)\};',txt,re.S)
    if not m: return []
    strs=re.findall(r'"([0-9\- ]*)"',m.group(1))
    if len(strs)%719: return []
    out=[]
    for ri in range(len(strs)//719):
        rows=[]
        for st in strs[ri*719:(ri+1)*719]:
            vals=[int(x) for x in st.split()]
            if len(vals)<2: break
            nu,no=vals[0],vals[1]
            p=2
            row=np.zeros(ACTION_WIDTH,dtype=np.int16)
            row[0]=nu
            for u in range(min(nu,MAX_UNITS)):
                if p+2>=len(vals): break
                off=1+u*3
                row[off:off+3]=vals[p:p+3]
                p+=3
            base=1+MAX_UNITS*3
            row[base]=min(no,RAW_ORDER_SLOTS)
            for o in range(min(no,RAW_ORDER_SLOTS)):
                if p+2>=len(vals): break
                off=base+1+o*3
                row[off:off+3]=vals[p:p+3]
                p+=3
            rows.append(row)
        if len(rows)==719:
            out.append((f'apex_cpp_{ri}',np.stack(rows)))
    return out

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--root',default='external/public_topscore_20260917')
    ap.add_argument('--out',default='runs/public_programme_corpus_v1')
    args=ap.parse_args()
    root=Path(args.root)
    out=Path(args.out)
    out.mkdir(parents=True,exist_ok=True)
    (out/'sources').mkdir(exist_ok=True)

    entries=[]
    candidate_tapes=[]
    route_bank_fingerprints={}
    source_seen={}
    dirs=sorted([p for p in root.iterdir() if p.is_dir() and re.match(r'^\d\d_',p.name)])
    for d in dirs:
        rank=int(d.name[:2])
        meta=json.loads((d/'kernel-metadata.json').read_text())
        nbp=d/meta['code_file']
        nb=json.loads(nbp.read_text(encoding='utf-8'))
        src,method,extra=extract_source_and_extra(nb)
        src_sha=sha(src) if src else None
        if src and src_sha not in source_seen:
            (out/'sources'/f'{src_sha}.py').write_bytes(src)
            source_seen[src_sha]=meta['id']

        lic=[]
        txt=src.decode('utf-8',errors='ignore') if src else ''
        if 'SPDX-License-Identifier: Apache-2.0' in txt:
            lic.append('spdx_apache_2_0')
        if 'Apache-2.0' in txt or 'Apache License' in txt:
            lic.append('apache_notice_present')

        family=[]
        for enc,comp,obj,objsha in json_blobs(src):
            rr=reconstruct_routes(obj)
            if not rr: continue
            if isinstance(obj,dict) and set(obj)>= {'actions','routes','shops'}:
                kind='modern41'
            elif isinstance(obj,dict) and set(obj)>= {'base','patches'}:
                kind='legacy13'
            else:
                kind='literal719'
            route_bank_fingerprints.setdefault(objsha,{'kind':kind,'ranks':[],'route_count':len(rr)})['ranks'].append(rank)
            for rid,tape in rr:
                candidate_tapes.append((rank,meta['id'],f'{kind}:{rid}',encode_tape(tape)))
            family.append({'kind':kind,'sha256':objsha,'routes':len(rr)})

        if 'actions.json' in extra:
            try:
                obj=json.loads(extra['actions.json'])
                count=0
                if isinstance(obj,list):
                    for j,tape in enumerate(obj):
                        if isinstance(tape,list) and len(tape)==719:
                            candidate_tapes.append((rank,meta['id'],f'archive_actions:{j}',encode_tape(tape)))
                            count+=1
                    family.append({'kind':'archive_actions','sha256':sha(extra['actions.json']),'routes':count})
                for n,b in extra.items():
                    if n!='main.py':
                        (out/'sources'/f'r{rank:02d}_{Path(n).name}').write_bytes(b)
            except Exception:
                pass

        if 'source/tape.inc' in extra:
            rr=parse_tape_inc(extra['source/tape.inc'])
            for rid,arr in rr:
                candidate_tapes.append((rank,meta['id'],rid,arr))
            if rr:
                family.append({'kind':'apex_cpp','sha256':sha(extra['source/tape.inc']),'routes':len(rr)})

        entries.append({
            'rank':rank,'ref':meta['id'],'title':meta['title'],
            'source_sha256':src_sha,'source_bytes':len(src) if src else 0,
            'extract_method':method,'license_markers':sorted(set(lic)),
            'programme_families':family,
        })

    tapes=[]
    programs=[]
    bysha={}
    for rank,ref,label,arr in candidate_tapes:
        h=sha(arr.tobytes())
        if h in bysha:
            programs[bysha[h]]['aliases'].append({'rank':rank,'ref':ref,'label':label})
            continue
        idx=len(tapes)
        bysha[h]=idx
        tapes.append(arr)
        programs.append({'program_id':idx,'sha256':h,'origin_rank':rank,'origin_ref':ref,'origin_label':label,'aliases':[]})

    tape_arr=np.stack(tapes).astype(np.int16) if tapes else np.empty((0,719,ACTION_WIDTH),dtype=np.int16)
    np.savez_compressed(out/'PROGRAMME_CORPUS.npz',tapes=tape_arr)

    exact_dups={}
    for e in entries:
        if e['source_sha256']:
            exact_dups.setdefault(e['source_sha256'],[]).append(e['rank'])

    manifest={
        'schema':'kculture-public-programme-corpus-v1',
        'notebooks':len(entries),
        'unique_sources':len(exact_dups),
        'source_duplicates':{k:v for k,v in exact_dups.items() if len(v)>1},
        'route_banks':route_bank_fingerprints,
        'candidate_programmes_before_dedup':len(candidate_tapes),
        'unique_programmes':len(programs),
        'action_width':ACTION_WIDTH,
        'turns':719,
        'entries':entries,
        'programmes':programs,
    }
    (out/'PROGRAMME_CORPUS.json').write_text(json.dumps(manifest,indent=2,sort_keys=True),encoding='utf-8')

    print('PROGRAMME_CORPUS_RESULT',json.dumps({
        'notebooks':manifest['notebooks'],
        'unique_sources':manifest['unique_sources'],
        'candidate_programmes':manifest['candidate_programmes_before_dedup'],
        'unique_programmes':manifest['unique_programmes'],
        'banks':[{'kind':v['kind'],'routes':v['route_count'],'ranks':v['ranks']} for v in route_bank_fingerprints.values()],
    },sort_keys=True),flush=True)
    print('PROGRAMME_CORPUS_OUT',str(out/'PROGRAMME_CORPUS.json'),flush=True)

if __name__=='__main__':
    main()
