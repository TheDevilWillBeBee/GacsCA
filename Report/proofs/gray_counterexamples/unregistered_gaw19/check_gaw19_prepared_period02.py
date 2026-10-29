"""Contracts for the universal single raw-record GAW19 boundary family.

The symbolic executor proves all data values. These checks tie its total
instruction semantics and the physical gather/copy/reset ports to frozen
local_R; concrete local cofactors supplement the written all-value lift.
"""
from pathlib import Path
from functools import lru_cache
from dataclasses import replace
from itertools import product,combinations
import hashlib,json,sys,time
import gaw19_symbolic_executor as a
k=a.k;own=a.own;base=a.base;prior=a.prior;P=a.P;MASK=a.MASK
S=Path(__file__).resolve().parent;ROOT=S.parents[3]
D=ROOT/'figs/gray_counterexamples/unregistered_gaw19'
sys.path.insert(0,str(ROOT))
from gacsca import gray_errors

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def vals(c):
    bits=[1<<i for i in range(100) if c.u>>i&1]
    assert len(bits)<=6
    return [c.v|sum(b for b,on in zip(bits,pattern) if on) for pattern in product((0,1),repeat=len(bits))]

def primitive_checks():
    """Exhaustive small cubes and exact quorum/counter boundary contracts.

    Their finite coverage does not replace the proof of 100-bit cube
    soundness in the companion document.
    """
    cubes=[a.B(sum((p==1)<<i for i,p in enumerate(pattern)),sum((p==2)<<i for i,p in enumerate(pattern)))
           for pattern in product(range(3),repeat=3)]
    checks=0;digest=hashlib.sha256()
    for x,y in product(cubes,repeat=2):
        for op in (0,1,2,3,4,5,6,7,8,9,10,11,13,19,20,21,22):
            got=a.alu(op,x,y,a.TOP) # ignored third operands are truly ignored
            for xv,yv in product(vals(x),vals(y)):
                expected=k.generic_alu(op,xv,yv,0)
                assert got.contains(expected),(op,x,y,xv,yv,got,expected)
                checks+=1
            digest.update(str((op,x,y,got)).encode())
    # One arbitrary full-width chunk can never upset a known >=3 quorum.
    quorum=0
    for value in (0,1,k.Q-1,k.U-1):
        for unknown in range(5):
            packed=a.C(0)
            for i in range(5):packed=a.bor(packed,a.shift(a.B(0,(1<<20)-1) if i==unknown else a.C(value),20*i))
            assert a.alu(14,packed,a.TOP,a.TOP)==a.C(value)
            assert a.alu(15,packed,a.TOP,a.TOP)==a.C(1)
            quorum+=2
    # Full-width VADDINDEX masks after addition; native Address quorums
    # recover even if the bad raw word has arbitrary 100-bit padding.
    adjusted=0
    for centre in (0,1,2,k.Q-3,k.Q-2,k.Q-1):
        for side in (-1,1):
            for unknown in range(5):
                packed=a.C(0)
                for i in range(5):
                    v=a.B(0,(1<<20)-1) if i==unknown else a.C((centre+side*(i+1))%k.Q)
                    packed=a.bor(packed,a.shift(v,20*i))
                value=a.alu(16,packed,a.C(-side),a.C(13))
                assert a.alu(14,value,a.TOP,a.TOP)==a.C(centre)
                adjusted+=1
    return dict(exhaustive_three_bit_cube_concretization_checks=checks,
        exact_full_width_quorum_contracts=quorum,adjusted_GF_four_clean_vote_contracts=adjusted,
        primitive_trace_sha256=digest.hexdigest(),universal_soundness_supplied_by_written_proof=True)

@lru_cache(None)
def words(g):return (MASK,)*k.FRAME_WORDS if g==0 else tuple(k.cell_words(base.nextH(g)))
@lru_cache(None)
def data(y):
    g,phase=divmod(y,k.Q);i=phase-P
    return words(g)[i] if 0<=i<k.FRAME_WORDS else 0
@lru_cache(None)
def bank(y):return sum(data(y+d*k.Q)<<((d+8)*k.WORD) for d in range(-8,9))

