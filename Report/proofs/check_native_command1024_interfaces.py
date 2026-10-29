#!/usr/bin/env python3
"""SP31 conditional SF identities and restricted native-factor cofactors.

The displayed proof supplies universal algebra/source correspondence.
Selected raw-state cofactors check the C transcription, not all noise.
"""
from pathlib import Path
from types import FunctionType
import ctypes,hashlib,json,subprocess,sys,time
import numpy as np
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from gacsca.netlist import Net,const_word
import proposed_native_command1024 as proposed

OUT=ROOT/'figs/robustness'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def conditional(module,p,shared,clock):
    def controller(n,cells,*args,**kwargs):
        gf=[n.input(('proof','computedGF',b)) for b in range(p.k)]
        return dict(addr=gf,age_now=const_word(p.age_code(clock),p.m),
            age=const_word(p.age_code(clock+1),p.m),
            f1=n.input(('proof','computedF1')),f2=n.input(('proof','computedF2')))
    namespace=dict(module.legacy.__dict__,schema=module.schema,width=module.width,
        previous=module.previous,dependency_table=module.dependency_table,
        service_build=module.service_build,pulse=module.pulse,
        generated_source=module.generated_source,proposed_build=lambda:(controller,'conditional interface only'))
    fn=module.legacy.full_net
    return FunctionType(fn.__code__,namespace,fn.__name__,fn.__defaults__)(p,lambda:shared)[0]


