"""Exact whole-emission phrase512/LZ format, all resources explicit.

One100-bit entry encodes1word98bits,2words49bits,or3words32bits.
This is a new finite CODE decoder format, not an extra hidden code table.
"""
from collections import Counter
from pathlib import Path
import sys,json,time
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'unregistered_gaw0'))
import gray_wider_word_gaw0 as k
from check_gray_wider_word_gaw0 import instance
from gaw1_lossless_code import gamma,uint
ROOT=Path(__file__).resolve().parents[4];D=ROOT/'figs/gray_counterexamples/unregistered_gaw1'

def pack_phrase(phrase):
    n=len(phrase);width={1:98,2:49,3:32}[n]
    assert all(0<=w<1<<width for w in phrase)
    return ((n-1)<<98)|sum(w<<(width*i) for i,w in enumerate(phrase))

def unpack_phrase(word):
    n=(word>>98)+1
    if not 1<=n<=3:return None
    width={1:98,2:49,3:32}[n]
    return tuple((word>>(width*i))&((1<<width)-1) for i in range(n))

def compress(words):
    frequency=Counter()
    for length,width in ((1,98),(2,49),(3,32)):
        for i in range(len(words)-length+1):
            phrase=tuple(words[i:i+length])
            if all(w<1<<width for w in phrase):frequency[phrase]+=1
    # A fully declared heuristic dictionary; DP below is optimal only for
    # these chosen512 phrases, not over all dictionaries or encodings.
    ranked=sorted(frequency,key=lambda p:(-frequency[p]*(sum(9+w.bit_length() for w in p)-10),-len(p),p))
    chosen=ranked[:512];lookup={p:i for i,p in enumerate(chosen)};dictionary=[pack_phrase(p) for p in chosen]
    n=len(words);cost=[0]*(n+1);actions=[None]*n;previous={};locations=[]
    for i,w in enumerate(words):locations.append(tuple(previous.get(w,())));previous.setdefault(w,[]).append(i)
    for i in range(n-1,-1,-1):
        w=words[i];options=[(9+w.bit_length()+cost[i+1],('literal',w))]
        for length in (1,2,3):
            phrase=tuple(words[i:i+length])
            if len(phrase)==length and phrase in lookup:options.append((10+cost[i+length],('dict',lookup[phrase],length)))
        for start in locations[i]:
            dist=i-start;length=0
            while i+length<n and words[i+length]==words[i-dist+length]:length+=1
            for ln in range(2,length+1):options.append((2+len(gamma(dist))+len(gamma(ln))+cost[i+ln],('copy',dist,ln)))
        cost[i],actions[i]=min(options,key=lambda pair:(pair[0],pair[1]))
    stream=[];steps=[];i=0
    while i<n:
        action=actions[i];steps.append(dict(word_index=i,action=action))
        if action[0]=='dict':stream.extend([0]+uint(action[1],9));i+=action[2]
        elif action[0]=='literal':stream.extend([1,0]+uint(action[1].bit_length(),7)+uint(action[1],action[1].bit_length()));i+=1
        else:stream.extend([1,1]+gamma(action[1])+gamma(action[2]));i+=action[2]
    assert len(stream)==cost[0]
    return stream,dictionary,steps

def decode(bits,dictionary,capacity=8192):
    output=[];pos=0
    def read(width):
        nonlocal pos
        if pos+width>len(bits):raise ValueError('truncated')
        value=sum(bits[pos+i]<<i for i in range(width));pos+=width;return value
    def positive():
        nonlocal pos
        zeros=0
        while True:
            if pos>=len(bits):raise ValueError('truncated gamma')
            bit=bits[pos];pos+=1
            if bit:break
            zeros+=1
            if zeros>13:raise ValueError('gamma overflow')
        value=1
        for _ in range(zeros):
            if pos>=len(bits):raise ValueError('truncated gamma suffix')
            value=2*value+bits[pos];pos+=1
        return value
    try:
        while pos<len(bits) and len(output)<capacity:
            first=read(1)
            if not first:
                phrase=unpack_phrase(dictionary[read(9)]&k.MASK)
                if phrase is None or len(output)+len(phrase)>capacity:raise ValueError('invalid phrase')
                output.extend(phrase)
            elif not read(1):
                width=read(7)
                if width>100:raise ValueError('literal width')
                output.append(read(width))
            else:
                distance=positive();length=positive()
                if distance>len(output) or length<2 or len(output)+length>capacity:raise ValueError('invalid copy')
                for _ in range(length):output.append(output[-distance])
    except ValueError:pass
    return output

def main():
    start=time.monotonic();rom,listing,labels=instance();words=[k.beta_word(rom,a) for a in range(rom.token_count)]
    bits,dictionary,steps=compress(words);assert decode(bits,dictionary)==words
    document=dict(bits=bits,dictionary=[hex(w) for w in dictionary],steps=steps,total_words=len(words),bits_used=len(bits),
        Q_fit=len(bits)<=8192,dictionary_capacity_bits=51200,decoder_temporary_array_capacity_bits=819200)
    (D/'GAW1_phrase_code.json').write_text(json.dumps(document,separators=(',',':'))+'\n')
    print(json.dumps(dict(words=len(words),bits=len(bits),Q_fit=len(bits)<=8192,dictionary_words=len(dictionary),
        phrase_counts=Counter(len(unpack_phrase(word)) for word in dictionary),
        actions=Counter(step['action'][0] for step in steps),elapsed=time.monotonic()-start)))

if __name__=='__main__':main()
