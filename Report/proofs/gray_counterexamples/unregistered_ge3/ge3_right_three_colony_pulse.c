/* UNREGISTERED conditional right-boundary template, not a whole Gray CA.
 * Frozen native quotient: bit0=clock, bit1=F1, bit2=WF1; F2=WF2=0.
 * Only [0,3Q) is updated. Left clock1/right all0 boundaries need proof.
 */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <assert.h>
#define Q 8192
#define END (3*Q)
#define MAXSEG 256
#define MAXCUT 4096
typedef struct {int lo,hi;unsigned v;} Segment;
typedef struct {int n;Segment s[MAXSEG];} State;
static int maximum_segments=0,maximum_cuts=0;
static uint64_t event_segments=0,checksum=1469598103934665603ULL;

static unsigned get(const State*s,int x){
    if(x<0)return 1;
    if(x>=END)return 0;
    int lo=0,hi=s->n;
    while(lo<hi){int m=(lo+hi)/2;if(s->s[m].hi<=x)lo=m+1;else hi=m;}
    assert(lo<s->n && s->s[lo].lo<=x);
    return s->s[lo].v;
}
static unsigned point(const State*s,int x,int t){
    unsigned a[11];for(int j=-5;j<=5;j++)a[j+5]=get(s,x+j);
    int r=x%Q,lc=0,rc=0;
    for(int j=1;j<=5;j++){lc+=a[5-j]&1;rc+=a[5+j]&1;}
    int L=lc>=3,R=rc>=3,I=0,H=0,W=0;
    for(int j=-5;j<=5;j++)if(0<=r+j && r+j<Q){
        W+=(a[j+5]>>2)&1;
        if(j<0)I+=((int)(a[j+5]&1)!=R);
        if(j>0)H+=(a[j+5]>>1)&1;
    }
    int F=I>=3 || W>=3 || H>=3 || (((a[5]>>1)&1) && H>=2);
    int label=F?L:R;
    int age=t+1+label;
    int nextW=r>=Q-5 && 96*Q<=age && age<98*Q;
    return (unsigned)(label+2*F+4*nextW);
}
static void append(State*s,int lo,int hi,unsigned v){
    assert(lo<hi && v<8);
    if(s->n && s->s[s->n-1].hi==lo && s->s[s->n-1].v==v)s->s[s->n-1].hi=hi;
    else {assert(s->n<MAXSEG);s->s[s->n++]=(Segment){lo,hi,v};}
}
static int cmpint(const void*a,const void*b){int x=*(const int*)a,y=*(const int*)b;return (x>y)-(x<y);}
static void cut(int*c,int*n,int x){if(0<=x && x<=END){assert(*n<MAXCUT);c[(*n)++]=x;}}
static void update(const State*old,State*next,int t){
    int c[MAXCUT],n=0;cut(c,&n,0);cut(c,&n,END);
    for(int i=0;i<old->n;i++)for(int d=-5;d<=5;d++){
        cut(c,&n,old->s[i].lo-d);cut(c,&n,old->s[i].hi-d);
    }
    for(int b=0;b<=3;b++)for(int d=-5;d<=5;d++)cut(c,&n,b*Q-d);
    for(int b=0;b<3;b++)cut(c,&n,b*Q+Q-5);
    qsort(c,(size_t)n,sizeof(int),cmpint);int k=0;
    for(int i=0;i<n;i++)if(!k || c[i]!=c[k-1])c[k++]=c[i];
    assert(k>=2);
    next->n=0;
    for(int i=0;i+1<k;i++)append(next,c[i],c[i+1],point(old,c[i],t));
    assert(next->s[0].lo==0 && next->s[next->n-1].hi==END);
    if(next->n>maximum_segments)maximum_segments=next->n;
    if(k>maximum_cuts)maximum_cuts=k;
    event_segments+=(uint64_t)(k-1);
    checksum^=(uint64_t)(t+1);checksum*=1099511628211ULL;
    for(int i=0;i<next->n;i++){
        checksum^=(uint64_t)next->s[i].lo;checksum*=1099511628211ULL;
        checksum^=(uint64_t)next->s[i].hi;checksum*=1099511628211ULL;
        checksum^=next->s[i].v;checksum*=1099511628211ULL;
    }
}
static int complete_clock(const State*s){for(int i=0;i<s->n;i++)if(!(s->s[i].v&1))return 0;return 1;}
static int quiet(const State*s){
    return s->n==2 && s->s[0].lo==0 && s->s[0].hi==2*Q && s->s[0].v==1 &&
        s->s[1].lo==2*Q && s->s[1].hi==END && s->s[1].v==3;
}
static void print_state(const State*s,int t,int*first){
    if(!*first)printf(",\n");*first=0;
    printf("{\"relative_period_row\":%d,\"segments\":[",t);
    for(int i=0;i<s->n;i++)printf("%s[%d,%d,%u]",i?",":"",s->s[i].lo,s->s[i].hi,s->s[i].v);
    printf("]}");
}
int main(void){
    State a={0},b={0};append(&a,0,END,0);
    int start=96*Q-2,end=100*Q,first=1,first_clock=-1,first_quiet=-1;
    printf("{\"Q\":%d,\"start_row\":%d,\"end_row\":%d,\"retained_rows\":[\n",Q,start,end);
    print_state(&a,start,&first);
    for(int t=start;t<end;t++){
        update(&a,&b,t);a=b;
        if(first_clock<0 && complete_clock(&a))first_clock=t+1;
        if(first_quiet<0 && quiet(&a))first_quiet=t+1;
        if((t+1)%256==0 || t+1<=96*Q+2 || t+1==98*Q-1 || t+1==98*Q ||
            t+1==first_clock || t+1==first_quiet || t+1==end)print_state(&a,t+1,&first);
    }
    assert(quiet(&a));
    printf("\n],\"all_updated_rows\":%d,\"event_segments\":%llu,\"max_segments\":%d,"
        "\"max_event_cuts\":%d,\"trace_fnv64\":\"%016llx\",\"first_complete_clock_row\":%d,"
        "\"first_quiet_native_row\":%d,\"final_quiet_right_template\":true}\n",end-start,
        (unsigned long long)event_segments,maximum_segments,maximum_cuts,
        (unsigned long long)checksum,first_clock,first_quiet);
    return 0;
}
