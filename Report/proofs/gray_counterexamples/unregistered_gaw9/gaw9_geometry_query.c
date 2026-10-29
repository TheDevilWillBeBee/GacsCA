/* Same exact factor; geometry-only query stop. Native canonical/common
 * geometry is absorbing for arbitrary subsequent flags/workspace. */
/* GAW9 mixed native/full-Age projection of frozen GAW2R.
 * Exact only while no Head can be born: Heads, Out and couriers start0.
 * Actual Info low bits, phase0/80Q-1 writes, SF wipes and radius8 WF are
 * evaluated here; future Workspace inputs are never selected externally.
 * History/Mail/Mem may evolve but do not enter this native/Info factor.
 */
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#define Q 8192
#define U (128*Q)
static const int S[5]={0,-2,-1,1,2};
typedef struct {uint16_t gf;uint32_t age;uint8_t f1,f2,w1,w2,info;} Site;
typedef struct {int status,steps,first_geometry_quiet,first_native_quiet,
    max_geometry_count,max_geometry_span,min_geometry_x,max_geometry_x,
    final_geometry_count,final_flag_count,final_info_count;
    uint64_t updates;} Result;
typedef struct {const Site *a;const uint8_t *initial;int lo,hi,n,offset,t;} View;
static int phase(int x){int p=x%Q;return p<0?p+Q:p;}
static Site readsite(const View*v,int x){
    if(v->lo<=x&&x<=v->hi)return v->a[x];
    Site z={.gf=(uint16_t)phase(x+v->offset),.age=(uint32_t)((96*Q+v->t)&(U-1)),.info=v->initial[x]};return z;
}
static uint32_t majority(const uint32_t a[5],uint32_t fallback,int *exists){
    for(int i=0;i<3;i++){int count=0;for(int j=0;j<5;j++)count+=a[i]==a[j];if(count>=3){*exists=1;return a[i];}}
    *exists=0;return fallback;
}
static Site native(const View*v,int x){
    Site self=readsite(v,x),z=self;uint32_t rg[5],lg[5],ra[5],la[5];int ex,lex,aex,laex;
    for(int i=0;i<5;i++){int j=i+1;Site r=readsite(v,x+j),l=readsite(v,x-j);
        rg[i]=(r.gf-j)&(Q-1);lg[i]=(l.gf+j)&(Q-1);ra[i]=r.age;la[i]=l.age;}
    int right=(int)majority(rg,self.gf,&ex),left=(int)majority(lg,self.gf,&lex);(void)lex;
    uint32_t rightage=majority(ra,self.age,&aex),leftage=majority(la,self.age,&laex);(void)laex;
    int mismatchGF=0,mismatchAge=0,rf=0,w1=0,w2=0,lf=0,linside=0;
    for(int j=-5;j<=5;j++){
        Site a=readsite(v,x+j);int inside=ex&&0<=right+j&&right+j<Q;
        w1+=inside&&a.w1;w2+=inside&&a.w2;
        if(j<0){mismatchGF+=inside&&a.gf!=((right+j)&(Q-1));mismatchAge+=inside&&a.age!=rightage;
            lf+=a.f2;linside+=inside&&a.f2;}
        if(j>0)rf+=inside&&a.f1;
    }
    z.f1=!ex||!aex||mismatchGF>=3||mismatchAge>=3||w1>=3||rf>=3||(self.f1&&rf>=2);
    int source3=!ex&&((leftage+1)%16==0),source4=w2>=3;
    int on=linside>=4||(z.f1&&lf>=4)||source3||source4;
    int erase=(!z.f1&&linside<=1)||(z.f1&&lf==0);
    z.f2=self.f2?(source3||source4||!erase):on;
    int rightvote=ex&&(!z.f1||z.f2);
    z.gf=rightvote?right:left;z.age=((rightvote?rightage:leftage)+1)&(U-1);z.w1=z.w2=0;
    return z;
}
static int voteinfo(const View*v,int y){int n=0;for(int h=0;h<5;h++)n+=(readsite(v,y-S[h]).info>>h)&1;return n>=3;}
static int primary(const View*v,const Site*b,int p){
    Site old=readsite(v,p),z=b[p];
    if(z.f1&&z.gf!=old.gf)return 0;
    if(z.age==0||(z.age==80*Q-1&&(z.gf==3||z.gf==Q-3)))return 0;
    return voteinfo(v,p);
}
static Site physical(const View*v,const Site*b,int x){
    Site z=b[x],old=readsite(v,x);int wipe=z.f1&&z.gf!=old.gf,bits=0;
    if(!wipe)for(int h=0;h<5;h++){
        int addr=(z.gf+S[h])&(Q-1);
        int commit=z.age==0||(z.age==80*Q-1&&(addr==3||addr==Q-3));
        if(!commit)bits|=voteinfo(v,x+S[h])<<h;
    }z.info=bits;
    if(!wipe&&96*Q<=z.age&&z.age<98*Q){
        if(z.gf>=Q-5)z.w1=primary(v,b,x+Q-3-z.gf);
        if(z.gf<=4&&!z.f1)z.w2=primary(v,b,x+3-z.gf);
    }return z;
}
int gaw9_cofactor(const Site *a,Site *out){
    uint8_t initial[17]={0};Site b[17];View v={a,initial,0,16,17,0,0};
    for(int x=5;x<=11;x++)b[x]=native(&v,x);
    *out=physical(&v,b,8);return 0;
}
int gaw9_campaign(Site *a,Site*b,const uint8_t*initial,int n,int offset,int limit,Result*r,int*events,int capacity,Site*final){
    memset(r,0,sizeof(*r));int alo=n,ahi=-1;
    for(int x=0;x<n;x++)if(a[x].gf!=phase(x+offset)||a[x].age!=96*Q||a[x].f1||a[x].f2||a[x].w1||a[x].w2||a[x].info!=initial[x]){if(alo==n)alo=x;ahi=x;}
    r->min_geometry_x=offset+n;r->max_geometry_x=offset-1;
    for(int t=0;t<limit;t++){
        if(ahi<alo){r->status=0;r->steps=t;if(!r->first_geometry_quiet)r->first_geometry_quiet=t;if(!r->first_native_quiet)r->first_native_quiet=t;return 0;}
        int lo=alo-8,hi=ahi+8;if(lo<16||hi>=n-16){r->status=-4;r->steps=t;return-4;}
        View v={a,initial,alo,ahi,n,offset,t};
        for(int x=lo-3;x<=hi+3;x++)b[x]=native(&v,x);
        int nlo=n,nhi=-1,glo=n,ghi=-1,gc=0,fc=0,ic=0;
        for(int x=lo;x<=hi;x++){
            b[x]=physical(&v,b,x);r->updates++;
            if(b[x].gf!=phase(x+offset)||b[x].age!=((96*Q+t+1)&(U-1))){if(glo==n)glo=x;ghi=x;gc++;}
            if(b[x].f1||b[x].f2||b[x].w1||b[x].w2)fc++;
            if(b[x].info!=initial[x])ic++;
            if(b[x].gf!=phase(x+offset)||b[x].age!=((96*Q+t+1)&(U-1))||b[x].f1||b[x].f2||b[x].w1||b[x].w2||b[x].info!=initial[x]){if(nlo==n)nlo=x;nhi=x;}
        }
        if(!gc&&!r->first_geometry_quiet)r->first_geometry_quiet=t+1;
        if(!gc&&!fc&&!r->first_native_quiet)r->first_native_quiet=t+1;
        if(gc>r->max_geometry_count)r->max_geometry_count=gc;
        if(gc&&ghi-glo+1>r->max_geometry_span)r->max_geometry_span=ghi-glo+1;
        if(gc&&glo+offset<r->min_geometry_x)r->min_geometry_x=glo+offset;
        if(gc&&ghi+offset>r->max_geometry_x)r->max_geometry_x=ghi+offset;
        if(t<capacity){int*e=events+8*t;e[0]=t+1;e[1]=gc;e[2]=gc?glo+offset:0;e[3]=gc?ghi+offset:0;e[4]=fc;e[5]=ic;e[6]=nhi>=nlo?nlo+offset:0;e[7]=nhi>=nlo?nhi+offset:0;}
        r->final_geometry_count=gc;r->final_flag_count=fc;r->final_info_count=ic;r->steps=t+1;
        Site*tmp=a;a=b;b=tmp;alo=nlo;ahi=nhi;
        /* Native quiet alone can leave legitimate SF/Info damage. Record
         * it exactly and stop; this is not a whole-period recovery claim. */
        if(!gc){r->status=0;for(int x=0;x<n;x++)final[x]=readsite(&(View){a,initial,alo,ahi,n,offset,t+1},x);return 0;}
    }
    r->status=1;for(int x=0;x<n;x++)final[x]=readsite(&(View){a,initial,alo,ahi,n,offset,limit},x);return 1;
}
