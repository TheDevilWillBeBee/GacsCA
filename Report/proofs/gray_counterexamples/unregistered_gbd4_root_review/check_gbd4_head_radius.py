"""Independent exact two-input witness for the raw Head movement radius."""
import hashlib,json,sys
from dataclasses import replace
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
SOURCE=ROOT/'Report/proofs/gray_counterexamples/unregistered_gbd4'
sys.path.insert(0,str(SOURCE))
import controller as c

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    source=SOURCE/'controller.py'
    # The frozen source is already pinned by the accepted GBD4 manifest.
    manifest=ROOT/'figs/gray_counterexamples/unregistered_gbd4/GBD4_manifest.json'
    m=json.loads(manifest.read_text())
    assert m['assets'][str(source.relative_to(ROOT))]==sha(source)
    offsets=sorted({c.S[q]+d+c.S[h] for q in range(5) for d in (-1,0,1) for h in range(5)})
    assert offsets==list(range(-5,6))
    x=100;q=1;y=x+c.S[q];head=c.Head(present=1,mode=c.TRAVEL,target=y+1)
    word=c.pack_head(head)
    before={z:c.Cell(addr=z%c.Q) for z in range(x-8,x+9)}
    # Two left-vote witnesses use slots different from the own/right votes.
    for h in (0,2):
        z=y-1+c.S[h];old=before[z];slots=list(old.head)
        slots[c.INV[h]]=word;before[z]=replace(old,head=tuple(slots))
    changed=y-1+c.S[1];slot=c.INV[1];assert changed==x-5
    after=dict(before);slots=list(after[changed].head);slots[slot]=word
    after[changed]=replace(after[changed],head=tuple(slots))
    assert all(before[z]==after[z] for z in before if z!=changed)
    for state in (before,after):
        assert not c.head_vote(state,y).present and not c.head_vote(state,y+1).present
    assert not c.head_vote(before,y-1).present and c.head_vote(after,y-1)==head
    first=c.actor(before,x,q,(0,));second=c.actor(after,x,q,(0,))
    assert not first.present and second.present and second.move==2 and second.mode==c.TRAVEL
    proof=Path(__file__).parent/'GBD4_HEAD_RADIUS_ERRATUM.md'
    result=dict(passed=True,scope='raw port-level Head movement wording erratum only',
        source_sha256=sha(source),manifest_sha256=sha(manifest),proof_sha256=sha(proof),
        checker_sha256=sha(Path(__file__)),all_role_movement_source_offsets=offsets,
        raw_role_movement_radius=5,logical_centre_movement_radius=3,
        x=x,q=q,logical_centre=y,changed_site=changed,changed_slot=slot,
        old_raw_word=hex(before[changed].head[slot]),new_raw_word=hex(word),
        first_output=hex(c.pack_head(first)),second_output=hex(c.pack_head(second)),
        entire_before_raw_Head_words={str(z):[hex(w) for w in before[z].head] for z in before},
        accepted_component_radius_at_most=7,native_software_runtime_or_rule_changed=False,
        complete_rule_noise_or_Gray_refutation_proved=False)
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