def hist(y,age,stage):
    return sum(data(y+(lane-8)*k.Q)<<(lane*k.WORD) for lane in range(17)
        if age>=k.capture(stage,lane)) if age>=k.GATHER_STARTS[stage-1] else 0

def prefix(x,age):
    start=max(s for s in k.STAGE_STARTS if s<=age)
    distance=min(age-start-1,16*k.Q-2) if start in k.GATHER_STARTS and age>start else None
    ml=lambda y:data(y+distance) if distance is not None else 0
    mr=lambda y:data(y-distance) if distance is not None else 0
    full=k.EARLY_RESET<=age<96*k.Q or 102*k.Q+1<=age<k.U
    return k.Cell(addr=x%k.Q,age=age,info=tuple(data(x+s) for s in k.SLOTS),
        program=tuple(k.beta_bit(own.ROM,(x+s)%k.Q) for s in k.SLOTS),
        mem=tuple(bank(x+s) if full else 0 for s in k.SLOTS),
        mail_l=tuple(ml(x+s) for s in k.SLOTS),mail_r=tuple(mr(x+s) for s in k.SLOTS),
        history1=tuple(hist(x+s,age,1) for s in k.SLOTS),
        history2=tuple(hist(x+s,age,2) for s in k.SLOTS),
        history3=tuple(hist(x+s,age,3) for s in k.SLOTS))

def actual_control_checks():
    checks=0;dig=hashlib.sha256();events=[]
    # Native words plus different packet/Mem/Info/Programme/History groups.
    indices=(0,1,2,3,4,5,6,k.FIELD['m0'],k.FIELD['info'],k.FIELD['program'],k.FRAME_WORDS-1)
    for stage in (1,2,3):
        for lane in range(17):
            g=8-lane;age=k.capture(stage,lane)
            for i in indices:
                y=g*k.Q+P+i
                for s in k.SLOTS:events.append((y-s,age))
    ages=sorted(set(k.STAGE_STARTS[1:])|{1,32*k.Q+1,64*k.Q+1,k.EARLY_RESET,k.EARLY_BIRTH,
        102*k.Q+1,75*k.Q,80*k.Q-1,96*k.Q-1,96*k.Q+1,98*k.Q-1,98*k.Q,99*k.Q})
    offsets=(0,1,2,3,4,5,P-2,P,P+1,P+2,P+3,P+4,P+5,P+k.FRAME_WORDS-1,
        P+k.FRAME_WORDS+1,k.Q-5,k.Q-4,k.Q-3,k.Q-2,k.Q-1)
    def old_with_work(x,age):
        z=prefix(x,age)
        if k.EARLY_BIRTH<=age<96*k.Q:
            # Actual early HALT is at P+5; its six known native outputs
            # have been proved universally by the symbolic execution.
            g=x//k.Q;out=k.cell_words(base.next2H(g))[:6]
            z=replace(z,out=tuple(out[(x+s)%k.Q-P] if P<=(x+s)%k.Q<P+6 else 0 for s in k.SLOTS))
        return z
    for g in range(-8,9):
        for age in ages:
            for offset in offsets:events.append((g*k.Q+offset,age))
    for x,age in events:
        got=k.local_transition({j:old_with_work(x+j,age-1) for j in range(-8,9)},own.ROM)
        expected=old_with_work(x,age)
        if age in (k.EARLY_BIRTH,102*k.Q+1):
            expected=replace(expected,heads=tuple(k.pack(k.Packet(p=1,pc=own.ROM.early_pc if age==k.EARLY_BIRTH else 0))
                if (x+s)%k.Q==P else 0 for s in k.SLOTS))
        # We check all derived noninterpreter fields at controls. During
        # active rows head/Scratch/Out are handled by the universal physical
        # copy factor; do not substitute these constructed values for them.
        names=('addr','age','f1','f2','wf1','wf2','info','program','mem','mail_l','mail_r',
               'history1','history2','history3','courier_l','courier_r')
        for name in names:assert getattr(got,name)==getattr(expected,name),(x,age,name)
        if age in k.STAGE_STARTS or age==k.EARLY_RESET:
            assert got.heads==got.out==got.scratch==(0,)*5
        if age in (k.EARLY_BIRTH,102*k.Q+1):assert got.heads==expected.heads
        dig.update(json.dumps([x,age,[getattr(got,n) for n in names]],separators=(',',':')).encode());checks+=1
    return dict(actual_local_R_capture_control_source_checks=checks,
        allM_capture_indices=list(indices),actual_noninterpreter_control_digest_sha256=dig.hexdigest(),
        no_future_WF_tape_selected=True,universality_from_derived_zero_early_seeds_and_written_gather_factor=True)

