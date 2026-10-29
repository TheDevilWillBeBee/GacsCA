#!/usr/bin/env python3
"""Emit and certify the GFD0 binary stage-three component, not an own rule."""
from pathlib import Path
from itertools import product, combinations
import argparse, ctypes, hashlib, json, subprocess, sys, time
ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np
from gacsca.netlist import Net, Compiled, const_word, at_least
import gray_binary_flag_delivery as p


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def emit(comp, out, stem):
    graph = out / (stem + '.json')
    graph.write_text(json.dumps(dict(inputs=comp.inputs, gates=comp.gates,
        outputs=list(comp.outputs.items()), digest=comp.digest), separators=(',', ':')) + '\n')
    code = ['#include <stdint.h>', '#include <stddef.h>',
            f'static const uint32_t gates[{max(1, len(comp.gates))}][3] = {{']
    code.extend('  {' + ','.join(map(str, gate)) + '},' for gate in comp.gates)
    code += ['};', f'static const uint32_t out_nodes[{len(comp.outputs)}] = {{' +
             ','.join(str(v) for v in comp.outputs.values()) + '};',
             'void gfd0_transition(const uint8_t *input, uint8_t *output) {',
             f'  uint8_t v[{comp.n_nodes}]; v[0]=0; v[1]=1;',
             f'  for(size_t i=0;i<{len(comp.inputs)};i++) v[i+2]=input[i]&1;',
             f'  for(size_t i=0;i<{len(comp.gates)};i++) {{',
             '    uint32_t op=gates[i][0],a=gates[i][1],b=gates[i][2];',
             f'    v[{2+len(comp.inputs)}+i]=op==0?(v[a]&v[b]):op==1?(v[a]|v[b]):(v[a]^v[b]);',
             '  }', f'  for(size_t i=0;i<{len(comp.outputs)};i++) output[i]=v[out_nodes[i]];', '}']
    source = out / (stem + '.c')
    source.write_text('\n'.join(code) + '\n')
    # Every C table row is the same topologically earlier two-input gate.
    for i, (op, a, b) in enumerate(comp.gates, 2 + len(comp.inputs)):
        assert op in (0, 1, 2) and 0 <= a < i and 0 <= b < i
    assert len(comp.outputs) == len(set(comp.outputs))
    return graph, source


def symbolic_routes():
    """Exact graph equalities under coherent bits, with all data free.

    Representative addresses are a complete set of branch/source categories;
    interval and singleton boundaries are independently exhausted below.
    No successful numeric execution is used to prove these routing identities.
    """
    cases = {(age, 4000) for stage in p.gather.STAGES for age in stage if 0 <= age < p.U}
    cases |= {(p.COLLECT_START, a) for a in range(p.NATIVE_START-2, p.COLLECTOR+3)}
    for age in (p.COLLECT_START+1, p.EVALUATE-1):
        cases |= {(age, a) for z in (p.NATIVE_START, p.COLLECTOR)
                  for a in range(z-3, z+4)}
    cases |= {(p.EVALUATE, p.COLLECTOR-s) for s in p.SLOTS}
    for age in (p.EVALUATE+1, p.DELIVERY, 80*p.Q, 96*p.Q-1):
        cases |= {(age, a) for z in (3, p.COLLECTOR, p.Q-3)
                  for a in range(z-3, z+4) if 0 <= a < p.Q}
    assertions = 0
    for age, address in sorted(cases):
        n = Net()
        logical = {(f, y, b): n.input(('free_logical', f, y, b))
                   for f, width in p.ALL_FIELDS for y in range(-3, 4) for b in range(width)}
        cells = {j: {f: [logical[f, j+s, b] if -3 <= j+s <= 3 else
                         n.input(('other_logical', f, j+s, b))
                         for s in p.SLOTS for b in range(width)]
                     for f, width in p.ALL_FIELDS} for j in range(-5, 6)}
        flag1, wipe = n.input(('free_flag1',)), n.input(('free_wipe',))
        writes = {s: (n.input(('write_enable', s)), n.input(('write_value', s))) for s in p.SLOTS}
        actual = p.build(n, cells, const_word(address, 13), const_word(age, 20),
                         flag1, wipe, writes)
        flags = {}

        def expression(command):
            name = command[0]
            if name == 'zero': return 0
            if name in ('majority3', 'or'):
                values = [expression(x) for x in command[1:]]
                return at_least(n, values, 2) if name == 'majority3' else n.OR(*values)
            if name == 'native_flag':
                _, y, which = command
                if y not in flags:
                    flags[y] = p.native_flags_build(n, [logical['pack', y, b] for b in range(p.PACK_BITS)])
                return flags[y][which-1]
            return logical[command]

        for f, width in p.EXTRA_FIELDS:
            for s in p.SLOTS:
                for b in range(width):
                    expected = n.AND(expression(p.extra_plan(age, address, s, f, b)), n.NOT(wipe))
                    assert actual[f, s, b] == expected, (age, address, s, f, b)
                    assertions += 1
        if age == p.DELIVERY:
            for s in p.SLOTS:
                a = (address+s) % p.Q
                f = 'courierL' if a == 3 else 'courierR' if a == p.Q-3 else 'simbit'
                expected = n.AND(logical[f, s, 0], n.NOT(wipe))
                assert actual['simbit', s, 0] == expected
                assertions += 1
    return len(cases), assertions


