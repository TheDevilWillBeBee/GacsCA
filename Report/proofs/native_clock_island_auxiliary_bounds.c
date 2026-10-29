/* SP28 exact native/header projection with interval WorkspaceFlag1.
 * No CA, constants, compiler, ROM or backend is changed.
 * Canonical GF and the proved two-clock alphabet are assumed.
 * Actual packet/code transitions are retained. Every possible corrected
 * Info signal is enclosed by raw WF1 in [0, its literal clock/GF guard].
 * Flag bounds are valid only while all allowed outputs share one clock
 * label; the program stops on the first failure of that proof obligation.
 * See the accompanying written proof before interpreting finite outputs.
 */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define Q 1024
#define U 475136
#define TF 278401
#define LIFETIME 1792
#define EPOCH 4096
#define N (256*Q)
#define MASK (N-1)
enum {LABEL,F1LO,F1HI,F2LO,F2HI,PV,CV,WF1HI,PLANES};
static uint8_t state[PLANES][N], next[PLANES][N], refined[N];
static uint16_t code_position[N], next_code_position[N];
static int get(const uint8_t *a,int x){return a[x&MASK];}
static int pos(int x){return code_position[x&MASK];}
static long long checked_label_quorums=0,ambiguous_label_quorums=0;

static void save_state(const char *path){
    FILE *out=fopen(path,"wb");
    if(!out || fwrite(state,1,sizeof(state),out)!=sizeof(state) ||
       fwrite(code_position,sizeof(uint16_t),N,out)!=N)exit(3);
    fclose(out);
}

static void snapshot(int t){
    int offset=t>=TF?t-TF:t;
    const int times[]={0,1,2,1791,1792,1793,2048,2049,4095,4096,4097};
    for(int i=0;i<(int)(sizeof(times)/sizeof(times[0]));i++)if(offset==times[i]){
        char path[160];snprintf(path,sizeof(path),"/tmp/SP28_auxiliary_clock_trace_%d.bin",t);
        save_state(path);break;
    }
}

/* Every valid packet descends from GF1..5 of one true colony, and its
 * tag remains GF-1. Distinct packet origins are Q apart, so a radius5
 * window sees at most one origin. All live counters have the same age
 * within a birth batch (J152). Code origins are jQ-5. At a reader the
 * only qualified origins are its own, or the next colony's in the last
 * five sites. This exact quotient removes repeated equality loops.
 */
static void service(int x,int eligible,int *packet_cohort,int *new_packet,
                    int *new_code,int *new_position){
    int packet_votes=0;
    for(int d=-5;d<=5;d++)packet_votes+=get(state[PV],x+d);
    *packet_cohort=packet_votes>=3;
    int phase=x%Q;
    *new_packet=eligible && *packet_cohort && 1<=phase && phase<=5;
    *new_code=*new_position=0;
    if(!eligible)return;
    int votes[2]={0,0},first[2]={99,99};
    int own_position=phase+5,next_position=own_position-Q;
    for(int d=-5;d<=5;d++){
        int y=(x+d)&MASK,valid=0,adjusted=0;
        if(state[PV][y]){valid=1;adjusted=((y%Q)+5-d)&2047;}
        else if(state[CV][y]){valid=1;adjusted=(pos(y)-d)&2047;}
        if(!valid)continue;
        int which=(adjusted==own_position)?0:
                  (next_position>=0 && adjusted==next_position)?1:-1;
        if(which>=0){votes[which]++;if(first[which]==99)first[which]=d;}
    }
    int chosen=-1;
    if(votes[0]>=3)chosen=0;
    if(votes[1]>=3 && (chosen<0 || first[1]<first[0]))chosen=1;
    if(chosen>=0){*new_code=1;*new_position=chosen?next_position:own_position;}
}

static void native_flags(int x,int right,int use_upper,int force,
                         int *f1,int *f2){
    int phase=x%Q,f1plane=use_upper?F1HI:F1LO,f2plane=use_upper?F2HI:F2LO;
    int mismatches=0,right_flags=0,quiet_joint=0;
    int left_flags=0,left_inside=0,wf1=0,wf2=0;
    for(int d=1;d<=5;d++){
        if(d<=phase){
            mismatches+=(get(refined,x-d)!=right);
            left_inside+=get(state[f2plane],x-d);
        }
        left_flags+=get(state[f2plane],x-d);
        quiet_joint+=(get(refined,x+d)==right && !get(state[f1plane],x+d));
    }
    for(int d=1;d<=8;d++)
        if(phase+d<Q)right_flags+=get(state[f1plane],x+d);
    for(int d=-5;d<=5;d++)if(0<=phase+d && phase+d<Q){
        if(use_upper)wf1+=get(state[WF1HI],x+d);
        wf2+=get(state[PV],x+d);
    }
    *f1=(mismatches>=3 || wf1>=3 || right_flags>=3 ||
         (state[f1plane][x] && right_flags>=2) || (phase<Q-5 && quiet_joint<3));
    int source=(wf2>=3);
    int on=(left_inside>=4 || (*f1 && left_flags>=4) || source);
    int erase=(!*f1 && left_inside<2) || (*f1 && left_flags==0);
    *f2=(state[f2plane][x] ? (source || !erase) : on) || force;
}

