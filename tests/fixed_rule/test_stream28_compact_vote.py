"""Literal and descriptive in-place vote on three adjacent history words."""
from dataclasses import replace
import unittest

from gacsca.fixed_rule import spatial_epoch
from gacsca.fixed_rule import stream28_holder_rule as holder
from gacsca.fixed_rule import stream28_compact_vote as compact
from gacsca.fixed_rule import stream28_compact_vote_description as description
from gacsca.fixed_rule import stream28_spatial_overlay as previous


class CompactVote(unittest.TestCase):
    def neighborhood(self,physical_site,voter,values,age,marked=True):
        history={(voter-1)%holder.Q:values[0],voter%holder.Q:values[1],
                 (voter+1)%holder.Q:values[2]}
        rows=[]
        for delta in compact.NEIGHBORHOOD:
            site=(physical_site+delta)%holder.Q
            static={f'p{offset+3}_kind':0 for offset in range(-3,4)}
            static.update({f'p{offset+3}_a':
                           compact.VOTE_SELF if marked and
                           (site+offset)%holder.Q==voter else 0
                           for offset in range(-3,4)})
            copies={f's{offset+2}_data':history.get((site+offset)%holder.Q,0)
                    for offset in holder.OFFSETS}
            raw=holder.Cell(address=site,age=age,**static,**copies)
            spatial=spatial_epoch.Cell(address=site)
            rows.append(compact.Cell(raw,spatial))
        return tuple(rows)

    def test_all_five_replicas_vote_in_place(self):
        voter=2863
        values=(0xf0f0f0f0f0f0f0f0,0xcccccccccccccccc,
                0xaaaaaaaaaaaaaaaa)
        expected=compact.majority3(*values)
        program=description.build()
        self.assertEqual((program.inputs,len(program.outputs)),
                         (15*compact.FIELDS,compact.FIELDS))
        self.assertEqual((compact.WIDTH,compact.NEIGHBORHOOD),
                         (previous.WIDTH,previous.NEIGHBORHOOD))
        for age in holder.VOTE_AGES:
            for offset in holder.OFFSETS:
                site=(voter-offset)%holder.Q
                neighbors=self.neighborhood(site,voter,values,age)
                actual=compact.local_step(neighbors)
                self.assertEqual(getattr(actual.holder,f's{offset+2}_data'),
                                 expected)
                words=tuple(word for row in neighbors
                            for word in compact.encode_cell(row))
                self.assertEqual(program.evaluate(words),
                                 compact.encode_cell(actual))

    def test_marker_and_vote_age_gate_the_change(self):
        site=2863
        values=(0,0xffffffffffffffff,0)
        marked=self.neighborhood(site,site,values,holder.VOTE_AGES[0])
        unmarked=self.neighborhood(site,site,values,holder.VOTE_AGES[0],False)
        off_age=self.neighborhood(site,site,values,holder.VOTE_AGES[0]-1)
        self.assertEqual(compact.local_step(marked).holder.s2_data,0)
        self.assertEqual(compact.local_step(unmarked),previous.local_step(unmarked))
        self.assertEqual(compact.local_step(off_age),previous.local_step(off_age))
        with self.assertRaises(ValueError):compact.local_step(marked[:-1])

    def test_one_damaged_copy_per_input_is_corrected_before_vote(self):
        voter=2863
        values=(0x123456789abcdef0,0x13579bdf02468ace,
                0x55aa55aa55aa55aa)
        rows=list(self.neighborhood(voter,voter,values,holder.VOTE_AGES[0]))
        for delta in (-1,0,1):
            index=7+delta
            row=rows[index]
            rows[index]=replace(row,holder=replace(
                row.holder,s2_data=row.holder.s2_data^((1<<64)-1)))
        after=compact.local_step(tuple(rows))
        self.assertEqual(after.holder.s2_data,compact.majority3(*values))
        words=tuple(word for row in rows for word in compact.encode_cell(row))
        self.assertEqual(description.build().evaluate(words),
                         compact.encode_cell(after))


if __name__=='__main__':unittest.main()
