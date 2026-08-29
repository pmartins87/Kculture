"""CR022 clock-safe diagnostic derivative of frozen CR008.

This is NOT Adaptive V2 strategy logic. It exists only to make the frozen CR008
backbone robust if Kaggle ever delivers an observation whose `step` field is
missing/None while day/hour remain valid.

Critical separation: CR008's learned feature encoder intentionally preserves its
original `step` semantics. Only the delegated R4B/COK backbone receives a
normalized observation. When raw step is present, the exact original object is
passed through and behavior must be identical to CR008.
"""
from __future__ import annotations

import copy
import importlib.util
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BASE_PATH=ROOT/'candidates/cr008_adaptive_frontrun.py'


def _load():
    spec=importlib.util.spec_from_file_location('kculture_cr022_clock_base',BASE_PATH)
    if spec is None or spec.loader is None:raise RuntimeError(f'Unable to load {BASE_PATH}')
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

_CR008=_load()
_ORIGINAL_R4B_AGENT=_CR008._BASE.agent


def _get(o,k,d=None):
    try:return o.get(k,d)
    except AttributeError:
        try:return o[k]
        except Exception:return d


def _normalized_backbone_obs(obs):
    raw=_get(obs,'step',None)
    if raw is not None:
        return obs
    try:
        day=max(0,int(_get(obs,'day',0) or 0));hour=max(0,int(_get(obs,'hour',0) or 0));derived=day*24+hour
    except Exception:
        return obs
    try:
        out=copy.deepcopy(obs)
        out['step']=derived
        return out
    except Exception:
        try:
            out=dict(obs);out['step']=derived;return out
        except Exception:
            return obs


def _clock_safe_r4b(obs,config=None):
    return _ORIGINAL_R4B_AGENT(_normalized_backbone_obs(obs),config)

# Patch only the R4B delegation inside this isolated CR008 module instance.
_CR008._BASE.agent=_clock_safe_r4b


def agent(obs,config=None):
    return _CR008.agent(obs,config)
