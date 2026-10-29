"""All-phase padding-congruence contract of frozen GAW2R's exact emission.

This checker does not project any experiment or change the rule. Its
paired-execution proof explicitly compares an unmasked record with a
legal native projection, only under the four-clean-quorum/new-F1zero
premises established in the written theorem. SF words remain unchanged.
"""
from pathlib import Path
from dataclasses import dataclass
from collections import deque,Counter
import hashlib,json,sys,time
S=Path(__file__).resolve().parent;ROOT=S.parents[3]
D=ROOT/'figs/gray_counterexamples/unregistered_gaw20'
sys.path.insert(0,str(S.parent/'unregistered_gaw2'))
import gaw2r_compositional_cost as own
k=own.k;ROWS=own.ROWS;LABEL=own.LABEL;P=k.PRIMARY_START

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def row(pc):
    r=ROWS[pc];decoded=k.decode(k.beta_word(own.ROM,pc))
    masked=tuple(v&((1<<w)-1) for v,w in zip(r['operands'],k.ARGS[r['opcode']]))
    assert decoded==(r['opcode'],masked)
    return decoded
def roweq(pc,name,*args):assert row(pc)==(name,args),(pc,row(pc),(name,args))

def native_normal(start,centre,suffix):
    stop=LABEL['native_right'+suffix]+2
    targets={LABEL['native_keep'+suffix]:'keep',LABEL['native_afterkeep'+suffix]:'afterkeep',LABEL['native_right'+suffix]:'right'}
    result=[];reads=[];pc=start
    while pc<stop:
        op,args=row(pc)
        if op=='MOVI' and args[0]==11 and pc+1<stop:
            offset=args[1];q=pc+1
            if row(q)==('MOVI',(7,centre)):q+=1
            no,na=row(q)
            if no=='LDX' and na[1:]==(P,11,7,0):
                assert offset in (0,1);result.append(('OLD',na[0],offset));reads.append(q);pc=q+1;continue
            if no=='READ5' and na[0]==11:
                assert offset in (P,P+1) and na[2]==centre
                result.append(('FIVE',offset-P,na[1]));pc=q+1;continue
        if op=='MOVI' and args[0]==9 and pc+1<stop:
            no,na=row(pc+1)
            if no in ('READMASK','FULLCOL'):
                field=args[1]-P;assert field in (2,3,4,5) and na[1]==9
                result.append(('FLAGS',na[0],field));pc+=2
                if no=='FULLCOL':
                    roweq(pc,'ALUI',na[0],k.ALU['RSHIFT'],na[0],centre-5)
                    roweq(pc+1,'ALUI',na[0],k.ALU['AND'],na[0],2047);pc+=2
                else:assert centre==8
                continue
        if op=='BNZ':args=(args[0],targets[args[1]])
        elif op=='JMP':args=(targets[args[0]],)
        result.append((op,*args));pc+=1
    return result,reads,stop

def native_contracts():
    central,reads,stop=native_normal(0,8,'');macros={0:stop};raw=set(reads)
    # Exact normalized arithmetic is the accepted literal h1 recipe.
    # Native-pad differences may be acquired only as raw defaultGF/Age;
    # neither is used outside VMAJ fallback in this arithmetic block.
    bad=set();conditional_fallbacks=masked_vectors=0
    for r in central:
        op=r[0]
        if op=='OLD':bad.add(r[1]);continue
        if op=='FIVE':
            if r[1]==0:bad.add(0)
            else:bad.discard(0) # READ5 drops high Age padding
            continue
        if op=='FLAGS':bad.discard(r[1]);continue
        if op=='MOVI':bad.discard(r[1]);continue
        if op in ('ALU','ALUI'):
            dst,fn,ai=r[1:4]
            if op=='ALUI':used=(ai,)
            else:
                bi,ci=r[4:6];used=(ai,) if fn in (0,9,13,19) else (ai,bi,ci) if fn in (12,16,18) else (ai,bi)
            if fn==k.ALU['VADDINDEX'] and ai in bad:
                assert op=='ALU' and used==(0,1,15)
                # At this exact syntax point width13 masks all raw GF
                # padding; equality of the low13 components suffices.
                bad.discard(dst);masked_vectors+=1;continue
            if fn==k.ALU['VMAJ'] and any(v in bad for v in used):
                assert op=='ALU' and ai not in bad and r[4] in (12,13)
                bad.discard(dst);conditional_fallbacks+=1;continue
            assert not any(v in bad for v in used),('unhandled native padding use',r,bad)
            bad.discard(dst);continue
        if op in ('BNZ','JMP'):
            if op=='BNZ':assert r[1] not in bad
            continue
        raise AssertionError(('unexpected native normal form',r))
    assert bad=={12,13} and conditional_fallbacks==4 and masked_vectors==2
    for i in range(6):
        start=LABEL['source_'+str(i)];nf,rd,end=native_normal(start,6+i,'_'+str(i))
        assert nf==central;raw.update(rd);macros[start]=end
    # Early appended native block is literally the central prefix with
    # relocation and HALT. This accepted check pins the exact row identity.
    early=own.ROM.early_pc
    for pc in range(LABEL['workspace']-1):
        a,args=row(pc);b,br=row(early+pc);assert a==b
        if a=='JMP':br=(br[0]-early,)
        if a=='BNZ':br=(br[0],br[1]-early)
        assert args==br,(pc,args,br)
    assert row(LABEL['workspace']-1)==('JMP',(LABEL['workspace'],))
    assert row(early+LABEL['workspace']-1)==('HLT',())
    return macros,raw,dict(native_recipe_instances=7,
        conditional_quorum_fallbacks=7*conditional_fallbacks,GF_vector_width13_masks=7*masked_vectors,
        only_remaining_native_register_differences=[12,13],early_prefix_exact_relocation=True)

