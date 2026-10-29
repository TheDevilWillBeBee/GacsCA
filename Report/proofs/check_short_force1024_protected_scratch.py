#!/usr/bin/env python3
"""Actual protected-prefix composition and a third foreign signal.

No rule change and no third complete-signal/eroder/iid assertion. The
written proof supplies source, pending, native and infinite-line lifts.
"""
from pathlib import Path
import hashlib,json,sys,time
import numpy as np
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from gacsca.netlist import Net,Compiled
from check_g17_schedule import Terms
import proposed_sparse_short_force1024 as proposed


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def execute(p,candidate,listing,terms,readonly,start,end,seed_scratch=None):
    sources=proposed.source_names(p);codes={name:i for i,name in enumerate(sources)}
    fields=[(field,bit) for field,width in candidate.schema for bit in range(width)]
    where={key:int(candidate.layout[i]) for i,key in enumerate(fields)}
    offsets={(row['field'],row['bit']):row['offsets'] for row in proposed.dependency_table(p)}
    live=set(candidate.comp.outputs.values())
    for _,a,b in candidate.comp.gates:live.update((a,b))
    at={}
    for key,node in candidate.comp.index.items():
        if key[0]!='x' or node not in live:continue
        _,off,field,bit=key;cell=where[field,bit]
        code=codes['info',0] if off==0 else codes['ln',offsets[field,bit].index(off)]
        assert (cell,code) not in at
        at[cell,code]=readonly(terms,key)
    regs=[[terms.var(('seed_reg',front,bit)) for bit in range(p.L)] for front in range(p.fronts)]
    scratch=dict(seed_scratch or {});hold={};last={};count=0;matched=False
    for row in listing:
        seq,page,tick,front,cell,op,kind,a,b,dest,note=row
        age=p.E0+page*p.PL+tick
        if age<start or age>=end:continue
        if page>p.MP and not matched:
            for bit in range(p.IW):regs[0][p.k+bit]=terms.var(('I',bit))
            matched=True
        word=int(candidate.rom[cell,page+(front<<p.logNP)])
        mask=(1<<p.SB)-1
        assert (word&3,(word>>2)&3,(word>>4)&mask,(word>>(4+p.SB))&mask,
                (word>>(4+2*p.SB))&((1<<p.DB)-1))==(op,kind,a,b,dest)
        def read(code):
            family,index=sources[code]
            if family=='reg':return regs[front][index]
            if family=='const':return index
            if family=='scr':return scratch.get((cell,index),terms.var(('seed_scr',cell,index)))
            return at[cell,code]
        value=terms.op(op,read(a),read(b));count+=1
        if kind==0:regs[front][dest]=value
        elif kind==1:hold[cell]=value
        elif kind==2:scratch[cell,dest]=value;last[cell,dest]=row
        else:assert kind==3
    return dict(hold=hold,scratch=scratch,last=last,instructions=count,where=where)


def dependencies(terms,target):
    stack=[target];live=set()
    while stack:
        node=stack.pop()
        if node in live:continue
        live.add(node);term=terms.terms[node]
        if term[0] in (0,1,2):stack.extend(term[1])
    return [terms.terms[node][1] for node in sorted(live) if terms.terms[node][0]=='variable']


