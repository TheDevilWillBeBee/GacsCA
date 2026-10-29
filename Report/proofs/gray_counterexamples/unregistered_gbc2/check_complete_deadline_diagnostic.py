"""Exact cutoff for the separate-code rejectedGBC2 compiler diagnostic.

It disproves an8Q bound for this specified prepared computation, not
U128Q by itself, aQ-bit own-rule period, Gray, or iid reliability.
"""
from dataclasses import asdict
from pathlib import Path
from hashlib import sha256
import argparse,json,time
import compact_completion_rule as b
import complete_branch_emitter as e
import check_complete_listing_extended as x
from check_complete_listing_diagnostic import make_machine


def run(output):
    t0=time.monotonic();r=e.emit_complete_structural_listing()
    name,cells,beta=next(c for c in x.selected() if c[0]=='five_simultaneous_PUSH20')
    cpu,identity=make_machine(r['listing']);encoded={j:b.encode_cell(c) for j,c in cells.items()}
    desired=b.encode_cell(b.total_rule(cells,beta))
    def tape(a):
        if not 0<=a<b.Q:return 0
        if not b.PRIMARY_START<=a<b.PRIMARY_START+b.FRAME_BITS:return 0
        return sum(encoded[j][a-b.PRIMARY_START]<<lane for lane,j in enumerate(b.LANES))
    p,position=b.Packet(p=1),b.PRIMARY_START;writes={};digest=sha256();cut=None
    cutoff=8*b.Q-2  # execution outputs112Q+2..120Q−1
    for tick in range(1,1000000):
        position+=1 if p.move==1 else -1 if p.move==2 else 0
        p,bit=cpu(p,position,{d:tape(position+d) for d in range(-4,5)},beta)
        assert p.mode!=b.ERROR,(tick,position,asdict(p))
        digest.update(json.dumps((tick,position,asdict(p),bit),sort_keys=True).encode())
        if bit is not None:writes[position]=bit
        if tick==cutoff:
            actual=tuple(writes.get(a,0) for a in range(b.PRIMARY_START,b.PRIMARY_START+b.FRAME_BITS))
            wrong=[i for i,(a,z) in enumerate(zip(actual,desired)) if a!=z]
            cut={'updates':tick,'physical_age':112*b.Q+1+tick,
                 'position':position,'packet':asdict(p),
                 'actual_bits':''.join(map(str,actual)),
                 'desired_bits':''.join(map(str,desired)),
                 'wrong_raw_bits':wrong,'written_columns':len(writes),
                 'trace_prefix_sha256':digest.hexdigest()}
        if p.mode==b.HALT:break
    else:raise AssertionError('diagnostic missed one-million cap')
    final=tuple(writes.get(a,0) for a in range(b.PRIMARY_START,b.PRIMARY_START+b.FRAME_BITS))
    wrong=[i for i,(a,z) in enumerate(zip(final,desired)) if a!=z]
    assert cut is not None and cut['wrong_raw_bits'] and not wrong and tick==126614
    out={'passed':True,'scope':'separate instruction-table/codesplit prepared8Q deadline counterexample',
         'Q':8192,'U':1048576,'lambda':24,'c':104,'physical_errors':[],
         'case':name,'input_cells':{str(j):asdict(c) for j,c in cells.items()},
         'target_beta_bits':''.join(map(str,beta)),
         'listing_bits':r['programme_bits'],'out_of_Q_references':len(r['invalid_references']),
         'diagnostic_identity':identity,'cutoff':cut,
         'full_completion_updates':tick,'final_wrong_raw_bits':wrong,
         'full_trace_sha256':digest.hexdigest(),
         'sources':{str(p):sha256(p.read_bytes()).hexdigest() for p in
                     (Path(__file__),Path(e.__file__),Path(b.__file__),Path(x.__file__))},
         'U128Q_impossible':False,'universal_full_deadline_proved':False,
         'whole_own_beta':False,'actual_Q_bit_period_failure':False,
         'intact_recursive_initialization':False,'gray_refutation':False,
         'iid_failure':False,'shorter_U_proved':False,
         'elapsed_seconds':time.monotonic()-t0}
    output.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:v for k,v in out.items() if k not in
          ('input_cells','target_beta_bits','cutoff')},indent=2))
    print(json.dumps({'cutoff':cutoff,'wrong_raw_count':len(cut['wrong_raw_bits']),
                      'first_wrong':cut['wrong_raw_bits'][0],'last_wrong':cut['wrong_raw_bits'][-1]},indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True)
    run(p.parse_args().output)
