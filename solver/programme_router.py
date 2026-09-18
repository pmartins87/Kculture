"""One exact-prefix continuation decision per episode; observation-only inference."""
from solver.programme_features import features
from solver.programme_actions import decode
class ProgrammeRouter:
    def __init__(self,tapes,model,enabled=True):
        self.tapes=tapes;self.model=model;self.enabled=enabled
        self.program=model['static_program'];self.decided=False;self.calls=0
    def act(self,obs,config=None):
        step=int(obs['step']);m=self.model
        if self.enabled and not self.decided and step>=m['checkpoint']:
            if step!=m['checkpoint']:raise RuntimeError('missed router checkpoint')
            x=features(obs);node=m['tree']
            while 'feature' in node:
                node=node['left'] if x[node['feature']]<=node['threshold'] else node['right']
            self.program=m['members'][int(node['action'])];self.decided=True;self.calls+=1
        return decode(self.tapes[self.program,step])
