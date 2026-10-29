"""Derive U records and legal-only second-period composition from large bursts."""
from pathlib import Path
import json,sys,time
S=Path(__file__).resolve().parent;sys.path.insert(0,str(S))
import search_gaw17_large_bursts as m
sys.path.insert(0,str(S.parent/'unregistered_gaw16'))
import continue_gaw16_word_bursts as inherited

def run(recipe,limit=16000):
    started=time.monotonic();r,state=m.run(recipe,limit=limit)
    if r['actual_quiet_coherent_closure'] is not None:
        r['actual_U_and2U_boundary']=inherited.boundary(state)
    r['elapsed_seconds']=time.monotonic()-started
    return r

def main():
    for recipe in m.recipes():
        r=run(recipe);p=m.D/(recipe['tag']+'_complete.json');p.write_text(json.dumps(r,indent=2)+'\n')
        b=r.get('actual_U_and2U_boundary',{})
        print(json.dumps(dict(tag=recipe['tag'],rows=len(r['actual_rows']),
            actual_full_burst=r['full_planned_error_burst_executed'],
            closure=r['actual_quiet_coherent_closure'] is not None,
            maximum_GF_or_Age=max(v['geometry'] for v in r['actual_rows']),
            actual_WF_outputs=sum(len(v['actual_Workspace_sources']) for v in r['actual_rows']),
            bad_U=b.get('actual_U_bad_normal_receivers'),illegal_U=b.get('actual_U_illegal_native_words'),
            terminal_by120Q=b.get('terminal_by120Q'),legal2U_shadow=b.get('complete2U_shadow'),
            seconds=r['elapsed_seconds'])),flush=True)

if __name__=='__main__':main()
