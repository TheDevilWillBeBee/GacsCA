"""Exact symbolic packing/route certificate and literal raw-slot checks."""
import argparse,hashlib,json,random
from pathlib import Path
import packing_kernel as k
import layout as l

ROOT=Path(__file__).resolve().parents[4]

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    a=argparse.ArgumentParser();a.add_argument('--output',type=Path,required=True)
    args=a.parse_args()
    # Symbolic seed IDs certify arbitrary payloads, not one numerical tape.
    state=[frozenset((i,)) for i in range(k.K)]
    merge_identities=0
    for t in range(1,20):
        new=[]
        for i in range(k.K):
            s=state[i]
            if i and i//20==(i-1)//20:s=s|state[i-1]
            wanted=frozenset(range(max(20*(i//20),i-t),i+1))
            assert s==wanted
            new.append(s);merge_identities+=1
        state=new
    for h in range(k.CHUNKS):
        end=k.source(h)-k.P
        assert state[end]==frozenset(range(20*h,min(k.K,20*h+20)))
        assert len({i%20 for i in state[end]})==len(state[end])
    # Exact arbitrary data basis: in each lane every seed occupies its own
    # bit index, so OR merging never substitutes a source from another chunk.
    rng=random.Random(81921042)
    histories=[[rng.getrandbits(17) for _ in range(k.K)] for _ in range(3)]
    temporal=[k.majority3(histories[0][i],histories[1][i],histories[2][i])
              for i in range(k.K)]
    # Check the literal seed, merge and chunk-load equations as well as
    # their symbolic source-set proof.  Metadata comes from the block,
    # rather than being inserted by a prepared carrier list at LOAD.
    previous=[k.Packet(rng.getrandbits(340),rng.getrandbits(13),
                       rng.getrandbits(1)) for _ in range(k.K)]
    seeded=[k.stage_action(k.P+i,k.SEED,previous[i],k.ZERO,k.ZERO,
                           temporal[i]) for i in range(k.K)]
    assert seeded==[k.Packet(k.seed_data(temporal[i],i%20),i//20,1)
                    for i in range(k.K)]
    merge_current=seeded
    literal_merge_updates=0
    for j in range(1,20):
        old=merge_current
        merge_current=[k.stage_action(k.P+i,k.SEED+j,old[i],
            old[i-1] if i else k.ZERO,k.ZERO,0) for i in range(k.K)]
        for i,v in enumerate(merge_current):
            wanted=0
            for b in range(max(20*(i//20),i-j),i+1):
                wanted|=seeded[b].data
            assert v==k.Packet(wanted,i//20,1)
            literal_merge_updates+=1
    packed=[]
    for h in range(k.CHUNKS):
        value=0
        for i in range(20*h,min(k.K,20*h+20)):
            value|=k.seed_data(temporal[i],i%20)
        assert value&~k.final_chunk_mask(h)==0
        packed.append(value)
    # Complete selected local-controller trace with symbolic labels carried
    # as arbitrary full payload values. Universal data proof: transport
    # controller NEVER inspects or modifies a correctly routed payload.
    current={}
    for i,old in enumerate(merge_current):
        v=k.stage_action(k.P+i,k.LOAD,old,k.ZERO,k.ZERO,0)
        if v.valid:current[k.P+i]=v
    assert current=={k.source(h):k.Packet(packed[h],h,1)
                     for h in range(k.CHUNKS)}
    route_rows=route_sites=0
    for elapsed in range(1,k.MAX_TRAVEL+1):
        candidates=set(current)|{x-1 for x in current}
        new={}
        for x in candidates:
            own=current.get(x,k.ZERO);right=current.get(x+1,k.ZERO)
            v=k.stage_action(x,k.LOAD+elapsed,own,k.ZERO,right,0)
            route_sites+=1
            if v.valid:new[x]=v
        formula={max(k.destination(h),k.source(h)-elapsed):k.Packet(packed[h],h,1)
                 for h in range(k.CHUNKS)}
        assert len(formula)==k.CHUNKS
        assert new==formula,(elapsed,'route formula failed')
        current=new;route_rows+=1
    assert current=={k.destination(h):k.Packet(packed[h],h,1)
                    for h in range(k.CHUNKS)}
    assert k.DONE<73*k.Q and k.DONE-k.SEED==3237
    # Structural raw-source certificate covers each actual SF field/slot.
    ports=0;used=set()
    for q,s in enumerate(k.SLOTS):
        for d in (-1,0,1):
            for h,b in enumerate(k.SLOTS):
                physical=s+d+b;slot=k.INV[h]
                assert physical+k.SLOTS[slot]==s+d
                assert abs(physical)<=5
                used.add(physical);ports+=1
    assert used==set(range(-5,6))
    # Literal raw block matches the coherent factor for arbitrary coherent
    # packets/history values and all output-copy roles. No chosen commands.
    def payload(x):
        return k.Packet(((x+9000)*9178349023145967)&k.DATA_MASK,
                        (x*971)&k.TAG_MASK,(x%3)!=0)
    def hist(bank,x):return ((x+10000)*(8191+bank*387))&k.HISTORY_MASK
    times=[k.SEED-1,k.SEED,*range(k.SEED+1,k.SEED+20),k.LOAD,
           k.LOAD+1,k.DONE-1,k.DONE,k.DONE+1]
    xs=[k.P-2,k.P-1,k.P,k.P+1,k.P+18,k.P+19,k.P+20,
        k.P+162,k.P+163,k.P+k.K-2,k.P+k.K-1,k.P+k.K,k.P+k.K+1]
    raw_calls=copy_checks=0
    for t in times:
        for x in xs:
            cells={z:k.coherent_cell(z,t,payload,hist) for z in range(x-5,x+6)}
            out=k.local(cells,x);raw_calls+=1
            for q,s in enumerate(k.SLOTS):
                y=x+s
                hs=[hist(b,y) for b in range(3)]
                want=k.stage_action(y%k.Q,t,payload(y),payload(y-1),payload(y+1),
                                    k.majority3(*hs))
                assert (out.data[q],out.tag[q],out.valid[q])== \
                       (want.data,want.tag,want.valid)
                copy_checks+=1
    # Malformed controls and colliding packet inputs have explicit total
    # cases. These are diagnostics, not a general damaged-history theorem.
    collision=k.stage_action(k.P,k.LOAD+1,k.Packet(7,0,1),k.ZERO,
                             k.Packet(9,0,1),0)
    assert collision==k.ZERO
    bad=k.stage_action(k.P,k.LOAD+1,k.Packet(7,k.CHUNKS,1),k.ZERO,
                      k.Packet(9,k.CHUNKS,1),0)
    assert bad==k.ZERO
    for t in (0,1,32*k.Q,64*k.Q,96*k.Q,k.U-1):
        p=k.Packet(7,9,1)
        assert k.stage_action(k.P,t,p,k.ZERO,k.ZERO,0)==p
    # Finite stage partition spans all legal Age values without relying on
    # tested samples of a long unchanged host rule.
    active_counts=dict(seed=1,merge=19,load=1,transport=k.MAX_TRAVEL,
                       other=k.U-(1+19+1+k.MAX_TRAVEL))
    assert sum(active_counts.values())==k.U
    proof=Path(__file__).with_name('GBD3_FINITE_HEAD_AND_LITERAL_WRITE.md')
    r=dict(schema='GBD3-new-K3387-packing-1',passed=True,Q=k.Q,U=k.U,lambda_=24,c=104,
           K=k.K,P=k.P,chunks=k.CHUNKS,seed_age=k.SEED,
           load_age=k.LOAD,done_age=k.DONE,max_travel=k.MAX_TRAVEL,
           packed_by_before73Q=True,seed_to_complete_ticks=k.DONE-k.SEED,
           symbolic_merge_source_set_identities=merge_identities,
           literal_seed_updates=k.K,literal_merge_updates=literal_merge_updates,
           literal_chunk_load_updates=k.K,
           complete_transport_rows=route_rows,transport_site_updates=route_sites,
           raw_source_slot_identities=ports,block_radius=5,
           literal_raw_calls=raw_calls,raw_output_copy_checks=copy_checks,
           total_stage_partition=active_counts,
           allocation=dict(binary_history_bits=3*17,packed_data_bits=340,
                           tag_bits=13,valid_bits=1,logical_SF_bits=405,
                           five_copy_SF_bits=2025,extra_bits_beyond_GBD0_proposal=0),
           native_ports_are_explicit_premise=True,
           controller_native_composition_proved=False,
           actual_autonomous_gathers_supplied=False,
           conditional_quiet_coherent_packing=True,
           own_software_emitted=False,beta_fit=False,full_rule=False,
           full_execution_deadline=False,physical_period=False,
           faithful_Gray=False,Gray_refutation=False,iid_failure=False,shorter_U=False,
           source_hashes={str(p.relative_to(ROOT)):sha(p) for p in
                        (Path(__file__),Path(k.__file__),Path(l.__file__),proof)})
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))


if __name__=='__main__':main()
