/* Exhaustive finite certificate for one prepared ACTUAL-Info shrinking pulse.
 * The transition is included verbatim from the frozen J164 factor. This is
 * a certificate wrapper, not a rule modification or a self-programme.
 */
#define main retained_info_factor_main
#include "native_address_info_factor.c"
#undef main
#include <assert.h>

static uint64_t tested_background_sites,tested_GF_support_sites;
static int initial_a=128*Q-512,initial_b=144*Q,initial_lo=127*Q;
static int previous_a,previous_b;

static void certify_row(int r){
    int a=N,b=0,count=0,flags[PLANES]={0},ones509=0,ones1021=0;
    int margin=8*(r+1)+37,lo=initial_lo-margin,hi=initial_b+margin;
    assert(0<lo && hi<N && 17*Q<lo);
    for(int x=0;x<N;x++){
        assert(state[LABEL][x]<=1 && state[PT][x]<16 && info[x]<=1);
        if(state[LABEL][x]){if(a==N)a=x;b=x+1;count++;}
        for(int p=1;p<PLANES;p++){
            if(p!=PT)assert(state[p][x]<=1);
            flags[p]+=state[p][x];
        }
        if((x&(Q-1))==509)ones509+=info[x];
        if((x&(Q-1))==1021)ones1021+=info[x];
        if(x<lo || x>=hi){
            int ref=16*Q+(x&(Q-1));
            for(int p=0;p<PLANES;p++)assert(state[p][x]==state[p][ref]);
            assert(code[x]==code[ref] && info[x]==info[ref]);
            tested_background_sites++;
        }
        tested_GF_support_sites++;
    }
    assert(count>=65);
    assert(initial_a-3*r<=a && a<=initial_a+3*r);
    assert(initial_b-3*r<=b && b<=initial_b+3*r);
    if(r){assert(a>=previous_a-3);assert(b<=previous_b+3);}
    previous_a=a;previous_b=b;
    if(r==6*Q){
        assert(a==initial_a-6*Q && b==initial_b-8*Q && count==14848 && count==b-a);
        assert(flags[F1]==1024 && !flags[F2] && !flags[WF1] && !flags[PV] && !flags[CV] && !flags[BP]);
        assert(ones509==8 && ones1021==0);
        for(int x=0;x<N;x++){
            int expected_f1=(a-512<=x && x<a)||(b-512<=x && x<b);
            assert(state[F1][x]==expected_f1 && code[x]==0);
        }
    }
    printf("{\"row\":%d,\"duration\":%d,\"left\":%d,\"right_exclusive\":%d,"
           "\"wrong_Addresses\":%d,\"holes_in_support_hull\":%d,\"Flag1\":%d,\"Flag2\":%d,\"WF1\":%d,"
           "\"packets\":%d,\"codes\":%d,\"pressure\":%d,\"Info509_ones\":%d,"
           "\"Info1021_ones\":%d,\"background_lo\":%d,\"background_hi\":%d}\n",
           r,duration,a,b,count,b-a-count,flags[F1],flags[F2],flags[WF1],flags[PV],flags[CV],flags[BP],
           ones509,ones1021,lo,hi);
    if(!(r&255))fflush(stdout);
}

int main(int argc,char **argv){
    if(argc!=2)return 2;
    duration=atoi(argv[1]);info_mode=2;
    if(duration!=Q && duration!=2*Q)return 2;
    for(int x=0;x<N;x++){
        state[LABEL][x]=initial_a<=x && x<initial_b;
        state[F1][x]=(initial_lo<=x && x<initial_a)||(initial_b-512<=x && x<initial_b);
        info[x]=(x&(Q-1))==509 && initial_a<=x && x<initial_b;
    }
    certify_row(0);
    for(int r=0;r<6*Q;r++){step(r);certify_row(r+1);}
    char path[200];snprintf(path,sizeof(path),"/tmp/SP28_info_shrinking_pulse_%d_final.bin",duration);
    FILE *f=fopen(path,"wb");if(!f)return 8;
    if(fwrite(state,1,sizeof(state),f)!=sizeof(state) || fwrite(code,2,N,f)!=N ||
       fwrite(info,1,N,f)!=N)return 8;
    if(fclose(f))return 8;
    printf("{\"certificate_complete\":true,\"duration\":%d,\"rows_checked\":%d,"
           "\"background_site_equalities\":%llu,\"GF_support_sites_checked\":%llu}\n",
           duration,6*Q+1,(unsigned long long)tested_background_sites,
           (unsigned long long)tested_GF_support_sites);
    return 0;
}
