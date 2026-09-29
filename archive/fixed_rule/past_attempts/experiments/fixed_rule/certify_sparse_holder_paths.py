"""Recheck new-ROM physical paths and packet times with unchanged local lemmas.

Function copies bind only diagnostic constructors to the candidate ROM. No
module globals or evolving interpreter are changed, and no depth is an input.
"""
import argparse
import hashlib
import json
from pathlib import Path
import resource
import sys
import time
from types import FunctionType
from gacsca.fixed_rule import sparse_holder_program as p, retimed_holder_rule as f
from experiments.fixed_rule import certify_retimed_holder_paths as reference
from experiments.fixed_rule import certify_retimed_holder_mail_schedule as mail


def bind(function, **replacements):
    namespace = dict(function.__globals__)
    namespace.update(p=p, **replacements)
    result = FunctionType(function.__code__, namespace, function.__name__,
                          function.__defaults__, function.__closure__)
    result.__kwdefaults__ = function.__kwdefaults__
    return result


class Ordinary(reference.Ordinary):
    __init__ = bind(reference.Ordinary.__init__)
    check = bind(reference.Ordinary.check)


class Metadata(reference.Metadata):
    __init__ = bind(reference.Metadata.__init__)
    check = bind(reference.Metadata.check)


class Dispatch(reference.Dispatch):
    __init__ = bind(reference.Dispatch.__init__)
    check = bind(reference.Dispatch.check)


def certify():
    clock = 'figs/fixed_rule/retimed_holder_clock_transfer_v1.json'
    # dispatch.routes originally names the old proof globals, unlike methods
    # already bound by reference. Bind through its proven retimed wrapper first.
    retimed_bind = lambda function: bind(reference.bind(function))
    result = bind(reference.certify, Ordinary=Ordinary, Metadata=Metadata,
                  Dispatch=Dispatch, bind=retimed_bind,
                  verify_dependencies=bind(reference.verify_dependencies))(clock)
    loaded = {'ordinary': {'rows': result['ordinary_rows']},
              'meta': {'paths': result['metadata_paths']},
              'dispatch': {'rows': result['dispatch_rows']}}
    schedule = bind(mail.check, verify_geometry=bind(mail.verify_geometry),
                    phases=bind(mail.phases))(loaded)
    assert schedule['passed']
    result['packet_schedule'] = schedule
    result['physical_descriptor_sha256'] = f.self_description().digest()
    result['ROM_sha256'] = hashlib.sha256(p.base_rom().tobytes()).hexdigest()
    result['clock_transfer_sha256'] = hashlib.sha256(Path(clock).read_bytes()).hexdigest()
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    start = time.perf_counter()
    result = certify()
    result.update(seconds=time.perf_counter()-start,
                  host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    sources = {Path(__file__).resolve()}
    for module in tuple(sys.modules.values()):
        filename = getattr(module, '__file__', None)
        if filename and '/fixed_rule/' in str(Path(filename).resolve()):
            sources.add(Path(filename).resolve())
    result['source_sha256'] = {str(path.relative_to(Path.cwd())):
                              hashlib.sha256(path.read_bytes()).hexdigest()
                              for path in sorted(sources)}
    with args.output.open('x') as stream:
        stream.write(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: v for k, v in result.items() if k not in (
        'ordinary_rows', 'metadata_paths', 'dispatch_rows', 'source_sha256', 'packet_schedule')}, indent=2))


if __name__ == '__main__':
    main()
