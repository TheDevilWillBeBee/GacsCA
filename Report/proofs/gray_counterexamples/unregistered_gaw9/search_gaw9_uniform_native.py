"""Flat-quorum mixed native faults: geometry-only actual-source query."""
from pathlib import Path
import ctypes,hashlib,json,random,sys,time
sys.path.insert(0,str(Path(__file__).resolve().parent))
import search_gaw9_mixed_native as mixed
k=mixed.k;S=mixed.S;D=mixed.D

def library():
    reference=mixed.library();c=ctypes.CDLL(str(D/'gaw9_geometry_query.so'))
    for name in ('gaw9_campaign','gaw9_cofactor'):
        getattr(c,name).argtypes=getattr(reference,name).argtypes
        getattr(c,name).restype=getattr(reference,name).restype
    return c

def cases():
    # Include near true boundaries and actual nonzero Programme-Info aliases.
    pb=k.PRIMARY_START+k.FIELD['program']
    starts=(0,k.Q-16,k.Q-8,k.PRIMARY_START,pb-3,-k.Q+k.PRIMARY_START)
    ages=(0,k.U-1,mixed.T,102*k.Q+1,112*k.Q,15,16,32*k.Q,64*k.Q,80*k.Q-1)
    assert all(mixed.allowed_age(a) for a in ages)
    result=[]
    for index in range(120):
        b=starts[index%len(starts)];age=ages[(index//len(starts))%len(ages)]
        mode=(index//12)%5;flags=(0,2,8,15)[(index//5)%4]
        payload=[]
        for j in range(16):
            if mode==0:gf=(b+j+1)%k.Q
            elif mode==1:gf=(b+j+k.Q//2)%k.Q
            elif mode==2:gf=j
            elif mode==3:gf=(k.Q-16+j)%k.Q
            else:gf=(j+(k.Q//2 if j>=8 else 0))%k.Q
            payload.append([gf,age,flags])
        result.append(dict(start=b,payload=payload,kind='uniform-Age-flat-GF',mode=mode,flags=flags))
    return result

def compact(out):
    events=out.pop('events');out['event_rows_sha256']=hashlib.sha256(json.dumps(events,separators=(',',':')).encode()).hexdigest()
    out['event_rows_count']=len(events)
    if out['status']==0:
        final=out.pop('final_native_Info_disagreement')
        out['final_native_Info_disagreement_sha256']=hashlib.sha256(json.dumps(final,separators=(',',':')).encode()).hexdigest()
        out['final_native_Info_disagreement_count']=len(final)
    return out

def main():
    start=time.monotonic();c=library();checks=mixed.cofactor_checks(c,count=4096)
    print(json.dumps(dict(actual_local_R_cofactors=checks,starting_flat_quorum_campaign=True)),flush=True)
    results=[]
    for index,recipe in enumerate(cases()):
        tick=time.monotonic();out=mixed.run(c,recipe['start'],recipe['payload'])
        if out['return_code']==-4:
            # A finite-domain guard is not an operational counterexample.
            out=mixed.run(c,recipe['start'],recipe['payload'],colonies=16)
        initial=[recipe['start']+j for j,p in enumerate(recipe['payload']) if p[0]!=(recipe['start']+j)%k.Q or p[1]!=mixed.T]
        mins=[out['min_geometry_x']]+initial;maxs=[out['max_geometry_x']]+initial
        out['entire_geometry_union_colony_hull']=[min(mins)//k.Q,max(maxs)//k.Q]
        out['contained_in_one_fixed_adjacent_colony_pair']=out['entire_geometry_union_colony_hull'][1]-out['entire_geometry_union_colony_hull'][0]<=1
        out['temporal_4Q_cover_possible_for_this_prefix']=out['status']==0 and out['first_geometry_quiet']<=mixed.LIMIT
        result=dict(recipe,case_index=index,**compact(out));results.append(result)
        print(json.dumps(dict(case=index,age=recipe['payload'][0][1],start=recipe['start'],mode=recipe['mode'],
            status=result['status'],geometry_quiet=result['first_geometry_quiet'],steps=result['steps'],
            union_colonies=result['entire_geometry_union_colony_hull'],
            fixed_pair=result['contained_in_one_fixed_adjacent_colony_pair'],
            elapsed_seconds=time.monotonic()-tick)),flush=True)
        data=dict(name='GAW9 flat-quorum actual native-Info original-real1 envelope search',Q=k.Q,U=k.U,
            error_lambda=24,error_separation=104,cofactor_checks=checks,cases=results,
            future_Workspace_externally_selected=False,actual_H_same_native_error_history=True,
            no_head_birth_horizon=mixed.LIMIT,geometry_quiet_is_absorbing_for_arbitrary_future_SF=True,
            whole_period_flags_History_decoder_or_Gray_conclusion_proved=False,
            written_factor_and_replay_pending=True,elapsed_seconds=time.monotonic()-start)
        (D/'GAW9_uniform_native_search.json').write_text(json.dumps(data,indent=2)+'\n')
    return data

if __name__=='__main__':main()
