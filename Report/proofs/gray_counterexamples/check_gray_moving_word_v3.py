#!/usr/bin/env python3
"""Finite replays of proposed full GMW3 emission and actual timing model.

Universal beta equivalence, all-input timing and Gray refinement remain open.
Compared outputs use the closed radius5 kernel, never a whole-rule syscall
in emitted code. Failures retain exact source snapshots and input bits.
"""
from pathlib import Path
from dataclasses import replace
import hashlib,json,random,sys,time
import numpy as np
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT))
import gray_moving_word_v3 as k
import build_gray_moving_word_v3 as builder
import check_gray_moving_word_v2 as old_checker


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    started=time.monotonic();directory=ROOT/'figs/gray_counterexamples'
    code,listing,labels,errors=builder.programme().assemble()
    assert not errors and len(code)<=65536
    beta=tuple(code+[0]*(65536-len(code)))
    choices={r['opcode']:r for r in listing};rng=random.Random(17179)
    fixtures=[('canonical_rest',old_checker.fixture()),('native_wrap',old_checker.fixture(commonage=k.U-1)),
        ('native_birth',old_checker.fixture(commonage=112*k.Q))]
    for mode in (k.RUN,k.SEEK,k.LOAD,k.WRITE,k.HALT,k.ERROR,6,7):
        packet=k.Packet(p=1,mode=mode,start=3,width=7,index=1,kind=1,lane=5,
            pc=choices['HLT']['address'],regs=tuple(rng.randrange(1<<20) for _ in range(16)))
        for move in (0,1,2,3):
            for age in (112*k.Q+1,112*k.Q+2):
                fixtures.append(('mode%d_move%d_age%d'%(mode,move,age),
                    old_checker.fixture(replace(packet,move=move),age,memory_seed=731)))
    for name in ('HLT','MAJ','WINCNT','ALU','MI5'):
        row=choices[name];p=k.Packet(p=1,pc=row['address'])
        cells=old_checker.fixture(p,112*k.Q+1,memory_seed=87)
        fixtures.append(('all_heads_'+name,{j:replace(c,heads=(k.pack(p),)*5) for j,c in cells.items()}))
    # Isolated source SEEKs at each candidate distance; every clipped-vote
    # field is exercised on legal and deliberately inconsistent copies.
    for position in range(-3,4):
        for move in (1,2):
            p=k.Packet(p=1,move=move,mode=k.SEEK,start=200 if move==1 else 0,width=1,index=0,kind=1,lane=5)
            fixtures.append(('source%d_move%d'%(position,move),
                old_checker.fixture(p,112*k.Q+2,head_position=position,memory_seed=291)))
    inputs=[];outputs=[];ticks=[];names=[]
    for name,cells in fixtures:
        out,n,p,_=k.execute(beta,k.input_tape(cells),400000)
        actual=[out.get(k.PRIMARY_START+i,0) for i in range(k.FRAME_BITS)]
        expected=k.cell_bits(k.local_transition(cells,beta))
        if p.mode!=k.HALT or actual!=expected:
            serial=1
            while (directory/('GMW3_emission_failure_%02d.json'%serial)).exists():serial+=1
            stem='GMW3_emission_failure_%02d'%serial
            asset=directory/(stem+'.npz')
            np.savez_compressed(asset,input_bits=np.array([k.cell_bits(cells[j]) for j in range(-5,6)],np.uint8),
                actual=np.array(actual,np.uint8),expected=np.array(expected,np.uint8),beta=np.array(beta,np.uint8))
            sources={}
            for path in (Path(k.__file__),Path(builder.__file__),Path(__file__)):
                saved=directory/(stem+'_'+path.name+'.txt');saved.write_bytes(path.read_bytes());sources[saved.name]=digest(saved)
            row=dict(name=name,measured_ticks=n,last_mode=p.mode,last_pc=p.pc,
                different_field_bits=np.flatnonzero(np.array(actual)!=np.array(expected)).tolist(),
                programme_bits=len(code),source_snapshots_sha256=sources,asset_sha256=digest(asset),
                universal_beta_equivalence_proved=False,Gray_or_iid_failure_proved=False,active_rule_modified=False)
            (directory/(stem+'.json')).write_text(json.dumps(row,indent=2)+'\n')
            raise AssertionError(stem+' '+name+' '+str(row['different_field_bits'][:12]))
        print(name,n,flush=True);inputs.append([k.cell_bits(cells[j]) for j in range(-5,6)])
        outputs.append(actual);ticks.append(n);names.append(name)
    bpath=directory/'GMW3_full_proposed_beta.bin';bpath.write_bytes(np.packbits(np.array(beta,np.uint8),bitorder='little').tobytes())
    lpath=directory/'GMW3_full_proposed_listing.json';lpath.write_text(json.dumps(dict(code_capacity=65536,
        programme_bits=len(code),instructions=listing,labels=labels,errors=errors),indent=2)+'\n')
    asset=directory/'GMW3_full_proposed_replays.npz';np.savez_compressed(asset,input_bits=np.array(inputs,np.uint8),
        outputs=np.array(outputs,np.uint8),ticks=np.array(ticks,np.uint32),names=np.array(names))
    row=dict(name='GMW3 full proposed emission; changed alternating fast/one-site transport',Q=k.Q,U=k.U,
        lambda_original=24,c_original=104,frame_bits=k.FRAME_BITS,rest_period=2,
        programme_bits=len(code),instructions=len(listing),out_of_range_references=len(errors),
        immutable_ROM_bits=65536,finite_whole_field_replays=len(fixtures),replays_measured_only=True,
        replay_names=names,measured_ticks=ticks,baseline_usable_active_ticks=65535,
        canonical_complete_ticks=ticks[0],canonical_halts_within_active_budget=ticks[0]<=65535,
        actual_128Q_schedule_changed=False,shorter_U_used=False,
        universal_full_beta_identity_proved=False,universal_runtime_bound_proved=False,
        physical_gather_early_flags_special_write_whole_period_completed=False,
        Gray_faithful=False,intact_iid_failure_proved=False,global_reliability_established=False,
        kernel_sha256=digest(k.__file__),builder_sha256=digest(builder.__file__),checker_sha256=digest(__file__),
        beta_sha256=digest(bpath),listing_sha256=digest(lpath),asset_sha256=digest(asset),
        base_GMW2_kernel_sha256=digest(k.base.__file__),base_GMW2_builder_sha256=digest(builder.previous.__file__),
        wall_seconds=time.monotonic()-started)
    (directory/'GMW3_full_proposed_certificate.json').write_text(json.dumps(row,indent=2)+'\n')
    print(json.dumps(row))


if __name__=='__main__':main()
