/* NEW isolated analysis factor of unchanged GAW2R. Not a new CA rule.
 * Binary GF labels and common Age imply both native GF quorums exist.
 * Before96Q there is no Workspace input. A pulse run requires a separately
 * proved actual80Q-1 special-Info source list; these are ports until certified.
 * Info copies at every potential primary have fixed origin and are voted
 * then wiped. Source primary and reader wipes are both used literally.
 */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define Q 8192
#define U (128*Q)
#define MAXSEG 4096
#define MAXCUT 200000
#define MAXSRC 128
typedef struct {int lo,hi,v;} Seg;
typedef struct {int p,bits;} Source;
typedef struct {int label,f1,wipe;} Native;
static Seg old[MAXSEG],next[MAXSEG];static int nseg;
static Source sources[MAXSRC];static int nsrc;
static int cuts[MAXCUT],ncuts;
static const int slots[5]={0,-2,-1,1,2};
static int state(int x){
    int lo=0,hi=nseg;
    while(lo<hi){int mid=(lo+hi)/2;if(old[mid].hi<=x)lo=mid+1;else hi=mid;}
    return lo<nseg&&old[lo].lo<=x?old[lo].v:0;
}
static int gf(int x,int label){return (x+(label?Q/2:0))&(Q-1);}
static Native native(int x){
    int r=0,l=0,mis=0,rf=0,wf=0;
    for(int j=1;j<=5;j++){r+=(state(x+j)&1);l+=(state(x-j)&1);}
    r=r>=3;l=l>=3;int addr=gf(x,r);
    for(int j=-5;j<=5;j++){
        int v=state(x+j),in=0<=addr+j&&addr+j<Q;
        if(j<0)mis+=in&&((v&1)!=r);
        if(j>0)rf+=in&&((v>>1)&1);
        wf+=in&&((v>>2)&1);
    }
    int f=mis>=3||rf>=3||wf>=3||(((state(x)>>1)&1)&&rf>=2);
    int label=f?l:r;return (Native){label,f,f&&label!=(state(x)&1)};
}
static int vote(int bits){return __builtin_popcount((unsigned)bits)>=3;}
static int source_vote(int p){
    for(int i=0;i<nsrc;i++)if(sources[i].p==p)return vote(sources[i].bits);
    return 0;
}
static int result(int x,int row){
    Native z=native(x);int w=0,addr=gf(x,z.label);
    if(96*Q<=row&&row<98*Q&&!z.wipe&&addr>=Q-5){
        int p=x+Q-3-addr;
        w=source_vote(p)&&!native(p).wipe;
    }
    return z.label|(z.f1<<1)|(w<<2);
}
static void cut(int x){if(ncuts>=MAXCUT){fprintf(stderr,"cut overflow\n");exit(2);}cuts[ncuts++]=x;}
static int cmp(const void *a,const void *b){int x=*(const int*)a,y=*(const int*)b;return (x>y)-(x<y);}
static int floor_div(int a,int b){int q=a/b,r=a%b;return q-(r<0);}
static void push(int lo,int hi,int v,int *nn){
    if(!v||hi<=lo)return;
    if(*nn&&next[*nn-1].hi==lo&&next[*nn-1].v==v)next[*nn-1].hi=hi;
    else{if(*nn>=MAXSEG){fprintf(stderr,"segment overflow\n");exit(2);}next[(*nn)++]=(Seg){lo,hi,v};}
}
static int step(int row,long long *events){
    int lo=0,hi=0;
    if(nseg){lo=old[0].lo-8;hi=old[nseg-1].hi+8;}
    if(96*Q<=row&&row<98*Q)for(int i=0;i<nsrc;i++)if(vote(sources[i].bits)){
        if(sources[i].p-3<lo)lo=sources[i].p-3;
        if(sources[i].p+4>hi)hi=sources[i].p+4;
    }
    ncuts=0;cut(lo);cut(hi);
    for(int i=0;i<nseg;i++)for(int j=-8;j<=8;j++){cut(old[i].lo-j);cut(old[i].hi-j);}
    /* All native inside/end predicates are constant between these cuts.
     * Both label wraps must be included, plus their±5 stencil shifts.
     */
    for(int k=floor_div(lo,Q)-1;k<=floor_div(hi,Q)+1;k++)
        for(int phase=0;phase<2;phase++)for(int j=-5;j<=5;j++)cut(k*Q+phase*(Q/2)+j);
    qsort(cuts,ncuts,sizeof(int),cmp);int nn=0;
    for(int i=0;i<ncuts-1;i++){
        int a=cuts[i],b=cuts[i+1];if(a<lo||b>hi||a==b)continue;
        int v=result(a,row);
        /* Supplementary endpoint audit: the partition proof, not these
         * two samples, establishes every interior integer identity.
         */
        if(result(b-1,row)!=v){fprintf(stderr,"event partition mismatch at row%d [%d,%d)\n",row,a,b);exit(3);}
        push(a,b,v,&nn);(*events)++;
    }
    int bits[MAXSRC];
    for(int i=0;i<nsrc;i++){
        bits[i]=0;int v=vote(sources[i].bits);
        for(int h=0;h<5;h++)bits[i]|=(v&&!native(sources[i].p-slots[h]).wipe)<<h;
    }
    int unchanged=nn==nseg&&!memcmp(old,next,(size_t)nn*sizeof(Seg));
    for(int i=0;i<nsrc;i++){unchanged&=bits[i]==sources[i].bits;sources[i].bits=bits[i];}
    memcpy(old,next,(size_t)nn*sizeof(Seg));nseg=nn;return unchanged;
}
static void record(FILE *f,int row){
    int header[3]={row,nseg,nsrc};fwrite(header,sizeof(int),3,f);
    fwrite(old,sizeof(Seg),(size_t)nseg,f);fwrite(sources,sizeof(Source),(size_t)nsrc,f);
}
static void print_state(int row){
    printf("{\"row\":%d,\"segments\":[",row);
    for(int i=0;i<nseg;i++)printf("%s[%d,%d,%d]",i?",":"",old[i].lo,old[i].hi,old[i].v);
    printf("],\"source_bits\":[");
    for(int i=0;i<nsrc;i++)printf("%s[%d,%d]",i?",":"",sources[i].p,sources[i].bits);
    printf("]}");
}
int main(int argc,char **argv){
    if(argc<3){fprintf(stderr,"usage: interval_native prefix|pulse binary-output [derived-source-file]\n");return 1;}
    int pulse=!strcmp(argv[1],"pulse");
    if(pulse){
        if(argc!=4)return 1;
        FILE *s=fopen(argv[3],"r");if(!s)return 1;
        while(nsrc<MAXSRC&&fscanf(s,"%d",&sources[nsrc].p)==1){sources[nsrc].bits=0;nsrc++;}fclose(s);
    }
    FILE *f=fopen(argv[2],"wb");if(!f)return 1;
    nseg=1;old[0]=(Seg){0,17*Q,1};int row=1,fixed=-1,rows=0;
    long long events=0;record(f,row);
    printf("{\"mode\":\"%s\",\"Q\":%d,\"U\":%d,\"snapshots\":[",argv[1],Q,U);print_state(row);
    int end=pulse?U:32*Q;
    while(row<end){
        int unchanged=step(++row,&events);rows++;
        if(row==80*Q-1){
            for(int i=0;i<nsrc;i++){
                Native z=native(sources[i].p);
                if(gf(sources[i].p,z.label)!=Q-3||z.wipe){fprintf(stderr,"invalid special-primary source port\n");return 4;}
                sources[i].bits=31;
            }
        }
        record(f,row);
        if(unchanged&&row<80*Q-1){
            if(fixed<0){fixed=row;printf(",");print_state(row);}
            if(!pulse)break;
            /* Quorums always exist, F20 and WFguard closed; no Age-bit
             * predicate remains. The fixed native factor thus persists.
             */
            row=80*Q-2;record(f,row);
        }
        if(row==80*Q-1){
            printf(",");print_state(row);
            row=96*Q-1;record(f,row);
        }
        if(row==96*Q||row==97*Q||row==98*Q||row==99*Q||row==102*Q){printf(",");print_state(row);}
        if(row>=98*Q&&unchanged){
            /* Source guard stays closed through U, including commit.
             * Future SFsource contents are irrelevant to native fields.
             */
            row=U;record(f,row);break;
        }
    }
    printf(",");print_state(row);printf("],\"first_prefix_fixed_row\":%d,\"computed_updates\":%d,\"event_intervals\":%lld,\"actual_source_derivation_still_required\":true}\n",fixed,rows,events);
    fclose(f);return 0;
}
