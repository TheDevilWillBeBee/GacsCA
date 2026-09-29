"""Freeze owned suffix implementation, audits, reports, and compact evidence."""
import argparse
import hashlib
import io
import json
from pathlib import Path
import tarfile


def archive(stem):
    root=Path(__file__).resolve().parents[2];stem=Path(stem)
    for ext in ('.json','.tar.gz'):
        if stem.with_suffix(ext).exists():raise FileExistsError('preserve prior evidence')
    files=set()
    for pattern in ('gacsca/fixed_rule/delivery_control*','gacsca/fixed_rule/delivery_composed*','gacsca/fixed_rule/flag_*.py','gacsca/fixed_rule/flag_*.c','gacsca/fixed_rule/flag_*.cpp','tests/fixed_rule/test_flag_*.py','tests/fixed_rule/test_delivery_control.py','tests/fixed_rule/test_delivery_composed.py','experiments/fixed_rule/*flag_*.py','experiments/fixed_rule/*delivery_control*.py','experiments/fixed_rule/*delivery_forcing*.py','figs/fixed_rule/*flag_*tests_v*.log','figs/fixed_rule/delivery_control*.json','figs/fixed_rule/delivery_forcing*.json','figs/fixed_rule/delivery_composed*.log','figs/fixed_rule/delivery_control_tests*.log','figs/fixed_rule/flag_*failure*.json','figs/fixed_rule/flag_*stop*.json','figs/fixed_rule/flag_byte_bounded*.json','figs/fixed_rule/flag_byte*execution_v1.log','figs/fixed_rule/flag_byte_bounded_v*.log','figs/fixed_rule/suffix_source_preservation_v1.json'):
        files.update(path for path in root.glob(pattern) if path.is_file())
    files.update(root/name for name in ('Report/fixed_rule/STATUS.md','Report/fixed_rule/SUFFIX.md','experiments/fixed_rule/archive_suffix.py'))
    content={str(path.relative_to(root)):path.read_bytes() for path in sorted(files)}
    with tarfile.open(stem.with_suffix('.tar.gz'),'x:gz') as bundle:
        for name,data in content.items():info=tarfile.TarInfo(name);info.size=len(data);bundle.addfile(info,io.BytesIO(data))
    result=dict(scope=__doc__,file_sha256={name:hashlib.sha256(data).hexdigest() for name,data in content.items()},archive_sha256=hashlib.sha256(stem.with_suffix('.tar.gz').read_bytes()).hexdigest())
    stem.with_suffix('.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(files=len(content),archive_sha256=result['archive_sha256'])))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True);archive(parser.parse_args().output)
