"""Native-record command discovery; physical writeback premises audited separately.

This does not replace the CA or choose future commands. Every trial bank is
the gather/reset recurrence from the frozen fourth boundary; a successful
physical lift must still justify native stores and source-zero preservation.
"""
from pathlib import Path
import sys,json
S=Path(__file__).resolve().parent;ROOT=S.parents[3]
sys.path.insert(0,str(S.parent/'unregistered_gaw27'))
import check_gaw27_physical_late_factor as old
k=old.k;own=old.own;Q=k.Q;U=k.U;P=k.PRIMARY_START
LO=-256;HI=512
NAMES=k.NATIVE_NAMES
def blocked(p,q,A):
    p,q=sorted((p,q))
    return p<(A+.5)*Q and q>=A*Q or p<(A+4)*Q and q>=(A+3.5)*Q
def retained(p,A):
    return not ((2*A+1)*Q//2<=p<(2*A+7)*Q//2 or (A+4)*Q<=p<(A+7)*Q)
def bank(T,V,g,foreign,A,late=False):
    origin=g*Q-(Q//2 if foreign else 0);records=V if foreign else T
    rows=[]
    for i in range(6):
        p=origin+P+i
        rows.append([records[g+d][i] if (not late or retained(p,A)) and (not d or not blocked(p,p+d*Q,A)) else 0 for d in range(-8,9)])
    return rows
def native(rows):
    cells={d:k.Cell(**dict(zip(NAMES,[r[d+8] for r in rows]))) for d in range(-8,9)}
    result=k.native_at(cells)
    return [result[name] for name in NAMES]
def next_records(T,V,n,A):
    outT={};outV={}
    for g in range(min(T)+8,max(T)-7):
        outT[g]=native(bank(T,V,g,False,A,True)) if g<=A+3 or g>=A+7 else [0]*6
        outV[g]=native(bank(T,V,g,True,A,True)) if A+4<=g<=A+7 else [0]*6
    return outT,outV
def commands(T,V,n,A):
    runs=[]
    for g in range(min(T)+8,max(T)-7):
        if g<=A or g>=A+4:runs.append((g,False,native(bank(T,V,g,False,A))))
        if A+1<=g<=A+4:runs.append((g,True,native(bank(T,V,g,True,A))))
    right=[];left=[]
    for g,f,z in runs:
        origin=g*Q-(Q//2 if f else 0)
        if z[2] and not ((not f and g==A) or (f and g==A+4)):right.append(origin+Q-3)
        if z[3]:left.append(origin+3)
    return runs,sorted(right),sorted(left)
def main():
    T={g:old.native_output_table(g) for g in range(LO,HI)}
    V={g:old.native_output_table(g,True) for g in range(LO,HI)}
    log=[]
    for n in range(4,21):
        A=3*n+13
        runs,right,left=commands(T,V,n,A)
        expected=sorted([g*Q+Q//2-3 for g in range(A+1,A+4)]+[(g+1)*Q-3 for g in range(A+4,A+7)])
        core=[p for p in right if p>=A*Q]
        entry=dict(boundary_period=n,A=A,right_core=core,right_core_matches_six_RF_template=core==expected,
            left_sources=left,positive_Flag2_runs=[dict(receiver=g,foreign=f,output=z,bank=bank(T,V,g,f,A)) for g,f,z in runs if z[3]],
            true_native_window={str(g):T[g] for g in range(A-16,A+10)},
            foreign_native_window={str(g):V[g] for g in range(A-2,A+9)})
        log.append(entry)
        if left or core!=expected:break
        T,V=next_records(T,V,n,A)
    print(json.dumps(dict(discovery_only=True,physical_native_writeback_and_zero_special_Info_unproved=True,
        Q=Q,U=U,lambda24=24,c104=104,entries=log),indent=2))
if __name__=='__main__':main()
