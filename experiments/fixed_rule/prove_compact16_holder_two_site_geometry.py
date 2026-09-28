"""Exact complete-descriptor geometry repair under two arbitrary site defects.

All healthy Addresses and legal clocks are symbolic; both faulty geometry/flag/
primary-Wf records are independently symbolic across their full physical widths.
Unused raw fields are unrestricted after an explicit descriptor support check.
"""
import argparse,itertools,json,resource,time
from pathlib import Path
from gacsca.fixed_rule import compact16_holder_rule as f
from gacsca.fixed_rule.wordcode import Program,LIT,NAND,ADD,SHR,EQ,LT,MASK
from gacsca.fixed_rule.word_prune import prune
from gacsca.fixed_rule.word_bdd import BDD
from experiments.fixed_rule.run_compact16_holder_streamed_depth2 import sha

NAMES=('address','age','f1','f2')
ALLOWED=frozenset((*NAMES,'w2_wf1','w2_wf2'))


class BoundedBDD(BDD):
    def node(self,var,lo,hi):
        if len(self.nodes)>200000:raise MemoryError('diagnostic BDD node budget exhausted')
        return super().node(var,lo,hi)


def geometry(description):
    if description.inputs!=len(f.NEIGHBORHOOD)*f.FIELDS or len(description.outputs)!=f.FIELDS:raise ValueError('complete fixed raw rule required')
    for i,(op,a,b) in enumerate(description.operations):
        if op==LIT:
            if type(a) is not int or not 0<=a<=MASK:raise ValueError('bad literal')
        elif op not in (NAND,ADD,SHR,EQ,LT) or any(type(x) is not int or not 0<=x<description.inputs+i for x in (a,b)):raise ValueError('bad descriptor DAG')
    if any(type(x) is not int or not 0<=x<description.wires for x in description.outputs):raise ValueError('invalid descriptor output')
    program=prune(Program(description.inputs,description.operations,tuple(description.outputs[f.COL[name]] for name in NAMES)))
    used={wire for op,a,b in program.operations if op!=LIT for wire in (a,b) if wire<program.inputs}
    used.update(wire for wire in program.outputs if wire<program.inputs)
    support=tuple(sorted((wire//f.FIELDS-7,f.SCHEMA[wire%f.FIELDS][0]) for wire in used))
    if any(not -5<=offset<=5 or name not in ALLOWED for offset,name in support):raise ValueError('unexpected geometry dependency')
    return program,support


def prove_case(pair,description=None):
    pair=tuple(pair)
    if len(pair)!=2 or len(set(pair))!=2 or any(x not in range(-5,6) for x in pair):raise ValueError('two distinct local positions required')
    desc=f.self_description() if description is None else description;program,support=geometry(desc)
    address_width=dict(f.SCHEMA)['address'];clock_width=f.U.bit_length()-1;raw_clock_width=dict(f.SCHEMA)['age']
    canonical_width=f.Q.bit_length()-1
    assert f.Q==1<<canonical_width and canonical_width<=address_width and f.U==1<<clock_width
    labels=[]
    for bit in range(address_width):
        for record in ('healthy','bad0','bad1'):
            if record!='healthy' or bit<canonical_width:labels.append((record,'address',bit))
    for bit in range(raw_clock_width):
        for record in ('healthy','bad0','bad1'):
            if record!='healthy' or bit<clock_width:labels.append((record,'age',bit))
    for record in ('bad0','bad1'):
        for field in ('f1','f2','w2_wf1','w2_wf2'):labels.append((record,field,0))
    b=BoundedBDD(len(labels));variables={key:b.variable(i) for i,key in enumerate(labels)};zero=b.const(0)
    def word(record,field,width):return tuple(variables[(record,field,bit)] for bit in range(width))+(0,)*(64-width)
    address=word('healthy','address',canonical_width);age=word('healthy','age',clock_width)
    inputs=[]
    for offset in f.NEIGHBORHOOD:
        values={name:zero for name,_ in f.SCHEMA}
        values['address']=b.add(address,b.const(offset&MASK))[:canonical_width]+(0,)*(64-canonical_width);values['age']=age
        if offset in pair:
            record='bad'+str(pair.index(offset));values['address']=word(record,'address',address_width);values['age']=word(record,'age',raw_clock_width)
            for field in ('f1','f2','w2_wf1','w2_wf2'):values[field]=word(record,field,1)
        inputs.extend(values[name] for name,_ in f.SCHEMA)
    try:
        actual=b.evaluate(program,tuple(inputs));wanted=(address,b.add(age,b.const(1))[:clock_width]+(0,)*(64-clock_width),zero,zero)
        for name,got,expected in zip(NAMES,actual,wanted):
            for bit,(x,y) in enumerate(zip(got,expected)):
                if x!=y:
                    assignment=b.witness(b.xor(x,y));witness={}
                    for i,(record,field,j) in enumerate(labels):witness.setdefault(record,{}).setdefault(field,0);witness[record][field]|=((assignment>>i)&1)<<j
                    raise AssertionError(dict(pair=pair,field=name,bit=bit,witness=witness))
        return dict(passed=True,defect_positions=pair,independent_bits=len(labels),BDD_nodes=len(b.nodes),checked_raw_outputs=NAMES,operations=len(program.operations),descriptor_sha256=desc.digest(),support=support)
    finally:b.binary.cache_clear()


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True);parser.add_argument('--pair',nargs=2,type=int);args=parser.parse_args();out=Path(args.output)
    if out.exists():raise FileExistsError(out)
    started=time.perf_counter();pairs=[tuple(args.pair)] if args.pair is not None else list(itertools.combinations(range(-5,6),2));rows=[]
    for pair in pairs:
        row=prove_case(pair);rows.append(row);print(json.dumps(dict(pair=pair,BDD_nodes=row['BDD_nodes'],seconds=time.perf_counter()-started)),flush=True)
    result=dict(passed=True,complete_position_cover=args.pair is None,cases=rows,all_healthy_addresses=f.Q,all_healthy_ages=f.U,all_faulty_addresses=1<<dict(f.SCHEMA)['address'],all_faulty_ages=1<<dict(f.SCHEMA)['age'],all_faulty_geometry_flags_and_primary_Wf_independent=True,unused_raw_fields_unrestricted=True,descriptor_sha256=f.self_description().digest(),seconds=time.perf_counter()-started,host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,source_sha256={str(x):sha(x) for x in (Path(__file__),Path(f.__file__),Path('gacsca/fixed_rule/compact16_holder_description.py'),Path('gacsca/fixed_rule/word_bdd.py'))},theorem='In canonical Address/uniform legal Age geometry with zero healthy primary flags/Wf and at most two arbitrary physical site replacements, one complete F step restores canonical Address, increments the healthy Age modulo U and makes Flag1=Flag2=0. G has the same geometry. Every unused raw field is unrestricted by checked syntactic support.',limitation='Geometry sublemma only; complete two-tick controller/Signal/Wf recovery additionally requires coherence and structural transfer arguments. No arbitrary-phase noisy amplification theorem.')
    out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='cases'},indent=2),flush=True)

if __name__=='__main__':main()