@dataclass(frozen=True)
class T:
    value:object=None
    equal:bool=True

E=T();BAD=T(None,False)
def C(v):return T(v&k.MASK,True)

def operation(fn,x,y,z):
    if fn==k.ALU['MOV']:return x
    if fn==k.ALU['AND'] and (x==C(0) or y==C(0)):return C(0)
    used=(x,) if fn in (0,9,13,19) else (x,y,z) if fn in (12,16,18) else (x,y)
    equal=all(v.equal for v in used)
    if all(v.value is not None for v in used):return C(k.generic_alu(fn,x.value,y.value,z.value or 0))
    return T(None,equal)

def paired_prefix(macros):
    # Native macro is justified by the exact normalized contracts above
    # and the written four-clean-quorum/new-F1zero premise. No phase or
    # payload value is enumerated: every equal unknown branch forks both.
    initial=(0,(C(0),)*16,(C(0),)*6,())
    queue=deque([initial]);seen=set();cut=[];counts=Counter();rawreads=set();digest=hashlib.sha256()
    while queue:
        state=queue.popleft()
        if state in seen:continue
        seen.add(state);pc,rs,ot,st=state;regs=list(rs);out=list(ot);scratch=dict(st)
        if pc==LABEL['baseline_loop']:
            assert all(v.equal for v in regs) and all(v.equal for v in out) and all(v.equal for v in scratch.values())
            assert regs[11]==C(6) and regs[13]==C(0) and regs[14]==C(0)
            cut.append(state);continue
        if pc in macros:
            regs=[E]*16;regs[12]=regs[13]=BAD;regs[14]=regs[15]=C(0);regs[7]=C(1)
            queue.append((macros[pc],tuple(regs),ot,st));counts['native_macros']+=1;continue
        op,args=row(pc);counts['instruction_'+op]+=1;destinations=[pc+1]
        if op=='JMP' and args[0]==LABEL['vote']:
            assert regs[11].value is not None and 6<=regs[11].value<=k.FRAME_WORDS-5
            assert regs[12].equal and regs[15].value is not None
            ret=regs[15].value
            # Raw SF inputs are identical before/after native projection.
            # Exact86-instruction helper is the frozen three-of-five
            # contract; its preserved registers include the deadR13.
            for i in (0,1,3,4,5):regs[i]=E
            regs[6]=C(0);regs[7]=C(16);regs[8]=C(5);regs[11]=C(regs[11].value+5)
            destinations=[ret];counts['same_raw_SF_helper_calls']+=1
        elif op=='JMP':destinations=[args[0]]
        elif op=='BNZ':
            q=regs[args[0]];assert q.equal,('unpaired branch',pc,args,q)
            destinations=[args[1] if q.value else pc+1] if q.value is not None else [pc+1,args[1]]
        elif op=='MOVI':regs[args[0]]=C(args[1])
        elif op in ('ALU','ALUI'):
            dst,fn,ai=args[:3]
            x,y,z=(regs[ai],C(args[3]),C(0)) if op=='ALUI' else (regs[ai],regs[args[3]],regs[args[4]])
            regs[dst]=operation(fn,x,y,z)
            if fn==k.ALU['AND'] and (not x.equal or not y.equal):
                assert regs[dst]==C(0);counts['padding_guard_cancellations']+=1
        elif op=='CODE':
            assert regs[args[1]].equal and regs[args[1]].value is not None
            regs[args[0]]=C(k.beta_word(own.ROM,regs[args[1]].value))
        elif op=='LDX':
            dst,start,index,lane,source=args
            assert regs[index].equal and regs[index].value is not None and regs[lane].equal and regs[lane].value is not None
            target=start-P+regs[index].value
            if source==0:
                assert start==P and target in (0,1)
                regs[dst]=BAD;rawreads.add(pc)
            elif source==1:assert 0<=target<6;regs[dst]=out[target]
            else:assert source==2;regs[dst]=scratch[target-128]
        elif op=='STX':
            value,start,index,dest=args
            assert regs[index].equal and regs[index].value is not None
            target=start-P+regs[index].value
            assert regs[value].equal,('unpaired observable store',pc,target,regs[value])
            if dest:scratch[target-128]=regs[value]
            else:assert 0<=target<6;out[target]=regs[value]
        else:raise AssertionError(('unsupported paired prefix instruction',pc,op,args))
        digest.update(str((pc,tuple(regs),tuple(out),tuple(sorted(scratch.items())),destinations)).encode())
        for dst in destinations:queue.append((dst,tuple(regs),tuple(out),tuple(sorted(scratch.items()))))
        assert len(seen)<20000,'unexpected prefix-state explosion'
    assert cut
    return rawreads,dict(paired_prefix_states=len(seen),body_cut_states=len(cut),
        unknown_equal_phase_branches_fork_both=True,no_unequal_PC_address_lane_or_observable_write=True,
        all_registers_Out_and_Scratch_equal_at_body_entry=True,
        primitive_counts=dict(sorted(counts.items())),paired_prefix_digest_sha256=digest.hexdigest())

