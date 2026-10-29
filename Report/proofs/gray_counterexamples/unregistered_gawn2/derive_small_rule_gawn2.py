"""Derive an explicit isolated finite Q4096 physical rule, once only.

This is a source-copy derivation with listed parameter/schedule changes,
not mutation of an imported frozen module's global constants.
"""
from pathlib import Path
import hashlib,json
HERE=Path(__file__).resolve().parent;GRAY=HERE.parent

def source():
    old0=GRAY/'unregistered_gaw0/gray_wider_word_gaw0.py'
    old2=GRAY/'unregistered_gaw2/gray_three_gather_gaw2r.py'
    oldnative=GRAY/'gray_moving_word_v2.py'
    head=old0.read_text().split('\ndef local_transition(cells,beta):',1)[0]
    head=head.replace('Q=8192;U=128*Q;', 'Q=4096;U=128*Q;')
    head=head.replace('CODE_CAPACITY=Q;PC_BITS=13','CODE_CAPACITY=Q;PC_BITS=12')
    head=head.replace("(8191 if n=='addr' else SMALL_MASK if n=='age' else 1)","(Q-1 if n=='addr' else U-1 if n=='age' else 1)")
    head=head.replace('return predecessor.scalar_native(native)','return scalar_native(native)')
    head=head.replace('def computed_primary(cells,y):','def _physical_primary(cells,y):')
    start=head.index('"""');stop=head.index('"""',start+3)+3
    head='''"""GAWN2: explicitly NEW fixed Q4096/U524288/radius8/Word100 instance.

Native GF/Age widths12/19, twelve-bit programme jump operands;
three gathers, native-only early pass,100Q late reset/birth,127Q stop.
Own immutable ROM is separately emitted. Original lambda24/c104 retained.
All word/immutable/radius/h1 departures from faithful Gray remain.
No damaged-lower or iid reliability theorem is asserted here.
"""'''+head[stop:]
    native=oldnative.read_text().split('\ndef scalar_native(cells):',1)[1].split('\ndef columns():',1)[0]
    native='\ndef scalar_native(cells):'+native
    native=native.replace('base=old.literal_maintenance.scalar(cells);c=cells[0]',
        'base=predecessor.old.literal_maintenance.scalar(cells,Q=Q,U=U);c=cells[0]')
    tail=old2.read_text().split('STAGE_STARTS=',1)[1]
    tail='STAGE_STARTS='+tail
    tail=tail.replace('(0,32*Q,64*Q,96*Q,102*Q)','(0,32*Q,64*Q,96*Q,100*Q)')
    tail=tail.replace('base.FIELD_NAMES','BASE_FIELD_NAMES').replace('class ROM(base.ROM):','class ROM(BASE_ROM):').replace('class Cell(base.Cell):','class Cell(BASE_CELL):')
    tail=tail.replace('def local_transition(cells,beta):','def _physical_transition(cells,beta):')
    tail=tail.replace('102*Q+1','100*Q+1').replace('<=120*Q','<=127*Q')
    aliases='''
BASE_FIELD_NAMES=FIELD_NAMES
BASE_ROM=ROM
BASE_CELL=Cell
GF_BITS=12;AGE_BITS=19
GF_MASK=Q-1;AGE_MASK=U-1
NATIVE_WIDTHS=(GF_BITS,AGE_BITS,1,1,1,1)
LATE_RESET=100*Q;LATE_BIRTH=LATE_RESET+1;ACTIVE_END=127*Q
'''
    projection='''

def project(cell):
    return replace(cell,**{name:getattr(cell,name)&((1<<width)-1)
        for name,width in zip(NATIVE_NAMES,NATIVE_WIDTHS)})

def project_neighborhood(cells):
    return {j:project(cell) for j,cell in cells.items()}

def computed_primary(cells,y):
    return _physical_primary(project_neighborhood(cells),y)

def local_transition(cells,beta):
    """Declared represented-D extension of the new physical alphabet rule."""
    return _physical_transition(project_neighborhood(cells),beta)
'''
    result=head+native+aliases+tail+projection
    return result,{str(p.relative_to(HERE.parents[3])):hashlib.sha256(p.read_bytes()).hexdigest()
        for p in (old0,old2,oldnative)}

def main():
    path=HERE/'small_rule_gawn2.py';assert not path.exists(),'never overwrite derived rule'
    text,origins=source();path.write_text(text)
    out=HERE.parents[3]/'figs/gray_counterexamples/unregistered_gawn2';out.mkdir(parents=True,exist_ok=True)
    meta=out/'GAWN2_rule_derivation.json';assert not meta.exists()
    record=dict(explicit_new_rule_and_constants=True,Q=4096,U=524288,native_widths=[12,19,1,1,1,1],PC_BITS=12,
        LATE_RESET=409600,LATE_BIRTH=409601,ACTIVE_END=520192,original_error_lambda=24,original_error_separation=104,
        rule_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),generator_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        source_origins_sha256=origins,G17_or_old_frozen_rules_modified=False,semantics_or_noise_theorem_proved_by_derivation=False)
    meta.write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record,sort_keys=True))

if __name__=='__main__':main()
