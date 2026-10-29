/* Exact native/interface cycle for changing ONLY the epoch duration.
 * This reuses the immutable J156 projection at its original duration4Q.
 * It checks a force-on Q-row cycle and the common force-off tail.
 * It is not a new own-programme or iid certificate. No active CA changes.
 */
#define main original_J156_projection_main
#include "native_address_island_auxiliary_bounds.c"
#undef main

static uint8_t initial_frame[PLANES][N],prefix_frame[PLANES][N];
static int require_shift(const uint8_t old[PLANES][N],int delta){
    for(int p=0;p<PLANES;p++)for(int x=0;x<N;x++)
        if(state[p][x]!=old[p][(x+delta)&MASK])return 0;
    return 1;
}
static void report_frame(const char *name,int t){
    int a=N,b=-1,count=0;
    for(int x=0;x<N;x++)if(state[LABEL][x]){
        if(a==N)a=x;b=x;count++;
    }
    printf("{\"stage\":\"%s\",\"time\":%d,\"left\":%d,\"right_exclusive\":%d,\"wrong_Addresses\":%d,\"distinct_quorums\":%lld}\n",
           name,t,a,b+1,count,checked_quorums);
    fflush(stdout);
    char path[160];snprintf(path,sizeof(path),"/tmp/SP28_epoch_duration_%s.bin",name);
    save_state(path);
}
int main(void){
    const int a=128*Q-displacement,b=144*Q;
    for(int x=a;x<b;x++)state[LABEL][x]=1;
    for(int x=0;x<N;x++)state[F1LO][x]=state[F1HI][x]=
        (127*Q<=x && x<a)||(b-displacement<=x && x<b);
    memcpy(initial_frame,state,sizeof(state));report_frame("initial",0);
    for(int t=TF;t<TF+6*Q;t++){
        if(t==TF+3*Q){
            for(int x=0;x<N;x++)if(state[F1LO][x]!=state[F1HI][x] ||
                state[F2LO][x]!=1 || state[F2HI][x]!=1 || state[WF1HI][x])return 8;
            memcpy(prefix_frame,state,sizeof(state));report_frame("prefix3Q",t);
        }
        if(t==TF+4*Q){
            if(!require_shift(prefix_frame,3*Q))return 9;
            report_frame("prefix4Q",t);
        }
        int rc=step(t);if(rc)return rc;
    }
    if(!require_shift(initial_frame,12*Q))return 10;
    report_frame("quiet6Q",TF+6*Q);
    printf("{\"force_on_Q_row_translation_cycle\":true,\"cycle_translation\":%d,\"force_off_tail_rows\":%d,\"tail_returns_quiet_template\":true}\n",-3*Q,2*Q);
    return 0;
}
