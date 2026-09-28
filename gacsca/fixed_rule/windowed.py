"""Address-derived program projection of the complete computing substrate.

Physical cells have NO mutable opcode/operand/index/boundary records. A fixed ROM
provides these seven fields from the cell's raw 16-bit Address. The simulated
370-bit rule includes every evaluator and packet transition. Its conjugacy with
this 237-bit projected rule is essential; this is not a claim that a test ROM
constitutes self-reference or that static Address supplies Gray maintenance.
"""
from dataclasses import dataclass
from functools import lru_cache
import hashlib
import json
import numpy as np
from . import window_rule, window_program

STATIC = ('kind','index','a','b','d','first','last')
SCHEMA = tuple((name,width) for name,width in window_rule.SCHEMA if name not in STATIC)
WIDTH = sum(width for _,width in SCHEMA)
NEIGHBORHOOD = (-1,0,1)
COL = {name:i for i,(name,_) in enumerate(SCHEMA)}


@dataclass(frozen=True)
class Cell:
    bit: int = 0
    head: int = 0
    phase: int = 0
    pc: int = 0
    ra: int = 0
    rb: int = 0
    rd: int = 0
    value: int = 0
    direction: int = 0
    lp_target: int = 0
    lp_bit: int = 0
    lp_cross: int = 0
    lp_valid: int = 0
    rp_target: int = 0
    rp_bit: int = 0
    rp_cross: int = 0
    rp_valid: int = 0
    address: int = 0

    def __post_init__(self):
        for name,width in SCHEMA:
            if not isinstance(getattr(self,name),int) or not 0 <= getattr(self,name) < 1 << width:
                raise ValueError(f'{name} outside projected alphabet')


@lru_cache(maxsize=1)
def rom():
    """One immutable description-derived ROM, independent of size or depth."""
    template = window_program.template()
    indices = [window_program.COL[name] for name in STATIC]
    if np.any(template[:,indices]>65535):
        raise ValueError('fixed ROM constant representation capacity exceeded')
    table = np.ascontiguousarray(template[:,indices],dtype=np.uint16)
    table.flags.writeable = False
    return table


def static_record(address):
    if address < len(rom()):
        return dict(zip(STATIC,map(int,rom()[address])))
    # Total extension for legal Address words outside the chosen colony length.
    return dict(kind=window_rule.PADDING_KIND,index=address,a=0,b=0,d=0,first=0,last=0)


def lift(cell):
    return window_rule.Cell(**static_record(cell.address),
                          **{name:getattr(cell,name) for name,_ in SCHEMA})


def project(cell):
    return Cell(**{name:getattr(cell,name) for name,_ in SCHEMA})


def local_step(left,center,right):
    return project(window_rule.local_step(lift(left),lift(center),lift(right)))


def step_ring(cells):
    return tuple(local_step(cells[i-1],cell,cells[(i+1)%len(cells)])
                 for i,cell in enumerate(cells))


def encode_cell(cell):
    return tuple((getattr(cell,name)>>i)&1 for name,width in SCHEMA for i in range(width))


def decode_cell(bits):
    if len(bits)!=WIDTH or any(bit not in (0,1) for bit in bits):
        raise ValueError('complete projected raw word required')
    values,offset={},0
    for name,width in SCHEMA:
        values[name]=sum(int(bits[offset+i])<<i for i in range(width))
        offset+=width
    return Cell(**values)


def identity():
    records=json.dumps(rom().tolist(),separators=(',',':')).encode()
    return dict(schema=SCHEMA,width=WIDTH,neighborhood=NEIGHBORHOOD,
                rom_sha256=hashlib.sha256(records).hexdigest(),
                simulated_rule=window_rule.identity(),
                representation='complete window_rule rule with local program-record canonicalization')


def array_from_cells(cells):
    return np.array([[getattr(cell,name) for name,_ in SCHEMA] for cell in cells],dtype=np.uint32)


def cells_from_array(array):
    return tuple(Cell(**{name:int(row[i]) for name,i in COL.items()}) for row in array)


def project_array(array):
    return np.ascontiguousarray(array[:,[window_program.COL[name] for name,_ in SCHEMA]])


def lift_array(array):
    output=np.zeros((len(array),len(window_rule.SCHEMA)),dtype=np.uint32)
    for name,_ in SCHEMA:
        output[:,window_program.COL[name]]=array[:,COL[name]]
    addresses=array[:,COL['address']]
    output[:,window_program.COL['index']]=addresses
    output[:,window_program.COL['kind']]=window_rule.PADDING_KIND
    valid=addresses<len(rom())
    for j,name in enumerate(STATIC):
        output[valid,window_program.COL[name]]=rom()[addresses[valid],j]
    return output


def encode_cores(cells):
    """Block-local E_G = pi E_F lift. No neighbor initialization is performed."""
    return project_array(window_program.encode_cores(tuple(lift(cell) for cell in cells)))


def decode_cores(array):
    geometry=window_program.layout()
    if len(array)%geometry.computation_cells:
        raise ValueError('partial colony')
    result=[]
    for base in range(0,len(array),geometry.computation_cells):
        lifted=window_rule.decode_cell(array[base+geometry.info_start:base+geometry.info_start+window_rule.WIDTH,
                                          COL['bit']].tolist())
        raw=project(lifted)
        if lift(raw)!=lifted:
            raise ValueError('encoded static program does not match encoded Address')
        result.append(raw)
    return tuple(result)


def check_boundary(array):
    return window_program.check_boundary(lift_array(array))
