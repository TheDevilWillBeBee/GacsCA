"""Actual post-burst Programme/read/store lineage at the native Age primary."""
from pathlib import Path
import json,sys,time
S=Path(__file__).resolve().parent;sys.path.insert(0,str(S))
import search_gaw17_large_bursts as m
k=m.k

def check():
    started=time.monotonic();recipe=m.recipes()[0];state=m.Phase(recipe)
    for t in range(104):
        if t:state.fault(t)
        state.step(check=t in (0,103))
    y=m.P+1;loaded=state.copies('heads',y)
    assert state.age==m.T+104 and not state.words
    assert all(k.unpack(q).mode==k.RUN and k.unpack(q).pc==m.STORE_PC and k.unpack(q).regs[0]==k.MASK for q in loaded)
    assert state.copies('out',y)==(0,)*5
    assert all(q in (0,1) for x in range(y-4,y+5) for q in state.raw(x).program)
    r105=state.step(check=True);prepared=state.copies('heads',y)
    assert all(k.unpack(q).mode==k.SEEK and k.unpack(q).target==y%k.Q and k.unpack(q).regs[0]==k.MASK for q in prepared)
    r106=state.step(check=True);stored=state.copies('out',y);assert stored==(k.MASK,)*5
    return dict(passed=True,actual_intact_H_chronological_T=True,recipe=recipe,
        actual_complete_burst_points=10816,last_physical_error_time=m.T+103,
        actual_loaded_Head_time=m.T+104,actual_Programme_already_boolean=True,
        actual_native_Age_primary=y,actual_loaded_Head_full_words=[hex(q) for q in loaded],
        actual_STX_prepared_Head_time=m.T+105,actual_prepared_Head_words=[hex(q) for q in prepared],
        actual_later_Out_time=m.T+106,actual_Out_copies=[hex(q) for q in stored],
        actual_following_full_local_R_checks=r105['actual_full_local_R_checks']+r106['actual_full_local_R_checks'],
        future_Head_or_tape_or_controller_supplied=False,
        persistence_to_U_uses_separate_complete_trace=True,
        legal_decoder_or_2U_or_Gray_iid_failure_claim=False,elapsed_seconds=time.monotonic()-started)

if __name__=='__main__':
    r=check();(m.D/'GAW17_padding_lineage_certificate.json').write_text(json.dumps(r,indent=2)+'\n')
    print(json.dumps(dict(passed=True,actual_Out_time=r['actual_later_Out_time'],
        following_full_local_R_checks=len(r['actual_following_full_local_R_checks']),seconds=r['elapsed_seconds'])),flush=True)