def category_exhaustion():
    # The extra routes depend on these clock equalities/ranges only. A complete
    # 20-bit clock partition is retained, including words beyond the legal period.
    points = {0, 1 << 20, p.COLLECT_START, p.COLLECT_START+1, p.EVALUATE,
              p.EVALUATE+1, 80*p.Q, p.DELIVERY, p.DELIVERY+1}
    for start, _, _ in p.gather.STAGES: points.update((start, start+1))
    points = sorted(points)
    classes = 0
    for lo, hi in zip(points, points[1:]):
        if lo == hi: continue
        for address in range(p.Q):
            for s in p.SLOTS:
                a = (address+s) % p.Q
                for f, width in p.EXTRA_FIELDS:
                    # Native field index determines the sole seed singleton;
                    # all eleven lanes share it and differ only by lane source.
                    for b in range(0, width, 11) if f == 'pack' else (0,):
                        assert p.extra_plan(lo, address, s, f, b) == p.extra_plan(hi-1, address, s, f, b)
                        command = p.extra_plan(lo, address, s, f, b)
                        if command[0] == 'native_flag': assert a == p.COLLECTOR and lo == p.EVALUATE
                classes += 1
    return points, classes


def symbolic_pack_and_couriers():
    # A token (colony, native-bit-index, lane) is a distinct free Boolean input.
    # Sets at a bit index denote an OR. The invariant proves each final bit has
    # exactly one token, so OR-hold does not change native raw-word semantics.
    words = {}
    for colony in range(-2, 3):
        for k in range(p.NATIVE_BITS):
            words[colony*p.Q+p.NATIVE_START+k] = {
                k*11+lane: frozenset({(colony, k, lane)}) for lane in range(11)}
    traces = []
    for step in range(1, p.NATIVE_BITS):
        targets = set(words) | {x+1 for x in words}
        nxt = {}
        for x in targets:
            a = x % p.Q
            incoming = words.get(x-1, {})
            old = words.get(x, {}) if a == p.COLLECTOR else {}
            if a == p.COLLECTOR:
                value = {b: old.get(b, frozenset()) | incoming.get(b, frozenset())
                         for b in set(old) | set(incoming)}
            elif p.NATIVE_START <= a < p.COLLECTOR: value = incoming
            else: value = {}
            if value: nxt[x] = value
        words = nxt
        traces.append(dict(step=step, occupied=len(words), collector_counts=[
            len(words.get(colony*p.Q+p.COLLECTOR, {})) for colony in range(-2, 3)]))
    assert set(words) == {g*p.Q+p.COLLECTOR for g in range(-2, 3)}
    for g in range(-2, 3):
        for k in range(p.NATIVE_BITS):
            for lane in range(11):
                assert words[g*p.Q+p.COLLECTOR][k*11+lane] == frozenset({(g, k, lane)})
    # Carrier tags expose cross-colony contamination regardless of flag value.
    courier_trace = []
    for field, dest, direction in (('courierL', 3, -1), ('courierR', p.Q-3, 1)):
        state = {g*p.Q+p.COLLECTOR: frozenset({g}) for g in range(-2, 3)}
        distance = abs(dest-p.COLLECTOR)
        for step in range(1, distance+4):
            nxt = {}
            for x in set(state) | {x+direction for x in state}:
                a = x % p.Q
                incoming = state.get(x-direction, frozenset())
                if a == dest: value = state.get(x, frozenset()) | incoming
                elif min(dest,p.COLLECTOR) <= a <= max(dest,p.COLLECTOR): value = incoming
                else: value = frozenset()
                if value: nxt[x] = value
            state = nxt
            if step >= distance:
                assert state == {g*p.Q+dest: frozenset({g}) for g in range(-2, 3)}
        courier_trace.append(dict(field=field, distance=distance,
            first_arrival_age=p.EVALUATE+distance, endpoint_tags=[[g, [g]] for g in range(-2, 3)]))
    return traces, courier_trace


