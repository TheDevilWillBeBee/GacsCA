#!/usr/bin/env python3
"""GH0 physical hardwirer and GH1 delayed-gather obligation certificate.

An arbitrary correct beta of at mostQ bits is a PREMISE, not an own beta.
Finite C/Python comparisons are measured; word-capacity, schedule and
initialization arguments have the explicit scopes in the written proof.
"""
from pathlib import Path
from itertools import combinations,product
from functools import lru_cache
import ctypes,hashlib,json,subprocess,sys,time
import numpy as np
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT))
sys.path.insert(0,str(ROOT/'Report/proofs'))
import gray_layout_hardwirer as gh
import gray_hardwired_gather as gather
import gray_raw_gather as gt
import gray_moving_word_v2 as native_h1
from gacsca import gray_errors
from gacsca.netlist import Net,const_word
from check_g17_schedule import Terms


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def emit(comp,name,directory):
    graph=directory/(name+'_transitions.json')
    graph.write_text(json.dumps(dict(name=name+' isolated component, no own beta',Q=gh.Q,U=gh.U,
        inputs=comp.inputs,gates=comp.gates,outputs=list(comp.outputs.items()),netlist_sha256=comp.digest,
        projected_programme_input_equation='beta[(rawGF(actual_holder)+copy_offset) modQ]',
        native_computed_controls_are_integration_ports=True),separators=(',',':'))+'\n')
    code=['#include <stdint.h>',f'void {name.lower()}_transition(const uint8_t *input,uint8_t *output) {{',
        f' uint8_t v[{comp.n_nodes}];',' v[0]=0; v[1]=1;']
    code += [f' v[{2+i}]=input[{i}]&1;' for i in range(len(comp.inputs))]
    for i,(op,a,b) in enumerate(comp.gates,2+len(comp.inputs)):
        assert op in (0,1,2) and 0<=a<i and 0<=b<i
        code.append(f' v[{i}]=v[{a}] '+('&','|','^')[op]+f' v[{b}];')
    for i,(tag,node) in enumerate(comp.outputs.items()):code.append(f' output[{i}]=v[{node}]; /* {tag} */')
    code+=['}',f'void {name.lower()}_projected(const uint8_t *raw,const uint16_t *gf,const uint8_t *beta,uint8_t *output) {{',
        f' uint8_t input[{len(comp.inputs)}];',f' for(unsigned i=0;i<{len(comp.inputs)};i++)input[i]=raw[i]&1;']
    programme=[]
    for i,tag in enumerate(comp.inputs):
        if tag[0]=='x' and tag[2]=='programme':
            holder=tag[1];slot=gh.SLOTS[tag[3]]
            code.append(f' input[{i}]=beta[((gf[{holder+5}]&8191)+({slot+gh.Q}))&8191]&1;')
            programme.append(dict(input_index=i,actual_relative_holder=holder,copy_slot=slot))
    code+=[f' {name.lower()}_transition(input,output);','}']
    source=directory/(name+'_transitions.c');source.write_text('\n'.join(code)+'\n')
    library=directory/(name+'_transitions.so')
    subprocess.run(['gcc','-std=c11','-O2','-fPIC','-shared',str(source),'-o',str(library)],check=True)
    return graph,source,library,programme


def data_scalar(cells,phase,age,f1,wipe,f1result,f2result,writes):
    widths=dict(gt.FIELDS);answer={};starts={s[0] for s in gt.STAGES}
    def vote(f,y,b=0):return gh.majority([cells[y-t][f][i*widths[f]+b] for i,t in enumerate(gh.SLOTS)])&1
    for s in gh.SLOTS:
        for f,w in gt.FIELDS:
            for b in range(w):
                v=vote(f,s,b)
                if f=='simbit':
                    if age==0:v=vote('nextbit',s)
                    elif age==gt.FLAG_DELIVERY:
                        if (phase+s)%gh.Q==3:v=f2result
                        elif (phase+s)%gh.Q==gh.Q-3:v=f1result
                elif f=='nextbit':
                    if age in starts:v=0
                    elif 112*gh.Q<=age<120*gh.Q and writes[s][0]:v=writes[s][1]
                elif f in ('mailL','mailR'):
                    if age in starts:v=0
                    elif age in gather.GATHER_LOAD:v=vote('simbit',s)
                    elif any(start<=age<end for start,end,_ in gt.STAGES[:3]):v=vote(f,s+(1 if f=='mailL' else -1))
                elif f.startswith('history'):
                    g=int(f[-1])-1;off=gt.LANES[b]
                    if age in {x[0] for x in gt.STAGES[:g+1]}:v=0
                    elif age==gather.capture_age(g,b):v=vote('simbit' if not off else 'mailR' if off<0 else 'mailL',s)
                elif f=='voted':
                    if age in starts:v=0
                    elif age==112*gh.Q+1:
                        v=int(sum(vote('history'+str(g),s,b) for g in (1,2,3))>=2)
                if f in ('mailL','mailR') and f1:v=0
                answer[f,s,b]=0 if wipe else v
    return answer


