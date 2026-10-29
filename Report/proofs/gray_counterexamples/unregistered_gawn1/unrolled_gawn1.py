"""GAWN1: isolated NEW own-ROM instance, with software-unrolled SF voting.

Physical equations/ISA/native padded extension are those of GAWN0.
The fixed newly emitted ROM changes the instantiated rule; G17 and all
previous frozen sources/ROMs stay unchanged. No noisy theorem is asserted.
"""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'unregistered_gawn0'))
from normalized_gawn0 import *

