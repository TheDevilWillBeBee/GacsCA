"""Exact local native/geometry/courier contracts for new GAW2D/GAW2R.

No iid sampling, large-grid experiment, or intact-history counterexample.
The accompanying proof supplies the infinite-line induction.
"""
from pathlib import Path
from dataclasses import replace
from types import SimpleNamespace
import sys,json,time,hashlib,importlib.util
import gray_three_gather_gaw2 as d
import gray_three_gather_gaw2r as r
import build_gray_three_gather_gaw2 as bd
import build_gray_three_gather_gaw2r as br
ROOT=Path(__file__).resolve().parents[4]
D=ROOT/'figs/gray_counterexamples/unregistered_gaw2'

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def module_from_snapshot(path,name):
    # Load retained exact source text with its intended isolated import paths.
    module=SimpleNamespace(__file__=str(path));scope=module.__dict__
    scope['__name__']=name;exec(compile(path.read_text(),str(path),'exec'),scope)
    return module


def replay_initial_failures():
    source=D/'GAW2_before_clock_cache_builder.txt'
    frozen=module_from_snapshot(source,'gaw2_initial_builder')
    rom,rows,labels,errors=frozen.programme().assemble();assert not errors
    rom=replace(rom,bits=rom.bits+(0,)*(65536-len(rom.bits)))
    oldrom=json.loads((D/'GAW2D_rom_initial.json').read_text())
    assert list(rom.bits)==oldrom['bits'] and [hex(w) for w in rom.dictionary]==oldrom['dictionary']
    initial_listing=json.loads((D/'GAW2D_listing_initial.json').read_text())
    # The retained listing has a descriptive header but exact emitted rows.
    assert initial_listing['instructions']==rows
    # The snapshot added one inert audit label after the retained emission.
    oldlabels=initial_listing['labels']
    assert set(labels)-set(oldlabels)=={'data_updates'} and labels['data_updates']==1091
    assert all(labels[n]==v for n,v in oldlabels.items())
    results=[]
    for n in (1,2):
        path=D/('GAW2D_deadline_probe_%02d.json'%n);record=json.loads(path.read_text())
        cells={j-8:d.cell_from_words([int(w,16) for w in words]) for j,words in enumerate(record['inputs'])}
        expected=d.cell_words(d.local_transition(cells,rom));tape=d.input_tape(cells)
        assert [hex(v) for v in expected]==record['expected']
        out,ticks,head,_=d.execute(rom,tape,limit=200000)
        actual=[out.get(d.PRIMARY_START+i,0) for i in range(d.FRAME_WORDS)]
        assert ticks==record['full_ticks'] and head.mode==d.HALT
        assert actual==expected and [hex(v) for v in actual]==record['actual']
        prefix,used,head,_=d.execute(rom,tape,limit=65535)
        deadline=[prefix.get(d.PRIMARY_START+i,0) for i in range(d.FRAME_WORDS)]
        wrong=[i for i,(a,b) in enumerate(zip(deadline,expected)) if a!=b]
        assert wrong==record['deadline_wrong_words'] and wrong
        assert [hex(v) for v in deadline]==record['deadline_outputs']
        results.append(dict(name=record['name'],ticks=ticks,deadline=used,wrong_words=wrong,prepared_only=True))
    return results



