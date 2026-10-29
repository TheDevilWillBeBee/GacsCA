#!/usr/bin/env python3
"""Explore late programme sufficiency with unconstrained earlier workspace.

This is a scoped abstract suffix probe, not physical reachability or repair.
All sources/failed simplifications and finite Boolean evaluations are kept.
"""
from pathlib import Path
import hashlib
import json
import sys
import time
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from check_g17_schedule import Terms
import proposed_sparse_short_force1024 as proposed


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run(p,candidate,listing,mode,start_age):
    terms=Terms()
    regs=[[terms.var(('seed_reg',front,bit)) for bit in range(p.L)] for front in range(p.fronts)]
    scratch={};hold={};writes={};at={}
    sources=proposed.source_names(p)
    source_code={name:i for i,name in enumerate(sources)}
    bits=[(field,bit) for field,width in candidate.schema for bit in range(width)]
    where={bit:int(candidate.layout[i]) for i,bit in enumerate(bits)}
    table=proposed.dependency_table(p)
    byphase={row['address']:(row['field'],row['bit']) for row in table}
    offsets={(row['field'],row['bit']):row['offsets'] for row in table}
    live=set(candidate.comp.outputs.values())
    for _,a,b in candidate.comp.gates:live.update((a,b))
    for key,nid in candidate.comp.index.items():
        if key[0]!='x' or nid not in live:continue
        _,off,field,bit=key
        cell=where[field,bit]
        if off==0:code=source_code['info',0]
        else:
            lane=offsets[field,bit].index(off)
            code=source_code['ln',lane]
        if mode=='all_readonly_zero':value=0
        elif mode=='h2_77_readonly_zero':
            value=0 if (field,bit)==('h2',77) else terms.var(key)
        elif mode=='h2_mail_readonly_zero':
            value=0 if field in ('h2','mr','ml') else terms.var(key)
        elif mode=='four_h2_copies_and_mail_zero':
            zero=field in ('mr','ml') or (field=='h2' and bit in (13,77,205,269))
            value=0 if zero else terms.var(key)
        elif mode=='shifted_initial_private_zero':
            true=byphase.get((where[field,bit]+512)%p.Q)
            zero=true is None or true[0] not in ('addr','info')
            value=0 if zero else terms.var(key)
        elif mode=='native_inputs_zero':
            value=0 if field in ('addr','age','f1','f2','wf1','wf2','packet_valid','service_valid','backward_pressure') else terms.var(key)
        else:raise ValueError(mode)
        assert (cell,code) not in at
        at[cell,code]=value
    instructions=0;match_initialized=False
    for row in listing:
        seq,page,tick,front,cell,op,kind,a,b,dest,note=row
        age=p.E0+page*p.PL+tick
        if age<start_age:continue
        if not match_initialized and page>p.MP:
            # The actual Match result is left completely free. No fetch
            # correctness is assumed from a damaged earlier key.
            for bit in range(p.IW):regs[0][p.k+bit]=terms.var(('I',bit))
            match_initialized=True
        word=int(candidate.rom[cell,page+(front<<p.logNP)])
        mask=(1<<p.SB)-1
        assert (word&3,(word>>2)&3,(word>>4)&mask,(word>>(4+p.SB))&mask,
                (word>>(4+2*p.SB))&((1<<p.DB)-1))==(op,kind,a,b,dest)
        def read(code):
            family,index=sources[code]
            if family=='reg':return regs[front][index]
            if family=='const':return index
            if family=='scr':return scratch.get((cell,index),terms.var(('seed_scr',cell,index)))
            assert (cell,code) in at,(row,code)
            return at[cell,code]
        value=terms.op(op,read(a),read(b));instructions+=1
        if kind==0:regs[front][dest]=value
        elif kind==1:hold[cell]=value;writes[cell]=dict(sequence=seq,page=page,tick=tick,age=age)
        elif kind==2:scratch[cell,dest]=value
        else:assert kind==3
    selected={}
    for field,bit in [('h2',77),*[('addr',bit) for bit in range(p.k)],
                      *[('age',bit) for bit in range(p.m)],('f1',0),('f2',0),('wf1',0),('wf2',0),
                      *[('h2',139+bit) for bit in range(p.k)]]:
        cell=where[field,bit]
        term=hold.get(cell,terms.var(('seed_hold',cell)))
        selected[f'{field}:{bit}']=dict(cell=cell,term=term,proved_constant=term if term in (0,1) else None,
            issue=writes.get(cell),symbolic_expression=str(terms.terms[term])[:500])
    # A nonconstant normal form alone is not a counterexample. Evaluate
    # explicitly supplied assignments to find witnesses, if available.
    variables=[i for i,term in enumerate(terms.terms) if term[0]=='variable']
    rng=np.random.default_rng(171)
    assignments=rng.integers(0,2,(len(variables),64),dtype=np.uint8).astype(bool)
    index={term:i for i,term in enumerate(variables)}
    values=[np.zeros(64,dtype=bool),np.ones(64,dtype=bool)]
    for term_id,term in enumerate(terms.terms[2:],2):
        if term[0]=='variable':value=assignments[index[term_id]]
        elif term[0]==0:value=np.logical_and.reduce([values[i] for i in term[1]])
        elif term[0]==1:value=np.logical_or.reduce([values[i] for i in term[1]])
        else:
            assert term[0]==2
            value=np.logical_xor.reduce([values[i] for i in term[1]])
        values.append(value)
    target=selected['h2:77']['term']
    rows=np.flatnonzero(values[target]).tolist()
    witness=None
    if rows:
        col=rows[0]
        witness=dict(column=col,target_output=1,
            assignments=[dict(name=terms.terms[node][1],value=int(assignments[i,col])) for i,node in enumerate(variables)])
    return dict(readonly_mode=mode,start_age=start_age,late_instructions=instructions,
        initial_register_and_scratch_bits_arbitrary=True,matched_instruction_I_arbitrary=True,
        terms=len(terms.terms),selected_Hold_outputs=selected,
        h2_77_suffix_proved_constant_zero=target==0,
        explicit_arbitrary_seed_h2_77_one_assignment=witness,
        seed_reachability_in_actual_first_pulse_history_proved=False)


