"""Closed accepted static Slice 40H fixtures."""
from __future__ import annotations
from dataclasses import replace
from ..schema import stable_record_id
from .schema import GateCloseoutFixture

def _f(name,kinds,projected,companion):
    draft=GateCloseoutFixture('',name,tuple(kinds),projected,companion,True,True,True,True,True)
    return replace(draft,fixture_id=stable_record_id('slice40h_closeout_fixture',{
        'name':name,'kinds':tuple(kinds),'projected':projected,'companion':companion}))

_FIXTURES=(
 _f('slice40h-material-ambiguity',('material_ambiguity_preserved',),1,0),
 _f('slice40h-clarification-relevant',('clarification_relevant',),0,1),
 _f('slice40h-unsupported',('unsupported',),1,0),
 _f('slice40h-refusal-relevant',('refusal_relevant',),1,0),
 _f('slice40h-held',('held',),1,0),
 _f('slice40h-blocked-progression',('blocked_progression',),1,0),
 _f('slice40h-later-selection-review',('candidate_supported_for_later_selection_review',),0,1),
 _f('slice40h-complete-mixed',(
   'material_ambiguity_preserved','clarification_relevant','unsupported','refusal_relevant',
   'held','blocked_progression','candidate_supported_for_later_selection_review'),5,2),
)
def list_gate_closeout_fixtures(): return _FIXTURES
def get_gate_closeout_fixture(name):
    return next((x for x in _FIXTURES if x.fixture_name==name),None) if type(name) is str else None
def is_exact_accepted_fixture(value): return type(value) is GateCloseoutFixture and value in _FIXTURES
