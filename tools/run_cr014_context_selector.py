"""Materialize the frozen CR-002B public references and run CR-014."""
from __future__ import annotations
import json, subprocess, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
CFG=ROOT/'configs/competitive_reset_current_meta_v1.json'
OUT=ROOT/'artifacts/cr014/opponents'
OUT.mkdir(parents=True,exist_ok=True)
config=json.loads(CFG.read_text(encoding='utf-8'))
paths=[]
for i,a in enumerate(config['public_agents']):
    p=OUT/f"ref_{i:02d}.py"; r=OUT/f"ref_{i:02d}.json"
    subprocess.run([sys.executable,str(ROOT/'tools/fetch_exact_package_main.py'),'--handle',a['handle'],'--output',str(p),'--receipt',str(r)],check=True)
    paths.append(p)
cmd=[sys.executable,str(ROOT/'tools/cr014_response_gate_lofo.py')]
for p in paths: cmd += ['--opponent',str(p)]
cmd += ['--output',str(ROOT/'artifacts/cr014/report.json'),'--model-output',str(ROOT/'artifacts/cr014/response_gate_model.json')]
subprocess.run(cmd,check=True)
