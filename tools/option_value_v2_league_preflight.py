#!/usr/bin/env python3
from __future__ import annotations
import json, sys, tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

from tools.programme_adaptive_expert_gate import acquire_public_main, load_public_agent, purge_package_modules, sha256_bytes

SPECS=[
  {"key":"v47_mirror","handle":"ahmedberatozer/kaggriculture-v47-reactive-market-coordination","sha":"f4ecd4876fde93a14e3381993283f3b6a1afa023b48dd57217f4d90794d39842","family":"modern41_v47"},
  {"key":"ready_stock","handle":"alperen5252525/kaggriculture-ready-stock-earlier-sales","sha":"45628c719dc967f81655c19f70e579c55a5758b9fe75a5fcdad9193eebf6a017","family":"modern41_ready_stock"},
  {"key":"v48","handle":"ahmedberatozer/kaggriculture-v48-clear-the-queue","sha":"4b5402888feeb4170dce38f34bebe56788b62ca287139fce7db72df8eb89bb96","family":"modern41_queue"},
  {"key":"v38","handle":"ahmedberatozer/kaggriculture-v38-smarter-feed-stronger-margins","sha":"a2047ebd8ca5720221e1421529655d9c67a7b2fedb74e874c7d3c55a8970ac7e","family":"legacy13"},
  {"key":"conditional_memory","handle":"ravi123a321at/177-180-fresh-top-30-v21-1-conditional-memory","sha":"d9dc24ce5429ec628ead0621a160bee90725350683d7dfcc4686fcaf511f3aab","family":"literal_conditional_memory"},
  {"key":"tactical_memory","handle":"web3cainiao/kaggriculture-v21-tactical-memory","sha":"630125b3f592fdb773f1fac6532b08e97e829ae188180ea17540b702b606a054","family":"literal_tactical_memory"},
  {"key":"best_market","handle":"reyhanksatria/best-market-agent-high-strategy","sha":"d39dba50793d9777c990347443bf0c481c78adaea86055f6f6b0600dcfcd9f2e","family":"literal_market_strategy"},
]

def main():
    rows=[]
    failures=[]
    with tempfile.TemporaryDirectory(prefix="option-league-v2-") as td:
        td=Path(td)
        for spec in SPECS:
            try:
                main_py, receipt=acquire_public_main(spec["handle"],td/spec["key"])
                observed=sha256_bytes(main_py.read_bytes())
                if observed!=spec["sha"]:
                    raise RuntimeError(f"sha mismatch {observed} != {spec['sha']}")
                agent=load_public_agent(main_py)
                rows.append({
                    **spec,
                    "observed_sha":observed,
                    "entrypoint":getattr(agent,"__name__",None),
                    "acquisition":receipt.get("acquisition"),
                })
                purge_package_modules(main_py.parent)
            except Exception as exc:
                failures.append({**spec,"error":f"{type(exc).__name__}: {exc}"})
    out={"schema":"option-value-v2-league-preflight","agents":rows,"failures":failures,"pass":not failures and len(rows)==len(SPECS)}
    p=ROOT/"artifacts/option-value-v2-league/PREFLIGHT.json"
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print("OPTION_VALUE_V2_LEAGUE_PREFLIGHT",json.dumps(out,sort_keys=True))
    if not out["pass"]:
        raise SystemExit(2)

if __name__=="__main__":
    main()
