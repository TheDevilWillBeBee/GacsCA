"""Finite supplements for the written stationary native-profile induction."""
from pathlib import Path
import argparse,ctypes,hashlib,json,random,sys,tempfile,time
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
sys.path.insert(0,str(HERE.parent/'unregistered_gawn10'))
import check_gawn10_two_offset_projection as c
Q=c.k.Q;T0=c.T0
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def profile(x,delta):
    return (int(-delta<=x<Q),int(-Q<=x<-delta or Q-max(delta,3)<=x<Q),0,0,0)
def compute():
    rng=random.Random(0x4741574e313201);dig=hashlib.sha256();full=hashlib.sha256();records=[];count=kernels=0
    with tempfile.TemporaryDirectory(prefix='gawn12_stationary_') as tmp:
        lib,binary=c.library(tmp)
        for delta in range(1,9):
            wrong=flags=0
            for x in range(-Q-8,Q+8):
                raw=(c.Site*17)(*[c.Site(*profile(x+j,delta)) for j in range(-8,9)])
                out=c.Site();assert lib.gawn10_cofactor(raw,x,delta,ctypes.byref(out))==0
                got=tuple(getattr(out,name) for name,_ in c.Site._fields_)
                want=profile(x,delta);assert got==want,(delta,x,got,want)
                c.add(dig,[delta,x,list(got)]);count+=1;wrong+=want[0];flags+=want[1]
            assert wrong==Q+delta and flags==Q+max(3-delta,0)
            r=(-3+delta)%Q;ell=-3-r if r<=5 else -3
            assert -delta>=ell
            positions=sorted(set((-Q-1,-Q,-Q+1,-delta-4,-delta-3,-delta-2,-delta-1,-delta,
                -delta+1,0,Q-max(delta,3)-1,Q-max(delta,3),Q-4,Q-3,Q-2,Q-1,Q,Q+1)))
            for x in positions:
                for age in (T0,T0+103,T0+4*Q,c.k.U-1):
                    c.actual_check(lib,rng,x,delta,age,[profile(x+j,delta) for j in range(-8,9)],full)
                    kernels+=1
            records.append(dict(delta=delta,ell=ell,wrong_Address_count=wrong,Flag1_count=flags,
                overwritten_sites=2*Q,full_kernel_comparisons=4*len(positions)))
        binary_sha=sha(binary)
    sources=(Path(__file__),HERE/'GAWN12_STATIONARY_NATIVE_PROFILE.md',
        HERE.parent/'unregistered_gawn10/gawn10_two_offset_projection.c',
        HERE.parent/'unregistered_gawn10/check_gawn10_two_offset_projection.py',
        HERE.parent/'unregistered_gawn2/small_rule_gawn2.py',
        HERE.parent/'unregistered_gawn2/small_compositional_cost.py')
    return dict(name='GAWN12 unchanged GAWN2 stationary native exterior-profile obstruction',passed=True,
        Q=Q,U=c.k.U,lambda_original=24,error_separation=104,first_fault_row=T0,
        actual_one_row_native_only_overwrite_from_H2=True,exact_overwritten_sites=2*Q,
        oldSF_clock_Flag2_Workspace_retained=True,no_later_errors=True,
        stationary_native_through_currentU_proved=True,
        invariant_alone_implies_native_recovery_byU=False,
        actual104site104row_class_reachability_proved=False,
        admitted_burst_termination_counterexample_Gray_G17_iid_or_bitfailure_proved=False,
        persistence_after_reopened_Workspace_pulse_proved=False,
        fullSF_evolution_or_fullperiod_physical_simulation_performed=False,
        rule_ROM_constants_G17_changed=False,native_site_checks=count,
        selected_full_kernel_comparisons=kernels,native_outputs_sha256=dig.hexdigest(),
        arbitrarySF_full_kernel_inputs_outputs_sha256=full.hexdigest(),C_shared_object_sha256=binary_sha,
        records=records,source_sha256={str(p.relative_to(ROOT)):sha(p) for p in sources})
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--write',action='store_true');args=parser.parse_args()
    start=time.perf_counter();certificate=compute()
    if args.write:
        out=ROOT/'figs/gray_counterexamples/unregistered_gawn12/GAWN12_stationary_native_certificate.json'
        out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(certificate,indent=2)+'\n')
    print(json.dumps(dict(passed=True,profiles=8,native_sites=certificate['native_site_checks'],
        full_kernel_comparisons=certificate['selected_full_kernel_comparisons'],
        actual_fault_width=2*Q,admitted_small_burst_refutation=False,full_reliability=False,
        elapsed=time.perf_counter()-start)))
if __name__=='__main__':main()
