"""Transfer local lemmas, with fresh spatial checks, to the retimed descriptor.

This is a theorem-premise checker, not an evolution backend. The clock bridge
substitutes arbitrary raw fields into old all-clock identities pointwise; it
does not substitute an old ROM trajectory or skip physical transitions.
"""
import argparse
import hashlib
import json
from pathlib import Path
import resource
import time
from gacsca.fixed_rule import retimed_holder_rule as f,retimed_holder_core as c,retimed_holder_program as p,retimed_holder_projected as r
from gacsca.fixed_rule import small_holder_rule as old_f,small_holder_core as old_c
from experiments.fixed_rule import certify_retimed_holder_clock_transfer as bridge
from experiments.fixed_rule import compose_small_holder_noiseless_period as old_period
from experiments.fixed_rule import join_small_holder_structural_invariant as structure
from experiments.fixed_rule.audit_small_holder_position_events import sha

ROOT=Path('figs/fixed_rule')
SOURCES={'clock':'retimed_holder_clock_transfer_v1.json',
         'head':'small_holder_head_invariant_v1.json','image':'small_holder_procedure_image_v1.json',
         **{name:old_period.SOURCES[name] for name in ('context','barriers','mail','mail_support','structure')}}

def load_inputs():
    # Revalidate the existing reference dependency chain. Its numerical ROM
    # catalogs are not returned as results for the retimed candidate.
    old_period.load_inputs()
    loaded={name:json.loads((ROOT/file).read_text()) for name,file in SOURCES.items()}
    for name,doc in loaded.items():
        assert doc['passed'],name
        for source,wanted in doc['source_sha256'].items():assert sha(source)==wanted,source
        if name!='clock' and 'descriptor_sha256' in doc:assert doc['descriptor_sha256']==old_f.self_description().digest()
    structure.join(ROOT/SOURCES['head'],ROOT/SOURCES['image'])
    return loaded


def validate_premises(loaded):
    assert f.SCHEMA==old_f.SCHEMA and c.SCHEMA==old_c.SCHEMA and c.CONTROL==old_c.CONTROL
    assert f.NEIGHBORHOOD==old_f.NEIGHBORHOOD and f.Q==old_f.Q
    clock=loaded['clock']
    assert clock['physical_descriptor_sha256']==f.self_description().digest()
    assert clock['reference_descriptor_sha256']==old_f.self_description().digest()
    assert clock['legal_new_ages']==f.U and clock['all_Ages_covered_without_sampling']
    expected=list(bridge.intervals(c));actual=[]
    for row in clock['intervals']:
        lo,hi=row['new_age_interval'];actual.append((lo,hi));old=row['reference_age']
        assert row['non_Age_words']==f.FIELDS-1 and row['exact_new_clock'] and row['arbitrary_other_raw_fields']
        assert 0<=old<old_f.U
        assert bridge.signature(c,lo)==bridge.signature(c,hi)==bridge.signature(old_c,old)
    assert actual==expected and sum(hi-lo+1 for lo,hi in actual)==f.U
    for key in ('head','image','mail'):
        doc=loaded[key]
        assert len(doc['cases'])==9 and {row['phase'] for row in doc['cases']}=={None,*range(8)},key
        assert all(row['passed'] and row['all_clock_ages']==old_f.U for row in doc['cases']),key
    assert not loaded['head']['pilot'] and not loaded['mail']['pilot']
    assert all(row['routing_destinations_disjoint'] and row['active_head_survives_iff_not_halted'] for row in loaded['head']['cases'])
    assert all(row['checked_primaries']==[-1,0,1] and row['canonical_geometry_preserved'] for row in loaded['image']['cases'])
    assert loaded['context']['complete_raw_words']==154 and loaded['context']['all_clock_ages']==old_f.U
    assert loaded['barriers']['procedure_word_identities']==90 and loaded['barriers']['all_clock_ages']==old_f.U
    assert loaded['barriers']['simultaneous_reset_vote_age']==old_c.RESET_AGES[4]==old_c.VOTE_AGES[1]
    assert c.RESET_AGES[4]==c.VOTE_AGES[1]
    assert loaded['mail_support']['support']['controller_outputs_independent_of_all_old_mail']==45
    return dict(passed=True,legal_new_ages=f.U,clock_intervals=len(actual),complete_non_Age_outputs=153,
                local_lemmas=['raw mail factorization','controller independence from old mail','procedure output image',
                              'head routing and zero inactive controllers','arbitrary context factorization','quiet reset/vote/commit'],
                scope='Canonical Address and uniform legal Age. Remaining premises (coherent procedure/one head for appropriate lemmas; zero head/controller/mail for quiet barriers) remain required.',
                principle='At each new Age, replace only uniform raw Age by the matched old representative; all other raw words are identical. Non-Age identities transfer for arbitrary metadata, including the actual new ROM. New Age advances independently modulo U.')

def geometry(record=r.record):
    """Finite actual-ROM endpoint check used with the symbolic routing lemma."""
    length=len(p.base_rom());first=[];last=[]
    for address in range(f.Q):
        row=record(address)
        if row['first']:first.append(address)
        if row['last']:last.append(address)
    assert first==[0] and last==[length-1],('ROM endpoint defect',first,last)
    checked=0
    for address in range(length):
        for direction in (c.RIGHT,c.LEFT):
            target=(address if record(address)['last'] else address+1) if direction==c.RIGHT else (address if record(address)['first'] else address-1)
            assert 0<=target<length,('head escaped',address,direction,target)
            checked+=1
    # A wait stays at its source, and HALT removes the head, both preserving confinement.
    # At every reset/first vote, only the unique first record can acquire a head.
    return dict(passed=True,core_cells=length,colony_cells=f.Q,first=first,last=last,
                directed_source_positions_checked=checked,minimum_gap_to_next_colony_core=f.Q-length,
                ROM_sha256=hashlib.sha256(p.base_rom().tobytes()).hexdigest())

def certify(loaded):
    result=validate_premises(loaded)
    replay=json.loads(json.dumps(bridge.certify()))
    assert all(loaded['clock'][key]==value for key,value in replay.items()),'clock bridge replay changed'
    spatial=structure.support(f.self_description());geom=geometry()
    assert geom['minimum_gap_to_next_colony_core']>=8
    assert spatial['maximum_head_controller_logical_radius']<=1
    assert spatial['static_fields_preserved']==49
    result.update(geometry=geom,spatial_support=spatial,
                  canonical_structural_domain_preserved=True,
                  structural_induction='New unique endpoints confine disjoint head routes. Core separation admits the zero/one-head local cases. Output-image and zero-inactive-controller conclusions restore coherence; metadata remains fixed. Mail, flags, Signals and Wf stay unrestricted.',
                  limitation='Transferred local identities and canonical structural induction, not Data correctness, a whole-period proof, damaged-geometry repair or backend equivalence.')
    return result


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True);args=parser.parse_args();out=Path(args.output)
    if out.exists():raise FileExistsError('preserve evidence')
    start=time.perf_counter();result=certify(load_inputs())
    result.update(descriptor_sha256=f.self_description().digest(),rom_sha256=hashlib.sha256(p.base_rom().tobytes()).hexdigest(),
                  input_sha256={str(ROOT/file):sha(ROOT/file) for file in SOURCES.values()},
                  source_sha256={str(path):sha(path) for path in (Path(__file__),Path(bridge.__file__),Path(old_period.__file__),Path(structure.__file__),Path(structure.head.__file__),Path(p.__file__),Path(r.__file__))},
                  seconds=time.perf_counter()-start,host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='spatial_support'},indent=2),flush=True)

if __name__=='__main__':main()
