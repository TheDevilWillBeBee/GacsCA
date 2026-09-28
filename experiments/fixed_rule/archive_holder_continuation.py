"""Preserve owned source/report state and verify every holder evidence dependency."""
import argparse,hashlib,io,json,tarfile
from pathlib import Path


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def execute(output):
    root=Path(__file__).resolve().parents[2];stem=Path(output);manifest=stem.with_suffix('.json');archive_path=stem.with_suffix('.tar.gz')
    if manifest.exists() or archive_path.exists():raise FileExistsError('preserve earlier bundle')
    checked=[];dependencies={}
    for path in sorted((root/'figs/fixed_rule').glob('holder_*.json')):
        record=json.loads(path.read_text())
        if not isinstance(record,dict):continue
        sources=record.get('source_sha256',{})
        if not isinstance(sources,dict):continue
        for name,digest in sources.items():
            source=(root/name).resolve();relative=str(source.relative_to(root));assert sha(source)==digest,(path.name,name)
            if relative in dependencies:assert dependencies[relative]==digest,relative
            dependencies[relative]=digest
        if sources:checked.append(path.name)
    files=[]
    for directory,extensions in (('gacsca/fixed_rule',('*.py','*.c','*.cpp','*.h','*.cu')),('tests/fixed_rule',('*.py',)),('experiments/fixed_rule',('*.py',)),('Report/fixed_rule',('*.md','*.txt'))):
        for extension in extensions:files.extend((root/directory).glob(extension))
    contents={str(path.relative_to(root)):path.read_bytes() for path in sorted(set(files))}
    with tarfile.open(archive_path,'x:gz') as archive:
        for name,data in contents.items():row=tarfile.TarInfo(name);row.size=len(data);archive.addfile(row,io.BytesIO(data))
    evidence={str(path.relative_to(root)):sha(path) for path in sorted((root/'figs/fixed_rule').glob('holder_*')) if path.is_file() and path.suffix in ('.json','.npz','.log')}
    result=dict(passed=True,checked_manifests=checked,distinct_frozen_dependencies=len(dependencies),source_files=len(contents),source_sha256={name:hashlib.sha256(data).hexdigest() for name,data in contents.items()},evidence_sha256=evidence,archive_sha256=sha(archive_path),scope='owned fixed_rule files only; verified immutable holder experiment/proof dependencies and preserved current reports/tests; no shared integration or GPU artifacts changed')
    manifest.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k not in ('source_sha256','evidence_sha256')},indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',required=True,type=Path);execute(p.parse_args().output)
