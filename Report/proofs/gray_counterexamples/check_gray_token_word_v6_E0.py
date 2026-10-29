#!/usr/bin/env python3
"""Separate GMW6 current-row E0 coupling cofactors and retained checks.

Universal whole-word payload correction is the linked algebraic proof.
The native flag cofactors exhaust their reduced finite Boolean domain;
full-cell comparisons are additional measured implementation checks.
No frozen GMW5/GMW6 checkpoint artifact is rewritten.
"""
from pathlib import Path
import hashlib,itertools,json,random,sys,time
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT))
import gray_token_word_v6 as k
import build_gray_token_word_v6 as builder
from gacsca import gray_errors


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
SUPPORTS=[()]+[(j,) for j in range(-5,6)]+list(itertools.combinations(range(-5,6),2))
GF_CLASSES=list(range(6))+list(range(k.Q-5,k.Q))


def native_cofactors():
    count=0
    for address in GF_CLASSES:
        for support in SUPPORTS:
            for values in itertools.product(range(16),repeat=len(support)):
                cells={j:dict(addr=(address+j)%k.Q,age=112*k.Q,f1=0,f2=0,wf1=0,wf2=0) for j in range(-5,6)}
                for j,payload in zip(support,values):
                    # Geometry majority independence is proved algebraically;
                    # this concrete setting makes every bad GF/Age differ.
                    cells[j]['addr']=(cells[j]['addr']+3979)%k.Q
                    cells[j]['age']^=k.SMALL_MASK
                    for i,name in enumerate(('f1','f2','wf1','wf2')):cells[j][name]=(payload>>i)&1
                result=k.predecessor.scalar_native(cells)
                assert result==dict(addr=address,age=112*k.Q+1,f1=0,f2=0,wf1=0,wf2=0)
                count+=1
    assert count==156827
    return count


def vote_cofactors():
    count=0
    groups={y:tuple(y-s for s in k.SLOTS) for y in range(-3,4)}
    for y,holders in groups.items():
        assert len(set(holders))==5 and min(holders)>=-5 and max(holders)<=5
        for support in SUPPORTS:
            for bits in itertools.product((0,1),repeat=len(support)):
                payload=dict(zip(support,bits))
                for reference in (0,1):
                    assert k.vote([payload.get(x,reference) for x in holders])==reference
                    count+=1
    assert count==3402
    return count,groups


def arbitrary_cell(rng,maximum=False):
    def value(width):return (1<<width)-1 if maximum else rng.getrandbits(width)
    return k.Cell(addr=value(13),age=value(20),
        **{n:value(1) for n in ('f1','f2','wf1','wf2')},
        **{n:tuple(value(w) for _ in k.SLOTS) for n,w in
           (('heads',2200),('mem',1100),('out',100),('info',100),('scratch',100),('program',100))})


def quiet_slice(address,clock,rng):
    logical={y:{n:rng.getrandbits(w) for n,w in (('heads',2200),('mem',1100),
        ('out',100),('info',100),('scratch',100),('program',100))} for y in range(-7,8)}
    return {j:k.Cell(addr=(address+j)%k.Q,age=clock,
        **{n:tuple(logical[j+s][n] for s in k.SLOTS) for n in logical[0]}) for j in range(-5,6)}


def finite_full_cell_comparisons(rom):
    rng=random.Random(0x6E0);count=0
    addresses=sorted(set(GF_CLASSES+list(range(k.HEAD_ADDRESS-2,k.HEAD_ADDRESS+3))))
    clocks=(0,k.U-1,112*k.Q-1,112*k.Q,112*k.Q+1,120*k.Q-1,120*k.Q,k.U-2)
    rows=[]
    for address in addresses:
        for clock in clocks:
            clean=quiet_slice(address,clock,rng);expected=k.local_transition(clean,rom)
            payloads=[arbitrary_cell(rng,maximum=True),arbitrary_cell(rng)]
            for support in SUPPORTS:
                noisy=dict(clean)
                for i,j in enumerate(support):noisy[j]=payloads[i]
                assert k.local_transition(noisy,rom)==expected
                count+=1
            rows.append(dict(address=address,clock=clock,
                clean_inputs=[[hex(v) for v in k.cell_words(clean[j])] for j in range(-5,6)],
                fault_payloads=[[hex(v) for v in k.cell_words(cell)] for cell in payloads]))
    assert count==16*8*67==8576
    return dict(cases=count,GF_classes=addresses,clocks=list(clocks),measured_only=True),rows