def concrete_emitted_replays():
    cases=[];checks=0
    for g in range(-8,9):
        tape={P+i:bank(g*k.Q+P+i) for i in range(k.FRAME_WORDS)}
        for early in (True,False):
            out,ticks,packet,trace=k.execute(own.ROM,tape,limit=147455,record=True,early=early)
            assert packet.mode==k.HALT and ticks in (150,65062)
            expected=k.cell_words(base.next2H(g))
            assert [out.get(P+i,0) for i in range(6 if early else k.FRAME_WORDS)]==expected[:6 if early else k.FRAME_WORDS]
            # Cover every physical incoming/mode/store kind. The algebra
            # in the proof gives this factor for arbitrary coherent words.
            cover=set();beforeout={};scratch={};oldaddress=P
            for t,(address,oldp,newp,ow,sw) in enumerate(trace,1):
                key=(oldp.mode,newp.mode,oldp.move,newp.move,oldp.args&3)
                if key not in cover or t<=3:
                    age=(k.EARLY_BIRTH if early else 102*k.Q+1)+t
                    def cell(x,new=False):
                        z=prefix(x,age if new else age-1);origin=g*k.Q
                        outs=beforeout if not new or ow is None else {**beforeout,address:ow}
                        scraps=scratch if not new or sw is None else {**scratch,address:sw}
                        return replace(z,heads=tuple(k.pack(newp if new else oldp) if x+s==origin+(address if new else oldaddress) else 0 for s in k.SLOTS),
                            out=tuple(outs.get(x+s-origin,0) for s in k.SLOTS),scratch=tuple(scraps.get(x+s-origin,0) for s in k.SLOTS))
                    xs={g*k.Q+q-s for q in (oldaddress,address) for s in k.SLOTS}
                    for x in xs:
                        assert k.local_transition({j:cell(x+j) for j in range(-8,9)},own.ROM)==cell(x,True),(g,early,t,x)
                        checks+=1
                cover.add(key)
                if ow is not None:beforeout[address]=ow
                if sw is not None:scratch[address]=sw
                oldaddress=address
            cases.append(dict(receiver=g,early=early,HALT=True,updates=ticks,
                actual_mode_movement_coverage=[list(v) for v in sorted(cover)],
                full_output_known_shadow=True))
        print(json.dumps(dict(stage='concrete_allM_execution_and_copy_ports',receiver=g)),flush=True)
    return dict(cases=cases,actual_local_R_instruction_mode_movement_checks=checks,
        concrete_replays_only_supplement_universal_symbolic_certificate=True)

def boundary_checks():
    count=0;dig=hashlib.sha256()
    for g in range(-8,9):
        clean=k.cell_words(base.next2H(g))
        def old(x):
            return replace(prefix(x,k.U-1),out=tuple(clean[(x+s)-g*k.Q-P] if P<=(x+s)-g*k.Q<P+k.FRAME_WORDS else 0 for s in k.SLOTS))
        xs={g*k.Q+r for r in range(P-4,P+k.FRAME_WORDS+5)}
        xs.update(g*k.Q+r for r in (-5,-3,-2,-1,0,1,2,3,4,5,k.Q-5,k.Q-4,k.Q-3,k.Q-2,k.Q-1))
        for x in sorted(xs):
            got=k.local_transition({j:old(x+j) for j in range(-8,9)},own.ROM)
            assert got==base.encoded(x,base.next2H),(g,x,'complete raw commit/reset')
            dig.update(json.dumps([x,k.cell_words(got)],separators=(',',':')).encode());count+=1
    return dict(actual_complete_boundary_local_R_checks=count,complete_boundary_digest_sha256=dig.hexdigest(),
        unused_Info_zero_and_all_native_SF_reset_and_Programme_checked=True)

