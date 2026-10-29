/* Analysis only: sound powerset enclosure of the frozen SP31 binary-GF,
 * common-clock native/Info factor. 0={0}, 1={1}, 2={0,1}.
 * No rule, ROM, command, or physical fault history is changed. */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
enum {Q=1024,LO=80*Q,HI=200*Q,NX=HI-LO,BORDER=64};
typedef struct {int lo[NX+1],hi[NX+1];} Prefix;
typedef struct {int lo,hi;} Count;
static uint8_t a[5][NX],b[5][NX],info[NX],nextinfo[NX],g[NX],keep[NX];
static Prefix ps[5],pg,pq[2],pk;
static int dn(int v){return v==2?2:!v;}
static int da(int x,int y){return !x||!y?0:x==1?y:y==1?x:2;}
static int dor(int x,int y){return x==1||y==1?1:x==0?y:y==0?x:2;}
static int dm(int c,int x,int y){return c==0?y:c==1?x:x==y?x:2;}
static int dx(int x,int y){return x==2||y==2?2:x!=y;}
static int du(int x,int y){return x==y?x:2;}
static int has(int d,int v){return d==2||d==v;}
static int ge(Count n,int t){return n.lo>=t?1:n.hi<t?0:2;}
static int rd(const uint8_t*p,int i){return 0<=i&&i<NX?p[i]:0;}
static void prefix(Prefix*p,const uint8_t*v){
    p->lo[0]=p->hi[0]=0;
    for(int i=0;i<NX;i++){p->lo[i+1]=p->lo[i]+(v[i]==1);p->hi[i+1]=p->hi[i]+(v[i]!=0);}
}
static Count count(const Prefix*p,int l,int r){
    if(l<0)l=0;
    if(r>NX)r=NX;
    if(l>r)l=r;
    return (Count){p->lo[r]-p->lo[l],p->hi[r]-p->hi[l]};
}
static Count inverted(Count n,int size){return (Count){size-n.hi,size-n.lo};}
static int refine(int i){
    const int centers[4]={-30,-10,10,30};int lo=0,hi=0;
    for(int k=0;k<4;k++){int v=ge(count(&ps[0],i+centers[k]-2,i+centers[k]+3),3);lo+=v==1;hi+=v!=0;}
    int zero=lo<=1||(lo<=2&&2<=hi&&has(a[0][i],0));
    int one=hi>=3||(lo<=2&&2<=hi&&has(a[0][i],1));
    return zero&&one?2:one;
}
static void prepare(void){
    for(int j=0;j<5;j++)prefix(&ps[j],a[j]);
    for(int i=0;i<NX;i++)g[i]=refine(i);
    prefix(&pg,g);
    for(int r=0;r<2;r++){
        pq[r].lo[0]=pq[r].hi[0]=0;
        for(int i=0;i<NX;i++){
            int v=da(r?g[i]:dn(g[i]),dn(a[1][i]));
            pq[r].lo[i+1]=pq[r].lo[i]+(v==1);pq[r].hi[i+1]=pq[r].hi[i]+(v!=0);
        }
    }
}
static unsigned local(int i,int x,int elapsed){
    int rf=ge(count(&pg,i+1,i+6),3),lf=ge(count(&pg,i-5,i),3);
    int output[6]={-1,-1,-1,-1,-1,-1};
    for(int r=0;r<2;r++)if(has(rf,r)){
        int p=(x+512*r)&(Q-1),leftn=p<5?p:5;
        Count mm=count(&pg,i-leftn,i);if(r)mm=inverted(mm,leftn);
        int rightn=Q-1-p<8?Q-1-p:8;
        Count right=count(&ps[1],i+1,i+1+rightn),quiet=count(&pq[r],i+1,i+6);
        int low=p<5?-p:-5,high=Q-1-p<5?Q-1-p:5;
        Count w1=count(&ps[2],i+low,i+high+1),w2=count(&ps[4],i+low,i+high+1);
        Count leftall=count(&ps[3],i-5,i),leftinside=count(&ps[3],i-leftn,i);
        int f=dor(ge(mm,3),dor(ge(right,3),dor(da(a[1][i],ge(right,2)),dor(ge(w1,3),p<Q-5?dn(ge(quiet,3)):0))));
        int d4=ge(w2,3),on=dor(ge(leftinside,4),dor(da(f,ge(leftall,4)),d4));
        int erase=dor(da(dn(f),dn(ge(leftinside,2))),da(f,dn(ge(leftall,1))));
        int f2=dm(a[3][i],dor(d4,dn(erase)),on),selected=dm(dor(dn(f),f2),r,lf);
        int wf1=-1,wf2=-1;
        for(int s=0;s<2;s++)if(has(selected,s)){
            int np=(x+512*s)&(Q-1);
            int v1=elapsed<2*Q&&np>=Q-5?rd(info,i+Q-3-np):0;
            int v2=elapsed<2*Q&&np<5?da(dn(f),rd(info,i+3-np)):0;
            wf1=wf1<0?v1:du(wf1,v1);wf2=wf2<0?v2:du(wf2,v2);
        }
        int values[6]={selected,f,wf1,f2,wf2,dn(da(f,dx(selected,g[i])))};
        for(int j=0;j<6;j++)output[j]=output[j]<0?values[j]:du(output[j],values[j]);
    }
    unsigned packed=0;for(int j=0;j<6;j++)packed|=(unsigned)output[j]<<(2*j);
    return packed;
}
/* Read-only local checker entry point. Its neighbourhood includes every
 * native dependency (radius37) and both special Info addresses. */
