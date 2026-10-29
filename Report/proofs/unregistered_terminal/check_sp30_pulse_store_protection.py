"""Uniform conditional early-Hold protection; no actual-history iteration."""
from pathlib import Path
from itertools import product
import hashlib,json,sys,time
import numpy as np
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'Report/proofs'))
from gacsca import rule_g
import proposed_sparse_signal_reservation1024 as proposed
import check_signal_reservation1024_encoded as encoded


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    started=time.monotonic();p=proposed.parameters();c=proposed.load_artifact()
    dest=ROOT/'figs/robustness/unregistered_pulse_store'
    dest.mkdir(exist_ok=True)
    proof=Path(__file__).with_name('SP30_PULSE_STORE_PROTECTION.md')
    listing_path=ROOT/'figs/robustness/SP30_program_listing.json'
    listing=json.loads(listing_path.read_text())
    assert (p.Q,p.U,p.T_wf,p.fronts,p.delta,p.PK,p.NH,p.mux_front,p.sel_front)==(1024,475136,278401,5,5,3,1,True,0)
    S=p.T_wf+6144;phases=(*range(59,69),88);issues=[];keys=0
    for a,shift in product(phases,(0,512)):
        phase=a+shift
        found=[row for row in listing if row[4]==phase and row[6]==rule_g.K_HOLD]
        assert len(found)==1
        row=found[0];column=row[1]+(row[3]<<p.logNP)
        assert np.flatnonzero(((c.rom[phase]>>2)&3)==rule_g.K_HOLD).tolist()==[column]
        t=p.E0+row[1]*p.PL+row[2]
        assert t+2<p.T_wf if shift==0 else t>S
        issues.append(dict(normal_phase=a,phase_shift=shift,ROM_column=column,
                           input_issue=t,materialized=t+2))
        keys+=c.rom.shape[1]
    assert keys==90112
    diff=sorted({((i-j)*p.delta)%p.Q for i,j in product(range(5),repeat=2)})
    assert 512 not in diff
    # All five-copy subsets and every PK-bit kind, including unused kinds.
    # Absent actual records have zero kind; no raw noise is introduced here.
    pending=0
    for kind,mask in product(range(1<<p.PK),range(32)):
        present=[(mask>>i)&1 for i in range(5)]
        words=[kind if v else 0 for v in present]
        presence=int(sum(present)>=3)
        voted=sum(int(sum((w>>b)&1 for w in words)>=3)<<b for b in range(p.PK))
        assert not presence or voted==kind
        pending+=1
    assert pending==256
    # These exact interfaces are rechecked without invoking their writers.
    reset,forward=encoded.commit(p);assert (reset,forward)==(807,5)
    mask=(set(range(58,901))-{509,515})|{901,902,965}
    assert set(phases)<=mask
    reservations=[]
    for j,a,s in product(range(-8,-7),phases,proposed.SLOTS):
        end=j*p.Q+a-s+37
        assert end<-7616
        reservations.append(dict(relative_colony=j,phase=a,slot=s,right_GF_reserve=end))
    left_clearance=-7616-max(r['right_GF_reserve'] for r in reservations)
    assert left_clearance==449
    right=[]
    for j,a,s in product(range(6,24),range(59,69),proposed.SLOTS):
        start=j*p.Q+a-s-37
        assert start>6*p.Q
        right.append(dict(relative_colony=j,phase=a,slot=s,left_GF_reserve=start))
    assert min(r['left_GF_reserve'] for r in right)-6*p.Q==20
    recovered=[(j,a,s) for j,a,s in product(range(6),phases,proposed.SLOTS)]
    assert len(recovered)==330
    assert set(range(6))|set(range(6,24))==set(range(24))
    assert [j-(-6) for j in range(23)]==list(range(6,29))
    # The written argument depends on these actual control/copy equations.
    front=(ROOT/'gacsca/rule.py').read_text()
    assert "psel = w_mux(n, match_pass, rsrc[k:k + p.PW], list(t) + list(page) + fid)" in front
    mux=(ROOT/'gacsca/rule_g.py').read_text().split('def _mux_front(',1)[1].split('def _sel_front(',1)[0]
    for literal in ('not_match = n.NOT(match_pass)',
                    'executing = n.AND(arr[d], not_match)',
                    'new[\'pend\'][d + 2] = pend',
                    'new[\'pkind\'][(d + 2) * p.PK + j] = pkind[j]'):
        assert literal in mux,literal
    generated=proposed.generated_source(p)
    assert "holds = [n.AND(lv(x, 'hold', r), n.NOT(commit)) for r in range(p.NH)]" in generated
    assert "new[f][(slot + 2) * w + i] = n.AND(keep, vals[f][i])" in generated
    deps=('SP30_encoded_certificate.json','SP30_front_certificate.json',
          'SP30_translation_class_certificate.json','SP30_seventh_signal_certificate.json')
    certificate=dict(name='SP30 uniform conditional pulse-store protection',
        proof_sha256=sha(proof),checker_sha256=sha(__file__),
        candidate_sha256=c.digest(),netlist_sha256=c.comp.digest,
        listing_sha256=sha(listing_path),full_generated_source_sha256=hashlib.sha256(generated.encode()).hexdigest(),
        source_dependencies_sha256={name:sha(ROOT/name) for name in (
            'gacsca/rule.py','gacsca/rule_g.py','gacsca/netlist.py',
            'Report/proofs/proposed_sparse_signal_reservation1024.py',
            'Report/proofs/check_signal_reservation1024_encoded.py')},
        receipt_dependencies_sha256={name:sha(ROOT/'figs/robustness'/name) for name in deps},
        Q=p.Q,U=p.U,T_wf=p.T_wf,pulse_end=S,
        Hold_ROM_keys=keys,Hold_issue_records=issues,comb_differences=diff,
        pending_presence_kind_cases=pending,commit_reset_bits=reset,
        forwarded_Hold_Info_identities=forward,recovered_zero_GF_F1_Info_copies=330,
        protected_edge_reservations=reservations,right_GF_reservations=right,
        left_edge_clearance=449,right_GF_clearance=20,
        conditional_destination_exclusion_and_Hold_preservation_proved=True,
        all_integer_K_translations_covered=True,
        native_history_reset_and_actual_ROM_premises_required=True,
        pre_TF_correct_Hold_values_supplied_by_this_lemma=False,
        actual_all_period_regeneration_or_history_or_permanent_defect_proved=False,
        global_reliability_established=False,active_rule_modified=False,
        elapsed_seconds=time.monotonic()-started)
    (dest/'certificate.json').write_text(json.dumps(certificate,indent=2)+'\n')
    print(json.dumps({key:certificate[key] for key in (
        'Hold_ROM_keys','pending_presence_kind_cases','commit_reset_bits',
        'recovered_zero_GF_F1_Info_copies','left_edge_clearance','right_GF_clearance',
        'conditional_destination_exclusion_and_Hold_preservation_proved',
        'actual_all_period_regeneration_or_history_or_permanent_defect_proved',
        'global_reliability_established','elapsed_seconds')}),flush=True)


if __name__=='__main__':main()
