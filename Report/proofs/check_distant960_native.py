#!/usr/bin/env python3
"""SP23 native-only transfer of J125; programme/data map remain separate."""
import hashlib,json,time
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
import numpy as np
from gacsca.netlist import Net,Compiled,mixed_age_increment
import proposed_sparse_distant960 as proposed
import check_distant_native448 as local_checker


def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    started=time.monotonic();p=proposed.parameters();n,comp=proposed.cached(p)
    raw={j:{f:[n.input(('x',j,f,b)) for b in range(w)] for f,w in proposed.schema(p)}
         for j in proposed.local.OFFSETS}
    corrected=proposed.local.refine(n,raw,p)
    cells={j:dict(value,**corrected[j]) if j in corrected else value for j,value in raw.items()}
    service=proposed.service_build(n,{j:dict(packet_tag=cells[j]['packet_tag'],packet_count=cells[j]['packet_count'],
        packet_valid=cells[j]['packet_valid'][0],wf2=cells[j]['wf2'][0],
        flag_valid=cells[j]['service_valid'][0],flag_position=cells[j]['service_position'],
        flag_count=cells[j]['service_count']) for j in range(-5,6)},p)
    epoch=proposed.previous.base.starter.epoch(n,cells,p);pressure=proposed.pulse(n,cells,p)
    native={j:dict(addr=cells[j]['addr'],age=cells[j]['age'],
        **{f:cells[j][f][0] for f in ('f1','f2','wf1','wf2')}) for j in proposed.local.OFFSETS}
    mt=proposed.proposed_build()[0](n,native,p.k,p.m,Q=p.Q,nb=p.nb,radix=p.R,pos_bits=p.PB,
        service_force=n.any([service['service_force'],epoch['force'],pressure['signal']]))
    identities=0
    for f in ('addr','age'):
        for b,node in enumerate(mt[f]):
            assert n.outputs['y',f,b]==node;identities+=1
    for address in range(p.Q):
        for bad in range(4): local_checker.one_bad_block(p,address,bad)
        local_checker.native_cofactor(p,address)
    clock=Net();bits=[clock.input(('age',b)) for b in range(p.m)]
    successor=mixed_age_increment(clock,bits,p.PB,p.R,p.nb)
    for b,node in enumerate(successor):clock.set_output(('age',b),node)
    codes=np.array([p.age_code(t) for t in range(p.U)],dtype=np.uint32)
    expected=np.array([p.age_code((t+1)%p.U) for t in range(p.U)],dtype=np.uint32)
    got=Compiled(clock).evaluate({('age',b):((codes>>b)&1).astype(bool) for b in range(p.m)},bool)
    assert all(np.array_equal(got['age',b],((expected>>b)&1).astype(bool)) for b in range(p.m))
    assert proposed.LANE_OFFSETS==tuple(json.loads((ROOT/'figs/robustness/distant_native448_certificate.json').read_text())['actual_native_dependency_profile']['addr']['nonzero_offsets'])
    latest=max(g*p.Q+abs(off)*(p.Q//8)+1 for g in p.gathers_q for off in proposed.LANE_OFFSETS)
    assert latest==23641<p.E0==24192
    helper=proposed.framed_build(p)
    assert helper.__globals__['Q']==965 and helper.__globals__['POSITION_BITS']==10
    result=dict(proposal='SP23',proposed_rule_change=True,active_G17_modified=False,SP22_modified=False,
        checker_sha256=digest(Path(__file__)),proposal_source_sha256=digest(Path(proposed.__file__)),
        local_proposal_source_sha256=digest(Path(proposed.local.__file__)),
        local_checker_sha256=digest(Path(local_checker.__file__)),
        helpers_sha256=digest(ROOT/'gacsca/netlist.py'),
        local_certificate_sha256=digest(ROOT/'figs/robustness/distant_native448_certificate.json'),
        proposed_netlist_sha256=comp.digest,module_generated_source_sha256=hashlib.sha256(proposed.generated_source(p).encode()).hexdigest(),
        Q=p.Q,U=p.U,width=proposed.width(p),radius=37,history_ranks=64,
        full_output_native_wiring_identities=identities,one_bad_block_free_word_cofactors=4*p.Q,
        all_phase_native_free_common_Age_and_flags_cofactors=p.Q,legal_clock_increment_cases=p.U,
        initial_global_canonical_GF_Age_required=True,all_other_initial_fields_and_I_arbitrary=True,
        error_set_E0_union_actual_real1_required=True,higher_errors_allowed=False,
        all_time_computed_GF_Age_under_E0_plus_real1_proved=True,
        latest_actual_capture_age=latest,evaluation_age=p.E0,
        frame_size=965,frame_position_bits=10,frame_lifetime_unchanged=1792,
        capture_arithmetic_only_complete_physical_schedule_unproved=True,
        universal_own_programme_or_complete_encoding_proved=False,
        data_map_or_iid_threshold_established=False,global_reliability_established=False,
        seconds=time.monotonic()-started,
        scope='J125 geometry/vote/native induction applies to SP23 changed constants with actual30 GF/Age wiring identities; no own programme/data/higher-error theorem')
    (ROOT/'figs/robustness/SP23_native_certificate.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(native_wiring=identities,cofactors=4*p.Q,legal_clocks=p.U,latest_capture=latest,seconds=result['seconds'])),flush=True)


if __name__=='__main__': main()
