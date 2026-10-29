"""Interface checks for the universal two-existing-block word argument."""
from pathlib import Path
import hashlib,json,sys,time
import numpy as np

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'Report/proofs'))
from gacsca.netlist import Net,Compiled,majority_word
import proposed_sparse_signal_reservation1024 as proposed
import proposed_distant_native448 as distant

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main(write=True):
    started=time.monotonic();p=proposed.parameters()
    assert (p.Q,p.k,p.m)==(1024,10,19)
    assert distant.CENTERS==(-30,-10,10,30)
    assert distant.REFINED==tuple(range(-5,6))
    total=0;checks=[]
    for w in range(1,5):
        n=Net();C=[n.input(('C',b)) for b in range(w)]
        X=[n.input(('X',b)) for b in range(w)]
        Y=[n.input(('Y',b)) for b in range(w)]
        vx=n.input(('vx',));vy=n.input(('vy',))
        word,exists=distant.block_quorum(n,[(X,vx),(Y,vy),(C,1),(C,1)],C)
        for b,node in enumerate(word):n.set_output(('result',b),node)
        z=np.arange(1<<(3*w+2),dtype=np.uint32)
        values={('C',b):((z>>b)&1).astype(bool) for b in range(w)}
        values.update({('X',b):((z>>(w+b))&1).astype(bool) for b in range(w)})
        values.update({('Y',b):((z>>(2*w+b))&1).astype(bool) for b in range(w)})
        values['vx',]=((z>>(3*w))&1).astype(bool)
        values['vy',]=((z>>(3*w+1))&1).astype(bool)
        comp=Compiled(n);result=comp.evaluate(values,bool)
        assert all(np.array_equal(result['result',b],values['C',b]) for b in range(w))
        total+=len(z);checks.append(dict(width=w,cases=len(z),netlist_sha256=comp.digest))
    n=Net();A=[n.input(('common_Age',b)) for b in range(p.m)]
    symbolic_majorities=0;geometry=0
    for gf in range(p.Q):
        C=[(gf>>b)&1 for b in range(p.k)]+A
        word,exists=majority_word(n,[C]*5,C)
        assert word==C and exists==1
        symbolic_majorities+=1
        for side in (-1,1):
            for center in ((-30,-10) if side==-1 else (10,30)):
                for u in range(-2,3):
                    d=center+u
                    assert side*d>=8
                    assert ((gf+d)%p.Q-d)%p.Q==gf
                    geometry+=1
    assert (total,symbolic_majorities,geometry)==(18720,1024,20480)
    quiet=json.loads((ROOT/'figs/robustness/unregistered_quiet_frame/certificate.json').read_text())
    assert quiet['complete_frame_SF_holder_interval']==[1,1023]
    assert quiet['native_outputs_structurally_instruction_independent']==31
    source=(ROOT/'Report/proofs/proposed_distant_native448.py').read_text()
    assert 'exists=at_least(n,[n.AND(valid,w_eq(n,word,bitwise))' in source
    assert 'return w_mux(n,exists,bitwise,default),exists' in source
    proof=Path(__file__).with_name('SP30_HALF_LINE_REFINEMENT.md')
    result=dict(name='SP30 canonical half-line native-pair refinement',Q=p.Q,U=p.U,
        actual_pair_width=p.k+p.m,checker_sha256=sha(__file__),proof_sha256=sha(proof),
        candidate_sha256=proposed.load_artifact().digest(),
        source_dependencies_sha256={name:sha(ROOT/name) for name in (
            'Report/proofs/proposed_sparse_signal_reservation1024.py',
            'Report/proofs/proposed_distant_native448.py','gacsca/netlist.py',
            'Report/proofs/unregistered_terminal/SP30_QUIET_FRAME_PROTOCOL.md')},
        receipt_dependencies_sha256={'unregistered_quiet_frame/certificate.json':sha(ROOT/'figs/robustness/unregistered_quiet_frame/certificate.json')},
        actual_block_quorum_finite_checks=checks,total_small_word_assignments=total,
        identical_symbolic_pair_majorities=symbolic_majorities,modulo_geometry_cases=geometry,
        universal_all_word_width_two_existing_block_argument_proved=True,
        arbitrary_left_native_words_allowed=True,canonical_right_pair_required=True,
        arbitrary_integer_boundary_and_GF_wrap_covered=True,
        conditional_true_right_edge_frame_keep_and_late_store_lift_proved=True,
        actual_pulse_and_prefix_geometry_clock_ROM_reset_captures_required=True,
        actual_multiperiod_bootstrap_or_general_eroder_proved=False,
        global_reliability_established=False,active_rule_or_frozen_SP30_changed=False,
        elapsed_seconds=time.monotonic()-started)
    dest=ROOT/'figs/robustness/unregistered_half_line_refinement';dest.mkdir(exist_ok=True)
    if write:(dest/'certificate.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('total_small_word_assignments',
        'identical_symbolic_pair_majorities','modulo_geometry_cases',
        'universal_all_word_width_two_existing_block_argument_proved',
        'global_reliability_established','elapsed_seconds')}),flush=True)

if __name__=='__main__':main()
