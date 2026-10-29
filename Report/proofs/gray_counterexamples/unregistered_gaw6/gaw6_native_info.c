/* GAW6 projection of frozen GAW2R on a common clock, computed Info held.
 * Radius8; Info bits are the actual five old holders, not a clean source.
 * This component does not implement heads/Out/History or cross Age0/80Q-1.
 */
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#define Q 8192
#define U (128*Q)
typedef struct {uint16_t gf; uint8_t f1,f2,w1,w2,info,keep;} Site;
static const int S[5]={0,-2,-1,1,2};
static int majority5(const int v[5],int fallback,int *exists){
    int candidate=0,balance=0;
    for(int i=0;i<5;i++){if(!balance){candidate=v[i];balance=1;}else balance+=v[i]==candidate?1:-1;}
    int count=0;for(int i=0;i<5;i++)count+=v[i]==candidate;
    *exists=count>=3;return *exists?candidate:fallback;
}
static int inside(int addr,int exists,int j){return exists&&addr+j>=0&&addr+j<Q;}
static int votebit(const Site *a,int x){
    int c=0;for(int i=0;i<5;i++)c+=(a[x-S[i]].info>>i)&1;return c>=3;
}
static int votekeep(const Site *a,int x){
    int c=0;for(int i=0;i<5;i++)c+=(a[x-S[i]].keep>>i)&1;return c>=3;
}
static Site native(const Site *a,int x,int oldage){
    Site z=a[x];int right[5],left[5],ex,lex,rv,lv;
    for(int i=0;i<5;i++){int j=i+1;right[i]=(a[x+j].gf-j)&(Q-1);left[i]=(a[x-j].gf+j)&(Q-1);}
    rv=majority5(right,a[x].gf,&ex);lv=majority5(left,a[x].gf,&lex);
    int mismatch=0,rf=0,w1=0,w2=0,lf=0,linside=0;
    for(int j=-5;j<=5;j++){
        int in=inside(rv,ex,j);
        w1+=in&&a[x+j].w1;w2+=in&&a[x+j].w2;
        if(j<0){mismatch+=in&&a[x+j].gf!=((rv+j)&(Q-1));lf+=a[x+j].f2;linside+=in&&a[x+j].f2;}
        if(j>0)rf+=in&&a[x+j].f1;
    }
    z.f1=!ex||mismatch>=3||w1>=3||rf>=3||(a[x].f1&&rf>=2);
    int source3=!ex&&((oldage+1)%16==0),source4=w2>=3;
    int on=linside>=4||(z.f1&&lf>=4)||source3||source4;
    int erase=(!z.f1&&linside<=1)||(z.f1&&lf==0);
    z.f2=a[x].f2?(source3||source4||!erase):on;
    z.gf=ex&&(!z.f1||z.f2)?rv:lv;z.w1=z.w2=0;
    return z;
}
int gaw6_step(const Site *a,Site *b,int n,int oldage){
    if(n<17||oldage<0||oldage>=U)return -1;
    int age=(oldage+1)%U;
    if(age==0||age==80*Q-1)return -2;
    memcpy(b,a,(size_t)n*sizeof(Site));
    uint8_t *wipe=calloc((size_t)n,1),*v=calloc((size_t)n,1),*vk=calloc((size_t)n,1);
    if(!wipe||!v||!vk){free(wipe);free(v);free(vk);return -3;}
    for(int x=5;x<n-5;x++){b[x]=native(a,x,oldage);wipe[x]=b[x].f1&&b[x].gf!=a[x].gf;v[x]=votebit(a,x);vk[x]=votekeep(a,x);}
    for(int x=8;x<n-8;x++){
        int bits=0,keep=0;if(!wipe[x])for(int h=0;h<5;h++){bits|=v[x+S[h]]<<h;keep|=vk[x+S[h]]<<h;}
        b[x].info=bits;b[x].keep=keep;
        if(!wipe[x]&&96*Q<=age&&age<98*Q){
            if(b[x].gf>=Q-5){int p=x+Q-3-b[x].gf;b[x].w1=!wipe[p]&&v[p];}
            if(b[x].gf<=4&&!b[x].f1){int p=x+3-b[x].gf;b[x].w2=!wipe[p]&&v[p];}
        }
    }
    free(wipe);free(v);free(vk);return 0;
}
/* All-native rows for a GF-only burst from a canonical H source. Adaptive
 * envelope stays at least16 sites from both fixed canonical boundaries.
 * Buffer Info contains actual I lower bits. Errors occur on initial row.
 */
