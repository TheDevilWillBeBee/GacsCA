/* SP31 restricted native/Info factor: common legal clock, two GF phases,
 * native F2/WF2=0, voted Info at residues3/515=0, no Info write/no errors.
 * Private header fields do not participate in this changed native factor.
 * Event trajectories alone do not prove the physical input premises.
 */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define Q 1024
#define MAX 20000
typedef struct {int lo,hi;unsigned v;} Segment;
typedef struct {int n;Segment seg[MAX];} State;
typedef struct {int n;int x[MAX];} Info;
static int phase(int x){int p=x%Q;return p<0?p+Q:p;}
static unsigned at(const State *s,int x){
    int a=0,b=s->n;
    while(a<b){int m=(a+b)/2;if(s->seg[m].hi<=x)a=m+1;else b=m;}
    return a<s->n&&s->seg[a].lo<=x?s->seg[a].v:0;
}
static int info_at(const Info *s,int x){
    int a=0,b=s->n;
    while(a<b){int m=(a+b)/2;if(s->x[m]<x)a=m+1;else b=m;}
    return a<s->n&&s->x[a]==x;
}
static int refined(const State *s,int x){
    static const int centre[4]={-30,-10,10,30};int n=0;
    for(int b=0;b<4;b++){
        int v=0;for(int u=-2;u<=2;u++)v+=(at(s,x+centre[b]+u)&1)!=0;
        n+=v>=3;
    }
    return n>=3?1:n<=1?0:(at(s,x)&1);
}
static unsigned local(const State *s,const Info *m,int x,int elapsed){
    int labels[11],right=0,left=0;
    for(int d=-5;d<=5;d++){labels[d+5]=refined(s,x+d);if(d>0)right+=labels[d+5];if(d<0)left+=labels[d+5];}
    right=right>=3;left=left>=3;
    int p=phase(x+512*right),mismatch=0,rflags=0,wflags=0,quiet=0;
    for(int d=1;d<=5;d++){
        if(p-d>=0)mismatch+=labels[5-d]!=right;
        quiet+=labels[5+d]==right&&!(at(s,x+d)&2);
    }
    for(int d=1;d<=8;d++)if(p+d<Q)rflags+=(at(s,x+d)&2)!=0;
    for(int d=-5;d<=5;d++)if(0<=p+d&&p+d<Q)wflags+=(at(s,x+d)&4)!=0;
    int f=mismatch>=3||rflags>=3||((at(s,x)&2)&&rflags>=2)||wflags>=3||(p<Q-5&&quiet<3);
    int selected=f?left:right,newp=phase(x+512*selected);
    int wf=elapsed<2*Q&&newp>=Q-5&&info_at(m,x+Q-3-newp);
    return selected|(f<<1)|(wf<<2)|(labels[5]<<3);
}
static void append(State *s,int lo,int hi,unsigned v){
    if(!v||lo==hi)return;
    if(s->n&&s->seg[s->n-1].hi==lo&&s->seg[s->n-1].v==v)s->seg[s->n-1].hi=hi;
    else {if(s->n==MAX){fprintf(stderr,"segment capacity\n");exit(2);}s->seg[s->n++]=(Segment){lo,hi,v};}
}
static int compare(const void *a,const void *b){int x=*(const int*)a,y=*(const int*)b;return(x>y)-(x<y);}
static uint64_t step(const State *s,const Info *m,State *next,Info *newm,int elapsed){
    static int cuts[MAX*180];int n=0;
    int lo=s->n?s->seg[0].lo:m->x[0],hi=s->n?s->seg[s->n-1].hi:m->x[m->n-1]+1;
    if(m->n){if(m->x[0]<lo)lo=m->x[0];if(m->x[m->n-1]+1>hi)hi=m->x[m->n-1]+1;}
    lo-=37;hi+=37;cuts[n++]=lo;cuts[n++]=hi;
    for(int i=0;i<s->n;i++)for(int d=-37;d<=37;d++){
        cuts[n++]=s->seg[i].lo-d;cuts[n++]=s->seg[i].hi-d;
    }
    for(int g=lo/Q-2;g<=hi/Q+2;g++)for(int label=0;label<2;label++)for(int d=-8;d<=8;d++){
        int x=g*Q-512*label-d;if(lo<=x&&x<=hi)cuts[n++]=x;
    }
    if(n>MAX*180){fprintf(stderr,"cut capacity\n");exit(3);}
    qsort(cuts,n,sizeof(int),compare);next->n=0;uint64_t events=0;
    for(int i=0;i<n-1;i++){
        int a=cuts[i],b=cuts[i+1];if(a>=b||a<lo||b>hi)continue;
        unsigned v=local(s,m,a,elapsed);
        if(v!=local(s,m,b-1,elapsed)){fprintf(stderr,"event disagreement %d %d t%d\n",a,b,elapsed);exit(4);}
        for(int d=-37;d<=37;d++)if(at(s,a+d)!=at(s,b-1+d)){fprintf(stderr,"omitted state cut\n");exit(5);}
        for(int label=0;label<2;label++)for(int d=-8;d<=8;d++){
            int p=phase(a+512*label),q=phase(b-1+512*label);
            if((0<=p+d&&p+d<Q)!=(0<=q+d&&q+d<Q)){fprintf(stderr,"omitted phase cut\n");exit(6);}
        }
        append(next,a,b,v&7);events++;
    }
    newm->n=0;
    for(int i=0;i<m->n;i++){
        int y=m->x[i],keeps=0;
        for(int slot=-2;slot<=2;slot++){
            unsigned v=local(s,m,y-slot,elapsed);
            keeps+=!((v&2)&&((v&1)!=((v>>3)&1)));
        }
        if(keeps>=3)newm->x[newm->n++]=y;
    }
    return events;
}
unsigned sp31_cofactor(const uint8_t *native,const uint8_t *info,int p,int elapsed){
    State s={0};Info m={0};
    for(int i=0;i<81;i++){int x=p+i-40;append(&s,x,x+1,native[i]);if(info[i])m.x[m.n++]=x;}
    return local(&s,&m,p,elapsed);
}

