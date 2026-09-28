"""Exact boundary-family proof with independent arbitrary neighbor payloads.

All 2^30 Ages, independent neighboring Data words, and independent low Signal
bits are covered. Other raw fields have the flagged cap values. Capture creates
a one-tick low Signal bit from Data; omitting it was a failed first conjecture. This is not a general damaged-state or
noise-robustness theorem.
"""
import argparse,hashlib,json,time
from pathlib import Path
from gacsca.fixed_rule.word_bdd import BDD
from gacsca.fixed_rule import repair_b_rule as f,repair_b_projected as r,repair_b_initial as initial


def prove():
    age_bits=dict(f.SCHEMA)['age'];b=BDD(age_bits+11*65)
    age=tuple(b.variable(i) for i in range(age_bits))+(0,)*(64-age_bits)
    cap=r.lift(initial.terminal_data()[0]);payloads=[];inputs=[]
    for neighbor in range(11):
        data=tuple(b.variable(age_bits+64*neighbor+i) for i in range(64));payloads.append(data)
        signal=(b.variable(age_bits+11*64+neighbor),)+(0,)*63
        inputs.extend(age if name=='age' else data if name=='data' else signal if name=='signal' else b.const(getattr(cap,name)) for name,_ in f.SCHEMA)
    actual=b.evaluate(f.self_description(),inputs)
    reset=0
    for value in f.RESET_AGES:reset=b.or_(reset,b.arithmetic(4,age,b.const(value))[0])
    next_age=b.add(age,b.const(1))[:age_bits]+(0,)*(64-age_bits)
    next_data=tuple(b.and_(b.inv(reset),bit) for bit in payloads[5])
    capture=b.arithmetic(4,age,b.const(f.CAPTURE_AGE-1))[0]
    next_signal=(b.and_(capture,payloads[5][0]),)+(0,)*63
    expected=tuple(next_age if name=='age' else next_data if name=='data' else next_signal if name=='signal' else b.const(getattr(cap,name)) for name,_ in f.SCHEMA)
    for (name,_),got,want in zip(f.SCHEMA,actual,expected):
        for bit,(a,c) in enumerate(zip(got,want)):
            if a!=c:raise AssertionError((name,bit,b.witness(b.xor(a,c))))
    gaps=[y-x for x,y in zip(f.RESET_AGES,(*f.RESET_AGES[1:],f.U))]
    return dict(passed=True,symbolic_input_bits=b.variables,all_ages=f.U,independent_neighbor_Data_words=11,BDD_nodes=len(b.nodes),descriptor_sha256=f.self_description().digest(),payload_transition='zero when old Age is a reset age, otherwise retain own Data; no dependence on neighbor payload',signal_transition='own Data low bit at computed capture Age, otherwise zero',maximum_payload_reset_delay=max(gaps),limitation='only the flagged, synchronized boundary family; arbitrary structure, higher Signal bits, head or packet faults are outside this proof')

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',required=True,type=Path);a=parser.parse_args();assert not a.output.exists()
    started=time.monotonic();result=prove();result['seconds']=time.monotonic()-started;result['verifier_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest();a.output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