int gaw6_campaign(Site *a,Site *b,const uint8_t *initial_info,int n,int offset,
    int firstage,int steps,int *summary,int *events,int event_capacity){
    uint8_t *wipe=calloc((size_t)n,1),*v=calloc((size_t)n,1),*vk=calloc((size_t)n,1);
    if(!wipe||!v||!vk){free(wipe);free(v);free(vk);return -3;}
    int alo=n,ahi=-1,blo=n,bhi=-1,count=0,maxgf=0,maxspan=0;
    for(int x=0;x<n;x++)if(a[x].gf!=((x+offset)&(Q-1))||a[x].f1||a[x].f2||a[x].w1||a[x].w2||a[x].info!=initial_info[x]||a[x].keep!=31){if(alo==n)alo=x;ahi=x;}
    for(int tick=0;tick<steps;tick++){
        int age=(firstage+tick+1)%U;if(age==0||age==80*Q-1){free(wipe);free(v);free(vk);return -2;}
        if(ahi<alo){summary[0]=tick;summary[1]=count;summary[2]=maxgf;summary[3]=maxspan;summary[4]=0;free(wipe);free(v);free(vk);return 0;}
        int lo=alo-8,hi=ahi+8;if(lo<16||hi>=n-16){free(wipe);free(v);free(vk);return -4;}
        if(bhi>=blo)for(int x=blo;x<=bhi;x++){b[x]=(Site){.gf=(uint16_t)((x+offset)&(Q-1)),.info=initial_info[x],.keep=31};}
        for(int x=lo-3;x<=hi+3;x++){b[x]=native(a,x,(firstage+tick)%U);wipe[x]=b[x].f1&&b[x].gf!=a[x].gf;v[x]=votebit(a,x);vk[x]=votekeep(a,x);}
        int nlo=n,nhi=-1,glo=n,ghi=-1,gcount=0,fcount=0,icount=0;
        for(int x=lo;x<=hi;x++){
            int bits=0,keep=0;if(!wipe[x])for(int h=0;h<5;h++){bits|=v[x+S[h]]<<h;keep|=vk[x+S[h]]<<h;}b[x].info=bits;b[x].keep=keep;
            if(!wipe[x]&&96*Q<=age&&age<98*Q){
                if(b[x].gf>=Q-5){int p=x+Q-3-b[x].gf;b[x].w1=!wipe[p]&&v[p];}
                if(b[x].gf<=4&&!b[x].f1){int p=x+3-b[x].gf;b[x].w2=!wipe[p]&&v[p];}
            }
            int badgf=b[x].gf!=((x+offset)&(Q-1));
            if(badgf){if(glo==n)glo=x;ghi=x;gcount++;}
            if(b[x].f1||b[x].f2||b[x].w1||b[x].w2)fcount++;
            if(b[x].info!=initial_info[x]||b[x].keep!=31)icount++;
            if(badgf||b[x].f1||b[x].f2||b[x].w1||b[x].w2||b[x].info!=initial_info[x]||b[x].keep!=31){if(nlo==n)nlo=x;nhi=x;}
        }
        /* Extra source-only sites must not become uncontrolled stale input. */
        for(int x=lo-3;x<lo;x++)b[x]=(Site){.gf=(uint16_t)((x+offset)&(Q-1)),.info=initial_info[x],.keep=31};
        for(int x=hi+1;x<=hi+3;x++)b[x]=(Site){.gf=(uint16_t)((x+offset)&(Q-1)),.info=initial_info[x],.keep=31};
        if(count<event_capacity){int *e=events+8*count;e[0]=tick+1;e[1]=gcount;e[2]=gcount?glo+offset:0;e[3]=gcount?ghi+offset:0;e[4]=fcount;e[5]=icount;e[6]=nhi>=nlo?nlo+offset:0;e[7]=nhi>=nlo?nhi+offset:0;}
        count++;if(gcount>maxgf)maxgf=gcount;if(gcount&&ghi-glo+1>maxspan)maxspan=ghi-glo+1;
        Site *tmp=a;a=b;b=tmp;blo=alo;bhi=ahi;alo=nlo;ahi=nhi;
    }
    summary[0]=steps;summary[1]=count;summary[2]=maxgf;summary[3]=maxspan;summary[4]=ahi>=alo;
    free(wipe);free(v);free(vk);return 0;
}
