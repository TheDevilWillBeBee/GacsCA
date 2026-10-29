/* NEW second-period scalar audit. These unmodified word-quorum helpers
 * are copied from frozen GAW23, whose source hash is pinned by the manifest.
 * This checks the changed-driver history; it is not a new CA rule. */
#define main old_interval_main
#include "../unregistered_gaw23/gaw23_interval_native.c"
#undef main
#include <assert.h>
typedef struct {int addr,age,f1,f2,wf1,wf2,wipe;} RawResult;
static int word_majority(const int a[5],int fallback,int *exists){
    for(int i=0;i<5;i++){
        int count=0;for(int j=0;j<5;j++)count+=a[i]==a[j];
        if(count>=3){*exists=1;return a[i];}
    }
    *exists=0;return fallback;
}
static RawResult raw_native(int x,int row){
    int right[5],left[5],e,le;
    for(int j=1;j<=5;j++){
        right[j-1]=(gf(x+j,state(x+j)&1)-j)&(Q-1);
        left[j-1]=(gf(x-j,state(x-j)&1)+j)&(Q-1);
    }
    int ra=word_majority(right,gf(x,state(x)&1),&e);
    int la=word_majority(left,gf(x,state(x)&1),&le);
    assert(e&&le); /* both binary GF labels have a five-word quorum */
    int mismatch=0,rf=0,wf=0;
    for(int j=-5;j<=5;j++){
        int in=0<=ra+j&&ra+j<Q,v=state(x+j);
        if(j<0)mismatch+=in&&gf(x+j,v&1)!=((ra+j)&(Q-1));
        if(j>0)rf+=in&&((v>>1)&1);
        wf+=in&&((v>>2)&1);
    }
    int f=mismatch>=3||rf>=3||wf>=3||(((state(x)>>1)&1)&&rf>=2);
    /* Common Age gives both five-word Age quorums. Old F2/WF2 are0,
     * and source3 is false because the right GF quorum exists. Thus
     * the h1 turn-on equation produces F2=0 without its erasure clause.
     */
    int addr=f?la:ra;
    return (RawResult){addr,row%U,f,0,0,0,f&&addr!=gf(x,state(x)&1)};
}
static int raw_result(int x,int row){
    RawResult z=raw_native(x,row);
    if(96*Q<=z.age&&z.age<98*Q&&!z.wipe&&Q-5<=z.addr){
        int p=x+Q-3-z.addr;RawResult source=raw_native(p,row);
        z.wf1=source_vote(p)&&!source.wipe;
    }
    assert(z.addr==gf(x,0)||z.addr==gf(x,1));
    return (z.addr==gf(x,1))|(z.f1<<1)|(z.wf1<<2);
}
static void prepare_cuts(int row,int *lo,int *hi){
    *lo=*hi=0;if(nseg){*lo=old[0].lo-8;*hi=old[nseg-1].hi+8;}
    if(96*Q<=row&&row<98*Q)for(int i=0;i<nsrc;i++)if(vote(sources[i].bits)){
        if(sources[i].p-3<*lo)*lo=sources[i].p-3;
        if(sources[i].p+4>*hi)*hi=sources[i].p+4;
    }
    ncuts=0;cut(*lo);cut(*hi);
    for(int i=0;i<nseg;i++)for(int j=-8;j<=8;j++){cut(old[i].lo-j);cut(old[i].hi-j);}
    for(int k=floor_div(*lo,Q)-1;k<=floor_div(*hi,Q)+1;k++)
        for(int phase=0;phase<2;phase++)for(int j=-5;j<=5;j++)cut(k*Q+phase*(Q/2)+j);
    qsort(cuts,ncuts,sizeof(int),cmp);
}
static int read_record(FILE *f,int *row,Seg *s,int *nn,Source *src,int *ns){
    int h[3];size_t n=fread(h,sizeof(int),3,f);if(!n)return 0;assert(n==3);
    *row=h[0];*nn=h[1];*ns=h[2];assert(0<=*nn&&*nn<=MAXSEG&&0<=*ns&&*ns<=MAXSRC);
    assert(fread(s,sizeof(Seg),(size_t)*nn,f)==(size_t)*nn);
    assert(fread(src,sizeof(Source),(size_t)*ns,f)==(size_t)*ns);return 1;
}
int main(int argc,char **argv){
    assert(argc==2);FILE *f=fopen(argv[1],"rb");assert(f);
    int row,after,nn,ns;Seg target[MAXSEG];Source targetsrc[MAXSRC];
    assert(read_record(f,&row,old,&nseg,sources,&nsrc));assert(row==0&&nsrc==24);
    long long intervals=0,cofactors=0,source_cofactors=0,updates=0,jumps=0,ignored=0;
    while(read_record(f,&after,target,&nn,targetsrc,&ns)){
        assert(ns==nsrc&&after>row);
        if(after==row+1){
            int lo,hi;prepare_cuts(after,&lo,&hi);
            for(int i=0;i<ncuts-1;i++){
                int a=cuts[i],b=cuts[i+1];if(a<lo||b>hi||a==b)continue;
                assert(raw_result(a,after)==result(a,after));assert(raw_result(b-1,after)==result(b-1,after));
                intervals++;cofactors+=2;
            }
            assert(raw_result(lo-1,after)==0&&raw_result(hi,after)==0);cofactors+=2;
            int expected_bits[MAXSRC];
            for(int i=0;i<nsrc;i++){
                expected_bits[i]=0;
                for(int h=0;h<5;h++){
                    RawResult z=raw_native(sources[i].p-slots[h],after);
                    expected_bits[i]|=(vote(sources[i].bits)&&!z.wipe)<<h;source_cofactors++;
                }
            }
            step(after,&ignored);updates++;
            if(after==80*Q-1){
                for(int i=0;i<nsrc;i++){
                    RawResult z=raw_native(sources[i].p,after);assert(z.addr==Q-3&&!z.wipe);sources[i].bits=31;
                }
            }else for(int i=0;i<nsrc;i++)assert(sources[i].bits==expected_bits[i]);
            assert(nseg==nn&&!memcmp(old,target,(size_t)nn*sizeof(Seg)));
            assert(!memcmp(sources,targetsrc,(size_t)ns*sizeof(Source)));
        }else{
            assert(nseg==nn&&!memcmp(old,target,(size_t)nn*sizeof(Seg)));
            assert(!memcmp(sources,targetsrc,(size_t)ns*sizeof(Source)));
            assert((row==1&&after==80*Q-2)||(row==80*Q-1&&after==96*Q-1)||(row>=98*Q&&after==U));
            int lo,hi;prepare_cuts(row+1,&lo,&hi);
            for(int i=0;i<ncuts-1;i++){
                int a=cuts[i],b=cuts[i+1];if(a<lo||b>hi||a==b)continue;
                assert(raw_result(a,row+1)==state(a));assert(raw_result(b-1,row+1)==state(b-1));cofactors+=2;
            }
            jumps++;
        }row=after;
    }fclose(f);
    assert(row==U&&updates==24579&&intervals==20488060&&jumps==3&&nseg==3);
    assert(old[0].lo==14*Q&&old[0].hi==29*Q/2&&old[0].v==2);
    assert(old[1].lo==29*Q/2&&old[1].hi==45*Q/2&&old[1].v==1);
    assert(old[2].lo==45*Q/2&&old[2].hi==23*Q&&old[2].v==3);
    printf("{\"passed\":true,\"independent_event_intervals\":%lld,\"scalar_native_WF_cofactors\":%lld,\"source_holder_wipe_cofactors\":%lld,\"computed_updates\":%lld,\"fixed_guard_jumps\":%lld,\"native_GF_foreign_interval_at2U\":[%d,%d],\"source_Info_at2U_commit_not_claimed\":true}\n",intervals,cofactors,source_cofactors,updates,jumps,29*Q/2,23*Q);
    return 0;
}
