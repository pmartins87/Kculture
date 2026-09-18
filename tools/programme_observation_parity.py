"""Compare programme native path with independently serialized observation path."""
import sys,json
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'native/programme'),str(ROOT/'external/kaggriculture-cppsim')]
import kagprog,kagsim
from solver.programme_features import features,ITEMS
from tools.build_public_programme_corpus_v1 import UNIT_OP,MARKET_OP
from solver.programme_actions import decode
def main():
    tapes=np.load(sys.argv[1])['tapes'].astype(np.int32)
    ids=[0,38,51,52,54,55,58,59];points=[0,144,168,192,216,240,480,718]
    comparisons=0;games=0
    for i,p in enumerate(ids):
        q=ids[(i+1)%len(ids)];seed=52001+i
        expected={t:kagprog.prefix_features(tapes[p],tapes[q:q+1],[seed],t,1) for t in points}
        margins=kagprog.evaluate_matrix(tapes[p:p+1],tapes[q:q+1],[seed],1)['margin'].reshape(2)
        for seat in [0,1]:
            game=kagsim.Game(seed)
            for t in range(719):
                if t in expected:
                    actual=features(game.observe(seat))
                    np.testing.assert_array_equal(actual,expected[t][seat],err_msg=f'program={p} seat={seat} step={t}')
                    comparisons+=1
                a,b=decode(tapes[p,t]),decode(tapes[q,t])
                game.step(a,b) if seat==0 else game.step(b,a)
            assert game.reward(seat)-game.reward(1-seat)==margins[seat]
            games+=1
    result=dict(pass_gate=True,games=games,feature_vectors=comparisons,feature_values=comparisons*114,scope='kagprog vs pinned kagsim observation/action serialization; official hosted not rechecked')
    out=ROOT/'data/programme_teacher/2026-09-18/OBSERVATION_PARITY.json';out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
if __name__=='__main__':main()
