"""Specified dictionary512 + finite LZ word-stream coding attempt.

Decodes exact whole GAW0D instruction/data words, not a rule-evaluation oracle.
All persistent code is the bitstream + exactly512100-bit dictionary words.
Generic decoder uses a bounded temporary word array, explicitly counted.
"""
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
import json,sys,time,hashlib
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'unregistered_gaw0'))
import gray_wider_word_gaw0 as k
from check_gray_wider_word_gaw0 import instance
ROOT=Path(__file__).resolve().parents[4]
DEST=ROOT/'figs/gray_counterexamples/unregistered_gaw1'

def gamma(n):
    assert n>=1;s=bin(n)[2:];return [0]*(len(s)-1)+[int(c) for c in s]

def uint(n,width):return [(n>>i)&1 for i in range(width)]

def compress(words):
    freq=Counter(words)
    # Fixed dictionary selection; dictionary0zero is explicit.
    chosen=sorted((w for w in freq if w),key=lambda w:(-freq[w]*max(0,w.bit_length()-1),w))[:511]
    dictionary=[0]+chosen;lookup={w:i for i,w in enumerate(dictionary)}
    dictionary+= [0]*(512-len(dictionary))
    n=len(words);cost=[0]*(n+1);actions=[None]*n;previous={}
    locations=[]
    for i,w in enumerate(words):locations.append(tuple(previous.get(w,())));previous.setdefault(w,[]).append(i)
    for i in range(n-1,-1,-1):
        w=words[i]
        candidates=[]
        if w in lookup:candidates.append((10+cost[i+1],('dict',lookup[w])))
        candidates.append((9+w.bit_length()+cost[i+1],('literal',w)))
        for start in locations[i]:
            dist=i-start;length=0
            while i+length<n and words[i+length]==words[i-dist+length]:length+=1
            for ln in range(2,length+1):
                expense=2+len(gamma(dist))+len(gamma(ln))+cost[i+ln]
                candidates.append((expense,('copy',dist,ln)))
        cost[i],actions[i]=min(candidates,key=lambda p:(p[0],p[1]))
    stream=[];steps=[];i=0
    while i<n:
        action=actions[i];steps.append(dict(word_index=i,action=action))
        if action[0]=='dict':stream.extend([0]+uint(action[1],9));i+=1
        elif action[0]=='literal':
            w=action[1];stream.extend([1,0]+uint(w.bit_length(),7)+uint(w,w.bit_length()));i+=1
        else:
            stream.extend([1,1]+gamma(action[1])+gamma(action[2]));i+=action[2]
    assert len(stream)==cost[0]
    return stream,dictionary,steps

def decode(bits,dictionary,capacity=8192):
    """Total bounded decoder; malformed/truncated streams yield no further words.

    0+index9 is dictionary.10+width7+little-endian literal is raw word.
    11+gamma distance+gamma length copies only a valid earlier word.
    Inputs are bounded; counter/bit checks cap every loop.
    """
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
            if not first:output.append(dictionary[read(9)]&k.MASK)
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
    start=time.monotonic();rom,listing,labels=instance()
    words=[k.beta_word(rom,a) for a in range(rom.token_count)]
    bits,dictionary,steps=compress(words);assert decode(bits,dictionary)==words
    filename=DEST/'GAW1_lossless_code.json'
    filename.write_text(json.dumps(dict(bits=bits,dictionary=[hex(w) for w in dictionary],steps=steps,
        total_words=len(words),bits_used=len(bits),Q_fit=len(bits)<=8192,dictionary_capacity_bits=51200,
        decoder_temporary_array_capacity_bits=8192*100),separators=(',',':'))+'\n')
    print(json.dumps(dict(words=len(words),bits=len(bits),Q_fit=len(bits)<=8192,dictionary_words=len(dictionary),
        code_capacity_plus_dictionary_bits=8192+51200,temporary_decoder_array_bits=8192*100,
        actions=Counter(step['action'][0] for step in steps),elapsed=time.monotonic()-start)))

if __name__=='__main__':main()
