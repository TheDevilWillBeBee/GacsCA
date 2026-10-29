#!/usr/bin/env python3
"""Conditional GR1 front execution and tracked-field forwarding certificates.

The certificates prove local frame/route implications, not a noisy or
continuing encoded-period lift. Decoder/ALU semantics are the existing
fixed interpreter; the new proof is that all physical holders read the
same corrected operands and produce the required stores and carried regs.
"""
from pathlib import Path
import hashlib,json,sys,time
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT)); sys.path.insert(0,str(ROOT/'Report/proofs'))
from gacsca import rule_g
from gacsca.netlist import Net,const_word,w_eq_const,w_add_const,w_in_range
from check_g17_schedule import Terms
import gray_staged_rule as proposed
import gray_staged_transport as staged


def digest(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def front_certificate(p):
    classes={}; visits=0
    for page in range(p.NP):
        if page==p.MP: continue
        for tick in range(p.PL):
            step=tick if page%2==0 else p.PL-1-tick
            for front in range(p.fronts):
                center=p.lo-p.H+step+front*p.delta
                previous=center if tick==0 else center+(-1 if page%2==0 else 1)
                assert center-2>=0 and center+2<p.Q
                if tick==0 and page:
                    prior_step=(p.PL-1 if (page-1)%2==0 else 0)
                    prior=p.lo-p.H+prior_step+front*p.delta
                    assert prior==center
                for holder in rule_g.SLOTS:
                    key=(page==0 and tick==0,tick==0,page%2,p.lo<=center<p.hi,front,holder)
                    classes.setdefault(key,(page,tick,front,holder,center,previous))
                visits+=1
    count=0
    for key,(page,tick,front,holder,center,previous) in classes.items():
        first,turn,direction,inside,_,_=key
        n=Net(); R=[n.input(('R',b)) for b in range(p.L)]
        I=[n.input(('I',b)) for b in range(p.IW)]
        cache={}
        def lv(x,f,b=0):
            absolute=center+holder+x
            if f=='reg' and absolute==previous: return R[b]
            name=absolute,f,b
            if name not in cache: cache[name]=n.input(('other',)+name)
            return cache[name]
        actual=rule_g._five_front(n,p,I,lv,
            const_word(p.E0+page*p.PL+tick,p.m),const_word(center+holder,p.k))
        d=-holder; rsrc=[0]*p.L if first else R
        lanes=[lv(d,'info'),lv(d,'hold')]+[lv(d,'h1',b) for b in range(10)]+[
            lv(d,'scr',b) for b in range(p.S)]
        sources=rsrc+lanes+[0,1]
        op=rule_g._decoder(n,I[:2],4)
        kinds=rule_g._decoder(n,I[2:4],4)
        if not inside: kinds=[0]*4
        a=rule_g._decoder(n,I[4:4+p.SB],len(sources))
        b=rule_g._decoder(n,I[4+p.SB:4+2*p.SB],len(sources))
        dest=I[4+2*p.SB:p.IW]
        destinations=rule_g._decoder(n,dest,p.L)
        A=n.any(n.AND(s,v) for s,v in zip(a,sources))
        B=n.any(n.AND(s,v) for s,v in zip(b,sources))
        alu=n.any((n.AND(op[rule_g.AND],n.AND(A,B)),n.AND(op[rule_g.OR],n.OR(A,B)),
                   n.AND(op[rule_g.XOR],n.XOR(A,B)),n.AND(op[rule_g.ANDN],n.ANDN(A,B))))
        expected_reg=[n.MUX(n.AND(kinds[rule_g.K_REG],destinations[j]),alu,rsrc[j])
                      for j in range(p.L)]
        in_scr=n.AND(kinds[rule_g.K_SCR],w_in_range(n,dest,0,p.S))
        pend=n.OR(kinds[rule_g.K_HOLD],in_scr)
        pkind=[n.MUX(in_scr,bit,0) for bit in
               w_add_const(n,dest[:2]+[0]*(p.PK-2),p.NH)[:p.PK]]
        expected=dict(reg=expected_reg,pend=[pend if slot==d else 0 for slot in staged.SLOTS],
            pkind=[bit if slot==d else 0 for slot in staged.SLOTS for bit in pkind],
            pval=[n.AND(pend,alu) if slot==d else 0 for slot in staged.SLOTS])
        for f in expected:
            assert actual[f]==expected[f],(key,f)
            count+=len(actual[f])
        assert [n.outputs['laddr',j] for j in range(p.k)]==const_word(center,p.k)
        selector=page+(front<<p.logNP)
        assert [n.outputs['psel',j] for j in range(p.PW)]==const_word(selector,p.PW)
        assert n.outputs['arrive',0]==1
        count+=p.k+p.PW+1
    return dict(nonmatch_visits_classified=visits,semantic_classes=len(classes),
        exact_output_and_lookup_equalities=count,
        classification_fields=['first-pass start','page turn','direction','inside work rows','front index','holder offset'],
        symbolic_register_bits_per_class=p.L,symbolic_instruction_bits_per_class=p.IW,
        nonmatch_front_route_proved_conditionally=True,
        proof_scope='Every nonmatch visit and copy holder belongs to a checked class. Absolute page affects only the known selector bits, not the data equation. The exact checks certify carry/start reset, selection of the corrected logical operands, instruction effect, and coherent pending target/value. Nonarriving slots have zero outputs by the arrive gates.',
        uses_existing_decoder_and_ALU_definition=True,
        complete_noisy_front_or_period_proved=False)


def evaluate_net(n,terms,input_value):
    value=[]
    for node,kind in enumerate(n.kind):
        if node<2: value.append(node)
        elif kind=='IN':
            value.append(input_value(next(name for name,index in n.input_node.items() if index==node)))
        else:
            op,a,b=n.gate[node]; value.append(terms.op(op,value[a],value[b]))
    return value


def forwarding_certificate(p,comp):
    equalities=0; cases=[]
    for phase in staged.address_boundaries()[:-1]:
        terms=Terms(); clock=[terms.var(('common_raw_age',b)) for b in range(p.m)]
        logical=lambda f,x,b=0:terms.var(('logical',f,x,b))
        def actual_input(name):
            if name[0]=='I': return terms.var(name)
            _,x,f,b=name
            if f=='addr': return ((phase+x)%p.Q>>b)&1
            if f=='age': return clock[b]
            if f in ('f1','f2','wf1','wf2'): return terms.var(('native_flag',x,f))
            if f=='reg': return terms.var(('raw_reg',x,b))
            w=proposed.logical_width(f,p); slot,bit=divmod(b,w)
            return logical(f,x+slot-2,bit)
        node=[0,1]+[actual_input(name) for name in comp.inputs]
        for op,a,b in comp.gates: node.append(terms.op(op,node[a],node[b]))
        actual={name:node[index] for name,index in comp.outputs.items()}
        # The already certified native canonical/common-geometry lemma is
        # used explicitly, with all 44 flags arbitrary, not WF=0.
        assert [actual['y','addr',b] for b in range(p.k)]==const_word(phase,p.k)
        n=Net(); raw_clock=[n.input(('clock',b)) for b in range(p.m)]
        computed_age=w_add_const(n,raw_clock,1)
        data={}
        def raw(f,x,b=0):
            key=f,x,b
            if key not in data: data[key]=n.input(('logical',)+key)
            return data[key]
        def forwarded(f,x,b=0):
            target=0 if f=='hold' else b+1
            hit=n.AND(raw('pend',x),w_eq_const(n,[raw('pkind',x,j) for j in range(p.PK)],target))
            return n.MUX(hit,raw('pval',x),raw(f,x,b))
        cells={x:{f:[forwarded(f,x+slot,b) if f in ('hold','scr') else raw(f,x+slot,b)
                         for slot in staged.SLOTS for b in range(w)]
                     for f,w in staged.FIELDS} for x in range(-5,6)}
        native_f1=n.input(('computed_f1',))
        expected=staged.build(n,cells,const_word(phase,p.k),computed_age,native_f1,0)
        def expected_input(name):
            if name[0]=='clock': return clock[name[1]]
            if name[0]=='computed_f1': return actual['y','f1',0]
            return logical(name[1],name[2],name[3])
        val=evaluate_net(n,terms,expected_input)
        assert [actual['y','age',b] for b in range(p.m)]==[val[b] for b in computed_age]
        for f,w in staged.FIELDS:
            for slot in staged.SLOTS:
                for b in range(w):
                    assert actual['y',f,(slot+2)*w+b]==val[expected[f,slot,b]],(phase,f,slot,b)
                    equalities+=1
        cases.append(dict(phase=phase,symbolic_common_clock_bits=p.m,
                          independent_native_flag_bits=44,tracked_equalities=260))
    return dict(address_route_classes=len(cases),whole_clock_words_symbolic=True,
        exact_tracked_coupling_equalities=equalities,cases=cases,
        coherent_pending_forwarding_and_selective_reset_coupling_proved=True,
        canonical_native_geometry_lemma_reused=True,input_workspace_flags_arbitrary=True,
        native_geometry_receipt_sha256=digest(ROOT/'figs/gray_counterexamples/native_geometry_invariant_certificate.json'),
        proof_scope='Every tracked GR1 physical output equals the certified primitive applied to coherent logical data, with Hold/scratch reads forwarding the current coherent pending store. Native GF remains canonical, native Age is the common raw Age+1 and wipe is zero, even with arbitrary native/Workspace flags. The partition covers every Address branch; all clocks are free simultaneously.',
        input_premise='The compared raw tracked fields and pending fields have five coherent copies. This local implication does not prove that fresh noise, arbitrary initial private fields, or successive interpreter steps preserve those premises.',
        physical_E0_lift_or_continuing_period_proved=False)


def main():
    start=time.monotonic(); candidate=proposed.load_artifact(); p=candidate.p
    route=front_certificate(p); print(json.dumps(route),flush=True)
    forwarding=forwarding_certificate(p,candidate.comp)
    receipt=dict(candidate='GR1',Q=p.Q,U=p.U,candidate_sha256=candidate.digest(),
        netlist_sha256=candidate.comp.digest,front_route=route,tracked_coupling=forwarding,
        checker_sha256=digest(__file__),proposal_sha256=digest(proposed.__file__),
        transport_primitive_sha256=digest(staged.__file__),
        inherited_rule_sha256=digest(ROOT/'gacsca/rule_g.py'),
        inherited_timing_sha256=digest(ROOT/'gacsca/rule.py'),
        term_library_sha256=digest(ROOT/'Report/proofs/check_g17_schedule.py'),
        primitive_receipt_sha256=digest(ROOT/'figs/gray_counterexamples/gray_staged_transport_certificate.json'),
        build_receipt_sha256=digest(ROOT/'figs/gray_counterexamples/GR1_program_build.json'),
        measured_only=False,gray_verbatim_simulation=False,
        physical_self_simulation_proved=False,full_physical_E0_lift_proved=False,
        global_reliability_established=False,elapsed_seconds=time.monotonic()-start)
    (ROOT/'figs/gray_counterexamples/GR1_frame_certificate.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(dict(semantic_classes=route['semantic_classes'],
        front_equalities=route['exact_output_and_lookup_equalities'],
        tracked_coupling_equalities=forwarding['exact_tracked_coupling_equalities'],
        elapsed_seconds=receipt['elapsed_seconds'])),flush=True)


if __name__=='__main__': main()
