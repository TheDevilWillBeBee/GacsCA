"""Mixed-native/all-mutable-SF cofactor and selected actual-history audit."""
from pathlib import Path
import ctypes,hashlib,json,random,sys,time
S=Path(__file__).resolve().parent;sys.path.insert(0,str(S))
import check_gaw14_active_factor as active
import continue_gaw14_boundaries as boundary
k=active.k;own=active.own;base=active.base;D=active.D;source=active.source

def mixed_cofactors(count=256):
    rng=random.Random(0xa1410424);c=active.library();n=81;centre=40;digest=hashlib.sha256();fields=0;nonwipe=0;store=0
    beta=(ctypes.c_uint8*k.Q)(*[k.beta_bit(own.ROM,x) for x in range(k.Q)])
    for trial in range(count):
        a=(active.Site*n)(*[active.Site((x-centre)%k.Q,active.T,0,0,0,0,31) for x in range(n)])
        b=(active.Site*n)();pb=(ctypes.c_uint8*n)(*[sum(beta[(x-centre+s)%k.Q]<<h for h,s in enumerate(k.SLOTS)) for x in range(n)])
        np=(ctypes.c_uint8*n)();wipe=(ctypes.c_int*n)();r=active.Result()
        W={y:rng.getrandbits(1700) for y in range(-10,11)};I={y:rng.getrandbits(100) for y in range(-10,11)}
        cells={};coherent_heads={}
        for y in range(-10,11):
            coherent_heads[y]=k.pack(k.Packet(p=1,mode=k.SEEK,pc=own.ROM.token_count,target=y%k.Q,
                args=k.descriptor(1,0,dest=trial&1),regs=(rng.getrandbits(100),)+(0,)*15))
        for d in range(-8,9):
            gf=d%k.Q if trial%4==0 else ((d+k.Q//2)%k.Q if d else 0) if trial%4==1 else rng.randrange(k.Q)
            age=active.T+rng.randrange(-32,33);flags=rng.randrange(16);tag=rng.randrange(32)
            a[centre+d]=active.Site(gf,age,flags&1,(flags>>1)&1,(flags>>2)&1,(flags>>3)&1,tag)
            pb[centre+d]=rng.randrange(32)
            heads=[]
            for h in range(5):
                if trial%4<2:heads.append(coherent_heads[d+k.SLOTS[h]])
                elif (trial+h)%3==0:heads.append(rng.getrandbits(k.HEAD_BITS))
                else:heads.append(k.pack(k.Packet(p=rng.randrange(2),move=rng.randrange(4),mode=rng.randrange(5),
                    pc=rng.choice((0,own.ROM.token_count,k.Q-1,k.Q)),target=rng.randrange(k.Q+1),
                    args=rng.getrandbits(100),regs=tuple(rng.getrandbits(100) for q in range(16)))))
            mem=tuple(W[d+s]*((tag>>h)&1) for h,s in enumerate(k.SLOTS))
            cells[d]=k.Cell(addr=gf,age=age,f1=flags&1,f2=(flags>>1)&1,wf1=(flags>>2)&1,wf2=(flags>>3)&1,
                heads=tuple(heads),out=tuple(rng.getrandbits(100) for h in range(5)),
                scratch=tuple(rng.getrandbits(100) for h in range(5)),mem=mem,history1=mem,history2=mem,history3=mem,
                info=tuple(I[d+s]*((tag>>h)&1) for h,s in enumerate(k.SLOTS)),
                program=tuple((pb[centre+d]>>h)&1 for h in range(5)))
        assert c.gaw14_step(a,b,pb,np,beta,n,-centre,active.T+1,wipe,ctypes.byref(r))==0
        direct=k.local_transition(cells,own.ROM);z=b[centre]
        assert (z.gf,z.age,z.f1,z.f2,z.w1,z.w2)==(direct.addr,direct.age,direct.f1,direct.f2,direct.wf1,direct.wf2)
        for h,s in enumerate(k.SLOTS):
            tag=(z.info>>h)&1
            assert all(getattr(direct,name)[h]==W[s]*tag for name in ('mem','history1','history2','history3'))
            assert direct.info[h]==I[s]*tag and direct.program[h]==((np[centre]>>h)&1)
            incoming=k.incoming([k.unpack(k.logical(cells,'heads',s+j)) for j in (-1,0,1)])
            mem=k.logical(cells,'mem',s);out=k.logical(cells,'out',s);scratch=k.logical(cells,'scratch',s);program=k.logical(cells,'program',s)
            p,ow,sw=k.step_packet(incoming,(z.gf+s)%k.Q,mem,out,scratch,program,own.ROM)
            if z.f1 and z.gf!=cells[0].addr:p=k.ZERO;out=scratch=0
            else:
                nonwipe+=1;store+=int(ow is not None or sw is not None)
                out=out if ow is None else ow;scratch=scratch if sw is None else sw
            assert (direct.heads[h],direct.out[h],direct.scratch[h])==(k.pack(p),out,scratch)
            fields+=13
        digest.update(json.dumps([k.cell_words(direct),r.row_hash],separators=(',',':')).encode())
    return dict(actual_full_local_R_mixed_native_arbitrary_mutable_SF_cofactors=count,
        holder_field_assignments=fields,nonwipe_holder_cases=nonwipe,actual_store_holder_cases=store,signature_sha256=digest.hexdigest(),
        native_GF_and_all_flags_free_legal_clock_window=True,
        readonly_shared_coefficient_and_boolean_programme_premises=True,
        samples_supplement_algebraic_factor_not_universal_sampling=True)

def describe(prefix,output):
    ys=prefix['closure']['readonly_erased_coordinates']
    nonzero=[y for y in ys if active.prior.B(y)]
    info=[y for y in ys if base.I(y)]
    offsets={}
    for y in nonzero:
        g,a=divmod(y,k.Q)
        if active.P<=a<active.P+k.FRAME_WORDS:offsets.setdefault(str(g),[]).append(a-active.P)
    event_count=len(prefix['events']);rows=prefix.get('actual_full_local_R_prefix_rows',0)+event_count
    bad=output['actual_U_and2U']['actual_U_bad_normal_receivers']
    actual=output['actual_U_and2U']['actual_U_normal_raw_records']
    diffs={}
    for g in bad:
        words=[int(v,16) for v in actual[str(g)]];shadow=k.cell_words(base.nextH(g))
        diffs[str(g)]=[[i,hex(a),hex(b)] for i,(a,b) in enumerate(zip(words,shadow)) if a!=b]
    return dict(tag=prefix['recipe']['tag'],GF_shift=prefix['recipe']['gf_shift'],
        overwritten_Age=prefix['recipe']['age'],true_Age=active.T,flags=prefix['recipe']['flags'],
        fault_support=[prefix['recipe']['start'],prefix['recipe']['start']+16],
        complete_native_SF_closure_elapsed=rows,
        first_geometry_quiet=prefix['first_geometry_quiet'],first_native_quiet=prefix['first_native_quiet'],
        erased_keep_tag_count=len(ys),erased_keep_tag_hull=None if not ys else [min(ys),max(ys)+1],
        actual_nonzero_readonly_bank_disagreement_coordinates=nonzero,
        actual_nonzero_Info_disagreement_coordinates=info,
        actual_normal_bank_disagreement_offsets=offsets,
        surviving_nonshadow_Head_groups=[y for y,v in prefix['closure']['Head'] if y//k.Q in (0,1)],
        actual_U_bad_normal_records=bad,actual_U_normal_word_differences=diffs,
        permitted_fixed_adjacent_pair=output['actual_U_and2U']['fixed_adjacent_pair_covers'],
        native_padding_legal_at_U=output['actual_U_and2U']['U_native_padding_legal'],
        complete_actual2U_shadow=output['actual_U_and2U']['complete2U_shadow'],
        actual_raw_U_commit_and_reset_checks=output['actual_U_and2U']['actual_raw_U_commit_and_reset_local_R_checks'])

def main(write=True,replay_histories=False):
    started=time.monotonic();cofactors=mixed_cofactors();cases=[]
    for recipe in active.recipes()+source.recipes()[1:3]:
        prefix_path=D/(recipe['tag']+'_active_receipt.json');out_path=D/(recipe['tag']+'_boundary_receipt.json')
        prefix=json.loads(prefix_path.read_text());output=json.loads(out_path.read_text())
        if replay_histories:
            if recipe['tag'].startswith('active_'):got,_=active.run(recipe)
            else:
                initial,_,_=source.run(recipe,limit=32)
                old=json.loads((D/(recipe['tag']+'_prefix.json')).read_text())
                assert source.stable(initial)==source.stable(old)
                got,_=active.run_seeded(initial)
            assert source.stable(got)==source.stable(prefix)
            computed=boundary.run(prefix);assert source.stable(computed)==source.stable(output)
        case=describe(prefix,output)
        assert case['native_padding_legal_at_U'] and case['complete_actual2U_shadow'] and case['permitted_fixed_adjacent_pair']
        cases.append(case)
    snapshots={g:active.prior.actual_snapshot(g) for g in (-2,-1,0,1,2)}
    chronology=active.prior.actual_chronological_prefix_checks(snapshots)
    result=dict(name='GAW14 selected actual mixed-native/interpreter original real1 histories',Q=k.Q,U=k.U,
        error_lambda=24,error_separation=104,actual_intact_H_shared_history=True,
        mixed_native_SF_factor=cofactors,chronological_T_prefix=chronology,cases=cases,
        all_ten_actual_U_records_legal_and_adjacent_pair=True,all_ten_complete2U_shadow=True,
        universal_mixed_native_SF_repair=False,Gray_operational_iid_or_shorter_U_failure=False,
        zero_keep_tags_not_counts_of_nonzero_word_errors=True,
        active_rule_or_registered_main_modified=False,elapsed_seconds=time.monotonic()-started)
    target=D/'GAW14_mixed_active_certificate.json'
    if write:target.write_text(json.dumps(result,indent=2)+'\n')
    else:assert source.stable(result)==source.stable(json.loads(target.read_text()))
    print(json.dumps(dict(passed=True,selected_actual_histories=10,mixed_full_local_R_cofactors=256,
        chronology_checks=chronology['actual_last_chronological_prefix_full_local_R_checks'],
        all2Ushadow=True,operational_Gray_iid_failure=False,elapsed_seconds=time.monotonic()-started)),flush=True)
    return result

if __name__=='__main__':main()
