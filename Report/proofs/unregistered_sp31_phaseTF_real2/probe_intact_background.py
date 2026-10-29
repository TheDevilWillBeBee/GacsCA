#!/usr/bin/env python3
"""Discovery contracts for a genuine phase-TF intact-start native/Info fault.

Universal all-time intact alias scope and fault lifts require a separate
written proof. These are finite initializer, full-native and support checks.
"""
from pathlib import Path
import hashlib,json,sys,time
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT),str(ROOT/'Report/proofs'),str(ROOT/'Report/proofs/unregistered_terminal')]
import proposed_native_command1024 as proposed
from gacsca.netlist import Compiled
from probe_sp30_symbolic_left_absorption import AbsorptionNet
from gacsca.gray_errors import level0_points
OUT=ROOT/'figs/robustness/unregistered_sp31_phaseTF_real2'
NATIVE=('addr','age','f1','f2','wf1','wf2')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def initial_Info(y):
    while True:
        g,p=divmod(y,1024)
        if 59<=p<=68:return ((g%1024)>>(p-59))&1
        if not 92<=p<=96:return 0
        parent=g+p-94
        assert abs(parent)<abs(y),(y,parent)
        y=parent
def initial_word(x,f,b):
    return ((x%1024)>>b)&1 if f=='addr' else initial_Info(x+proposed.SLOTS[b]) if f=='info' else 0
def finite_initializer(c):
    assert c.layout[:10].tolist()==list(range(59,69))
    assert [int(c.layout[c.row['info',i]]) for i in range(5)]==list(range(92,97))
    n=0
    for g in range(-256,257):
        for (f,b),phase in zip(c.rows,c.layout):
            assert initial_Info(g*1024+int(phase))==initial_word(g,f,b),(g,f,b,phase)
            n+=1
        for phase in (3,58,509,515,965,1021):assert initial_Info(g*1024+phase)==0
    return dict(upper_coordinates=[-256,256],finite_full_encoding_primary_equalities=n,
                initializer_uses_unshifted_origin_and_strict_absolute_value_rank=True,
                all_native_flags_and_private_fields_initially_zero=True)
def native(p):
    rows=[]
    for age in (0,p.T_wf-1,p.T_wf,p.T_wf+171,p.U-1):
        for x in (0,1,2,3,4,5,37,511,512,513,1018,1019,1020,1021,1022,1023):
            class Intact(AbsorptionNet):
                def input(self,key):
                    if isinstance(key,tuple) and len(key)==4 and key[0]=='x':
                        _,d,f,b=key;z=x+d
                        if f in NATIVE:
                            v=z%p.Q if f=='addr' else p.age_code(age) if f=='age' else 0
                            return (v>>b)&1
                        if f=='info' and (z+proposed.SLOTS[b])%p.Q in (3,509,515,1021):return 0
                    return super().input(key)
            n,_=proposed.full_net(p,Intact)
            values={f:sum(n.outputs['y',f,b]<<b for b in range(dict(proposed.schema(p))[f]))
                for f in NATIVE if all(n.outputs['y',f,b] in (0,1) for b in range(dict(proposed.schema(p))[f]))}
            expect=dict(addr=x%p.Q,age=p.age_code((age+1)%p.U),f1=0,f2=0,wf1=0,wf2=0)
            assert values==expect,(age,x,values,expect)
            rows.append(dict(logical_Age=age,receiver=x,outputs=values,full_cofactor_sha256=Compiled(n).digest))
    return rows
def supports(p):
    # Genuine actual upper old GF is canonical, old F1/alias copies0;
    # these premise facts are supplied by the forthcoming all-time proof.
    upper=[*range(-15*p.Q,0),*range(1019,1024)]
    assert len(upper)==15365 and max(upper)-min(upper)+1==16*p.Q
    assert not level0_points([(x,p.T_wf) for x in upper])
    gf=range(-14*p.Q-512,0)
    flag=(*range(-15*p.Q,-14*p.Q-512),*range(-512,0))
    lower=set()
    for x,phase in [*((x,68) for x in gf),*((x,88) for x in flag)]:
        lower.update(x*p.Q+phase-slot for slot in proposed.SLOTS)
    for slot in proposed.SLOTS:
        x=1021-slot;phase=92+(slot+2)
        lower.update(x*p.Q+phase-copy for copy in proposed.SLOTS)
    assert len(lower)==79385
    assert (min(lower),max(lower))==(-15728554,1047646)
    assert max(lower)-min(lower)<16*p.Q*p.Q and max(lower)-min(lower)<24*p.Q*p.Q
    assert not level0_points([(x,p.T_wf*p.U) for x in lower])
    return dict(upper_fault_row=p.T_wf,upper_genuine_changed_whole_cell_locations=len(upper),
                upper_support_hull=[min(upper),max(upper)+1],upper_E0_points=0,
                upper_c16_real2_conditioniii_all_points_diameter_below16Q=True,
                upper_E1_exclusion_requires_written_lambdaQ_connected_support_isolation_proof=True,
                lower_fault_row=p.T_wf*p.U,lower_genuine_changed_whole_cell_locations=len(lower),
                lower_support_hull=[min(lower),max(lower)+1],lower_E0_points=0,
                lower_c16_real3_conditioniii_all_points_diameter_below16Q_squared=True,
                lower_E1_E2_exclusion_requires_written_connected_support_isolation_proof=True,
                causality_radius=39,comparison_steps=172,comparison_cone_radius=172*39,
                changed_farleft_geometry_rightmost_exclusive=-14*p.Q-512,
                comparison_cone_excludes_farleft_difference=172*39<14*p.Q+512)
def compute():
    start=time.monotonic();p=proposed.parameters();c=proposed.load_artifact()
    return dict(Q=p.Q,U=p.U,TF=p.T_wf,candidate_sha256=c.digest(),netlist_sha256=c.comp.digest,
        probe_sha256=sha(__file__),initializer=finite_initializer(c),selected_native_cofactors=native(p),support=supports(p),
        selected_finite_checks_measured_supplements=True,
        all_time_intact_native_alias_or_genuine_fault_trajectory_proved_by_this_probe=False,
        original_J225_same_fault_or_Gray_iid_counterexample_claim=False,
        rule_ROM_constants_or_G17_changed=False,global_reliability_established=False,seconds=time.monotonic()-start)
def main():
    OUT.mkdir(parents=True,exist_ok=True);path=OUT/'intact_background_probe01_receipt.json';assert not path.exists()
    r=compute();path.write_text(json.dumps(r,indent=2)+'\n')
    print(json.dumps(dict(passed=True,native_cofactors=len(r['selected_native_cofactors']),support=r['support'],seconds=r['seconds'])),flush=True)
if __name__=='__main__':main()
