"""Address-derived program projection of the complete computing substrate.

Physical cells have NO mutable opcode/operand/index/boundary records. A fixed ROM
provides these seven fields from the cell's raw 16-bit Address. The simulated
193-bit rule includes every evaluator and packet transition. Its conjugacy with
this 125-bit projected rule is essential; this is not a claim that a test ROM
constitutes self-reference or that static Address supplies Gray maintenance.
"""
from dataclasses import dataclass
from functools import lru_cache
import hashlib
import json
import numpy as np
from . import addressed, addressed_block

STATIC = ('kind','index','a','b','d','first','last')
SCHEMA = tuple((name,width) for name,width in addressed.SCHEMA if name not in STATIC)
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
    template = addressed_block.template()
    indices = [addressed_block.COL[name] for name in STATIC]
    table = np.ascontiguousarray(template[:,indices],dtype=np.uint16)
    table.flags.writeable = False
    return table


def static_record(address):
    if address < len(rom()):
        return dict(zip(STATIC,map(int,rom()[address])))
    # Total extension for legal Address words outside the chosen colony length.
    return dict(kind=addressed.MEM,index=address,a=0,b=0,d=0,first=0,last=0)


def lift(cell):
    return addressed.Cell(**static_record(cell.address),
                          **{name:getattr(cell,name) for name,_ in SCHEMA})


def project(cell):
    return Cell(**{name:getattr(cell,name) for name,_ in SCHEMA})


def local_step(left,center,right):
    return project(addressed.local_step(lift(left),lift(center),lift(right)))


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
                simulated_rule=addressed.identity(),
                representation='complete unprojected rule restricted via static-Address conjugacy')


def array_from_cells(cells):
    return np.array([[getattr(cell,name) for name,_ in SCHEMA] for cell in cells],dtype=np.uint32)


def cells_from_array(array):
    return tuple(Cell(**{name:int(row[i]) for name,i in COL.items()}) for row in array)


def project_array(array):
    return np.ascontiguousarray(array[:,[addressed_block.COL[name] for name,_ in SCHEMA]])


def lift_array(array):
    output=np.zeros((len(array),len(addressed.SCHEMA)),dtype=np.uint32)
    for name,_ in SCHEMA:
        output[:,addressed_block.COL[name]]=array[:,COL[name]]
    addresses=array[:,COL['address']]
    output[:,addressed_block.COL['index']]=addresses
    valid=addresses<len(rom())
    for j,name in enumerate(STATIC):
        output[valid,addressed_block.COL[name]]=rom()[addresses[valid],j]
    return output


def encode(cells):
    """Block-local E_G = pi E_F lift. No neighbor initialization is performed."""
    return project_array(addressed_block.encode(tuple(lift(cell) for cell in cells)))


def decode(array):
    geometry=addressed_block.layout()
    if len(array)%geometry.colony_cells:
        raise ValueError('partial colony')
    result=[]
    for base in range(0,len(array),geometry.colony_cells):
        lifted=addressed.decode_cell(array[base+geometry.info_start:base+geometry.info_start+addressed.WIDTH,
                                          COL['bit']].tolist())
        raw=project(lifted)
        if lift(raw)!=lifted:
            raise ValueError('encoded static program does not match encoded Address')
        result.append(raw)
    return tuple(result)


def check_boundary(array):
    return addressed_block.check_boundary(lift_array(array))
