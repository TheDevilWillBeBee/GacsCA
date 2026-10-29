/* GAW7: exact event quotient for canonical GF, two Age labels, WF=F2=0.
 * The separate proof must derive WF=0 from the actual rule history.
 * This is not a complete-CA simulator and does not choose arbitrary tapes.
 */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define Q 8192
#define MAX 1024
typedef struct { int lo, hi; unsigned v; } Segment;
typedef struct { int n; Segment seg[MAX]; } State;
static unsigned at(const State *s,int x) {
    for(int i=0;i<s->n;i++) {
        if(x<s->seg[i].lo) return 0;
        if(x<s->seg[i].hi) return s->seg[i].v;
    }
    return 0;
}
static int phase(int x) { int p=x%Q; return p<0?p+Q:p; }
static unsigned local(const State *s,int x) {
    int p=phase(x),left=0,right=0,rf=0,inconsistent=0;
    for(int d=1;d<=5;d++) {left+=(at(s,x-d)&1)!=0;right+=(at(s,x+d)&1)!=0;}
    int lv=left>=3,rv=right>=3;
    for(int d=1;d<=5;d++) {
        if(p-d>=0) inconsistent+=((at(s,x-d)&1)!=0)!=rv;
        if(p+d<Q) rf+=(at(s,x+d)&2)!=0;
    }
    int f=inconsistent>=3||rf>=3||((at(s,x)&2)&&rf>=2);
    return (f?lv:rv)|(f<<1);
}
unsigned gaw7_cofactor(unsigned labels,unsigned flags,int p) {
    State s={0};int bit=0;
    for(int d=-5;d<=5;d++) {
        unsigned label=d?((labels>>bit++)&1):0;
        unsigned flag=d==0?((flags>>5)&1):d>0?((flags>>(d-1))&1):0;
        unsigned v=label|(flag<<1);
        if(v)s.seg[s.n++]=(Segment){p+d,p+d+1,v};
    }
    return local(&s,p);
}
static int compare_int(const void *a,const void *b) {
    int x=*(const int*)a,y=*(const int*)b;return (x>y)-(x<y);
}
static void append(State *s,int lo,int hi,unsigned v) {
    if(!v||lo==hi) return;
    if(s->n&&s->seg[s->n-1].hi==lo&&s->seg[s->n-1].v==v) s->seg[s->n-1].hi=hi;
    else {if(s->n>=MAX){fprintf(stderr,"segment capacity exceeded\n");exit(2);}s->seg[s->n++]=(Segment){lo,hi,v};}
}
static uint64_t step(const State *s,State *n) {
    n->n=0;if(!s->n)return 0;
    int low=s->seg[0].lo-5,high=s->seg[s->n-1].hi+5,cuts[MAX*32],nc=0;
    cuts[nc++]=low;cuts[nc++]=high;
    for(int i=0;i<s->n;i++)for(int d=-5;d<=5;d++) {
        cuts[nc++]=s->seg[i].lo-d;cuts[nc++]=s->seg[i].hi-d;
    }
    for(int g=low/Q-2;g<=high/Q+2;g++) for(int d=-5;d<=5;d++) {
        int v=g*Q-d;if(low<=v&&v<=high)cuts[nc++]=v;
    }
    qsort(cuts,nc,sizeof(int),compare_int);uint64_t events=0;
    for(int i=0;i<nc-1;i++) {
        int lo=cuts[i],hi=cuts[i+1];if(lo>=hi||lo<low||hi>high)continue;
        unsigned v=local(s,lo);
        /* Exact partition assertion, not a sample of an omitted interval. */
        if(v!=local(s,hi-1)){fprintf(stderr,"event endpoint discrepancy %d %d\n",lo,hi);exit(3);}
        for(int d=-5;d<=5;d++) {
            if(at(s,lo+d)!=at(s,hi-1+d))exit(4);
            if((phase(lo)+d>=0&&phase(lo)+d<Q)!=(phase(hi-1)+d>=0&&phase(hi-1)+d<Q))exit(5);
        }
        append(n,lo,hi,v);events++;
    }
    return events;
}
int main(int argc,char **argv) {
    int first=argc>1?atoi(argv[1]):0,last=argc>2?atoi(argv[2]):first;
    int width=argc>3?atoi(argv[3]):16,limit=argc>4?atoi(argv[4]):4*Q;
    if(first<0||last>=Q||first>last||width<1||width>16)return 1;
    uint64_t total=0;int max_clock=0,max_quiet=0;
    printf("b,width,clock_recovery,flag_recovery,event_checks,max_segments,min_hull,max_hull\n");
    for(int b=first;b<=last;b++) {
        State a={.n=1,.seg={{b,b+width,1}}},n={0};int healed=0,t=0,maxn=1,low=b,high=b+width;
        uint64_t events=0;
        while(a.n&&t<limit) {
            events+=step(&a,&n);a=n;t++;
            int label=0;for(int j=0;j<a.n;j++)label|=a.seg[j].v&1;
            if(!label&&!healed)healed=t;
            if(a.n>maxn)maxn=a.n;
            if(a.n) {if(a.seg[0].lo<low)low=a.seg[0].lo;if(a.seg[a.n-1].hi>high)high=a.seg[a.n-1].hi;}
        }
        if(a.n||!healed){fprintf(stderr,"unhealed b%d width%d t%d segments%d\n",b,width,t,a.n);return 6;}
        printf("%d,%d,%d,%d,%llu,%d,%d,%d\n",b,width,healed,t,(unsigned long long)events,maxn,low,high);
        total+=events;if(healed>max_clock)max_clock=healed;if(t>max_quiet)max_quiet=t;
    }
    fprintf(stderr,"total_events=%llu max_clock=%d max_quiet=%d\n",(unsigned long long)total,max_clock,max_quiet);
    return 0;
}