def reachable_allM_row():
    # An explicit additional example: inject at the actual clean first-U
    # row. Every one of these 500 whole-cell replacements changes Info.
    payloads=[];support=set();digest=hashlib.sha256()
    for x in range(P-2,P+k.FRAME_WORDS+2):
        old=base.encoded(x,base.nextH)
        new=replace(old,info=tuple(data(x+s) for s in k.SLOTS))
        assert old!=new
        support.add((x,k.U));ws=k.cell_words(new)
        payloads.append([x,k.U,[hex(v) for v in ws]])
        digest.update(json.dumps(payloads[-1],separators=(',',':')).encode())
    assert len(support)==500
    first=gray_errors.classify(support,Q=k.Q,U=k.U,sep=104)
    assert not first['level0'] and not first['level1'] and first['candidate_level1'] and first['witness']
    # Original candidate2: two adjacent-pair candidate1 subsets are linked
    # at24Q; (iii) no104Q-separated subsets because totaldiam499<104Q;
    # (iv) no errors outside. Dense connectivity excludes every isolated
    # proper real1 subset; wholeSfailsiii by the retained pair witness.
    pairs=[[(P-2,k.U),(P-1,k.U)],[(P+104,k.U),(P+105,k.U)]]
    assert gray_errors.linked(pairs[0],pairs[1],24*k.Q,24*k.U)
    # They are candidate1 subsets relative to the *shared* full history,
    # not actual real1 errors: their isolation from the other498 sites
    # deliberately fails. Relative to themselves each would instead beE0.
    for p in pairs:
        q=gray_errors.classify(p,E=support,Q=k.Q,U=k.U,sep=104)
        assert q['candidate_level1'] and not q['level1'] and not q['level0']
    return dict(chronological_clean_prefix_uses_intact_H_period_theorem=True,
        physical_time=k.U,points=500,extent=[500,1],all_whole_cell_replacements_genuinely_changed=True,
        exact_original_c104_class='one actual real2; no actual E0/E1 points',
        actual_E1_empty_by_dense_line_isolation_and_whole_set_iii_failure=True,
        classifier_real1_failure=first,candidate2_linked_candidate1_pairs=pairs,
        condition_iii_all_subset_diameter_bound=[499,0],condition_iii_threshold=[104*k.Q,104*k.U],
        condition_iv_empty_external_error_history=True,
        full_whole_cell_payloads=payloads,payload_sha256=digest.hexdigest(),
        exact_noisy_U_is_the_allM_member_of_the_prepared_family=True,
        complete2U_and_all_later_shadow_follows_from_universal_prepared_period=True,
        arbitrary_prepared_record_real1_reachability_claim=False)

def main():
    start=time.monotonic();symbolic=json.loads((D/'GAW19_symbolic_execution_certificate.json').read_text())
    assert symbolic['universal_single_prepared_record_emitted_outputs_and_deadline']
    r=dict(Q=k.Q,U=k.U,error_lambda=24,error_separation=104,
        symbolic_certificate_sha256=sha(D/'GAW19_symbolic_execution_certificate.json'),
        primitive_contracts=primitive_checks(),actual_gather_control_ports=actual_control_checks(),
        concrete_copy_execution_ports=concrete_emitted_replays(),actual_raw_boundary=boundary_checks(),
        additional_actual_intact_start_allM_error=reachable_allM_row(),
        quantified_arbitrary_record_words=496,quantified_arbitrary_record_bits=49600,
        exact_prepared_background='E(R(H),0), receiver0 raw496 Word100 record arbitrary',
        actual_global_period_composition_proved_by_universal_execution_and_written_factor=True,
        universal_malformed_native_refinement=False,later_shadow_phases_or_real1_higher_Gray_iid_or_shorterU=False,
        new_rule_native_projection_or_legal_upper_theorem_on_W=False)
    # Canonicalize tuple-valued classifier coordinates to their JSON form.
    # No numeric value, predicate, payload or transition is changed.
    r=json.loads(json.dumps(r))
    path=D/'GAW19_prepared_period_certificate.json'
    if '--issue' in sys.argv:assert not path.exists();path.write_text(json.dumps(r,indent=2)+'\n')
    else:assert r==json.loads(path.read_text())
    print(json.dumps(dict(passed=True,elapsed_seconds=time.monotonic()-start,stage='prepared_family_physical_contracts')),flush=True)
    return r

if __name__=='__main__':main()