def projected_inputs(comp,raw,gf,beta):
    result=raw.copy()
    for i,tag in enumerate(comp.inputs):
        if tag[0]=='x' and tag[2]=='programme':
            result[:,i]=np.array(beta,np.uint8)[((gf[:,tag[1]+5].astype(np.int32)+gh.SLOTS[tag[3]])%gh.Q)]
    return result


def scalar_output(comp,name,row,gf,beta):
    values=dict(zip(comp.inputs,map(int,row)))
    phase=sum(values['computed_address',b]<<b for b in range(13))
    age=sum(values['computed_age',b]<<b for b in range(20));wipe=values['native_wipe',]
    cells={}
    for j in range(-5,6):
        info=tuple(values['x',j,'simbit',q] for q in range(5))
        heads=tuple(sum(values['x',j,('head' if name=='GH0' else 'hardwire_head'),q*18+b]<<b for b in range(18)) for q in range(5))
        cells[j]=(int(gf[j+5]),info,heads)
    if name=='GH0':base=tuple(values['base_simbit',s] for s in gh.SLOTS);data={}
    else:
        old={j:{f:[values['x',j,f,b] for b in range(5*w)] for f,w in gt.FIELDS} for j in range(-5,6)}
        writes={s:(values['write_enable',s],values['write_value',s]) for s in gh.SLOTS}
        data=data_scalar(old,phase,age,values['computed_flag1',],wipe,values['flag1_result',],values['flag2_result',],writes)
        base=tuple(data['simbit',s,0] for s in gh.SLOTS)
    result=gh.scalar(cells,phase,age,wipe,beta,base)
    answer=[]
    for tag in comp.outputs:
        _,f,s,b=tag;q=gh.SLOTS.index(s)
        if f in ('head','hardwire_head'):v=(result['head'][q]>>b)&1
        elif f in ('simbit','write_enable','write_value'):v=result[f][q]
        else:v=data[f,s,b]
        answer.append(v)
    return answer


