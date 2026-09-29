"""Complete-descriptor structural composition for two-site/two-tick G repair.

Cuts are found by exact expression structure, not names or opcode inventories.
The geometry cuts use the separately quantified two-site geometry certificate.
"""
import argparse,json,resource,time
from collections import Counter
from pathlib import Path
from gacsca.fixed_rule import compact16_holder_rule as f,compact16_holder_core as c,compact16_holder_program as p
from gacsca.fixed_rule.wordcode import Program,Builder,LIT
from experiments.fixed_rule.certify_compact16_holder_replica_repair import Structure,majority,gates,cut
from experiments.fixed_rule.prove_compact16_holder_two_site_geometry import geometry
from experiments.fixed_rule.certify_compact16_holder_clock_mail_factorization import ClockTerms
from experiments.fixed_rule.run_compact16_holder_streamed_depth2 import sha


def cuts(description):
    structure=Structure();actual=structure.wires(description);by_node={}
    for wire,node in enumerate(actual):by_node.setdefault(node,[]).append(wire)
    roots={};groups=[]
    def identify(program,labels):
        nodes=structure.wires(program)
        for label,output in zip(labels,program.outputs):
            found=by_node.get(nodes[output],())
            if found:
                groups.append(dict(label=label,roots=list(found)))
                for wire in found:
                    if wire in roots:assert roots[wire]==label,('conflicting cut',roots[wire],label)
                    roots[wire]=label
    gp,_=geometry(description)
    for offset in f.OFFSETS:
        def shift(wire):
            result=wire+offset*f.FIELDS if wire<gp.inputs else wire
            if wire<gp.inputs:assert 0<=result<gp.inputs
            return result
        shifted=Program(gp.inputs,tuple((op,a,b) if op==LIT else (op,shift(a),shift(b)) for op,a,b in gp.operations),tuple(shift(x) for x in gp.outputs))
        identify(shifted,tuple(('geometry',offset,name) for name in ('address','age','f1','f2')))
    for primary in range(-4,5):
        for name,width in f.PROCEDURE:
            b=Builder(description.inputs);leaves=tuple((primary+e+7)*f.FIELDS+f.COL[f's{2-e}_{name}'] for e in f.OFFSETS)
            identify(b.finish((majority(b,leaves,width),)),(('procedure',primary,name),))
    for primary in range(-5,6):
        b=Builder(description.inputs);one=b.const(1)
        leaves=[b.band(b.shr((primary+e+7)*f.FIELDS+f.COL['signal'],b.const(2-e)),one) for e in f.OFFSETS]
        identify(b.finish((b.count(leaves,3),)),(('signal',primary,'bit'),))
    assert sum(x['label'][0]=='geometry' for x in groups)==20
    assert {x['label'][1] for x in groups if x['label'][0]=='signal'}==set(range(-4,6)), 'unexpected reached Signal votes'
    return roots,groups


def variables(terms,word):
    pending=[word];seen=set();result=set()
    while pending:
        x=pending.pop()
        if x in seen:continue
        seen.add(x);node=terms.nodes[x];kind=node[0]
        if kind=='variable':result.add(node[1])
        elif kind=='op':pending.extend(node[2:])
        elif kind in ('not','modadd'):pending.append(node[1])
        elif kind!='const':raise AssertionError(('unreviewed proof node',node))
    return result


