#!/usr/bin/env python3
"""SP31's specified actual first pulse, including two free Flag2 sources.

The written proof supplies the physical program/gather induction and the
universal factor reduction. Exact circuit identities and four finite
infinite-line event executions certify its local premises and endpoint.
Selected transcription cofactors remain measured support only.
"""
from pathlib import Path
from itertools import product
import ctypes, hashlib, json, subprocess, sys, tempfile, time
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from gacsca.netlist import Net, Compiled, const_word, w_eq_const, w_in_range
from gacsca import rule_g
import proposed_native_command1024 as proposed

OUT = ROOT / 'figs/robustness'
DIR = OUT / 'SP31_two_sources'
SOURCE = Path(__file__).with_name('sp31_two_flag2_sources.c')
PROOF = Path(__file__).with_name('SP31_FIRST_PULSE.md')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def blocked(strips, j, d, phase, Q):
    lo, hi = sorted((j*Q+phase, (j+d)*Q+phase))
    return any(lo+8*max(0, (left-lo+7)//8) <= min(hi, right-1)
               for left, right in strips)


def template(x, Q, L=128, R=143):
    a, b = L*Q-512, R*Q
    return int(a <= x < b), int((L-1)*Q <= x < a or b-512 <= x < b)


def quiet_cofactors(p, L=128, R=143):
    a, b = L*p.Q-512, R*p.Q
    refinements = natives = 0
    build, source = proposed.proposed_build()
    for edge in (a, b):
        for x in range(edge-40, edge+41):
            n = Net()
            age = [n.input(('common_clock', k)) for k in range(p.m)]
            cells = {j: dict(addr=const_word((x+j+512*template(x+j,p.Q,L,R)[0])%p.Q,p.k),
                             age=age) for j in range(-32,33)}
            got, _ = proposed.local.refine_one(n,cells,p,0)
            assert got['addr'] == cells[0]['addr'] and got['age'] == age
            refinements += 1
    readers = sorted(set(range(a-p.Q-40,a+p.Q+41)) | set(range(b-p.Q-40,b+p.Q+41)))
    for x in readers:
        n = Net()
        age = [n.input(('common_clock', k)) for k in range(p.m)]
        cells = {j: dict(addr=const_word((x+j+512*template(x+j,p.Q,L,R)[0])%p.Q,p.k),
                         age=age, f1=template(x+j,p.Q,L,R)[1], f2=0, wf1=0, wf2=0)
                 for j in range(-5,9)}
        got = build(n,cells,p.k,p.m,Q=p.Q,nb=p.nb,radix=p.R,pos_bits=p.PB,service_force=0)
        assert got['addr'] == cells[0]['addr'] and got['age_now'] == age
        assert got['f1'] == template(x,p.Q,L,R)[1] and got['f2'] == 0
        natives += 1
    assert (refinements,natives) == (162,4258)
    return dict(template=[L,R], refinements=refinements, native_cofactors=natives,
                maintenance_source_sha256=hashlib.sha256(source.encode()).hexdigest())


def source_enclosure(p, candidate):
    a, b = 128*p.Q-512,143*p.Q
    strips = ((127*p.Q,a),(b-512,b))
    table = proposed.dependency_table(p)
    byphase = {r['address']:r for r in table}
    phase_at = {(r['field'],r['bit']):r['address'] for r in table}
    routes = []
    for row in table:
        if row['field'] not in ('addr','age','f2','wf2'):
            continue
        actual = byphase[(row['address']+512)%p.Q]
        assert actual['field'] == 'h2'
        routes.append(dict(virtual_field=row['field'], virtual_bit=row['bit'],
                           virtual_phase=row['address'], true_phase=actual['address'],
                           true_zero_field='h2', true_zero_bit=actual['bit']))
    assert [r['true_zero_bit'] for r in routes if r['virtual_field']=='addr'] == list(range(139,149))
    class ZeroF2(Net):
        def input(self,key):
            if isinstance(key,tuple) and len(key)==4 and key[0]=='x' and key[2] in ('age','f2','wf2'):
                return 0
            return super().input(key)
    zero_f2, _ = proposed.full_net(p,ZeroF2)
    assert zero_f2.outputs['y','f2',0] == 0
    class ZeroGF(Net):
        def input(self,key):
            if isinstance(key,tuple) and len(key)==4 and key[0]=='x' and key[2]=='addr':
                return 0
            return super().input(key)
    zero_gf, _ = proposed.full_net(p,ZeroGF)
    assert zero_gf.outputs['y','f1',0] == 1
    assert all(zero_gf.outputs['y','addr',bit] == 0 for bit in range(p.k))
    records = []
    route_cases = 0
    for j in (*range(84,127),*range(143,181)):
        for row in table:
            if row['field'] != 'addr':
                continue
            for d in (0,*row['offsets']):
                assert blocked(strips,j,d,row['address'],p.Q) == blocked(strips,j,d,59,p.Q)
                route_cases += 1
        class Captured(Net):
            def input(self,key):
                if isinstance(key,tuple) and len(key)==4 and key[0]=='x':
                    _,d,f,bit = key
                    if f == 'addr':
                        word = 0 if blocked(strips,j,d,phase_at[f,bit],p.Q) else (j+d)%p.Q
                        return (word>>bit)&1
                    if f in ('age','f1','f2','wf1','wf2','packet_valid','service_valid','backward_pressure'):
                        return 0
                return super().input(key)
        n, _ = proposed.full_net(p,Captured)
        flag = n.outputs['y','f1',0]
        assert flag == int(j in (124,125,126,143,144,145)),(j,flag)
        assert n.outputs['y','f2',0] == 0
        records.append(dict(colony=j,Flag1=flag,Flag2=0,other_Info_and_unmentioned_inputs_free=True))
    assert len(records) == 81
    assert (83+37)*p.Q+68 < strips[0][0]
    assert (181-37)*p.Q+59 >= strips[-1][1]
    # Every complete virtual interpreter/copy footprint is homogeneous.
    foreign = []
    for j in range(128,143):
        origin = j*p.Q-512
        assert a <= origin+1 and origin+1023 < b
        assert all(not any(lo <= y < hi for lo,hi in strips)
                   for y in (origin+1,origin+1023))
        foreign.append(dict(virtual_colony=j,origin=origin,Flag1=1,Flag2=0))
    # Exact special/alias role on each of its five actual holders. The
    # only special writes with incomplete interpreter/courier footprints
    # are the two stated left commands. Existing alias Info starts0.
    aliases = []
    for j,phase in product(range(120,151),(3,509,515,1021)):
        y = j*p.Q+phase
        labels = [template(y-slot,p.Q)[0] for slot in proposed.SLOTS]
        assert len(set(labels)) == 1
        virtual = (phase+512*labels[0])%p.Q
        assert virtual in (3,509,515,1021)
        aliases.append(dict(colony=j,physical_primary=y,physical_phase=phase,
                            virtual_phase=virtual,special_write=virtual in (3,1021)))
    unknown = [127*p.Q+3,142*p.Q+515]
    assert [(r['physical_primary'],r['virtual_phase']) for r in aliases
            if r['physical_primary'] in unknown] == [(unknown[0],3),(unknown[1],3)]
    for phase,shift,slot in product((3,509,515,1021),(0,512),proposed.SLOTS):
        mask = (set(range(58,901))-{509,515})|{901,902,965}
        assert ((phase-slot+shift)%p.Q+slot)%p.Q not in mask
    return dict(foreign_zero_source_routes=routes,true_complete_frame_cofactors=records,
                GF_capture_route_checks=route_cases,complete_foreign_frames=foreign,
                universal_zero_Age_F2_WF2_F2_identity=True,
                universal_zero_GF_GF0_Flag1_one_identity=True,
                actual_alias_special_write_classes=aliases,
                partial_Flag2_free_vote_primaries=unknown,
                universal_two_phase_commit_alias_zero_cases=40)


def literal_transcription(p,candidate,library):
    lib = ctypes.CDLL(str(library))
    fn = lib.sp31_two_sources_cofactor
    ptr = ctypes.POINTER(ctypes.c_uint8)
    fn.argtypes = [ptr,ptr,ctypes.c_int,ctypes.c_int]
    fn.restype = ctypes.c_uint
    count = 4096
    rng = np.random.default_rng(31225)
    boundary = [*range(9),*range(503,521),*range(1015,1024)]
    residues = np.resize(np.array(boundary,dtype=np.int64),count)
    elapsed = np.resize(np.array([0,1,2047,2048,6143],dtype=np.int64),count)
    native = rng.integers(0,32,size=(count,81),dtype=np.uint8)
    info = rng.integers(0,2,size=(count,81),dtype=np.uint8)
    expected = np.array([fn(a.ctypes.data_as(ptr),b.ctypes.data_as(ptr),int(x),int(t))
                         for a,b,x,t in zip(native,info,residues,elapsed)],dtype=np.uint8)
    ages = np.array([p.age_code(p.T_wf+int(t)) for t in elapsed],dtype=np.uint32)
    next_ages = np.array([p.age_code(p.T_wf+int(t)+1) for t in elapsed],dtype=np.uint32)
    shifts = {'f1':1,'wf1':2,'f2':3,'wf2':4}
    values = {}
    for key in candidate.comp.inputs:
        if key[0] == 'I':
            v = rng.integers(0,2,size=count,dtype=np.uint8)
        else:
            _,d,f,b = key
            if f == 'addr': v = (((residues+d+512*(native[:,d+40]&1))%p.Q)>>b)&1
            elif f == 'age': v = (ages>>b)&1
            elif f in shifts: v = (native[:,d+40]>>shifts[f])&1
            elif f == 'info': v = info[:,d+b-2+40]
            else: v = rng.integers(0,2,size=count,dtype=np.uint8)
        values[key] = v.astype(bool)
    actual = candidate.comp.evaluate(values,bool)
    gf = (residues+512*(expected&1))%p.Q
    for b in range(p.k):
        assert np.array_equal(actual['y','addr',b],((gf>>b)&1).astype(bool)),('GF',b)
    for b in range(p.m):
        assert np.array_equal(actual['y','age',b],((next_ages>>b)&1).astype(bool)),('Age',b)
    for f,shift in shifts.items():
        assert np.array_equal(actual['y',f,0],((expected>>shift)&1).astype(bool)),f
    keep = ~(((expected>>1)&1).astype(bool)&((expected&1)!=((expected>>5)&1)))
    for slot in proposed.SLOTS:
        assert np.array_equal(actual['y','info',slot+2],keep&info[:,slot+40].astype(bool)),('Info',slot)
    return dict(selected_actual_full_net_transcription_cases=count,measured_only=True,
                four_native_flags_and_private_I_Info_free=True,
                common_legal_clock_and_binary_GF_required=True)


def main():
    start = time.monotonic()
    DIR.mkdir(parents=True,exist_ok=True)
    p = proposed.parameters()
    candidate = proposed.load_artifact()
    assert candidate.digest() == 'dc456bac4904647b66ee1f922788cdeb4428df91e21858fd8de0b3ccb4a69421'
    assert candidate.comp.digest == '73378f4aa5669c54a21dfcd1f2a277e14aaf4d98e0508d4e6870de7491c36d44'
    deps = ('SP31_program_build.json','SP31_symbolic_schedule.json','SP31_native_certificate.json',
            'SP31_front_certificate.json','SP31_interface_certificate.json','SP31_encoded_certificate.json')
    receipts = {name:json.loads((OUT/name).read_text()) for name in deps}
    programme = receipts['SP31_symbolic_schedule.json']
    assert programme['early_flag_store_ages'] == {'58':257973,'965':251472}
    assert programme['final_hold_equalities'] == 842 and programme['early_flag_equalities'] == 2
    assert proposed.flag_store_cells(p) == (965,58)
    assert p.courier_ticks() == (278343,278344,278343)
    assert 278344+(58-3)+1 == 278343+(1021-965)+1 == p.T_sig
    assert p.T_sig+1 == p.T_wf == 278401
    quiet = [quiet_cofactors(p),quiet_cofactors(p,135,146)]
    print(json.dumps({'quiet_templates_checked':quiet}),flush=True)
    source = proposed.generated_source(p)
    for line in ('        service_force=0,\n',
                 '    wf2 = n.all([left_end, in_wf, sim_l, n.NOT(f1_new)])\n',
                 '    keep = n.NOT(wipe)\n',
                 '    sig = age_is(p.T_sig)\n'):
        assert source.count(line) == 1,line
    n = Net()
    age = [n.input(('age',b)) for b in range(p.m)]
    n.set_output(('birth',),w_eq_const(n,age,p.age_code(p.T_wf)))
    n.set_output(('WF',),w_in_range(n,age,p.age_code(p.T_wf),p.age_code(p.T_wf+2*p.Q-1)+1))
    for begin,end in ((0,p.T_wf),(p.T_wf+6144,p.U)):
        codes = np.array([p.age_code(t) for t in range(begin,end)],dtype=np.uint32)
        got = Compiled(n).evaluate({('age',b):((codes>>b)&1).astype(bool) for b in range(p.m)},bool)
        assert all(not v.any() for v in got.values())
    # Majority fold is exact for every incoherent old copy and holder mask.
    for old,gates in product(range(32),repeat=2):
        vote = int(old.bit_count()>=3)
        assert int(sum(vote*((gates>>i)&1) for i in range(5))>=3) == vote*int(gates.bit_count()>=3)
    enclosure = source_enclosure(p,candidate)
    print(json.dumps({'complete_true_source_frames':len(enclosure['true_complete_frame_cofactors']),
                      'partial_Flag2_free_vote_primaries':enclosure['partial_Flag2_free_vote_primaries']}),flush=True)
    runs = []
    with tempfile.TemporaryDirectory(prefix='sp31_actual_first_pulse_') as td:
        exe,library = Path(td)/'pulse',Path(td)/'factor.so'
        logs = []
        for target,args in ((exe,[]),(library,['-shared','-fPIC'])):
            built = subprocess.run(['cc','-O3','-std=c11','-Wall','-Wextra','-Werror',*args,
                                    str(SOURCE),'-o',str(target)],check=True,capture_output=True)
            assert not built.stdout and not built.stderr
            logs.append(built.stdout+built.stderr)
        (DIR/'certificate_compile.log').write_bytes(b''.join(logs))
        binary_sha,library_sha = sha(exe),sha(library)
        transcription = literal_transcription(p,candidate,library)
        print(json.dumps(transcription),flush=True)
        base_info = [127997,129021,130045,138749,139773,140797,141821,142845,143869,144893,145917]
        for mask in range(4):
            replay = Path(td)/f'mask{mask}.jsonl'
            t0 = time.monotonic()
            with replay.open('wb') as stream:
                run = subprocess.run([str(exe),str(mask),'6144'],stdout=stream,
                                     stderr=subprocess.PIPE,check=True)
            assert not run.stderr
            (DIR/f'mask{mask}_certificate_stderr.log').write_bytes(run.stderr)
            original = DIR/f'mask{mask}_trace.jsonl'
            assert replay.read_bytes() == original.read_bytes(),('changed trace',mask)
            records = [json.loads(line) for line in replay.read_text().splitlines()]
            rows,endpoint = records[:-1],records[-1]
            assert len(rows) == 6145 and [r['row'] for r in rows] == list(range(6145))
            assert rows[0]['GF_sites'] == 15872 and rows[-1]['GF_sites'] == 11776
            assert (rows[-1]['GF_left'],rows[-1]['GF_right_exclusive']) == (137728,149504)
            assert rows[-1]['Flag1_sites'] == 1024
            assert all(rows[-1][f] == 0 for f in ('GF_holes','WF1_sites','Flag2_sites','WF2_sites'))
            assert endpoint['endpoint_segments'] == [[137216,137728,2],[137728,148992,1],[148992,149504,3]]
            expected_info = sorted(base_info+[130051]*(bool(mask&1))+[145923]*(bool(mask&2)))
            assert endpoint['endpoint_Info'] == expected_info
            assert endpoint['exact_event_execution_complete'] and not endpoint['physical_input_premises_supplied_by_this_C']
            assert rows[-1]['events'] == [9894718,10041616,10041616,10188514][mask]
            assert all(a['events'] < b['events'] for a,b in zip(rows,rows[1:]))
            assert all(a['Info_ones'] >= b['Info_ones'] for a,b in zip(rows,rows[1:]))
            assert max(r['segments'] for r in rows) == 61
            assert sum(r['GF_holes']>0 for r in rows) == 1 and max(r['GF_holes'] for r in rows) == 3
            peak = (mask&1 != 0)+(mask&2 != 0)
            assert max(r['Flag2_sites'] for r in rows) == 1024*peak
            assert max(r['WF2_sites'] for r in rows) == 5*peak
            r = dict(mask=mask,updates=6144,trace_rows=6145,events=rows[-1]['events'],
                     endpoint_template=[135,146],endpoint_GF_sites=11776,
                     maximum_segments=61,intermediate_GF_hole_rows=1,maximum_GF_holes=3,
                     peak_Flag2_sites=1024*peak,peak_WF2_sites=5*peak,
                     retained_Info_primaries=expected_info,trace_sha256=sha(original),
                     elapsed_seconds=time.monotonic()-t0)
            runs.append(r)
            print(json.dumps({'exact_replay':r}),flush=True)
    e = receipts['SP31_encoded_certificate.json']
    assert e['literal_commit_zero_bits'] == 807 and e['literal_masked_Hold_Info_forwarding_identities'] == 5
    assert e['every_current_and_successor_clock_word_symbolic']
    source_deps = ('gacsca/rule_g.py','gacsca/netlist.py','gacsca/machine.py',
                   'Report/proofs/proposed_native_command1024.py',
                   'Report/proofs/check_native_command1024_encoded.py')
    proof_deps = ('SP31_OWN_RULE.md','SP28_FULL_ADDRESS_ISLAND.md','SP30_FIRST_SIGNAL.md',
                  'unregistered_terminal/SP30_16Q_ACTUAL_REGENERATION.md')
    result = dict(proposal='SP31',additional_rule_change=False,active_G17_or_frozen_SP30_modified=False,
                  Q=p.Q,U=p.U,T_wf=p.T_wf,candidate_sha256=candidate.digest(),netlist_sha256=candidate.comp.digest,
                  checker_sha256=sha(__file__),proof_sha256=sha(PROOF),C_source_sha256=sha(SOURCE),
                  rebuilt_C_binary_sha256=binary_sha,rebuilt_C_library_sha256=library_sha,
                  source_dependencies_sha256={name:sha(ROOT/name) for name in source_deps},
                  proof_dependencies_sha256={name:sha(PROOF.parent/name) for name in proof_deps},
                  receipt_dependencies_sha256={name:sha(OUT/name) for name in deps},
                  retained_assets_sha256={str(path.relative_to(OUT)):sha(path) for path in sorted(DIR.iterdir()) if path.is_file()},
                  quiet_templates=quiet,legal_pre_TF_guard_cases=p.T_wf,
                  legal_post_pulse_guard_cases=p.U-p.T_wf-6144,mail_gate_fold_cases=1024,
                  source_enclosure=enclosure,transcription_checks=transcription,exact_four_runs=runs,
                  exact_event_intervals=sum(r['events'] for r in runs),
                  single_dense_original_real2_support=[127*p.Q,143*p.Q],original_lambda=24,original_c=16,
                  initial_native_template=[128,143],endpoint_native_template=[135,146],
                  same_actual_intact_start_single_error_row_first_pulse_proved=True,
                  all_initial_upper_Info_payloads_and_both_partial_Flag2_votes_allowed=True,
                  actual_Info_erasures_and_native_Flag2_WF2_evolve_not_prescribed=True,
                  computed_first_boundary_native_template_and807_reset_proved=True,
                  first_boundary_all_four_physical_signal_alias_tracks_zero_proved=True,
                  second_period_bank_source_regeneration_or_general_eroder_proved=False,
                  full_upper_error_map_or_positive_iid_epsilon_or_minimum_sufficient_change_proved=False,
                  Gray_or_G17_refutation=False,global_reliability_established=False,
                  elapsed_seconds=time.monotonic()-start)
    (OUT/'SP31_first_pulse_certificate.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('same_actual_intact_start_single_error_row_first_pulse_proved',
                                         'exact_event_intervals','global_reliability_established','elapsed_seconds')}),flush=True)


if __name__ == '__main__':
    main()