def finite_temporal_cone(rom):
    rng=random.Random(0xC0E0);logical={y:{n:rng.getrandbits(w) for n,w in
        (('heads',2200),('mem',1100),('out',100),('info',100),('scratch',100),('program',100))}
        for y in range(-47,48)}
    initial={x:k.Cell(addr=(k.HEAD_ADDRESS+x)%k.Q,age=112*k.Q,
        **{n:tuple(logical[x+s][n] for s in k.SLOTS) for n in logical[0]}) for x in range(-45,46)}
    support={(0,1),(1,1),(30,3)}
    groups=gray_errors.level0_points(support)
    assert groups==support
    classified=gray_errors.classify(support,support,Q=k.Q,U=k.U,sep=104)
    assert classified['level0']==3 and not classified['candidate_level1'] and not classified['level1']
    values={p:arbitrary_cell(rng,maximum=p[0]==0) for p in sorted(support)}
    clean=dict(initial);noisy=dict(initial);updates=0;counts=[]
    for t in range(8):
        for (x,tick),cell in values.items():
            if tick==t:noisy[x]=cell
        lo=min(clean)+5;hi=max(clean)-5
        clean_next={x:k.local_transition({j:clean[x+j] for j in range(-5,6)},rom) for x in range(lo,hi+1)}
        noisy_next={x:k.local_transition({j:noisy[x+j] for j in range(-5,6)},rom) for x in range(lo,hi+1)}
        assert noisy_next==clean_next
        updates+=len(clean_next);counts.append(len(clean_next));clean,noisy=clean_next,noisy_next
    return dict(native_clock_start=112*k.Q,geometry_offset=k.HEAD_ADDRESS,
        initial=[[x,[hex(v) for v in k.cell_words(c)]] for x,c in sorted(initial.items())],
        errors=[dict(x=x,t=t,raw_words=[hex(v) for v in k.cell_words(values[x,t])]) for x,t in sorted(support)],
        original_error_class='E0',pair_is_spatial_not_temporal=True,
        classifier=classified,
        updates=updates,per_row_counts=counts,all_noisy_outputs_equal_clean=True,
        retained_finite_cone_not_iid_or_intact_history=True)


def main():
    start=time.monotonic();directory=ROOT/'figs/gray_counterexamples';source=Path(__file__).parent
    rom,_,_,errors=builder.programme().assemble();assert not errors
    native=native_cofactors();vote,groups=vote_cofactors();print('native',native,'vote',vote,flush=True)
    comparisons,rows=finite_full_cell_comparisons(rom)
    inputs=directory/'GMW6_E0_full_cell_replays.json'
    inputs.write_text(json.dumps(rows,separators=(',',':'))+'\n')
    cone=directory/'GMW6_E0_temporal_cone.json';cone.write_text(json.dumps(finite_temporal_cone(rom),separators=(',',':'))+'\n')
    receipt=dict(name='GMW6 conditional current-row whole-cell E0 coupling',Q=k.Q,U=k.U,
        lambda_original=24,c_original=104,kernel_sha256=digest(k.__file__),builder_sha256=digest(builder.__file__),
        checker_sha256=digest(__file__),proof_sha256=digest(source/'GMW6_E0_COMPONENT_COUPLING.md'),
        frozen_prepared_receipt_sha256=digest(directory/'GMW6_token_word_certificate.json'),
        dependencies_sha256={name:digest(source/name) for name in ('gray_moving_word_v2.py',
            'gray_moving_word_kernel.py','literal_maintenance.py')},classifier_sha256=digest(gray_errors.__file__),
        native_reduced_Boolean_cofactors=native,vote_cofactors=vote,actual_holder_groups=groups,
        all_GF_Age_payload_extension_is_algebraic_not_sampled=True,
        full_cell_comparisons=comparisons,full_cell_replay_sha256=digest(inputs),
        temporal_cone_sha256=digest(cone),quiet_coherent_current_row_coupling_proved_conditionally=True,
        prepared_pure_E0_decoder_extension_proved_conditionally=True,
        current_row_only_no_previous_error_wake=True,arbitrary_whole_cell_replacements=True,
        immutable_ROM_is_rule_constant_explicit=True,constant_zero_Workspace_departure_explicit=True,
        full_Gray_period_or_real1_or_iid_proved=False,active_rule_modified=False,
        elapsed_seconds=time.monotonic()-start)
    (directory/'GMW6_E0_component_certificate.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(dict(native=native,vote=vote,full_cell_comparisons=comparisons['cases'],
        elapsed_seconds=receipt['elapsed_seconds'])))


if __name__=='__main__':main()