static void report(const State *s,const Info *m,int t,uint64_t events){
    int last=-1,nright=0;
    for(int i=0;i<s->n;i++)if(s->seg[i].v&1){
        int l=s->seg[i].lo>0?s->seg[i].lo:0,h=s->seg[i].hi;
        if(h>l){nright+=h-l;if(last<h)last=h;}
    }
    printf("{\"relative_row\":%d,\"upper_logical_Age\":%d,\"native0\":%u,\"native1021\":%u,\"wrongGF_right_sites\":%d,\"wrongGF_right_exclusive\":%d,\"Info_ones\":%d,\"segments\":%d,\"events\":%llu,\"native_segments\":[",
           t,278401+t,at(s,0),at(s,1021),nright,last,m->n,s->n,(unsigned long long)events);
    for(int i=0;i<s->n;i++)printf("%s[%d,%d,%u]",i?",":"",s->seg[i].lo,s->seg[i].hi,s->seg[i].v);
    printf("],\"voted_Info_ones\":[");for(int i=0;i<m->n;i++)printf("%s%d",i?",":"",m->x[i]);
    puts("]}");
}
int main(int argc,char **argv){
    int ticks=argc>1?atoi(argv[1]):6144;if(ticks<1||ticks>6144)return 1;
    static State a,next;static Info m,newm;
    append(&a,-15*Q,-14*Q-512,2);
    append(&a,-14*Q-512,-512,1);append(&a,-512,0,3);
    m.x[m.n++]=Q-3;
    uint64_t events=0;report(&a,&m,0,events);
    for(int t=0;t<ticks;t++){
        events+=step(&a,&m,&next,&newm,t);a=next;m=newm;report(&a,&m,t+1,events);
    }
    printf("{\"endpoint_segments\":[");for(int i=0;i<a.n;i++)printf("%s[%d,%d,%u]",i?",":"",a.seg[i].lo,a.seg[i].hi,a.seg[i].v);
    printf("],\"endpoint_Info\":[");for(int i=0;i<m.n;i++)printf("%s%d",i?",":"",m.x[i]);
    printf("],\"exact_event_execution_complete\":true,\"J261_actual_native_projection_input_requires_written_factor\":true,\"whole_SF_or_reset_lift_supplied_by_this_C\":false}\n");return 0;
}