def native_checks(out):
    graphs = [Compiled(p.native_netlist(corrected)) for corrected in (False, True)]
    for label, graph in zip(('printed','h1_changed'), graphs):
        (out/f'GFD0_native_{label}.json').write_text(json.dumps(dict(inputs=graph.inputs,
            gates=graph.gates, outputs=list(graph.outputs.items()), digest=graph.digest), separators=(',',':'))+'\n')
    # With old central F2=0, the printed erase branch is unused, identically.
    n = Net(); bits = [n.input(('bank', b)) for b in range(p.PACK_BITS)]
    bits[p.NATIVE_TAGS.index(('f2',0))*11+5] = 0
    assert p.native_flags_build(n,bits,False) == p.native_flags_build(n,bits,True)
    rng = np.random.default_rng(0x47464430)
    banks = []
    for _ in range(192):
        cells = {j: {f: int(rng.integers(0,1<<w)) for f,w in p.NATIVE_SCHEMA} for j in p.LANES}
        banks.append(p.pack_bank(cells))
    for age in (0,14,15,16,31,p.U-2,p.U-1):
        cells = {j:dict(addr=(271+j)%p.Q,age=age,f1=0,f2=0,wf1=0,wf2=0) for j in p.LANES}
        for j in range(1,6): cells[j]['addr']=0
        banks.append(p.pack_bank(cells))
    bits = np.asarray([[(word>>b)&1 for b in range(p.PACK_BITS)] for word in banks],dtype=np.uint8)
    results = []
    for corrected, graph in zip((False,True),graphs):
        actual = graph.evaluate({name:bits[:,i].astype(bool) for i,name in enumerate(graph.inputs)},bool)
        actual = np.column_stack([actual[name] for name in graph.outputs]).astype(np.uint8)
        expected = np.asarray([p.native_flags_scalar(word,corrected) for word in banks],dtype=np.uint8)
        assert np.array_equal(actual,expected)
        results.append(actual)
    np.savez_compressed(out/'GFD0_native_raw_checks.npz',inputs=bits,printed=results[0],h1_changed=results[1])
    assert tuple(results[0][-5]) == (1,1)  # missing-colony A=15 -> computed Age16.
    return len(banks), [g.digest for g in graphs]


