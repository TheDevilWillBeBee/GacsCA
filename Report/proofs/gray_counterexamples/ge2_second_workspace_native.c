/* Exact infinite-line interval update of the conditional second GE2 pulse.
 * Bits of a segment value: 0=clock label, 1=Flag1, 2=Workspace1.
 * GF is canonical, Flag2/Workspace2 zero. This is not a full Gray CA.
 */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <assert.h>

#define Q 8192
#define MAXSEG 2048
#define MAXCUT 32768
static const int command[]={-4,-3,-2,-1,10,11,12,13,14,15,16,17,18,19,20,21,22};
typedef struct {int lo,hi;unsigned v;} Segment;
typedef struct {int n;Segment s[MAXSEG];} State;
static int max_segments=0,max_cuts=0;
static uint64_t event_segments=0,checksum=1469598103934665603ULL;

static int floorq(int x){return x>=0 ? x/Q : -((-x+Q-1)/Q);}
static int cmpint(const void*a,const void*b){int x=*(const int*)a,y=*(const int*)b;return (x>y)-(x<y);}
static unsigned get(const State*s,int x){
    int lo=0,hi=s->n;
    while(lo<hi){int m=(lo+hi)/2;if(s->s[m].hi<=x)lo=m+1;else hi=m;}
    return lo<s->n && s->s[lo].lo<=x ? s->s[lo].v : 0;
}
static void append(State*s,int lo,int hi,unsigned v){
    assert(lo<hi && v<8);
    if(s->n && s->s[s->n-1].hi==lo && s->s[s->n-1].v==v)s->s[s->n-1].hi=hi;
    else {assert(s->n<MAXSEG);s->s[s->n++]=(Segment){lo,hi,v};}
}
static int commanded(int colony){
    for(unsigned k=0;k<sizeof(command)/sizeof(command[0]);k++)if(command[k]==colony)return 1;
    return 0;
}
static unsigned point(const State*s,int x,int old_t){
    unsigned old[11];for(int j=-5;j<=5;j++)old[j+5]=get(s,x+j);
    int colony=floorq(x),r=x-colony*Q,lc=0,rc=0;
    for(int j=1;j<=5;j++){lc+=(old[5-j]&1);rc+=(old[5+j]&1);}
    int L=lc>=3,R=rc>=3,mismatch=0,rightflags=0,workspace=0;
    for(int j=-5;j<=5;j++)if(0<=r+j && r+j<Q){
        workspace+=(old[j+5]>>2)&1;
        if(j<0)mismatch+=((int)(old[j+5]&1)!=R);
        if(j>0)rightflags+=(old[j+5]>>1)&1;
    }
    int F=mismatch>=3 || workspace>=3 || rightflags>=3 || (((old[5]>>1)&1) && rightflags>=2);
    int label=F ? L : R;
    int age=old_t+1+label;
    int W=commanded(colony) && r>=Q-5 && 96*Q<=age && age<98*Q;
    return (unsigned)(label+2*F+4*W);
}
static void addcut(int*cuts,int*n,int x,int lo,int hi){
    if(lo<=x && x<=hi){assert(*n<MAXCUT);cuts[(*n)++]=x;}
}
static void update(const State*old,State*next,int old_t){
    int lo=-3*Q-5,hi=23*Q; /* hull of the seventeen derived source strips */
    if(old->n){if(old->s[0].lo-5<lo)lo=old->s[0].lo-5;
        if(old->s[old->n-1].hi+5>hi)hi=old->s[old->n-1].hi+5;}
    int cuts[MAXCUT],n=0;addcut(cuts,&n,lo,lo,hi);addcut(cuts,&n,hi,lo,hi);
    for(int i=0;i<old->n;i++)for(int d=-5;d<=5;d++){
        addcut(cuts,&n,old->s[i].lo-d,lo,hi);addcut(cuts,&n,old->s[i].hi-d,lo,hi);
    }
    for(int c=floorq(lo)-1;c<=floorq(hi)+1;c++){
        for(int d=-5;d<=5;d++)addcut(cuts,&n,c*Q-d,lo,hi);
        addcut(cuts,&n,c*Q+Q-5,lo,hi);
    }
    qsort(cuts,(size_t)n,sizeof(int),cmpint);int distinct=0;
    for(int i=0;i<n;i++)if(!distinct || cuts[i]!=cuts[distinct-1])cuts[distinct++]=cuts[i];
    if(distinct>max_cuts)max_cuts=distinct;
    next->n=0;
    for(int i=0;i+1<distinct;i++)append(next,cuts[i],cuts[i+1],point(old,cuts[i],old_t));
    /* Exterior zero is implicit; trim zero end intervals exactly. */
    int first=0;while(first<next->n && !next->s[first].v)first++;
    int last=next->n;while(last>first && !next->s[last-1].v)last--;
    for(int i=first;i<last;i++)next->s[i-first]=next->s[i];
    next->n=last-first;
    if(next->n>max_segments)max_segments=next->n;
    event_segments+=(uint64_t)(distinct-1);
    checksum^=(uint64_t)(old_t+1);checksum*=1099511628211ULL;
    for(int i=0;i<next->n;i++){
        checksum^=(uint64_t)(int64_t)next->s[i].lo;checksum*=1099511628211ULL;
        checksum^=(uint64_t)(int64_t)next->s[i].hi;checksum*=1099511628211ULL;
        checksum^=next->s[i].v;checksum*=1099511628211ULL;
    }
}
static int clock_target(const State*s){
    int left=0,right=0;int64_t width=0;
    for(int i=0;i<s->n;i++)if(s->s[i].v&1){
        if(!width)left=s->s[i].lo;
        right=s->s[i].hi;width+=s->s[i].hi-s->s[i].lo;
    }
    return left==0 && right==23*Q && width==23*Q;
}
static int final_target(const State*s){
    if(s->n!=3)return 0;
    return s->s[0].lo==-Q && s->s[0].hi==0 && s->s[0].v==2 &&
        s->s[1].lo==0 && s->s[1].hi==22*Q && s->s[1].v==1 &&
        s->s[2].lo==22*Q && s->s[2].hi==23*Q && s->s[2].v==3;
}
static void print_state(const State*s,int t,int*first){
    if(!*first)printf(",\n");
    *first=0;
    printf("{\"local_period_row\":%d,\"segments\":[",t);
    for(int i=0;i<s->n;i++)printf("%s[%d,%d,%u]",i?",":"",s->s[i].lo,s->s[i].hi,s->s[i].v);
    printf("]}");
}
int main(void){
    State a={0},b={0};append(&a,-Q,0,2);append(&a,0,19*Q,1);append(&a,19*Q,20*Q,3);
    int start=96*Q-2,end=100*Q,first=1,first20=-1,first_final=-1;
    printf("{\"Q\":%d,\"start_row\":%d,\"end_row\":%d,\"retained_rows\":[\n",Q,start,end);
    print_state(&a,start,&first);
    for(int t=start;t<end;t++){
        update(&a,&b,t);a=b;
        if(first20<0 && clock_target(&a))first20=t+1;
        if(first_final<0 && final_target(&a))first_final=t+1;
        if((t+1)%256==0 || t+1<=96*Q+2 || t+1==98*Q-1 || t+1==98*Q || t+1==end ||
            t+1==first20 || t+1==first_final)print_state(&a,t+1,&first);
    }
    assert(clock_target(&a) && final_target(&a));
    printf("\n],\"all_updated_rows\":%d,\"event_segments\":%llu,\"max_segments\":%d,\"max_event_cuts\":%d,"
        "\"trace_fnv64\":\"%016llx\",\"first_exact_23Q_clock_row\":%d,\"first_exact_quiet_23Q_native_row\":%d,"
        "\"final_matches_23Q_stationary_native_form\":true}\n",end-start,(unsigned long long)event_segments,
        max_segments,max_cuts,(unsigned long long)checksum,first20,first_final);
    return 0;
}
