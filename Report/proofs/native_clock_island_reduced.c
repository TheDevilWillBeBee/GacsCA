/* Isolated SP28 native/epoch reduction, not the autonomous full rule.
 * GF is canonical. Age has two phase labels. Raw Workspace flags and all
 * packet/code/backward inputs are zero at every step. Actual native Flag1
 * and Flag2 evolve. No rule, compiler, simulator or candidate is changed.
 */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define Q 1024
#define U 475136
#define TF 278401
#define EPOCH 4096
#define N (256*Q)
#define MASK (N-1)
static uint8_t state[3][N], next[3][N], refined[N];
static int get(const uint8_t *a, int x) { return a[x & MASK]; }
static void step(int t) {
    int active[2];
    for (int label=0; label<2; label++) {
        int clock=(t+label*TF)%U;
        active[label]=(TF<=clock && clock<TF+EPOCH);
    }
    for(int x=0;x<N;x++) {
        int votes=0;
        const int centers[4]={-30,-10,10,30};
        for(int k=0;k<4;k++) {
            int ones=0;
            for(int d=-2;d<=2;d++) ones+=get(state[0],x+centers[k]+d);
            votes+=(ones>=3);
        }
        refined[x]=(votes>=3) ? 1 : (votes<=1) ? 0 : state[0][x];
    }
    for(int x=0;x<N;x++) {
        int phase=x%Q, right=0,left=0;
        for(int d=1;d<=5;d++) {
            right+=get(refined,x+d);
            left+=get(refined,x-d);
        }
        right=(right>=3); left=(left>=3);
        int mismatches=0, right_flags=0, quiet_joint=0;
        int left_flags=0,left_inside=0;
        for(int d=1;d<=5;d++) {
            if(d<=phase) {
                mismatches+=(get(refined,x-d)!=right);
                left_inside+=get(state[2],x-d);
            }
            left_flags+=get(state[2],x-d);
            quiet_joint+=(get(refined,x+d)==right && !get(state[1],x+d));
        }
        for(int d=1;d<=8;d++)
            if(phase+d<Q) right_flags+=get(state[1],x+d);
        int f1=(mismatches>=3 || right_flags>=3 ||
                (state[1][x] && right_flags>=2) ||
                (phase<Q-5 && quiet_joint<3));
        int on=(left_inside>=4 || (f1 && left_flags>=4));
        int erase=(!f1 && left_inside<2) || (f1 && left_flags==0);
        int f2=(state[2][x] ? !erase : on) || active[right];
        next[0][x]=(!f1 || f2) ? right : left;
        next[1][x]=f1;
        next[2][x]=((t+1+next[0][x]*TF)%U==0) ? 0 : f2;
    }
    memcpy(state,next,sizeof(state));
}
static int summarize(const char *name,int t,int save) {
    int lo=N,hi=-1,ones=0,f1=0,f2=0;
    for(int x=0;x<N;x++) {
        if(state[0][x]) { if(lo==N)lo=x;hi=x;ones++; }
        f1+=state[1][x]; f2+=state[2][x];
    }
    int contiguous=(hi<lo || ones==hi-lo+1);
    int aligned=(lo%Q==0 && (hi+1)%Q==0);
    int quiet_template=(contiguous && aligned && f2==0);
    if(quiet_template) for(int x=0;x<N;x++) {
        int expected=(lo-Q<=x && x<lo) || (hi+1-Q<=x && x<hi+1);
        if(state[1][x]!=expected) { quiet_template=0;break; }
    }
    printf("{\"stage\":\"%s\",\"time\":%d,\"left\":%d,\"right_exclusive\":%d,"
           "\"wrong_clocks\":%d,\"Flag1\":%d,\"Flag2\":%d,"
           "\"contiguous\":%s,\"aligned\":%s,\"quiet_template\":%s}\n",
           name,t,lo,hi+1,ones,f1,f2,contiguous?"true":"false",
           aligned?"true":"false",quiet_template?"true":"false");
    fflush(stdout);
    if(save) {
        char path[128];snprintf(path,sizeof(path),"/tmp/SP28_native_clock_%s.bin",name);
        FILE *out=fopen(path,"wb");if(!out || fwrite(state,1,sizeof(state),out)!=sizeof(state))exit(3);
        fclose(out);
    }
    return quiet_template;
}
int main(void) {
    int a=128*Q,b=144*Q;
    for(int x=a;x<b;x++)state[0][x]=1;
    for(int x=0;x<N;x++)state[1][x]=(a-Q<=x && x<a) || (b-Q<=x && x<b);
    summarize("initial",0,1);
    for(int t=0;t<6*Q;t++) { step(t); if(t==0)summarize("first",1,1); }
    if(!summarize("after_false_epoch",6*Q,1)) return 4;
    /* The Python/written proof must certify the force-free quiet template
     * before either omitted interval can be considered an exact jump.
     */
    for(int t=TF;t<TF+6*Q;t++)step(t);
    if(!summarize("after_true_epoch",TF+6*Q,1)) return 5;
    summarize("period",U,1);
    return 0;
}