def full_c_check(comp, source, out):
    library = out/'GFD0_prefix_transition.so'
    subprocess.run(['gcc','-std=c11','-O2','-fPIC','-shared',str(source),'-o',str(library)],check=True)
    ptr=ctypes.POINTER(ctypes.c_uint8)
    fun=ctypes.CDLL(str(library)).gfd0_transition
    fun.argtypes=[ptr,ptr];fun.restype=None
    rng=np.random.default_rng(0x434F5059)
    inputs=rng.integers(0,2,size=(32,len(comp.inputs)),dtype=np.uint8)
    index={name:i for i,name in enumerate(comp.inputs)}
    for row in range(len(inputs)):
        phase=(p.COLLECTOR-2+row%5)%p.Q
        # Exact canonical native closure; upper packed banks remain arbitrary.
        age=(p.COLLECT_START-1,p.EVALUATE-1,p.DELIVERY-1,80*p.Q-1)[row%4]
        for j in range(-5,6):
            for f,w in p.NATIVE_SCHEMA:
                value=(phase+j)%p.Q if f=='addr' else age if f=='age' else 0
                for b in range(w):inputs[row,index['native',j,f,b]]=(value>>b)&1
    results=comp.evaluate({name:inputs[:,i].astype(bool) for i,name in enumerate(comp.inputs)},bool)
    expected=np.column_stack([results[name] for name in comp.outputs]).astype(np.uint8)
    actual=np.empty_like(expected)
    for i in range(len(inputs)):fun(inputs[i].ctypes.data_as(ptr),actual[i].ctypes.data_as(ptr))
    assert np.array_equal(actual,expected)
    np.savez_compressed(out/'GFD0_actual_prefix_C_raw_checks.npz',inputs=inputs,outputs=actual)
    return len(inputs),library


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--outdir',type=Path,
        default=ROOT/'figs/gray_counterexamples/unregistered_gfd0')
    args=parser.parse_args();out=args.outdir;out.mkdir(parents=True,exist_ok=True)
    started=time.monotonic()
    print('GFD0: symbolic routing',flush=True)
    count,identities=symbolic_routes()
    print('GFD0: complete scalar control partition',flush=True)
    clocks,classes=category_exhaustion()
    pack_trace,courier_trace=symbolic_pack_and_couriers()
    native_count,native_digests=native_checks(out)
    layout=p.layout()
    assert p.FRAME_BITS==2322 and 2*p.FRAME_BITS<=p.Q
    assert p.NATIVE_START==2935 and p.COLLECTOR==2971
    assert not ({0,3,p.Q-3}&set(layout.values()))
    capture=max(p.gather.capture_age(2,l) for l in range(11))
    assert capture==69*p.Q+2 and capture<p.COLLECT_START
    assert p.EVALUATE==565288 and p.EVALUATE+max(abs(p.COLLECTOR-3),abs(p.Q-3-p.COLLECTOR))<p.DELIVERY
    for source in courier_trace:assert source['first_arrival_age']<80*p.Q
    majority=0
    for pair in combinations(range(5),2):
        for correct,a,b in product((0,1),repeat=3):
            values=[correct]*5;values[pair[0]]=a;values[pair[1]]=b
            assert at_least(Net(),values,3)==correct;majority+=1
    print('GFD0: emitting actual prefix graph and C',flush=True)
    comp=Compiled(p.netlist(internal_native=True))
    assert max(abs(name[1]) for name in comp.inputs if name[0] in ('x','native'))==5
    assert not any('flag_result' in str(name) or 'programme' in str(name) for name in comp.inputs)
    graph,source=emit(comp,out,'GFD0_prefix_transition')
    measured_count,library=full_c_check(comp,source,out)
    sources=[Path(__file__).resolve(),Path(p.__file__).resolve(),
        Path(p.gather.__file__).resolve(),Path(p.printed.__file__).resolve(),
        ROOT/'gacsca/maintenance.py',ROOT/'gacsca/netlist.py',
        ROOT/'papers_txt/gray_readers_guide.txt',
        Path(__file__).with_name('GFD0_BINARY_STAGE3_FLAG_DELIVERY.md')]
    assets={str(path.relative_to(ROOT)):sha(path) for path in sources}
    products=[graph,source,library,out/'GFD0_native_printed.json',out/'GFD0_native_h1_changed.json',
              out/'GFD0_native_raw_checks.npz',out/'GFD0_actual_prefix_C_raw_checks.npz']
    receipt=dict(name='GFD0 binary stage-3 flag-delivery component',passed=True,
        Q=p.Q,U=p.U,lambda_=p.LAMBDA,c=p.ERROR_SEPARATION,
        native_literal_printed=True,h1_only_separately_compared=True,
        input_bank_all_407_bits_free=True,no_native_input_coherence_required=True,
        native_controls_actual_prefix_internal=True,late_WF_and_fifth_write_ports_open=True,
        early_flag_oracle_or_immutable_instruction_ROM=False,
        native_oldF2zero_printed_h1_symbolic_identity=True,
        component_frame_bits=p.FRAME_BITS,component_2K_le_Q=True,final_frame_proved=False,
        radius=5,symbolic_route_cases=count,symbolic_route_identities=identities,
        complete_clock_partition=clocks,address_slot_clock_categories=classes,
        symbolic_pack_trace=pack_trace,symbolic_courier_trace=courier_trace,
        actual_three_gather_last_capture=capture,collect_start=p.COLLECT_START,evaluation=p.EVALUATE,
        info_delivery=p.DELIVERY,rest_begin=80*p.Q,pulse_begin=96*p.Q,
        source_order='old collected bank -> early native circuit -> old courier -> special SimBit -> held final computed primary',
        native_raw_scalar_checks_measured=native_count,native_circuit_digests=native_digests,
        local_C_raw_checks_measured=measured_count,copy_majority_payload_cofactors=majority,
        prefix_graph_digest=comp.digest,prefix_gate_count=len(comp.gates),prefix_input_bits=len(comp.inputs),
        prefix_outputs=len(comp.outputs),source_hashes=assets,
        product_hashes={path.name:sha(path) for path in products},
        own_beta_fit=False,full_ProgramBit_hardwirer_refinement=False,full_period=False,
        continuing_E0=False,Gray_counterexample=False,iid_theorem=False,shorter_U=False)
    (out/'GFD0_binary_stage3_certificate.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    print(json.dumps(dict(passed=True,elapsed=time.monotonic()-started,route_identities=identities,
        gates=len(comp.gates),frame_bits=p.FRAME_BITS,certificate=str(out/'GFD0_binary_stage3_certificate.json'))),flush=True)


if __name__=='__main__':main()
