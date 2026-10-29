"""Read/replay actual-source native factor and two physical first-row events."""
from pathlib import Path
from dataclasses import replace,asdict
import hashlib,json,sys,time
sys.path.insert(0,str(Path(__file__).resolve().parent))
import search_gaw9_mixed_native as mixed
import search_gaw9_uniform_native as uniform
ROOT=mixed.ROOT;S=mixed.S;D=mixed.D;k=mixed.k;base=mixed.base;own=mixed.own

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def payload(recipe,complete=False):
    b=recipe['start'];support=set();rows=[];digest=hashlib.sha256()
    for j,(gf,age,flags) in enumerate(recipe['payload']):
        x=b+j;old=mixed.prior.held(x)
        new=replace(old,addr=gf,age=age,f1=flags&1,f2=(flags>>1)&1,wf1=(flags>>2)&1,wf2=(flags>>3)&1)
        assert old!=new
        support.add((x,mixed.T));ow=k.cell_words(old);nw=k.cell_words(new)
        row=[x,mixed.T,ow,nw];digest.update(json.dumps(row,separators=(',',':')).encode()+b'\n')
        rows.append(dict(x=x,t=mixed.T,old_native_words=ow[:6],replacement_native_words=nw[:6],
            unchanged_SF_recipe='actual frozen row96 words(x)[6:]',
            **(dict(old_words=[hex(w) for w in ow],replacement_words=[hex(w) for w in nw]) if complete else {})))
    cl=base.gray_errors.classify(support,support,Q=k.Q,U=k.U,sep=104,exact_limit=1)
    assert cl['level0']==0 and cl['level1'] and cl['extent']==(16,1)
    return dict(support=sorted(support),classification=cl,chronological_whole_cell_payloads=rows,
        chronological_full_words_sha256=digest.hexdigest())

def actual_event(recipe):
    b=recipe['start'];faults={}
    for j,(gf,age,flags) in enumerate(recipe['payload']):
        x=b+j;faults[x]=replace(mixed.prior.held(x),addr=gf,age=age,
            f1=flags&1,f2=(flags>>1)&1,wf1=(flags>>2)&1,wf2=(flags>>3)&1)
    def initial(x):return faults.get(x,mixed.prior.held(x))
    outputs={x:k.local_transition({d:initial(x+d) for d in range(-8,9)},own.ROM) for x in range(b-8,b+24)}
    cones=[dict(x=x,old_cone_words=[[d,[hex(w) for w in k.cell_words(initial(x+d))]] for d in range(-8,9)],
        actual_output_words=[hex(w) for w in k.cell_words(z)]) for x,z in outputs.items()]
    return outputs,dict(**payload(recipe,complete=True),actual_full_local_R_cones=cones)

def source_and_birth_events():
    p=next(y for y in range(k.PRIMARY_START,k.PRIMARY_START+k.FRAME_WORDS) if base.I(y)&1)
    b=p-13;alias=dict(start=b,payload=[[k.Q-16+j,mixed.T,0] for j in range(16)])
    outputs,source=actual_event(alias)
    assert all(outputs[b+j].wf1==1 for j in range(11,16))
    assert base.I(p)&1 and outputs[p].info[0]&1
    assert outputs[p].f1 and outputs[p].addr==k.Q-3
    assert outputs[p].addr==alias['payload'][13][0]
    assert not any(outputs[p].heads+outputs[p].out+outputs[p].courier_l+outputs[p].courier_r)
    source.update(actual_source_primary=p,actual_initial_I=base.I(p),computed_source_Info_lowbit=1,
        source_wipe_false=True,receivers=[b+j for j in range(11,16)],actual_reachable_WF1_nonzero=True,
        silent_Workspace_shortcut_invalid=True,operational_or_Gray_failure=False)
    b=k.PRIMARY_START-6;birth=dict(start=b,payload=[[(b+j+1)%k.Q,102*k.Q,0] for j in range(16)])
    assert not mixed.allowed_age(102*k.Q)
    outputs,head=actual_event(birth);logical=k.PRIMARY_START-1
    packet=k.pack(k.Packet(p=1,pc=0))
    holders=[]
    for h,s in enumerate(k.SLOTS):
        x=logical-s;z=outputs[x]
        assert z.heads[h]==packet and z.mem[h]==0
        assert z.age==102*k.Q+1 and (z.addr+s)%k.Q==k.PRIMARY_START
        assert not (z.f1 and z.addr!=birth['payload'][x-b][0])
        holders.append(dict(x=x,holder=h,slot_offset=s,Head=hex(z.heads[h]),Mem=hex(z.mem[h]),
            computed_native_words=k.cell_words(z)[:6],computed_service_Address=(z.addr+s)%k.Q))
    assert mixed.prior.prior.bank(logical)==0
    head.update(actual_shifted_logical_head=logical,actual_five_holders=holders,
        actual_late_birth_clock=102*k.Q+1,actual_intact_bank_at_head=0,
        birth_free_factor_hypothesis_violated=True,whole_period_or_Gray_failure=False,
        subsequent_execution_History_Out_or_decoder_proved=False)
    return dict(actual_alias_source=source,actual_shifted_birth=head)

