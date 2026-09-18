"""Leave one route-bank family out, with disjoint test seeds; no hyperparameter sweep."""
import sys,json
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'tools')]
from programme_suffix_teacher_v0 import utility,fit_tree,predict,eval_choice
D=ROOT/'data/programme_teacher/2026-09-18'
def family(p):
    labels=[p['origin_label']]+[a['label'] for a in p['aliases']]
    if any(x.startswith('modern41:') for x in labels):return 'modern41'
    if any(x.startswith('legacy13:') for x in labels):return 'legacy13'
    return 'additional_programmes'
def main():
    z=np.load(D/'PROGRAMME_TEACHER_DATA.npz');manifest=json.loads((D/'PROGRAMME_CORPUS.json').read_text())
    # Pool miscellaneous small lineages in one held-out block conservatively.
    families=np.array([family(p) for p in manifest['programmes']]);fam=families[z['opponent_program']]
    result=[]
    for held in sorted(set(families)):
        for gid in np.unique(z['group']):
            ix=np.flatnonzero(z['group']==gid);X=z['features'][ix];R=z[f'group_{gid}_margins'];U=utility(R)
            train=np.flatnonzero((z['holdout'][ix]==0)&(fam[ix]!=held))
            test=np.flatnonzero((z['holdout'][ix]==1)&(fam[ix]==held))
            assert len(train) and len(test)
            tree=fit_tree(X,U,train,0,4,max(12,min(48,len(train)//20)))
            base=int(np.argmax(U[train].mean(0)))
            b=eval_choice(R[test],U[test],np.full(len(test),base));t=eval_choice(R[test],U[test],predict(tree,X[test]));o=eval_choice(R[test],U[test],np.argmax(U[test],axis=1))
            result.append(dict(family=held,group=int(gid),train=len(train),test=len(test),static=b,tree=t,oracle=o))
    summary=[]
    for held in sorted(set(families)):
        rows=[r for r in result if r['family']==held]
        summary.append(dict(family=held,opponents=int((families==held).sum()),static_wr=float(np.mean([r['static']['win_rate'] for r in rows])),tree_wr=float(np.mean([r['tree']['win_rate'] for r in rows])),oracle_wr=float(np.mean([r['oracle']['win_rate'] for r in rows]))))
    out=dict(schema='programme-family-holdout-v1',scope='exploratory route-bank-block holdout; no independent hosted validation',summary=summary,groups=result)
    (D/'FAMILY_HOLDOUT.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(summary))
if __name__=='__main__':main()