def finite_backends(comp,name,beta,directory,source,library):
    ptr=ctypes.POINTER(ctypes.c_uint8);gptr=ctypes.POINTER(ctypes.c_uint16)
    fun=getattr(ctypes.CDLL(str(library)),name.lower()+'_projected');fun.argtypes=[ptr,gptr,ptr,ptr]
    rng=np.random.default_rng(0x474830+(name=='GH1'))
    clocks=[0,1,2,3,14,3984,20366,20367,61328,16*gh.Q,32*gh.Q,32*gh.Q+1,
        48*gh.Q,64*gh.Q+1,80*gh.Q-1,96*gh.Q,112*gh.Q+1,gh.U-1]
    count=192;raw=rng.integers(0,2,size=(count,len(comp.inputs)),dtype=np.uint8)
    gf=rng.integers(0,gh.Q,size=(count,11),dtype=np.uint16)
    for i in range(count):
        phase=int(rng.integers(gh.Q));age=clocks[i%len(clocks)]
        for label,value,width in (('computed_address',phase,13),('computed_age',age,20)):
            for b in range(width):raw[i,comp.inputs.index((label,b))]=(value>>b)&1
    actual=projected_inputs(comp,raw,gf,beta)
    net=comp.evaluate({tag:actual[:,i].astype(bool) for i,tag in enumerate(comp.inputs)},bool)
    expected=np.column_stack([net[tag] for tag in comp.outputs]).astype(np.uint8)
    cresult=np.empty_like(expected);barray=np.array(beta,np.uint8)
    for i in range(count):
        fun(raw[i].ctypes.data_as(ptr),gf[i].ctypes.data_as(gptr),barray.ctypes.data_as(ptr),cresult[i].ctypes.data_as(ptr))
        independent=scalar_output(comp,name,raw[i],gf[i],beta)
        if independent!=expected[i].tolist() or not np.array_equal(cresult[i],expected[i]):
            stem=name+'_semantic_failure_01';asset=directory/(stem+'.npz')
            np.savez_compressed(asset,raw=raw[i],gf=gf[i],beta=np.array(beta,np.uint8),net=expected[i],scalar=np.array(independent,np.uint8),compiled=cresult[i])
            snapshots={}
            for path in (Path(gh.__file__),Path(gather.__file__),Path(__file__)):
                saved=directory/(stem+'_'+path.name+'.txt');saved.write_bytes(path.read_bytes());snapshots[saved.name]=digest(saved)
            (directory/(stem+'.json')).write_text(json.dumps(dict(source_snapshots_sha256=snapshots,
                asset_sha256=digest(asset),changed_component_bug=True,Gray_or_iid_failure_proved=False),indent=2)+'\n')
            raise AssertionError(stem+' '+str(i))
    asset=directory/(name+'_backend_inputs.npz');np.savez_compressed(asset,raw=raw,gf=gf,
        beta=np.array(beta,np.uint8),net=expected,compiled=cresult)
    return dict(cases=count,measured_only=True,asset=asset.name,asset_sha256=digest(asset),
        compiled_source_sha256=digest(source),compiled_library_sha256=digest(library))


def capacity():
    cases=0
    for correct in (0,1):
        for count in range(3):
            for faults in combinations(range(5),count):
                for assignment in range(1<<count):
                    word=[correct]*5
                    for i,q in enumerate(faults):word[q]=(assignment>>i)&1
                    assert gh.majority(word)==correct;cases+=1
    assert cases==102
    return cases


def physical_run(address,beta):
    old=gh.Packet(1,gh.COLLECT,address&1,0);position=gh.ADDR_START;age=2;records=[];checks=0
    # Prepared input, including an initially wrong auxiliary ProgrammeBit.
    aux=1-beta[address]
    def info(y):
        if y==0:return aux
        b=y-gh.ADDR_START
        return (address>>b)&1 if 0<=b<13 else 0
    while old.mode!=gh.DONE:
        target=position+gh.direction(old);newage=age+1
        expected,we,value=gh.head_step(old,target,info(target),beta[target])
        assert expected.mode!=gh.ERROR and 0<=target<gh.Q
        for s in gh.SLOTS:
            x=target-s
            cells={j:((x+j)%gh.Q,tuple(info(x+j+t) for t in gh.SLOTS),
                tuple(gh.pack(old) if x+j+t==position else 0 for t in gh.SLOTS)) for j in range(-5,6)}
            actual=gh.scalar(cells,x%gh.Q,newage,0,beta)
            wanted_head=tuple(gh.pack(expected) if x+t==target else 0 for t in gh.SLOTS)
            wanted_info=tuple(value if we and x+t==0 else info(x+t) for t in gh.SLOTS)
            assert actual['head']==wanted_head and actual['simbit']==wanted_info,(address,newage,x)
            checks+=1
        records.append((newage,target,gh.pack(old),gh.pack(expected),int(we),value))
        if we:aux=value
        old=expected;position=target;age=newage
    assert age==gh.completion_age(address) and aux==beta[address]
    return np.array(records,np.int64),checks


def initialization(beta):
    layout=gh.layout();reverse={a:tag for tag,a in layout.items()}
    @lru_cache(None)
    def D(x):
        parent,a=divmod(int(x),gh.Q)
        if a==0:return beta[parent%gh.Q]
        tag=reverse.get(a)
        if tag is None:return 0
        f,b=tag
        if f=='addr':return ((parent%gh.Q)>>b)&1
        if f=='simbit':
            target=parent+gh.SLOTS[b];assert abs(target)<abs(x)
            return D(target)
        return 0
    examples=sorted(set(range(-8,9))|{sign*(gh.Q**e+d) for sign in (-1,1) for e in (1,2,8,32) for d in (0,1,gh.Q-1)})
    count=0
    for x in examples:
        assert D(x*gh.Q)==beta[x%gh.Q]
        for (f,b),a in layout.items():
            expected=((x%gh.Q)>>b)&1 if f=='addr' else D(x+gh.SLOTS[b]) if f=='simbit' else 0
            assert D(x*gh.Q+a)==expected;count+=1
    assert layout['history1',0]==4010 and D(4010)==0
    assert all(D(x)==0 for x in range(4010-14,4010+15))
    return layout,D,count


