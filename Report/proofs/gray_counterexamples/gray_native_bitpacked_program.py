"""GPN0: concrete bit-packed Boolean programme/evaluator, no page ROM.

This separate-module encoder fails Q8192 before its native prefix fits.
It is a total abstract evaluator and a serial fetch lower-bound model,
not a physical self-simulating cellular automaton.
"""
from gacsca.netlist import Net,Compiled
import literal_maintenance

MAGIC=0x4750
HEADER=(('magic',16),('version',4),('k',5),('m',5),('w',5),
        ('inputs',16),('gates',16),('outputs',8))


def native_compiled(k=13,m=20,builder=literal_maintenance.build):
    n=Net()
    cells={j:dict(addr=[n.input(('x',j,'addr',b)) for b in range(k)],
                  age=[n.input(('x',j,'age',b)) for b in range(m)],
                  **{f:n.input(('x',j,f)) for f in ('f1','f2','wf1','wf2')})
           for j in range(-5,6)}
    native=builder(n,cells,k,m)
    for field in ('addr','age','f1','f2'):
        values=native[field] if isinstance(native[field],list) else[native[field]]
        for bit,node in enumerate(values):n.set_output((field,bit),node)
    return Compiled(n)


def number_bits(value,width):
    if not 0<=value<1<<width:raise ValueError((value,width))
    return [(value>>i)&1 for i in range(width)]


def encode(comp,k=13,m=20):
    w=(comp.n_nodes-1).bit_length()
    header=dict(magic=MAGIC,version=0,k=k,m=m,w=w,inputs=len(comp.inputs),
                gates=len(comp.gates),outputs=len(comp.outputs))
    bits=[]
    for name,width in HEADER:bits.extend(number_bits(header[name],width))
    for i,(op,a,b) in enumerate(comp.gates,2+len(comp.inputs)):
        assert op in (0,1,2) and 0<=a<i and 0<=b<i
        bits.extend(number_bits(op,2)+number_bits(a,w)+number_bits(b,w))
    for node in comp.outputs.values():bits.extend(number_bits(node,w))
    return bits


def decode(bits):
    """Total parser on binary strings; None deterministically means invalid.

    Extra padding after a declared programme is ignored. Reserved opcode3,
    forward/out-of-range operands and malformed headers are invalid.
    """
    if any(bit not in (0,1) for bit in bits):return None
    cursor=0
    def take(width):
        nonlocal cursor
        if cursor+width>len(bits):raise ValueError('truncated')
        value=sum(int(bits[cursor+i])<<i for i in range(width));cursor+=width
        return value
    try:
        header={name:take(width) for name,width in HEADER}
        k,m,w=header['k'],header['m'],header['w']
        ni,ng,no=header['inputs'],header['gates'],header['outputs']
        if (header['magic']!=MAGIC or header['version']!=0 or
            not 1<=k<=30 or not 1<=m<=30 or not 1<=w<=31 or
            ni!=11*(k+m+4) or no!=k+m+2 or (2+ni+ng)>1<<w):return None
        gates=[]
        for i in range(2+ni,2+ni+ng):
            op,a,b=take(2),take(w),take(w)
            if op==3 or not 0<=a<i or not 0<=b<i:return None
            gates.append((op,a,b))
        outputs=[take(w) for _ in range(no)]
        if any(out>=2+ni+ng for out in outputs):return None
        return dict(header=header,gates=gates,outputs=outputs,consumed_bits=cursor)
    except ValueError:return None


def evaluate(bits,inputs,output_width=35):
    """Total abstract evaluator; invalid programme/input returns zero+bad.

    Memory operations have unit logical semantics here, with no physical
    locality or speed claim. Programme bits are fetched serially once.
    """
    parsed=decode(bits)
    if parsed is None or len(inputs)!=parsed['header']['inputs'] or any(
            value not in (0,1) for value in inputs):
        return [0]*output_width,True
    values=[0,1]+list(map(int,inputs))
    for op,a,b in parsed['gates']:
        left,right=values[a],values[b]
        values.append(left&right if op==0 else left|right if op==1 else left^right)
    return [values[node] for node in parsed['outputs']],False
