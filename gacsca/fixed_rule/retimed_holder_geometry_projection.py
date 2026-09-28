"""Diagnostic physical geometry projection before Wf can become nonzero.

This is not a full-state executor. Uniform clock and zero input Wf are required.
The complete descriptor supplies the independence certificate. The formulas here
independently transcribe core.maintenance, including candidate-B Flag2 erasure.
"""
import numpy as np
from . import retimed_holder_rule as f


def majority(values, fallback):
    result = fallback.copy()
    exists = np.zeros(len(fallback), dtype=bool)
    for candidate in values:
        hit = np.count_nonzero(values == candidate, axis=0) >= 3
        result[hit] = candidate[hit]
        exists |= hit
    return result, exists


def step(state, age):
    if not isinstance(state, np.ndarray) or state.dtype != np.int64 or state.ndim != 2 or state.shape[1] != 3 or len(state) < 11:
        raise ValueError('complete Address/Flag1/Flag2 ring required')
    if type(age) is not int or not 0 <= age < 32768:
        raise ValueError('certified early uniform clock required')
    if np.any(state[:,0] < 0) or np.any(state[:,0] >= f.Q) or np.any(state[:,1:] < 0) or np.any(state[:,1:] > 1):
        raise ValueError('geometry outside fixed alphabet')
    address, flag1, flag2 = state.T
    near = {j:np.roll(state, -j, axis=0) for j in range(-5,6)}
    adjusted = {j:(near[j][:,0]-j) % f.Q for j in (*range(-5,0),*range(1,6))}
    right, exists = majority(np.array([adjusted[j] for j in range(1,6)]), address)
    inside = {j:exists & (right+j >= 0) & (right+j < f.Q) for j in range(-5,6)}
    inconsistent = ~exists | (sum(inside[j] & (near[j][:,0] != (right+j) % f.Q) for j in range(-5,0)) >= 3)
    right_flags = sum(inside[j] & (near[j][:,1] != 0) for j in range(1,6))
    out1 = inconsistent | (right_flags >= 3) | ((flag1 != 0) & (right_flags >= 2))
    left_flags = sum(near[j][:,2] for j in range(-5,0))
    inside_left_flags = sum(inside[j] & (near[j][:,2] != 0) for j in range(-5,0))
    d3 = ~exists & ((age+1) % 16 == 0)
    on = (inside_left_flags >= 4) | (out1 & (left_flags >= 4)) | d3
    erase = (~out1 & (inside_left_flags <= 1)) | (out1 & (left_flags == 0))
    out2 = np.where(flag2 != 0, d3 | ~erase, on)
    left, _ = majority(np.array([adjusted[j] for j in range(-1,-6,-1)]), address)
    voted = np.where(exists & (~out1 | out2), right, left)
    return np.column_stack((voted, out1, out2)).astype(np.int64)
