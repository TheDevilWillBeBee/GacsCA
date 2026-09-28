"""Proof verification must reject forged derivations even with new checksums."""
import contextlib
import hashlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import numpy as np
from gacsca.fixed_rule.delivery_rule import Q
from experiments.fixed_rule.flag_byte_bounded_execution import execute
from experiments.fixed_rule.audit_flag_byte import audit


class DerivationAuditTests(unittest.TestCase):
    def test_complete_proof_and_tampered_local_query(self):
        with tempfile.TemporaryDirectory(prefix='fixed_rule_proof_') as directory,contextlib.redirect_stdout(io.StringIO()):
            root=Path(directory);checkpoint=root/'checkpoint.npz';stem=root/'proof'
            np.savez_compressed(checkpoint,runs=np.array([(1,255,65535),(Q//64,0,0)],dtype=np.uint64),right_signals=np.array([0],dtype=np.uint8),left_signals=np.array([0],dtype=np.uint8))
            with patch("experiments.fixed_rule.flag_byte_bounded_execution.resource.setrlimit"):
                execute(checkpoint,stem,17)
            good=audit(stem,root/'good.json');self.assertTrue(good['passed']);self.assertGreater(good['verified_queries'],0)
            with np.load(stem.with_suffix('.npz'),allow_pickle=False) as a:data={name:a[name] for name in a.files}
            # A level-two query is a physical leaf transition. Alter its result
            # and update the outer checksum: local derivation checks must fail.
            row=next(i for i,query in enumerate(data['queries']) if data['nodes'][query[0],0]==2)
            data['queries'][row,2]=0
            np.savez_compressed(stem.with_suffix('.npz'),**data)
            meta=json.loads(stem.with_suffix('.json').read_text());meta['artifact_sha256']=hashlib.sha256(stem.with_suffix('.npz').read_bytes()).hexdigest();stem.with_suffix('.json').write_text(json.dumps(meta))
            with self.assertRaises(AssertionError):audit(stem,root/'bad.json')
            self.assertFalse((root/'bad.json').exists())


if __name__=='__main__':unittest.main()
