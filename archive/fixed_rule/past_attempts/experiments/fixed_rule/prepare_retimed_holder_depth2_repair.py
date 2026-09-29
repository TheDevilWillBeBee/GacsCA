"""Construct a non-vacuous depth-two encoded-controller fault fixture.

Diagnostic preparation only. Complete GPU faulty trajectories are separate work.
"""
import argparse,hashlib,json,resource,time
from dataclasses import replace
from pathlib import Path
import numpy as np
from gacsca.fixed_rule import retimed_holder_projected as r,retimed_holder_rule as f,retimed_holder_core as c,retimed_holder_program as p,retimed_holder_initial as initial
from gacsca.fixed_rule import retimed_holder_endpoint_image_array as image


def raw(cell):return np.array(f.encode_cell(r.lift(cell)),dtype=np.uint64)

def fixture():
    values=dict(address=100,age=c.RESET_AGES[4]+100)
    for j in range(5):
        for name,value in dict(data=0x13579bdf,head=1,phase=c.READ_B,pc=23,rb=99,rd=107,value=0x123456789abcdef0,alu=c.NAND).items():values[f's{j}_{name}']=value
    healthy=r.Cell(**values);dirty=replace(healthy,s0_rb=98,s1_rb=98);triple=replace(dirty,s2_rb=98)
    return healthy,dirty,triple


def physical_faults(healthy,dirty):
    g=p.layout();arrays=[]
    for cell in (healthy,dirty):
        bank=np.zeros((1,g.memory_count+5),dtype=np.uint64);bank[0,list(g.info)]=raw(cell)
        arrays.append(image.render(bank,np.zeros((1,2),dtype=np.uint64),0))
    changes=np.argwhere(arrays[0]!=arrays[1]);faults=[]
    for pos,k in changes:
        xor=int(arrays[0][pos,k]^arrays[1][pos,k]);assert xor==1
        primary=int(pos)*f.Q+g.info[int(k)]
        for offset in f.OFFSETS:faults.append(((primary-offset)%(f.Q*f.Q),f.COL[f's{offset+2}_data'],xor))
    faults=np.array(faults,dtype=np.uint64);assert len({(int(a),int(b)) for a,b,_ in faults})==len(faults)
    grouped={}
    for pos,field,xor in faults:grouped.setdefault(int(pos),[]).append((int(field),int(xor)))
    for pos,changes_here in grouped.items():
        before=raw(initial.cell_at((healthy,),2,pos));after=raw(initial.cell_at((dirty,),2,pos))
        for field,xor in changes_here:before[field]^=np.uint64(xor)
        np.testing.assert_array_equal(before,after)
    return faults,len(changes)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True);args=parser.parse_args();out=Path(args.output);artifact=out.with_suffix('.npz')
    if out.exists() or artifact.exists():raise FileExistsError(out)
    started=time.perf_counter();healthy,dirty,triple=fixture();following=[r.step_ring((x,))[0] for x in (healthy,dirty,triple)]
    assert following[0]==following[1] and following[0]!=following[2]
    assert following[0].s2_phase==c.WRITE and following[2].s2_phase==c.READ_B
    assert following[0].s2_value==c.arithmetic(c.NAND,healthy.s2_value,healthy.s2_data)
    two,intermediate_two=physical_faults(healthy,dirty);three,intermediate_three=physical_faults(healthy,triple)
    assert len(two)==50 and len(three)==75
    np.savez_compressed(artifact,healthy=raw(healthy),dirty_two=raw(dirty),dirty_three=raw(triple),healthy_next=raw(following[0]),dirty_two_next=raw(following[1]),dirty_three_next=raw(following[2]),two_physical_faults=two,three_physical_faults=three)
    sha=lambda path:hashlib.sha256(Path(path).read_bytes()).hexdigest()
    result=dict(passed=True,two_wrong_top_rb_copies=True,three_copy_control_changes_transition=True,active_controller_transition='READ_B to WRITE with NAND',two_intermediate_word_faults=intermediate_two,three_intermediate_word_faults=intermediate_three,two_case_bottom_bit_faults=len(two),three_case_bottom_bit_faults=len(three),all_affected_physical_cells_equal_direct_depth2_initialization=True,seconds=time.perf_counter()-started,host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,artifact_sha256=sha(artifact),source_sha256={str(path):sha(path) for path in (Path(__file__),Path(image.__file__),Path(initial.__file__))},scope='Exact deterministic initial physical bit-fault sets representing two/three wrong encoded top rb replicas. Scalar non-vacuous repair/control verified. No faulty depth-two GPU trajectory or general stochastic correction claim yet.')
    out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