def native_and_whole_cell_E0(beta):
    rng=np.random.default_rng(0x45304748);count=0
    for phase,age in product((0,1,gh.ADDR_START,gh.ADDR_END,gh.Q-1),(2,3,14,20366,16*gh.Q,32*gh.Q)):
        logical_heads={y:int(rng.integers(1<<18)) for y in range(-9,10)}
        logical_info={y:int(rng.integers(2)) for y in range(-9,10)}
        reference={x:dict(addr=(phase+x)%gh.Q,age=(age-1)%gh.U,f1=0,f2=0,wf1=0,wf2=0,
            simbit=tuple(logical_info[x+s] for s in gh.SLOTS),head=tuple(logical_heads[x+s] for s in gh.SLOTS)) for x in range(-7,8)}
        for size in range(3):
            for faults in combinations(range(-5,6),size):
                actual={x:dict(c) for x,c in reference.items()}
                for x in faults:
                    actual[x].update(addr=int(rng.integers(gh.Q)),age=int(rng.integers(gh.U)),
                        **{f:int(rng.integers(2)) for f in ('f1','f2','wf1','wf2')},
                        simbit=tuple(map(int,rng.integers(2,size=5))),head=tuple(map(int,rng.integers(1<<18,size=5))))
                for s in gh.SLOTS:
                    x=-s
                    def frame(world):return {j:(world[x+j]['addr'],world[x+j]['simbit'],world[x+j]['head']) for j in range(-5,6)}
                    native=native_h1.scalar_native({j:{f:actual[x+j][f] for f in ('addr','age','f1','f2','wf1','wf2')} for j in range(-5,6)})
                    assert (native['addr'],native['age'],native['f1'],native['f2'])==((phase+x)%gh.Q,age,0,0)
                    got=gh.scalar(frame(actual),native['addr'],native['age'],0,beta)
                    wanted=gh.scalar(frame(reference),(phase+x)%gh.Q,age,0,beta)
                    assert got==wanted,(phase,age,faults,s)
                    count+=1
    return count


def raw_holder_witness(beta):
    chosen=list(beta);chosen[0]=1;chosen[1]=0
    programme=[]
    for q,t in enumerate(gh.SLOTS):
        holder=-t;gf=1 if holder==0 else holder%gh.Q
        value=gh.projected_programme(gf,t,chosen)
        programme.append(dict(actual_holder=holder,copy_slot=t,raw_GF=gf,
            actual_programme_index=(gf+t)%gh.Q,value=value))
    assert [r['value'] for r in programme]==[0,1,1,1,1]
    old=gh.Packet(1,gh.HOME,0,0);outputs=[]
    for q,s in enumerate(gh.SLOTS):
        x=-s
        cells={j:((1 if x+j==0 else (x+j)%gh.Q),(0,)*5,
            tuple(gh.pack(old) if x+j+t==1 else 0 for t in gh.SLOTS)) for j in range(-5,6)}
        result=gh.scalar(cells,x%gh.Q,3984,0,chosen)
        assert result['write_enable'][q]==1 and result['simbit'][q]==1
        outputs.append(dict(actual_output_holder=x,copy_slot=s,auxiliary_value=result['simbit'][q]))
    classification=gray_errors.classify([(0,3983)],Q=gh.Q,U=gh.U,sep=104)
    assert classification['level0']==1
    return dict(beta=np.array(chosen,np.uint8),physical_programme_accesses=programme,
        output_holders=outputs,actual_E0_support=[[0,3983]],classification=classification,
        raw_head_center_lookup_would_return=0,actual_five_holder_vote_returns=1)


