/* NEW unregistered GE1 native-prefix instance, not an autonomous Gray rule.
 * bit0=clock offset1, bit1=Flag1, bit2=Workspace1; Flag2=Workspace2=0.
 * argv: initial integer-colony width, then every held Flag1 source colony.
 * The infinite-exterior and raw-native factor obligations are in the proof.
 */
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#define Q 8192
#define MAXSEG 2048
#define MAXCUT 65536
#define MAXCOMMAND 512
typedef struct {int lo,hi;unsigned v;} Segment;
typedef struct {int n;Segment s[MAXSEG];} State;
static int lower,upper,command[MAXCOMMAND],ncommand;
static int maximum_segments,maximum_cuts;
static uint64_t events,checksum=1469598103934665603ULL;
static int floor_div(int x){int r=x/Q;if(x<0 && x%Q)r--;return r;}
static int source(int g){for(int i=0;i<ncommand;i++)if(command[i]==g)return 1;return 0;}
static unsigned get(const State*s,int x){
    if(x<lower || x>=upper)return 0;
    int lo=0,hi=s->n;
    while(lo<hi){int m=(lo+hi)/2;if(s->s[m].hi<=x)lo=m+1;else hi=m;}
    assert(lo<s->n && s->s[lo].lo<=x);return s->s[lo].v;
}
static unsigned point(const State*s,int x,int t){
    unsigned a[11];for(int j=-5;j<=5;j++)a[j+5]=get(s,x+j);
    int colony=floor_div(x),r=x-colony*Q,lc=0,rc=0;
    for(int j=1;j<=5;j++){lc+=(int)(a[5-j]&1);rc+=(int)(a[5+j]&1);}
    int L=lc>=3,R=rc>=3,I=0,H=0,W=0;
    for(int j=-5;j<=5;j++)if(0<=r+j && r+j<Q){
        W+=(int)((a[j+5]>>2)&1);
        if(j<0)I+=((int)(a[j+5]&1)!=R);
        if(j>0)H+=(int)((a[j+5]>>1)&1);
    }
    int F=I>=3 || W>=3 || H>=3 || (((a[5]>>1)&1) && H>=2);
    int label=F?L:R,age=t+1+label;
    int nextW=source(colony) && r>=Q-5 && 96*Q<=age && age<98*Q;
    return (unsigned)(label+2*F+4*nextW);
}
static void append(State*s,int lo,int hi,unsigned v){
    assert(lo<hi && v<8);
    if(s->n && s->s[s->n-1].hi==lo && s->s[s->n-1].v==v)s->s[s->n-1].hi=hi;
    else {assert(s->n<MAXSEG);s->s[s->n++]=(Segment){lo,hi,v};}
}
static int cmpint(const void*a,const void*b){int x=*(const int*)a,y=*(const int*)b;return (x>y)-(x<y);}
static void cut(int*c,int*n,int x){if(lower<=x && x<=upper){assert(*n<MAXCUT);c[(*n)++]=x;}}
static void update(const State*old,State*next,int t){
    int c[MAXCUT],n=0;cut(c,&n,lower);cut(c,&n,upper);
    for(int i=0;i<old->n;i++)for(int d=-5;d<=5;d++){
        cut(c,&n,old->s[i].lo-d);cut(c,&n,old->s[i].hi-d);
    }
    for(int b=lower/Q;b<=upper/Q;b++)for(int d=-5;d<=5;d++)cut(c,&n,b*Q-d);
    for(int b=lower/Q;b<upper/Q;b++)cut(c,&n,b*Q+Q-5);
    qsort(c,(size_t)n,sizeof(int),cmpint);int k=0;
    for(int i=0;i<n;i++)if(!k || c[i]!=c[k-1])c[k++]=c[i];
    next->n=0;
    for(int i=0;i+1<k;i++)append(next,c[i],c[i+1],point(old,c[i],t));
    assert(next->s[0].lo==lower && next->s[next->n-1].hi==upper);
    if(next->n>maximum_segments)maximum_segments=next->n;
    if(k>maximum_cuts)maximum_cuts=k;
    events+=(uint64_t)(k-1);
    checksum^=(uint64_t)(t+1);checksum*=1099511628211ULL;
    for(int i=0;i<next->n;i++){
        checksum^=(uint64_t)(int64_t)next->s[i].lo;checksum*=1099511628211ULL;
        checksum^=(uint64_t)(int64_t)next->s[i].hi;checksum*=1099511628211ULL;
        checksum^=next->s[i].v;checksum*=1099511628211ULL;
    }
}
static void print_state(const State*s,int t,int*first){
    if(!*first)printf(",\n");
    *first=0;
    printf("{\"relative_period_row\":%d,\"segments\":[",t);
    for(int i=0;i<s->n;i++)printf("%s[%d,%d,%u]",i?",":"",s->s[i].lo,s->s[i].hi,s->s[i].v);
    printf("]}");
}
int main(int argc,char**argv){
    assert(argc>=2 && argc-2<MAXCOMMAND);int width=atoi(argv[1]);assert(width>=2 && width<=104);
    lower=-2*Q;upper=(width+5)*Q;
    for(int i=2;i<argc;i++){
        int c=atoi(argv[i]);command[ncommand++]=c;
        if((c-2)*Q<lower)lower=(c-2)*Q;
        if((c+3)*Q>upper)upper=(c+3)*Q;
    }
    State a={0},b={0};
    append(&a,lower,-Q,0);append(&a,-Q,0,2);append(&a,0,(width-1)*Q,1);
    append(&a,(width-1)*Q,width*Q,3);append(&a,width*Q,upper,0);
    int start=96*Q-2,end=100*Q,first=1;
    printf("{\"Q\":%d,\"initial_width_Q\":%d,\"domain\":[%d,%d],\"commands\":[",Q,width,lower,upper);
    for(int i=0;i<ncommand;i++)printf("%s%d",i?",":"",command[i]);
    printf("],\"start_row\":%d,\"end_row\":%d,\"retained_rows\":[\n",start,end);
    print_state(&a,start,&first);
    for(int t=start;t<end;t++){
        update(&a,&b,t);a=b;
        if((t+1)%256==0 || t+1<=96*Q+3 || t+1==98*Q-1 || t+1==98*Q || t+1==end)
            print_state(&a,t+1,&first);
    }
    printf("\n],\"all_updated_rows\":%d,\"event_segments\":%llu,\"max_segments\":%d,"
        "\"max_event_cuts\":%d,\"trace_fnv64\":\"%016llx\"}\n",end-start,
        (unsigned long long)events,maximum_segments,maximum_cuts,(unsigned long long)checksum);
    return 0;
}