def structural(description=None):
    desc=f.self_description() if description is None else description;roots,groups=cuts(desc)
    address_bits=f.Q.bit_length()-1;clock_bits=f.U.bit_length()-1
    t=ClockTerms(p.base_rom());address=t.variable('canonical_address',address_bits);age=t.variable('legal_age',clock_bits);zero=t.const(0)
    def evaluate(holder,damaged_center=False):
        values=[]
        for relative in f.NEIGHBORHOOD:
            site=holder+relative
            for name,width in f.SCHEMA:
                value=t.variable(f'raw_{site}_{name}',width)
                if relative==0:
                    if name=='address':value=t.variable('bad_address',dict(f.SCHEMA)['address']) if damaged_center else t.modular_add(address,holder,address_bits)
                    elif name=='age':value=t.variable('bad_age',32) if damaged_center else age
                    elif name.startswith('p'):
                        prefix,field=name.split('_',1);offset=int(prefix[1:])-3
                        value=t.variable(f'bad_meta_{offset}_{field}' if damaged_center else f'meta_{holder+offset}_{field}',width)
                    elif damaged_center:value=t.variable('bad_raw_'+name,width)
                values.append(value)
        for wire,(op,a,b) in enumerate(desc.operations,desc.inputs):
            if wire in roots:
                kind,offset,name=roots[wire];site=holder+offset
                if kind=='geometry':
                    value=t.modular_add(address,site,address_bits) if name=='address' else t.modular_add(age,1,clock_bits) if name=='age' else zero
                elif kind=='procedure':value=t.variable(f'proc_{site}_{name}',dict(f.PROCEDURE)[name])
                else:value=t.variable(f'signal_{site}',1)
            else:value=t.const(a) if op==LIT else t.op(op,values[a],values[b])
            values.append(value)
        return tuple(values[x] for x in desc.outputs)
    healthy=evaluate(0);damaged=evaluate(0,True);procedure={f's{k}_{name}' for k in range(5) for name,_ in f.PROCEDURE}
    nonprocedure=[]
    for k,(name,_) in enumerate(f.SCHEMA):
        if name.startswith('p'):
            assert desc.outputs[k]==7*f.FIELDS+k,'F metadata preservation changed'
            continue
        support=variables(t,healthy[k]);assert not any(x.startswith(('raw_','bad_raw_')) for x in support),(name,'uncut raw dependency',support)
        if name not in procedure:
            assert healthy[k]==damaged[k],('nonprocedure depends on faulty old center',name)
            nonprocedure.append(name)
        else:
            assert all(x in ('canonical_address','legal_age') or x.startswith(('proc_','meta_')) for x in support),(name,support)
    # Completely unrestricted logical procedure words at every site. No one-head
    # or inactive-controller premise is introduced by this alpha-equivalence.
    rows={holder:evaluate(holder) for holder in f.OFFSETS};coherent=[]
    for name,_ in f.PROCEDURE:
        words=[rows[holder][f.COL[f's{2-holder}_{name}']] for holder in f.OFFSETS]
        assert len(set(words))==1,('healthy output backups not coherent',name)
        coherent.append(name)
    assert len(nonprocedure)==15 and len(coherent)==18
    return dict(passed=True,cut_groups=dict(Counter(x['label'][0] for x in groups)),cut_root_count=len(roots),groups=groups,all_mutable_nonprocedure_fields_equal=nonprocedure,healthy_output_coherent_procedure_fields=coherent,unrestricted_logical_procedure_words=True,no_head_count_assumption=True,all_healthy_addresses=f.Q,all_legal_ages=f.U,symbolic_terms=len(t.nodes),complete_raw_outputs=f.FIELDS,static_fields_restored_by_G_projection=len(f.STATIC))


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True);args=parser.parse_args();out=Path(args.output)
    if out.exists():raise FileExistsError(out)
    started=time.perf_counter();path=Path('figs/fixed_rule/compact16_holder_two_site_geometry_v1.json');geo=json.loads(path.read_text())
    assert geo['passed'] and geo['complete_position_cover'] and len(geo['cases'])==55
    assert geo['descriptor_sha256']==f.self_description().digest()
    for source,digest in geo['source_sha256'].items():assert sha(source)==digest,source
    gate_checks=gates();existing_cut=cut();result=structural()
    result.update(geometry_certificate=str(path),geometry_certificate_sha256=sha(path),majority_gate_checks=gate_checks,complete_procedure_cut_replayed=True,replayed_cut_groups=existing_cut['identified_majority_groups'],descriptor_sha256=f.self_description().digest(),seconds=time.perf_counter()-started,host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,source_sha256={str(x):sha(x) for x in (Path(__file__),Path('experiments/fixed_rule/certify_compact16_holder_replica_repair.py'),Path('experiments/fixed_rule/certify_compact16_holder_clock_mail_factorization.py'),Path(f.__file__),Path('gacsca/fixed_rule/compact16_holder_description.py'))},theorem='For G on the infinite line or a periodic ring of size divisible by Q, canonical Address, uniform legal Age, zero primary flags/Wf, coherent procedures and coherent fivefold Signals imply: replacing arbitrary mutable states at at most two physical sites gives exactly the same complete G^2 configuration as the healthy trajectory. Logical controller/mail/Data words are unrestricted. Fixed metadata is regenerated by G, not independently faulted hardware.',limitation='Conditional two-tick isolated-pulse recovery. Does not assert arbitrary forcing-phase recovery, persistent space-time noise, global amplification, robust cap behavior or a general threshold.')
    out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='groups'},indent=2),flush=True)

if __name__=='__main__':main()
