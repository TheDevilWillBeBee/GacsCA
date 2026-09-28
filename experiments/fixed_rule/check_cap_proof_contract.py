"""Validate complete raw-output coverage before invoking a cap identity proof.

The original proofs use zip over known complete descriptors. This front-end also
rejects omitted/extra outputs and malformed DAG references explicitly, so it is
safe to use with mutated descriptors in negative tests.
"""
import argparse,hashlib,json,time
from pathlib import Path
from gacsca.fixed_rule.wordcode import NAND,ADD,SHR,EQ,LT,LIT,MASK
from . import prove_cap_orbit as candidate,prove_serial_vote_cap as serial


def checked(checker,description=None):
    f=checker.f;d=f.self_description() if description is None else description
    if d.inputs!=11*f.FIELDS or len(d.outputs)!=f.FIELDS:raise ValueError('all raw neighborhood/controller words required')
    for index,(op,a,b) in enumerate(d.operations):
        if op==LIT:
            if not isinstance(a,int) or not 0<=a<=MASK:raise ValueError('invalid literal')
        elif op not in (NAND,ADD,SHR,EQ,LT) or any(not isinstance(v,int) or not 0<=v<d.inputs+index for v in (a,b)):raise ValueError('invalid or forward instruction reference')
    if any(not isinstance(v,int) or not 0<=v<d.wires for v in d.outputs):raise ValueError('invalid output reference')
    return checker.prove(d)


def execute(output):
    output=Path(output)
    if output.exists():raise FileExistsError('preserve evidence')
    start=time.monotonic();rows={name:checked(checker) for name,checker in (('candidate_b',candidate),('serial_vote',serial))}
    result=dict(passed=True,complete_raw_output_contract=True,proofs=rows,seconds=time.monotonic()-start,verifier_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',required=True,type=Path);execute(parser.parse_args().output)