def blocked(strips,j,d,phase,Q):
    lo,hi=sorted((j*Q+phase,(j+d)*Q+phase))
    return any(lo+8*max(0,(a-lo+7)//8)<=min(hi,b-1) for a,b in strips)


def main():
    begin=time.monotonic();out=ROOT/'figs/robustness';p=proposed.parameters();candidate=proposed.load_artifact()
    listing_path=out/'SP29_program_listing.json';listing=json.loads(listing_path.read_text())
    start=p.E0+280*p.PL
    class MailboxLoad(Net):
        def input(self,key):
            if isinstance(key,tuple) and len(key)==4 and key[0]=='x':
                _,d,field,bit=key
                return ((d%p.Q)>>bit)&1 if field=='addr' else int(field=='info')
            return super().input(key)
    loaded_mail,_=proposed.full_net(p,MailboxLoad)
    assert all(loaded_mail.outputs['y',field,bit]==1 for field in ('mr','ml') for bit in range(5))
    def first_zero(terms,key):return 0 if key[2] in ('h2','mr','ml') else terms.var(key)
    terms=Terms();first=execute(p,candidate,listing,terms,first_zero,start,p.U)
    h2_phases=[first['where']['h2',bit] for bit in range(dict(candidate.schema)['h2'])]
    assert h2_phases==list(range(432,752))
    assert all(first['hold'][phase]==0 for phase in h2_phases)
    h2_issues=[row for row in listing if row[4] in h2_phases and row[6]==1]
    assert len(h2_issues)==320 and len(set(row[4] for row in h2_issues))==320
    assert min(p.E0+row[1]*p.PL+row[2] for row in h2_issues)>start
    def h2_zero(terms,key):return 0 if key[2]=='h2' else terms.var(key)
    fibre_terms=Terms();fibre=execute(p,candidate,listing,fibre_terms,h2_zero,start,p.U)
    dep=dependencies(fibre_terms,fibre['hold'][509]);seeds=[(name[1],name[2]) for name in dep if name[0]=='seed_scr']
    assert len(seeds)==47 and all(name[0] in ('seed_scr','x') for name in dep)
    assert all(name[2] in ('mr','ml') for name in dep if name[0]=='x')
    trace=json.loads((out/'SP29_suffix_control_dependency_probe.json').read_text())
    assert set(dep)==set(tuple(name) for name in trace['cases'][0]['target_dependency_variables'])
    writes=[];keys=0
    for cell,index in seeds:
        prior=[row for row in listing if row[4]==cell and row[6]==2 and row[9]==index and p.E0+row[1]*p.PL+row[2]<start]
        assert prior
        row=prior[-1];age=p.E0+row[1]*p.PL+row[2]
        assert age+2<p.T_wf and cell+2+37<576
        words=candidate.rom[cell]
        actual=np.flatnonzero((((words>>2)&3)==2)&(((words>>(4+2*p.SB))&((1<<p.DB)-1))==index)).tolist()
        expected=sorted(r[1]+(r[3]<<p.logNP) for r in listing if r[4]==cell and r[6]==2 and r[9]==index)
        assert actual==expected
        keys+=len(words)
        writes.append(dict(cell=cell,index=index,last_issue_age=age,materialized_age=age+2,last_sequence=row[0],last_page=row[1]))
    assert keys==192512
    table=proposed.dependency_table(p);phase_at={(r['field'],r['bit']):r['address'] for r in table}
    used_offsets={(r['field'],r['bit']):r['offsets'] for r in table}
    strips=((121*p.Q,121*p.Q+512),(135*p.Q+512,136*p.Q))
    def left_value(j,key):
        _,d,field,bit=key;col=j+d
        if field=='h2':
            # Full-net allocation includes dead ±37 H2 inputs. Bind only
            # its certified live field-specific profile (and direct input).
            if d and d not in used_offsets[field,bit]:return None
            assert col<=120
            return 0
        if field not in ('addr','age','f1','wf1'):return None
        if blocked(strips,j,d,phase_at[field,bit],p.Q):return 0
        assert col<=120
        if field=='addr':return (col%p.Q>>bit)&1
        if field=='f1':return 0
        if col==120:return ('upper120_'+field,bit)
        return (p.age_code(1)>>bit)&1 if field=='age' else 0
    cases=[]
    for j in range(83,115):
        class Captured(Net):
            def input(self,key):
                if isinstance(key,tuple) and len(key)==4 and key[0]=='x':
                    value=left_value(j,key)
                    if isinstance(value,int):return value
                    if isinstance(value,tuple):return super().input(value)
                return super().input(key)
        net,_=proposed.full_net(p,Captured)
        expected={'addr':j%p.Q,'age':p.age_code(2),'f1':0,'h2':0};checks=0
        for field,value in expected.items():
            for bit in range(dict(candidate.schema)[field]):
                assert net.outputs['y',field,bit]==(value>>bit)&1,(j,field,bit)
                checks+=1
        cases.append(dict(colony=j,constant_output_equalities=checks,netlist_sha256=Compiled(net).digest))
    def readonly(terms,key):
        value=left_value(114,key)
        if isinstance(value,int):return value
        return terms.var(value if isinstance(value,tuple) else key)
    joined_terms=Terms();prefix=execute(p,candidate,listing,joined_terms,readonly,p.E0,p.T_wf)
    seed_values={key:prefix['scratch'][key] for key in seeds}
    suffix=execute(p,candidate,listing,joined_terms,readonly,start,p.U,seed_values)
    assert suffix['hold'][509]==0
    assert prefix['instructions']>0 and suffix['instructions']==41477
    # All eight actual second pulses have this protecting support minimum.
    pulse=json.loads((out/'SP29_second_pulse_case_probe.json').read_text())
    hulls=[]
    for case in pulse['cases']:
        rows=[json.loads(line) for line in (out/case['log_name']).read_text().splitlines() if '"row"' in line]
        hull=[min(row['left'] for row in rows),max(row['right_exclusive'] for row in rows)]
        assert hull==[117312,139264]
        assert 114*p.Q+max(cell+2+37 for cell,index in seeds)<hull[0]
        hulls.append(dict(mask=case['mask'],all_row_GF_support_hull=hull))
    # GF Hold timing in the second period gives the actual next zero words.
    GF_rows=[];romkeys=0
    for phase in range(59,69):
        for shift in (0,512):
            current=phase+shift;rows=[row for row in listing if row[4]==current and row[6]==1]
            assert len(rows)==1
            row=rows[0];age=p.E0+row[1]*p.PL+row[2]
            assert age>p.T_wf+6144 if shift else age+2<p.T_wf
            assert np.flatnonzero(((candidate.rom[current]>>2)&3)==1).tolist()==[row[1]+(row[3]<<p.logNP)]
            romkeys+=candidate.rom.shape[1]
            GF_rows.append(dict(phase=current,shift=shift,input_issue_age=age,materialized_age=age+2))
    zero_primaries=[j*p.Q+phase for j in range(115,128) for phase in range(571,581)]
    assert all(118272<=y-2 and y+2<131072 for y in zero_primaries)
    next_strips=((115*p.Q,115*p.Q+512),(127*p.Q+512,128*p.Q));direct=inside=cleared=0
    for h in range(116,128):
        for phase in range(59,69):
            y=h*p.Q-512+phase;assert y in zero_primaries;direct+=1
            row=next(r for r in table if r['address']==phase)
            for d in row['offsets']:
                src=y+d*p.Q;known=src in zero_primaries
                erased=blocked(next_strips,h-1,d,phase+512,p.Q)
                assert known or erased,(h,phase,d,src)
                for gather in p.gathers_q:
                    assert gather*p.Q+abs(d)*(p.Q//8)+1<p.E0
                    if known:inside+=1
                    else:cleared+=1
    assert (direct,inside+cleared)==(120,23040)
    deps=('SP29_second_signal_enclosure_certificate.json','SP29_first_boundary_signal_data_certificate.json',
          'SP29_next_ghost_signal_certificate.json','SP29_suffix_control_dependency_probe.json',
          'SP29_second_pulse_case_probe.json','SP29_symbolic_schedule.json','SP29_front_certificate.json',
          'SP29_encoding_family_certificate.json','SP29_refined_wipe_certificate.json')
    receipt=dict(proposal='SP29',scope='Actual first-left H2zero/second-left protected scratch/second-U zero GF words/third complete foreign signals; same original error/no later errors; no complete third pulse or eroder',
        Q=p.Q,U=p.U,T_wf=p.T_wf,first_left_boundary_H2_zero_bits=320,
        first_tick_mailbox_load_ten_one_copy_identities=10,first_tick_mailbox_load_netlist_sha256=Compiled(loaded_mail).digest,
        first_left_H2_zero_true_colonies_upper_bound=120,first_left_H2_zero_suffix_instructions=first['instructions'],
        first_left_H2_zero_suffix_terms=len(terms.terms),first_left_H2_hold_issues=320,
        protected_scratch_seed_records=writes,protected_scratch_seed_count=47,
        protected_scratch_all_ROM_key_checks=keys,protected_scratch_no_post_TF_issue_proved=True,
        second_pulse_all_eight_GF_support_hulls=hulls,
        second_left_fresh_H2_cofactor_cases=cases,second_left_fresh_H2_constant_output_equalities=sum(row['constant_output_equalities'] for row in cases),
        protected_prefix_instructions=prefix['instructions'],protected_suffix_instructions=suffix['instructions'],
        protected_prefix_suffix_terms=len(joined_terms.terms),protected_prefix_suffix_h2_77_zero_proved=True,
        second_boundary_MF509_zero_true_colonies_upper_bound=114,
        second_boundary_GF_zero_primary_count=len(zero_primaries),second_boundary_GF_zero_copy_count=5*len(zero_primaries),
        second_boundary_GF_zero_primaries=zero_primaries,second_GF_Hold_issue_records=GF_rows,second_GF_all_ROM_key_checks=romkeys,
        third_complete_foreign_frame_count=12,third_foreign_MF509_one_colonies=list(range(116,128)),
        third_foreign_GF_direct_primary_checks=direct,third_foreign_GF_capture_route_checks=inside+cleared,
        third_foreign_inside_zero_capture_routes=inside,third_foreign_strip_cleared_capture_routes=cleared,
        second_actual_native_boundary_clock0_time=2*p.U,third_signal_computed_time=2*p.U+p.T_wf,
        original_initial_upper_Info_arbitrary=True,mailbox_zero_not_required_for_protected_second_left_suffix=True,
        actual_third_complete_foreign_GF_zero_Flag1_signal_proved=True,
        actual_second_left_retained_signal_zero_proved=True,
        actual_full_third_signal_or_third_pulse_proved=False,all_second_boundary_upper_data_restored=False,
        general_eroder_higher_map_or_positive_iid_rate_proved=False,global_reliability_established=False,
        numerical_whole_CA_trajectory_used=False,active_G17_modified=False,rule_programme_or_constant_change=False,
        checker_sha256=digest(__file__),written_proof_sha256=digest(ROOT/'Report/proofs/SP29_PROTECTED_SCRATCH.md'),
        proposal_source_sha256=digest(proposed.__file__),algebra_source_sha256=digest(ROOT/'Report/proofs/check_g17_schedule.py'),
        listing_sha256=digest(listing_path),proposed_candidate_sha256=candidate.digest(),proposed_netlist_sha256=candidate.comp.digest,
        retained_initial_unused_input_failure_sha256=digest(out/'SP29_protected_scratch_initial_unused_H2_input_failure.json'),
        retained_initial_unused_input_source_sha256=digest(out/'SP29_protected_scratch_initial_unused_H2_input_checker.py.txt'),
        receipt_dependencies_sha256={name:digest(out/name) for name in deps},seconds=time.monotonic()-begin)
    (out/'SP29_protected_scratch_certificate.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({key:receipt[key] for key in ('protected_scratch_seed_count',
        'second_left_fresh_H2_constant_output_equalities','protected_prefix_suffix_h2_77_zero_proved',
        'third_foreign_MF509_one_colonies','third_foreign_inside_zero_capture_routes',
        'third_foreign_strip_cleared_capture_routes','seconds','global_reliability_established')}),flush=True)


if __name__=='__main__':main()