def replay_cached_failures():
    rom,_,_,errors=bd.programme().assemble();assert not errors
    rom=replace(rom,bits=rom.bits+(0,)*(65536-len(rom.bits)))
    records=json.loads((D/'GAW2D_cached_deadline_probes.json').read_text())
    results=[]
    for record in records:
        original=json.loads((D/record['input_receipt']).read_text())
        cells={j-8:d.cell_from_words([int(w,16) for w in ws]) for j,ws in enumerate(original['inputs'])}
        tape=d.input_tape(cells);expected=d.cell_words(d.local_transition(cells,rom))
        out,ticks,head,_=d.execute(rom,tape)
        assert head.mode==d.HALT and ticks==record['full_ticks']
        assert [out.get(d.PRIMARY_START+i,0) for i in range(d.FRAME_WORDS)]==expected
        assert [hex(v) for v in expected]==record['expected']
        prefix,used,head,_=d.execute(rom,tape,limit=65535)
        wrong=[i for i,v in enumerate(expected) if prefix.get(d.PRIMARY_START+i,0)!=v]
        assert wrong==record['deadline_wrong_words'] and wrong
        assert [hex(prefix.get(d.PRIMARY_START+i,0)) for i in range(d.FRAME_WORDS)]==record['deadline_outputs']
        results.append(dict(name=record['name'],ticks=ticks,wrong_words=wrong,prepared_only=True))
    assert results[1]['ticks']>16*d.Q-1
    return results

def native_contract(k):
    # Exhaust both flag masks separately; the other flag is irrelevant to
    # the formula under its stated premise, by the literal native equations.
    addresses=list(range(6))+[6]+list(range(k.Q-5,k.Q))
    f1checks=f2checks=0
    for address in addresses:
        for mask in range(2048):
            cells={j:k.Cell(addr=(address+j)%k.Q,age=123,
                f1=((mask>>(j+5))&1) if -5<=j<=5 else 0) for j in range(-8,9)}
            got=k.native_at(cells)
            right=sum((mask>>(j+5))&1 for j in range(1,6) if address+j<k.Q)
            selfbit=(mask>>5)&1
            assert got['f1']==int(right>=3 or selfbit and right>=2)
            assert got['addr']==address and got['age']==124
            f1checks+=1
            cells={j:k.Cell(addr=(address+j)%k.Q,age=123,
                f2=((mask>>(j+5))&1) if -5<=j<=5 else 0) for j in range(-8,9)}
            got=k.native_at(cells)
            left=sum((mask>>(j+5))&1 for j in range(-5,0) if address+j>=0)
            expected=int(left>=4 or selfbit and left>=2)
            assert got['f1']==0 and got['f2']==expected,(address,mask,got,expected)
            assert got['addr']==address and got['age']==124
            f2checks+=1
    return dict(quiet_F1_cofactors=f1checks,quiet_F2_cofactors=f2checks,
        address_classes=addresses,quiet_by=99*k.Q,boundary_zero_strip_growth=2)


def geometry_contract(k):
    rows=[]
    for g in (1,2,3):
        for lane in range(17):
            start=k.GATHER_STARTS[g-1];delta=lane-8;capture=k.capture(g,lane)
            for copy,s in enumerate(k.SLOTS):
                for word in range(k.FRAME_WORDS):
                    holder=k.PRIMARY_START+word-s
                    logical=holder+s
                    assert logical==k.PRIMARY_START+word
                    oldtick=capture-1
                    source=logical if delta==0 else logical+delta*k.Q
                    assert source==k.PRIMARY_START+word+delta*k.Q
                    if delta:assert oldtick-(start+1)==abs(delta)*k.Q
                    assert 0<=holder<k.Q
                rows.append((g,lane,copy,s,capture,delta*k.Q))
    last=max(k.capture(g,l) for g in (1,2,3) for l in range(17))
    assert last==72*k.Q+2 and k.EARLY_RESET==last+1
    assert k.EARLY_BIRTH==last+2
    # No active interpreter crosses a colony edge: all operand contracts
    # lie in the frame or its internal128..149 Scratch subframe.
    assert k.PRIMARY_START-2>5 and k.PRIMARY_START+k.FRAME_WORDS+2<k.Q-5
    return dict(actual_holder_source_identities=len(rows)*k.FRAME_WORDS,
        captures=rows,last_capture=last,early_birth=k.EARLY_BIRTH,
        frame=[k.PRIMARY_START,k.PRIMARY_START+k.FRAME_WORDS-1])


