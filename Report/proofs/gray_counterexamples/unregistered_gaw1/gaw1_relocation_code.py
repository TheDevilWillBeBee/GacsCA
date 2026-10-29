"""Exact whole-word stream compression with a specified finite relocation copy.

No rule is changed: this is a code representation/decoder feasibility audit.
It shares the explicit512100-bit dictionary and bounded8192WORD100 buffer
accounting of gaw1_lossless_code; there is no hidden expanded immutable table.
"""
from pathlib import Path
from collections import Counter
import json,time
import gaw1_lossless_code as old
k=old.k;ROOT=old.ROOT;D=old.DEST


def transform(word,src,end,dst,oc,nc):
    """Total syntax-only transformation, never a cell/rule evaluator.

    Relocate only internal branch/return targets. Rebase declared READ5 lane,
    literal lane and FULLCOL shift fields. Every field assignment is masked.
    The transform is defined for any100-bit word, including invalid op15.
    """
    decoded=k.decode(word)
    if decoded is None:return word
    name,args=decoded;args=list(args);delta=dst-src;changed=False
    if name in ('JMP','BNZ'):
        index=0 if name=='JMP' else 1
        if src<=args[index]<end:args[index]=(args[index]+delta)&8191;changed=True
    elif name=='MOVI' and args[0]==15 and src<=args[1]<end:
        args[1]=(args[1]+delta)&((1<<20)-1);changed=True
    if oc!=nc:
        if name=='READ5' and args[2]==oc:args[2]=nc;changed=True
        elif name=='MOVI' and args[0] in (7,12) and args[1]==oc:args[1]=nc;changed=True
        elif name=='ALUI' and args[0] in range(4) and args[1]==k.ALU['RSHIFT'] and args[2]==args[0] and args[3]==oc-5:
            args[3]=(nc-5)&((1<<20)-1);changed=True
    if not changed:return word
    lo=sum(b<<i for i,b in enumerate(k.instruction_bits(name,*args)))
    width=k.LENGTH[k.OP[name]]
    return (word & (k.MASK^((1<<width)-1)))|lo


def compress(words):
    # Fixed dictionary is identical to the prior exact raw/LZ attempt.
    freq=Counter(words);chosen=sorted((w for w in freq if w),key=lambda w:(-freq[w]*max(0,w.bit_length()-1),w))[:511]
    dictionary=[0]+chosen;lookup={w:i for i,w in enumerate(dictionary)};dictionary+=[0]*(512-len(dictionary))
    n=len(words);cost=[0]*(n+1);actions=[None]*n
    # Deliberately restricted candidate set: exact prior words, and a generic
    # instruction-boundary start with raw first word equal. No optimality over
    # all code grammars is claimed. The DP is exact for the included candidates.
    loc={};positions=[]
    for i,w in enumerate(words):positions.append(tuple(loc.get(w,())));loc.setdefault(w,[]).append(i)
    special={190:6,331:7,472:8,613:9,754:10,895:11}
    for i in range(n-1,-1,-1):
        w=words[i];candidates=[(9+w.bit_length()+cost[i+1],('literal',w))]
        if w in lookup:candidates.append((10+cost[i+1],('dict',lookup[w])))
        for start in positions[i]:
            length=0
            while i+length<n and words[i+length]==words[start+length]:length+=1
            for ln in range(2,length+1):candidates.append((3+len(old.gamma(i-start))+len(old.gamma(ln))+cost[i+ln],('copy',i-start,ln)))
        # Syntax relocation copies include arbitrary branch-retargeting and
        # a four-bit old/new centre parameter. Candidate windows are bounded,
        # with exact reconstruction verified for every proposed length.
        if i in special:
            for start,oc in special.items():
                if start>=i:continue
                nc=special[i];ln=141
                assert all(transform(words[start+j],start,start+ln,i,oc,nc)==words[i+j] for j in range(ln))
                expense=3+len(old.gamma(i-start))+len(old.gamma(ln))+8+cost[i+ln]
                candidates.append((expense,('relocate',i-start,ln,oc,nc)))
        cost[i],actions[i]=min(candidates,key=lambda p:(p[0],p[1]))
    stream=[];steps=[];i=0
    while i<n:
        a=actions[i];steps.append(dict(word_index=i,action=a))
        if a[0]=='dict':stream.extend([0]+old.uint(a[1],9));i+=1
        elif a[0]=='literal':stream.extend([1,0]+old.uint(a[1].bit_length(),7)+old.uint(a[1],a[1].bit_length()));i+=1
        elif a[0]=='copy':stream.extend([1,1,0]+old.gamma(a[1])+old.gamma(a[2]));i+=a[2]
        else:stream.extend([1,1,1]+old.gamma(a[1])+old.gamma(a[2])+old.uint(a[3],4)+old.uint(a[4],4));i+=a[2]
    assert len(stream)==cost[0];return stream,dictionary,steps


def decode(bits,dictionary,capacity=8192):
    output=[];pos=0
    def read(width):
        nonlocal pos
        if pos+width>len(bits):raise ValueError('truncated')
        v=sum(bits[pos+i]<<i for i in range(width));pos+=width;return v
    def gamma():
        nonlocal pos
        zeros=0
        while True:
            if pos>=len(bits):raise ValueError('truncated gamma')
            bit=bits[pos];pos+=1
            if bit:break
            zeros+=1
            if zeros>13:raise ValueError('gamma overflow')
        v=1
        for _ in range(zeros):
            if pos>=len(bits):raise ValueError('truncated gamma suffix')
            v=2*v+bits[pos];pos+=1
        return v
    try:
        while pos<len(bits) and len(output)<capacity:
            if not read(1):output.append(dictionary[read(9)]&k.MASK);continue
            if not read(1):
                width=read(7)
                if width>100:raise ValueError('bad literal')
                output.append(read(width));continue
            changed=read(1);distance=gamma();length=gamma();oc=nc=0
            if changed:oc=read(4);nc=read(4)
            if distance>len(output) or length<2 or len(output)+length>capacity:raise ValueError('bad copy')
            dst=len(output);src=dst-distance
            # Relocated source must be already completely available. Plain
            # copies may overlap. This avoids a circular relocation source.
            if changed and length>distance:raise ValueError('overlapping relocation')
            for j in range(length):
                word=output[src+j]
                output.append(transform(word,src,src+length,dst,oc,nc) if changed else word)
    except ValueError:pass
    return output


def main():
    started=time.monotonic();rom,listing,labels=old.instance();words=[k.beta_word(rom,i) for i in range(rom.token_count)]
    bits,dictionary,steps=compress(words);assert decode(bits,dictionary)==words
    data=dict(name='Specified relocation-aware dictionary512 stream',bits=bits,dictionary=[hex(w) for w in dictionary],steps=steps,
        whole_emission_words=len(words),bits_used=len(bits),Q_fit=len(bits)<=8192,dictionary_capacity_bits=51200,
        temporary_decoder_buffer_capacity_bits=819200,all_emitted_words_reconstructed=True,
        physical_decoder_or_changed_CODE_rule_or_own_recompiled_rule=False,elapsed_seconds=time.monotonic()-started)
    (D/'GAW1_relocation_code.json').write_text(json.dumps(data,separators=(',',':'))+'\n')
    print(json.dumps(dict(words=len(words),bits=len(bits),Q_fit=len(bits)<=8192,actions=Counter(s['action'][0] for s in steps),elapsed=data['elapsed_seconds'])))

if __name__=='__main__':main()
