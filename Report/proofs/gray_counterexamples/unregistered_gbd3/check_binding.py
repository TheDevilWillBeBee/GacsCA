"""Fresh K3387 literal History packing, birth and software execution.

Prepared History/native ports are assumptions, not assigned future tape.
The packet bank and the Head are produced by the emitted local components.
"""
import argparse,hashlib,json,random
from dataclasses import replace
from pathlib import Path
import controller as cpu
import layout as layout
import packing_kernel as p
import binding_kernel as binding
import check_controller as controller_checks

ROOT=Path(__file__).resolve().parents[4]
HERE=Path(__file__).resolve().parent


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def pack_records(records):
    rng=random.Random(991324)
    # Two actual good History banks and a wholly arbitrary third bank.
    temporal=[sum(((records[lane-8]>>i)&1)<<lane for lane in range(17))
              for i in range(p.K)]
    hist=[[rng.getrandbits(17) for _ in range(p.K)],temporal,temporal]
    old=[p.Packet(rng.getrandbits(340),rng.getrandbits(13),rng.getrandbits(1))
         for _ in range(p.K)]
    seeded=[p.stage_action(p.P+i,p.SEED,old[i],p.ZERO,p.ZERO,
                          p.majority3(*[h[i] for h in hist])) for i in range(p.K)]
    for t in range(1,20):
        old=seeded
        seeded=[p.stage_action(p.P+i,p.SEED+t,old[i],old[i-1] if i else p.ZERO,p.ZERO,0)
                for i in range(p.K)]
    current={}
    for i,packet in enumerate(seeded):
        new=p.stage_action(p.P+i,p.LOAD,packet,p.ZERO,p.ZERO,0)
        if new.valid:current[p.P+i]=new
    assert len(current)==p.CHUNKS
    for elapsed in range(1,p.MAX_TRAVEL+1):
        next_row={}
        for x in set(current)|{z-1 for z in current}:
            v=p.stage_action(x,p.LOAD+elapsed,current.get(x,p.ZERO),p.ZERO,
                             current.get(x+1,p.ZERO),0)
            if v.valid:next_row[x]=v
        current=next_row
    assert len(current)==170
    for h in range(p.CHUNKS):
        assert current[p.P+h]==p.Packet(layout.bank_container(records,h),h,1)
    return current,hist[0]


def main():
    a=argparse.ArgumentParser();a.add_argument('--output',type=Path,required=True)
    args=a.parse_args();rng=random.Random(3387819204)
    records={d:rng.getrandbits(layout.K) for d in range(-8,9)}
    packed,bad_history=pack_records(records)
    runs=[]
    for bit,slot in ((44,0),(44,4),(44+7*20,4)):
        runs.append(controller_checks.helper_program(records,'Head',bit,20,slot,
                    prepared_memory={x:v.data for x,v in packed.items()},birth_from_component=True))
    # Literal binding on free/incoherent raw Head/Mem/Out/History values:
    # outside reset/birth the two ordinary OLD-state equations compose;
    # reset/birth ignore every old forged Head. Native ports remain free.
    supplement_count=0
    beta=tuple(runs[0]['beta'])
    times=[0,p.SEED-1,p.SEED,p.LOAD,p.LOAD+1,p.DONE,binding.BIRTH,binding.BIRTH+1,p.U-1]
    for t in times:
        for addr in (0,p.P-1,p.P,p.P+2,p.P+169,p.Q-1):
            raw={x:binding.Cell(addr=(addr+x)&(p.Q-1),age=t,
                     history=tuple(tuple(rng.getrandbits(17) for _ in range(5)) for _ in range(3)),
                     data=tuple(rng.getrandbits(340) for _ in range(5)),
                     tag=tuple(rng.getrandbits(13) for _ in range(5)),
                     valid=tuple(rng.getrandbits(1) for _ in range(5)),
                     head=tuple(rng.getrandbits(204) for _ in range(5)),
                     out=tuple(rng.getrandbits(20) for _ in range(5))) for x in range(-8,9)}
            v=binding.local(raw,0,beta);pv=p.local(raw,0)
            assert (v.data,v.tag,v.valid)==(pv.data,pv.tag,pv.valid)
            if p.SEED<=t<=binding.BIRTH:
                want=tuple(cpu.pack_head(binding.head_birth((addr+s)&(p.Q-1))
                      if t==binding.BIRTH else cpu.Head()) for s in cpu.S)
                assert v.head==want
            else:
                view={x:cpu.Cell(c.addr,c.age,c.head,c.data,c.out) for x,c in raw.items()}
                cv=cpu.local(view,0,beta,-2,20)
                assert (v.head,v.out)==(cv.head,cv.out)
            supplement_count+=1
    proof=HERE/'GBD3_FINITE_HEAD_AND_LITERAL_WRITE.md'
    receipt=dict(schema='GBD3-K3387-history-packing-and-Head-binding-1',passed=True,
        Q=p.Q,U=p.U,lambda_=24,c=104,K=layout.K,twoK=2*layout.K,
        Head_bits=cpu.HEAD_BITS,chunks=p.CHUNKS,packing_source_constants_are_new=True,
        seed_computed_port_age=p.SEED,load_computed_port_age=p.LOAD,
        last_packing_computed_port_age=p.DONE,birth_computed_port_age=binding.BIRTH,
        first_execution_computed_port_age=binding.BIRTH+1,
        max_transport_rows=p.MAX_TRAVEL,packed_packets={str(x):vars(v) for x,v in packed.items()},
        arbitrary_third_history=bad_history,
        actual_upper_records={str(d):z for d,z in records.items()},
        actual_reset_birth_and_helper_runs=runs,total_raw_binding_supplements=supplement_count,
        component_radius=7,computed_native_ports_are_premise=True,
        three_History_banks_are_premise=True,actual_new_K_packing=True,
        literal_computed_port_reset_birth=True,conditional_software_binding=True,
        full_own_beta=False,beta_fit=False,full_rule=False,autonomous_gathers=False,
        physical_period=False,noise_map=False,faithful_Gray=False,Gray_refutation=False,
        iid_failure=False,shorter_U=False,
        source_hashes={str(path.relative_to(ROOT)):sha(path) for path in
        (Path(__file__),Path(p.__file__),Path(binding.__file__),Path(controller_checks.__file__),
         Path(cpu.__file__),Path(layout.__file__),HERE/'helpers.py',proof)})
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))


if __name__=='__main__':main()
