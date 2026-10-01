"""Address projection of the compact 8Q circuit's immutable ROM.

For dual-pass successors the 341 spatial and 49 holder static input words
come from immutable address tables of that fixed rule. The projected words
are initial data for SOURCE holder Data; physical transitions never call this
module. Continuous colony maintenance remains a separate obligation.
"""
from functools import lru_cache
import hashlib

from gacsca.fixed_rule import spatial_codec8
from gacsca.fixed_rule import spatial_epoch8 as spatial
from gacsca.fixed_rule import stream28_compact_layout as layout_module
from gacsca.fixed_rule import stream28_compact_vote8 as combined
from gacsca.fixed_rule import stream28_holder_rule as holder
from gacsca.fixed_rule import stream28_dual_holder_rom as dual_holder_rom
from experiments.fixed_rule.build_compact8_circuit import initial_cells,static_plan


@lru_cache(maxsize=3)
def template(dual_pass=False,u20=False):
    """The one fixed circuit layout with all evolving input words zero."""
    inputs=static_plan(dual_pass,u20)['routes'].program.inputs
    rows=initial_cells((0,)*inputs,dual_pass,u20)
    assert len(rows)==spatial.Q
    assert all(row.address==site for site,row in enumerate(rows))
    return rows


def spatial_input_wires():
    return tuple(wire for wire in layout_module.build().static_inputs
                 if wire%combined.FIELDS>=holder.FIELDS)


def holder_input_wires():
    return tuple(wire for wire in layout_module.build().static_inputs
                 if wire%combined.FIELDS<holder.FIELDS)


def project_spatial_static(center_address,words,dual_pass=False,u20=False):
    """Fill each used upper spatial-ROM input from its canonical address.

    Evolving inputs and holder-ROM inputs are preserved verbatim. This is a
    host-side initial-data operation, not a host-side simulated transition.
    """
    if not 0<=center_address<spatial.Q:
        raise ValueError('canonical upper cell address required')
    if len(words)!=static_plan(dual_pass,u20)['routes'].program.inputs:
        raise ValueError('complete typed local input required')
    result=list(words)
    rows=template(dual_pass,u20)
    for wire in spatial_input_wires():
        neighbor,field=divmod(wire,combined.FIELDS)
        site=(center_address+neighbor-7)%spatial.Q
        local_field=field-holder.FIELDS
        result[wire]=spatial_codec8.encode_cell(rows[site])[local_field]
    return tuple(result)


def source_data_at_address(center_address,words,dual_pass=False,u20=False):
    """Data required at each physical SOURCE holder site before capture."""
    projected=project_spatial_static(center_address,words,dual_pass,u20)
    return {site:projected[wire] for site,wire in
            static_plan(dual_pass,u20)['raw_sources'].items()}


def project_all_dual_static(center_address,words,u20=False):
    """Derive all 390 used static words from the one dual-pass ROM table.

    The holder table includes the provisional short SEND controller. This
    projection is initial-data compilation; full holder dynamics and ROM
    correction are separate obligations.
    """
    result=list(project_spatial_static(center_address,words,True,u20))
    for wire in holder_input_wires():
        neighbor,field=divmod(wire,combined.FIELDS)
        site=(center_address+neighbor-7)%spatial.Q
        name=holder.SCHEMA[field][0]
        result[wire]=dual_holder_rom.holder_static_fields(site)[name]
    return tuple(result)


@lru_cache(maxsize=3)
def spatial_static_digest(dual_pass=False,u20=False):
    """Hash the immutable spatial fields at all 8,192 addresses."""
    dynamic={1,3,*range(spatial_codec8.FIELDS-12,spatial_codec8.FIELDS)}
    sha=hashlib.sha256()
    for row in template(dual_pass,u20):
        for index,value in enumerate(spatial_codec8.encode_cell(row)):
            if index not in dynamic:sha.update(int(value).to_bytes(8,'little'))
    return sha.hexdigest()
