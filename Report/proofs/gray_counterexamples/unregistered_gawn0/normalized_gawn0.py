"""GAWN0: explicit new own-ROM proposal with a total padded-input extension.

Physical native widths remain13/20/1/1/1/1; SF Word100 is unchanged.
Only isolated new assets use this module. No G17/frozen GAW2R edit.
"""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'unregistered_gaw2'))
import gray_three_gather_gaw2r as original
from gray_three_gather_gaw2r import *

NATIVE_WIDTHS=(13,20,1,1,1,1)

def project(cell):
    return replace(cell,**{name:getattr(cell,name)&((1<<width)-1)
        for name,width in zip(NATIVE_NAMES,NATIVE_WIDTHS)})

def project_neighborhood(cells):
    return {j:project(cell) for j,cell in cells.items()}

def local_transition(cells,beta):
    """Declared total D->A extension, evaluated with the NEW own beta."""
    return original.local_transition(project_neighborhood(cells),beta)

def computed_primary(cells,relative):
    return original.computed_primary(project_neighborhood(cells),relative)

