/* Exact existing two-Q native/Info factor with a new prepared signal mask.
 * This changes initial data only, not a transition equation. The added
 * true-phase ones are suggested by the blocked-mail source calculation.
 * An actual preceding physical history is a separate proof obligation.
 */
#define main retained_factor_main
#include "native_address_info_factor.c"
#undef main

int main(void){
    duration=2*Q;
    info_mode=3; /* Separate /tmp snapshot names; preserve prior modes. */
    int a=128*Q-512,b=144*Q;
    const int extra_colonies[6]={124,125,126,144,145,146};
    for(int x=0;x<N;x++){
        state[LABEL][x]=a<=x && x<b;
        state[F1][x]=(127*Q<=x && x<a)||(b-512<=x && x<b);
        info[x]=(x&(Q-1))==509 && a<=x && x<b;
    }
    for(int j=0;j<6;j++)info[extra_colonies[j]*Q+1021]=1;
    summary("initial",0);
    const int checkpoints[]={1,2,1791,1792,1793,1794,2048,2049,2064,2368,3*Q,4*Q,6*Q};
    for(int t=0;t<6*Q;t++){
        step(t);
        for(unsigned j=0;j<sizeof(checkpoints)/sizeof(checkpoints[0]);j++)
            if(t+1==checkpoints[j])summary("trace",t+1);
    }
    summary("final",6*Q);
    return 0;
}
