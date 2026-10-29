"""Isolated observation hook: union of selected-row computed differences.

Only tracking allocation, observation and download are changed. The CUDA
word transition and periodic boundary conditions are unchanged. No active
backend is edited. The hook is checked against literal NumPy separately.
"""
from contextlib import contextmanager
import ctypes
import numpy as np
from gacsca import gpu


def source(candidate,order='dfs'):
    text=gpu._source(candidate,order)
    edits=[
        ('unsigned long long *firstA, *lastA, *firstB, *lastB; };',
         'unsigned long long *firstA, *lastA, *firstB, *lastB; wd* everA; };'),
        ('        dA &= ~fresh;',
         '        dA &= ~fresh;\n        if (dA) atomicOr(&tr->everA[(size_t)ring * NW + w], dA);'),
        ('cudaFree(s->trh.firstB); cudaFree(s->trh.lastB); cudaFree(s->tr);',
         'cudaFree(s->trh.firstB); cudaFree(s->trh.lastB); cudaFree(s->trh.everA); cudaFree(s->tr);'),
        ('  t.rowsA = rows;',
         '  t.rowsA = rows;\n  cudaMalloc(&t.everA, (size_t)s->nrings * s->NW * 2 * sizeof(wd));\n'
         '  cudaMemset(t.everA, 0, (size_t)s->nrings * s->NW * 2 * sizeof(wd));'),
        ('extern "C" void sim_destroy(void* h) {',
         'extern "C" int sim_track_ever_get(void* h, unsigned int* host) {\n'
         '  Sim* s = (Sim*)h; if (!s->tr) return -1;\n'
         '  cudaMemcpy(host, s->trh.everA, (size_t)s->nrings * s->NW * 2 * sizeof(wd), cudaMemcpyDeviceToHost);\n'
         '  return (int)cudaGetLastError();\n}\nextern "C" void sim_destroy(void* h) {')]
    for old,new in edits:
        assert text.count(old)==1,old
        text=text.replace(old,new)
    return text


@contextmanager
def loader():
    original=gpu._source
    def observed(candidate,order='dfs'):
        gpu._source=original
        try:
            return source(candidate,order)
        finally:
            gpu._source=observed
    gpu._source=observed
    try:
        yield
    finally:
        gpu._source=original


def sim(candidate,nrings,colonies):
    with loader():
        return gpu.GpuSim(candidate,nrings,colonies,mode='grid')


def ever_words(sim):
    get=sim.lib.sim_track_ever_get
    get.argtypes=[ctypes.c_void_p,ctypes.c_void_p]
    get.restype=ctypes.c_int
    result=np.empty((sim.nrings,sim.N//32),dtype=np.uint32)
    err=get(sim.h,result.ctypes.data)
    if err:
        raise RuntimeError(f'CUDA tracking error {err}')
    return result


def ever_sites(sim):
    words=ever_words(sim)
    return np.unpackbits(words.view(np.uint8),axis=1,bitorder='little').astype(bool)