def main(write=True):
    start=time.monotonic();p=proposed.parameters();c=proposed.load_artifact()
    build=json.loads((OUT/'SP31_program_build.json').read_text())
    programme=json.loads((OUT/'SP31_symbolic_schedule.json').read_text())
    assert build['build_complete'] and build['proposed_candidate_sha256']==c.digest()
    assert programme['final_hold_equalities']==842 and programme['early_flag_equalities']==2
    assert c.digest()=='dc456bac4904647b66ee1f922788cdeb4428df91e21858fd8de0b3ccb4a69421'
    records=[]
    private_header={'wf2','packet_tag','packet_valid','packet_count','service_valid','service_position','service_count','backward_pressure'}
    for clock in (0,p.E0,p.T_sig,p.T_wf,p.T_wf+2*p.Q,p.U-1):
        shared=Net();old=conditional(proposed.prior,p,shared,clock)
        previous=dict(old.outputs);shared.outputs={};new=conditional(proposed,p,shared,clock)
        same=[];different=[]
        for key,node in previous.items():
            if key[0]!='y' or key[1] not in private_header:
                assert new.outputs[key]==node,(clock,key)
                same.append(key)
            elif new.outputs[key]!=node:different.append(key)
        records.append(dict(clock=clock,unrestricted_conditional_SF_and_control_node_equalities=len(same),
            changed_private_header_output_bits=len(different)))
    # Unrestricted node equality for native F1; inspect complete live
    # dependencies for the changed GF/Age/F1/F2 outputs.
    shared=Net();old,_=proposed.prior.full_net(proposed.prior.parameters(),lambda:shared)
    f1=old.outputs['y','f1',0];shared.outputs={};new,_=proposed.full_net(p,lambda:shared)
    assert f1==new.outputs['y','f1',0]
    allowed={'addr','age','f1','f2','wf1','wf2'}
    targets=[node for key,node in new.outputs.items() if key[0]=='y' and key[1] in {'addr','age','f1','f2'}]
    # Net.live_nodes is normally the source of Compiled, but here restrict
    # the outputs before asking it for dependencies.
    saved=dict(new.outputs);new.outputs={('proof_native',i):v for i,v in enumerate(targets)}
    native_live=set(new.live_nodes());new.outputs=saved
    input_keys=[key for key,node in new.input_node.items() if node in native_live]
    assert all(key[0]=='x' and key[2] in allowed for key in input_keys)
    library=Path('/tmp/sp31_native_events_interfaces.so')
    source=Path(__file__).with_name('sp31_native_events.c')
    subprocess.run(['cc','-O3','-std=c11','-Wall','-Wextra','-Werror','-shared','-fPIC',str(source),'-o',str(library)],check=True,capture_output=True)
    lib=ctypes.CDLL(str(library));fn=lib.sp31_cofactor
    fn.argtypes=[ctypes.POINTER(ctypes.c_uint8),ctypes.POINTER(ctypes.c_uint8),ctypes.c_int,ctypes.c_int]
    fn.restype=ctypes.c_uint
    rng=np.random.default_rng(3131);count=2048
    residues=np.array(([0,1,2,3,4,5,6,7,8,503,504,505,506,507,508,509,510,511,512,513,514,515,516,517,518,519,520,1015,1016,1017,1018,1019,1020,1021,1022,1023]*57)[:count])
    elapsed=np.tile([0,1,2047,2048,6143],410)[:count]
    native=rng.integers(0,8,size=(count,81),dtype=np.uint8)
    raw_info=rng.integers(0,2,size=(count,81),dtype=np.uint8)
    for i,x in enumerate(residues):
        pos=(x+np.arange(-40,41))%p.Q
        raw_info[i,(pos==3)|(pos==515)]=0
    expected=np.array([fn(a.ctypes.data_as(ctypes.POINTER(ctypes.c_uint8)),
        b.ctypes.data_as(ctypes.POINTER(ctypes.c_uint8)),int(x),int(t))
        for a,b,x,t in zip(native,raw_info,residues,elapsed)],dtype=np.uint8)
    values={}
    ages=np.array([p.age_code(p.T_wf+int(t)) for t in elapsed],dtype=np.uint32)
    for key in c.comp.inputs:
        if key[0]=='I':v=rng.integers(0,2,size=count,dtype=np.uint8)
        else:
            _,d,f,b=key
            if f=='addr':v=((residues+d+512*(native[:,d+40]&1))%p.Q>>b)&1
            elif f=='age':v=(ages>>b)&1
            elif f=='f1':v=(native[:,d+40]>>1)&1
            elif f=='wf1':v=(native[:,d+40]>>2)&1
            elif f in ('f2','wf2'):v=np.zeros(count,dtype=np.uint8)
            elif f=='info':v=raw_info[:,d+b-2+40]
            else:v=rng.integers(0,2,size=count,dtype=np.uint8)
        values[key]=v.astype(bool)
    actual=c.comp.evaluate(values,bool)
    gf=(residues+512*(expected&1))%p.Q
    for b in range(p.k):assert np.array_equal(actual['y','addr',b],((gf>>b)&1).astype(bool))
    assert np.array_equal(actual['y','f1',0],((expected>>1)&1).astype(bool))
    assert np.array_equal(actual['y','wf1',0],((expected>>2)&1).astype(bool))
    assert not actual['y','f2',0].any() and not actual['y','wf2',0].any()
    keep=~(((expected>>1)&1).astype(bool)&((expected&1)!=((expected>>3)&1)))
    for slot in proposed.SLOTS:assert np.array_equal(actual['y','info',slot+2],keep&raw_info[:,slot+40].astype(bool))
    result=dict(proposal='SP31',explicit_new_rule=True,active_G17_or_SP30_modified=False,
        Q=p.Q,U=p.U,width=c.W,radius=37,candidate_sha256=c.digest(),netlist_sha256=c.comp.digest,
        checker_sha256=sha(__file__),proposal_source_sha256=sha(proposed.__file__),
        conditional_SF_records=records,unrestricted_F1_function_unchanged=True,
        unrestricted_native_GF_Age_F1_F2_private_header_instruction_independence=True,
        native_live_input_keys=len(input_keys),selected_actual_full_net_factor_transcription_cases=count,
        C_source_sha256=sha(source),C_library_sha256=sha(library),
        symbolic_own_programme_proved=True,actual_complete_encoding_or_E0_theorem_proved_by_this_checker=False,
        actual_prepared_native_event_premises_or_general_eroder_proved=False,
        global_reliability_established=False,elapsed_seconds=time.monotonic()-start)
    if write:(OUT/'SP31_interface_certificate.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('selected_actual_full_net_factor_transcription_cases',
        'unrestricted_native_GF_Age_F1_F2_private_header_instruction_independence',
        'symbolic_own_programme_proved','global_reliability_established','elapsed_seconds')}),flush=True)
    return result


if __name__=='__main__':main()
