"""Explicit packet-supported pressure revision, separate from SP14.

Keep every packet/coded output unchanged. Add its existing unrestricted
packet-cohort witness to computed maintenance pressure. A proper packet
then supplies pressure even when younger coded words mask its votes.
No birth guard, source initialization or reliability theorem is supplied
by this module alone. The radius-six guard is a separate proved proposal.
"""
import proposed_framed_service as original


def build(n, cells):
    result = original.build(n, cells)
    result['service_force'] = n.OR(result['service_force'], result['packet_any_cohort'])
    return result
