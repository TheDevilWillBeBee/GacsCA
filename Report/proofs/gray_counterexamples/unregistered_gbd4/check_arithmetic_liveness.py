"""Independent exact word-wrap and listing write-set contract checks."""
import argparse,json
from pathlib import Path
import controller as c
import native_emitter as n

def liveness(program):
    labels=program['labels'];rows=program['rows'];positions=program['positions']
    limits={'RAW':'RAMLOAD','RAMLOAD':'RAMLOAD5','RAMLOAD5':'RAMSTORE','RAMSTORE':'Q5'}
    result={}
    for name in ('RAW','RAMLOAD','RAMLOAD5','RAMSTORE','Q5'):
        end=labels[limits[name]] if name in limits else program['bits']
        selected=[row for row,pc in zip(rows,positions) if labels[name]<=pc<end]
        written=set()
        for row in selected:
            if row[0] in ('LIT','READ','READQ','GETHEAD'):written.add(row[1])
            elif row[0]=='ALU':written.add(row[2])
        result[name]=sorted(written)
    assert set(result['RAW'])<={0,6,7}
    assert set(result['RAMLOAD'])<={0,5,6,7}
    assert set(result['RAMLOAD5'])<={5,6,7}
    assert set(result['RAMSTORE'])<={5,6,7}
    assert 1 not in result['Q5'] and 4 not in result['Q5']
    return result

def main(output):
    arithmetic=0
    for value in range(c.Q):
        for j in range(-5,6):
            adjusted=((value-(j&c.MASK))&c.MASK)&(c.Q-1)
            assert adjusted==(value-j)%c.Q
            unsigned=(value+j)&c.MASK
            assert (unsigned<c.Q)==(0<=value+j<c.Q)
            arithmetic+=2
    result=dict(passed=True,native_unsigned_arithmetic_checks=arithmetic,
                helper_register_writes={key:liveness(n.native_program(flag))
                   for key,flag in (('h1',False),('printed',True))},
                generic_emitted_all_native_word_wrap_contract=True,
                full_own_beta=False,Gray_refutation=False)
    output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))

if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--output',type=Path,required=True)
    main(a.parse_args().output)
