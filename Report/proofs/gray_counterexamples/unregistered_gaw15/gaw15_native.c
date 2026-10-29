/* NEW exact pre-Workspace native batch for frozen GAW2R.
 * Python computes all physical SF equations and the actual computed-primary
 * Workspace outputs from the same old row. No selected future commands.
 */
#include "../unregistered_gaw9/gaw9_native_info.c"
typedef struct {int geometry,flags,lo,hi,sources,births;uint64_t hash;} G15Result;
int gaw15_native(const Site*a,Site*b,const uint8_t*beta,uint8_t*pb,
    int n,int offset,int nextage,int*sources,int*births,G15Result*r){
    memset(r,0,sizeof(*r));r->lo=n;r->hi=-1;
    View v={.a=a,.initial=NULL,.lo=0,.hi=n-1,.n=n,.offset=offset,.t=0};
    for(int x=0;x<n;x++)b[x]=(Site){.gf=(uint16_t)phase(offset+x),.age=(uint32_t)nextage};
    for(int x=5;x<n-5;x++)b[x]=native(&v,x);
    uint64_t hash=UINT64_C(1469598103934665603);
    for(int x=9;x<n-9;x++){
        Site z=b[x];int wipe=z.f1&&z.gf!=a[x].gf;
        pb[x]=0;if(!wipe)for(int h=0;h<5;h++)pb[x]|=beta[(z.gf+S[h])&(Q-1)]<<h;
        if(z.gf!=phase(offset+x)||z.age!=(uint32_t)nextage)r->geometry++;
        if(z.f1||z.f2)r->flags++;
        if(z.gf!=phase(offset+x)||z.age!=(uint32_t)nextage||z.f1||z.f2){if(r->lo==n)r->lo=x;r->hi=x;}
        if(!wipe&&96*Q<=z.age&&z.age<98*Q&&
            (z.gf>=Q-5||(z.gf<=4&&!z.f1)))sources[r->sources++]=x;
        if(z.age==72*Q+4||z.age==102*Q+1)for(int h=0;h<5;h++)
            if(((z.gf+S[h])&(Q-1))==3848)births[r->births++]=offset+x+S[h];
        uint8_t cleanpb=0;for(int h=0;h<5;h++)cleanpb|=beta[phase(offset+x+S[h])]<<h;
        if(z.gf!=phase(offset+x)||z.age!=(uint32_t)nextage||z.f1||z.f2||pb[x]!=cleanpb){
            uint64_t data[5]={(uint64_t)x,z.gf,z.age,(uint64_t)(z.f1|(z.f2<<1)),pb[x]};
            for(int j=0;j<5;j++)hash=(hash^data[j])*UINT64_C(1099511628211);
        }
    }
    r->hash=hash;
    if(r->hi>=r->lo&&(r->lo<24||r->hi>=n-24))return -4;
    return 0;
}