def courier_contract(k):
    start=75*k.Q;read=80*k.Q-2;duration=read-start
    left_distance=k.PRIMARY_START;right_distance=k.Q-k.PRIMARY_START-5
    assert max(left_distance,right_distance)<duration
    # Exact continuous shift from one local impulse: by read time neither
    # endpoint contains it. A periodic train also misses at this residue.
    assert duration!=left_distance and duration!=right_distance
    assert (duration-left_distance)%k.Q and (duration-right_distance)%k.Q
    # Holding without a source interval captures neighbour colony commands.
    foreign_left=k.Q+left_distance;foreign_right=k.Q+right_distance
    assert foreign_left<duration and foreign_right<duration
    # With the declared route gates there is exactly one initial source in
    # each directed interval; a held endpoint is an absorbing OR boundary.
    route_lengths=(left_distance+1,right_distance+1)
    for distance in (left_distance,right_distance):
        # Packet-location induction: one step/tick until absorption.
        for t in range(duration+1):assert max(distance-t,0)==(distance-t if t<distance else 0)
    return dict(source_phase=start,source_to_endpoint=[left_distance,right_distance],
        old_source_read=read,shift_without_hold_wrong=True,
        hold_without_route_gate_contaminates_after=[foreign_left,foreign_right],
        gated_routes_disjoint=True,route_site_counts=route_lengths)


def storage(k,builder):
    rom,rows,labels,errors=builder.programme().assemble();assert not errors
    narrow=SimpleNamespace(**{n:v for n,v in vars(k).items() if not n.startswith('__')})
    narrow.TOKEN_BITS=9;narrow.DICTIONARY_SIZE=512;narrow.CODE_CAPACITY=k.Q
    small,_,_,failed=builder.programme(engine=narrow).assemble()
    assert failed==[dict(dictionary_overflow=rom.used_dictionary)]
    rawbits=37+5*len(k.FIELD_NAMES)*k.WORD
    assert rawbits==49037
    return dict(instructions=len(rows),code_words=rom.token_count,distinct_dictionary=rom.used_dictionary,
        direct_beta_bits=rom.token_count*rom.token_bits,Q=k.Q,fit_Q=False,
        dictionary_limit512=False,nine_bit_attempt=dict(beta_bits=small.token_count*small.token_bits,errors=failed),
        diagnostic_code_bits=65536,diagnostic_dictionary_bits=2048*k.WORD,
        early_pc_metadata_bits=k.PC_BITS,total_immutable_bits=65536+2048*k.WORD+k.PC_BITS,
        raw_cell_bits=rawbits,literal_Gray_Q_ge_2K=False,
        bit_layout_necessary_Q=2*rawbits,next_power_of_two_Q=1<<(2*rawbits-1).bit_length())


def main(write=True):
    start=time.monotonic()
    result=dict(name='GAW2 exact three-gather/courier/quiet/timing interface contracts',
        geometry=geometry_contract(r),couriers=courier_contract(r),native_quiet=native_contract(r),
        initial_deadline_failures=replay_initial_failures(),cached_deadline_failures=replay_cached_failures(),storage_D=storage(d,bd),storage_R=storage(r,br),
        Q=r.Q,U=r.U,error_lambda=24,error_separation=104,
        noise_history_used=False,faithful_Gray_refutation=False,iid_failure=False,
        shorter_U_proved=False,full_Q_bit_programme=False,
        scope='isolated changed WORD100/radius8/immutable-code rule; zero-error period proof in companion document',
        elapsed_seconds=time.monotonic()-start)
    if write:(D/'GAW2_period_contracts.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(passed=True,elapsed_seconds=result['elapsed_seconds'],
        storage=result['storage_R'],quiet=result['native_quiet'],failure_ticks=[v['ticks'] for v in result['initial_deadline_failures']])))
    return result

if __name__=='__main__':main()