def gather_routes():
    """Exact symbolic routes on the complete computed-clock partition.

    Coherent logical data, native masks and future ports are independent
    Boolean variables. The scalar routing decision is independent of the
    emitted GH1 predicates, including its changed first snapshot/captures.
    """
    equations=rest_equations=0
    clocks=gather.clock_boundaries();phases=gt.address_boundaries()
    widths=dict(gt.FIELDS)
    for age,phase in product(clocks[:-1],phases[:-1]):
        n=Net();variables={(f,y,b):n.input(('logical',f,y,b)) for f,w in gt.FIELDS
            for y in range(-7,8) for b in range(w)}
        cells={j:{f:[variables[f,j+s,b] for s in gh.SLOTS for b in range(w)]
            for f,w in gt.FIELDS} for j in range(-5,6)}
        f1=n.input(('f1',));wipe=n.input(('wipe',));r1=n.input(('r1',));r2=n.input(('r2',))
        writes={s:(n.input(('we',s)),n.input(('wv',s))) for s in gh.SLOTS}
        actual=gather.data_build(n,cells,const_word(phase,13),const_word(age,20),f1,wipe,r1,r2,writes)
        starts={x[0] for x in gt.STAGES}
        rest=any(end<=age<stop for _,end,stop in gt.STAGES)
        for s in gh.SLOTS:
            for f,w in gt.FIELDS:
                for b in range(w):
                    expected=variables[f,s,b]
                    if f=='simbit':
                        if age==0:expected=variables['nextbit',s,0]
                        elif age==gt.FLAG_DELIVERY:
                            if (phase+s)%gh.Q==3:expected=r2
                            elif (phase+s)%gh.Q==gh.Q-3:expected=r1
                    elif f=='nextbit':
                        if age in starts:expected=0
                        elif 112*gh.Q<=age<120*gh.Q:expected=n.MUX(*writes[s],expected)
                    elif f in ('mailL','mailR'):
                        if age in starts:expected=0
                        elif age in gather.GATHER_LOAD:expected=variables['simbit',s,0]
                        elif any(start<=age<end for start,end,_ in gt.STAGES[:3]):
                            expected=variables[f,s+(1 if f=='mailL' else -1),b]
                    elif f.startswith('history'):
                        g=int(f[-1])-1;off=gt.LANES[b]
                        if age in {x[0] for x in gt.STAGES[:g+1]}:expected=0
                        elif age==gather.capture_age(g,b):
                            expected=variables['simbit' if not off else 'mailR' if off<0 else 'mailL',s,0]
                    elif f=='voted':
                        if age in starts:expected=0
                        elif age==112*gh.Q+1:
                            a,c,d=[variables['history'+str(g),s,b] for g in (1,2,3)]
                            expected=n.OR(n.AND(a,c),n.AND(d,n.OR(a,c)))
                    if rest:assert expected==variables[f,s,b];rest_equations+=1
                    if f in ('mailL','mailR'):expected=n.AND(expected,n.NOT(f1))
                    expected=n.AND(expected,n.NOT(wipe))
                    assert actual[f,s,b]==expected,(age,phase,f,s,b)
                    equations+=1
    return dict(clock_partition=clocks,address_partition=phases,
        exact_data_route_equalities=equations,exact_data_rest_equalities=rest_equations)


def real1_first_update(comp):
    """Actual emitted GH1 map, not a majority surrogate.

    At time1 neither delayed load nor birth has happened. ProgrammeBits and
    all future ports stay free. The input Head banks near y are zero, so
    the Address-primary birth at3958 cannot enter this local cone.
    """
    terms=Terms();assertions=0;y=4010
    widths=dict(gt.FIELDS)|{'hardwire_head':18}
    for site,noisy in product(range(y-7,y+8),(False,True)):
        nodes=[0,1]
        for name in comp.inputs:
            if name[0]=='x':
                _,off,field,b=name
                if field=='programme':value=terms.var(('actual_programme_holder',site+off,b))
                else:
                    q,lane=divmod(b,widths[field]);holder=site+off;logical=holder+gh.SLOTS[q]
                    assert y-14<=logical<=y+14
                    value=int(noisy and field=='simbit' and logical==y and holder in (y-1,y,y+1))
            elif name[0]=='computed_address':value=((site%gh.Q)>>name[1])&1
            elif name[0]=='computed_age':value=(2>>name[1])&1
            elif name[0] in ('computed_flag1','native_wipe'):value=0
            else:value=terms.var(('future_port',)+name)
            nodes.append(value)
        for op,a,b in comp.gates:nodes.append(terms.op(op,nodes[a],nodes[b]))
        for name,node in comp.outputs.items():
            _,field,s,b=name;expected=int(noisy and field=='simbit' and site+s==y)
            assert nodes[node]==expected,(site,noisy,name)
            assertions+=1
    assert assertions==30*330
    return assertions


