/* GAW8 canonical-GF categorical-Age/Flag1/Flag2/Workspace projection.
 * New WF=0 is an explicit proof obligation, not imposed physical noise.
 * The preserved initial source used GAW7's3844 source-cone horizon.
 * The extended source additionally uses GAW8's held-SF phase invariant
 * for offsets1..16 and elapsed times<=4Q. source_horizon is a query bound,
 * not a change to the frozen physical GAW2R rule.
 */
#include <stdint.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#define Q 8192
#define MAX 4096
#define F1 (1u<<16)
#define F2 (1u<<17)
#define W1 (1u<<18)
#define W2 (1u<<19)
#define AGEONLY (1u<<31)
typedef struct {int lo,hi;uint32_t v;} Segment;
typedef struct {int n;Segment a[MAX];} State;
typedef struct {
    int status,clock_recovery,native_recovery,max_segments,min_hull,max_hull,final_segments;
    uint64_t events;
} Result;
static uint32_t at(const State*s,int x){
    int lo=0,hi=s->n;
    while(lo<hi){int mid=lo+(hi-lo)/2;if(s->a[mid].hi<=x)lo=mid+1;else hi=mid;}
    return lo<s->n&&s->a[lo].lo<=x?s->a[lo].v:0;
}
static int phase(int x){int p=x%Q;return p<0?p+Q:p;}
static uint32_t maj(const State*s,int x,int direction,uint32_t fallback,int *exists){
    uint32_t values[5];for(int d=1;d<=5;d++)values[d-1]=at(s,x+direction*d)&65535;
    for(int i=0;i<3;i++){int c=0;for(int j=0;j<5;j++)c+=values[i]==values[j];if(c>=3){*exists=1;return values[i];}}
    *exists=0;return fallback;
}
static uint32_t local(const State*s,int x){
    uint32_t self=at(s,x),label=self&65535;int p=phase(x),re,le;
    uint32_t right=maj(s,x,1,label,&re),left=maj(s,x,-1,label,&le);(void)le;
    int inc=0,rf=0,lin=0,lall=0,w1=0,w2=0;
    for(int d=-5;d<=5;d++){
        uint32_t v=at(s,x+d);int inside=0<=p+d&&p+d<Q;
        w1+=inside&&(v&W1)!=0;w2+=inside&&(v&W2)!=0;
        if(d<0){inc+=inside&&(v&65535)!=right;lin+=inside&&(v&F2)!=0;lall+=(v&F2)!=0;}
        if(d>0)rf+=inside&&(v&F1)!=0;
    }
    int f1=!re||inc>=3||w1>=3||rf>=3||((self&F1)&&rf>=2);
    int source=w2>=3;
    int on=lin>=4||(f1&&lall>=4)||source;
    int erase=(!f1&&lin<=1)||(f1&&lall==0);
    int f2=self&F2?(source||!erase):on;
    return ((!f1||f2)?right:left)|(f1?F1:0)|(f2?F2:0);
}
uint32_t gaw8_cofactor(const uint32_t *values,int p){
    State s={0};for(int j=-5;j<=5;j++)if(values[j+5])s.a[s.n++]=(Segment){p+j,p+j+1,values[j+5]};
    return local(&s,p);
}
static void append(State*s,int lo,int hi,uint32_t v){
    if(!v||lo==hi)return;
    if(s->n&&s->a[s->n-1].hi==lo&&s->a[s->n-1].v==v)s->a[s->n-1].hi=hi;
    else {if(s->n==MAX){fprintf(stderr,"capacity\n");exit(2);}s->a[s->n++]=(Segment){lo,hi,v};}
}
static int cmp(const void*a,const void*b){int x=*(const int*)a,y=*(const int*)b;return(x>y)-(x<y);}
static uint64_t step(const State*s,State*n){
    n->n=0;if(!s->n)return 0;
    int low=s->a[0].lo-5,high=s->a[s->n-1].hi+5,cuts[MAX*32],nc=0;
    cuts[nc++]=low;cuts[nc++]=high;
    for(int i=0;i<s->n;i++)for(int d=-5;d<=5;d++){cuts[nc++]=s->a[i].lo-d;cuts[nc++]=s->a[i].hi-d;}
    for(int g=low/Q-2;g<=high/Q+2;g++)for(int d=-5;d<=5;d++){int v=g*Q-d;if(low<=v&&v<=high)cuts[nc++]=v;}
    qsort(cuts,nc,sizeof(int),cmp);uint64_t events=0;
    for(int i=0;i<nc-1;i++){
        int lo=cuts[i],hi=cuts[i+1];if(lo>=hi||lo<low||hi>high)continue;
        uint32_t v=local(s,lo);if(v!=local(s,hi-1))exit(3);
        for(int d=-5;d<=5;d++){if(at(s,lo+d)!=at(s,hi-1+d))exit(4);
            if((0<=phase(lo)+d&&phase(lo)+d<Q)!=(0<=phase(hi-1)+d&&phase(hi-1)+d<Q))exit(5);}
        append(n,lo,hi,v);events++;
    }return events;
}
static void inject(State*s,State*n,int b,const uint32_t *row,int width){
    int cuts[MAX*2+32],nc=0;n->n=0;
    for(int i=0;i<s->n;i++){cuts[nc++]=s->a[i].lo;cuts[nc++]=s->a[i].hi;}
    for(int j=0;j<=width;j++)cuts[nc++]=b+j;
    qsort(cuts,nc,sizeof(int),cmp);
    for(int i=0;i<nc-1;i++){
        int lo=cuts[i],hi=cuts[i+1];if(lo>=hi)continue;
        uint32_t v=at(s,lo);if(b<=lo&&lo<b+width){
            uint32_t replacement=row[lo-b];
            v=(replacement&AGEONLY)?((v&~65535u)|(replacement&65535u)):replacement;
        }append(n,lo,hi,v);
    }
}
int gaw8_run(int b,const uint32_t *rows,int width,int nrows,int limit,int source_horizon,Result *r,uint32_t *final,int final_capacity){
    if(width<1||width>16||nrows<1||nrows>16||source_horizon<3844||limit<source_horizon)return-1;
    State *a=calloc(1,sizeof(State)),*n=calloc(1,sizeof(State));if(!a||!n)exit(6);
    memset(r,0,sizeof(*r));for(int j=0;j<width;j++)append(a,b+j,b+j+1,rows[j]&~AGEONLY);
    r->max_segments=a->n;r->min_hull=b;r->max_hull=b+width;
    int t=0;
    while(a->n&&t<limit){
        r->events+=step(a,n);State*z=a;a=n;n=z;t++;
        if(t<nrows){inject(a,n,b,rows+t*width,width);z=a;a=n;n=z;}
        int label=0;for(int j=0;j<a->n;j++)label|=a->a[j].v&65535;
        if(!label&&!r->clock_recovery&&t>=nrows)r->clock_recovery=t;
        if(a->n>r->max_segments)r->max_segments=a->n;
        if(a->n){if(a->a[0].lo<r->min_hull)r->min_hull=a->a[0].lo;if(a->a[a->n-1].hi>r->max_hull)r->max_hull=a->a[a->n-1].hi;}
        if(t==source_horizon&&label){r->status=1;break;}
    }
    r->native_recovery=a->n?0:t;r->final_segments=a->n;if(a->n&&!r->status)r->status=2;
    if(3*a->n<=final_capacity)for(int j=0;j<a->n;j++){final[3*j]=a->a[j].lo;final[3*j+1]=a->a[j].hi;final[3*j+2]=a->a[j].v;}
    free(a);free(n);return t;
}
