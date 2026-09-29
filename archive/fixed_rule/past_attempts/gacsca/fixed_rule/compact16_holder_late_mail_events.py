"""Late sparse physical events preserving coherent mail and multiple heads.

Reuse complete local packet transitions and their existing guarded transport.
Independent single-controller batches still reject mail; synchronous sparse
execution handles it exactly. This is a backend-domain extension, not a rule.
"""
import ctypes
from functools import lru_cache
import hashlib
from pathlib import Path
import subprocess
import numpy as np
from . import compact16_holder_late_multi_events as multi,compact16_holder_late_events as base
from . import compact16_holder_rule as f,compact16_holder_records as q,compact16_holder_packed as packed


def source_text():
    source=multi.source_text()
    for guard in ('  for(unsigned k=P_LP_TARGET;k<P_ADDRESS;++k)if(get(row,k))return false;',
                  'if(w.age>=PREFIX_LIMIT)for(unsigned k=P_LP_TARGET;k<P_ADDRESS;++k)if(get(row,k))w.status[3*col+2]=1;'):
        assert source.count(guard)==1;source=source.replace(guard,'/* Coherent mail is retained by the complete sparse local kernel. */')
    return source


@lru_cache(maxsize=1)
def library():
    source=source_text();controller=Path(base.independent.__file__).with_suffix('.cu').read_text();header=base.period.header()
    identity=hashlib.sha256(source.encode()+controller.encode()+header.encode()+b'nvcc-O2-sm80-late-mail-v1').hexdigest()[:20]
    directory=Path(__file__).resolve().parents[2]/'figs/fixed_rule/build'/('compact16_holder_late_mail_'+identity);directory.mkdir(parents=True,exist_ok=True);target=directory/'events.so'
    if not target.exists():
        (directory/'compact16_holder_resident_period.cu').write_text(source);(directory/'compact16_holder_resident_period_generated.h').write_text(header)
        path=directory/'compact16_holder_resident_independent.cu';path.write_text(controller)
        with (directory/'build.log').open('w') as out:subprocess.run(['/usr/local/cuda/bin/nvcc','-O2','-std=c++17','-arch=sm_80','--shared','-Xcompiler','-fPIC',str(path),'-o',str(target)],check=True,stdout=out,stderr=subprocess.STDOUT)
    lib=ctypes.CDLL(str(target))
    for name in ('rp_create','rp_free','rp_info','rp_initial','rp_bank','rp_restore_age','rp_jump','rp_step','rp_read','rp_snapshot','ri_run'):
        original=getattr(multi.library(),name);fn=getattr(lib,name);fn.argtypes=original.argtypes;fn.restype=original.restype
    return lib


def validated(raw):
    if not isinstance(raw,np.ndarray) or raw.dtype!=np.uint64 or raw.ndim!=2 or raw.shape[1]!=f.FIELDS:raise ValueError('complete raw physical array required')
    blank=raw.copy();mail=[(name,width) for name,width in f.PROCEDURE if name.startswith(('lp_','rp_'))]
    for name,width in mail:
        for d in f.OFFSETS:
            values=raw[:,f.COL[f's{d+2}_{name}']]
            if width<64 and np.any(values>=np.uint64(1<<width)):raise ValueError('mail word exceeds alphabet')
            if not np.array_equal(values,np.roll(raw[:,f.COL['s2_'+name]],-d)):raise ValueError('coherent raw mail required')
            blank[:,f.COL[f's{d+2}_{name}']]=0
    # Reuse the unchanged remaining-domain validator, then restore all mail.
    # blank is a temporary validation/allocation scaffold, never evolved.
    rows=base.logical(blank)
    for name,_ in mail:rows[:,q.COL[name]]=raw[:,f.COL['s2_'+name]]
    return blank,rows


class World(multi.World):
    def __init__(self,raw,**kwargs):
        blank,logical=validated(raw);n=len(raw)//f.Q;parts=logical.reshape(n,f.Q,len(q.SCHEMA));active=[q.COL[name] for name in base.period.ACTIVE]
        selected=[np.flatnonzero(np.any(part[:,active],axis=1)) for part in parts]
        if any(len(indices)>base.period.SLOTS for indices in selected):raise ValueError('complete sparse capacity exceeded')
        super().__init__(blank,**kwargs)
        try:
            self.lib=library()
            for col,(part,indices) in enumerate(zip(parts,selected)):
                records=np.zeros((1,base.period.SLOTS,packed.WORDS),dtype=np.uint64);records[0,:len(indices)]=packed.pack(part[indices]);counts=np.array([len(indices)],dtype=np.uint64)
                if self.lib.rp_initial(self.handle,col,1,base.period.pointer(records),base.period.pointer(counts)):raise RuntimeError('complete coherent mail upload failed')
            np.testing.assert_array_equal(self.raw(),raw)
        except BaseException:self.close();raise