unsigned sp31_fifth_ternary_cofactor(const uint16_t*native,const uint8_t*inf,int p,int elapsed){
    memset(a,0,sizeof(a));memset(info,0,sizeof(info));int c=NX/2;
    for(int d=-40;d<=40;d++){
        for(int j=0;j<5;j++)a[j][c+d]=(native[d+40]>>(2*j))&3;
        info[c+d]=inf[d+40];
    }
    prepare();return local(c,p,elapsed);
}
static int save(const char*path){
    FILE*f=fopen(path,"wb");if(!f)return 2;
    if(fwrite(a,1,sizeof(a),f)!=sizeof(a)||fwrite(info,1,sizeof(info),f)!=sizeof(info)){fclose(f);return 2;}
    return fclose(f)?2:0;
}
static int report(int row){
    int definite[5]={0},possible[5]={0},unknown[5]={0},border=0,inf=0,left=HI,right=LO;
    for(int i=0;i<NX;i++){
        for(int j=0;j<5;j++){definite[j]+=a[j][i]==1;possible[j]+=a[j][i]!=0;unknown[j]+=a[j][i]==2;}
        inf+=info[i]!=0;
        if(a[0][i]!=0){if(left>LO+i)left=LO+i;right=LO+i+1;}
        if(i<2*BORDER||i>=NX-2*BORDER){for(int j=0;j<5;j++)border+=a[j][i]!=0;border+=info[i]!=0;}
    }
    printf("{\"row\":%d,\"GF_possible_left\":%d,\"GF_possible_right_exclusive\":%d,\"native_definite_ones\":[%d,%d,%d,%d,%d],\"native_possible_ones\":[%d,%d,%d,%d,%d],\"native_unknown\":[%d,%d,%d,%d,%d],\"Info_possible_ones\":%d,\"border_violations\":%d}\n",row,left,right,definite[0],definite[1],definite[2],definite[3],definite[4],possible[0],possible[1],possible[2],possible[3],possible[4],unknown[0],unknown[1],unknown[2],unknown[3],unknown[4],inf,border);
    return border?42:0;
}
int main(int argc,char**argv){
    if(argc<2||argc>4)return 1;
    int ticks=argc>2?atoi(argv[2]):6144,stop_fixed=argc>3?atoi(argv[3]):0;
    if(ticks<1||ticks>196735||(stop_fixed!=0&&stop_fixed!=1))return 1;
    for(int i=0;i<NX;i++){
        int x=LO+i,col=x/Q,p=x&(Q-1);
        /* J251 actual fifth-source enclosure, with correlations enlarged.
         * Native F2 and both WF were reset and remain0 through the prefix. */
        a[0][i]=152*Q-512<=x&&x<155*Q?1:142*Q+1<=x&&x<152*Q-512?2:0;
        a[1][i]=155*Q-512<=x&&x<155*Q?1:142*Q-2<=x&&x<152*Q-512?2:0;
        int fixed=(p==509&&152<=col&&col<=154)||(p==1021&&((100<=col&&col<=139)||(155<=col&&col<=157)));
        int free=(p==509&&142<=col&&col<=151)||(p==1021&&140<=col&&col<=150)||(p==3&&133<=col&&col<=151)||(p==515&&142<=col&&col<=154);
        if(fixed&&free)return 3;
        info[i]=free?2:fixed;
    }
    int code=report(0);if(code)return code;
    for(int t=0;t<ticks;t++){
        prepare();
        for(int i=BORDER;i<NX-BORDER;i++){
            unsigned v=local(i,LO+i,t);
            for(int j=0;j<5;j++)b[j][i]=(v>>(2*j))&3;
            keep[i]=(v>>10)&3;
        }
        /* All exterior input is canonical. A radius37 guard is checked at
         * every row; no finite periodic boundary or supplied repair is used. */
        for(int i=0;i<BORDER;i++)keep[i]=keep[NX-1-i]=1;
        prefix(&pk,keep);
        for(int i=0;i<NX;i++)nextinfo[i]=da(info[i],ge(count(&pk,i-2,i+3),3));
        int same=t>=2*Q&&!memcmp(a,b,sizeof(a));
        memcpy(a,b,sizeof(a));memcpy(info,nextinfo,sizeof(info));
        code=report(t+1);if(code){if(save(argv[1]))return 2;return code;}
        if(same&&stop_fixed){
            if(save(argv[1]))return 2;
            printf("{\"native_abstract_fixed_point\":true,\"row\":%d,\"Workspace_guard_disabled_until_next_period_pulse\":true,\"actual_Info_or_full_boundary_or_repair_proved\":false,\"global_reliability_established\":false}\n",t+1);
            return 0;
        }
    }
    if(save(argv[1]))return 2;
    puts("{\"finite_ternary_enclosure_complete\":true,\"actual_fifth_endpoint_or_repair_proved\":false,\"global_reliability_established\":false}");
    return 0;
}