def main():
    started=time.monotonic();directory=ROOT/'figs/gray_counterexamples'
    rng=np.random.default_rng(0x42455441);beta=tuple(map(int,rng.integers(2,size=gh.Q)))
    beta=tuple([1]+list(beta[1:]))
    layout,D,examples=initialization(beta);bitcases=capacity()
    routes=gather_routes()
    emitted={};backends={};graphs={}
    for name,p in (('GH0',gh),('GH1',gather)):
        comp=p.compiled();graph,source,library,programme=emit(comp,name,directory)
        assert max(abs(tag[1]) for tag in comp.inputs if tag[0]=='x')==5
        backends[name]=finite_backends(comp,name,beta,directory,source,library)
        emitted[name]=dict(netlist_sha256=comp.digest,inputs=len(comp.inputs),outputs=len(comp.outputs),gates=len(comp.gates),
            graph_sha256=digest(graph),source_sha256=digest(source),actual_programme_holder_bindings=programme)
        graphs[name]=comp
    print('emission and finite backends passed',flush=True)
    injection=real1_first_update(graphs['GH1'])
    traces={};physicalchecks=0
    for address in (0,gh.Q-1):
        trace,count=physical_run(address,beta);traces['address%d'%address]=trace;physicalchecks+=count
        assert trace.tolist()==[list(row) for row in gh.logical_run(address,beta)]
    asset=directory/'GH0_physical_courier_traces.npz';np.savez_compressed(asset,beta=np.array(beta,np.uint8),**traces)
    print('physical courier checks',physicalchecks,flush=True)
    cells=native_and_whole_cell_E0(beta);sourcewitness=raw_holder_witness(beta)
    access=directory/'GH0_raw_holder_programme_witness.json'
    witness_beta=directory/'GH0_raw_holder_witness_beta.bin'
    witness_beta.write_bytes(np.packbits(sourcewitness['beta'],bitorder='little').tobytes())
    access.write_text(json.dumps(dict({k:v for k,v in sourcewitness.items() if k!='beta'},
        beta_asset=witness_beta.name,beta_sha256=digest(witness_beta)),indent=2)+'\n')
    coordinates=[]
    for g in range(3):
        for b,off in enumerate(gt.LANES):
            capture=gather.capture_age(g,b);start,end,_=gt.STAGES[g]
            assert start<gather.GATHER_LOAD[g]<=capture<end
            assert capture==gather.GATHER_LOAD[g] if off==0 else capture==gather.GATHER_LOAD[g]+1+abs(off)*gh.Q
            coordinates.append(dict(stage=g+1,offset=off,load=gather.GATHER_LOAD[g],capture=capture,
                source_displacement=off*gh.Q))
    assert gh.completion_age(gh.Q-1)==20366 and gather.GATHER_LOAD[0]==20367
    assert max(gather.capture_age(0,b) for b in range(11))==61328<16*gh.Q
    assert max(gather.capture_age(2,b) for b in range(11))<gt.FLAG_DELIVERY
    times=[gh.completion_age(a) for a in range(gh.Q)]
    assert all(t<gather.GATHER_LOAD[0] for t in times)
    points=[(4009,1),(4010,1),(4011,1)]
    classification=gray_errors.classify(points,Q=gh.Q,U=gh.U,sep=104)
    assert classification['level0']==0 and classification['level1']
    # The new hardwirer reads SimBits only at the thirteen Address primaries.
    assert 4010 not in range(gh.ADDR_START,gh.ADDR_END+1)
    assert 4010 not in (0,3,gh.Q-3)
    proof=Path(__file__).with_name('GH0_HARDWIRER_GATHER.md')
    dependencies=('GT0_raw_gather_certificate.json','Gray_literal_stage_envelope_certificate.json',
        'GMW2_full_programme_audit_certificate.json','GH0_initial_validator_serialization_failure.json')
    row=dict(name='GH0 interior-layout projected programme courier and GH1 delayed first gather',
        Q=gh.Q,U=gh.U,lambda_original=24,c_original=104,
        courier_head_bits=18,preliminary_projected_frame_bits=367,final_complete_frame_certified=False,
        arbitrary_correct_beta_at_most_Q_is_premise=True,actual_own_beta_exists_proved=False,
        beta_used_for_checks_is_random_data_not_a_certified_own_programme=True,
        no_64K_instruction_ROM_or_whole_rule_apply=True,projected_programme_source_uses_actual_raw_holder_GF=True,
        all_raw_component_radius5_by_equations=True,raw_holder_bindings=emitted,
        backend_checks_measured_only=backends,bitwise_arbitrary_replacement_cofactors=bitcases,
        physical_all_five_holder_checks=physicalchecks,physical_address0_and8191_checks_complete=True,
        native_h1_complete_cell_finite_checks=cells,native_h1_is_explicit_correction=True,
        universal_copy_transparency_uses_correct_computed_controls_and_native_E0_word_argument=True,
        courier_completion_age_formula='2+12+3970+2A',all8192_address_bounds_checked=True,
        worst_courier_completion_age=20366,Gather1_load=20367,furthest_Gather1_capture=61328,
        only_Gather1_load_capture_schedule_changed=True,stage_endpoints_or_U_changed=False,
        original_GT0_sources_or_receipts_modified=False,other_gather_loads=list(gather.GATHER_LOAD[1:]),
        gathering_coordinates=coordinates,quiet_native_and_stable_Address_premises_explicit=True,
        all_raw_GH1_data_route_and_rest_partition_certificate=routes,
        GH1_programme_corrected_before_first_snapshot_conditional_theorem=True,
        recursive_initialization_for367_bit_prefix_frame_proved=True,finite_initializer_bit_checks=examples,
        original_real1_points=points,original_real1_classification=classification,
        selected_real1_cannot_change_hardwirer_controls_by_disjoint_read_predicates=True,
        actual_first_clean_GH1_update_cofactors=30,actual_first_clean_GH1_output_assertions=injection,
        GH1_conditional_first56Q_native_hardwirer_gather_retention_composition_proved=True,
        three_colony_witness_time=56*gh.Q,three_colony_witness_sites=[-4182,4010,12202],
        actual_complete_Gray_rule_or_Proposition4_counterexample_proved=False,
        universal_programme_fit_update_runtime_or_full_period_proved=False,
        iid_failure_or_positive_noise_rate_proved=False,active_rule_modified=False,global_reliability_established=False,
        kernel_sha256=digest(gh.__file__),gather_sha256=digest(gather.__file__),checker_sha256=digest(__file__),
        proof_sha256=digest(proof) if proof.exists() else None,
        base_GT0_sha256=digest(gt.__file__),native_h1_GMW2_sha256=digest(native_h1.__file__),
        physical_trace_sha256=digest(asset),raw_holder_witness_sha256=digest(access),
        raw_holder_witness_beta_sha256=digest(witness_beta),
        receipt_dependencies_sha256={name:digest(directory/name) for name in dependencies},
        paper_text_sha256=digest(ROOT/'papers_txt/gray_readers_guide.txt'),
        paper_pdf_sha256=digest(next((ROOT/'papers').glob('A Reader*'))),
        netlist_library_sha256=digest(ROOT/'gacsca/netlist.py'),
        term_library_sha256=digest(ROOT/'Report/proofs/check_g17_schedule.py'),
        literal_native_sha256=digest(native_h1.old.literal_maintenance.__file__),
        generated_literal_native_sha256=native_h1.old.literal_maintenance.source_sha256(),
        classifier_sha256=digest(ROOT/'gacsca/gray_errors.py'),wall_seconds=time.monotonic()-started)
    (directory/'GH0_hardwirer_gather_certificate.json').write_text(json.dumps(row,indent=2)+'\n')
    print(json.dumps(row))


if __name__=='__main__':main()