static int step(int t){
    int force_clock[2],birth_clock[2],workspace_clock[2];
    for(int label=0;label<2;label++){
        int clock=(t+label*TF)%U;
        force_clock[label]=(TF<=clock && clock<TF+EPOCH);
        birth_clock[label]=(clock==TF);
        workspace_clock[label]=(TF<=clock && clock<TF+2*Q);
    }
    int phase_time=t%U;
    int last_birth=(phase_time>=TF)?TF:0;
    int counter=phase_time-last_birth-1;
    int eligible=(0<=counter && counter<LIFETIME-1);
    for(int x=0;x<N;x++){
        int votes=0;const int centers[4]={-30,-10,10,30};
        for(int k=0;k<4;k++){
            int ones=0;
            for(int d=-2;d<=2;d++)ones+=get(state[LABEL],x+centers[k]+d);
            votes+=(ones>=3);
        }
        refined[x]=(votes>=3)?1:(votes<=1)?0:state[LABEL][x];
    }
    for(int x=0;x<N;x++){
        int phase=x%Q,right=0,left=0;
        for(int d=1;d<=5;d++){right+=get(refined,x+d);left+=get(refined,x-d);}
        right=(right>=3);left=(left>=3);
        int packet_cohort,new_packet,new_code,new_position;
        service(x,eligible,&packet_cohort,&new_packet,&new_code,&new_position);
        /* Computed backward signal implies epoch force because its clock
         * window is a subset of the identical RF clock epoch window.
         */
        int force=force_clock[right] || packet_cohort || new_code;
        int f1lo,f1hi,f2lo,f2hi;
        native_flags(x,right,0,force,&f1lo,&f2lo);
        native_flags(x,right,1,force,&f1hi,&f2hi);
        if(f1lo>f1hi || f2lo>f2hi){fprintf(stderr,"nonmonotone bounds\n");return 7;}
        if(right!=left){
            checked_label_quorums++;
            int necessarily_right=(!f1hi || f2lo);
            int necessarily_left=(f1lo && !f2hi);
            if(!necessarily_right && !necessarily_left){
                ambiguous_label_quorums++;
                printf("{\"first_ambiguous_row\":%d,\"site\":%d,\"GF\":%d,"
                       "\"RF_label\":%d,\"LF_label\":%d,\"Flag1_bounds\":[%d,%d],"
                       "\"Flag2_bounds\":[%d,%d]}\n",t,x,phase,right,left,f1lo,f1hi,f2lo,f2hi);
                fflush(stdout);return 6;
            }
        }
        int selected=(!f1lo || f2lo)?right:left;
        int commit=((t+1+selected*TF)%U==0);
        next[LABEL][x]=selected;
        next[F1LO][x]=f1lo;next[F1HI][x]=f1hi;
        next[F2LO][x]=commit?0:f2lo;next[F2HI][x]=commit?0:f2hi;
        int birth=birth_clock[right] && 1<=phase && phase<=5;
        next[PV][x]=!commit && (birth || new_packet);
        next[CV][x]=!commit && new_code;
        next_code_position[x]=next[CV][x]?new_position:0;
        next[WF1HI][x]=phase>=Q-5 && workspace_clock[selected];
    }
    memcpy(state,next,sizeof(state));
    memcpy(code_position,next_code_position,sizeof(code_position));
    return 0;
}

static int summarize(const char *name,int t){
    int lo=N,hi=-1,ones=0,f1lo=0,f1hi=0,f2lo=0,f2hi=0,aux=0;
    for(int x=0;x<N;x++){
        if(state[LABEL][x]){if(lo==N)lo=x;hi=x;ones++;}
        f1lo+=state[F1LO][x];f1hi+=state[F1HI][x];
        f2lo+=state[F2LO][x];f2hi+=state[F2HI][x];
        aux+=state[PV][x]+state[CV][x]+state[WF1HI][x];
    }
    int contiguous=(hi<lo || ones==hi-lo+1);
    int aligned=(lo%Q==0 && (hi+1)%Q==0);
    int quiet_template=(contiguous && aligned && !f2lo && !f2hi && !aux);
    if(quiet_template)for(int x=0;x<N;x++){
        int expected=(lo-Q<=x && x<lo)||(hi+1-Q<=x && x<hi+1);
        if(state[F1LO][x]!=expected || state[F1HI][x]!=expected){quiet_template=0;break;}
    }
    printf("{\"stage\":\"%s\",\"time\":%d,\"left\":%d,\"right_exclusive\":%d,"
           "\"wrong_clocks\":%d,\"Flag1_bounds_total\":[%d,%d],"
           "\"Flag2_bounds_total\":[%d,%d],\"auxiliary_ones\":%d,"
           "\"quiet_template\":%s,\"distinct_clock_quorums_checked\":%lld,"
           "\"ambiguous_clock_quorums\":%lld}\n",name,t,lo,hi+1,ones,f1lo,f1hi,
           f2lo,f2hi,aux,quiet_template?"true":"false",checked_label_quorums,ambiguous_label_quorums);
    fflush(stdout);
    char path[160];snprintf(path,sizeof(path),"/tmp/SP28_auxiliary_clock_%s.bin",name);
    save_state(path);
    return quiet_template;
}

int main(void){
    int a=128*Q,b=144*Q;
    for(int x=a;x<b;x++)state[LABEL][x]=1;
    for(int x=0;x<N;x++)state[F1LO][x]=state[F1HI][x]=
        (a-Q<=x && x<a)||(b-Q<=x && x<b);
    summarize("initial",0);
    for(int t=0;t<6*Q;t++){snapshot(t);int rc=step(t);if(rc)return rc;if(t==0)summarize("first",1);}
    if(!summarize("after_false_epoch",6*Q))return 4;
    /* J152 gives true auxiliary-zero quiet rows; J150's aligned-template
     * theorem supplies these exact force-free jumps if the tests above
     * have established the common native template.
     */
    for(int t=TF;t<TF+6*Q;t++){snapshot(t);int rc=step(t);if(rc)return rc;}
    if(!summarize("after_true_epoch",TF+6*Q))return 5;
    summarize("period",U);
    return 0;
}