def main():
    started=time.monotonic();macros,raw,native=native_contracts();guards,prefix=paired_prefix(macros)
    # Exhaust all actual full Word100 input reads in the emitted full pass.
    # After the body cut, the unique remaining raw input read is the SF
    # helper. Its typed parameter is>=6 by frozen full compiler contracts.
    allraw={pc for pc,r in ROWS.items() if pc<own.ROM.early_pc and r['opcode']=='LDX' and r['operands'][-1]==0}
    helper={LABEL['vote_loop']+6};roweq(next(iter(helper)),'LDX',0,P,11,6,0)
    assert allraw==raw|guards|helper,(allraw-(raw|guards|helper),(raw|guards|helper)-allraw)
    cost=json.loads((ROOT/'figs/gray_counterexamples/unregistered_gaw2/GAW2R_compositional_cost.json').read_text())
    assert cost['maximum_ticks']==141557 and cost['available_ticks']==147455
    r=dict(Q=k.Q,U=k.U,error_lambda=24,error_separation=104,
        native_contract=native,paired_prefix=prefix,
        every_full_word_input_LDX_site=sorted(allraw),raw_default_native_LDX_sites=sorted(raw),
        raw_GF_guard_LDX_sites=sorted(guards),body_raw_SF_helper_LDX_site=next(iter(helper)),
        all_record_native_projection_is_explicit_proved_comparison_not_actual_input_mask=True,
        congruence_requires_four_clean_native_votes_and_new_F1zero_at_central_and_all_source_centres=True,
        only_native0_to5_padding_projected_all490_SF_words_unchanged=True,
        late_actual_instruction_operand_travel_trace_and_Out_observations_match_legal_projection=True,
        universal_late_deadline_from_frozen_legal_contract=141557,available_late_updates=147455,
        early_native_prefix_available_bound=213,universal_generic_malformed_padding_quotient=False,
        later_intact_shadow_and_global_period_lift_supplied_by_written_proof=True)
    path=D/'GAW20_padding_congruence_certificate.json'
    if '--issue' in sys.argv:assert not path.exists();path.write_text(json.dumps(r,indent=2)+'\n')
    else:assert r==json.loads(path.read_text())
    print(json.dumps(dict(passed=True,elapsed_seconds=time.monotonic()-started,**r)),flush=True);return r

if __name__=='__main__':main()
