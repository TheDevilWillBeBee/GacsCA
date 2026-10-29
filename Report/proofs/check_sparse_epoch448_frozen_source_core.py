#!/usr/bin/env python3
"""SP18 finite adversarial frozen-clock/displaced-packet source core.

Reuse the pinned driven source-core geometry, but overwrite all physical
bits with the explicitly retained adversarial words. GF has phase -6;
Age is frozen at T_wf; native F2 is zero; F1/WF1 are one. A fresh root6
packet is planted at sites7..11 every kernel row. No rule is changed.
"""
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
import check_sparse_epoch448_source_core as prior


def main():
    source=Path(prior.__file__).read_text()
    source=source.replace('default=20','default=4')
    source=source.replace("stem = 'SP18_epoch_source_core'","stem = 'SP18_epoch_frozen_source_core'")
    old="                values=shifted_reference[:,sites].copy()"
    new="""                values=np.zeros((candidate.W,len(sites)),dtype=bool)
                candidate.set_field(values,'addr',(sites-6)%p.Q)
                candidate.set_field(values,'age',p.age_code(p.T_wf))
                candidate.set_field(values,'f1',1)
                candidate.set_field(values,'wf1',1)
                packet_sites=(sites>=7)&(sites<=11)
                candidate.set_field(values,'wf2',packet_sites.astype(np.int64))
                candidate.set_field(values,'packet_valid',packet_sites.astype(np.int64))
                candidate.set_field(values,'packet_tag',np.where(packet_sites,sites-7,0))"""
    assert source.count(old)==1
    source=source.replace(old,new)
    source=source.replace("driver_sha256=digest(Path(__file__)),",
        "driver_sha256=digest(Path(__file__)), "
        "inherited_driver_sha256=digest(Path(prior.__file__)),")
    source=source.replace("overwrite_rule='copy the evolving one-site-shifted periodic reference, all physical bits',",
        "overwrite_rule='all bits explicitly set: GF phase -6, frozen T_wf Age, F1/WF1=1, F2=0, root6 five-word packet/count0, other bits zero',")
    source=source.replace("core_begin=begin,core_tau=tau,overwrite_batches=17,total_overwrites=257,",
        "core_begin=begin,core_tau=tau,overwrite_batches=17,total_overwrites=257,"
        "overwrite_GF_phase=-6,overwrite_frozen_clock=p.T_wf,planted_packet_origin=6,")
    namespace=dict(prior.__dict__,prior=prior,__file__=__file__)
    exec(compile(source,str(Path(__file__).resolve()),'exec'),namespace)
    namespace['main']()


if __name__=='__main__':
    main()
