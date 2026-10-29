"""Exact GBD6 encoding rejection, issued M/H component and scatter checks.

Expected native/controller values belong to the CHECKER, not any opcode.
The standalone execution has explicit prepared-bank/native-result premises.
No full concatenated beta or full-period theorem is asserted.
"""
import argparse,hashlib,json,sys,time
from pathlib import Path
from dataclasses import replace
from collections import Counter
import full_rule_family as f
import controller_emitter as e
import component_cost
BASE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(BASE/'unregistered_gbd4'))
import execution
r=f.r;c=e.c;l=e.l

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def raw_record(seed,j):
    return int.from_bytes(hashlib.shake_256(f'GBD6:{seed}:{j}'.encode()).digest((l.K+7)//8),'little')&((1<<l.K)-1)
def record_cell(z):
    native={name:((z>>l.NATIVE_OFFSETS[name])&((1<<width)-1)) for name,width in l.NATIVE}
    sf={name:tuple(sum(((z>>(l.SF_OFFSETS[name]+5*b+q))&1)<<b for b in range(width))
                  for q in range(5)) for name,width in l.SF}
    return r.Cell(native['GF'],native['Age'],native['Flag1'],native['Flag2'],native['WF1'],native['WF2'],**sf)
def records(seed,age,flag=0):
    result={j:raw_record(seed,j) for j in range(-8,9)}
    for j,z in result.items():
        result[j]=(z>>37)<<37|((200+j)%r.Q)|(age<<13)|(flag<<33)
    return result

def emission(out):
    results={}
    for printed,name in ((False,'h1'),(True,'printed')):
        p=e.programme(printed);s=e.standalone(printed)
        assert p['beta'] is None and p['bits']>c.Q and p['invalid_targets']
        listing=dict(rows=p['rows'],labels=p['labels'],positions=p['positions'],
            bits=p['bits'],invalid_targets=p['invalid_targets'],beta_issued=False,
            scratch_Out_positions=p['scratch_Out_positions'],omitted_full_own_fields=p['omitted_full_own_fields'])
        path=out/f'GBD6_{name}_rejected_listing.json';path.write_text(json.dumps(listing,indent=2)+'\n')
        component=out/f'GBD6_{name}_controller.bits';component.write_text(''.join(map(str,s['beta']))+'\n')
        results[name]=dict(total_bits=p['bits'],instructions=len(p['rows']),
            native_prefix_bits=p['native_prefix_bits'],additional_controller_bits=p['new_controller_bits'],
            out_of_Q_references=len(p['invalid_targets']),standalone_component_bits=s['bits'],
            standalone_instructions=len(s['rows']),standalone_invalid_targets=len(s['invalid_targets']),
            rejected_listing_sha256=sha(path),component_sha256=sha(component))
    assert results['h1']['total_bits']==12653 and results['printed']['total_bits']==12708
    return results

def component_runs(out):
    programme=e.standalone();cases=[]
    phases=(0,1,2,r.Q+2,8*r.Q+2,16*r.Q,32*r.Q,32*r.Q+1,64*r.Q+3*r.Q+2,72*r.Q+2,96*r.Q,r.U-1)
    recipes=[dict(age=age,variant='canonical') for age in phases]
    recipes.extend((dict(age=72*r.Q+2,variant='GFkeep_zero'),dict(age=32*r.Q+1,variant='missing_GF_quorum')))
    for index,recipe in enumerate(recipes):
        age=recipe['age'];bank=records(index,age,int(index in (2,9)))
        if recipe['variant']=='GFkeep_zero':bank[0]=(bank[0]&~(r.Q-1))|201
        elif recipe['variant']=='missing_GF_quorum':
            for j in bank:bank[j]=(bank[j]&~(r.Q-1))|((200+17*j)%r.Q)
        cells={j:record_cell(z) for j,z in bank.items()};native=r.native(cells,0)
        expected=f.local(cells,0,programme['beta'])
        regs=(0,0,0,native['addr'],native['age'],0,0,0)
        initial_out={e.n.RAM_BASE+e.n.RAM['F1']:native['f1']}
        run=execution.run(programme,bank,initial_regs=regs,initial_out=initial_out,
            limit=100000,physical_every=503)
        outputs={int(k):v for k,v in run['final_outputs'].items()}
        word=lambda b:(outputs.get(l.P+b//20,0)>>(b%20))&1
        for name,width in (('Mailbox',4),('History',51)):
            for q in range(5):
                got=sum(word(l.sf_bit(name,b,q))<<b for b in range(width))
                assert got==getattr(expected,name)[q],(index,age,name,q,got,getattr(expected,name)[q])
        path=out/f'GBD6_controller_case{index:02d}.json'
        data=dict(case=index,recipe=recipe,raw_upper_records={str(j):z for j,z in bank.items()},
            actual_native_result=native,declared_native_ABI_regs=list(regs),
            declared_native_RAM_F1=initial_out,expected_Mailbox=list(expected.Mailbox),
            expected_History=list(expected.History),literal_component_run=run,
            native_result_ABI_prepared=True,actual_complete_own_execution=False)
        path.write_text(json.dumps(data,indent=2)+'\n')
        cases.append(dict(case=index,age=age,updates=run['ticks'],
            Head_range=run['Head_range'],raw_role_checks=run['raw_role_checks'],sha256=sha(path)))
    return cases

def scatter(out):
    words={h:(h*379319+171177)&c.MASK for h in range(f.p.CHUNKS)}
    state={};updates=0;collisions=0
    for t in range(f.OLOAD,f.ODONE+1):
        sites=set(range(f.P,f.P+f.K)) if t==f.OLOAD else set(state)|{a+1 for a in state}
        new={}
        for a in sites:
            own=(f.p.Packet(words.get(a-f.P,0),0,0) if t==f.OLOAD else state.get(a,f.p.ZERO))
            value=f.out_packet(a,t,own,state.get(a-1,f.p.ZERO))
            if value.valid:new[a]=value
            updates+=1
        assert len(new)==f.p.CHUNKS
        state=new
    assert state=={f.p.source(h):f.p.Packet(words[h],h,1) for h in words}
    scratch={a:packet.data for a,packet in state.items()}
    for action in range(f.EXPAND+1,f.SPREAD_END+1):
        new={}
        for a in range(f.P,f.P+f.K):
            value=scratch.get(a,0)
            if (a-f.P)//20==(a+1-f.P)//20 and a+1<f.P+f.K:value|=scratch.get(a+1,0)
            if value:new[a]=value
        scratch=new
    for a in range(f.P,f.P+f.K):assert scratch.get(a,0)==words[(a-f.P)//20]
    # Literal raw-copy commit against the same previously derived Scratch.
    class Frame(dict):
        def __missing__(self,x):
            value=r.Cell(addr=x%r.Q,age=f.COMMIT,
                Scratch=tuple(scratch.get(x+s,0) for s in r.S))
            self[x]=value;return value
    frame=Frame();roles=0
    for x in range(f.P-2,f.P+f.K+2):
        new=f.local(frame,x,(0,))
        assert new.addr==x%r.Q and new.age==0
        for q,s in enumerate(r.S):
            y=x+s
            bit=((words[(y-f.P)//20]>>((y-f.P)%20))&1) if f.P<=y<f.P+f.K else 0
            assert new.Info[q]==bit
            for name in r.FIELD_WIDTHS:
                if name!='Info':assert getattr(new,name)[q]==0
            roles+=1
    return dict(conditional_quiet_native_and_completed_Out=True,actual_whole_period=False,
        seed_action=f.OLOAD,transport_updates=f.p.MAX_TRAVEL,
        packed_destination_row=f.ODONE+1,expansion_action=f.EXPAND,
        spread_finished_raw_row=f.SPREAD_END+1,commit_action=f.COMMIT,
        literal_packet_site_updates=updates,commit_copy_roles=roles,
        source_words=words,all_K_committed_bits=True)

def locality():
    # Independent executable access trace supplements the algebraic bounds.
    accesses=[];phases=(0,1,8194,65538,f.EARLY_BIRTH,f.EARLY_BIRTH+1,f.CSEED-1,f.CSEED,f.CSEED+1,80*r.Q,
        80*r.Q+1,96*r.Q,98*r.Q,f.LRESET,f.LBIRTH,f.LBIRTH+1,f.OLOAD,
        f.OLOAD+1,f.EXPAND,f.EXPAND+1,f.SPREAD_END,f.COMMIT)
    class Frame(dict):
        def __init__(self,phase,case):super().__init__();self.phase=phase;self.case=case;self.reads=[]
        def __getitem__(self,x):self.reads.append(x);return super().__getitem__(x)
        def __missing__(self,x):
            z=raw_record(self.case,x)
            value=replace(record_cell(z),addr=(200+x)%r.Q,age=self.phase,f1=0,f2=0,wf1=0,wf2=0)
            self[x]=value;return value
    for i,t in enumerate(phases):
        frame=Frame(t,i);new=f.local(frame,0,(0,))
        assert max(map(abs,frame.reads))<=7
        accesses.append(dict(phase=t,physical_offsets=sorted(set(frame.reads))))
    return dict(selected_all_raw_SF_access_cases=accesses,
        theoretical_native_radius=5,theoretical_packet_gather_radius=5,
        theoretical_raw_Head_radius=5,theoretical_READ_WRITE_radius=7,
        final_self_Info_Workspace_order=True,total_rule_radius_at_most=7)

def courier_delivery():
    """Literal clamped transport and source deadlines, without invented beta.

    Native Out readiness is the inherited actual-prefix composition. The
    exhaustive bit transport below verifies the new finite courier equation,
    not an execution of a missing complete own programme.
    """
    import itertools
    old=json.loads((Path(__file__).resolve().parents[4]/
        'figs/gray_counterexamples/unregistered_gbd5/attempt03/GBD5_certificate.json').read_text())
    latest=old['universal_complete_prefix_row'];assert latest==627003 and latest<f.CSEED
    distances=(r.Q-3-f.FLAG_SEED,f.FLAG_SEED-3)
    deadlines=[f.CSEED+2+d for d in distances]
    assert max(deadlines)<80*r.Q
    cases=[];updates=0
    # Every combination of the two delivered bits in three adjacent colonies.
    # No command may cross either clamped endpoint. This is a component check;
    # the theorem separately derives these bits from actual native Out.
    for values in itertools.product(range(4),repeat=3):
        commands=dict(zip((-1,0,1),values));state={};info={};arrivals={}
        last=f.CSEED+1+max(distances)
        for t in range(f.CSEED,last+1):
            sites={g*r.Q+f.FLAG_SEED for g in commands} if t==f.CSEED else (
                set(state)|{y-1 for y in state}|{y+1 for y in state})
            new={}
            for y in sites:
                g,a=divmod(y,r.Q);own=state.get(y,0)
                value=f.courier(a,t,own,state.get(y-1,0),state.get(y+1,0),
                    commands.get(g,0)<<13)
                if value:new[y]=value
                updates+=1
            for g,bits in commands.items():
                for index,a in enumerate((r.Q-3,3)):
                    y=g*r.Q+a
                    if t>f.CSEED:info[y]=(state.get(y,0)>>index)&1
                    if t+1>=deadlines[index]:assert info.get(y,0)==(bits>>index)&1
                    if y in new:assert (new[y]>>index)&1==(bits>>index)&1
            assert all(y//r.Q in commands for y in new),'neighbour command leaked'
            state=new
        cases.append(dict(commands=commands,final_sources=info))
    # All raw slot roles at seed, first arrival and held deadline are checked
    # against local(), with other SF arbitrary. These are local cofactors;
    # they do not substitute a prepared whole-state physical trajectory.
    role_checks=0
    for bits in range(4):
        for stage in ('seed','right','left','held'):
            t=f.CSEED if stage=='seed' else deadlines[0] if stage in ('right','held') else deadlines[1]
            source=f.FLAG_SEED if stage=='seed' else r.Q-3 if stage in ('right','held') else 3
            class Frame(dict):
                def __missing__(self,y):
                    value=r.Cell(addr=y%r.Q,age=t,
                        Out=tuple((bits<<13) if (y+s)%r.Q==f.FLAG_SEED else 0 for s in r.S),
                        Couriers=tuple(bits if (y+s)%r.Q in (f.FLAG_SEED,r.Q-3,3) else 0 for s in r.S))
                    self[y]=value;return value
            frame=Frame()
            for q,s in enumerate(r.S):
                x=source-s;new=f.local(frame,x,(0,))
                if stage=='seed':assert new.Couriers[q]==bits
                else:assert new.Info[q]==((bits>>(0 if source==r.Q-3 else 1))&1)
                role_checks+=1
    return dict(actual_native_only_clean_prefix_composition=True,
        complete_own_beta_execution=False,native_prefix_latest_row=latest,
        courier_seed_action=f.CSEED,seed_slack=f.CSEED-latest,
        explicit_75Q_to_78Q_seed_change=True,original_75Q_readiness_proved=False,
        source_distances=distances,source_correct_raw_rows=deadlines,
        source_deadline=80*r.Q,right_deadline_slack=80*r.Q-max(deadlines),
        exhaustive_adjacent_command_tuples=64,literal_courier_site_updates=updates,
        local_raw_copy_cofactors=role_checks,source_field_bits=(13,14),
        held_source_Info_through_raw_96Q=True,cases=cases,
        errors=False,no_future_command_tape=True,
        literal_courier_cofactors_are_not_a_full_state_replay=True)

def main(out):
    start=time.monotonic();out.mkdir(parents=True,exist_ok=True)
    emitted=emission(out);runs=component_runs(out);transport=scatter(out);sources=locality()
    couriers=courier_delivery()
    cost=component_cost.contract()
    for item in runs:
        case=json.loads((out/f"GBD6_controller_case{item['case']:02d}.json").read_text())
        n=case['actual_native_result']
        keep=int(n['addr']==(int(case['raw_upper_records']['0'])&(r.Q-1)))
        scalar=component_cost.run(e.standalone(),n['age_now'],n['f1'],keep)
        assert scalar['updates']==item['updates'],'zero-data control factor differs from physical replay'
    result=dict(passed=True,schema='GBD6 total rule family and specified encoder rejection v1',
        Q=r.Q,U=r.U,lambda_=24,c=104,K=r.K,Head_bits=204,
        total_rule_family=True,all_raw_branches_defined=True,emission=emitted,
        complete_native_Mailbox_History_component_only=True,selected_component_runs=runs,
        conditional_output_transport=transport,locality=sources,
        native_only_early_flag_delivery=couriers,
        universal_controller_cost=cost,
        complete_beta=False,beta_fit=False,complete_self_simulation=False,
        universal_whole_runtime=False,full_period=False,authentic_Gray_programme=False,
        intact_recursive_initialization=False,error_history=False,noise_map=False,
        Gray_refutation=False,iid_failure=False,shorter_U=False)
    target=out/'GBD6_certificate.json';target.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(passed=True,elapsed=time.monotonic()-start,certificate_sha256=sha(target))))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--out',required=True,type=Path)
    main(parser.parse_args().out)