def main():
    start=time.monotonic();p=proposed.parameters();candidate=proposed.load_artifact()
    out=ROOT/'figs/robustness';listing_path=out/'SP29_program_listing.json'
    listing=json.loads(listing_path.read_text())
    rows=[run(p,candidate,listing,mode,284547) for mode in
          ('all_readonly_zero','h2_77_readonly_zero','h2_mail_readonly_zero',
           'four_h2_copies_and_mail_zero','shifted_initial_private_zero','native_inputs_zero')]
    result=dict(scope='Exploratory exact abstract late-suffix implications only; no physical seed reachability or complete signal claim',
        proposed_candidate_sha256=candidate.digest(),checker_sha256=digest(__file__),
        programme_listing_sha256=digest(listing_path),proposal_sha256=digest(proposed.__file__),
        algebra_source_sha256=digest(ROOT/'Report/proofs/check_g17_schedule.py'),
        retained_initial_dense_route_failure_sha256=digest(out/'SP29_late_suffix_initial_dense_route_failure.json'),
        retained_two_mode_probe_sha256=digest(out/'SP29_late_suffix_two_mode_probe.json'),
        cases=rows,active_G17_modified=False,rule_or_constant_changed=False,
        global_reliability_established=False,seconds=time.monotonic()-start)
    destination=out/'SP29_late_suffix_probe.json'
    destination.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(cases=[{k:r[k] for k in ('readonly_mode','late_instructions','h2_77_suffix_proved_constant_zero')} for r in rows],
                         seconds=result['seconds'])),flush=True)


if __name__=='__main__':main()
