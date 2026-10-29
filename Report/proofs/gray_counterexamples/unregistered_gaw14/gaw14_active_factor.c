/* NEW diagnostic factor for frozen GAW2R, not a changed CA.
 * Contract: every computed clock is in a late active interval and is
 * neither reset nor birth. No WF guard, gather, capture or commit opens.
 * info is reused only as five readonly SF-copy keep bits; native() does
 * not read it. Python computes all mutable Head/Out/Scratch equations.
 */
#include "../unregistered_gaw9/gaw9_native_info.c"
typedef struct {
    int status,geometry,flags,wipes,dirty_lo,dirty_hi,geometry_lo,geometry_hi;
    uint64_t row_hash;
} ActiveResult;
static int keepvote(const Site*a,int y){int count=0;for(int h=0;h<5;h++)count+=(a[y-S[h]].info>>h)&1;return count>=3;}
static uint64_t mix(uint64_t h,uint64_t v){return (h^v)*UINT64_C(1099511628211);}
int gaw14_step(const Site*a,Site*b,const uint8_t*old_program,uint8_t*new_program,
    const uint8_t*beta,int n,int offset,int shadow_age,int*wipe_indices,ActiveResult*r){
    memset(r,0,sizeof(*r));r->dirty_lo=r->geometry_lo=n;r->dirty_hi=r->geometry_hi=-1;
    View v={.a=a,.initial=NULL,.lo=0,.hi=n-1,.n=n,.offset=offset,.t=0};
    for(int x=0;x<n;x++){
        b[x]=(Site){.gf=(uint16_t)phase(offset+x),.age=(uint32_t)shadow_age,.info=31};
        new_program[x]=old_program[x];
    }
    for(int x=5;x<n-5;x++)b[x]=native(&v,x);
    for(int x=9;x<n-9;x++){
        Site z=b[x];
        if(!((102*Q+1<z.age&&z.age<=120*Q)||(72*Q+4<z.age&&z.age<75*Q))){r->status=-2;return -2;}
        int wipe=z.f1&&z.gf!=a[x].gf;
        if(wipe)wipe_indices[r->wipes++]=x;
        z.info=0;new_program[x]=0;
        if(!wipe)for(int h=0;h<5;h++){
            z.info|=keepvote(a,x+S[h])<<h;
            new_program[x]|=beta[(z.gf+S[h])&(Q-1)]<<h;
        }
        b[x]=z;
        if(z.gf!=phase(offset+x)||z.age!=(uint32_t)shadow_age){
            r->geometry++;if(r->geometry_lo==n)r->geometry_lo=x;r->geometry_hi=x;
        }
        if(z.f1||z.f2||z.w1||z.w2)r->flags++;
        if(z.gf!=phase(offset+x)||z.age!=(uint32_t)shadow_age||z.f1||z.f2||z.w1||z.w2||z.info!=31){
            if(r->dirty_lo==n)r->dirty_lo=x;r->dirty_hi=x;
        }
    }
    if(r->dirty_hi>=r->dirty_lo&&(r->dirty_lo<20||r->dirty_hi>=n-20)){r->status=-4;return-4;}
    uint64_t h=UINT64_C(1469598103934665603);
    for(int x=r->dirty_lo;x<=r->dirty_hi;x++){
        h=mix(h,x);h=mix(h,b[x].gf);h=mix(h,b[x].age);
        h=mix(h,b[x].f1|(b[x].f2<<1)|(b[x].w1<<2)|(b[x].w2<<3));
        h=mix(h,b[x].info);h=mix(h,new_program[x]);
    }
    r->row_hash=h;return 0;
}