def envelope(out,recipe):
    pts=[recipe['start']+j for j,p in enumerate(recipe['payload']) if p[0]!=(recipe['start']+j)%k.Q or p[1]!=mixed.T]
    assert pts
    lo=min([out['min_geometry_x']]+pts);hi=max([out['max_geometry_x']]+pts)
    cols=[lo//k.Q,hi//k.Q]
    assert cols[1]-cols[0]<=1
    return dict(entire_geometry_union_colony_indices=list(range(cols[0],cols[1]+1)),
        one_fixed_adjacent_colony_pair=[cols[0],cols[0]+1],
        geometry_quiet=out['first_geometry_quiet'],geometry_quiet_absorbing_proved=True,
        original_4Q_geometry_envelope_instance=True)

def main(write=True):
    start=time.monotonic();c=mixed.library();g=uniform.library();checks=mixed.cofactor_checks(c)
    assert mixed.cofactor_checks(g)==checks
    oldmixed=json.loads((D/'GAW9_mixed_native_search.json').read_text())
    olduniform=json.loads((D/'GAW9_uniform_native_search.json').read_text())
    assert checks==oldmixed['actual_factor_cofactor_checks']==olduniform['cofactor_checks']
    assert len(oldmixed['cases'])==20 and len(olduniform['cases'])==120
    cases=[];updates=0
    for family,recipes,stored,lib in (('mixed',mixed.cases(),oldmixed['cases'],c),
                                    ('uniform',uniform.cases(),olduniform['cases'],g)):
        for index,(recipe,old) in enumerate(zip(recipes,stored)):
            out=mixed.run(lib,recipe['start'],recipe['payload'])
            assert out['status']==0 and out['return_code']==0
            if family=='mixed':
                assert dict(recipe,case_index=index,**out)==old
            else:
                initial=[recipe['start']+j for j,p in enumerate(recipe['payload']) if p[0]!=(recipe['start']+j)%k.Q or p[1]!=mixed.T]
                out['entire_geometry_union_colony_hull']=[min([out['min_geometry_x']]+initial)//k.Q,max([out['max_geometry_x']]+initial)//k.Q]
                out['contained_in_one_fixed_adjacent_colony_pair']=True
                out['temporal_4Q_cover_possible_for_this_prefix']=True
                assert dict(recipe,case_index=index,**uniform.compact(dict(out)))==old
            assert 0<out['first_geometry_quiet']<=2736
            updates+=out['updates']
            cases.append(dict(family=family,case_index=index,recipe=recipe,**payload(recipe),**envelope(out,recipe),
                all_raw_native_Flags_U_or_History_decoder_relation_proved=False))
    events=source_and_birth_events()
    result=dict(name='GAW9 actual mixed native/Info factor and original-real1 geometry-envelope instances',
        Q=k.Q,U=k.U,error_lambda=24,error_separation=104,no_head_birth_horizon=mixed.LIMIT,
        admitted_legal_Age_count=k.U-2*mixed.LIMIT,full_legal_Age_count=k.U,
        actual_full_local_R_cofactors=checks,cases=cases,exact_updated_sites=updates,
        maximum_mixed_geometry_quiet=max(x['geometry_quiet'] for x in cases if x['family']=='mixed'),
        maximum_uniform_geometry_quiet=max(x['geometry_quiet'] for x in cases if x['family']=='uniform'),
        actual_source_and_birth_events=events,actual_H_same_shared_error_histories=True,
        future_Workspace_inputs_selected=False,all140_fixed_pair_4Q_geometry_instances=True,
        all_arbitrary_payloads_or_Flags_U_recovery_proved=False,
        birth_near_output_or_History_decoder_map_proved=False,Gray_G17_iid_or_shorter_U_conclusion=False,
        new_rule_created=False,active_rule_modified=False,registered_main_modified=False,
        elapsed_seconds=time.monotonic()-start)
    assert result['maximum_mixed_geometry_quiet']==6 and result['maximum_uniform_geometry_quiet']==2736
    p=D/'GAW9_native_factor_receipt.json'
    if write:p.write_text(json.dumps(result,indent=2)+'\n')
    else:
        old=json.loads(p.read_text());a=dict(result);a.pop('elapsed_seconds');old.pop('elapsed_seconds')
        assert json.loads(json.dumps(a))==old
    print(json.dumps(dict(passed=True,cases=len(cases),exact_updated_sites=updates,
        admitted_Age_count=result['admitted_legal_Age_count'],geometry_quiet_by=2736,
        actual_nonzero_WF_source=True,actual_shifted_five_copy_birth=True,
        operational_Gray_or_iid_counterexample=False,elapsed_seconds=time.monotonic()-start)),flush=True)
    return result

if __name__=='__main__':main()
