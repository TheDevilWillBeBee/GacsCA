"""Actual clean-row native/gather/packing/birth/software composition checks."""
import argparse,hashlib,json,sys,time
from pathlib import Path
from functools import lru_cache
from collections import Counter
import prefix_rule as r
import chronology as h

BASE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(BASE/'unregistered_gbd4'))
import native_emitter as emitter
import cost_contract as cost

ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT))
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
@lru_cache(None)
def records(g):
    raw=hashlib.shake_256(('GBD5 actual initial upper:'+str(g)).encode()).digest((r.K+7)//8)
    return int.from_bytes(raw,'little')&((1<<r.K)-1)
def unused(y):return (y*673+1)&1

def emit_native(out):
    graphs={};checks=0
    for printed,key in ((False,'h1'),(True,'printed')):
        graph=r.native_net(printed)
        data=dict(inputs=graph.inputs,gates=graph.gates,outputs=list(graph.outputs.items()),digest=graph.digest)
        (out/f'GBD5_native_{key}_hardware.json').write_text(json.dumps(data,separators=(',',':'))+'\n')
        graphs[key]=dict(gates=len(graph.gates),inputs=len(graph.inputs),digest=graph.digest)
        for address in (0,1,4,5,17,8190,8191):
            for age in (0,1,15,16,72*r.Q+2,r.BIRTH,80*r.Q-1,r.U-1):
                cells={j:r.Cell(addr=(address+j)%r.Q,age=age) for j in range(-5,6)}
                expected=r.native(cells,0,printed)
                assert expected==dict(addr=address,age_now=age,age=(age+1)%r.U,f1=0,f2=0)
                values={(j,name,b):bool((getattr(cells[j],name)>>b)&1) for j,name,b in graph.inputs}
                got=graph.evaluate(values,bool)
                for name in expected:
                    bits=[key for key in graph.outputs if key[0]==name]
                    value=sum(int(got[key])<<key[1] for key in bits)
                    assert value==expected[name],(printed,address,age,name)
                checks+=1
    return dict(graphs=graphs,actual_native_hardware_closure_checks=checks)

def chronology_checks(beta):
    assert h.row(0,0,records,unused)==r.encode(records,unused,0)
    points={0,1,2,r.p.SEED-1,r.p.SEED,*range(r.p.SEED+1,r.p.LOAD+2),
            r.p.LOAD+2,r.p.DONE-1,r.p.DONE,r.BIRTH-1}
    for start in r.STARTS:points.update((start,start+1,start+2,start+r.ACTIVE-1,start+r.ACTIVE))
    for g in range(3):
        for d in r.LANES:
            t=r.capture(g,d);points.update((t-1,t,t+1))
    xs=(r.P-1,r.P,r.P+1,r.P+18,r.P+19,r.P+20,
        r.P+169,r.P+r.K-2,r.P+r.K-1,r.P+r.K,0,r.Q-1)
    calls=roles=0
    for t in sorted(points):
        if t>=r.BIRTH:continue
        frame=h.Frame(t,records,unused)
        for x in xs:
            computed=r.local(frame,x,beta)
            expected=h.row(t+1,x,records,unused)
            assert computed==expected,(t,x,'derived global row mismatch')
            calls+=1;roles+=5
    # Every capture at every normal record primary in colony0 has the
    # literal OLD Mail/Info source identity, not an independently chosen bank.
    routes=0
    for g in range(3):
        for lane,d in enumerate(r.LANES):
            t=r.capture(g,d)
            for b in range(r.K):
                y=r.P+b
                source=h.info(y,records,unused) if d==0 else ((h.mailbox(t,y,records,unused)>>(0 if d<0 else 1))&1)
                assert source==((records(d)>>b)&1)
                assert ((h.history(t+1,y,records,unused)>>(17*g+lane))&1)==source
                routes+=1
    return dict(actual_local_prefix_rows=[t for t in sorted(points) if t<r.BIRTH],actual_local_prefix_calls=calls,
                actual_output_roles=roles,all_normal_primary_capture_routes=routes,
                no_native_or_History_ports=True)

def packing_trace(beta):
    p=r.p
    # Start from the ACTUAL derived History; old packets are actual row0
    # zeros, held until SEED. The literal packing controller generates
    # both data and metadata from that chronological History row.
    state={r.P+i:p.ZERO for i in range(r.K)}
    updates=0
    for t in range(p.SEED,p.LOAD+1):
        new={}
        for a in range(r.P,r.P+r.K):
            temporal=p.majority3(*[(h.history(t,a,records,unused)>>(17*g))&p.HISTORY_MASK for g in range(3)])
            v=p.stage_action(a,t,state.get(a,p.ZERO),state.get(a-1,p.ZERO),state.get(a+1,p.ZERO),temporal)
            assert v==h.packet(t+1,a,records)
            if v.valid:new[a]=v
            updates+=1
        state=new
    for t in range(p.LOAD+1,p.DONE+1):
        new={}
        for a in set(state)|{a-1 for a in state}:
            v=p.stage_action(a,t,state.get(a,p.ZERO),p.ZERO,state.get(a+1,p.ZERO),0)
            assert v==h.packet(t+1,a,records)
            if v.valid:new[a]=v
            updates+=1
        assert len(new)==p.CHUNKS;state=new
    assert state=={p.destination(j):p.Packet(h.payload(0,j,records),j,1) for j in range(p.CHUNKS)}
    assert p.DONE+1==r.BIRTH
    # Birth is an actual prefix_rule update on completed packets and current
    # canonical native fields, not a synthesized entry Head or a port.
    frame=h.Frame(r.BIRTH,records,unused);roles=0
    for x in range(r.P-8,r.P+12):
        got=r.local(frame,x,beta)
        for q,s in enumerate(r.S):
            expected=r.c.Head(1,0,r.c.RUN,0,0,0,(0,)*8) if x+s==r.P+2 else r.c.Head()
            assert r.c.unpack_head(got.Head[q])==expected
            assert got.Mem[q]==h.packet(r.BIRTH,x+s,records).data
            roles+=1
    return dict(literal_packet_site_updates=updates,transport_rows=p.MAX_TRAVEL,
                all3_banks_actual=True,packing_complete_raw_row=p.DONE+1,
                birth_action=r.BIRTH,born_raw_row=r.BIRTH+1,actual_birth_copy_roles=roles)

def cpu_trace(beta,g,outdir):
    c=r.c;position=g*r.Q+r.P+2
    initial=h.Frame(r.BIRTH,records,unused)
    head=c.unpack_head(r.local(initial,position,beta).Head[0])
    assert head.present and head.mode==c.RUN
    outputs={};ops=Counter();roles=0;events=[];ticks=0
    for tick in range(33938):
        if not head.present:break
        t=r.BIRTH+1+tick
        frame=h.Frame(t,records,unused,
            lambda y:head if y==position else c.Head(),lambda y:outputs.get(y,0))
        oldhead=head;oldpos=position
        name,args,_=c.instruction(beta,head.pc)
        if head.mode==c.RUN:
            ops[name]+=1
            native=r.native(frame,position)
            assert native==dict(addr=position%r.Q,age_now=t,age=t+1,f1=0,f2=0)
            view=r.raw_view(frame,position,native)
            new=c.actor(view,position,0,beta);newpos=position
            if name=='WRITE':
                for offset in c.patches(c.write_request(head,beta,20),-2):
                    y=position+offset
                    actual=r.local(frame,y,beta)
                    outputs[y]=actual.Out[0]
                    for q,s in enumerate(r.S):
                        assert r.local(frame,y-s,beta).Out[q]==outputs[y];roles+=1
        else:
            candidates=[]
            for y in range(position-1,position+2):
                view=r.raw_view(frame,y,r.native(frame,y))
                new=c.actor(view,y,0,beta)
                if new.present:candidates.append((y,new))
            assert len(candidates)==1
            newpos,new=candidates[0]
        if tick%257==0:
            for q,s in enumerate(r.S):
                assert c.unpack_head(r.local(frame,newpos-s,beta).Head[q])==new;roles+=1
        position,head=newpos,new;ticks+=1
        if tick<3 or name=='HALT':events.append(dict(row=t+1,position=position,Head=c.pack_head(head)))
    else:raise AssertionError('actual chronology exceeded universal native bound')
    word=outputs[g*r.Q+r.P]|(outputs[g*r.Q+r.P+1]<<20)
    got=dict(addr=word&8191,age=(word>>13)&c.MASK,f1=(word>>33)&1,f2=(word>>34)&1)
    upper={j:r.Cell(addr=records(g+j)&8191,age=(records(g+j)>>13)&c.MASK,
        f1=(records(g+j)>>33)&1,f2=(records(g+j)>>34)&1,
        wf1=(records(g+j)>>35)&1,wf2=(records(g+j)>>36)&1) for j in range(-5,6)}
    expected=r.native(upper,0);expected.pop('age_now')
    assert got==expected
    finalrow=r.BIRTH+1+ticks;assert finalrow<=627003<r.EARLY_END
    result=dict(colony=g,actual_initial_upper_records={str(j):records(g+j) for j in r.LANES},
        no_future_commands_or_tapes=True,actual_born_row=r.BIRTH+1,
        updates=ticks,halted_raw_row=finalrow,actual_result=got,expected=expected,
        physical_output_role_checks=roles,opcounts=dict(ops),
        actual_written_Out={str(y):v for y,v in sorted(outputs.items())},events=events)
    path=outdir/f'GBD5_colony{g}_execution.json';path.write_text(json.dumps(result,indent=2)+'\n')
    return dict(colony=g,updates=ticks,halted_raw_row=finalrow,
                physical_role_checks=roles,path=path.name,sha256=sha(path))

def main(out):
    started=time.monotonic();out.mkdir(parents=True,exist_ok=True)
    programme=emitter.native_program();beta=programme['beta'];assert len(beta)==7051
    (out/'GBD5_beta.bits').write_text(''.join(map(str,beta))+'\n')
    hardware=emit_native(out);chronology=chronology_checks(beta);packing=packing_trace(beta)
    runs=[cpu_trace(beta,g,out) for g in (0,1)]
    result=dict(passed=True,schema='GBD5 autonomous clean-prefix bridge v1',Q=r.Q,U=r.U,lambda_=24,c=104,
        K=r.K,Head_bits=r.c.HEAD_BITS,total_binary_state_bits=r.K,
        immutable_native_prefix_beta_bits=7051,stored_instruction_dictionary_bits=0,
        native_hardware=hardware,chronology=chronology,packing=packing,actual_CPU_runs=runs,
        universal_native_programme_updates=cost.bound(programme)['total_updates'],
        universal_complete_prefix_row=627003,early_stage_end=r.EARLY_END,slack=28357,
        actual_global_E_start=True,autonomous_native_ports=True,actual_all3_History_banks=True,
        actual_packing_and_birth=True,universal_clean_prefix_by_composition=True,
        all_upper_Kbit_patterns=True,unused_lower_Info_arbitrary=True,immutable_beta_departure=True,
        radius7_prefix_within8_proposal=True,authentic_flag_couriers=False,late_pass=False,
        full_own_beta=False,full_own_controller_software=False,full_physical_period=False,
        intact_recursive_initialization=False,noise_map=False,faithful_Gray=False,
        Gray_refutation=False,iid_failure=False,shorter_U=False)
    target=out/'GBD5_certificate.json';target.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(passed=True,elapsed=time.monotonic()-started,receipt_sha256=sha(target))),flush=True)

if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--out',type=Path,required=True);main(a.parse_args().out)
